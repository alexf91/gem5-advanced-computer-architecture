#
# Copyright 2018 Alexander Fasching
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""
Contains functions and classes to run gem5 from Python instead of the other
way around. This enables further analysis of algorithms through Jupyter.
"""

from __future__ import print_function

__all__ = ('BenchmarkRunner', )

import os
import socket
import subprocess
import contextlib
import tempfile
import shutil

# Path of the gem5 binary relative to this file
cwd = os.path.abspath(os.path.dirname(__file__))
gem5path = os.path.join(cwd, '..', '..', 'build', 'ALPHA', 'gem5.opt')

class BenchmarkRunner(object):
    gem5path = gem5path

    def __init__(self, predictor, prog, *args, socket_name='/tmp/gem5.socket'):
        self.predictor = predictor
        self.prog = prog
        self.args = args
        self.socket_name = socket_name

        self.stdout = None
        self.stderr = None
        self.stats = None

    def run(self):
        assert os.path.exists(self.gem5path)
        sepath = os.path.join(os.path.dirname(__file__), 'se.py')

        outdir = tempfile.mkdtemp(prefix='gem5-')

        cmd = [
            self.gem5path, '--outdir', outdir, sepath, '-n', '1', '--cpu-type',
            'MinorCPU', '--caches', '-c', self.prog
        ]
        if self.args:
            cmd.append('--options')
            cmd.append(' '.join(map(str, self.args)))

        cmd.append(self.socket_name)

        # Initialize the passive socket
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.socket_name)

        sockfd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sockfd.bind(self.socket_name)
        sockfd.listen(1)

        # Start the simulator
        env = {'PYTHONPATH': os.path.join(cwd, '..', '..', 'configs')}
        gemproc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        # Accept the connection from the simulator
        connfd, addr = sockfd.accept()
        connfp = connfd.makefile(mode='rw')

        # Run the predictor
        while True:
            line = connfp.readline()
            if not line:
                break

            info = eval(line)
            #print(info)
            meth = getattr(self.predictor, '_base_' + info['method'])
            del info['method']
            results = meth(**info)
            if results is not None:
                rsp = ','.join(map(str, map(int, results)))
                connfp.write(rsp + '\n')
                connfp.flush()

        # Cleanup
        gemproc.wait()

        connfd.close()
        sockfd.close()
        with contextlib.suppress(FileNotFoundError):
            os.unlink(self.socket_name)

        self.stdout = gemproc.stdout.read()
        self.stderr = gemproc.stderr.read()
        with open(os.path.join(outdir, 'stats.txt')) as fp:
            self.stats = fp.read()

        shutil.rmtree(outdir)

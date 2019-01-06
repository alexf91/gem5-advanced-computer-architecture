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

__all__ = ('ExternalRunner', 'InternalRunner', 'FullSystemRunner', 'CPUType')

import os
import socket
import subprocess
import contextlib
import tempfile
import shutil
import struct
import enum

from .statistics import Statistics


METH_UNCOND_BRANCH = 0
METH_LOOKUP        = 1
METH_BTB_UPDATE    = 2
METH_UPDATE        = 3
METH_SQUASH        = 4

# Path of the gem5 binary relative to this file
pkgdir = os.path.abspath(os.path.dirname(__file__))
gem5path = os.path.join(pkgdir, '..', '..', 'build', 'ALPHA', 'gem5.opt')


class CPUType(enum.Enum):
    MINOR_CPU = 0
    ATOMIC_SIMPLE_CPU = 1

class ExternalRunner(object):
    """Benchmark runner for external predictors."""
    gem5path = gem5path

    def __init__(self, predictor, prog, args=None, stdin=None,
                 cputype=CPUType.ATOMIC_SIMPLE_CPU):
        self.predictor = predictor
        self.prog = prog
        self.args = args or tuple()
        self.stdin = stdin
        self.cputype = cputype

        self.stdout = None
        self.stderr = None
        self.stats = None

    def run(self):
        assert os.path.exists(self.gem5path)
        sepath = os.path.join(pkgdir, 'se.py')

        outdir = tempfile.mkdtemp(prefix='gem5-')
        socket_name = os.path.join(outdir, 'gem5.socket')

        cmd = [self.gem5path, '--outdir', outdir, sepath, '-n', '1']

        if self.cputype == CPUType.MINOR_CPU:
            cmd.extend(['--cpu-type', 'MinorCPU', '--caches'])
        elif self.cputype == CPUType.ATOMIC_SIMPLE_CPU:
            cmd.extend(['--cpu-type', 'AtomicSimpleCPU'])
        else:
            raise ValueError('Unknown CPU type')

        cmd.extend(['-c', self.prog])

        if self.args:
            cmd.append('--options')
            cmd.append(' '.join(map(str, self.args)))

        # Append the configuration parameters
        config = '\n'.join([
            'branchPred = ExternalBP()',
            'branchPred.socketName = "%s"' % socket_name,
            'root.system.cpu[0].branchPred = branchPred',
        ])
        cmd.append(config)

        # Initialize the passive socket
        sockfd = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sockfd.bind(socket_name)
        sockfd.listen(1)

        # Start the simulator
        pipe = None if self.stdin is None else subprocess.PIPE
        env = {'PYTHONPATH': os.path.join(pkgdir, '..', '..', 'configs')}
        gemproc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=pipe)

        if pipe:
            gemproc.stdin.write(self.stdin.encode())
            gemproc.stdin.close()

        # Accept the connection from the simulator
        connfd, addr = sockfd.accept()
        connfp = connfd.makefile(mode='rwb')

        # Run the predictor
        while True:
            msg = connfp.read(21)
            if not msg:
                break
            assert len(msg) == 21

            info = struct.unpack('=bhQQbb', msg)
            if info[0] == METH_UNCOND_BRANCH:
                results = self.predictor._base_uncond_branch(info[1], info[2],
                                                             info[3])
            elif info[0] == METH_LOOKUP:
                results = self.predictor._base_lookup(info[1], info[2],
                                                      info[3])
            elif info[0] == METH_BTB_UPDATE:
                results = self.predictor._base_btb_update(info[1], info[2],
                                                          info[3])
            elif info[0] == METH_UPDATE:
                results = self.predictor._base_update(info[1], info[2],
                                                      info[4], info[3],
                                                      info[5])
            elif info[0] == METH_SQUASH:
                results = self.predictor._base_squash(info[1], info[3])

            #print(info)
            if results is not None:
                rsp = struct.pack('=bQ', *results)
                connfp.write(rsp)
                connfp.flush()

        # Cleanup
        gemproc.wait()

        connfd.close()
        sockfd.close()

        self.stdout = gemproc.stdout.read().decode()
        self.stderr = gemproc.stderr.read().decode()
        self.stats = []
        with open(os.path.join(outdir, 'stats.txt')) as fp:
            for section in fp.read().split('Begin Simulation Statistics'):
                stats = Statistics(section)
                if stats.rows:
                    self.stats.append(stats)

        shutil.rmtree(outdir)


class InternalRunner(object):
    """Benchmark runner for internal predictors."""
    gem5path = gem5path

    def __init__(self, setup_code, prog, args=None, stdin=None,
                 cputype=CPUType.ATOMIC_SIMPLE_CPU):
        self.setup_code = setup_code
        self.prog = prog
        self.args = args or tuple()
        self.stdin = stdin
        self.cputype = cputype

        self.stdout = None
        self.stderr = None
        self.stats = None

    def run(self):
        assert os.path.exists(self.gem5path)
        sepath = os.path.join(pkgdir, 'se.py')

        outdir = tempfile.mkdtemp(prefix='gem5-')

        cmd = [self.gem5path, '--outdir', outdir, sepath, '-n', '1']

        if self.cputype == CPUType.MINOR_CPU:
            cmd.extend(['--cpu-type', 'MinorCPU', '--caches'])
        elif self.cputype == CPUType.ATOMIC_SIMPLE_CPU:
            cmd.extend(['--cpu-type', 'AtomicSimpleCPU'])
        else:
            raise ValueError('Unknown CPU type')

        cmd.extend(['-c', self.prog])

        if self.args:
            cmd.append('--options')
            cmd.append(' '.join(map(str, self.args)))

        # Append the setup code
        cmd.append(self.setup_code)

        # Start the simulator
        pipe = None if self.stdin is None else subprocess.PIPE
        env = {'PYTHONPATH': os.path.join(pkgdir, '..', '..', 'configs')}
        gemproc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, stdin=pipe)

        if pipe:
            gemproc.stdin.write(self.stdin.encode())
            gemproc.stdin.close()

        # Cleanup
        gemproc.wait()

        self.stdout = gemproc.stdout.read().decode()
        self.stderr = gemproc.stderr.read().decode()
        self.stats = []
        with open(os.path.join(outdir, 'stats.txt')) as fp:
            for section in fp.read().split('Begin Simulation Statistics'):
                stats = Statistics(section)
                if stats.rows:
                    self.stats.append(stats)

        shutil.rmtree(outdir)


class FullSystemRunner(object):
    """Run a full system without a branch predictor."""
    gem5path = gem5path

    def __init__(self, scriptcode, cputype=CPUType.ATOMIC_SIMPLE_CPU):
        self.scriptcode = scriptcode
        self.cputype = cputype

        self.stdout = None
        self.stderr = None
        self.stats = None
        self.terminal = None

    def run(self):
        assert os.path.exists(self.gem5path)
        fspath = os.path.join(pkgdir, '..', '..', 'configs', 'example',
                              'fs.py')

        outdir = tempfile.mkdtemp(prefix='gem5-')
        scriptpath = os.path.join(outdir, 'runscript.sh')
        with open(scriptpath, 'w') as fp:
            fp.write(self.scriptcode)

        cmd = [self.gem5path, '--outdir', outdir, fspath, '-n', '1']

        if self.cputype == CPUType.MINOR_CPU:
            cmd.extend(['--cpu-type', 'MinorCPU', '--caches'])
        elif self.cputype == CPUType.ATOMIC_SIMPLE_CPU:
            cmd.extend(['--cpu-type', 'AtomicSimpleCPU'])
        else:
            raise ValueError('Unknown CPU type')

        cmd.extend(['--script', scriptpath])

        # Start the simulator
        m5path = '/dist/m5/system:%s/../toolchain/m5_system_2.0b3' % pkgdir
        imgpath = ('%s/../toolchain/m5_system_2.0b3/disks/linux-parsec.img'
                    % pkgdir)
        env = {
            'PYTHONPATH': os.path.join(pkgdir, '..', '..', 'configs'),
            'M5_PATH': m5path,
            'LINUX_IMAGE': imgpath
        }
        gemproc = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)

        # Cleanup
        gemproc.wait()

        self.stdout = gemproc.stdout.read().decode()
        self.stderr = gemproc.stderr.read().decode()
        self.stats = []
        with open(os.path.join(outdir, 'stats.txt')) as fp:
            for section in fp.read().split('Begin Simulation Statistics'):
                stats = Statistics(section)
                if stats.rows:
                    self.stats.append(stats)
        with open(os.path.join(outdir, 'system.terminal')) as fp:
            self.terminal = fp.read()

        shutil.rmtree(outdir)

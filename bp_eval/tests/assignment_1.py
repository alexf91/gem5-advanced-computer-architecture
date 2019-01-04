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

from bpredict import *


def print_stats(runner):
    assert len(runner.stats) == 3

    sim_seconds = runner.stats[1].find('sim_seconds')[0]
    direct_ctrl = runner.stats[1].find('num_direct_control_insts')[0]
    indirect_ctrl = runner.stats[1].find('num_indirect_control_insts')[0]

    print(sim_seconds.name, sim_seconds.values[0])
    print(direct_ctrl.name, direct_ctrl.values[0])
    print(indirect_ctrl.name, indirect_ctrl.values[0])
    print('direct_percentage', direct_ctrl.values[0] /
            (direct_ctrl.values[0] + indirect_ctrl.values[0]))
    print()


# Run the blackscholes benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    './blackscholes 1 /parsec/install/inputs/blackscholes/in_4K.txt /dev/null',
    '/sbin/m5 exit',
])

blackscholes_runner = FullSystemRunner(scriptcode=script,
                                       cputype=CPUType.ATOMIC_SIMPLE_CPU)
blackscholes_runner.run()
print('blackscholes')
print_stats(blackscholes_runner)


# Run the canneal benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    './canneal 1 10000 5 /parsec/install/inputs/canneal/100.nets',
    '/sbin/m5 exit',
])

canneal_runner = FullSystemRunner(scriptcode=script,
                                  cputype=CPUType.ATOMIC_SIMPLE_CPU)
canneal_runner.run()
print('canneal')
print_stats(canneal_runner)


# Run the streamcluster benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    # usage: ./streamcluster k1 k2 d n chunksize clustersize in out nproc
    './streamcluster 10 20 3 100 100 100 /dev/zero /dev/null 1',
    '/sbin/m5 exit',
])

streamcluster_runner = FullSystemRunner(scriptcode=script,
                                        cputype=CPUType.ATOMIC_SIMPLE_CPU)
streamcluster_runner.run()
print('streamcluster')
print_stats(streamcluster_runner)


# Run the dedup benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    './dedup -i /parsec/install/inputs/dedup/test.dat -o /dev/null',
    '/sbin/m5 exit',
])

dedup_runner = FullSystemRunner(scriptcode=script,
                                cputype=CPUType.ATOMIC_SIMPLE_CPU)
dedup_runner.run()
print('dedup')
print_stats(dedup_runner)

#!/usr/bin/env python
# coding: utf-8

from bpredict import *


def print_stats(runner):
    insts_setup = runner.stats[0].find('sim_insts')[0]
    insts_benchmark = runner.stats[1].find('sim_insts')[0]
    print('setup_insts:    ', insts_setup.values[0])
    print('benchmark_insts:',
            insts_benchmark.values[0] - insts_setup.values[0])

    sim_seconds = runner.stats[1].find('sim_seconds')[0]
    direct_ctrl = runner.stats[1].find('num_direct_control_insts')[0]
    indirect_ctrl = runner.stats[1].find('num_indirect_control_insts')[0]

    print(sim_seconds.name, sim_seconds.values[0])
    print(direct_ctrl.name, direct_ctrl.values[0])
    print(indirect_ctrl.name, indirect_ctrl.values[0])
    print('direct_percentage', direct_ctrl.values[0] /
            (direct_ctrl.values[0] + indirect_ctrl.values[0]))
    print()

RUN_INSTS = 100 * 10**6


# Run the blackscholes benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    './blackscholes 1 /parsec/install/inputs/blackscholes/in_4K.txt /dev/null',
    '/sbin/m5 exit',
])

INIT_INSTS = 149648136
blackscholes_runner = FullSystemRunner(scriptcode=script,
                                       cputype=CPUType.ATOMIC_SIMPLE_CPU,
                                       maxinsts=INIT_INSTS + RUN_INSTS)
blackscholes_runner.run()
print_stats(blackscholes_runner)


# Run the canneal benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    # usage: ./canneal NTHREADS NSWAPS TEMP NETLIST [NSTEPS]
    './canneal 1 10000 2000 /parsec/install/inputs/canneal/100000.nets 32',
    '/sbin/m5 exit',
])

INIT_INSTS = 2030400132
canneal_runner = FullSystemRunner(scriptcode=script,
                                  cputype=CPUType.ATOMIC_SIMPLE_CPU,
                                  maxinsts=INIT_INSTS + RUN_INSTS)
canneal_runner.run()
print_stats(canneal_runner)


# Run the streamcluster benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
# usage: ./streamcluster k1 k2 d n chunksize clustersize infile outfile nproc
    './streamcluster 10 20 32 4096 4096 1000 none /dev/null 1',
    '/sbin/m5 exit',
])

INIT_INSTS = 96937392
streamcluster_runner = FullSystemRunner(scriptcode=script,
                                        cputype=CPUType.ATOMIC_SIMPLE_CPU,
                                        maxinsts=INIT_INSTS + RUN_INSTS)
streamcluster_runner.run()
print_stats(streamcluster_runner)


# Run the dedup benchmark
script = '\n'.join([
    'cd /parsec/install/bin',
    './dedup -c -t 1 -i /parsec/install/inputs/dedup/hamlet.dat -o /dev/null',
    '/sbin/m5 exit',
])

INIT_INSTS = 105959907
dedup_runner = FullSystemRunner(scriptcode=script,
                                cputype=CPUType.ATOMIC_SIMPLE_CPU,
                                maxinsts=INIT_INSTS + RUN_INSTS)
dedup_runner.run()
print_stats(dedup_runner)

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

import matplotlib.pyplot as plt
import bpredict


benchmark = 'benchmarks/picosat/picosat.alpha'
args = ('benchmarks/picosat/CBS_k3_n100_m403_b30_1.cnf', )

pred = bpredict.Local2BitPredictor(8192)
runner = bpredict.BenchmarkRunner(pred, benchmark, *args)
runner.run()
print(runner.stats)
for line in runner.stats.split('\n'):
    if 'system.cpu.branchPred.BTBHitPct' in line:
        print(line)

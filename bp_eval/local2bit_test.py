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


benchmark = 'benchmarks/blackscholes/blackscholes.alpha'
args = (1, 'benchmarks/blackscholes/blackscholes.test.input', '/dev/null')

sizes = [256, 512, 1024, 2048, 4096, 8192, 16384]
hitrate = []

for size in sizes:
    pred = bpredict.Local2BitPredictor(size)
    runner = bpredict.BenchmarkRunner(pred, benchmark, *args)
    runner.run()
    for line in runner.stats.split('\n'):
        if 'system.cpu.branchPred.BTBHitPct' in line:
            hitrate.append(float(line.split()[1]) / 100)

plt.semilogx(sizes, hitrate)
plt.title('Local 2-Bit Predictor')
plt.xlabel('Predictor size in bytes')
plt.xticks(sizes, sizes)
plt.ylabel('Hitrate')
plt.grid()
plt.show()

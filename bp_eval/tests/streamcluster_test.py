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

from multiprocessing import Pool
import matplotlib.pyplot as plt
import bpredict


benchmark = '../benchmarks/streamcluster/streamcluster'
args = (10, 20, 3, 100, 100, 100, '/dev/zero', '/dev/null', 1)
sizes = [256, 512, 1024, 2048, 4096, 8192, 16384]


def run_benchmark(size):
    pred = bpredict.Local2BitPredictor(size)
    runner = bpredict.ExternalRunner(pred, benchmark, args=args)
    runner.run()

    predicted = runner.stats[0].find('condPredicted')[0].values[0]
    incorrect = runner.stats[0].find('condIncorrect')[0].values[0]

    return (incorrect / predicted)


if __name__ == '__main__':
    pool = Pool(8)
    hitrate = pool.map(run_benchmark, sizes)

    plt.semilogx(sizes, hitrate)
    plt.title('Local 2-Bit Predictor')
    plt.xlabel('Predictor size in bytes')
    plt.xticks(sizes, sizes)
    plt.ylabel('Misprediction Rate')
    plt.grid()
    plt.show()

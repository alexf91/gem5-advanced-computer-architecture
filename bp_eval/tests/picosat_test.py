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

import os
import matplotlib.pyplot as plt
import bpredict


benchmark = '../benchmarks/picosat/picosat.alpha'
allargs = [
    ('../benchmarks/picosat/uf50-01.cnf', ),
#    ('../benchmarks/picosat/uf50-02.cnf', ),
#    ('../benchmarks/picosat/uf50-03.cnf', ),
#    ('../benchmarks/picosat/uf50-04.cnf', ),
#    ('../benchmarks/picosat/uf50-05.cnf', ),
#    ('../benchmarks/picosat/uuf50-01.cnf', ),
#    ('../benchmarks/picosat/uuf50-02.cnf', ),
#    ('../benchmarks/picosat/uuf50-03.cnf', ),
#    ('../benchmarks/picosat/uuf50-04.cnf', ),
#    ('../benchmarks/picosat/uuf50-05.cnf', ),
]

for args in allargs:
    pred = bpredict.Local2BitPredictor(8192)
    runner = bpredict.ExternalRunner(pred, benchmark, args=args)
    runner.run()

    predicted = runner.stats.find('condPredicted')[0].values[0]
    incorrect = runner.stats.find('condIncorrect')[0].values[0]

    print('Misprediction rate: %f' % (incorrect / predicted))

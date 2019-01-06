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


benchmark = '../benchmarks/sjeng/sjeng'
stdin = '\n'.join([
    'sd 3',
    'setboard rnbqkbnr/pp2pppp/2p5/3p4/2PP4/2N5/PP2PPPP/R1BQKBNR b KQkq - 1 3',
    'go',
    'go',
    'quit'
])

pred = '\n'.join([
        'branchPred = LocalBP()',
        'branchPred.localPredictorSize = 2048',
        'root.system.cpu[0].branchPred = branchPred',
    ])
runner = bpredict.InternalRunner(pred, benchmark, stdin=stdin)
runner.run()

print(runner.stdout)

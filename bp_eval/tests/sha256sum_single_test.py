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

import time
import matplotlib.pyplot as plt
import bpredict


benchmark = '../benchmarks/sha256sum/sha256sum'
args = ('../benchmarks/sha256sum/inputs/256K.bin', )

def run_test(runner):
    start = time.time()
    runner.run()

    predicted = runner.stats[0].find('condPredicted')[0].values[0]
    incorrect = runner.stats[0].find('condIncorrect')[0].values[0]

    print('    misprediction rate: %f' % (incorrect / predicted))
    print('    runtime: %f' % (time.time() - start))


# Run with the external TwoLevelAdaptive predictor (7168 bit)
pred = bpredict.TwoLevelAdaptiveTrainingPredictor(512, 10)
runner = bpredict.ExternalRunner(pred, benchmark, args)
print('External TwoLevelAdaptiveTrainingPredictor:')
run_test(runner)

# Run with the external Local2Bit predictor (8192 bit)
pred = bpredict.Local2BitPredictor(4096)
runner = bpredict.ExternalRunner(pred, benchmark, args)
print('External Local2BitPredictor:')
run_test(runner)

# Run with the perceptron predictor (8064 bit)
pred = bpredict.PerceptronPredictor(256, 36, 48, 64)
runner = bpredict.ExternalRunner(pred, benchmark, args)
print('External PerceptronPredictor:')
run_test(runner)

# Run with the combining predictor (4096 + 4032 bit)
pred_a = bpredict.Local2BitPredictor(2048)
pred_b = bpredict.PerceptronPredictor(256, 18, 48, 64)
pred = bpredict.Combining2BitPredictor(pred_a, pred_b, 1024, init=3)
runner = bpredict.ExternalRunner(pred, benchmark, args)
print('External Combining2BitPredictor (4K + 4K + 2K):')
run_test(runner)

# Run with the combining predictor (8192 + 8064 bit)
pred_a = bpredict.Local2BitPredictor(4096)
pred_b = bpredict.PerceptronPredictor(256, 36, 48, 64)
pred = bpredict.Combining2BitPredictor(pred_a, pred_b, 1024, init=3)
runner = bpredict.ExternalRunner(pred, benchmark, args)
print('External Combining2BitPredictor (8K + 8K + 2K):')
run_test(runner)


# Run with the internal predictor.
pred = '\n'.join([
        'branchPred = LocalBP()',
        'branchPred.localPredictorSize = 4096',
        'branchPred.localCtrBits = 2',
        'root.system.cpu[0].branchPred = branchPred',
    ])
runner = bpredict.InternalRunner(pred, benchmark, args)
print('Internal Local2BitPredictor:')
run_test(runner)

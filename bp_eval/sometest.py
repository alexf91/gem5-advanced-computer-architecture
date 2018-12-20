import bpredict
import bpredict.predictors

pred = bpredict.predictors.DummyPredictor()

runner = bpredict.BenchmarkRunner(
            pred,
            'benchmarks/blackscholes/blackscholes.alpha', 1,
            'benchmarks/blackscholes/blackscholes.test.input',
            '/dev/null'
         )

runner.run()
print(runner.stats)

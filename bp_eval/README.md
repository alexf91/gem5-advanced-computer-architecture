# Branch Prediction Evaluation

## bpredict

`bpredict` is a Python package that allows running branch prediction algorithms
written in both Python and C++. When a Python predictor is executed, gem5 runs
a branch predictor called `ExternalBP`, which communicates with the Python
predictor over Unix Domain Sockets.

## Benchmarks

Precompiled benchmark applications include `sha256sum` from the GNU core utils
and PicoSAT.

# Branch Prediction Evaluation

## Building gem5

There's likely a bug in gem5 or in GCC 8.2 that prohibits the use of the
AtomicSimpleCPU. For this reason, gem5 is built with Clang.
```
CC=clang CXX=clang++ scons -j4 build/ALPHA/gem5.opt
```
The build process shows a lot of warnings, so the `-Werror` flag was disabled
in the build configuration.

## bpredict

`bpredict` is a Python package that allows running branch prediction algorithms
written in both Python and C++. When a Python predictor is executed, gem5 runs
a branch predictor called `ExternalBP`, which communicates with the Python
predictor over Unix Domain Sockets.

## Benchmarks

The benchmark applications include `sha256sum` from the GNU core utils, the
PicoSAT solver, blackscholes and streamcluster. The latter two are from the
PARSEC 3.0 collection.
The benchmarks are either precompiled or are built by executing the `build.sh`
script in the benchmark directory.

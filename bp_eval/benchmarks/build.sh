#!/bin/sh

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd -P)"

export CC="$SCRIPT_DIR/../toolchain/alphaev67-unknown-linux-gnu/bin/alphaev67-unknown-linux-gnu-gcc"
export CXX="$SCRIPT_DIR/../toolchain/alphaev67-unknown-linux-gnu/bin/alphaev67-unknown-linux-gnu-g++"
export CFLAGS=-static -O3
export CXXFLAGS=-static -O3

# Build hello world example
make -C hello-world

# Build PicoSAT
(cd picosat && ./configure.sh -static && make)

# Build the streamcluster benchmark
make -C streamcluster

# Build the blackscholes benchmark
make -C blackscholes

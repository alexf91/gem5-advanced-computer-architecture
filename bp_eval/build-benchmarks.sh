#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd -P)"

DOWNLOAD_DIR=$SCRIPT_DIR/.downloads
TOOLCHAIN_DIR=$SCRIPT_DIR/toolchain
BUILD_DIR=$SCRIPT_DIR/.build
BENCHMARKS_DIR=$SCRIPT_DIR/benchmarks

mkdir -p $DOWNLOAD_DIR && cd $DOWNLOAD_DIR

# Get the source archives of the benchmark applications
wget -nc 'http://eddylab.org/software/hmmer/hmmer-2.3.2.tar.gz'
wget -nc 'http://fmv.jku.at/picosat/picosat-965.tar.gz'
wget -nc 'https://ftp.gnu.org/gnu/coreutils/coreutils-8.1.tar.gz'
wget -nc 'http://parsec.cs.princeton.edu/download/3.0/parsec-3.0-core.tar.gz'
wget -nc 'https://github.com/official-stockfish/Stockfish/archive/sf_2.3.1.tar.gz'

# Build the benchmark applications if they haven't been built before
export PATH=$TOOLCHAIN_DIR/alphaev67-unknown-linux-gnu/bin:$PATH
mkdir -p $BUILD_DIR

cd $BENCHMARKS_DIR/hello-world
alphaev67-unknown-linux-gnu-gcc -Wall -static -o hello-world hello-world.c

cd $BUILD_DIR
if [ ! -d hmmer-2.3.2 ]; then
    tar xf "$DOWNLOAD_DIR/hmmer-2.3.2.tar.gz" && cd hmmer-2.3.2
    ./configure --host=alphaev67-unknown-linux-gnu
    make CFLAGS='-static -O2' -j3
    cp src/hmmsearch $BENCHMARKS_DIR/hmmr/
fi

cd $BUILD_DIR
if [ ! -d picosat-965 ]; then
    tar xf "$DOWNLOAD_DIR/picosat-965.tar.gz" && cd picosat-965
    ./configure.sh --static
    make CC=alphaev67-unknown-linux-gnu-gcc -j3
    cp picosat $BENCHMARKS_DIR/picosat/
fi

cd $BUILD_DIR
if [ ! -d coreutils-8.1 ]; then
    tar xf "$DOWNLOAD_DIR/coreutils-8.1.tar.gz" && cd coreutils-8.1
    ./configure --host=alphaev67-unknown-linux-gnu
    make CFLAGS='-static -O2' -j3
    cp src/sha256sum $BENCHMARKS_DIR/sha256sum/
fi

cd $BUILD_DIR
if [ ! -d parsec-3.0 ]; then
    tar xf "$DOWNLOAD_DIR/parsec-3.0-core.tar.gz"

    cd $BUILD_DIR/parsec-3.0/pkgs/apps/blackscholes/src
    alphaev67-unknown-linux-gnu-g++ -DNCO=4 -O2 blackscholes.c \
        -o blackscholes -static
    cp blackscholes $BENCHMARKS_DIR/blackscholes/

    cd $BUILD_DIR/parsec-3.0/pkgs/kernels/streamcluster/src
    make CXX=alphaev67-unknown-linux-gnu-g++ CXXFLAGS='-static -O2'
    cp streamcluster $BENCHMARKS_DIR/streamcluster/
fi

cd $BUILD_DIR
if [ ! -d Stockfish-sf_2.3.1 ]; then
    tar xf "$DOWNLOAD_DIR/sf_2.3.1.tar.gz" && cd Stockfish-sf_2.3.1/src
    make build EXTRACXXFLAGS+=-static \
               EXTRALDFLAGS=-static \
               CXX=alphaev67-unknown-linux-gnu-g++ COMP=gcc ARCH=general-64 -j3
    cp stockfish $BENCHMARKS_DIR/stockfish/
fi

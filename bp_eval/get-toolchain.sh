#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")"; pwd -P)"

DOWNLOAD_DIR=$SCRIPT_DIR/.downloads
TOOLCHAIN_DIR=$SCRIPT_DIR/toolchain

mkdir -p $DOWNLOAD_DIR && cd $DOWNLOAD_DIR

# Download all necessary archives and files
wget -nc 'http://www.m5sim.org/dist/current/alphaev67-unknown-linux-gnu.tar.bz2'
wget -nc 'http://www.m5sim.org/dist/current/m5_system_2.0b3.tar.bz2'
wget -nc 'http://www.cs.utexas.edu/~parsec_m5/vmlinux_2.6.27-gcc_4.3.4'
wget -nc 'http://www.cs.utexas.edu/~parsec_m5/tsb_osfpal'
wget -nc 'http://www.cs.utexas.edu/~parsec_m5/linux-parsec-2-1-m5-with-test-inputs.img.bz2'

# Don't overwrite anything
if [ -d "$TOOLCHAIN_DIR" ]; then
    echo "Toolchain directory already exists"
    exit 1
fi
mkdir -p $TOOLCHAIN_DIR && cd $TOOLCHAIN_DIR

# Extract everything
tar xf "$DOWNLOAD_DIR/alphaev67-unknown-linux-gnu.tar.bz2"
tar xf "$DOWNLOAD_DIR/m5_system_2.0b3.tar.bz2"
cp "$DOWNLOAD_DIR/vmlinux_2.6.27-gcc_4.3.4" "$TOOLCHAIN_DIR/m5_system_2.0b3/binaries/vmlinux"
cp "$DOWNLOAD_DIR/tsb_osfpal" "$TOOLCHAIN_DIR/m5_system_2.0b3/binaries/ts_osfpal"
bzcat "$DOWNLOAD_DIR/linux-parsec-2-1-m5-with-test-inputs.img.bz2" > \
      "$TOOLCHAIN_DIR/m5_system_2.0b3/disks/linux-parsec.img"

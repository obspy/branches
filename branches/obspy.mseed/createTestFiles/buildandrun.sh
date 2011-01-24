#!/bin/bash

make clean
make all
./fullASCII_littleEndian
./smallASCII_littleEndian
./int32Steim1_littleEndian
./int32Steim2_littleEndian
./int32Int32_littleEndian
./int16Int16_littleEndian
./float32Float32_littleEndian
./float64Float64_littleEndian
./fullASCII_bigEndian
./smallASCII_bigEndian
./int32Steim1_bigEndian
./int32Steim2_bigEndian
./int32Int32_bigEndian
./int16Int16_bigEndian
./float32Float32_bigEndian
./float64Float64_bigEndian
make clean
rm -rf output
mkdir output
mv *.mseed output

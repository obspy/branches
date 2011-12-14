#! /bin/tcsh

# This script runs SAC program for instrument correction
# Instrument Correction will be done for all waveforms in the BH_RAW folder
# Response files will be loaded from Resp folder

# Instrument Correction has three main steps:
# 1) RTR: remove the trend
# 2) tapering
# 3) pre-filtering and deconvolution of Resp file from Raw counts

# Address of waveform and resp file:
echo $1
echo $2
echo "setbb resp $2 \n"
#echo "r $1 \n p1" | sac

# Go to the folder that all corrected seismograms with SAC will be saved
cd "$3/IRIS/BH_SAC"

# Check whether mtrans exists in the folder or not
if(-e mtrans) then
  rm -f mtrans
endif

# Fill out the mtrans with required SAC commands

echo "#! /bin/tcsh" > mtrans
echo "sac <<eof" >> mtrans
echo "setbb resp $2" >> mtrans
echo "r  $1" >> mtrans
echo "rtrend" >> mtrans
echo "taper" >> mtrans
echo "trans from evalresp fname %resp to none freqlim 0.008 0.012 3.0 4.0" >> mtrans
echo " w ./$4" >> mtrans

# one extra line for LMU: "quit"
echo "quit" >> mtrans
echo "eof" >> mtrans
chmod a+x mtrans

./mtrans

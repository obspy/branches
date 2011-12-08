#! /bin/tcsh


echo $1
echo $2
echo "setbb resp $2 \n"
#echo "r $1 \n p1" | sac

cd "$3/IRIS"

mkdir sac_folder

cd "./sac_folder"
if(-e mtrans) then
  rm -f mtrans
endif

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

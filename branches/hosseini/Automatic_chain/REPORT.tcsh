#!/bin/tcsh

set add = $1


set rep_IRIS = "$add/*/*/IRIS/info/report_st"
set rep_ARC = "$add/*/*/ARC/info/report_st"

set exc_IRIS = "$add/*/*/IRIS/Excep_py/excep_iris"
set exc_ARC = "$add/*/*/ARC/Excep_py/excep_arc"

set DQ_IRIS = "$add/*/*/IRIS/QC/DQ"
set DQ_ARC = "$add/*/*/ARC/QC/DQ"

set TQ_IRIS = "$add/*/*/IRIS/QC/TQ"
set TQ_ARC = "$add/*/*/ARC/QC/TQ"

set GAP_IRIS = "$add/*/*/IRIS/QC/gap"
set GAP_ARC = "$add/*/*/ARC/QC/gap"


set add2 = $2

cat $rep_IRIS >> $add2/report_iris.txt
cat $rep_ARC >> $add2/report_arc.txt

cat $exc_IRIS >> $add2/excep_iris.txt
cat $exc_ARC >> $add2/excep_arc.txt

cat $DQ_IRIS >> $add2/DQ_iris.txt
cat $DQ_ARC >> $add2/DQ_arc.txt

cat $TQ_IRIS >> $add2/TQ_iris.txt
cat $TQ_ARC >> $add2/TQ_arc.txt

cat $GAP_IRIS >> $add2/gap_iris.txt
cat $GAP_ARC >> $add2/gap_arc.txt

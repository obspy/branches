#!/bin/tcsh

set add = "/import/neptun-radler/hosseini-downloads/Data_old"


set rep_IRIS = "$add/*/*/IRIS/STATION/Report_station"
set rep_ARC = "$add/*/*/ARC/STATION/Report_station"

set exc_IRIS = "$add/*/*/IRIS/EXCEP/Exception_file_IRIS"
set exc_ARC = "$add/*/*/ARC/EXCEP/Exception_file_ARC"

set DQ_IRIS = "$add/*/*/IRIS/QC/DataQuality"
set DQ_ARC = "$add/*/*/ARC/QC/DataQuality"

set TQ_IRIS = "$add/*/*/IRIS/QC/TimingQuality"
set TQ_ARC = "$add/*/*/ARC/QC/TimingQuality"

set GAP_IRIS = "$add/*/*/IRIS/QC/GAP"
set GAP_ARC = "$add/*/*/ARC/QC/GAP"

cat $rep_IRIS >> ~/Desktop/report/report_IRIS.txt
cat $rep_ARC >> ~/Desktop/report/report_ARC.txt

cat $exc_IRIS >> ~/Desktop/report/excep_IRIS.txt
cat $exc_ARC >> ~/Desktop/report/excep_ARC.txt

cat $DQ_IRIS >> ~/Desktop/report/DQ_IRIS.txt
cat $DQ_ARC >> ~/Desktop/report/DQ_ARC.txt

cat $TQ_IRIS >> ~/Desktop/report/TQ_IRIS.txt
cat $TQ_ARC >> ~/Desktop/report/TQ_ARC.txt

cat $GAP_IRIS >> ~/Desktop/report/GAP_IRIS.txt
cat $GAP_ARC >> ~/Desktop/report/GAP_ARC.txt

@echo off
SETLOCAL

REM
REM Run vcvars32.bat in VS2008 command line for 32 bit!
REM Run vcvars64.bat in VS2008 command line for 64 bit!
REM

REM
REM Set your correct python interpreter here or just use virtualenv.
set PYTHON=python
REM


FOR %%M IN (core mseed gse2 signal imaging arclink fissures sac seisan seishub wav xseed sh segy) DO (
cd ..\..
cd trunk\obspy.%%M
echo === obspy.%%M ===
cp obspy\%%M\README.txt .
%PYTHON% setup.py -q release sdist
IF [%1]==[] (
  %PYTHON% setup.py -q release build bdist_wininst --user-access-control=auto
  %PYTHON% setup.py -q release build bdist_egg
) ELSE (
  %PYTHON% setup.py -q release build -c mingw32 bdist_wininst
  %PYTHON% setup.py -q release build -c mingw32 bdist_egg
)
del README.txt
echo OK
)

cd ..\..
cd branches\pypi

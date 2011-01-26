@echo off
SETLOCAL

set WORKSPACE="D:\Workspace\obspy"
set HOME=%HOMEDRIVE%%HOMEPATH%

echo Building ...
FOR %%M IN (core mseed gse2 signal imaging arclink fissures sac seisan seishub wav xseed sh segy) DO (
cd /d %WORKSPACE%
cd obspy.%%M
rmdir /S /Q dist >NUL 2>NUL
echo === obspy.%%M ===
cp obspy\%%M\README.txt .
python setup.py -q release sdist upload
IF [%1]==[] (
  python setup.py -q release build bdist_wininst --user-access-control=auto upload
  python setup.py -q release build bdist_egg upload
) ELSE (
  python setup.py -q release build -c mingw32 bdist_wininst upload
  python setup.py -q release build -c mingw32 bdist_egg upload
)
del README.txt
echo OK
rmdir /S /Q dist >NUL 2>NUL
)

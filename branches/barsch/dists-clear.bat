@echo off
SETLOCAL

echo Clearing ...
FOR %%M IN (core mseed gse2 signal imaging arclink fissures sac seisan seishub wav xseed sh segy) DO (
cd ..\..
cd trunk\obspy.%%M
rmdir /S /Q dist >NUL 2>NUL
rmdir /S /Q build >NUL 2>NUL
)
echo OK
echo:

cd ..\..
cd branches\pypi

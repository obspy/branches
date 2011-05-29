@echo off
SETLOCAL

set WORKSPACE="D:\Workspace\obspy"

echo Clearing ...
FOR %%M IN (core mseed gse2 signal imaging arclink fissures sac seisan seishub wav xseed sh segy db iris neries taup) DO (
cd /d %WORKSPACE%
cd obspy.%%M
rmdir /S /Q dist >NUL 2>NUL
rmdir /S /Q build >NUL 2>NUL
)
echo OK
echo:

@echo off
REM
REM Set your correct python interpreter here or just use virtualenv.
set PYTHON=python
REM

REM
REM build the new egg file in the dist directory
REM
%PYTHON% setup.py bdist_egg

REM
REM copy the egg into the win_installer directory
REM
copy dist\sm_analyser-0.1.0-py2.6.egg win_installer

REM
REM compile windows installer
REM
cd win_installer 
"C:\Program Files\NSIS\makensis" /V1 setup.nsi
cd ..

REM
REM copy installer to I-drive
REM
copy win_installer\setup.exe I:\SEISMO\yannikb\strong_motion_analyser

pause

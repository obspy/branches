@echo off

cd /d D:\Workspace\obspy\branches\pypi

PATH = C:\MinGW\bin\;C:\MinGW\include;%PATH%
echo Python 2.5.x - 32 bit
call "D:\Python\obspy\25\win32\Scripts\activate.bat"
del D:\Python\Python25-32bit.log 2> nul
call develop.bat mingw32 > D:\Python\Python25-32bit.log
call "D:\Python\obspy\25\win32\Scripts\deactivate.bat"
echo DONE
echo.

call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars32.bat"

echo Python 2.6.x - 32 bit
call "D:\Python\obspy\26\win32\Scripts\activate.bat"
del D:\Python\Python26-32bit.log 2> nul
call develop.bat > D:\Python\Python26-32bit.log
call "D:\Python\obspy\26\win32\Scripts\deactivate.bat"
echo DONE
echo.

echo Python 2.7.x - 32 bit
call "D:\Python\obspy\27\win32\Scripts\activate.bat"
del D:\Python\Python27-32bit.log 2> nul
call develop.bat > D:\Python\Python27-32bit.log
call "D:\Python\obspy\27\win32\Scripts\deactivate.bat"
echo DONE
echo.

call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat"

echo Python 2.6.x - 64 bit
call "D:\Python\obspy\26\x64\Scripts\activate.bat"
del D:\Python\Python26-64bit.log 2> nul
call develop.bat > D:\Python\Python26-64bit.log
call "D:\Python\obspy\26\x64\Scripts\deactivate.bat"
echo DONE
echo.

echo Python 2.7.x - 64 bit
call "D:\Python\obspy\27\x64\Scripts\activate.bat"
del D:\Python\Python27-64bit.log 2> nul
call develop.bat > D:\Python\Python27-64bit.log
call "D:\Python\obspy\27\x64\Scripts\deactivate.bat"
echo DONE
echo.

cd /d D:\Python

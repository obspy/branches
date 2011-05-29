@echo off

cd /d D:\Workspace\obspy-barsch

PATH = D:\Programme\MinGW\bin\;D:\Programme\MinGW\include;%PATH%
echo Python 2.5.x - 32 bit
call "D:\Python\obspy\25\win32\Scripts\activate.bat"
call _dists-build.bat mingw32
call "D:\Python\obspy\25\win32\Scripts\deactivate.bat"
echo DONE
echo:

call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars32.bat"

echo Python 2.6.x - 32 bit
call "D:\Python\obspy\26\win32\Scripts\activate.bat"
call _dists-build.bat
call "D:\Python\obspy\26\win32\Scripts\deactivate.bat"
echo DONE
echo:

echo Python 2.7.x - 32 bit
call "D:\Python\obspy\27\win32\Scripts\activate.bat"
call _dists-build.bat
call "D:\Python\obspy\27\win32\Scripts\deactivate.bat"
echo DONE
echo:

call "C:\Program Files (x86)\Microsoft Visual Studio 9.0\VC\bin\vcvars64.bat"

echo Python 2.6.x - 64 bit
call "D:\Python\obspy\26\x64\Scripts\activate.bat"
call _dists-build.bat
call "D:\Python\obspy\26\x64\Scripts\deactivate.bat"
echo DONE
echo:

echo Python 2.7.x - 64 bit
call "D:\Python\obspy\27\x64\Scripts\activate.bat"
call _dists-build.bat
call "D:\Python\obspy\27\x64\Scripts\deactivate.bat"
echo DONE
echo:

cd /d D:\Workspace\obspy-barsch

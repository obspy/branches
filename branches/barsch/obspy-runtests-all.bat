@echo off

echo Python 2.5.x - 32 bit
call "D:\Python\obspy\25\win32\Scripts\activate.bat"
call "D:\Python\obspy\25\win32\Scripts\obspy-runtests.exe" %*
call "D:\Python\obspy\25\win32\Scripts\deactivate.bat"

echo Python 2.6.x - 32 bit
call "D:\Python\obspy\26\win32\Scripts\activate.bat"
call "D:\Python\obspy\26\win32\Scripts\obspy-runtests.exe" %*
call "D:\Python\obspy\26\win32\Scripts\deactivate.bat"

echo Python 2.7.x - 32 bit
call "D:\Python\obspy\27\win32\Scripts\activate.bat"
call "D:\Python\obspy\27\win32\Scripts\obspy-runtests.exe" %*
call "D:\Python\obspy\27\win32\Scripts\deactivate.bat"

echo Python 2.6.x - 64 bit
call "D:\Python\obspy\26\x64\Scripts\activate.bat"
call "D:\Python\obspy\26\x64\Scripts\obspy-runtests.exe" %*
call "D:\Python\obspy\26\x64\Scripts\deactivate.bat"

echo Python 2.7.x - 64 bit
call "D:\Python\obspy\27\x64\Scripts\activate.bat"
call "D:\Python\obspy\27\x64\Scripts\obspy-runtests.exe" %*
call "D:\Python\obspy\27\x64\Scripts\deactivate.bat"

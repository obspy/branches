!include "LogicLib.nsh"
!include "EnvVarUpdate.nsh"
!include "x64.nsh"
;!include MUI2.nsh

outFile "setup.exe" 
Name SmAnalyser
Var PythonDirectory
;Var StartMenuGroup


RequestExecutionLevel admin

# Download URLs
!define PYTHON_WIN32 "http://www.python.org/ftp/python/2.6.6/python-2.6.6.msi"
!define PYTHON_WIN64 "http://www.python.org/ftp/python/2.6.6/python-2.6.6.amd64.msi"
!define DISTRIBUTE_URL "http://python-distribute.org/distribute_setup.py"
!define DISTRIBUTE_FILE "distribute_setup.py"
!define NUMPY_WIN32 "http://www.obspy.org/www/files/numpy-1.5.1-win32-superpack-python2.6.exe"
!define NUMPY_WIN64 "http://www.obspy.org/www/files/numpy-1.5.1.win-amd64-py2.6.exe"
!define NUMPY_FILE "numpy-1.5.1-python2.6.exe"
!define SCIPY_WIN32 "http://www.obspy.org/www/files/scipy-0.8.0-win32-superpack-python2.6.exe"
!define SCIPY_WIN64 "http://www.obspy.org/www/files/scipy-0.8.0.win-amd64-py2.6.exe"
!define SCIPY_FILE "scipy-0.8.0-python2.6.exe"
!define MATPLOTLIB_WIN32 "http://www.obspy.org/www/files/matplotlib-1.0.0.win32-py2.6.exe"
!define MATPLOTLIB_WIN64 "http://www.obspy.org/www/files/matplotlib-1.0.0.win-amd64-py2.6.exe"
!define MATPLOTLIB_FILE "matplotlib-1.0.0-python2.6.exe"

# strong motion analyser package
!define INSTALLEGG "sm_analyser-0.1.0-py2.6.egg"


;!insertmacro MUI_PAGE_DIRECTORY
;!insertmacro MUI_PAGE_STARTMENU Application $StartMenuGroup
;!insertmacro MUI_PAGE_INSTFILES
;!insertmacro MUI_PAGE_FINISH
;!insertmacro MUI_UNPAGE_CONFIRM
;!insertmacro MUI_UNPAGE_INSTFILES

# Installer languages
;!insertmacro MUI_LANGUAGE English
;!insertmacro MUI_LANGUAGE German

Function InstallPython
    # check for Python 2.6.x
    ReadRegStr $2 HKLM "SOFTWARE\Python\PythonCore\2.6\InstallPath\InstallGroup" ""
    ${If} $2 == 'Python 2.6'
        ReadRegStr $2 HKLM "SOFTWARE\Python\PythonCore\2.6\InstallPath\" ""
        strcpy $PythonDirectory $2
        DetailPrint "Python 2.6.x installation found at $PythonDirectory."
    ${Else}
        DetailPrint "No existing Python 2.6.x installation found!"
        MessageBox MB_OKCANCEL "Python 2.6.5 will now be downloaded and installed." IDOK ok IDCANCEL cancel  
        ok:
        	# fetch latest version
        	StrCpy $2 "$TEMP\python-2.6.5.msi"
        	IfFileExists $2 installpy 0
        	${If} ${RunningX64}
        	    DetailPrint "Downloading ${PYTHON_WIN64}"
        	    nsisdl::download /TIMEOUT=30000 ${PYTHON_WIN64} $2
        	    GoTo installpy
        	${Else}
        	    DetailPrint "Downloading ${PYTHON_WIN32}"
        	    nsisdl::download /TIMEOUT=30000 ${PYTHON_WIN32} $2
        	    GoTo installpy
    		${EndIf}
        	Pop $R0 ;Get the return value
        	    StrCmp $R0 "success" +3
        	    MessageBox MB_OK "Download failed: $R0"
        	    Quit
       	cancel:
       		Quit
       	installpy:
	    	DetailPrint $2
        	ExecWait '"msiexec" /i "$TEMP\python-2.6.5.msi"'
        	#Delete $2
     		# set Python directory
        	ReadRegStr $2 HKLM "SOFTWARE\Python\PythonCore\2.6\InstallPath\" ""
        	MessageBox MB_OK $2
        	strcpy $PythonDirectory $2
    ${EndIf}
    # check PATH
    ${EnvVarUpdate} $0 "PATH" "P" "HKLM" "$PythonDirectory"
    ${EnvVarUpdate} $0 "PATH" "P" "HKLM" "$PythonDirectory\Scripts"
	
FunctionEnd


Function InstallDependencies
    #
    # distribute
    #
    nsExec::Exec '"$PythonDirectory\python.exe" -c "import setuptools"'
    Pop $R0
    ${If} $R0 == 0
        DetailPrint "Setuptools/distribute already installed."
    ${Else}
        strcpy $2 "$TEMP\${DISTRIBUTE_FILE}"
        DetailPrint "Downloading ${DISTRIBUTE_URL}"
        nsisdl::download /TIMEOUT=30000 ${DISTRIBUTE_URL} $2
        Pop $R0 ;Get the return value
            StrCmp $R0 "success" +3
            MessageBox MB_OK "Download failed: $R0"
            Quit
        DetailPrint "Running python ${DISTRIBUTE_FILE}"
        nsExec::Exec '"$PythonDirectory\python.exe" "$2"'
        Delete "$TEMP\distribute_setup.py"
    ${EndIf}
    #
    # NumPy
    #
    nsExec::Exec '"$PythonDirectory\python.exe" -c "import numpy"'
    Pop $R0
    ${If} $R0 == 0
        DetailPrint "NumPy already installed."
    ${Else}
        strcpy $2 "$TEMP\${NUMPY_FILE}"
        ${If} ${RunningX64}
            DetailPrint "Downloading ${NUMPY_WIN64}"
            nsisdl::download /TIMEOUT=30000 ${NUMPY_WIN64} $2
        ${Else}
            DetailPrint "Downloading ${NUMPY_WIN32}"
            nsisdl::download /TIMEOUT=30000 ${NUMPY_WIN32} $2
        ${EndIf}
        Pop $R0 ;Get the return value
            StrCmp $R0 "success" +3
            MessageBox MB_OK "Download failed: $R0"
            Quit
        ExecWait $2
        Delete $2
    ${EndIf}
    # SciPy
    nsExec::Exec '"$PythonDirectory\python.exe" -c "import scipy"'
    Pop $R0
    ${If} $R0 == 0
        DetailPrint "SciPy already installed."
    ${Else}
        strcpy $2 "$TEMP\${SCIPY_FILE}"
        ${If} ${RunningX64}
            DetailPrint "Downloading ${SCIPY_WIN64}"
            nsisdl::download /TIMEOUT=30000 ${SCIPY_WIN64} $2
        ${Else}
            DetailPrint "Downloading ${SCIPY_WIN32}"
            nsisdl::download /TIMEOUT=30000 ${SCIPY_WIN32} $2
        ${EndIf}
        Pop $R0 ;Get the return value
            StrCmp $R0 "success" +3
            MessageBox MB_OK "Download failed: $R0"
            Quit
        ExecWait $2
        Delete $2
    ${EndIf}
    # MatPlotLib
    nsExec::Exec '"$PythonDirectory\python.exe" -c "import matplotlib"'
    Pop $R0
    ${If} $R0 == 0
        DetailPrint "matplotlib already installed."
    ${Else}
        strcpy $2 "$TEMP\${MATPLOTLIB_FILE}"
        ${If} ${RunningX64}
            DetailPrint "Downloading ${MATPLOTLIB_WIN64}"
            nsisdl::download /TIMEOUT=30000 ${MATPLOTLIB_WIN64} $2
        ${Else}
            DetailPrint "Downloading ${MATPLOTLIB_WIN32}"
            nsisdl::download /TIMEOUT=30000 ${MATPLOTLIB_WIN32} $2
        ${EndIf}
        Pop $R0 ;Get the return value
            StrCmp $R0 "success" +3
            MessageBox MB_OK "Download failed: $R0"
            Quit
        ExecWait $2
        Delete $2
    ${EndIf}
    # obspy.core
    nsExec::Exec '"$PythonDirectory\python.exe" -c "import obspy.core"'
    Pop $R0
    ${If} $R0 == 0
        DetailPrint "obspy.core already installed."
    ${Else}
	    DetailPrint "Running easy_install.exe -U obspy.core"
	    nsExec::Exec '"$PythonDirectory\Scripts\easy_install.exe" -U "obspy.core"'
    ${EndIf}
FunctionEnd

Function InstallSmAnalyser
	setOutPath $TEMP
	file ${INSTALLEGG}
    DetailPrint "Running easy_install.exe -U ${INSTALLEGG}"
 	nsExec::Exec '"$PythonDirectory\Scripts\easy_install.exe" -U ${INSTALLEGG}'
FunctionEnd


section
Call InstallPython
Call InstallDependencies
Call InstallSmAnalyser
SectionEnd



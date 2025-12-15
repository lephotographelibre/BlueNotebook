@echo off
REM Launch script for BlueNotebook on Windows

REM Move to the script directory to ensure relative paths work
cd /d "%~dp0"

set PYTHON_VERSION=3.11.9
set VENV_NAME=.venv_bluenotebook
set VENV_DIR=bluenotebook\%VENV_NAME%

echo "🚀 BlueNotebook launch... ---"


echo "--- copy requirements.txt ---"
COPY requirements_windows3.11.9.txt requirements.txt /A /V /Y



REM --- Environment Verification ---

REM 1. Check if pyenv-win is installed
if not exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo " ❌ ERROR: pyenv-win is not detected."
    echo "Please install it to manage Python versions: https://github.com/pyenv-win/pyenv-win#installation"
    REM ++++ Powershell Admin system: Windows-X Terminal (Administrateur
    REM PS C:\Users\jmdig> Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Reopen PowerShell
    REM PS C:\Users\jmdig> pyenv --version

    pause
    exit /b 1
)

REM Add pyenv to PATH for this session
set "PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%USERPROFILE%\.pyenv\pyenv-win\shims;%PATH%"

REM 2. Check if the Python version is installed
pyenv versions | findstr /C:"%PYTHON_VERSION%" > nul
if %errorlevel% neq 0 (
    echo "❌ Python %PYTHON_VERSION% is not installed via pyenv."
    echo "Attempting to install..."
    pyenv install %PYTHON_VERSION% || (
        echo "❌ ERROR: The installation of Python %PYTHON_VERSION% failed."
        pause
        exit /b 1
    )
)

REM 3. Create the virtual environment if it doesn't exist
if not exist "%VENV_DIR%" (
    echo "Creating the virtual environment '%VENV_DIR%'..."
    "%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\python.exe" -m venv %VENV_DIR%
    if %errorlevel% neq 0 ( echo "❌ ERROR: The creation of the virtual environment failed." & pause & exit /b 1 )
)

set "VENV_PYTHON=%CD%\%VENV_DIR%\Scripts\python.exe"

REM 5. Install/Verify dependencies
echo "Verification and installation of dependencies from requirements.txt...""
"%VENV_PYTHON%" -m pip install --upgrade pip
if %errorlevel% neq 0 ( echo "❌ ERROR: The pip update failed." & pause & exit /b 1 )



REM Uses requirements.txt located at the root of the BlueNotebook folder
"%VENV_PYTHON%" -m pip install -r "requirements.txt"
if %errorlevel% neq 0 ( echo "❌ ERROR: The dependency installation failed." & pause & exit /b 1 )

echo "✅ Dependencies up to date."
 

REM --- Application Launch ---
echo "🚀 BlueNotebook App launch... ---"

REM --- PATH Configuration for Cairo library (required for WeasyPrint/CairoSVG) ---
REM Looks for Cairo installation path (GTK Runtime or msys64)
set "CAIRO_PATH="
if exist "C:\Program Files\GTK3-Runtime Win64\bin" set "CAIRO_PATH=C:\Program Files\GTK3-Runtime Win64\bin"
if not defined CAIRO_PATH if exist "C:\msys64\mingw64\bin" set "CAIRO_PATH=C:\msys64\mingw64\bin"
if not defined CAIRO_PATH if exist "%USERPROFILE%\msys64\mingw64\bin" set "CAIRO_PATH=%USERPROFILE%\msys64\mingw64\bin"

if defined CAIRO_PATH (
    echo "✅ Added '%CAIRO_PATH%' to the PATH for Cairo."
    set "PATH=%CAIRO_PATH%;%PATH%"
) else (
    echo "❌ WARNING: Unable to find the Cairo library (GTK3 or msys64). PDF/SVG export may fail."
)

REM --- Setting Journal Directory and Locale ---
set "JOURNAL_DIRECTORY=E:\Dropbox\BlueNotebookJournal"
REM set "BLUENOTEBOOK_LOCALE=fr_FR"
"%VENV_PYTHON%" -V
"%VENV_PYTHON%" -m pip -V
REM "%VENV_PYTHON%" -m pip install pyqt5-tools
REM Passes all arguments (%*) to the python script
cd bluenotebook
call "%VENV_PYTHON%" main.py %*
if %errorlevel% neq 0 ( echo "❌  ERROR: Launching main.py failed." & pause & exit /b 1 )
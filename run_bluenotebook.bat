@echo off
REM Script de lancement pour BlueNotebook sur Windows
cd bluenotebook
set PYTHON_VERSION=3.11.9
set VENV_NAME=.venv_bluenotebook

echo "🚀 BlueNotebook launch... ---"


echo "--- copy requirements.txt ---"
COPY ..\requirements_windows3.11.9.txt ..\requirements.txt /A /V /Y



REM --- Verification de l'environnement ---

REM 1. Verifier si pyenv-win est installe
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

REM Ajouter pyenv au PATH pour cette session
set "PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%USERPROFILE%\.pyenv\pyenv-win\shims;%PATH%"

REM 2. Verifier si la version de Python est installee
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

REM 3. Creer l'environnement virtuel s'il n'existe pas
if not exist "%VENV_NAME%" (
    echo "Creating the virtual environment '%VENV_NAME%'..."
    "%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\python.exe" -m venv %VENV_NAME%
    if %errorlevel% neq 0 ( echo "❌ ERROR: The creation of the virtual environment failed." & pause & exit /b 1 )
)

set "VENV_PYTHON=%CD%\%VENV_NAME%\Scripts\python.exe"

REM 5. Installer/verifier les dependances
echo "Verification and installation of dependencies from requirements.txt...""
"%VENV_PYTHON%" -m pip install --upgrade pip
if %errorlevel% neq 0 ( echo "❌ ERROR: The pip update failed." & pause & exit /b 1 )



REM Utilise le requirements.txt situe a la racine du dossier BlueNotebook
"%VENV_PYTHON%" -m pip install -r "..\requirements.txt"
if %errorlevel% neq 0 ( echo "❌ ERROR: The dependency installation failed." & pause & exit /b 1 )

echo "✅ Dependencies up to date."
 

REM --- Lancement de l'application ---
echo "🚀 BlueNotebook App launch... ---"

REM --- Configuration du PATH pour la bibliotheque Cairo (necessaire pour WeasyPrint/CairoSVG) ---
REM Cherche le chemin d'installation de Cairo (GTK Runtime ou msys64)
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

REM --- Positionnement du repertoire du journal et locale---
set "JOURNAL_DIRECTORY=E:\Dropbox\BlueNotebookJournal"
REM set "BLUENOTEBOOK_LOCALE=fr_FR"
"%VENV_PYTHON%" -V
"%VENV_PYTHON%" -m pip -V
REM "%VENV_PYTHON%" -m pip install pyqt5-tools
REM Transmet tous les arguments (%*) au script python
call "%VENV_PYTHON%" main.py %*
if %errorlevel% neq 0 ( echo "❌  ERROR: Launching main.py failed." & pause & exit /b 1 )
@echo off
REM Script de lancement pour BlueNotebook sur Windows

set PYTHON_VERSION=3.11.9
set VENV_NAME=.venv_bluenotebook

echo "--- Lancement de BlueNotebook ---"


echo "--- copy requirements.txt ---"
COPY ..\requirements_windows3.11.9.txt ..\requirements.txt /A /V /Y
REM COPY ..\freeze_352_requirements.txt ..\requirements.txt /A /V /Y


REM --- Verification de l'environnement ---

REM 1. Verifier si pyenv-win est installe
if not exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo "ERREUR: pyenv-win n'est pas detecte."
    echo "Veuillez l'installer pour gerer les versions de Python : https://github.com/pyenv-win/pyenv-win#installation"
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
    echo "Python %PYTHON_VERSION% n'est pas installe via pyenv."
    echo "Tentative d'installation..."
    pyenv install %PYTHON_VERSION% || (
        echo "ERREUR: L'installation de Python %PYTHON_VERSION% a echoue."
        pause
        exit /b 1
    )
)

REM 3. Creer l'environnement virtuel s'il n'existe pas
if not exist "%VENV_NAME%" (
    echo "Creation de l'environnement virtuel '%VENV_NAME%'..."
    "%USERPROFILE%\.pyenv\pyenv-win\versions\%PYTHON_VERSION%\python.exe" -m venv %VENV_NAME%
    if %errorlevel% neq 0 ( echo "ERREUR: La creation de l'environnement virtuel a echoue." & pause & exit /b 1 )
)

set "VENV_PYTHON=%CD%\%VENV_NAME%\Scripts\python.exe"

REM 5. Installer/verifier les dependances
echo "Verification et installation des dependances depuis requirements.txt..."
"%VENV_PYTHON%" -m pip install --upgrade pip
if %errorlevel% neq 0 ( echo "ERREUR: La mise a jour de pip a echoue." & pause & exit /b 1 )



REM Utilise le requirements.txt situe a la racine du dossier BlueNotebook
"%VENV_PYTHON%" -m pip install -r "..\requirements.txt"
if %errorlevel% neq 0 ( echo "ERREUR: L'installation des dependances a echoue." & pause & exit /b 1 )

echo "Dependances a jour."
 

REM --- Lancement de l'application ---
echo "Lancement de l'application BlueNotebook..."

REM --- Configuration du PATH pour la bibliotheque Cairo (necessaire pour WeasyPrint/CairoSVG) ---
REM Cherche le chemin d'installation de Cairo (GTK Runtime ou msys64)
set "CAIRO_PATH="
if exist "C:\Program Files\GTK3-Runtime Win64\bin" set "CAIRO_PATH=C:\Program Files\GTK3-Runtime Win64\bin"
if not defined CAIRO_PATH if exist "C:\msys64\mingw64\bin" set "CAIRO_PATH=C:\msys64\mingw64\bin"
if not defined CAIRO_PATH if exist "%USERPROFILE%\msys64\mingw64\bin" set "CAIRO_PATH=%USERPROFILE%\msys64\mingw64\bin"

if defined CAIRO_PATH (
    echo "Ajout de '%CAIRO_PATH%' au PATH pour Cairo."
    set "PATH=%CAIRO_PATH%;%PATH%"
) else (
    echo "AVERTISSEMENT: Impossible de trouver la bibliotheque Cairo (GTK3 ou msys64). L'export PDF/SVG pourrait echouer."
)

REM --- Positionnement du repertoire du journal et locale---
REM set "JOURNAL_DIRECTORY=E:\Dropbox\BlueNotebookJournal"
REM set "BLUENOTEBOOK_LOCALE=fr_FR"
"%VENV_PYTHON%" -V
"%VENV_PYTHON%" -m pip -V
"%VENV_PYTHON%" -m pip install pyqt5-tools
REM Transmet tous les arguments (%*) au script python
call "%VENV_PYTHON%" main.py %*
if %errorlevel% neq 0 ( echo "ERREUR: Le lancement de main.py a echoue." & pause & exit /b 1 )
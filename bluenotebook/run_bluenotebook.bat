@echo off
REM Script de lancement pour BlueNotebook sur Windows

set PYTHON_VERSION=3.13.5
set VENV_NAME=.venv_bluenotebook

echo "--- Lancement de BlueNotebook ---"

REM --- Verification de l'environnement ---

REM 1. Verifier si pyenv-win est installe
if not exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo "ERREUR: pyenv-win n'est pas detecte."
    echo "Veuillez l'installer pour gerer les versions de Python : https://github.com/pyenv-win/pyenv-win#installation"
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
    pyenv install %PYTHON_VERSION%
)

REM 3. Creer l'environnement virtuel s'il n'existe pas
if not exist "%USERPROFILE%\.pyenv\pyenv-win\versions\%VENV_NAME%" (
    echo "Creation de l'environnement virtuel '%VENV_NAME%'..."
    pyenv virtualenv %PYTHON_VERSION% %VENV_NAME%
)

REM 4. Activer l'environnement virtuel
pyenv local %VENV_NAME%
echo "Environnement virtuel '%VENV_NAME%' active."

REM 5. Installer/verifier les dependances
echo "Verification et installation des dependances depuis requirements.txt..."
pip install -r requirements.txt 

echo "Dependances a jour."

REM --- Lancement de l'application ---
echo "Lancement de l'application BlueNotebook... V1.1.0"

REM Transmet tous les arguments (%*) au script python
python main.py %*
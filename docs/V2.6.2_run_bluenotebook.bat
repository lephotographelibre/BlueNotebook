@echo off
REM Script de lancement pour BlueNotebook sur Windows
REM Version 2.0 - Ajout de la gestion des variables d'environnement par défaut

setlocal

set "PYTHON_VERSION=3.13.5"
set "VENV_NAME=.venv_bluenotebook"

echo "--- Lancement de BlueNotebook ---"

REM --- Configuration de l'environnement (valeurs par défaut si non définies) ---

REM Répertoire du journal par défaut
if not defined JOURNAL_DIRECTORY (
    set "JOURNAL_DIRECTORY=%USERPROFILE%\BlueNotebookJournal"
)
echo "Répertoire du journal utilisé : %JOURNAL_DIRECTORY%"

REM Locale par défaut
if not defined BLUENOTEBOOK_LOCALE (
    set "BLUENOTEBOOK_LOCALE=fr_FR"
)
echo "Locale utilisée : %BLUENOTEBOOK_LOCALE%"

REM Répertoire de sauvegarde par défaut
if not defined BACKUP_DIRECTORY (
    set "BACKUP_DIRECTORY=%USERPROFILE%\Documents\BlueNotebook_Backups"
)
echo "Répertoire de sauvegarde par défaut : %BACKUP_DIRECTORY%"


REM --- Vérification de l'environnement ---

REM 1. Vérifier si pyenv-win est installé
if not exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo "ERREUR: pyenv-win n'est pas détecté."
    echo "Veuillez l'installer pour gérer les versions de Python : https://github.com/pyenv-win/pyenv-win#installation"
    pause
    exit /b 1
)

REM Ajouter pyenv au PATH pour cette session
set "PATH=%USERPROFILE%\.pyenv\pyenv-win\bin;%USERPROFILE%\.pyenv\pyenv-win\shims;%PATH%"

REM 2. Vérifier si la version de Python est installée
pyenv versions | findstr /C:"%PYTHON_VERSION%" > nul
if %errorlevel% neq 0 (
    echo "Python %PYTHON_VERSION% n'est pas installé via pyenv."
    echo "Tentative d'installation..."
    pyenv install %PYTHON_VERSION%
)

REM 3. Créer l'environnement virtuel s'il n'existe pas
if not exist "%USERPROFILE%\.pyenv\pyenv-win\versions\%VENV_NAME%" (
    echo "Création de l'environnement virtuel '%VENV_NAME%'..."
    pyenv virtualenv %PYTHON_VERSION% %VENV_NAME%
)

REM 4. Activer l'environnement virtuel
pyenv local %VENV_NAME%
echo "Environnement virtuel '%VENV_NAME%' activé."

REM 5. Installer/vérifier les dépendances
echo "Vérification et installation des dépendances depuis requirements.txt..."
pip install -r requirements.txt > nul

echo "Dépendances à jour."

REM --- Lancement de l'application ---
echo "Lancement de l'application BlueNotebook..."

REM Transmet tous les arguments (%*) au script python
python main.py %*

endlocal

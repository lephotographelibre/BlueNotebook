#!/bin/bash
# Script de lancement optimisé pour BlueNotebook sur Linux

set -e # Arrête le script si une commande échoue

# Se déplacer dans le répertoire du script pour que les chemins relatifs fonctionnent
cd "$(dirname "$0")"

QT_VERSION="5.15.11"
PYTHON_VERSION="3.13.5"
VENV_NAME=".venv_bluenotebook"
VENV_PATH="$(pyenv root)/versions/${VENV_NAME}"

echo "🚀 BlueNotebook launch..."

# --- Vérification de l'environnement ---

# 1. Vérifier si pyenv est installé
if ! command -v pyenv &> /dev/null; then
    echo "❌ Error: pyenv is not installed."
    echo "Please install it to manage Python versions: https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# --- Vérification de l'environnement (uniquement si nécessaire) ---
if [ ! -d "$VENV_PATH" ]; then
    echo "🛠️ Virtual environment '${VENV_NAME}' not found. Launching single installation..."
    
    # Initialiser pyenv pour l'installation
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"
    
    # Vérifier si la version de Python requise est disponible
    if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
        echo "🐍 The ${PYTHON_VERSION} version of Python is not installed. Attempting to install..."
        pyenv install "${PYTHON_VERSION}"
    fi
    
    # Créer l'environnement virtuel
    echo "📦 Creating the virtual environment..."
    pyenv virtualenv "${PYTHON_VERSION}" "${VENV_NAME}"
    
    # Forcer la réinstallation des dépendances après la création
    rm -f "${VENV_PATH}/.dependencies_installed"
fi

# --- Activation et Lancement ---
PYTHON_EXEC="${VENV_PATH}/bin/python"
PIP_EXEC="${VENV_PATH}/bin/pip"

# set requirements file
cp -p requirements_linux_3.13.5.txt requirements.txt

# Vérifier et installer les dépendances seulement si requirements.txt est plus récent
if [ "requirements.txt" -nt "${VENV_PATH}/.dependencies_installed" ]; then
    echo "📦 Dependency update..."
    "$PIP_EXEC" install -q -r requirements.txt
    touch "${VENV_PATH}/.dependencies_installed"
    echo "✅ Up-to-date dependencies."
fi

# --- Lancement de l'application ---
echo "🎨 Desktop environment detection for the Qt theme..."
PLATFORM_THEME=""


# La variable XDG_CURRENT_DESKTOP est la méthode la plus standard.
# On la vérifie en premier, en ignorant la casse.
case "${XDG_CURRENT_DESKTOP,,}" in
  *kde*|*plasma*)
    PLATFORM_THEME="kde"
    ;;
  *gnome*|*cinnamon*|*mate*|*xfce*)
    PLATFORM_THEME="gtk3"
    ;;
esac

if [ -n "$PLATFORM_THEME" ]; then
    export QT_QPA_PLATFORMTHEME=$PLATFORM_THEME
    echo "✅ Qt theme forced to '$PLATFORM_THEME' for better integration."
else
    echo "❗ Desktop environment not detected or not supported for a specific theme. Qt will choose the default."
fi


echo "" # Ligne vide pour l'aération
echo "📘 Launch of the BlueNotebook application..."

# locale -c  
# export BLUENOTEBOOK_LOCALE=de_DE

# Pour les tests de langue, décommentez et définissez la locale souhaitée (ex: "en_US", "fr_FR").
# Cette variable d'environnement a une priorité plus basse que le paramètre dans settings.json.
# La gestion de la locale est maintenant entièrement déléguée à main.py.
# export BLUENOTEBOOK_LOCALE="en_US"
# export JOURNAL_DIRECTORY="/home/jm/Work/BlueNotebook/"
export JOURNAL_DIRECTORY="/ssd/Dropbox/BlueNotebookJournal/"

# Définir un répertoire de sauvegarde par défaut (optionnel, décommenter pour utiliser)
# export BACKUP__DIRECTORY="/home/jm/Documents/BlueNotebook_Backups"
export BACKUP__DIRECTORY="/ssd/Dropbox/BlueNotebookBackup/"

cd bluenotebook && "$PYTHON_EXEC" main.py "$@"
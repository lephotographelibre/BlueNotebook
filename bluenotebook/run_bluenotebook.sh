#!/bin/bash

# Script de lancement pour BlueNotebook sur Linux

set -e # Arrête le script si une commande échoue

# Se déplacer dans le répertoire du script pour que les chemins relatifs fonctionnent
cd "$(dirname "$0")"

PYTHON_VERSION="3.13.5"
VENV_NAME=".venv_bluenotebook"

echo "🚀 Lancement de BlueNotebook..."

# --- Vérification de l'environnement ---

# 1. Vérifier si pyenv est installé
if ! command -v pyenv &> /dev/null; then
    echo "❌ Erreur : pyenv n'est pas installé."
    echo "Veuillez l'installer pour gérer les versions de Python : https://github.com/pyenv/pyenv#installation"
    exit 1
fi

# Initialiser pyenv dans le shell courant
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"

# 2. Vérifier si la version de Python requise est disponible
if ! pyenv versions --bare | grep -q "^${PYTHON_VERSION}$"; then
    echo "🐍 La version ${PYTHON_VERSION} de Python n'est pas installée avec pyenv."
    echo "Tentative d'installation..."
    pyenv install "${PYTHON_VERSION}"
fi

# 3. Créer l'environnement virtuel s'il n'existe pas
if ! pyenv virtualenvs --bare | grep -q "^${VENV_NAME}$"; then
    echo "🛠️  Création de l'environnement virtuel '${VENV_NAME}'..."
    pyenv virtualenv "${PYTHON_VERSION}" "${VENV_NAME}"
fi

# 4. Activer l'environnement virtuel
export PYENV_VERSION="${VENV_NAME}"
echo "✅ Environnement virtuel '${VENV_NAME}' activé."

# 5. Installer/vérifier les dépendances
echo "📦 Vérification et installation des dépendances depuis requirements.txt..."
pip install -q -r requirements.txt

echo "✅ Dépendances à jour."

# --- Lancement de l'application ---

echo "🎨 Détection de l'environnement de bureau pour le thème Qt..."
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
    echo "✅ Thème Qt forcé à '$PLATFORM_THEME' pour une meilleure intégration."
else
    echo "ℹ️ Environnement de bureau non détecté ou non supporté pour un thème spécifique. Qt choisira par défaut."
fi

echo "" # Ligne vide pour l'aération
echo "📘 Lancement de l'application BlueNotebook..."
# export JOURNAL_DIRECTORY="/home/jm/Work/BlueNotebook/"
export JOURNAL_DIRECTORY="/ssd/Dropbox/BlueNotebookJournal/"
# Définir un répertoire de sauvegarde par défaut (optionnel, décommenter pour utiliser)
# export BACKUP__DIRECTORY="/home/jm/Documents/BlueNotebook_Backups"
export BACKUP__DIRECTORY="/ssd/Dropbox/BlueNotebookBackup/"
python main.py "$@"
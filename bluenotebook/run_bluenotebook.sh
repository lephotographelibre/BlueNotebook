#!/bin/bash

# Script de lancement pour BlueNotebook sur Linux

set -e # Arrête le script si une commande échoue

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
pip install -r requirements.txt

echo "✅ Dépendances à jour."

# --- Lancement de l'application ---

echo "📘 Lancement de l'application BlueNotebook..."
# export JOURNAL_DIRECTORY="/home/jm/Work/BlueNotebook/"
export JOURNAL_DIRECTORY="/ssd/Dropbox/bluenotebook"
python main.py "$@"
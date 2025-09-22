#!/bin/bash

# Script d'installation pour BlueNotebook sur Linux

set -e # Arrête le script si une commande échoue

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Installation de BlueNotebook..."

# --- 1. Création du fichier .desktop ---
echo "Création du fichier bluenotebook.desktop..."

DESKTOP_FILE_CONTENT="[Desktop Entry]
Version=1.0
Name=BlueNotebook
GenericName[fr]=Éditeur de journal Markdown
Comment=Éditeur de journal Markdown avec aperçu en temps réel
Exec=${PROJECT_ROOT}/bluenotebook/run_bluenotebook.sh --journal \"/ssd/Dropbox/bluenotebook\"
Icon=${PROJECT_ROOT}/bluenotebook/resources/images/bluenotebook_256-x256_fond_blanc.png
Terminal=false
Type=Application
Categories=Office;TextEditor;Development;
StartupNotify=true
"

echo "$DESKTOP_FILE_CONTENT" > "${PROJECT_ROOT}/bluenotebook.desktop"

# --- 2. Installation du lanceur ---
echo "Installation du lanceur pour l'utilisateur courant..."
mkdir -p ~/.local/share/applications
cp "${PROJECT_ROOT}/bluenotebook.desktop" ~/.local/share/applications/

echo "✅ BlueNotebook a été installé avec succès !"
echo "Vous pouvez maintenant le trouver dans votre menu d'applications."
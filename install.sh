#!/bin/bash

# Installation script for BlueNotebook on Linux

set -e # Stop the script if a command fails

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🚀 Installing BlueNotebook..."

# --- 1. Creating the .desktop file ---
echo "Creating bluenotebook.desktop file..."

DESKTOP_FILE_CONTENT="[Desktop Entry]
Version=1.0
Name=BlueNotebook
GenericName=Markdown Journal Editor
GenericName[fr]=Éditeur de journal Markdown
Comment=Markdown journal editor with real-time preview
Exec=${PROJECT_ROOT}/run_bluenotebook.sh
Icon=${PROJECT_ROOT}/bluenotebook/resources/images/bluenotebook_256-x256_fond_blanc.png
Terminal=false
Type=Application
Categories=Office;TextEditor;Development;
StartupNotify=true
"

echo "$DESKTOP_FILE_CONTENT" > "${PROJECT_ROOT}/bluenotebook.desktop"

# --- 2. Installing the launcher ---
echo "Installing the launcher for the current user..."
mkdir -p ~/.local/share/applications
cp "${PROJECT_ROOT}/bluenotebook.desktop" ~/.local/share/applications/

echo "✅ BlueNotebook has been successfully installed!"
echo "You can now find it in your applications menu."
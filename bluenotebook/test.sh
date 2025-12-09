#!/bin/bash

# Script de lancement pour l'application de test i18n

set -e
cd "$(dirname "$0")"

echo "🚀 Lancement de l'application de test i18n..."

# On utilise python3, en supposant qu'il est dans le PATH.
python3 test_main.py
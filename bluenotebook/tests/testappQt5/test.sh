#!/bin/bash

# Script de lancement pour l'application de test i18n

set -e
cd "$(dirname "$0")"

echo "🚀 Lancement de l'application de test i18n..."

# On utilise python3, en supposant qu'il est dans le PATH de votre environnement virtuel.
# Si vous lancez ce script depuis un terminal où le venv n'est pas activé,
# il faudra peut-être utiliser le chemin complet vers le python de votre venv.
python3 test_main.py


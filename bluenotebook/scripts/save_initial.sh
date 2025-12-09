#!/bin/bash

# Script pour sauvegarder l'état initial des fichiers Python.
# Il copie chaque fichier .py en un fichier _initial.py.
# Les répertoires 'tests' et '.venv_bluenotebook' sont ignorés.

echo "--- Démarrage de la sauvegarde des fichiers .py en _initial.py ---"

# Le répertoire de départ pour la recherche est 'bluenotebook'
START_DIR="bluenotebook"

# Utilise find pour rechercher les fichiers .py
# -path 'bluenotebook/tests' -prune : ignore le répertoire 'tests'
# -path 'bluenotebook/.venv_bluenotebook' -prune : ignore le répertoire '.venv_bluenotebook'
# -print0 et read -d $'\0' sont utilisés pour une gestion robuste des noms de fichiers
# (gère les espaces et autres caractères spéciaux).

find "$START_DIR" -path "$START_DIR/tests" -prune -o -path "$START_DIR/.venv_bluenotebook" -prune -o -type f -name "*.py" -print0 | while IFS= read -r -d $'\0' py_file; do
    # Exclure les fichiers qui se terminent déjà par _initial.py pour éviter les copies en boucle
    if [[ "$py_file" == *"_initial.py" ]]; then
        continue
    fi
    
    # Construit le nouveau nom de fichier avec le suffixe _initial.py
    initial_file="${py_file%.py}_initial.py"
    
    # Copie le fichier en mode verbeux (-v) pour afficher l'opération
    cp -v "$py_file" "$initial_file"
done

echo ""
echo "--- Opération terminée. Les fichiers initiaux ont été sauvegardés. ---"

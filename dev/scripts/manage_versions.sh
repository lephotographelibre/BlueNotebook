#!/bin/bash

# Script pour organiser les fichiers de sauvegarde (_wrap.py et _initial.py)
# dans des arborescences de répertoires dédiées.

# S'assurer que le script est exécuté depuis la racine du projet
if [ ! -d "bluenotebook" ]; then
    echo "Erreur : Ce script doit être exécuté depuis la racine du projet (le dossier contenant 'bluenotebook')."
    exit 1
fi

echo ""
SOURCE_DIR="bluenotebook"
WRAP_DIR="bluenotebook_wrap"
INITIAL_DIR="bluenotebook_initial"

# --- Création et préparation des répertoires de destination ---
echo "--- Préparation des répertoires de destination ---"
mkdir -p "$WRAP_DIR"
mkdir -p "$INITIAL_DIR"

# Copie de l'arborescence des sous-dossiers
echo "Copie de l'arborescence de '$SOURCE_DIR' vers '$WRAP_DIR' et '$INITIAL_DIR'..."
find "$SOURCE_DIR" -mindepth 1 -type d -not -path "*/tests*" -not -path "*/.venv_bluenotebook*" -print0 | while IFS= read -r -d $'\0' dir; do
    # Recrée la même structure dans les répertoires de destination
    mkdir -p "$WRAP_DIR/${dir#$SOURCE_DIR/}"
    mkdir -p "$INITIAL_DIR/${dir#$SOURCE_DIR/}"
done
echo "Arborescence copiée."
echo ""

# --- Phase 1: Déplacement des fichiers _wrap.py ---
echo "--- Étape 1: Copie des fichiers .py vers '$WRAP_DIR' ---"
find "$SOURCE_DIR" -type f -name "*.py" -not -name "*_initial.py" -not -path "*/tests*" -not -path "*/.venv_bluenotebook*" -print0 | while IFS= read -r -d $'\0' py_file; do
    # Calcule le chemin de destination en conservant la structure
    dest_path="$WRAP_DIR/${py_file#$SOURCE_DIR/}"
    # Copie le fichier
    cp -v "$py_file" "$dest_path"
done
echo "Fichiers .py copiés."
echo ""

# --- Phase 2: Déplacement des fichiers _initial.py ---
echo "--- Étape 2: Déplacement des fichiers _initial.py vers '$INITIAL_DIR' ---"
find "$SOURCE_DIR" -type f -name "*_initial.py" -not -path "*/tests*" -not -path "*/.venv_bluenotebook*" -print0 | while IFS= read -r -d $'\0' initial_file; do
    # Calcule le chemin de destination
    dest_path="$INITIAL_DIR/${initial_file#$SOURCE_DIR/}"
    # Déplace le fichier
    mv -v "$initial_file" "$dest_path"
done
echo "Fichiers _initial.py déplacés."

echo ""
echo "Opérations terminées."

echo ""
echo "--- Étape 3: Restauration des fichiers _initial.py vers '$SOURCE_DIR' ---"
find "$INITIAL_DIR" -type f -name "*_initial.py" -print0 | while IFS= read -r -d $'\0' initial_file; do
    # Calcule le chemin relatif du fichier initial (ex: gui/editor_initial.py)
    relative_path="${initial_file#$INITIAL_DIR/}"
    
    # Construit le chemin de destination dans le répertoire source en enlevant '_initial.py'
    dest_file="$SOURCE_DIR/${relative_path%_initial.py}.py"
    
    # Copie le fichier pour écraser la version de travail
    cp -v "$initial_file" "$dest_file"
done
echo "Fichiers initiaux restaurés dans le répertoire de travail."
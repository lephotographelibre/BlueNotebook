#!/bin/bash

# Script : find_prints.sh
# Description : Recherche les appels à print( dans tous les fichiers .py du dossier courant et sous-dossiers
# Usage : ./find_prints.sh   ou   bash find_prints.sh

echo "Recherche des appels à print( dans les fichiers .py ..."
echo "=================================================="

# Utilisation de grep :
# -r : récursif
# -n : affiche le numéro de ligne
# -i : insensible à la casse (optionnel, retirez-le si vous voulez une recherche exacte)
# --include="*.py" : ne cherche que dans les fichiers .py
# "print(" : motif recherché

grep -r -n -i --include="*.py" "print(" .

# Si vous voulez exclure les commentaires (lignes commençant par #), vous pouvez utiliser une version plus avancée :
# grep -r -n -i --include="*.py" "^[^#]*print(" .

echo
echo "Recherche terminée."

# Option alternative plus précise (exclut les lignes commentées) :
# Vous pouvez décommenter les lignes ci-dessous si vous préférez cette version

# echo "Version avancée : exclusion des commentaires"
# echo "==========================================="
# grep -r -n --include="*.py" "print(" . | grep -v "^[^:]*:[0-9]*:#"

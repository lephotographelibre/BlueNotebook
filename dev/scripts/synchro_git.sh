#!/bin/bash

# Script pour synchroniser les branches Git 'main' et 'develop' avec le dépôt distant.
# Ce script:
# 1. Récupère toutes les dernières modifications depuis les dépôts distants.
# 2. Met à jour et pousse la branche 'main'.
# 3. Met à jour et pousse la branche 'develop'.
# 4. Fusionne 'main' dans 'develop' pour s'assurer que 'develop' inclut toutes les mises à jour de 'main', puis pousse 'develop'.
# 5. Retourne à la branche sur laquelle vous étiez avant l'exécution du script.

# Arrête le script si une commande échoue
set -e

echo "Démarrage de la synchronisation Git..."

# Sauvegarde de la branche actuelle pour y revenir à la fin
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Branche actuelle: $CURRENT_BRANCH"

echo "1. Récupération de toutes les dernières modifications depuis les dépôts distants..."
git fetch --all --prune

echo "2. Synchronisation de la branche 'main'..."
git checkout main
git pull origin main
git push origin main

echo "3. Synchronisation de la branche 'develop'..."
git checkout develop
git pull origin develop
git push origin develop

echo "4. Fusion de 'main' dans 'develop' et pousse vers le dépôt distant..."
# S'assure que la branche 'main' locale est bien à jour avant la fusion
git checkout main
git pull origin main
# Retourne sur develop pour fusionner main
git checkout develop
git merge origin/main # Fusionne les changements de main dans develop
git push origin develop

echo "Synchronisation Git terminée."

# Retour à la branche initiale si ce n'était ni main ni develop
if [ "$CURRENT_BRANCH" != "develop" ] && [ "$CURRENT_BRANCH" != "main" ]; then
    echo "Retour à la branche précédente: $CURRENT_BRANCH"
    git checkout "$CURRENT_BRANCH"
fi

echo "Le script a terminé son exécution."

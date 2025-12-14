#!/bin/bash
# update_and_compile_translations_pyqt5.sh
# À placer à la racine du projet
echo "*** ne pas oublier: pyenv activate .venv_bluenotebook *****"
# pyenv activate .venv_bluenotebook


# !!!!!!!!!!!!!!! A executer EN DEHORS DEV VSCODE !!!!!!!!!!!!!!!!!!!!!!!!!!
# Flatpak --> ou ouvrir le file system avec flatseal



# ------------------------------------------------------------------
# 1. Création des dossiers
# ------------------------------------------------------------------
mkdir -p i18n

# ------------------------------------------------------------------
# 2. Liste de tous les .py (exclusions complètes)
# ------------------------------------------------------------------
FILES=$(find . -type f -name "*.py" \
    ! -path "*/__pycache__/*" \
    ! -path "*/tests/*" \
    ! -path "*/scripts/*" \
    ! -path "*/resources/*" \
    ! -path "./.venv_bluenotebook/*" \
    ! -name "*wrap_strings*")

echo "Fichiers Python trouvés : $(echo "$FILES" | wc -w)"
echo

# ------------------------------------------------------------------
# 3. Mise à jour des .ts (fr / en / es)
# ------------------------------------------------------------------
echo "Étape 1 : mise à jour des fichiers .ts"
# pylupdate5 -verbose bluenotebook/core/*.py -ts bluenotebook/i18n/bluenotebook_en.ts
pylupdate5 -verbose $FILES -ts i18n/bluenotebook_fr.ts
pylupdate5 -verbose $FILES -ts i18n/bluenotebook_en.ts
pylupdate5 -verbose $FILES -ts i18n/bluenotebook_es.ts

echo
echo "Étape 2 : compilation des .ts → .qm"
# ------------------------------------------------------------------
# 4. Compilation avec lrelease (cherche automatiquement lrelease ou lrelease-qt5)
# ------------------------------------------------------------------
if command -v lrelease >/dev/null 2>&1; then
    LRELEASE="lrelease"
elif command -v lrelease-qt5 >/dev/null 2>&1; then
    LRELEASE="lrelease-qt5"
else
    echo "ERREUR : lrelease ou lrelease-qt5 non trouvé !"
    echo "    Installe-le avec : sudo apt install qt5-default qttools5-dev-tools   (Ubuntu/Debian)"
    echo "                  ou : sudo apt install qttools5-dev-tools             (plus récent)"
    exit 1
fi

$LRELEASE i18n/bluenotebook_fr.ts -qm i18n/bluenotebook_fr.qm
$LRELEASE i18n/bluenotebook_en.ts -qm i18n/bluenotebook_en.qm
$LRELEASE i18n/bluenotebook_es.ts -qm i18n/bluenotebook_es.qm

# ------------------------------------------------------------------
# 5. Résultat final
# ------------------------------------------------------------------
echo
echo "════════════════════════════════════════"
echo "Terminé ! Fichiers générés :"
ls -lh i18n/bluenotebook_*.ts i18n/bluenotebook_*.qm 2>/dev/null || echo "Aucun fichier généré"
echo "════════════════════════════════════════"
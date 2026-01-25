#!/bin/bash
# Script de test manuel pour le système backup/restore amélioré
# Usage: ./test_backup_restore.sh

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Tests du système Backup/Restore amélioré de BlueNotebook${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Vérifier que nous sommes dans le bon répertoire
if [ ! -d "bluenotebook" ]; then
    echo -e "${RED}Erreur: Ce script doit être exécuté depuis la racine du projet${NC}"
    exit 1
fi

echo -e "${YELLOW}Test 1: Vérification syntaxique des fichiers modifiés${NC}"
echo "Compilation de journal_restore_worker.py..."
python3 -m py_compile bluenotebook/core/journal_restore_worker.py && echo -e "${GREEN}✓ journal_restore_worker.py OK${NC}"

echo "Compilation de backup_handler.py..."
python3 -m py_compile bluenotebook/gui/backup_handler.py && echo -e "${GREEN}✓ backup_handler.py OK${NC}"

echo "Compilation de main_window.py..."
python3 -m py_compile bluenotebook/gui/main_window.py && echo -e "${GREEN}✓ main_window.py OK${NC}"

echo ""
echo -e "${YELLOW}Test 2: Vérification des imports${NC}"
echo "Vérification de la présence des fichiers..."

if [ -f "bluenotebook/core/journal_restore_worker.py" ]; then
    echo -e "${GREEN}✓ journal_restore_worker.py existe${NC}"
else
    echo -e "${RED}✗ journal_restore_worker.py manquant${NC}"
fi

if grep -q "from core.journal_restore_worker import JournalRestoreWorker" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ Import JournalRestoreWorker dans main_window.py${NC}"
else
    echo -e "${RED}✗ Import JournalRestoreWorker manquant dans main_window.py${NC}"
fi

if grep -q "from core.journal_restore_worker import JournalRestoreWorker" bluenotebook/gui/backup_handler.py; then
    echo -e "${GREEN}✓ Import JournalRestoreWorker dans backup_handler.py${NC}"
else
    echo -e "${RED}✗ Import JournalRestoreWorker manquant dans backup_handler.py${NC}"
fi

echo ""
echo -e "${YELLOW}Test 3: Vérification des composants UI${NC}"

if grep -q "self.restore_status_label" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ restore_status_label défini${NC}"
else
    echo -e "${RED}✗ restore_status_label manquant${NC}"
fi

if grep -q "self.restore_flash_timer" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ restore_flash_timer défini${NC}"
else
    echo -e "${RED}✗ restore_flash_timer manquant${NC}"
fi

if grep -q "self.restore_progress_dialog" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ restore_progress_dialog défini${NC}"
else
    echo -e "${RED}✗ restore_progress_dialog manquant${NC}"
fi

echo ""
echo -e "${YELLOW}Test 4: Vérification des callbacks${NC}"

if grep -q "def _on_restore_progress" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ _on_restore_progress défini${NC}"
else
    echo -e "${RED}✗ _on_restore_progress manquant${NC}"
fi

if grep -q "def _on_restore_finished" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ _on_restore_finished défini${NC}"
else
    echo -e "${RED}✗ _on_restore_finished manquant${NC}"
fi

if grep -q "def _on_restore_error" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ _on_restore_error défini${NC}"
else
    echo -e "${RED}✗ _on_restore_error manquant${NC}"
fi

if grep -q "def _start_restore_flashing" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ _start_restore_flashing défini${NC}"
else
    echo -e "${RED}✗ _start_restore_flashing manquant${NC}"
fi

if grep -q "def _stop_restore_flashing" bluenotebook/gui/main_window.py; then
    echo -e "${GREEN}✓ _stop_restore_flashing défini${NC}"
else
    echo -e "${RED}✗ _stop_restore_flashing manquant${NC}"
fi

echo ""
echo -e "${YELLOW}Test 5: Vérification de la classe RestoreMergeDialog${NC}"

if grep -q "class RestoreMergeDialog" bluenotebook/gui/backup_handler.py; then
    echo -e "${GREEN}✓ RestoreMergeDialog définie${NC}"
else
    echo -e "${RED}✗ RestoreMergeDialog manquante${NC}"
fi

if grep -q "smart_merge_radio" bluenotebook/gui/backup_handler.py; then
    echo -e "${GREEN}✓ Option 'Fusion intelligente' présente${NC}"
else
    echo -e "${RED}✗ Option 'Fusion intelligente' manquante${NC}"
fi

if grep -q "full_replace_radio" bluenotebook/gui/backup_handler.py; then
    echo -e "${GREEN}✓ Option 'Remplacement complet' présente${NC}"
else
    echo -e "${RED}✗ Option 'Remplacement complet' manquante${NC}"
fi

echo ""
echo -e "${YELLOW}Test 6: Vérification du worker JournalRestoreWorker${NC}"

if grep -q "class JournalRestoreWorker" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ JournalRestoreWorker défini${NC}"
else
    echo -e "${RED}✗ JournalRestoreWorker manquant${NC}"
fi

if grep -q "_validate_archive" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Méthode _validate_archive présente${NC}"
else
    echo -e "${RED}✗ Méthode _validate_archive manquante${NC}"
fi

if grep -q "_backup_current_journal" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Méthode _backup_current_journal présente${NC}"
else
    echo -e "${RED}✗ Méthode _backup_current_journal manquante${NC}"
fi

if grep -q "_extract_archive" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Méthode _extract_archive présente${NC}"
else
    echo -e "${RED}✗ Méthode _extract_archive manquante${NC}"
fi

if grep -q "_smart_merge" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Méthode _smart_merge présente${NC}"
else
    echo -e "${RED}✗ Méthode _smart_merge manquante${NC}"
fi

if grep -q "_full_replace" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Méthode _full_replace présente${NC}"
else
    echo -e "${RED}✗ Méthode _full_replace manquante${NC}"
fi

echo ""
echo -e "${YELLOW}Test 7: Vérification du nom d'archive simplifié${NC}"

if grep -q 'BlueNotebook-Backup-{datetime.now().strftime' bluenotebook/gui/backup_handler.py; then
    echo -e "${GREEN}✓ Nom d'archive simplifié (sans nom du journal)${NC}"
else
    echo -e "${RED}✗ Nom d'archive non simplifié${NC}"
fi

echo ""
echo -e "${YELLOW}Test 8: Vérification de la suppression du code dupliqué${NC}"

# Compter le nombre de définitions de _on_journal_backup_finished
count=$(grep -c "def _on_journal_backup_finished" bluenotebook/gui/main_window.py || echo "0")

if [ "$count" -eq 1 ]; then
    echo -e "${GREEN}✓ Code dupliqué supprimé (_on_journal_backup_finished: 1 occurrence)${NC}"
elif [ "$count" -gt 1 ]; then
    echo -e "${RED}✗ Code encore dupliqué (_on_journal_backup_finished: $count occurrences)${NC}"
else
    echo -e "${RED}✗ Fonction _on_journal_backup_finished introuvable${NC}"
fi

count=$(grep -c "def _on_journal_backup_error" bluenotebook/gui/main_window.py || echo "0")

if [ "$count" -eq 1 ]; then
    echo -e "${GREEN}✓ Code dupliqué supprimé (_on_journal_backup_error: 1 occurrence)${NC}"
elif [ "$count" -gt 1 ]; then
    echo -e "${RED}✗ Code encore dupliqué (_on_journal_backup_error: $count occurrences)${NC}"
else
    echo -e "${RED}✗ Fonction _on_journal_backup_error introuvable${NC}"
fi

echo ""
echo -e "${YELLOW}Test 9: Vérification de la traduction i18n${NC}"

if grep -q "JournalRestoreContext" bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Contexte de traduction JournalRestoreContext défini${NC}"
else
    echo -e "${RED}✗ Contexte de traduction manquant${NC}"
fi

if grep -q 'JournalRestoreContext.tr(' bluenotebook/core/journal_restore_worker.py; then
    echo -e "${GREEN}✓ Utilisation de JournalRestoreContext.tr() présente${NC}"
else
    echo -e "${RED}✗ Traductions manquantes dans le worker${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Tests de vérification terminés avec succès !${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Prochaines étapes pour tester manuellement :${NC}"
echo ""
echo "1. Lancer l'application BlueNotebook"
echo "   $ python3 -m bluenotebook.bluenotebook"
echo ""
echo "2. Tester la sauvegarde :"
echo "   - Menu Fichier → Sauvegarde Journal"
echo "   - Vérifier le nom : BlueNotebook-Backup-YYYY-MM-DD-HH-MM.zip"
echo ""
echo "3. Tester la restauration :"
echo "   - Menu Fichier → Restauration Journal"
echo "   - Sélectionner une archive"
echo "   - Choisir 'Fusion intelligente' ou 'Remplacement complet'"
echo "   - Observer la progression (0-100%)"
echo "   - Vérifier le backup de sécurité .bak-YYYYMMDD-HHMMSS"
echo ""
echo "4. Tester les conflits :"
echo "   - Créer un fichier avec même date dans journal et archive"
echo "   - Restaurer avec fusion intelligente"
echo "   - Vérifier fichier .restored créé"
echo ""

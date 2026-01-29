#!/bin/bash
# Script de validation AppImage pour soumission à AppImage Hub
# =============================================================================

set -e

SCRIPT_VERSION="1.0.0"
SCRIPT_DATE="2026-01-29"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# =============================================================================
# Vérification des paramètres
# =============================================================================

if [ -z "$1" ]; then
    echo -e "${RED}Erreur: Numéro de version requis${NC}"
    echo "Usage: $0 <VERSION>"
    echo "Exemple: $0 4.2.7"
    exit 1
fi

VERSION="$1"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Validation AppImage BlueNotebook - Version ${VERSION}${NC}"
echo -e "${CYAN}  Script version: ${SCRIPT_VERSION} (${SCRIPT_DATE})${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Variables de chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_DIR="${SCRIPT_DIR}/build_${VERSION}"
APPDIR="${BUILD_DIR}/BlueNotebook.AppDir"
DESKTOP_FILE="${APPDIR}/bluenotebook.desktop"
METAINFO_FILE="${APPDIR}/usr/share/metainfo/io.github.lephotographelibre.BlueNotebook.metainfo.xml"
APPIMAGE_FILE="${SCRIPT_DIR}/BlueNotebook-${VERSION}-x86_64.AppImage"

# Compteurs de résultats
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_WARNING=0

# =============================================================================
# Fonctions utilitaires
# =============================================================================

print_test() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_pass() {
    echo -e "${GREEN}  ✓ $1${NC}"
    ((TESTS_PASSED++)) || true
}

print_fail() {
    echo -e "${RED}  ✗ $1${NC}"
    ((TESTS_FAILED++)) || true
}

print_warn() {
    echo -e "${YELLOW}  ⚠ $1${NC}"
    ((TESTS_WARNING++)) || true
}

# =============================================================================
# Tests de validation
# =============================================================================

echo -e "${YELLOW}Démarrage des tests de validation...${NC}"
echo ""

# Test 1: Vérifier que l'AppDir existe
print_test "Test 1: Vérification de l'existence de l'AppDir"
if [ -d "$APPDIR" ]; then
    print_pass "AppDir trouvé: $APPDIR"
else
    print_fail "AppDir non trouvé: $APPDIR"
    echo -e "${RED}Erreur critique: L'AppDir n'existe pas. Exécutez d'abord build_all_appimage.sh${NC}"
    exit 1
fi
echo ""

# Test 2: Vérifier le fichier .desktop
print_test "Test 2: Vérification du fichier .desktop"
if [ -f "$DESKTOP_FILE" ]; then
    print_pass "Fichier .desktop trouvé"

    # Vérifier si desktop-file-validate est disponible
    if command -v desktop-file-validate &> /dev/null; then
        if desktop-file-validate "$DESKTOP_FILE" 2>&1; then
            print_pass "Validation desktop-file-validate réussie"
        else
            print_fail "Validation desktop-file-validate échouée"
            echo -e "${YELLOW}Détails de l'erreur:${NC}"
            desktop-file-validate "$DESKTOP_FILE" 2>&1 | sed 's/^/    /'
        fi
    else
        print_warn "desktop-file-validate non installé (sudo apt install desktop-file-utils)"
    fi
else
    print_fail "Fichier .desktop non trouvé: $DESKTOP_FILE"
fi
echo ""

# Test 3: Vérifier le fichier AppStream metainfo
print_test "Test 3: Vérification du fichier AppStream metainfo"
if [ -f "$METAINFO_FILE" ]; then
    print_pass "Fichier metainfo trouvé dans usr/share/metainfo/"

    # Vérifier si appstreamcli est disponible
    if command -v appstreamcli &> /dev/null; then
        if appstreamcli validate "$METAINFO_FILE" 2>&1; then
            print_pass "Validation appstreamcli réussie"
        else
            print_warn "Validation appstreamcli avec avertissements"
            echo -e "${YELLOW}Détails:${NC}"
            appstreamcli validate "$METAINFO_FILE" 2>&1 | sed 's/^/    /'
        fi
    else
        print_warn "appstreamcli non installé (sudo apt install appstream)"
    fi
else
    print_fail "Fichier metainfo non trouvé: $METAINFO_FILE"
    print_fail "Le fichier metainfo DOIT être dans usr/share/metainfo/"
fi
echo ""

# Test 4: Vérifier l'icône
print_test "Test 4: Vérification de l'icône"
if [ -f "$APPDIR/bluenotebook.png" ]; then
    print_pass "Icône trouvée"

    # Vérifier les dimensions
    if command -v identify &> /dev/null; then
        ICON_SIZE=$(identify -format "%wx%h" "$APPDIR/bluenotebook.png" 2>/dev/null)
        if [ ! -z "$ICON_SIZE" ]; then
            print_pass "Dimensions de l'icône: $ICON_SIZE"
        fi
    fi
else
    print_fail "Icône non trouvée: $APPDIR/bluenotebook.png"
fi
echo ""

# Test 5: Vérifier AppRun
print_test "Test 5: Vérification du script AppRun"
if [ -f "$APPDIR/AppRun" ]; then
    if [ -x "$APPDIR/AppRun" ]; then
        print_pass "AppRun trouvé et exécutable"
    else
        print_fail "AppRun existe mais n'est pas exécutable"
    fi
else
    print_fail "AppRun non trouvé"
fi
echo ""

# Test 6: Exécuter appdir-lint.sh
print_test "Test 6: Exécution de appdir-lint.sh"
APPDIR_LINT="${BUILD_DIR}/appdir-lint.sh"

if [ ! -f "$APPDIR_LINT" ]; then
    echo -e "${YELLOW}  Téléchargement de appdir-lint.sh...${NC}"
    wget -q -O "$APPDIR_LINT" https://raw.githubusercontent.com/AppImage/pkg2appimage/master/appdir-lint.sh
    chmod +x "$APPDIR_LINT"
fi

if [ -f "$APPDIR_LINT" ]; then
    echo -e "${YELLOW}  Exécution de appdir-lint.sh (ceci peut prendre quelques secondes)...${NC}"
    LINT_OUTPUT=$(bash "$APPDIR_LINT" "$APPDIR" 2>&1 || true)

    # Compter les erreurs et avertissements
    ERROR_COUNT=$(echo "$LINT_OUTPUT" | grep -c "ERROR" || true)
    WARNING_COUNT=$(echo "$LINT_OUTPUT" | grep -c "WARNING" || true)

    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_pass "Aucune erreur trouvée par appdir-lint.sh"
    else
        print_fail "appdir-lint.sh a trouvé $ERROR_COUNT erreur(s)"
    fi

    if [ "$WARNING_COUNT" -gt 0 ]; then
        print_warn "appdir-lint.sh a trouvé $WARNING_COUNT avertissement(s)"
    fi

    # Afficher les détails si des erreurs/warnings
    if [ "$ERROR_COUNT" -gt 0 ] || [ "$WARNING_COUNT" -gt 0 ]; then
        echo -e "${YELLOW}  Détails de appdir-lint.sh:${NC}"
        echo "$LINT_OUTPUT" | grep -E "(ERROR|WARNING)" | sed 's/^/    /' || true
    fi
else
    print_warn "Impossible de télécharger appdir-lint.sh"
fi
echo ""

# Test 7: Vérifier la structure de répertoires
print_test "Test 7: Vérification de la structure de répertoires"
REQUIRED_DIRS=(
    "usr/local/bin"
    "usr/local/lib"
    "app"
)

ALL_DIRS_OK=true
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$APPDIR/$dir" ]; then
        print_pass "Répertoire trouvé: $dir"
    else
        print_warn "Répertoire manquant: $dir"
        ALL_DIRS_OK=false
    fi
done
echo ""

# Test 8: Vérifier l'AppImage finale
print_test "Test 8: Vérification de l'AppImage finale"
if [ -f "$APPIMAGE_FILE" ]; then
    print_pass "AppImage trouvée: $(basename "$APPIMAGE_FILE")"

    APPIMAGE_SIZE=$(du -h "$APPIMAGE_FILE" | cut -f1)
    print_pass "Taille: $APPIMAGE_SIZE"

    if [ -x "$APPIMAGE_FILE" ]; then
        print_pass "AppImage exécutable"
    else
        print_fail "AppImage non exécutable"
    fi
else
    print_warn "AppImage finale non trouvée (peut-être pas encore construite)"
fi
echo ""

# Test 9: Vérifier les dépendances Python
print_test "Test 9: Vérification des dépendances Python"
if [ -d "$APPDIR/usr/local/lib/python3.11/site-packages" ]; then
    print_pass "Site-packages Python trouvé"

    # Vérifier PyQt5
    if [ -d "$APPDIR/usr/local/lib/python3.11/site-packages/PyQt5" ]; then
        print_pass "PyQt5 trouvé"
    else
        print_fail "PyQt5 manquant"
    fi

    # Vérifier les packages critiques
    CRITICAL_PACKAGES=("markdown" "beautifulsoup4" "requests" "Pillow")
    for pkg in "${CRITICAL_PACKAGES[@]}"; do
        if ls "$APPDIR/usr/local/lib/python3.11/site-packages" | grep -i "$pkg" > /dev/null 2>&1; then
            print_pass "Package trouvé: $pkg"
        else
            print_warn "Package possiblement manquant: $pkg"
        fi
    done
else
    print_fail "Site-packages Python non trouvé"
fi
echo ""

# Test 10: Vérifier les bibliothèques système critiques
print_test "Test 10: Vérification des bibliothèques système"
CRITICAL_LIBS=(
    "libssl.so*"
    "libcrypto.so*"
)

for lib_pattern in "${CRITICAL_LIBS[@]}"; do
    if find "$APPDIR/usr/lib/x86_64-linux-gnu" -name "$lib_pattern" 2>/dev/null | grep -q .; then
        print_pass "Bibliothèque trouvée: $lib_pattern"
    else
        print_warn "Bibliothèque non trouvée: $lib_pattern"
    fi
done
echo ""

# =============================================================================
# Résumé final
# =============================================================================

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  RÉSUMÉ DE LA VALIDATION${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

TOTAL_TESTS=$((TESTS_PASSED + TESTS_FAILED + TESTS_WARNING))

echo -e "${GREEN}✓ Tests réussis:     $TESTS_PASSED${NC}"
echo -e "${YELLOW}⚠ Avertissements:    $TESTS_WARNING${NC}"
echo -e "${RED}✗ Tests échoués:     $TESTS_FAILED${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "  Total:             $TOTAL_TESTS tests"
echo ""

# Déterminer le statut final
if [ $TESTS_FAILED -eq 0 ]; then
    if [ $TESTS_WARNING -eq 0 ]; then
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ VALIDATION COMPLÈTE RÉUSSIE${NC}"
        echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${GREEN}Votre AppImage est prête pour la soumission à AppImage Hub!${NC}"
        echo ""
        exit 0
    else
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo -e "${YELLOW}  ⚠ VALIDATION RÉUSSIE AVEC AVERTISSEMENTS${NC}"
        echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
        echo ""
        echo -e "${YELLOW}Votre AppImage peut être soumise, mais vérifiez les avertissements ci-dessus.${NC}"
        echo ""
        exit 0
    fi
else
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}  ✗ VALIDATION ÉCHOUÉE${NC}"
    echo -e "${RED}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${RED}Des erreurs critiques ont été détectées. Veuillez les corriger avant la soumission.${NC}"
    echo ""
    exit 1
fi

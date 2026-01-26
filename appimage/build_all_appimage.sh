#!/bin/bash
set -e

# =============================================================================
# Script de construction automatisé d'AppImage pour BlueNotebook
# =============================================================================
# Usage: ./build_all_appimage.sh <VERSION>
# Exemple: ./build_all_appimage.sh 4.2.3
#
# Ce script génère une AppImage portable complète pour une version spécifique
# de BlueNotebook, incluant tous les fichiers nécessaires.
# =============================================================================

SCRIPT_VERSION="1.0.0"
SCRIPT_DATE="2025-01-20"

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
    echo "Exemple: $0 4.2.3"
    exit 1
fi

VERSION="$1"
GIT_TAG="v${VERSION}"

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  Build AppImage BlueNotebook - Version ${VERSION}${NC}"
echo -e "${CYAN}  Script version: ${SCRIPT_VERSION} (${SCRIPT_DATE})${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# Variables de chemins
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="${SCRIPT_DIR}/build_${VERSION}"
DOCKERFILE_TEMPLATE="${SCRIPT_DIR}/Dockerfile.template"
DOCKERFILE_VERSION="${WORK_DIR}/Dockerfile"
ICON_SOURCE="${SCRIPT_DIR}/bluenotebook_256-x256_fond_blanc.png"
DOCKER_IMAGE="bluenotebook-appimage:${VERSION}"
APPIMAGE_NAME="BlueNotebook-${VERSION}-x86_64.AppImage"
DESKTOP_FILE="BlueNotebook-${VERSION}.desktop"

# =============================================================================
# Vérification des prérequis
# =============================================================================

echo -e "${YELLOW}Vérification des prérequis...${NC}"

# Vérifier Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Erreur: Docker n'est pas installé${NC}"
    exit 1
fi

# Vérifier l'icône
if [ ! -f "$ICON_SOURCE" ]; then
    echo -e "${RED}Erreur: Icône non trouvée: $ICON_SOURCE${NC}"
    exit 1
fi

# Vérifier le Dockerfile template
if [ ! -f "$DOCKERFILE_TEMPLATE" ]; then
    echo -e "${RED}Erreur: Dockerfile template non trouvé: $DOCKERFILE_TEMPLATE${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Prérequis OK${NC}"
echo ""

# =============================================================================
# Création du répertoire de travail
# =============================================================================

echo -e "${YELLOW}Création du répertoire de travail...${NC}"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"
echo -e "${GREEN}✓ Répertoire: $WORK_DIR${NC}"
echo ""

# =============================================================================
# Génération du Dockerfile spécifique à la version
# =============================================================================

echo -e "${YELLOW}Génération du Dockerfile pour la version ${VERSION}...${NC}"

cat > "$DOCKERFILE_VERSION" << 'DOCKERFILE_CONTENT'
# Utiliser une base Debian 11 (GLIBC 2.31) pour meilleure compatibilité
FROM debian:11-slim AS builder

# Installation des dépendances de build
RUN apt-get update && apt-get install -y \
    git \
    wget \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libffi-dev \
    liblzma-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf-2.0-dev \
    pkg-config \
    python3-dev \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5dbus5 \
    libqt5network5 \
    libqt5svg5 \
    libqt5webengine5 \
    libqt5webenginewidgets5 \
    libqt5webenginecore5 \
    libqt5printsupport5 \
    qtbase5-dev \
    qtwebengine5-dev \
    && rm -rf /var/lib/apt/lists/*

# Compilation de Python 3.11.13 depuis les sources
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tgz && \
    tar xzf Python-3.11.13.tgz && \
    cd Python-3.11.13 && \
    ./configure --enable-optimizations --enable-shared --prefix=/usr/local && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd .. && \
    rm -rf Python-3.11.13*

# Création des liens symboliques Python
RUN ln -sf /usr/local/bin/python3.11 /usr/local/bin/python3 && \
    ln -sf /usr/local/bin/pip3.11 /usr/local/bin/pip3

# Clonage du dépôt BlueNotebook à la version spécifique
DOCKERFILE_CONTENT

# Ajouter la ligne avec la version spécifique
echo "ARG GIT_TAG=${GIT_TAG}" >> "$DOCKERFILE_VERSION"

cat >> "$DOCKERFILE_VERSION" << 'DOCKERFILE_CONTENT2'
RUN git clone https://github.com/lephotographelibre/BlueNotebook.git /app && \
    cd /app && \
    git checkout ${GIT_TAG} && \
    rm -rf /app/.git

# Installation des dépendances Python
WORKDIR /app
RUN /usr/local/bin/pip3.11 install --no-cache-dir -r requirements.txt

# Étape finale : Image runtime minimale
FROM debian:11-slim

# Installation des bibliothèques runtime uniquement
RUN apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libqt5widgets5 \
    libqt5gui5 \
    libqt5core5a \
    libqt5dbus5 \
    libqt5network5 \
    libqt5svg5 \
    libqt5webengine5 \
    libqt5webenginewidgets5 \
    libqt5webenginecore5 \
    libqt5printsupport5 \
    libx11-6 \
    libxext6 \
    libxrender1 \
    libfontconfig1 \
    libfreetype6 \
    libjpeg62-turbo \
    libpng16-16 \
    zlib1g \
    libssl1.1 \
    libffi7 \
    libsqlite3-0 \
    libreadline8 \
    libbz2-1.0 \
    liblzma5 \
    && rm -rf /var/lib/apt/lists/*

# Copie de Python compilé et ses bibliothèques
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Configuration de ldconfig pour libpython
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/python.conf && ldconfig

WORKDIR /app/bluenotebook
ENV QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"

CMD ["python3.11", "main.py"]
DOCKERFILE_CONTENT2

echo -e "${GREEN}✓ Dockerfile généré: $DOCKERFILE_VERSION${NC}"
echo ""

# =============================================================================
# Construction de l'image Docker
# =============================================================================

echo -e "${YELLOW}Construction de l'image Docker...${NC}"
echo -e "${BLUE}Image: ${DOCKER_IMAGE}${NC}"
echo -e "${BLUE}Tag Git: ${GIT_TAG}${NC}"
echo ""

docker build --build-arg GIT_TAG="${GIT_TAG}" -t "${DOCKER_IMAGE}" -f "$DOCKERFILE_VERSION" "$SCRIPT_DIR"

echo ""
echo -e "${GREEN}✓ Image Docker créée: ${DOCKER_IMAGE}${NC}"
echo ""

# =============================================================================
# Construction de l'AppImage
# =============================================================================

echo -e "${YELLOW}Construction de l'AppImage...${NC}"

APPDIR="BlueNotebook.AppDir"
TEMP_EXTRACT="temp_docker_extract"

# Nettoyage préalable
rm -rf "$APPDIR" "$TEMP_EXTRACT"
mkdir -p "$APPDIR" "$TEMP_EXTRACT"

# Extraction du contenu Docker
echo -e "${BLUE}Extraction du contenu Docker...${NC}"
CONTAINER_ID=$(docker create "$DOCKER_IMAGE")
docker export "$CONTAINER_ID" | tar -x -C "$TEMP_EXTRACT"
docker rm "$CONTAINER_ID" > /dev/null

# Création de la structure AppDir
mkdir -p "$APPDIR/usr/local/"{bin,lib}
mkdir -p "$APPDIR/usr/lib/x86_64-linux-gnu"
mkdir -p "$APPDIR/lib/x86_64-linux-gnu"
mkdir -p "$APPDIR/app"

# Copie de Python complet
echo -e "${BLUE}Copie de Python 3.11.13 et dépendances...${NC}"
cp -r "$TEMP_EXTRACT/usr/local/lib" "$APPDIR/usr/local/"
cp -r "$TEMP_EXTRACT/usr/local/bin" "$APPDIR/usr/local/"

# Copie de l'application
echo -e "${BLUE}Copie de BlueNotebook...${NC}"
cp -r "$TEMP_EXTRACT/app" "$APPDIR/"

# Copie des bibliothèques SSL (critique pour Python _ssl)
echo -e "${BLUE}Copie des bibliothèques SSL...${NC}"
for search_dir in "$TEMP_EXTRACT/usr/lib/x86_64-linux-gnu" \
                  "$TEMP_EXTRACT/usr/lib" \
                  "$TEMP_EXTRACT/lib/x86_64-linux-gnu" \
                  "$TEMP_EXTRACT/lib"; do
    if [ -d "$search_dir" ]; then
        find "$search_dir" -name "libssl.so*" -o -name "libcrypto.so*" 2>/dev/null | while read -r lib; do
            cp -P "$lib" "$APPDIR/usr/lib/x86_64-linux-gnu/" 2>/dev/null || true
            cp -P "$lib" "$APPDIR/usr/lib/" 2>/dev/null || true
            cp -P "$lib" "$APPDIR/lib/x86_64-linux-gnu/" 2>/dev/null || true
            cp -P "$lib" "$APPDIR/lib/" 2>/dev/null || true
        done
    fi
done

# Vérifier que libssl est présente
if [ ! -f "$APPDIR/usr/lib/x86_64-linux-gnu/libssl.so.1.1" ] && [ ! -f "$APPDIR/usr/lib/x86_64-linux-gnu/libssl.so.3" ]; then
    echo -e "${RED}ERREUR: libssl non trouvée!${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python et dépendances SSL copiés${NC}"

# Note: PyQt5 package (installé via pip dans Docker) inclut déjà TOUTES les bibliothèques Qt
# Elles sont dans /usr/local/lib/python3.11/site-packages/PyQt5/Qt5/
# Pas besoin de copier Qt depuis le système - cela évite les conflits de versions
echo -e "${YELLOW}Note: Utilisation de Qt embarqué dans PyQt5 (déjà dans site-packages)${NC}"
echo -e "${GREEN}✓ PyQt5 avec Qt embarqué sera utilisé${NC}"

# Copie des bibliothèques nécessaires (sans glibc)
echo -e "${YELLOW}Copie des bibliothèques de dépendances...${NC}"
LIBS_TO_COPY=(
    "libcairo.so*"
    "libpango*.so*"
    "libgdk_pixbuf*.so*"
    "libfreetype.so*"
    "libfontconfig.so*"
    "libpng16.so*"
    "libffi.so*"
    "libglib*.so*"
    "libharfbuzz*.so*"
    "libz.so*"
    "libexpat.so*"
    "libbz2.so*"
    "libsqlite3.so*"
    "libreadline.so*"
    "liblzma.so*"
    "libjpeg.so*"
    "libxcb*.so*"
    "libX11*.so*"
    "libXext*.so*"
    "libXrender*.so*"
    "libXau.so*"
    "libXdmcp.so*"
    "libxshmfence.so*"
    "libxkbcommon*.so*"
    "libpixman*.so*"
    "libtiff.so*"
    "libwebp*.so*"
    "libmount.so*"
    "libblkid.so*"
    "libuuid.so*"
    "libselinux.so*"
    "libpcre.so*"
    "libtinfo.so*"
    "libdbus*.so*"
    "libsystemd.so*"
    "liblz4.so*"
    "libgcrypt.so*"
    "libgpg-error.so*"
    "libdouble-conversion.so*"
    "libicui18n.so*"
    "libicuuc.so*"
    "libicudata.so*"
    "libpcre*.so*"
    "libgraphite2.so*"
    "libbsd.so*"
    "libmd.so*"
    "libevent*.so*"
    "libminizip.so*"
    "libre2.so*"
    "libvpx.so*"
    "libopus.so*"
    "libwebpmux.so*"
    "libwebpdemux.so*"
    "liblcms2.so*"
    "libavcodec.so*"
    "libavformat.so*"
    "libavutil.so*"
    "libswresample.so*"
    "libnss3.so*"
    "libnspr4.so*"
    "libsmime3.so*"
    "libnssutil3.so*"
    "libplc4.so*"
    "libplds4.so*"
    "libsoftokn3.so*"
    "libfreebl3.so*"
    "libfreeblpriv3.so*"
)

for lib_pattern in "${LIBS_TO_COPY[@]}"; do
    find "$TEMP_EXTRACT/usr/lib" "$TEMP_EXTRACT/lib" -name "$lib_pattern" 2>/dev/null | while read -r lib; do
        cp -P "$lib" "$APPDIR/usr/lib/x86_64-linux-gnu/" 2>/dev/null || true
    done
done

echo -e "${GREEN}✓ Bibliothèques copiées${NC}"

# Supprimer les bibliothèques système critiques (doivent venir du système hôte)
echo -e "${YELLOW}Nettoyage des bibliothèques système critiques...${NC}"
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libc.so"*
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libm.so"*
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libpthread.so"*
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libdl.so"*
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/librt.so"*
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/ld-linux"*
echo -e "${GREEN}✓ Nettoyage effectué${NC}"

# Copie de l'icône haute résolution
echo -e "${BLUE}Copie de l'icône...${NC}"
cp "$ICON_SOURCE" "$APPDIR/bluenotebook.png"
ln -sf bluenotebook.png "$APPDIR/.DirIcon"
echo -e "${GREEN}✓ Icône copiée (256x256)${NC}"

# Création du fichier .desktop pour l'AppImage
cat > "$APPDIR/bluenotebook.desktop" << DESKTOP_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BlueNotebook
GenericName=Journal personnel
Comment=Journal personnel et organisateur de notes
Exec=bluenotebook
Icon=bluenotebook
Terminal=false
Categories=Office;Calendar;X-Diary;
MimeType=text/plain;
Keywords=journal;diary;notes;markdown;
StartupNotify=true
StartupWMClass=bluenotebook
DESKTOP_EOF

echo -e "${GREEN}✓ Fichier .desktop créé${NC}"

# Création du script AppRun
echo -e "${BLUE}Création du script AppRun...${NC}"
cat > "$APPDIR/AppRun" << 'APPRUN_EOF'
#!/bin/bash
set -e

HERE="$(dirname "$(readlink -f "${0}")")"

# Options de debug
if [ "$1" = "--debug-ssl" ]; then
    echo "Debug SSL/TLS:"
    echo "Bibliothèques SSL disponibles:"
    ls -la "$HERE/usr/lib/x86_64-linux-gnu/libssl"* "$HERE/usr/lib/x86_64-linux-gnu/libcrypto"* 2>/dev/null
    echo ""
    echo "LD_LIBRARY_PATH qui sera utilisé:"
    echo "$HERE/usr/local/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib:$HERE/lib/x86_64-linux-gnu:$HERE/lib"
    exit 0
fi

if [ "$1" = "--debug-qt" ]; then
    echo "Debug Qt:"
    echo "Plugins Qt disponibles:"
    find "$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins" -type f 2>/dev/null
    echo ""
    echo "Dépendances du plugin:"
    ldd "$HERE/usr/lib/x86_64-linux-gnu/qt5/plugins/platforms/libqxcb.so" 2>&1 | grep "not found"
    echo ""
    echo "Bibliothèques SSL disponibles:"
    ls -la "$HERE/usr/lib/x86_64-linux-gnu/libssl"* "$HERE/usr/lib/x86_64-linux-gnu/libcrypto"* 2>/dev/null
    exit 0
fi

# CRITICAL: Inclure les bibliothèques Qt de PyQt5 EN PREMIER pour éviter les conflits
export LD_LIBRARY_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/lib:$HERE/usr/local/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib:$HERE/lib/x86_64-linux-gnu:$HERE/lib:$LD_LIBRARY_PATH"

# Configuration Python
export PYTHONHOME="$HERE/usr/local"
export PYTHONPATH="$HERE/usr/local/lib/python3.11/site-packages:$PYTHONPATH"
export PATH="$HERE/usr/local/bin:$PATH"

# Utiliser les plugins Qt de PyQt5 (embarqués avec le package)
export QT_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins/platforms"

# Configuration Qt pour AppImage
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu --no-sandbox"
export QT_XCB_GL_INTEGRATION=none
export QTWEBENGINE_DISABLE_SANDBOX=1

# Force NSS to use AppImage libraries (prevent system NSS conflicts)
export NSS_DISABLE_UNLOAD=1
export LD_PRELOAD="$HERE/usr/lib/x86_64-linux-gnu/libnss3.so:$HERE/usr/lib/x86_64-linux-gnu/libnssutil3.so:$HERE/usr/lib/x86_64-linux-gnu/libsoftokn3.so:$HERE/usr/lib/x86_64-linux-gnu/libfreeblpriv3.so:$HERE/usr/lib/x86_64-linux-gnu/libfreebl3.so:$HERE/usr/lib/x86_64-linux-gnu/libsmime3.so:$HERE/usr/lib/x86_64-linux-gnu/libnspr4.so:$HERE/usr/lib/x86_64-linux-gnu/libplc4.so:$HERE/usr/lib/x86_64-linux-gnu/libplds4.so"
export QTWEBENGINEPROCESS_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/libexec/QtWebEngineProcess"
export QTWEBENGINE_RESOURCES_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/resources"
export QTWEBENGINE_LOCALES_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/translations"

# Création du répertoire de données
DATA_DIR="$HOME/.bluenotebook"
mkdir -p "$DATA_DIR/journal" "$DATA_DIR/backup"

# Note: PyQt5 est maintenant EMBARQUÉ dans l'AppImage, pas besoin de vérification système
# Vérifier que PyQt5 est bien disponible dans l'AppImage
"$HERE/usr/local/bin/python3.11" -c "import PyQt5.QtWidgets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "=========================================="
    echo "ERREUR: PyQt5 non trouvé dans l'AppImage"
    echo "=========================================="
    echo ""
    echo "L'AppImage semble corrompue ou incomplète."
    echo "Veuillez re-télécharger l'AppImage ou la reconstruire."
    echo ""
    exit 1
fi

# Lancement de l'application
cd "$HERE/app/bluenotebook"
exec "$HERE/usr/local/bin/python3.11" main.py "$@"
APPRUN_EOF

chmod +x "$APPDIR/AppRun"
echo -e "${GREEN}✓ AppRun créé${NC}"

# Téléchargement d'appimagetool si nécessaire
APPIMAGETOOL="$WORK_DIR/appimagetool-x86_64.AppImage"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo -e "${BLUE}Téléchargement d'appimagetool...${NC}"
    wget -q -O "$APPIMAGETOOL" https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$APPIMAGETOOL"
    echo -e "${GREEN}✓ appimagetool téléchargé${NC}"
fi

# Génération de l'AppImage
echo -e "${BLUE}Génération de l'AppImage...${NC}"
ARCH=x86_64 "$APPIMAGETOOL" --no-appstream "$APPDIR" "$APPIMAGE_NAME"

# Embarquer l'icône dans l'AppImage pour qu'elle soit visible dans le gestionnaire de fichiers
echo -e "${BLUE}Embarquement de l'icône dans l'AppImage...${NC}"

# Méthode simple et fiable : ajouter l'icône à la fin du fichier avec le marqueur AppImage
ICON_SIZE=$(stat -c%s "$ICON_SOURCE")

# Ajouter l'icône à la fin de l'AppImage
cat "$ICON_SOURCE" >> "$APPIMAGE_NAME"

# Ajouter le marqueur pour que les gestionnaires de fichiers trouvent l'icône
# Format: taille de l'icône (4 octets little-endian) + signature "AI\x02"
printf "$(printf '\\x%02x' $((ICON_SIZE & 0xFF)) $((ICON_SIZE >> 8 & 0xFF)) $((ICON_SIZE >> 16 & 0xFF)) $((ICON_SIZE >> 24 & 0xFF)))" >> "$APPIMAGE_NAME"
printf '\x41\x49\x02' >> "$APPIMAGE_NAME"

echo -e "${GREEN}✓ Icône embarquée (taille: $ICON_SIZE octets)${NC}"

# Déplacer l'AppImage dans le répertoire parent
mv "$APPIMAGE_NAME" "$SCRIPT_DIR/"
echo -e "${GREEN}✓ AppImage créée: $SCRIPT_DIR/$APPIMAGE_NAME${NC}"

# Copier l'icône dans le répertoire parent pour le fichier .desktop
echo -e "${BLUE}Copie de l'icône pour le fichier .desktop...${NC}"
cp "$ICON_SOURCE" "$SCRIPT_DIR/"
echo -e "${GREEN}✓ Icône copiée: $SCRIPT_DIR/$(basename "$ICON_SOURCE")${NC}"

# Nettoyage temporaire
rm -rf "$TEMP_EXTRACT"
echo ""

# =============================================================================
# Génération du fichier .desktop pour installation système
# =============================================================================

echo -e "${YELLOW}Génération du fichier .desktop pour installation système...${NC}"

APPIMAGE_ABSOLUTE_PATH="$(cd "$SCRIPT_DIR" && pwd)/$APPIMAGE_NAME"
ICON_ABSOLUTE_PATH="$(cd "$SCRIPT_DIR" && pwd)/$(basename "$ICON_SOURCE")"

cat > "$SCRIPT_DIR/$DESKTOP_FILE" << DESKTOP_SYSTEM_EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=BlueNotebook
GenericName=Journal personnel
Comment=Journal personnel et organisateur de notes (Version ${VERSION})
Exec=${APPIMAGE_ABSOLUTE_PATH} %F
Icon=${ICON_ABSOLUTE_PATH}
Terminal=false
Categories=Office;Calendar;X-Diary;
MimeType=text/plain;
Keywords=journal;diary;notes;markdown;
StartupNotify=true
StartupWMClass=bluenotebook
DESKTOP_SYSTEM_EOF

echo -e "${GREEN}✓ Fichier .desktop créé: $SCRIPT_DIR/$DESKTOP_FILE${NC}"
echo ""

# =============================================================================
# Génération des scripts d'installation et désinstallation
# =============================================================================

echo -e "${YELLOW}Génération des scripts d'installation...${NC}"

# Script d'installation
cat > "$SCRIPT_DIR/install_BlueNotebook-${VERSION}.sh" << 'INSTALL_EOF'
#!/bin/bash
# Script d'installation de BlueNotebook dans le menu système
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_NAME="BlueNotebook"
INSTALL_EOF

echo "VERSION=\"${VERSION}\"" >> "$SCRIPT_DIR/install_BlueNotebook-${VERSION}.sh"

cat >> "$SCRIPT_DIR/install_BlueNotebook-${VERSION}.sh" << INSTALL_EOF2
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
APPIMAGE_FILE="\${SCRIPT_DIR}/BlueNotebook-${VERSION}-x86_64.AppImage"
DESKTOP_FILE="\${SCRIPT_DIR}/BlueNotebook-${VERSION}.desktop"
ICON_FILE="\${SCRIPT_DIR}/$(basename "$ICON_SOURCE")"
INSTALL_EOF2

cat >> "$SCRIPT_DIR/install_BlueNotebook-${VERSION}.sh" << 'INSTALL_EOF3'

echo -e "${GREEN}Installation de BlueNotebook ${VERSION}${NC}"
echo ""

# Vérifications
if [ ! -f "$APPIMAGE_FILE" ]; then
    echo -e "${RED}Erreur: AppImage non trouvée: $APPIMAGE_FILE${NC}"
    exit 1
fi

if [ ! -f "$DESKTOP_FILE" ]; then
    echo -e "${RED}Erreur: Fichier .desktop non trouvé: $DESKTOP_FILE${NC}"
    exit 1
fi

# Création des répertoires
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/256x256/apps

# Rendre exécutable
chmod +x "$APPIMAGE_FILE"
echo -e "${GREEN}✓ AppImage rendue exécutable${NC}"

# Copier l'icône
if [ -f "$ICON_FILE" ]; then
    cp "$ICON_FILE" ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png
    echo -e "${GREEN}✓ Icône installée${NC}"
else
    echo -e "${YELLOW}⚠ Icône non trouvée, utilisation de l'icône de l'AppImage${NC}"
fi

# Installer le lanceur
cp "$DESKTOP_FILE" ~/.local/share/applications/
echo -e "${GREEN}✓ Lanceur installé${NC}"

# Mettre à jour les bases de données
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
echo -e "${GREEN}✓ Bases de données mises à jour${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Installation réussie !${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo "BlueNotebook est disponible dans:"
echo "  • Menu → Bureautique → BlueNotebook"
echo "  • Recherche d'applications: tapez 'BlueNotebook'"
echo ""
INSTALL_EOF3

chmod +x "$SCRIPT_DIR/install_BlueNotebook-${VERSION}.sh"
echo -e "${GREEN}✓ Script d'installation créé: install_BlueNotebook-${VERSION}.sh${NC}"

# Script de désinstallation
cat > "$SCRIPT_DIR/uninstall_BlueNotebook-${VERSION}.sh" << 'UNINSTALL_EOF'
#!/bin/bash
# Script de désinstallation de BlueNotebook
set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

UNINSTALL_EOF

echo "VERSION=\"${VERSION}\"" >> "$SCRIPT_DIR/uninstall_BlueNotebook-${VERSION}.sh"

cat >> "$SCRIPT_DIR/uninstall_BlueNotebook-${VERSION}.sh" << 'UNINSTALL_EOF2'
DESKTOP_FILE="BlueNotebook-${VERSION}.desktop"

echo -e "${YELLOW}Désinstallation de BlueNotebook ${VERSION}${NC}"
echo ""

# Supprimer le lanceur
if [ -f ~/.local/share/applications/"$DESKTOP_FILE" ]; then
    rm -f ~/.local/share/applications/"$DESKTOP_FILE"
    echo -e "${GREEN}✓ Lanceur supprimé${NC}"
else
    echo -e "${YELLOW}⚠ Lanceur déjà supprimé${NC}"
fi

# Supprimer l'icône
if [ -f ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png ]; then
    rm -f ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png
    echo -e "${GREEN}✓ Icône supprimée${NC}"
else
    echo -e "${YELLOW}⚠ Icône déjà supprimée${NC}"
fi

# Mettre à jour les bases de données
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true
echo -e "${GREEN}✓ Bases de données mises à jour${NC}"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Désinstallation réussie${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Note importante:${NC}"
echo "  • L'AppImage a été conservée (non supprimée)"
echo "  • Vos données dans ~/.bluenotebook sont conservées"
echo ""
echo "Pour supprimer complètement BlueNotebook:"
echo "  • Supprimer manuellement l'AppImage"
echo "  • Supprimer ~/.bluenotebook (vos données)"
echo ""
UNINSTALL_EOF2

chmod +x "$SCRIPT_DIR/uninstall_BlueNotebook-${VERSION}.sh"
echo -e "${GREEN}✓ Script de désinstallation créé: uninstall_BlueNotebook-${VERSION}.sh${NC}"
echo ""

# =============================================================================
# Génération du script de nettoyage
# =============================================================================

echo -e "${YELLOW}Génération du script de nettoyage...${NC}"

cat > "$SCRIPT_DIR/cleanup.sh" << CLEANUP_EOF
#!/bin/bash
# Script de nettoyage des fichiers de build

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "\${YELLOW}Nettoyage des fichiers de build BlueNotebook ${VERSION}...\${NC}"
echo ""

# Supprimer le répertoire de build
if [ -d "${WORK_DIR}" ]; then
    echo -e "\${YELLOW}Suppression du répertoire de build...\${NC}"
    rm -rf "${WORK_DIR}"
    echo -e "\${GREEN}✓ Répertoire de build supprimé\${NC}"
fi

# Supprimer l'image Docker
if docker image inspect "${DOCKER_IMAGE}" &> /dev/null; then
    echo -e "\${YELLOW}Suppression de l'image Docker...\${NC}"
    docker rmi "${DOCKER_IMAGE}"
    echo -e "\${GREEN}✓ Image Docker supprimée\${NC}"
else
    echo -e "\${YELLOW}⚠ Image Docker déjà supprimée\${NC}"
fi

echo ""
echo -e "\${GREEN}═══════════════════════════════════════════════════\${NC}"
echo -e "\${GREEN}  Nettoyage terminé\${NC}"
echo -e "\${GREEN}═══════════════════════════════════════════════════\${NC}"
echo ""
echo -e "\${YELLOW}Fichiers conservés:\${NC}"
echo "  • ${APPIMAGE_NAME}"
echo "  • ${DESKTOP_FILE}"
echo "  • $(basename "$ICON_SOURCE")"
echo "  • install_BlueNotebook-${VERSION}.sh"
echo "  • uninstall_BlueNotebook-${VERSION}.sh"
echo "  • cleanup.sh (ce script)"
echo ""
CLEANUP_EOF

chmod +x "$SCRIPT_DIR/cleanup.sh"
echo -e "${GREEN}✓ Script de nettoyage créé: cleanup.sh${NC}"
echo ""

# =============================================================================
# Résumé final
# =============================================================================

APPIMAGE_SIZE=$(du -h "$SCRIPT_DIR/$APPIMAGE_NAME" | cut -f1)

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  BUILD TERMINÉ AVEC SUCCÈS !${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Fichiers générés:${NC}"
echo "  ✓ $APPIMAGE_NAME ($APPIMAGE_SIZE)"
echo "  ✓ $DESKTOP_FILE"
echo "  ✓ $(basename "$ICON_SOURCE")"
echo "  ✓ install_BlueNotebook-${VERSION}.sh"
echo "  ✓ uninstall_BlueNotebook-${VERSION}.sh"
echo "  ✓ cleanup.sh"
echo ""
echo -e "${YELLOW}Image Docker:${NC}"
echo "  • ${DOCKER_IMAGE}"
echo ""
echo -e "${YELLOW}Répertoire de build:${NC}"
echo "  • ${WORK_DIR}"
echo ""
echo -e "${CYAN}───────────────────────────────────────────────────────────────${NC}"
echo -e "${YELLOW}Prochaines étapes:${NC}"
echo ""
echo -e "${GREEN}1. Tester l'AppImage:${NC}"
echo "   chmod +x $APPIMAGE_NAME"
echo "   ./$APPIMAGE_NAME"
echo ""
echo -e "${GREEN}2. Installer dans le menu système:${NC}"
echo "   ./install_BlueNotebook-${VERSION}.sh"
echo ""
echo -e "${GREEN}3. Nettoyer les fichiers temporaires:${NC}"
echo "   ./cleanup.sh"
echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"

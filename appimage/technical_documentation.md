# Documentation Technique - BlueNotebook AppImage

## Table des matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture et choix techniques](#architecture-et-choix-techniques)
3. [Prérequis](#prérequis)
4. [Structure des fichiers](#structure-des-fichiers)
5. [Processus de construction](#processus-de-construction)
6. [Utilisation](#utilisation)
7. [Dépannage](#dépannage)
8. [Limitations et compromis](#limitations-et-compromis)


---

## Vue d'ensemble

### Objectif
Créer une AppImage portable de BlueNotebook qui peut s'exécuter sur la plupart des distributions Linux modernes **sans aucune installation préalable**.

### Résultat final (Version portable - V35_PORTABLE et suivantes)

**✅ Recommandé : Build automatisé avec `build_all_appimage.sh`**

- **Nom du fichier** : `BlueNotebook-X.Y.Z-x86_64.AppImage` (X.Y.Z = version)
- **Taille** : ~379 MB
- **Compatibilité** : Ubuntu 20.04+, Debian 11+, Fedora 34+, et distributions équivalentes (GLIBC 2.31+)
- **Dépendances système** : **AUCUNE** (PyQt5 et Qt embarqués)
- **Portabilité** : **100%** - Fonctionne sans installation
- **Build** : Un seul script `build_all_appimage.sh <VERSION>`

**Fichiers générés automatiquement :**
- `BlueNotebook-X.Y.Z-x86_64.AppImage` : L'application portable
- `BlueNotebook-X.Y.Z.desktop` : Lanceur pour le menu système
- `install_BlueNotebook-X.Y.Z.sh` : Installation automatique
- `uninstall_BlueNotebook-X.Y.Z.sh` : Désinstallation propre
- `cleanup.sh` : Nettoyage des fichiers temporaires

### Résultat final (Anciennes versions - V34 et antérieures)

**⚠️ Anciennes AppImages (avant janvier 2025)**

- **Nom du fichier** : `BlueNotebook-4.2.3-x86_64.AppImage`
- **Taille approximative** : ~150-200 MB
- **Compatibilité** : Ubuntu 20.04+, Debian 11+, Fedora 34+
- **Dépendances système requises** : PyQt5 (python3-pyqt5, python3-pyqt5.qtwebengine)
- **Portabilité** : ⚠️ Partielle - Nécessite PyQt5 installé

**Recommandation :** Utiliser les nouvelles versions portables (V35_PORTABLE+)

---

## Architecture et choix techniques

### Décisions architecturales clés

#### 1. Base Docker : Debian 11 (Bullseye)
**Choix** : Utiliser Debian 11 au lieu de Debian 12 ou Ubuntu récent

**Raison** :
- Debian 11 utilise GLIBC 2.31, compatible avec la majorité des distributions Linux encore supportées
- Debian 12 utilise GLIBC 2.38, trop récent et incompatible avec de nombreux systèmes
- La compatibilité descendante de GLIBC est critique pour la portabilité

**Compromis** :
- Légèrement moins récent, mais beaucoup plus portable

#### 2. Python 3.11.13 compilé depuis les sources
**Choix** : Compiler Python 3.11.13 dans le Docker au lieu d'utiliser le Python système

**Raison** :
- Garantit une version exacte de Python indépendante du système hôte
- Permet d'embarquer toutes les dépendances Python nécessaires
- Évite les conflits avec le Python système de l'utilisateur

**Implémentation** :
```dockerfile
# Compilation de Python depuis les sources
RUN wget https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tgz && \
    tar xzf Python-3.11.13.tgz && \
    cd Python-3.11.13 && \
    ./configure --enable-optimizations --enable-shared --prefix=/usr/local && \
    make -j$(nproc) && \
    make install && \
    ldconfig
```

#### 3. Qt/PyQt5 embarqué (Nouvelle approche - V35_PORTABLE et suivantes)

**✅ Choix actuel (depuis janvier 2025)** : Embarquer PyQt5 avec Qt complet dans l'AppImage

**Raison** :
- Le package PyQt5 (installé via pip) inclut **DÉJÀ** toutes les bibliothèques Qt
- Emplacement : `/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/`
- Contenu complet : `lib/`, `plugins/`, `libexec/QtWebEngineProcess`, `resources/`, `translations/`
- **Aucune dépendance système** nécessaire
- **Portabilité maximale** : fonctionne sur toutes distributions (GLIBC 2.31+)

**Implémentation** :
```bash
# Dans AppRun : Priorité aux bibliothèques Qt de PyQt5
export LD_LIBRARY_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/lib:..."

# Plugins Qt de PyQt5
export QT_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins/platforms"

# QtWebEngine de PyQt5
export QTWEBENGINEPROCESS_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/libexec/QtWebEngineProcess"
```

**Avantages** :
- ✅ Aucune installation système requise
- ✅ Pas de conflits de versions Qt
- ✅ Version Qt garantie compatible avec PyQt5
- ✅ Portabilité 100%

**Inconvénient** :
- ❌ Taille augmentée : ~379 MB vs ~150-200 MB

**Compromis accepté** : Portabilité maximale > Taille réduite

---

#### 3bis. Qt/PyQt5 du système hôte (Ancienne approche - V34 et antérieures)

**⚠️ Approche obsolète (avant janvier 2025)** : NE PAS embarquer Qt, utiliser celui du système

**Raison** :
- Conflits de symboles entre Qt de différentes versions (erreur `Qt_5_PRIVATE_API`)
- Les bibliothèques Qt sont étroitement liées au système graphique (X11, Wayland)
- Plugin xcb nécessite une compatibilité parfaite avec les bibliothèques système

**Problème rencontré** :
```
undefined symbol: _ZN23QPlatformVulkanInstance22presentAboutToBeQueuedEP7QWindow,
version Qt_5_PRIVATE_API
```

**Solution (ancienne)** :
- Désactiver la copie de Qt depuis Docker
- Demander à l'utilisateur d'installer PyQt5 sur son système
- Utiliser `unset QT_PLUGIN_PATH` pour forcer l'utilisation de Qt système

**Limitation** :
- ⚠️ Portabilité partielle - nécessite PyQt5 installé
- ⚠️ Dépendance système

**→ Obsolète : Utiliser la nouvelle approche (PyQt5 embarqué)**

#### 4. Bibliothèques SSL embarquées
**Choix** : Embarquer libssl.so.1.1 et libcrypto.so.1.1 dans l'AppImage

**Raison** :
- Le module Python `_ssl` (compilé) nécessite ces bibliothèques
- Nécessaire pour geopy et autres packages utilisant SSL/TLS
- Les chemins doivent être dans LD_LIBRARY_PATH

**Implémentation** :
- Copie dans plusieurs emplacements : `/usr/lib/`, `/usr/lib/x86_64-linux-gnu/`, `/lib/`, `/lib/x86_64-linux-gnu/`
- Tous ces chemins ajoutés à LD_LIBRARY_PATH

#### 5. Gestion de LD_LIBRARY_PATH
**Choix** : Configurer un LD_LIBRARY_PATH exhaustif sans inclure les bibliothèques système critiques

**Configuration finale** :
```bash
export LD_LIBRARY_PATH="$HERE/usr/local/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib:$HERE/lib/x86_64-linux-gnu:$HERE/lib:$LD_LIBRARY_PATH"
```

**Bibliothèques EXCLUES** (utilisent celles du système) :
- `libc.so.6`, `libm.so.6` (GLIBC)
- `libpthread.so`, `libdl.so`, `librt.so`
- `ld-linux-x86-64.so.2`

**Raison** :
- Ces bibliothèques système sont critiques et doivent correspondre au noyau
- Les embarquer causerait des erreurs `GLIBC_PRIVATE` ou `symbol lookup error`

---

## Prérequis

### Sur la machine de build
- Docker installé et fonctionnel
- Accès Internet (pour télécharger appimagetool et sources Python)
- ~5 GB d'espace disque libre
- Bash shell

### Sur la machine cible (utilisateur final)
- Distribution Linux avec GLIBC 2.31+ (Ubuntu 20.04+, Debian 11+, Fedora 34+)
- PyQt5 installé :
  ```bash
  # Ubuntu/Debian
  sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine
  
  # Fedora
  sudo dnf install python3-qt5 python3-qt5-webengine
  
  # Arch
  sudo pacman -S python-pyqt5 python-pyqt5-webengine
  
  # Ou via pip
  pip3 install --user PyQt5 PyQtWebEngine
  ```

---

## Structure des fichiers

```
BlueNotebook-AppImage/
├── Dockerfile                              # Image Docker avec Debian 11 + Python 3.11.13
├── requirements.txt                        # Dépendances Python de BlueNotebook
├── build-appimage.sh                       # Script de construction de l'AppImage
├── bluenotebook_256-x256_fond_blanc.png   # Icône personnalisée (256x256 PNG)
├── BlueNotebook-4.2.3-x86_64.AppImage     # AppImage finale (générée)
├── BlueNotebook-4.2.3.desktop             # Fichier .desktop (généré)
├── install-bluenotebook.sh                # Script d'installation (à créer)
└── uninstall-bluenotebook.sh              # Script de désinstallation (à créer)
```

### Contenu de l'AppImage

```
BlueNotebook.AppDir/
├── AppRun                        # Script de lancement principal
├── bluenotebook.desktop          # Fichier desktop pour intégration système
├── bluenotebook.svg              # Icône de l'application
├── app/                          # Code source de BlueNotebook
│   └── bluenotebook/
├── usr/
│   ├── local/
│   │   ├── bin/
│   │   │   └── python3.11        # Python 3.11.13 compilé
│   │   └── lib/
│   │       ├── python3.11/       # Bibliothèque standard Python
│   │       │   ├── encodings/
│   │       │   ├── lib-dynload/  # Modules C compilés (_ssl, etc.)
│   │       │   └── site-packages/ # PyQt5, geopy, markdown, etc.
│   │       └── libpython3.11.so.1.0
│   └── lib/
│       └── x86_64-linux-gnu/
│           ├── libssl.so.1.1     # Bibliothèques SSL/TLS
│           ├── libcrypto.so.1.1
│           └── ...               # Autres dépendances (cairo, pango, etc.)
└── lib/
    └── x86_64-linux-gnu/
        └── libssl.so.1.1         # Copie supplémentaire pour compatibilité
```

---

## Processus de construction

### Méthode recommandée : Build automatisé (Nouveau)

**✅ Méthode recommandée depuis janvier 2025**

Le nouveau système de build automatisé simplifie considérablement la création d'AppImages pour n'importe quelle version de BlueNotebook.

#### Script unique : `build_all_appimage.sh`

**Usage :**
```bash
./build_all_appimage.sh <VERSION>
```

**Exemple :**
```bash
# Build de la version 4.2.3
./build_all_appimage.sh 4.2.3

# Build de la version 4.3.0
./build_all_appimage.sh 4.3.0
```

#### Ce que fait le script automatiquement

1. **Génération du Dockerfile spécifique**
   - À partir du template `Dockerfile.template`
   - Injection du tag Git `vX.Y.Z`
   - Création dans `build_X.Y.Z/Dockerfile`

2. **Construction de l'image Docker**
   - Nom : `bluenotebook-appimage:X.Y.Z`
   - Base : Debian 11 (GLIBC 2.31)
   - Python 3.11.13 compilé
   - Clonage de BlueNotebook depuis GitHub (tag spécifique)

3. **Construction de l'AppImage**
   - Extraction du contenu Docker
   - Assemblage de la structure AppDir
   - PyQt5 avec Qt embarqué (portabilité maximale)
   - Génération de l'AppImage

4. **Génération des fichiers complémentaires**
   - `BlueNotebook-X.Y.Z-x86_64.AppImage` : L'application portable
   - `BlueNotebook-X.Y.Z.desktop` : Lanceur pour le menu système
   - `install_BlueNotebook-X.Y.Z.sh` : Script d'installation
   - `uninstall_BlueNotebook-X.Y.Z.sh` : Script de désinstallation
   - `cleanup.sh` : Nettoyage des fichiers temporaires

#### Avantages du build automatisé

✅ **Un seul script** pour tout le processus
✅ **Multi-versions** : Support de n'importe quelle version GitHub
✅ **Reproductible** : Build identique à chaque exécution
✅ **Scripts générés** : Installation/désinstallation automatiques
✅ **Portable** : PyQt5/Qt embarqué (aucune dépendance système)
✅ **Nettoyage intégré** : Un script pour tout supprimer

#### Fichiers requis

```
appimage/
├── build_all_appimage.sh                   # Script principal
├── Dockerfile.template                      # Template Docker générique
└── bluenotebook_256-x256_fond_blanc.png    # Icône 256x256
```

#### Fichiers générés après build

```
appimage/
├── BlueNotebook-X.Y.Z-x86_64.AppImage      # ✓ AppImage portable (379 MB)
├── BlueNotebook-X.Y.Z.desktop              # ✓ Lanceur système
├── install_BlueNotebook-X.Y.Z.sh           # ✓ Script d'installation
├── uninstall_BlueNotebook-X.Y.Z.sh         # ✓ Script de désinstallation
├── cleanup.sh                               # ✓ Script de nettoyage
└── build_X.Y.Z/                             # Répertoire de travail (supprimable)
```

#### Workflow complet

```bash
# 1. Build automatique
./build_all_appimage.sh 4.2.3

# 2. Test
./BlueNotebook-4.2.3-x86_64.AppImage

# 3. Installation dans le menu
./install_BlueNotebook-4.2.3.sh

# 4. Nettoyage
./cleanup.sh
```

Pour plus de détails, voir [README_BUILD_SYSTEM.md](README_BUILD_SYSTEM.md).

---

### Méthode manuelle (Ancienne)

**⚠️ Cette méthode est conservée pour référence mais le build automatisé est recommandé**

### Phase 1 : Construction de l'image Docker

#### Dockerfile expliqué

```dockerfile
# Base : Debian 11 pour GLIBC 2.31
FROM debian:11-slim AS builder

# Installation des outils de build
RUN apt-get update && apt-get install -y \
    git wget build-essential \
    # Dépendances Python
    libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libncursesw5-dev xz-utils tk-dev \
    libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev \
    # Dépendances graphiques (pour les headers, pas runtime)
    libcairo2-dev libpango1.0-dev libgdk-pixbuf-2.0-dev \
    qtbase5-dev qtwebengine5-dev

# Compilation de Python 3.11.13
# --enable-optimizations : Active les optimisations PGO
# --enable-shared : Crée libpython3.11.so pour les modules C
# --prefix=/usr/local : Installation dans /usr/local
WORKDIR /tmp
RUN wget https://www.python.org/ftp/python/3.11.13/Python-3.11.13.tgz && \
    tar xzf Python-3.11.13.tgz && \
    cd Python-3.11.13 && \
    ./configure --enable-optimizations --enable-shared --prefix=/usr/local && \
    make -j$(nproc) && \
    make install && \
    ldconfig

# Clonage de BlueNotebook depuis GitHub
ARG GIT_COMMIT=main
RUN git clone https://github.com/lephotographelibre/BlueNotebook.git /app && \
    cd /app && \
    git checkout $GIT_COMMIT && \
    rm -rf /app/.git

# Installation des dépendances Python
WORKDIR /app
RUN /usr/local/bin/pip3.11 install --no-cache-dir -r requirements.txt

# Image finale minimale (sans outils de build)
FROM debian:11-slim
RUN apt-get update && apt-get install -y \
    # Bibliothèques runtime uniquement
    libcairo2 libpango-1.0-0 libgdk-pixbuf-2.0-0 \
    libssl1.1 libffi7 libsqlite3-0 \
    # Qt runtime (pas utilisé dans AppImage finale, mais présent dans Docker)
    libqt5widgets5 libqt5gui5 libqt5core5a libqt5webengine5

# Copie depuis le builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app

# Configuration ldconfig pour libpython
RUN echo "/usr/local/lib" > /etc/ld.so.conf.d/python.conf && ldconfig
```

**Construction de l'image** :
```bash
docker build -t jmdigne/bluenotebook:4.2.3 -f Dockerfile .
```

**Temps de build** : 15-30 minutes (compilation de Python)

### Phase 2 : Extraction et assemblage de l'AppImage

Le script `build-appimage.sh` effectue les étapes suivantes :

#### 2.1 Extraction du contenu Docker
```bash
CONTAINER_ID=$(docker create "$DOCKER_IMAGE")
docker export "$CONTAINER_ID" | tar -x -C "$TEMP_EXTRACT"
docker rm "$CONTAINER_ID"
```

**Pourquoi `docker export` ?**
- Extrait le système de fichiers complet du container
- Permet de copier sélectivement les fichiers nécessaires

#### 2.2 Copie de Python et dépendances
```bash
# Copie COMPLÈTE de /usr/local (Python + packages)
cp -r "$TEMP_EXTRACT/usr/local/lib" "$APPDIR/usr/local/"
cp -r "$TEMP_EXTRACT/usr/local/bin" "$APPDIR/usr/local/"
```

**Points critiques** :
- Copier `/usr/local/lib` ENTIER pour inclure :
  - `python3.11/` (stdlib complète avec encodings, collections, etc.)
  - `python3.11/lib-dynload/` (modules C comme _ssl, _sqlite3)
  - `python3.11/site-packages/` (PyQt5, geopy, markdown, etc.)
  - `libpython3.11.so.1.0` (bibliothèque partagée)

#### 2.3 Copie de libssl dans tous les emplacements
```bash
# Recherche exhaustive de libssl
for search_dir in "$TEMP_EXTRACT/usr/lib/x86_64-linux-gnu" \
                  "$TEMP_EXTRACT/usr/lib" \
                  "$TEMP_EXTRACT/lib/x86_64-linux-gnu" \
                  "$TEMP_EXTRACT/lib"; do
    find "$search_dir" -name "libssl.so*" -o -name "libcrypto.so*" | while read lib; do
        # Copier dans TOUS les emplacements possibles
        cp -P "$lib" "$APPDIR/usr/lib/x86_64-linux-gnu/"
        cp -P "$lib" "$APPDIR/usr/lib/"
        cp -P "$lib" "$APPDIR/lib/x86_64-linux-gnu/"
        cp -P "$lib" "$APPDIR/lib/"
    done
done
```

**Pourquoi plusieurs copies ?**
- Différents systèmes cherchent libssl dans différents chemins
- Le module `_ssl.so` utilise un chemin compilé en dur
- Redondance pour maximiser la compatibilité

#### 2.4 Copie des autres bibliothèques
```bash
LIBS_TO_COPY=(
    "libcairo.so*" "libpango*.so*" "libgdk_pixbuf*.so*"
    "libfreetype.so*" "libfontconfig.so*" "libpng16.so*"
    "libffi.so*" "libglib*.so*" "libharfbuzz*.so*"
    "libz.so*" "libexpat.so*" "libbz2.so*"
    "libsqlite3.so*" "libreadline.so*" "liblzma.so*"
    # Bibliothèques X11 (pour compatibilité, même si Qt système est utilisé)
    "libxcb*.so*" "libX11*.so*" "libXext*.so*" "libXrender*.so*"
)
```

**Note** : Les bibliothèques Qt ne sont PAS copiées (commentées dans le script)

#### 2.5 Nettoyage des bibliothèques système
```bash
# Supprimer les bibliothèques système critiques
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libc.so"* 
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libpthread.so"* 
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/libdl.so"* 
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/librt.so"* 
rm -f "$APPDIR/usr/lib/x86_64-linux-gnu/ld-linux"*
```

**Critique** : Ne JAMAIS embarquer ces bibliothèques, elles doivent venir du système

#### 2.6 Création du script AppRun

**Variables d'environnement clés** :

```bash
# Chemins de bibliothèques (ordre important !)
export LD_LIBRARY_PATH="$HERE/usr/local/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib:$HERE/lib/x86_64-linux-gnu:$HERE/lib:$LD_LIBRARY_PATH"

# Configuration Python
export PYTHONHOME="$HERE/usr/local"           # Où Python cherche sa stdlib
export PYTHONPATH="$HERE/usr/local/lib/python3.11/site-packages:$PYTHONPATH"
export PATH="$HERE/usr/local/bin:$PATH"       # Pour trouver python3.11

# Qt du système
unset QT_PLUGIN_PATH                          # Force utilisation Qt système
unset QT_QPA_PLATFORM_PLUGIN_PATH
```

**Vérification PyQt5** :
```bash
python3 -c "import PyQt5.QtWidgets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "ERREUR: PyQt5 non installé sur le système"
    # Afficher instructions d'installation
    exit 1
fi
```

**Lancement** :
```bash
cd "$HERE/app/bluenotebook"
exec "$HERE/usr/local/bin/python3.11" main.py "$@"
```

#### 2.7 Génération de l'AppImage avec appimagetool
```bash
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
ARCH=x86_64 appimagetool-x86_64.AppImage --no-appstream "$APPDIR" "$OUTPUT_APPIMAGE"
```

---

## Utilisation

### Nouvelle version portable (V35_PORTABLE et suivantes)

**✅ Recommandé : AppImages générées avec build_all_appimage.sh**

Les nouvelles AppImages (générées depuis janvier 2025) sont **100% portables** et n'ont **AUCUNE dépendance système**.

#### Pas d'installation PyQt5 nécessaire

❌ **Plus besoin d'installer PyQt5** sur le système
✅ PyQt5 et Qt sont **embarqués** dans l'AppImage

#### Lancement de l'application

```bash
chmod +x BlueNotebook-4.2.3-x86_64.AppImage
./BlueNotebook-4.2.3-x86_64.AppImage
```

L'application démarre directement, sans aucune installation préalable.

#### Options de debug

```bash
# Debug SSL (vérifier libssl)
./BlueNotebook-4.2.3-x86_64.AppImage --debug-ssl

# Debug Qt (vérifier plugins Qt embarqués)
./BlueNotebook-4.2.3-x86_64.AppImage --debug-qt
```

#### Intégration système (recommandé)

Le script de build génère automatiquement les scripts d'installation :

```bash
# Installation dans le menu système
./install_BlueNotebook-4.2.3.sh

# Désinstallation du menu
./uninstall_BlueNotebook-4.2.3.sh
```

Après installation, l'application apparaît dans :
- **Menu Applications** → **Bureautique** → **BlueNotebook**
- **Recherche d'applications** (tapez "BlueNotebook")

---

### Anciennes versions (V34 et antérieures)

**⚠️ Anciennes AppImages nécessitant PyQt5 système**

Si vous utilisez une ancienne AppImage (avant V35_PORTABLE) :

#### Installation de PyQt5 (une seule fois)

```bash
# Ubuntu/Debian
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine

# Fedora
sudo dnf install python3-qt5 python3-qt5-webengine

# Arch Linux
sudo pacman -S python-pyqt5 python-pyqt5-webengine

# Ou via pip (utilisateur)
pip3 install --user PyQt5 PyQtWebEngine
```

#### Lancement

```bash
chmod +x BlueNotebook-4.2.3-x86_64.AppImage
./BlueNotebook-4.2.3-x86_64.AppImage
```

**Recommandation :** Passer à la version portable (V35_PORTABLE+) pour éliminer cette dépendance.

#### Méthode manuelle

1. **Le fichier .desktop est généré automatiquement** par le script de build :
   - Nom : `BlueNotebook-4.2.3.desktop`
   - Chemin absolu vers l'AppImage pré-configuré
   - Icône intégrée
   - Catégorie : Bureautique (Office)

2. **Installation manuelle** :
```bash
# Rendre l'AppImage exécutable
chmod +x BlueNotebook-4.2.3-x86_64.AppImage

# Copier le fichier .desktop
cp BlueNotebook-4.2.3.desktop ~/.local/share/applications/

# Mettre à jour la base de données
update-desktop-database ~/.local/share/applications/

# Mettre à jour le cache des icônes (optionnel)
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

3. **Désinstallation manuelle** :
```bash
# Supprimer le lanceur
rm ~/.local/share/applications/BlueNotebook-4.2.3.desktop

# Supprimer l'icône (si copiée)
rm ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png

# Mettre à jour la base de données
update-desktop-database ~/.local/share/applications/

# Mettre à jour le cache des icônes
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

#### Contenu du fichier .desktop généré

```ini
[Desktop Entry]
Version=1.0
Type=Application
Name=BlueNotebook
GenericName=Journal personnel
Comment=Journal personnel et organisateur de notes
Exec=/chemin/absolu/vers/BlueNotebook-4.2.3-x86_64.AppImage %F
Icon=/chemin/absolu/vers/BlueNotebook-4.2.3-x86_64.AppImage
Terminal=false
Categories=Office;Calendar;Diary;
MimeType=text/plain;
Keywords=journal;diary;notes;markdown;
StartupNotify=true
StartupWMClass=bluenotebook
```

**Paramètres expliqués** :
- `Exec` : Chemin absolu vers l'AppImage (généré automatiquement)
- `Icon` : Utilise l'icône intégrée dans l'AppImage
- `Categories` : Place l'application dans le menu Bureautique
- `%F` : Permet d'ouvrir des fichiers par double-clic
- `StartupWMClass` : Améliore l'identification de la fenêtre

#### Scripts d'installation/désinstallation

Le script de build génère également deux scripts helper :

**install-bluenotebook.sh** :
- Vérifie la présence de l'AppImage et du .desktop
- Rend l'AppImage exécutable
- Copie l'icône dans `~/.local/share/icons/`
- Installe le lanceur dans `~/.local/share/applications/`
- Met à jour les bases de données système

**uninstall-bluenotebook.sh** :
- Supprime le lanceur du menu
- Supprime l'icône
- Met à jour les bases de données
- **Conserve** vos données dans `~/.bluenotebook`
- **Conserve** le fichier AppImage (ne le supprime pas automatiquement)

#### Localisation de l'application

Après installation, BlueNotebook apparaît dans :
- **Menu Applications** → **Bureautique** → **BlueNotebook**
- **Recherche d'applications** (tapez "BlueNotebook" ou "journal")
- **Fichiers récents** (si configuré)

#### Gestion des icônes

L'icône personnalisée (`bluenotebook_256-x256_fond_blanc.png`) est :
1. **Intégrée dans l'AppImage** lors du build
2. **Copiée dans le cache système** lors de l'installation
3. **Utilisée par le menu** pour afficher l'application

Si l'icône n'apparaît pas immédiatement :
```bash
# Forcer le rafraîchissement du cache
rm -rf ~/.cache/thumbnails/*
gtk-update-icon-cache ~/.local/share/icons/hicolor/
```

#### Notes importantes

- Le fichier `.desktop` utilise des **chemins absolus** générés automatiquement
- Si vous déplacez l'AppImage, réinstallez avec `./install-bluenotebook.sh`
- Vos données dans `~/.bluenotebook` sont **toujours conservées** lors de la désinstallation
- L'AppImage elle-même n'est **jamais supprimée** automatiquement

---

## Dépannage

### Problème : "libssl.so.1.1: cannot open shared object file"

**Cause** : Le module Python `_ssl` ne trouve pas libssl

**Solution** :
1. Extraire l'AppImage : `./BlueNotebook-4.2.3-x86_64.AppImage --appimage-extract`
2. Vérifier présence : `find squashfs-root -name "libssl.so*"`
3. Si absent, reconstruire l'AppImage avec le script mis à jour
4. Si présent, vérifier LD_LIBRARY_PATH dans `squashfs-root/AppRun`

**Debug** :
```bash
./BlueNotebook-4.2.3-x86_64.AppImage --debug-ssl
```

### Problème : "Could not load the Qt platform plugin 'xcb'"

**Cause 1** : PyQt5 non installé sur le système
```bash
python3 -c "import PyQt5.QtWidgets"
# Si erreur : installer PyQt5
sudo apt install python3-pyqt5 python3-pyqt5.qtwebengine
```

**Cause 2** : Conflit de versions Qt
```bash
# Vérifier les symboles undefined
QT_DEBUG_PLUGINS=1 ./BlueNotebook-4.2.3-x86_64.AppImage 2>&1 | grep "undefined symbol"
```

**Solution** : S'assurer que Qt n'est PAS embarqué dans l'AppImage (voir script build)

### Problème : "GLIBC_2.XX not found"

**Cause** : Système trop ancien ou image Docker construite avec Debian 12+

**Solution** :
1. Vérifier version GLIBC système : `ldd --version`
2. Reconstruire Docker avec Debian 11 (GLIBC 2.31)
3. Ne JAMAIS utiliser python:3.11-slim directement (utilise Debian 12)

### Problème : "No module named 'encodings'"

**Cause** : Bibliothèque standard Python incomplète

**Solution** :
1. Vérifier dans le build : `/usr/local/lib` ENTIER doit être copié
2. Ne pas copier seulement `python3.11/site-packages`, mais tout `/usr/local/lib`

---

## Limitations et compromis

### 1. Dépendance à PyQt5 système
**Limitation** : L'utilisateur doit installer PyQt5

**Raison** : Incompatibilités Qt entre distributions (symboles Qt_5_PRIVATE_API)

**Impact** : AppImage n'est pas 100% autonome, mais reste simple à installer

### 2. Compatibilité GLIBC
**Limitation** : Nécessite GLIBC 2.31+ (Ubuntu 20.04+, Debian 11+)

**Raison** : Python 3.11.13 compilé avec Debian 11

**Alternative possible** : Utiliser manylinux pour compatibilité CentOS 7 (GLIBC 2.17), mais plus complexe

### 3. Taille de l'AppImage
**Taille** : ~150-200 MB

**Contenu** :
- Python 3.11.13 complet : ~50 MB
- Bibliothèques Python (PyQt5, geopy, etc.) : ~80 MB
- Application BlueNotebook : ~20 MB
- Bibliothèques système (SSL, Cairo, etc.) : ~30 MB

**Compromis** : Portabilité vs taille

### 4. Pas de support 32-bit
**Limitation** : x86_64 uniquement

**Raison** : Python 3.11 et distributions modernes sont 64-bit

### 5. Pas de mise à jour automatique
**Limitation** : Pas de mécanisme de mise à jour intégré

**Solution possible** : Implémenter AppImageUpdate dans une version future

---

## Améliorations futures possibles

### 1. Support AppImageUpdate
Ajouter `appimageupdate` dans l'AppImage pour permettre les mises à jour :
```bash
# Dans le .desktop
[Desktop Entry]
X-AppImage-Update-Information=gh-releases-zsync|user|repo|latest|BlueNotebook-*-x86_64.AppImage.zsync
```

### 2. Réduction de taille
- Utiliser `strip` sur les bibliothèques
- Compresser avec `upx` (non recommandé pour Python)
- Exclure les modules Python inutilisés

### 3. Support multi-architecture
- Créer BlueNotebook-4.2.3-aarch64.AppImage pour ARM64
- Utiliser Docker buildx pour cross-compilation

### 4. Signature GPG
```bash
gpg --detach-sign BlueNotebook-4.2.3-x86_64.AppImage
```

### 5. CI/CD automatisé
GitHub Actions pour build automatique :
```yaml
name: Build AppImage
on:
  push:
    tags:
      - 'v*'
jobs:
  build:
    runs-on: ubuntu-20.04
    steps:
      - uses: actions/checkout@v2
      - name: Build Docker image
        run: docker build -t bluenotebook .
      - name: Build AppImage
        run: ./build-appimage.sh
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: BlueNotebook-AppImage
          path: BlueNotebook-*.AppImage
```

---

## Ressources et références

### Documentation officielle
- [AppImage Documentation](https://docs.appimage.org/)
- [Python Build from Source](https://devguide.python.org/getting-started/setup-building/)
- [Qt Platform Plugin](https://doc.qt.io/qt-5/qpa.html)

### Outils utilisés
- [appimagetool](https://github.com/AppImage/AppImageKit)
- [Docker](https://www.docker.com/)
- [Python 3.11.13](https://www.python.org/downloads/release/python-31113/)

### Problèmes connus et solutions
- [Qt Symbol Issues](https://bugreports.qt.io/browse/QTBUG-68814)
- [GLIBC Compatibility](https://developers.redhat.com/blog/2019/08/01/how-the-gnu-c-library-handles-backward-compatibility)
- [AppImage Best Practices](https://github.com/AppImage/AppImageKit/wiki/AppImage-Best-Practices)

---

## Contributeurs et maintenance

**Auteur initial** : Jean-Marc Digne (jmdigne)

**Repository** : https://github.com/lephotographelibre/BlueNotebook

**License** : À spécifier dans le repository

**Contact** : Via GitHub Issues

---

## Changelog

### Système de Build V1.0.0 (20 Janvier 2025)
- ✅ **Nouveau système de build automatisé** (`build_all_appimage.sh`)
- ✅ Support multi-versions via tags Git
- ✅ Dockerfile.template générique
- ✅ PyQt5 avec Qt embarqué (portabilité 100%)
- ✅ Génération automatique des scripts d'installation/désinstallation
- ✅ Script de nettoyage intégré
- ✅ Taille AppImage: ~379 MB (au lieu de ~150-200 MB, mais aucune dépendance système)
- ✅ Documentation complète du nouveau système

### Version 4.2.3 (Janvier 2025)
- ✅ Build initial de l'AppImage
- ✅ Python 3.11.13 embarqué
- ✅ Support SSL/TLS (libssl.so.1.1)
- ✅ Compatibilité Debian 11+ (GLIBC 2.31)
- ✅ ~~Utilisation de PyQt5 système pour éviter conflits Qt~~ **→ Obsolète**
- ✅ **PyQt5 avec Qt embarqué** (V35_PORTABLE et suivantes)
- ✅ Scripts de debug intégrés (--debug-ssl, --debug-qt)
- ✅ Documentation technique complète
- ✅ Icône haute résolution (256x256)

### Prochaines versions prévues
- [ ] Support AppImageUpdate
- [ ] Build ARM64
- [ ] CI/CD GitHub Actions avec build_all_appimage.sh
- [ ] Signature GPG
- [ ] Optimisation de taille (strip, compression)

---

## Annexes

### Annexe A : Système de build automatisé

#### Vue d'ensemble

Le nouveau système de build automatisé (janvier 2025) simplifie radicalement la création d'AppImages pour BlueNotebook.

#### Composants du système

**Fichiers de base requis :**
```
appimage/
├── build_all_appimage.sh              # Script principal (1 commande = tout)
├── Dockerfile.template                 # Template Docker générique
└── bluenotebook_256-x256_fond_blanc.png  # Icône 256x256
```

**Fichiers générés automatiquement :**
```
appimage/
├── BlueNotebook-X.Y.Z-x86_64.AppImage      # AppImage portable
├── BlueNotebook-X.Y.Z.desktop              # Lanceur système
├── install_BlueNotebook-X.Y.Z.sh           # Installation
├── uninstall_BlueNotebook-X.Y.Z.sh         # Désinstallation
├── cleanup.sh                               # Nettoyage
└── build_X.Y.Z/                             # Répertoire de travail
    ├── Dockerfile                           # Dockerfile spécifique
    ├── BlueNotebook.AppDir/                 # Structure AppImage
    └── appimagetool-x86_64.AppImage
```

#### Workflow automatique

1. **Génération du Dockerfile**
   ```bash
   # Le script copie Dockerfile.template et injecte le tag Git
   ARG GIT_TAG=vX.Y.Z
   ```

2. **Build Docker**
   ```bash
   docker build --build-arg GIT_TAG=vX.Y.Z \
                -t bluenotebook-appimage:X.Y.Z \
                -f build_X.Y.Z/Dockerfile .
   ```

3. **Extraction et assemblage**
   - Extraction du container avec `docker export`
   - Copie de Python, PyQt5, bibliothèques
   - PyQt5 avec Qt embarqué (site-packages/PyQt5/Qt5/)
   - Création du script AppRun avec tous les paths

4. **Génération AppImage**
   ```bash
   appimagetool --no-appstream BlueNotebook.AppDir \
                BlueNotebook-X.Y.Z-x86_64.AppImage
   ```

5. **Génération des scripts**
   - Installation : copie dans ~/.local/share/
   - Désinstallation : supprime lanceur et icône
   - Nettoyage : supprime build_X.Y.Z/ et image Docker

#### Utilisation complète

```bash
# 1. Build automatique pour version 4.2.3
./build_all_appimage.sh 4.2.3

# 2. Test immédiat
./BlueNotebook-4.2.3-x86_64.AppImage

# 3. Installation système
./install_BlueNotebook-4.2.3.sh

# 4. Nettoyage des fichiers temporaires
./cleanup.sh
```

#### Avantages vs ancien processus

| Aspect | Ancien processus | Nouveau processus |
|--------|------------------|-------------------|
| **Scripts** | Multiples (build-appimage.sh, rebuild, etc.) | 1 seul (build_all_appimage.sh) |
| **Versions** | Modification manuelle des scripts | Paramètre de ligne de commande |
| **Dockerfile** | Modification manuelle | Généré automatiquement |
| **Scripts install** | Création manuelle | Générés automatiquement |
| **Nettoyage** | Manuel | Script cleanup.sh généré |
| **PyQt5** | ~~Dépendance système~~ | Embarqué (100% portable) |
| **Taille** | ~150-200 MB | ~379 MB |
| **Portabilité** | ⚠️ Nécessite PyQt5 système | ✅ Aucune dépendance |

#### Architecture PyQt5/Qt embarqué

**Structure dans l'AppImage :**
```
usr/local/lib/python3.11/site-packages/PyQt5/
└── Qt5/
    ├── lib/                    # Bibliothèques Qt (libQt5Core.so, etc.)
    ├── plugins/                # Plugins Qt
    │   └── platforms/          # libqxcb.so, libqwayland.so
    ├── libexec/                # QtWebEngineProcess
    ├── resources/              # Ressources QtWebEngine
    └── translations/           # Locales QtWebEngine
```

**Variables d'environnement dans AppRun :**
```bash
# CRITICAL: Qt de PyQt5 EN PREMIER
export LD_LIBRARY_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/lib:..."

# Plugins Qt de PyQt5
export QT_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins"
export QT_QPA_PLATFORM_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins/platforms"

# QtWebEngine de PyQt5
export QTWEBENGINEPROCESS_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/libexec/QtWebEngineProcess"
```

**Pourquoi Qt embarqué ?**

✅ **Avantages :**
- Aucune dépendance PyQt5 système
- Pas de conflits de versions Qt
- Fonctionne sur toutes distributions (GLIBC 2.31+)
- Version Qt garantie compatible avec PyQt5

❌ **Inconvénient :**
- Taille augmentée (~379 MB vs ~150-200 MB)

**Compromis accepté :** Portabilité maximale > Taille réduite

#### Processus de génération détaillé

**1. Vérification des prérequis**
```bash
# Docker installé ?
command -v docker

# Icône présente ?
[ -f bluenotebook_256-x256_fond_blanc.png ]

# Template présent ?
[ -f Dockerfile.template ]
```

**2. Création du répertoire de build**
```bash
mkdir -p build_4.2.3
cd build_4.2.3
```

**3. Génération du Dockerfile**
```bash
cp ../Dockerfile.template Dockerfile
# Injection : ARG GIT_TAG=v4.2.3
```

**4. Build Docker**
```bash
docker build --build-arg GIT_TAG=v4.2.3 \
             -t bluenotebook-appimage:4.2.3 \
             -f Dockerfile .
# Temps : 15-30 minutes (compilation Python)
```

**5. Extraction Docker**
```bash
CONTAINER_ID=$(docker create bluenotebook-appimage:4.2.3)
docker export $CONTAINER_ID | tar -x -C temp_docker_extract
docker rm $CONTAINER_ID
```

**6. Assemblage AppDir**
```bash
# Copie complète de /usr/local (Python + site-packages)
cp -r temp_docker_extract/usr/local/lib AppDir/usr/local/
cp -r temp_docker_extract/usr/local/bin AppDir/usr/local/

# Copie SSL (multiple emplacements pour compatibilité)
cp libssl.so.1.1 AppDir/usr/lib/x86_64-linux-gnu/
cp libssl.so.1.1 AppDir/lib/x86_64-linux-gnu/

# Copie bibliothèques système (sans GLIBC)
cp libcairo.so* libpango*.so* ... AppDir/usr/lib/x86_64-linux-gnu/

# Note : Qt N'EST PAS copié depuis le système
# Qt est déjà dans site-packages/PyQt5/Qt5/
```

**7. Création AppRun**
```bash
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
export LD_LIBRARY_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/lib:..."
export QT_PLUGIN_PATH="$HERE/usr/local/lib/python3.11/site-packages/PyQt5/Qt5/plugins"
exec "$HERE/usr/local/bin/python3.11" main.py "$@"
EOF
chmod +x AppDir/AppRun
```

**8. Génération AppImage**
```bash
ARCH=x86_64 appimagetool --no-appstream \
            BlueNotebook.AppDir \
            BlueNotebook-4.2.3-x86_64.AppImage
```

**9. Génération .desktop**
```bash
cat > BlueNotebook-4.2.3.desktop << EOF
[Desktop Entry]
Exec=/chemin/absolu/BlueNotebook-4.2.3-x86_64.AppImage %F
Icon=/chemin/absolu/BlueNotebook-4.2.3-x86_64.AppImage
EOF
```

**10. Génération scripts install/uninstall**
```bash
# install_BlueNotebook-4.2.3.sh
# - Copie .desktop dans ~/.local/share/applications/
# - Copie icône dans ~/.local/share/icons/
# - update-desktop-database

# uninstall_BlueNotebook-4.2.3.sh
# - Supprime .desktop et icône
# - update-desktop-database
# - Conserve AppImage et données
```

**11. Génération script cleanup**
```bash
# cleanup.sh
# - Supprime build_4.2.3/
# - Supprime image Docker bluenotebook-appimage:4.2.3
# - Conserve AppImage et scripts
```

#### Options de debug

L'AppImage générée inclut des options de diagnostic :

```bash
# Debug SSL/TLS
./BlueNotebook-4.2.3-x86_64.AppImage --debug-ssl
# Affiche : chemins libssl, LD_LIBRARY_PATH

# Debug Qt
./BlueNotebook-4.2.3-x86_64.AppImage --debug-qt
# Affiche : plugins Qt disponibles, dépendances libqxcb
```

#### Compatibilité et tests

**Systèmes testés :**
- ✅ Ubuntu 20.04, 22.04, 24.04
- ✅ Debian 11, 12
- ✅ Fedora 34+
- ✅ Linux Mint 20+

**Tests automatisés possibles :**
```bash
# Test dans container Docker
docker run --rm -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v $(pwd):/app \
           -e DISPLAY=$DISPLAY \
           ubuntu:20.04 /app/BlueNotebook-4.2.3-x86_64.AppImage --version
```

#### Documentation complète

Pour plus de détails, voir :
- [README_BUILD_SYSTEM.md](README_BUILD_SYSTEM.md) : Guide d'utilisation complet
- [MODIFICATIONS_PORTABLE.md](MODIFICATIONS_PORTABLE.md) : Historique des modifications
- [TEST_PORTABILITE.md](TEST_PORTABILITE.md) : Guide de test

---

### Annexe B : Commandes Docker utiles

```bash
# Vérifier version GLIBC dans l'image
docker run --rm jmdigne/bluenotebook:4.2.3 ldd --version

# Vérifier version Python
docker run --rm jmdigne/bluenotebook:4.2.3 python3.11 --version

# Explorer l'image
docker run --rm -it jmdigne/bluenotebook:4.2.3 /bin/bash

# Trouver un fichier dans l'image
docker run --rm jmdigne/bluenotebook:4.2.3 find / -name "libssl.so*"

# Tester l'application dans Docker
docker run --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix jmdigne/bluenotebook:4.2.3
```

### Annexe B : Structure complète de l'AppImage

```
BlueNotebook.AppDir/
├── AppRun                                    [Script bash, 2 KB]
├── bluenotebook.desktop                      [Desktop file, 1 KB]
├── bluenotebook.svg                          [Icône SVG, 1 KB]
├── .DirIcon -> bluenotebook.desktop
├── app/
│   └── bluenotebook/
│       ├── main.py
│       ├── gui/
│       ├── integrations/
│       └── ...
├── usr/
│   ├── local/
│   │   ├── bin/
│   │   │   ├── python3.11                    [Binaire Python, 15 MB]
│   │   │   ├── pip3.11
│   │   │   └── ...
│   │   └── lib/
│   │       ├── libpython3.11.so.1.0          [Lib Python partagée, 3 MB]
│   │       └── python3.11/
│   │           ├── encodings/                [Encodages texte]
│   │           ├── collections/              [Modules stdlib]
│   │           ├── lib-dynload/              [Modules C]
│   │           │   ├── _ssl.cpython-311-x86_64-linux-gnu.so
│   │           │   ├── _sqlite3.cpython-311-x86_64-linux-gnu.so
│   │           │   └── ...
│   │           └── site-packages/            [Packages pip]
│   │               ├── PyQt5/
│   │               ├── geopy/
│   │               ├── markdown/
│   │               └── ...
│   └── lib/
│       └── x86_64-linux-gnu/
│           ├── libssl.so.1.1                 [SSL/TLS, 600 KB]
│           ├── libcrypto.so.1.1              [Crypto, 3 MB]
│           ├── libcairo.so.2
│           ├── libpango-1.0.so.0
│           └── ...
└── lib/
    └── x86_64-linux-gnu/
        ├── libssl.so.1.1                     [Copie redondante]
        └── libcrypto.so.1.1
```

### Annexe C : Variables d'environnement complètes

Toutes les variables définies dans AppRun :

```bash
HERE="/tmp/.mount_BlueNoXXXXXX"               # Auto-généré par AppImage

# Chemins de bibliothèques
LD_LIBRARY_PATH="$HERE/usr/local/lib:$HERE/usr/lib/x86_64-linux-gnu:$HERE/usr/lib:$HERE/lib/x86_64-linux-gnu:$HERE/lib:/usr/lib:/lib"

# Configuration Python
PYTHONHOME="$HERE/usr/local"
PYTHONPATH="$HERE/usr/local/lib/python3.11/site-packages:"
PATH="$HERE/usr/local
```

### Annexe D : Scripts d'installation et désinstallation

#### install-bluenotebook.sh
```bash
#!/bin/bash
# Script d'installation de BlueNotebook dans le menu système
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

APP_NAME="BlueNotebook"
VERSION="4.2.3"
APPIMAGE_FILE="./BlueNotebook-${VERSION}-x86_64.AppImage"
DESKTOP_FILE="./BlueNotebook-${VERSION}.desktop"

echo -e "${GREEN}Installation de BlueNotebook ${VERSION}${NC}"

# Vérifications
if [ ! -f "$APPIMAGE_FILE" ]; then
    echo -e "${RED}Erreur: AppImage non trouvée${NC}"
    exit 1
fi

if [ ! -f "$DESKTOP_FILE" ]; then
    echo -e "${RED}Erreur: Fichier .desktop non trouvé${NC}"
    exit 1
fi

# Création des répertoires
mkdir -p ~/.local/share/applications
mkdir -p ~/.local/share/icons/hicolor/256x256/apps

# Rendre exécutable
chmod +x "$APPIMAGE_FILE"

# Copier l'icône
if [ -f "bluenotebook_256-x256_fond_blanc.png" ]; then
    cp bluenotebook_256-x256_fond_blanc.png \
       ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png
fi

# Installer le lanceur
cp "$DESKTOP_FILE" ~/.local/share/applications/

# Mettre à jour les bases de données
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true

echo -e "${GREEN}✓ Installation réussie !${NC}"
echo "BlueNotebook est disponible dans Menu → Bureautique"
```

#### uninstall-bluenotebook.sh
```bash
#!/bin/bash
# Script de désinstallation de BlueNotebook
set -e

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

VERSION="4.2.3"
DESKTOP_FILE="BlueNotebook-${VERSION}.desktop"

echo -e "${YELLOW}Désinstallation de BlueNotebook ${VERSION}${NC}"

# Supprimer le lanceur
rm -f ~/.local/share/applications/"$DESKTOP_FILE"

# Supprimer l'icône
rm -f ~/.local/share/icons/hicolor/256x256/apps/bluenotebook.png

# Mettre à jour les bases de données
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
gtk-update-icon-cache ~/.local/share/icons/hicolor/ 2>/dev/null || true

echo -e "${GREEN}✓ Désinstallation réussie${NC}"
echo "Note: L'AppImage et vos données ont été conservées"
```

#### Utilisation des scripts

**Installation** :
```bash
chmod +x install-bluenotebook.sh
./install-bluenotebook.sh
```

**Désinstallation** :
```bash
chmod +x uninstall-bluenotebook.sh
./uninstall-bluenotebook.sh
```


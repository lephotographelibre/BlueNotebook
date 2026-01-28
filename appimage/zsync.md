# Support des mises à jour delta avec zsync

## Introduction

Le format `.zsync` permet aux utilisateurs de mettre à jour leur AppImage en ne téléchargeant que les blocs modifiés entre deux versions, réduisant considérablement la bande passante nécessaire (généralement 80-95% d'économie).

## Modifications apportées

### 1. Script de build AppImage (`appimage/build_all_appimage.sh`)

#### Nouvelles variables (lignes 52-55)
```bash
ZSYNC_NAME="${APPIMAGE_NAME}.zsync"
APPIMAGE_URL="https://github.com/lephotographelibre/BlueNotebook/releases/download/v${VERSION}/${APPIMAGE_NAME}"
```

#### Installation de zsync dans l'image Docker (ligne 175)
Le paquet `zsync` est maintenant installé dans l'image Docker runtime :
```dockerfile
RUN apt-get update && apt-get install -y \
    zsync \
    ...
```

#### Génération du fichier .zsync (lignes 539-559)
Après la création de l'AppImage, Docker exécute `zsyncmake` pour générer le fichier `.zsync` :
```bash
docker run --rm \
    -v "$SCRIPT_DIR:/output" \
    -w /output \
    "$DOCKER_IMAGE" \
    zsyncmake -u "$APPIMAGE_URL" -o "$ZSYNC_NAME" "$APPIMAGE_NAME"
```

### 2. Script de packaging (`dev/scripts/build_assets.sh`)

Ajout de la copie du fichier `.zsync` vers le répertoire `assets/` :
```bash
mv -v BlueNotebook-$VERSION-x86_64.AppImage.zsync ../assets/BlueNotebook-$VERSION-x86_64.AppImage.zsync
```

### 3. Script d'upload (`dev/scripts/upload_asset.sh`)

Ajout du type MIME pour les fichiers `.zsync` :
```bash
*.zsync)
  CONTENT_TYPE="application/x-zsync"
  ;;
```

## Fichiers générés pour une release

Pour chaque version, les fichiers suivants sont générés et uploadés :

| Fichier | Description |
|---------|-------------|
| `BlueNotebook-X.Y.Z-x86_64.AppImage` | AppImage exécutable |
| `BlueNotebook-X.Y.Z-x86_64.AppImage.zsync` | Fichier de métadonnées pour mises à jour delta |

## Utilisation côté utilisateur

### Mise à jour manuelle avec zsync
```bash
zsync -i BlueNotebook-4.2.6-x86_64.AppImage \
  https://github.com/lephotographelibre/BlueNotebook/releases/download/v4.2.7/BlueNotebook-4.2.7-x86_64.AppImage.zsync
```

### Mise à jour avec AppImageUpdate
```bash
AppImageUpdate BlueNotebook-4.2.6-x86_64.AppImage
```

## Fonctionnement technique

1. Le fichier `.zsync` contient des checksums par blocs de l'AppImage
2. L'outil zsync compare les blocs locaux avec les checksums distants
3. Seuls les blocs différents sont téléchargés
4. Les blocs sont fusionnés pour reconstruire la nouvelle version

## Avantages

- **Bande passante réduite** : Téléchargement de ~5-20% au lieu de 100%
- **Mises à jour plus rapides** : Moins de données à transférer
- **Économie serveur** : Moins de charge sur GitHub
- **Fiabilité** : Reprise possible en cas d'interruption

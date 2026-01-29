# Guide de soumission à AppImage Hub

Ce document décrit les étapes pour soumettre BlueNotebook à [AppImage Hub](https://github.com/AppImage/appimage.github.io).

## 📋 Checklist des requis AppImage Hub

Tous ces requis ont été validés et implémentés dans le processus de build :

- ✅ **Téléchargeable depuis URL** - Disponible sur GitHub Releases
- ✅ **Compatible Ubuntu LTS** - Base Debian 11 (GLIBC 2.31)
- ✅ **Fichier .desktop valide** - Validation avec desktop-file-validate
- ✅ **AppStream metainfo** - Fichier dans usr/share/metainfo/
- ✅ **Fonctionnement hors ligne** - Fonctions principales sans Internet
- ✅ **Icône embarquée** - 256x256 PNG
- ✅ **AppRun exécutable** - Script de lancement configuré

## 🔧 Étape 1 : Reconstruire l'AppImage avec les corrections

Les corrections suivantes ont été appliquées :

1. **Ajout du fichier metainfo** dans `usr/share/metainfo/`
2. **Retrait du flag `--no-appstream`** de appimagetool
3. **Mise à jour des URLs** des screenshots vers v4.2.7

Pour reconstruire l'AppImage avec ces corrections :

```bash
cd /home/jm/Work/BlueNotebookV4.2.7/appimage
./build_all_appimage.sh 4.2.7
```

## 🧪 Étape 2 : Valider l'AppImage

Un script de validation automatique a été créé pour vérifier tous les requis :

```bash
cd /home/jm/Work/BlueNotebookV4.2.7/appimage
./validate_appimage.sh 4.2.7
```

Ce script vérifie :
- ✓ Présence et structure de l'AppDir
- ✓ Validation du fichier .desktop (desktop-file-validate)
- ✓ Validation du fichier metainfo (appstreamcli)
- ✓ Exécution de appdir-lint.sh
- ✓ Vérification de l'icône
- ✓ Vérification du script AppRun
- ✓ Vérification des dépendances Python et système

### Installation des outils de validation (si nécessaire)

```bash
# Ubuntu/Debian
sudo apt install desktop-file-utils appstream

# Les autres outils (appdir-lint.sh) sont téléchargés automatiquement
```

## 📦 Étape 3 : Créer une GitHub Release

1. **Créer un tag Git** (si pas déjà fait) :
   ```bash
   git tag v4.2.7
   git push origin v4.2.7
   ```

2. **Créer une Release sur GitHub** :
   - Aller sur https://github.com/lephotographelibre/BlueNotebook/releases
   - Cliquer sur "Draft a new release"
   - Choisir le tag `v4.2.7`
   - Titre : `BlueNotebook v4.2.7`
   - Description : Copier depuis le changelog
   - Ajouter l'AppImage comme asset

3. **Upload de l'AppImage** :
   - Nom du fichier : `BlueNotebook-4.2.7-x86_64.AppImage`
   - Localisation : `/home/jm/Work/BlueNotebookV4.2.7/appimage/BlueNotebook-4.2.7-x86_64.AppImage`

4. **Publier la release**

L'URL de téléchargement sera :
```
https://github.com/lephotographelibre/BlueNotebook/releases/download/v4.2.7/BlueNotebook-4.2.7-x86_64.AppImage
```

## 🚀 Étape 4 : Soumettre à AppImage Hub

1. **Fork du repository AppImage Hub** :
   - Aller sur https://github.com/AppImage/appimage.github.io
   - Cliquer sur "Fork"

2. **Ajouter votre AppImage** :

   Créer le fichier `data/BlueNotebook` dans votre fork :

   ```yaml
   name: BlueNotebook
   categories:
     - Office
     - Utility
   description: Markdown-based desktop application for journaling and note-taking
   authors:
     - name: Jean-Marc DIGNE
       url: https://github.com/lephotographelibre
   license: GPL-3.0-or-later
   links:
     - type: GitHub
       url: https://github.com/lephotographelibre/BlueNotebook
     - type: Download
       url: https://github.com/lephotographelibre/BlueNotebook/releases/latest/download/BlueNotebook-x86_64.AppImage
   screenshots:
     - https://raw.githubusercontent.com/lephotographelibre/BlueNotebook/v4.2.7/docs/Screencopy/V4.2.6_Editor_english.jpg
   ```

   **Note:** Utiliser `/releases/latest/download/` pour avoir une URL constante

3. **Créer une Pull Request** :
   ```bash
   git clone https://github.com/VOTRE_USERNAME/appimage.github.io.git
   cd appimage.github.io
   git checkout -b add-bluenotebook
   # Créer le fichier data/BlueNotebook avec le contenu ci-dessus
   git add data/BlueNotebook
   git commit -m "Add BlueNotebook to AppImage catalog"
   git push origin add-bluenotebook
   ```

4. **Ouvrir la PR sur GitHub** et attendre la review automatique

## ✅ Vérifications finales avant soumission

- [ ] L'AppImage a été reconstruite avec les corrections
- [ ] Le script de validation ne retourne aucune erreur critique
- [ ] La GitHub Release v4.2.7 est publiée
- [ ] L'AppImage est téléchargeable depuis l'URL GitHub Releases
- [ ] Les screenshots sont accessibles (vérifier les URLs)
- [ ] Le fichier metainfo est présent dans usr/share/metainfo/
- [ ] desktop-file-validate ne retourne pas d'erreur
- [ ] appstreamcli validate ne retourne pas d'erreur critique

## 📝 Tests manuels recommandés

Avant la soumission, tester manuellement :

1. **Télécharger et exécuter l'AppImage** :
   ```bash
   chmod +x BlueNotebook-4.2.7-x86_64.AppImage
   ./BlueNotebook-4.2.7-x86_64.AppImage
   ```

2. **Tester hors ligne** :
   - Désactiver le réseau
   - Lancer l'application
   - Vérifier que l'éditeur et le journal fonctionnent

3. **Tester sur Ubuntu LTS** (si possible) :
   - Ubuntu 20.04 LTS (minimum supporté)
   - Ubuntu 22.04 LTS
   - Ubuntu 24.04 LTS

## 🐛 En cas de problème

Si la validation échoue :

1. **Consulter les logs** du script de validation
2. **Corriger les erreurs** dans le code source ou le script de build
3. **Reconstruire** l'AppImage
4. **Re-valider** avec le script

Pour obtenir de l'aide :
- Issues AppImage Hub : https://github.com/AppImage/appimage.github.io/issues
- Documentation AppImage : https://docs.appimage.org/

## 📚 Ressources

- [AppImage Best Practices](https://docs.appimage.org/packaging-guide/index.html)
- [AppImage Hub Checklist](https://github.com/AppImage/appimage.github.io#checklist-for-submitting-your-own-appimage)
- [Desktop Entry Specification](https://specifications.freedesktop.org/desktop-entry-spec/latest/)
- [AppStream Specification](https://www.freedesktop.org/software/appstream/docs/)

---

**Date de dernière mise à jour :** 2026-01-29
**Version BlueNotebook :** 4.2.7

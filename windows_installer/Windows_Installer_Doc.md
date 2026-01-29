# Documentation - Création d'un Installer Windows pour BlueNotebook

## Vue d'ensemble

Ce document décrit le processus complet de création d'un installateur Windows pour l'application BlueNotebook, depuis la compilation de l'application Python jusqu'à la génération du fichier d'installation final.

## Prérequis

- Python 3.11.9 (ou version compatible)
- Environnement virtuel Python activé
- Accès administrateur pour l'installation des outils

## Outils utilisés

### 1. PyInstaller
**Version recommandée** : Dernière version stable

**Rôle** : PyInstaller transforme une application Python en exécutable standalone Windows (.exe) qui peut fonctionner sans installation Python préalable.

**Installation** :
```bash
pip install pyinstaller pyinstaller-hooks-contrib
```

**Composants** :
- `pyinstaller` : Outil principal de compilation
- `pyinstaller-hooks-contrib` : Collection de hooks pour gérer les dépendances spécifiques de bibliothèques tierces

### 2. InstallForge
**Éditeur** : solicus  
**Rôle** : Créateur d'installateurs Windows professionnels avec interface graphique

**Chemin d'installation** : `C:\Program Files (x86)\solicus\InstallForge\`

**Exécutable en ligne de commande** : `ifbuildx86.exe`

## Processus de création - Étape par étape

### Étape 1 : Préparation de l'environnement

Activez votre environnement virtuel Python :
```powershell
# L'environnement doit être activé (indiqué par le préfixe)
(.venv_3.11.9) PS C:\Users\jmdig\github\BlueNotebook\bluenotebook\dist>
```

### Étape 2 : Compilation avec PyInstaller

**Commande** :
```powershell
pyinstaller main.spec --clean --noconfirm
```

**Paramètres expliqués** :
- `main.spec` : Fichier de configuration PyInstaller contenant les instructions de compilation
- `--clean` : Nettoie le cache et les builds précédents avant de compiler
- `--noconfirm` : Ne demande pas de confirmation avant de supprimer les fichiers existants

**Résultat** : 
- Création du dossier `dist\BlueNotebook\` contenant l'exécutable et toutes ses dépendances
- L'exécutable principal : `BlueNotebook.exe`

**Vérification** :
```powershell
.\BlueNotebook\BlueNotebook.exe
```
Cette commande lance l'application pour vérifier que la compilation s'est bien déroulée.

### Étape 3 : Création de l'installateur avec InstallForge

**Commande PowerShell** :
```powershell
Start-Process -FilePath "C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe" `
    -ArgumentList "-i", "`"C:\Users\jmdig\github\BlueNotebook\windows_installer\BlueNotebook_V4.2.7.ifp`"" `
    -NoNewWindow `
    -Wait
```

**Paramètres expliqués** :

- **Start-Process** : Commande PowerShell pour exécuter un processus
- **-FilePath** : Chemin vers l'exécutable InstallForge
- **-ArgumentList** :
  - `-i` : Indicateur pour spécifier le fichier projet
  - Chemin vers le fichier `.ifp` (InstallForge Project)
- **-NoNewWindow** : Exécute le processus dans la fenêtre PowerShell actuelle
- **-Wait** : Attend que le processus se termine avant de continuer

**Fichier projet** : `BlueNotebook_V4.2.7.ifp`
- Extension `.ifp` : InstallForge Project
- Contient toutes les configurations : fichiers à inclure, raccourcis, registre, etc.
- Localisé dans : `C:\Users\jmdig\github\BlueNotebook\windows_installer\`

## Structure des répertoires

```
BlueNotebook/
├── bluenotebook/
│   ├── main.spec              # Configuration PyInstaller
│   └── dist/
│       └── BlueNotebook/
│           └── BlueNotebook.exe  # Exécutable compilé
└── windows_installer/
    └── BlueNotebook_V4.2.7.ifp   # Projet InstallForge
```

## Workflow complet automatisé

Pour automatiser l'ensemble du processus, vous pouvez créer un script PowerShell :

```powershell
# Script : build_installer.ps1

# 1. Installation des dépendances (si nécessaire)
pip install pyinstaller pyinstaller-hooks-contrib

# 2. Compilation avec PyInstaller
Write-Host "Compilation de l'application..." -ForegroundColor Green
pyinstaller main.spec --clean --noconfirm

# 3. Vérification (optionnelle)
Write-Host "Vérification de l'exécutable..." -ForegroundColor Green
$testProcess = Start-Process -FilePath ".\BlueNotebook\BlueNotebook.exe" -PassThru
Start-Sleep -Seconds 3
Stop-Process -Id $testProcess.Id -Force

# 4. Création de l'installateur
Write-Host "Création de l'installateur Windows..." -ForegroundColor Green
Start-Process -FilePath "C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe" `
    -ArgumentList "-i", "`"C:\Users\jmdig\github\BlueNotebook\windows_installer\BlueNotebook_V4.2.7.ifp`"" `
    -NoNewWindow `
    -Wait

Write-Host "Build terminé avec succès!" -ForegroundColor Green
```

## Bonnes pratiques

1. **Versioning** : Mettez à jour le numéro de version dans le nom du fichier `.ifp` à chaque release
2. **Tests** : Testez toujours l'exécutable avant de créer l'installateur
3. **Clean builds** : Utilisez toujours `--clean` pour éviter les problèmes de cache
4. **Sauvegarde** : Conservez les fichiers `.spec` et `.ifp` sous contrôle de version (Git)
5. **Documentation** : Notez les dépendances système particulières dans le README

## Dépannage courant

| Problème | Solution |
|----------|----------|
| Modules manquants dans l'exe | Ajoutez les hooks dans le fichier `.spec` |
| Exe trop volumineux | Utilisez `--exclude-module` pour les modules inutiles |
| Erreur InstallForge | Vérifiez les chemins dans le fichier `.ifp` |
| Antivirus bloque l'exe | Signez numériquement votre exécutable |

## Ressources supplémentaires

- [Documentation PyInstaller](https://pyinstaller.org/)
- [Documentation InstallForge](https://installforge.net/)
- Fichier `main.spec` pour configurations avancées
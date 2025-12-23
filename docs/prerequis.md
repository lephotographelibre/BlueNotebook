# Prérequis d'Installation pour BlueNotebook

Ce document liste toutes les dépendances système (pour Ubuntu/Debian) et les paquets Python nécessaires pour faire fonctionner l'application BlueNotebook et toutes ses fonctionnalités.

## 1. Prérequis Système (Ubuntu/Debian)

### pyenv install 

Install pyenv using <https://github.com/pyenv/pyenv-installer>

```bash
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```

add these lines to .bash_profile

```bash
# User specific environment and startup programs
#
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
```

add tothis line to .bashrc

```bash
eval "$(pyenv virtualenv-init -)"
```
 

Ces paquets fournissent les bibliothèques de base nécessaires à certaines fonctionnalités graphiques et d'export.

### Dépendances Essentielles

Ces paquets sont requis pour la génération des cartes (GPS, GPX) et l'export PDF/EPUB.

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv libcairo2-dev libpango-1.0-0 libgdk-pixbuf2.0-0
# When running into a VM/Container You may have to install sound packages for QWebEngineView
sudo apt-get install libasound2t64
# if emojis not installed
sudo apt install fonts-noto-color-emoji
```

*   `python3-pip` : Pour installer les paquets Python.
*   `python3-venv` : Pour créer des environnements virtuels isolés.
*   `libcairo2-dev` : Requis par `py-staticmaps` et `cairosvg` pour le dessin et la manipulation d'images.
*   `libpango-1.0-0` et `libgdk-pixbuf2.0-0` : Requis par `WeasyPrint` pour l'export PDF.

### Dépendances pour le Développement (Optionnel)

Si vous souhaitez contribuer au développement, notamment pour la traduction de l'interface, installez les outils Qt.

```bash
sudo apt-get install qttools5-dev pyqt5-dev-tools
```

*   `qttools5-dev` : Fournit l'application graphique **Qt Linguist**.
*   `pyqt5-dev-tools` : Fournit les outils en ligne de commande `pylupdate5` et `lrelease`.

## 2. Prérequis Python

Il est fortement recommandé d'installer ces paquets dans un environnement virtuel.

```bash
# 1. Créez un environnement virtuel
python3 -m venv .venv_3.11.13

# 2. Activez-le
source .venv_3.11.13/bin/activate

# 3. Installez tous les paquets requis
# Linux 
pip install -r requirements.txt
```

### Liste des Paquets Python (`requirements.txt`)

Voici la liste des dépendances Python utilisées par le projet :

*   **Coeur de l'application :**
    *   `PyQt5` : Le framework pour l'interface graphique.
    *   `PyQtWebEngine` : Pour le panneau d'aperçu HTML.
    *   `markdown`, `Pygments`, `pymdown-extensions` : Pour la conversion et la coloration du Markdown.
    *   `requests` : Pour les requêtes réseau (météo, citation, YouTube).
    *   `beautifulsoup4`, `lxml` : Pour l'analyse de contenu HTML.
    *   `appdirs` : Pour trouver les répertoires de configuration système.

*   **Fonctionnalités optionnelles (incluses dans `requirements.txt`) :**
    *   `gpxpy`, `py-staticmaps[cairo]`, `geopy` : Pour l'intégration des cartes GPS et GPX.
    *   `Pillow`, `EbookLib`, `cairosvg` : Pour l'export au format EPUB.
    *   `WeasyPrint` : Pour l'export au format PDF.


## 3. Prérequis Système (Windows)

### pyenv

++++ Powershell Admin system: Windows-X Terminal (Administrateur)
https://github.com/pyenv-win/pyenv-win

PS C:\Users\jmdig> Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/pyenv-win/pyenv-win/master/pyenv-win/install-pyenv-win.ps1" -OutFile "./install-pyenv-win.ps1"; &"./install-pyenv-win.ps1"
Reopen PowerShell
PS C:\Users\jmdig> pyenv --version
pyenv 3.1.1

Add the following to you PATH variable
Instructions for those who are unsure about how to add PATH, search in Windows for Advanced system settings 
"search System".--> "Afficher les paramètres sytème avancés" 
Click Environment Variables. In the section System Variables, add a new PATH environment variable 
"Variables d'environnement". --> PATH Modifier

C:\Users\jmdig\.pyenv\pyenv-win\bin
C:\Users\jmdig\.pyenv\pyenv-win\shims

C:\Users\jmdig>pyenv local 3.11.9

C:\Users\jmdig>python -V
Python 3.11.9

Sur Windows, la gestion des environnements virtuels n'est pas une fonctionnalité de base de pyenv-win. 
Elle est fournie par un plugin séparé qui s'appelle pyenv-virtualenv. L

C:\Users\jmdig>git clone https://github.com/pyenv/pyenv-virtualenv.git "$(pyenv root)\plugins\pyenv-virtualenv"


### Cairo

comment installer libcairo-2.dll sur windows11

https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

Add PATH --> C:\Program Files\GTK3-Runtime Win64\bin

where libcairo-2.dll
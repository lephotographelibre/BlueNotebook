# Prérequis d'Installation pour BlueNotebook

Ce document liste toutes les dépendances système (pour Ubuntu/Debian) et les paquets Python nécessaires pour faire fonctionner l'application BlueNotebook et toutes ses fonctionnalités.

## 1. Prérequis Système (Ubuntu/Debian)

Ces paquets fournissent les bibliothèques de base nécessaires à certaines fonctionnalités graphiques et d'export.

### Dépendances Essentielles

Ces paquets sont requis pour la génération des cartes (GPS, GPX) et l'export PDF/EPUB.

```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv libcairo2-dev libpango-1.0-0 libgdk-pixbuf2.0-0
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
python3 -m venv .venv_bluenotebook

# 2. Activez-le
source .venv_bluenotebook/bin/activate

# 3. Installez tous les paquets requis
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

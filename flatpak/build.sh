#!/bin/bash

# Prepare Runtime
flatpak install flathub com.riverbankcomputing.PyQt.BaseApp//5.15-23.08 org.kde.Sdk//5.15-23.08 org.kde.Platform//5.15-23.08

cd BlueNotebook/flatpak
#  
pyenv activate .venv_3.11.13
# Install requirements-parserfir Flapak builds
pip install requirements-parser

# Package order is mandatory
python3 flatpak-pip-generator.py \
    --runtime=org.kde.Sdk//5.15-23.08 \
    --yaml \
    --output=./python3-requirements \
    --ignore-installed=markdown,Pygments \
    meson-python \
    pycairo \
    hatchling \
    pybind11 \
    "cffi<2.0.0" \
    requests \
    markdown \
    beautifulsoup4 \
    WeasyPrint \
    gpxpy \
    py-staticmaps \
    geopy \
    EbookLib \
    "Pillow==9.5.0" \
    cairosvg \
    Pygments \
    pymdown-extensions \
    PyMuPDF \
    youtube-transcript-api \
    markitdown \
    validators \
    readability-lxml \
    markdownify \
    markitdown[pdf]

# 1. Construire et exporter dans un dépôt local nommé 'repo'
flatpak-builder --user --install --force-clean --repo=repo build-dir ./io.github.lephotographelibre.BlueNotebook.yaml

# 2. Créer le fichier bundle (.flatpak) distribuable
flatpak build-bundle repo BlueNotebook.flatpak io.github.lephotographelibre.BlueNotebook

# Verifier l'installation
$ flatpak list --user | grep BlueNotebook
BlueNotebook    io.github.lephotographelibre.BlueNotebook       4.0.9   master  bluenotebook-origin

# Lancement en ligne de commande (Recommandé pour voir les logs)C'est la méthode la plus efficace pour tester car vous verrez directement les messages de sortie et les erreurs potentielles dans votre terminal.
flatpak run io.github.lephotographelibre.BlueNotebook


#  Débogage : Entrer dans le conteneur Si l'application ne se lance pas ou crashe, vous pouvez ouvrir un terminal à l'intérieur de l'environnement Flatpak pour explorer les fichiers et tester manuellement :
flatpak run --command=sh io.github.lephotographelibre.BlueNotebook

$ flatpak run -v --command=sh io.github.lephotographelibre.BlueNotebook
sh: flatpak : commande introuvable
(.venv_bluenotebook) jm@jm-22:~/Work/BlueNotebook$ /app/bin/bluenotebook
🚀 Lancement de BlueNotebook...
📂 Journal: /home/jm/Documents/BlueNotebookJournal
python3: can't open file '/app/share/bluenotebook/main.py': [Errno 2] No such file or directory



# Nettoyer l'installation
flatpak uninstall --user io.github.lephotographelibre.BlueNotebook
flatpak list --user | grep BlueNotebook


# requirements.txt
 
# Core application framework
PyQt5==5.15.11
PyQtWebEngine==5.15.7

# Markdown and HTML processing
beautifulsoup4
markdown
markdownify
pymdown-extensions
Pygments
readability-lxml

# Document export and conversion
cairosvg
cffi<2.0.0
EbookLib
markitdown
Pillow==9.5.0
PyMuPDF
WeasyPrint

# Integrations and network
geopy
gpxpy
py-staticmaps
requests
validators
youtube-transcript-api
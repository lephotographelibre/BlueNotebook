# Image de base légère basée sur Debian (Python 3.11)
FROM python:3.11-slim

# Mise à jour et installation des dépendances système
RUN apt-get update && apt-get install -y \
    git \
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
    && apt-get install -y --no-install-recommends \
    build-essential \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    meson \
    ninja-build \
    && rm -rf /var/lib/apt/lists/*

# Clonage du dépôt GitHub
RUN git clone https://github.com/lephotographelibre/BlueNotebook.git /app

# Installation des dépendances Python via pip
WORKDIR /app
RUN pip install --no-cache-dir -r requirements.txt

# Nettoyage des outils de build temporaires pour réduire la taille de l'image
RUN apt-get purge -y --auto-remove \
    build-essential \
    libcairo2-dev \
    pkg-config \
    python3-dev \
    meson \
    ninja-build \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root pour plus de sécurité
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/bash -m appuser && \
    mkdir -p /data/journal /data/backup && \
    chown -R appuser:appgroup /data /app

# Passage à l'utilisateur non-root
USER appuser

# Répertoire de travail dans l'application
WORKDIR /app/bluenotebook

# Commande de lancement de l'application
CMD ["python", "main.py"]

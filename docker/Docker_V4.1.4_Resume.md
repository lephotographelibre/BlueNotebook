```bash
-- Dockerfile ----- build from git clone https://github.com/lephotographelibre/BlueNotebook.git

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


-- build docker image

$ cd Bluenotebook
$ docker build -f docker/Dockerfile -t bluenotebook:4.1.4 -t bluenotebook:latest .


$ docker images
REPOSITORY             TAG         IMAGE ID       CREATED        SIZE
jmdigne/bluenotebook   4.1.4       8b37af965f22   17 hours ago   2.26GB
bluenotebook           4.1.4       8b37af965f22   17 hours ago   2.26GB
bluenotebook           latest      8b37af965f22   17 hours ago   2.26GB


-- set env for docker image

# Création des répertoires nécessaires
mkdir -p ~/bluenotebook_docker/config \
         ~/bluenotebook_docker/BlueNotebookJournal \
         ~/bluenotebook_docker/BlueNotebookBackup
# Attribution de la propriété à votre utilisateur (récursif)
chown -R $(id -u):$(id -g) ~/bluenotebook_docker
# Attribution des permissions d'écriture (récursif)
chmod -R u+rwX ~/bluenotebook_docker

-- Run

docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/bluenotebook_docker:/data \
    -v ~/bluenotebook_docker/config:/home/appuser/.config \
    -v ~/bluenotebook_docker/BlueNotebookJournal:/home/appuser/BlueNotebookJournal \
    -v ~/bluenotebook_docker/BlueNotebookBackup:/home/appuser/BlueNotebookBackup \
    --user=$(id -u):$(id -g) \
    bluenotebook:4.1.4

-- save docker image in a file

$ docker save bluenotebook:latest | gzip > V4.1.4_bluenotebook_docker_image.tar.gz


-- dockerhub https://app.docker.com/accounts/jmdigne ---

docker login
docker tag bluenotebook:4.1.4 jmdigne/bluenotebook:4.1.4
docker push jmdigne/bluenotebook:4.1.4
The push refers to repository [docker.io/jmdigne/bluenotebook]
fe9b6420471d: Pushed
88441d54aa70: Pushed
fbe95e127e02: Pushed
7d0f56eed6b4: Pushed
9f0535ed5ca2: Pushed
fa384bf02ac1: Mounted from library/python
600af8de593b: Mounted from library/python
424dc4972605: Mounted from library/python
77a2b55fbe8b: Mounted from library/python
4.1.3: digest: sha256:a2f12d0a593cefe6ecb3c7cb452e858c95e82feec254ec6f12f5a02f8c3c4e1a size: 2219

See it at https://hub.docker.com/repository/docker/jmdigne/bluenotebook/general
Use it using

docker pull jmdigne/bluenotebook:4.1.4

-- docker command cleanup all vm/containers

docker stop $(docker ps -q)          # Arrête les conteneurs en cours
docker rm $(docker ps -a -q)         # Supprime tous les conteneurs (arrêtés inclus)
docker rmi -f $(docker images -q)


```
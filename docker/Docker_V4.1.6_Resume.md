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
$ docker build -f docker/Dockerfile -t bluenotebook:4.1.6 -t bluenotebook:latest .


$ docker images
REPOSITORY             TAG         IMAGE ID       CREATED        SIZE
bluenotebook           4.1.6       5ee108775ea3   19 seconds ago   2.36GB
bluenotebook           latest      5ee108775ea3   19 seconds ago   2.36GB
python                 3.11-slim   955f4ccb5624   7 days ago       124MB
jmdigne/bluenotebook   4.1.4       8b37af965f22   7 days ago       2.26GB



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
    bluenotebook:latest

-- save docker image in a file

$ docker save bluenotebook:latest | gzip > docker/BlueNotebook-4.1.6-docker.tar.gz

 


-- dockerhub https://app.docker.com/accounts/jmdigne ---

docker login
docker build -t bluenotebook:4.1.6 -t bluenotebook:latest .

# 2. Tagger pour Docker Hub avec la version spécifique
docker tag bluenotebook:4.1.6 jmdigne/bluenotebook:4.1.6

# 3. Tagger pour Docker Hub avec latest
docker tag bluenotebook:4.1.6 jmdigne/bluenotebook:latest

# 4. Push des deux tags
docker push jmdigne/bluenotebook:4.1.6
docker push jmdigne/bluenotebook:latest

See it at https://hub.docker.com/repository/docker/jmdigne/bluenotebook/general
Use it using

docker pull jmdigne/bluenotebook:latest
or 
docker pull jmdigne/bluenotebook:4.1.6

-- docker command cleanup all vm/containers

docker stop $(docker ps -q)          # Arrête les conteneurs en cours
docker rm $(docker ps -a -q)         # Supprime tous les conteneurs (arrêtés inclus)
docker rmi -f $(docker images -q)


---------------

Voici un exemple complet avec deux versions consécutives (4.1.6 et 4.1.7) :

## Version 4.1.6 (première version)

```bash
# 1. Construire l'image avec les deux tags
docker build -t bluenotebook:4.1.6 -t bluenotebook:latest .

# 2. Tagger pour Docker Hub avec la version spécifique
docker tag bluenotebook:4.1.6 jmdigne/bluenotebook:4.1.6

# 3. Tagger pour Docker Hub avec latest
docker tag bluenotebook:4.1.6 jmdigne/bluenotebook:latest

# 4. Push des deux tags
docker push jmdigne/bluenotebook:4.1.6
docker push jmdigne/bluenotebook:latest
```

## Version 4.1.7 (version suivante)

```bash
# 1. Construire la nouvelle image avec les deux tags
docker build -t bluenotebook:4.1.7 -t bluenotebook:latest .

# 2. Tagger pour Docker Hub avec la version spécifique
docker tag bluenotebook:4.1.7 jmdigne/bluenotebook:4.1.7

# 3. Tagger pour Docker Hub avec latest (écrase l'ancien latest)
docker tag bluenotebook:4.1.7 jmdigne/bluenotebook:latest

# 4. Push des deux tags
docker push jmdigne/bluenotebook:4.1.7
docker push jmdigne/bluenotebook:latest  # Écrase le latest précédent sur Docker Hub
```

## Pull de l'image

```bash
# Pull de la dernière version (toujours la plus récente)
docker pull jmdigne/bluenotebook:latest

# Pull d'une version spécifique
docker pull jmdigne/bluenotebook:4.1.6
docker pull jmdigne/bluenotebook:4.1.7
```
## Run générique


```bash

docker run -it --rm \
    -e DISPLAY=$DISPLAY \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v ~/bluenotebook_docker:/data \
    -v ~/bluenotebook_docker/config:/home/appuser/.config \
    -v ~/bluenotebook_docker/BlueNotebookJournal:/home/appuser/BlueNotebookJournal \
    -v ~/bluenotebook_docker/BlueNotebookBackup:/home/appuser/BlueNotebookBackup \
    --user=$(id -u):$(id -g) \
    jmdigne/bluenotebook:latest
```


## Points clés

- Le tag `latest` pointe toujours vers la dernière image poussée
- Les versions spécifiques (4.1.6, 4.1.7) restent accessibles et ne changent jamais
- Quand vous poussez un nouveau `latest`, il écrase l'ancien sur Docker Hub
- `docker pull` sans tag utilise automatiquement `:latest`

 
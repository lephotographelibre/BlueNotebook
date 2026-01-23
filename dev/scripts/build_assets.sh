#!/bin/bash
# Packaging script to build assets for a release, with the version passed as a parameter.
# The assets will be available in the format: BlueNotebook-VERSION-xxx.yyy

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1

# cd Bluenotebook
cd ../..

source ~/.bash_profile
source ~/.bashrc
pyenv activate .venv_3.11.13
pip install requirements-parser PyYAML


echo "--- Starting Docker Image Build ---"
## Build Docker
#docker build -f docker/Dockerfile -t "bluenotebook:$VERSION" -t bluenotebook:latest .
# Récupère le hash du dernier commit de la branche main
LATEST_COMMIT=$(git ls-remote https://github.com/lephotographelibre/BlueNotebook.git HEAD | cut -f1)
# Lance le build avec le hash du commit
docker build --build-arg GIT_COMMIT=$LATEST_COMMIT -f docker/Dockerfile  -t "bluenotebook:$VERSION" -t bluenotebook:latest .

# dockerhub
echo "--- Docker tag ---"
# 2. Tag for Docker Hub with the specific version
docker tag "bluenotebook:$VERSION" "jmdigne/bluenotebook:$VERSION"
# 3. Tag for Docker Hub with the latest tag
docker tag "bluenotebook:$VERSION" jmdigne/bluenotebook:latest

echo "--- Docker tag push to dockerhub ---"
# 4. Push both tags
docker push "jmdigne/bluenotebook:$VERSION"
docker push jmdigne/bluenotebook:latest


echo "--- Docker tag push to github package ---"
if [ -z "$GITHUB_TOKEN" ]; then
    echo "⚠️  GITHUB_TOKEN non défini"
    exit 1
fi
echo $GITHUB_TOKEN | docker login ghcr.io -u lephotographelibre --password-stdin
docker tag "bluenotebook:$VERSION" "ghcr.io/lephotographelibre/bluenotebook:$VERSION"
docker push "ghcr.io/lephotographelibre/bluenotebook:$VERSION"


echo "--- Docker list images ---"
#5. List images
docker images

# Create a tar.gz archive of the Docker image
echo "Creating Docker image tar.gz archive as asset..."
docker save "bluenotebook:$VERSION" | gzip > "assets/BlueNotebook-$VERSION-docker.tar.gz"
ls -al assets
echo "...done"
echo "--- Docker Image Build Complete ---"

echo "--- Starting Flatpak Build ---"
## Build flatpak
cd flatpak
echo "--- Flatpak Clean previous installation ---"

# 0. Clean previous installation & install builder
flatpak list --user | grep BlueNotebook
flatpak uninstall --user io.github.lephotographelibre.BlueNotebook
flatpak list --user | grep BlueNotebook

#0. Install the builder
flatpak install flathub org.flatpak.Builder

echo "--- Flatpak python3-requirements ---"
# 1. Generate python3-requirements.yaml
python3 flatpak-pip-generator.py \
    --runtime=org.kde.Sdk//5.15-25.08 \
    --yaml \
    --output=./python3-requirements \
    --ignore-installed=markdown,Pygments \
    validators \
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
    Pillow \
    cairosvg \
    Pygments \
    pymdown-extensions \
    PyMuPDF \
    youtube-transcript-api \
    markitdown \
    readability-lxml \
    markdownify \
    pymupdf4llm
 
 

echo "--- Flatpak Build ---"
# 2. Build flatpak
# add  --install-deps-from=flathub 
flatpak run org.flatpak.Builder --user --install --force-clean --repo=repo build-dir ./io.github.lephotographelibre.BlueNotebook.yaml

echo "--- Flatpak List app ---"
# 3. List App
flatpak list --user | grep BlueNotebook
# 4. Create the distributable bundle (.flatpak) file
flatpak build-bundle repo "../assets/BlueNotebook-$VERSION.flatpak" io.github.lephotographelibre.BlueNotebook

echo "--- Flatpak Linter  ---"
# 5. run the linter (manifest/repo)
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest io.github.lephotographelibre.BlueNotebook.yaml
flatpak run --command=flatpak-builder-lint org.flatpak.Builder repo repo
echo "--- Flatpak Build Complete ---"


cd ..
cd appimage
echo "--- Starting AppImage Build ---"
./build_all_appimage.sh $VERSION
ls -al
mv -v BlueNotebook-$VERSION-x86_64.AppImage ../assets/BlueNotebook-$VERSION-x86_64.AppImage
mv -v *.desktop ../assets/
mv -v install_BlueNotebook-$VERSION.sh ../assets/install_BlueNotebook-$VERSION-AppImage.sh
mv -v uninstall_BlueNotebook-$VERSION.sh ../assets/uninstall_BlueNotebook-$VERSION-AppImage.sh
./cleanup.sh
rm ./cleanup.sh


echo "--- AppImage Build Complete ---"


echo "--- All asset builds finished ---"

echo "--- Assets List ---"
cd ..
ls -al assets
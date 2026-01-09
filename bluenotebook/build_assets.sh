#!/bin/bash
# Packaging script to build assets for a release, with the version passed as a parameter.
# The assets will be available in the format: BlueNotebook-VERSION-xxx.yyy

if [ -z "$1" ]; then
  echo "Usage: $0 <version>"
  exit 1
fi

VERSION=$1

# cd Bluenotebook
cd ..


pyenv activate .venv_3.11.13
pip install requirements-parser


echo "--- Starting Docker Image Build ---"
## Build Docker
docker build -f docker/Dockerfile -t "bluenotebook:$VERSION" -t bluenotebook:latest .
# dockerhub
# 2. Tag for Docker Hub with the specific version
docker tag "bluenotebook:$VERSION" "jmdigne/bluenotebook:$VERSION"
# 3. Tag for Docker Hub with the latest tag
docker tag "bluenotebook:$VERSION" jmdigne/bluenotebook:latest
# 4. Push both tags
docker push "jmdigne/bluenotebook:$VERSION"
docker push jmdigne/bluenotebook:latest
#5. List images
docker images

# Create a tar.gz archive of the Docker image
echo "Creating Docker image tar.gz archive..."
docker save "bluenotebook:$VERSION" | gzip > "assets/BlueNotebook-$VERSION-docker.tar.gz"
echo "...done"
echo "--- Docker Image Build Complete ---"

echo "--- Starting Flatpak Build ---"
## Build flatpak
cd flatpak
# 0. Clean previous installation
flatpak uninstall --user io.github.lephotographelibre.BlueNotebook
flatpak list --user | grep BlueNotebook
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
 
 


# 2. Build flatpak
flatpak run org.flatpak.Builder --user --install --force-clean --repo=repo build-dir ./io.github.lephotographelibre.BlueNotebook.yaml
# 3. List App
flatpak list --user | grep BlueNotebook
# 4. Create the distributable bundle (.flatpak) file
flatpak build-bundle repo "../assets/BlueNotebook-$VERSION.flatpak" io.github.lephotographelibre.BlueNotebook

# 5. run the linter (manifest/repo)
flatpak run --command=flatpak-builder-lint org.flatpak.Builder manifest io.github.lephotographelibre.BlueNotebook.yaml
flatpak run --command=flatpak-builder-lint org.flatpak.Builder repo repo
echo "--- Flatpak Build Complete ---"

echo "--- Starting AppImage Build ---"
## build Appimage
echo "--- AppImage Build Complete ---"
echo "--- All asset builds finished ---"

echo "--- Assets List ---"
ls al assets
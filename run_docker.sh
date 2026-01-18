#!/bin/bash

# Smart launch script for BlueNotebook via Docker
# Usage: ./start_docker.sh [data_directory]
# If no parameter is provided, defaults to ~/bluenotebook_docker.

IMAGE_REPO="jmdigne/bluenotebook"
DEFAULT_DIR="$HOME/bluenotebook_docker"

# Directory parameter management
if [ -n "$1" ]; then
    DATA_DIR="$1"
else
    DATA_DIR="$DEFAULT_DIR"
fi

echo "=========================================="
echo "🚀 BlueNotebook Docker Launcher"
echo "=========================================="

# --- Dependency check ---
if ! command -v curl &> /dev/null || ! command -v jq &> /dev/null; then
    echo "❌ Error: 'curl' and 'jq' are required to fetch the latest image version."
    echo "   Please install them to continue (e.g., sudo apt install curl jq)."
    exit 1
fi

# --- Fetching the latest image version ---
echo "🔎 Searching for the latest image version on Docker Hub..."
# Querying the Docker Hub API to find the most recent tag.
LATEST_TAG=$(curl -s "https://hub.docker.com/v2/repositories/${IMAGE_REPO}/tags/?page_size=1" | jq -r '.results[0].name')

if [ -z "$LATEST_TAG" ] || [ "$LATEST_TAG" == "null" ]; then
    echo "❌ Could not fetch the latest version. Check your connection or the repository name."
    exit 1
fi

IMAGE_NAME="${IMAGE_REPO}:${LATEST_TAG}"

echo "📂 Data directory : $DATA_DIR"
echo "📦 Docker Image   : $IMAGE_NAME"
echo ""

# 1. Pull image (if necessary)
echo "[1/3] Checking Docker image..."
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "   ⬇️  Image not found locally. Pulling from hub..."
    docker pull $IMAGE_NAME
else
    echo "   ✅ Image already present locally. Skipping pull."
fi

# 2. Create directories (if necessary)
echo "[2/3] Checking environment..."
DIRS_TO_CHECK=("config" "BlueNotebookJournal" "BlueNotebookBackup")
CREATED_ANY=false

# Create root directory if it doesn't exist
if [ ! -d "$DATA_DIR" ]; then
    echo "   📁 Creating root directory: $DATA_DIR"
    mkdir -p "$DATA_DIR"
    CREATED_ANY=true
fi

# Création des sous-dossiers s'ils n'existent pas
for subdir in "${DIRS_TO_CHECK[@]}"; do
    FULL_PATH="$DATA_DIR/$subdir"
    if [ ! -d "$FULL_PATH" ]; then
        echo "   📁 Creating subdirectory: $subdir"
        mkdir -p "$FULL_PATH"
        CREATED_ANY=true
    fi
done

if [ "$CREATED_ANY" = true ]; then
    echo "   🔒 Applying permissions..."
    chown -R $(id -u):$(id -g) "$DATA_DIR"
    chmod -R u+rwX "$DATA_DIR"
else
    echo "   ✅ Directories already exist. Skipping creation."
fi

# 3. Launch container
echo "[3/3] Launching BlueNotebook..."

# Temporarily allow the local user to connect to the X server for the container.
# This rule is automatically revoked when the script exits.
xhost +si:localuser:$(id -un)
trap 'xhost -si:localuser:$(id -un); echo "👋 Session ended."' EXIT

docker run -it --rm -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix -v "$DATA_DIR":/data -v "$DATA_DIR/config":/home/appuser/.config -v "$DATA_DIR/BlueNotebookJournal":/home/appuser/BlueNotebookJournal -v "$DATA_DIR/BlueNotebookBackup":/home/appuser/BlueNotebookBackup --user=$(id -u):$(id -g) $IMAGE_NAME

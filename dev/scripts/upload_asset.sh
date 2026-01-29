#!/bin/bash
# Script to upload assets to GitHub Releases
# Usage: ./upload_asset.sh <version>
# Example: ./upload_asset.sh 4.2.5

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if version parameter is provided
if [ -z "$1" ]; then
  echo -e "${RED}Error: Version parameter is required${NC}"
  echo "Usage: $0 <version>"
  echo "Example: $0 4.2.5"
  exit 1
fi

VERSION=$1
TAG_VERSION="v$VERSION"

# Check if GITHUB_TOKEN is set
if [ -z "$GITHUB_TOKEN" ]; then
  echo -e "${RED}Error: GITHUB_TOKEN environment variable is not set${NC}"
  echo "Please ensure GITHUB_TOKEN is exported in your ~/.bash_profile"
  exit 1
fi

# Get repository information from git remote
REPO_URL=$(git remote get-url origin)
# Extract owner and repo name from URL
# Handles both HTTPS and SSH URLs
if [[ $REPO_URL == *"github.com"* ]]; then
  OWNER_REPO=$(echo "$REPO_URL" | sed -e 's/.*github.com[:/]\(.*\)\.git$/\1/' -e 's/.*github.com[:/]\(.*\)$/\1/')
  OWNER=$(echo "$OWNER_REPO" | cut -d'/' -f1)
  REPO=$(echo "$OWNER_REPO" | cut -d'/' -f2)
else
  echo -e "${RED}Error: Not a GitHub repository${NC}"
  exit 1
fi

echo -e "${GREEN}Repository: $OWNER/$REPO${NC}"
echo -e "${GREEN}Version: $VERSION (tag: $TAG_VERSION)${NC}"

# API endpoint
API_URL="https://api.github.com"
UPLOAD_URL="https://uploads.github.com"

# Get release ID for the specified version
echo -e "${YELLOW}Fetching release information for $TAG_VERSION...${NC}"
RELEASE_INFO=$(curl -s \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Accept: application/vnd.github.v3+json" \
  "$API_URL/repos/$OWNER/$REPO/releases/tags/$TAG_VERSION")

# Check if release exists
if echo "$RELEASE_INFO" | grep -q '"message": "Not Found"'; then
  echo -e "${RED}Error: Release $TAG_VERSION not found${NC}"
  echo "Please create the release first on GitHub"
  exit 1
fi

# Extract release ID
RELEASE_ID=$(echo "$RELEASE_INFO" | grep -m 1 '"id":' | grep -o '[0-9]\+' | head -1)

if [ -z "$RELEASE_ID" ]; then
  echo -e "${RED}Error: Could not extract release ID${NC}"
  exit 1
fi

echo -e "${GREEN}Found release ID: $RELEASE_ID${NC}"

# Change to repository root
cd "$(git rev-parse --show-toplevel)"

# Check if assets directory exists
if [ ! -d "assets" ]; then
  echo -e "${RED}Error: assets directory not found${NC}"
  exit 1
fi

# Count total assets to upload
TOTAL_FILES=$(find assets -type f ! -name "release_asset_template.md" | wc -l)

if [ "$TOTAL_FILES" -eq 0 ]; then
  echo -e "${YELLOW}Warning: No assets found to upload${NC}"
  exit 0
fi

echo -e "${GREEN}Found $TOTAL_FILES asset(s) to upload${NC}"
echo ""

# Upload each asset
UPLOADED=0
FAILED=0

for ASSET_PATH in assets/*; do
  # Skip if not a file or if it's the template
  if [ ! -f "$ASSET_PATH" ] || [[ "$ASSET_PATH" == *"release_asset_template.md" ]]; then
    continue
  fi

  FILENAME=$(basename "$ASSET_PATH")
  echo -e "${YELLOW}Uploading: $FILENAME${NC}"

  # Check if asset already exists
  EXISTING_ASSET=$(echo "$RELEASE_INFO" | grep -o "\"name\": \"$FILENAME\"" || true)

  if [ ! -z "$EXISTING_ASSET" ]; then
    echo -e "${YELLOW}  Asset already exists, deleting old version...${NC}"
    # Get asset ID
    ASSET_ID=$(curl -s \
      -H "Authorization: token $GITHUB_TOKEN" \
      -H "Accept: application/vnd.github.v3+json" \
      "$API_URL/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets" | \
      grep -B 3 "\"name\": \"$FILENAME\"" | grep '"id":' | grep -o '[0-9]\+' | head -1)

    if [ ! -z "$ASSET_ID" ]; then
      curl -s -X DELETE \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.v3+json" \
        "$API_URL/repos/$OWNER/$REPO/releases/assets/$ASSET_ID"
      echo -e "${GREEN}  Old version deleted${NC}"
    fi
  fi

  # Determine content type based on file extension
  case "$FILENAME" in
    *.tar.gz)
      CONTENT_TYPE="application/gzip"
      ;;
    *.flatpak)
      CONTENT_TYPE="application/octet-stream"
      ;;
    *.AppImage)
      CONTENT_TYPE="application/x-executable"
      ;;
    *.zsync)
      CONTENT_TYPE="application/x-zsync"
      ;;
    *.sh)
      CONTENT_TYPE="application/x-sh"
      ;;
    *.desktop)
      CONTENT_TYPE="application/x-desktop"
      ;;
    *)
      CONTENT_TYPE="application/octet-stream"
      ;;
  esac

  # Upload the asset
  UPLOAD_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -H "Authorization: token $GITHUB_TOKEN" \
    -H "Content-Type: $CONTENT_TYPE" \
    -H "Accept: application/vnd.github.v3+json" \
    --data-binary @"$ASSET_PATH" \
    "$UPLOAD_URL/repos/$OWNER/$REPO/releases/$RELEASE_ID/assets?name=$FILENAME")

  # Extract HTTP status code (last line)
  HTTP_CODE=$(echo "$UPLOAD_RESPONSE" | tail -n 1)

  # Check if upload was successful (201 Created)
  if [ "$HTTP_CODE" -eq 201 ]; then
    echo -e "${GREEN}  ✓ Successfully uploaded${NC}"
    UPLOADED=$((UPLOADED + 1))
  else
    echo -e "${RED}  ✗ Upload failed (HTTP $HTTP_CODE)${NC}"
    FAILED=$((FAILED + 1))
    # Show error details
    ERROR_MSG=$(echo "$UPLOAD_RESPONSE" | head -n -1 | grep -o '"message": "[^"]*"' || echo "No error message")
    echo -e "${RED}  Error: $ERROR_MSG${NC}"
  fi

  echo ""
done

# Summary
echo "═══════════════════════════════════════"
echo -e "${GREEN}Upload Summary:${NC}"
echo -e "  Total assets: $TOTAL_FILES"
echo -e "  ${GREEN}Uploaded: $UPLOADED${NC}"
if [ "$FAILED" -gt 0 ]; then
  echo -e "  ${RED}Failed: $FAILED${NC}"
fi
echo "═══════════════════════════════════════"

if [ "$FAILED" -gt 0 ]; then
  exit 1
fi

echo -e "${GREEN}All assets uploaded successfully!${NC}"
echo -e "View release: https://github.com/$OWNER/$REPO/releases/tag/$TAG_VERSION"

#!/bin/bash
# Script to update version numbers in BlueNotebook files
# Usage: ./update_version.sh <old_version> <new_version>
# Example: ./update_version.sh 4.2.3 4.2.4

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if both version parameters are provided
if [ -z "$1" ] || [ -z "$2" ]; then
    echo -e "${RED}Error: Two version numbers required${NC}"
    echo "Usage: $0 <old_version> <new_version>"
    echo "Example: $0 4.2.3 4.2.4"
    exit 1
fi

OLD_VERSION=$1
NEW_VERSION=$2

# Validate version format (X.Y.Z) for both versions
if ! [[ $OLD_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid old version format. Expected X.Y.Z (e.g., 4.2.3)${NC}"
    exit 1
fi

if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo -e "${RED}Error: Invalid new version format. Expected X.Y.Z (e.g., 4.2.4)${NC}"
    exit 1
fi

# Check if versions are different
if [ "$OLD_VERSION" == "$NEW_VERSION" ]; then
    echo -e "${RED}Error: Old and new versions are identical${NC}"
    exit 1
fi

# Get the script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}BlueNotebook Version Update Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Old version: ${RED}$OLD_VERSION${NC}"
echo -e "New version: ${GREEN}$NEW_VERSION${NC}"
echo -e "Project root: $PROJECT_ROOT"
echo ""

# Files to update
HTML_DIR="$PROJECT_ROOT/bluenotebook/resources/html"
MAIN_PY="$PROJECT_ROOT/bluenotebook/main.py"
FLATPAK_YAML="$PROJECT_ROOT/flatpak/io.github.lephotographelibre.BlueNotebook.yaml"
FLATPAK_METAINFO="$PROJECT_ROOT/flatpak/io.github.lephotographelibre.BlueNotebook.metainfo.xml"

# Counter for changes
changes_made=0
files_modified=0
total_occurrences=0

# Function to process a single file
process_file() {
    local file=$1
    local relative_file="${file#$PROJECT_ROOT/}"

    if [ ! -f "$file" ]; then
        echo -e "${YELLOW}Warning: File not found: $relative_file${NC}"
        return
    fi

    echo -e "\n${BLUE}─────────────────────────────────────────${NC}"
    echo -e "${BLUE}Processing: ${NC}$relative_file"
    echo -e "${BLUE}─────────────────────────────────────────${NC}"

    # Find all occurrences of the old version
    local matches=$(grep -n -F "$OLD_VERSION" "$file" 2>/dev/null || true)

    if [ -z "$matches" ]; then
        echo -e "${YELLOW}No occurrence of $OLD_VERSION found in this file.${NC}"
        return
    fi

    local file_changed=0

    # Process each line with a version match
    while IFS= read -r match; do
        local line_num=$(echo "$match" | cut -d: -f1)
        local line_content=$(echo "$match" | cut -d: -f2-)

        ((total_occurrences++)) || true

        echo ""
        echo -e "${YELLOW}Found at line $line_num:${NC}"
        echo -e "  $line_content"
        echo ""
        echo -e "  Replace ${RED}$OLD_VERSION${NC} with ${GREEN}$NEW_VERSION${NC}?"
        echo -n "  [y/N/q(quit)]: "
        read -r response < /dev/tty

        case "$response" in
            [yY]|[yY][eE][sS])
                # Create the new line content
                local new_line_content="${line_content//$OLD_VERSION/$NEW_VERSION}"

                # Use sed to replace the specific line
                # Escape special characters for sed
                local escaped_new=$(printf '%s\n' "$new_line_content" | sed 's/[&/\]/\\&/g')

                sed -i "${line_num}s/.*/${escaped_new}/" "$file"

                echo -e "  ${GREEN}✓ Replaced${NC}"
                ((changes_made++)) || true
                file_changed=1
                ;;
            [qQ]|[qQ][uU][iI][tT])
                echo -e "\n${YELLOW}Script aborted by user.${NC}"
                echo -e "Changes made before abort: $changes_made"
                exit 0
                ;;
            *)
                echo -e "  ${YELLOW}Skipped${NC}"
                ;;
        esac
    done <<< "$matches"

    if [ $file_changed -eq 1 ]; then
        ((files_modified++)) || true
    fi
}

# Process HTML/MD files in resources/html
if [ -d "$HTML_DIR" ]; then
    echo -e "\n${GREEN}Processing files in resources/html...${NC}"
    for file in "$HTML_DIR"/*.html "$HTML_DIR"/*.md; do
        if [ -f "$file" ]; then
            process_file "$file"
        fi
    done
else
    echo -e "${YELLOW}Warning: HTML directory not found: $HTML_DIR${NC}"
fi

# Process main.py
echo -e "\n${GREEN}Processing main.py...${NC}"
process_file "$MAIN_PY"

# Process flatpak files
echo -e "\n${GREEN}Processing flatpak files...${NC}"
process_file "$FLATPAK_YAML"
process_file "$FLATPAK_METAINFO"

# Summary
echo -e "\n${BLUE}========================================${NC}"
echo -e "${BLUE}Summary${NC}"
echo -e "${BLUE}========================================${NC}"

if [ $total_occurrences -eq 0 ]; then
    echo -e "${RED}No occurrence of version $OLD_VERSION found in any file.${NC}"
    echo -e "Please check that the old version number is correct."
    exit 1
fi

echo -e "Total occurrences found: ${YELLOW}$total_occurrences${NC}"
echo -e "Total replacements made: ${GREEN}$changes_made${NC}"
echo -e "Files modified: ${GREEN}$files_modified${NC}"

if [ $changes_made -gt 0 ]; then
    echo -e "\n${GREEN}Version update complete!${NC}"
    echo -e "Don't forget to commit your changes."
else
    echo -e "\n${YELLOW}No changes were made.${NC}"
fi

"""
# Copyright (C) 2025 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path


class FileHandler:
    SUPPORTED_EXTENSIONS = [".md", ".markdown", ".txt"]

    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, "r", encoding="latin-1") as f:
                return f.read()

    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS

    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + ".bak")

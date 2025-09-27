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

Panneau affichant un nuage de tags.
"""

import json
import math
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
from PyQt5.QtGui import QFont


class TagCloudPanel(QWidget):
    """
    Panneau affichant une représentation en "nuage" des tags indexés.
    La taille de chaque tag est proportionnelle à sa fréquence.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("☁️ Nuage de Tags")
        self.label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #495057;
            }
        """
        )
        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)  # Pour le futur cliquable
        self.text_browser.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def update_cloud(self, journal_directory: Path, excluded_tags: set = None):
        """Met à jour le nuage de tags à partir du fichier d'index."""
        if not journal_directory:
            self.text_browser.clear()
            return

        index_file = journal_directory / "index_tags.json"
        if not index_file.exists():
            self.text_browser.setHtml("<p><i>Index des tags non trouvé.</i></p>")
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                tags_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.text_browser.setHtml("<p><i>Erreur de lecture de l'index.</i></p>")
            return

        if not tags_data:
            self.text_browser.setHtml("<p><i>Aucun tag à afficher.</i></p>")
            return

        # Filtrer les tags exclus par l'utilisateur
        if excluded_tags:
            tags_data = {
                tag: data
                for tag, data in tags_data.items()
                if tag.lstrip("@") not in excluded_tags
            }

        # Trier les tags par ordre alphabétique
        sorted_tags = sorted(tags_data.items(), key=lambda item: item[0])

        # Déterminer les tailles de police
        occurrences = [data["occurrences"] for _, data in sorted_tags]
        min_occ, max_occ = min(occurrences), max(occurrences)

        base_font_size = self.font().pointSize() or 10
        font_sizes = [
            base_font_size,
            base_font_size + 2,
            base_font_size + 4,
            base_font_size + 7,
            base_font_size + 10,
        ]

        html_parts = []
        for tag, data in sorted_tags:
            occ = data["occurrences"]
            # Normaliser la taille de la police sur 5 niveaux
            level = 0
            if max_occ > min_occ:
                level = math.floor(4 * (occ - min_occ) / (max_occ - min_occ))
            font_size = font_sizes[level]
            # Le nom du tag sans '@@'
            tag_name = tag.lstrip("@")
            html_parts.append(
                f'<span style="font-size: {font_size}pt;">{tag_name}</span>'
            )

        self.text_browser.setHtml(" &nbsp; ".join(html_parts))

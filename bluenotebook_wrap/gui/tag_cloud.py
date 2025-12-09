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
import unicodedata
from pathlib import Path
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextBrowser
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont


class NonNavigatingTextBrowser(QTextBrowser):
    """
    Un QTextBrowser qui n'essaie pas de naviguer lorsqu'un lien est cliqué.
    Il émet simplement le signal anchorClicked.
    """

    def setSource(self, name):
        # Surcharger pour ne rien faire, empêchant le widget de se vider lors d'un clic.
        pass


class TagCloudPanel(QWidget):
    """
    Panneau affichant une représentation en "nuage" des tags indexés.
    La taille de chaque tag est proportionnelle à sa fréquence.
    """

    tag_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.text_browser.anchorClicked.connect(self.on_anchor_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel(self.tr("☁️ Nuage de Tags"))
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.text_browser = NonNavigatingTextBrowser()
        self.text_browser.setOpenExternalLinks(False)  # Pour le futur cliquable
        self.text_browser.setStyleSheet(self.tr("border: none; background: transparent;"))
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def _normalize_tag(self, tag_text: str) -> str:
        """Convertit un tag en minuscules et sans accents pour la comparaison."""
        # Convertit en minuscules et décompose les caractères accentués
        nfkd_form = unicodedata.normalize(self.tr("NFKD"), tag_text.lower())
        # Conserve uniquement les caractères non-combinants (supprime les accents)
        return self.tr("").join([c for c in nfkd_form if not unicodedata.combining(c)])

    def update_cloud(self, journal_directory: Path, excluded_tags: set = None):
        """Met à jour le nuage de tags à partir du fichier d'index."""
        if not journal_directory:
            self.text_browser.clear()
            return

        index_file = journal_directory / "index_tags.json"
        if not index_file.exists():
            self.text_browser.setHtml(self.tr("<p><i>Index des tags non trouvé.</i></p>"))
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                tags_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.text_browser.setHtml(self.tr("<p><i>Erreur de lecture de l'index.</i></p>"))
            return

        if not tags_data:
            self.text_browser.setHtml(self.tr("<p><i>Aucun tag à afficher.</i></p>"))
            return

        # Filtrer les tags exclus par l'utilisateur
        if excluded_tags:
            normalized_excluded_tags = {self._normalize_tag(t) for t in excluded_tags}
            tags_data = {
                tag: data
                for tag, data in tags_data.items()
                if self._normalize_tag(tag.lstrip(self.tr("@"))) not in normalized_excluded_tags
            }

        # Trier les tags par ordre alphabétique
        sorted_tags = sorted(tags_data.items(), key=lambda item: item[0])

        # Déterminer les tailles de police
        occurrences = [data[self.tr("occurrences")] for _, data in sorted_tags]
        min_occ, max_occ = min(occurrences), max(occurrences)

        base_font_size = self.font().pointSize() or 10
        font_sizes = [
            base_font_size,
            base_font_size + 2,
            base_font_size + 4,
            base_font_size + 7,
            base_font_size + 10,
        ]

        # Récupérer la couleur de texte par défaut du thème pour une lisibilité parfaite
        text_color = (
            self.text_browser.palette().color(self.text_browser.foregroundRole()).name()
        )

        html_parts = []
        for tag, data in sorted_tags:
            occ = data[self.tr("occurrences")]
            # Normaliser la taille de la police sur 5 niveaux
            level = 0
            if max_occ > min_occ:
                level = math.floor(4 * (occ - min_occ) / (max_occ - min_occ))
            font_size = font_sizes[level]
            # Le nom du tag sans '@@'
            tag_name = tag.lstrip(self.tr("@"))
            # Rendre le tag cliquable en utilisant une balise <a>
            link_style = self.tr("text-decoration:none; color:%1;").arg(text_color)
            html_parts.append(
                self.tr("<a href="%1" style="%2 font-size: %3pt;">%4</a>").arg(tag_name).arg(link_style).arg(font_size).arg(tag_name)
            )

        self.text_browser.setHtml(self.tr(" &nbsp; ").join(html_parts))

    def on_anchor_clicked(self, url):
        """Gère le clic sur un tag dans le nuage."""
        tag_name = url.toString()
        self.tag_clicked.emit(tag_name)

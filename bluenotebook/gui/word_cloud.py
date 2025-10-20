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
"""
Panneau affichant un nuage de mots.
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


class WordCloudPanel(QWidget):
    """
    Panneau affichant une représentation en "nuage" des mots indexés.
    La taille de chaque mot est proportionnelle à sa fréquence.
    """

    word_clicked = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.text_browser.anchorClicked.connect(self.on_anchor_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("📖 Nuage de Mots")
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

        self.text_browser = NonNavigatingTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        # V2.6.3 - Style complet pour supprimer les bordures, y compris sur la scrollbar
        self.text_browser.setStyleSheet(
            """
            QTextBrowser {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """
        )
        layout.addWidget(self.text_browser)

        self.setLayout(layout)

    def _normalize_word(self, word_text: str) -> str:
        """Convertit un mot en minuscules et sans accents pour la comparaison."""
        nfkd_form = unicodedata.normalize("NFKD", word_text.lower())
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def update_cloud(self, journal_directory: Path, excluded_words: set = None):
        """Met à jour le nuage de mots à partir du fichier d'index."""
        if not journal_directory:
            self.text_browser.clear()
            return

        index_file = journal_directory / "index_words.json"
        if not index_file.exists():
            self.text_browser.setHtml("<p><i>Index des mots non trouvé.</i></p>")
            return

        try:
            with open(index_file, "r", encoding="utf-8") as f:
                words_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            self.text_browser.setHtml("<p><i>Erreur de lecture de l'index.</i></p>")
            return

        if not words_data:
            self.text_browser.setHtml("<p><i>Aucun mot à afficher.</i></p>")
            return

        if excluded_words:
            normalized_excluded = {self._normalize_word(w) for w in excluded_words}
            words_data = {
                word: data
                for word, data in words_data.items()
                if self._normalize_word(word) not in normalized_excluded
            }

        # Trier par occurrence pour ne garder que les 40 plus pertinents
        sorted_by_occurrence = sorted(
            words_data.items(), key=lambda item: item[1]["occurrences"], reverse=True
        )
        top_words = sorted_by_occurrence[:40]

        if not top_words:
            self.text_browser.setHtml(
                "<p><i>Aucun mot à afficher après filtrage.</i></p>"
            )
            return

        # Retrier par ordre alphabétique pour l'affichage
        display_words = sorted(top_words, key=lambda item: item[0])

        occurrences = [data["occurrences"] for _, data in display_words]
        min_occ, max_occ = min(occurrences), max(occurrences)

        base_font_size = self.font().pointSize() or 10
        font_sizes = [
            base_font_size,
            base_font_size + 2,
            base_font_size + 4,
            base_font_size + 7,
            base_font_size + 10,
        ]

        # V2.6.3 - Forcer la couleur de la police pour une meilleure cohérence
        text_color = "#333333"
        html_parts = []
        for word, data in display_words:
            occ = data["occurrences"]
            level = 0
            if max_occ > min_occ:
                level = math.floor(4 * (occ - min_occ) / (max_occ - min_occ))
            font_size = font_sizes[level]
            link_style = f"text-decoration:none; color:{text_color};"
            html_parts.append(
                f'<a href="{word}" style="{link_style} font-size: {font_size}pt;">{word}</a>'
            )

        self.text_browser.setHtml(" &nbsp; ".join(html_parts))

    def on_anchor_clicked(self, url):
        """Gère le clic sur un mot dans le nuage."""
        word = url.toString()
        self.word_clicked.emit(word)

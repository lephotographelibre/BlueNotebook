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
Panneau de lecture de documents EPUB pour BlueNotebook.
Inspiré du code de bluenotebook/tests/epub_readerV6.py
"""

import os
import re
import base64
from ebooklib import epub
import ebooklib

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QListWidget,
    QLineEdit,
    QPushButton,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt5.QtCore import Qt, QUrl, QBuffer, QIODevice, QByteArray
from PyQt5.QtGui import QPixmap


class EpubSchemeHandler(QWebEngineUrlSchemeHandler):
    """Gestionnaire de schéma personnalisé pour charger les ressources EPUB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.book = None
        self.resources = {}

    def set_book(self, book):
        """Définir le livre EPUB et charger les ressources."""
        self.book = book
        self.resources = {}

        if self.book:
            for item in self.book.get_items():
                if item.get_type() in [
                    ebooklib.ITEM_IMAGE,
                    ebooklib.ITEM_STYLE,
                    ebooklib.ITEM_SCRIPT,
                    ebooklib.ITEM_FONT,
                ]:
                    filename = item.get_name().replace("\\", "/")
                    self.resources[filename] = item.get_content()
                    basename = os.path.basename(filename)
                    if basename not in self.resources:
                        self.resources[basename] = item.get_content()
                    parts = filename.split("/")
                    for i in range(len(parts)):
                        partial_path = "/".join(parts[i:])
                        if partial_path not in self.resources:
                            self.resources[partial_path] = item.get_content()

    def requestStarted(self, request):
        """Gérer les requêtes de ressources."""
        url = request.requestUrl()
        path = url.path()

        if path.startswith("/"):
            path = path[1:]

        path = path.replace("\\", "/")

        content = self.resources.get(path)

        if content:
            content_type = b"application/octet-stream"
            path_lower = path.lower()
            if path_lower.endswith((".jpg", ".jpeg")):
                content_type = b"image/jpeg"
            elif path_lower.endswith(".png"):
                content_type = b"image/png"
            elif path_lower.endswith(".css"):
                content_type = b"text/css"

            buffer = QBuffer(parent=self)
            buffer.setData(QByteArray(content))
            buffer.open(QIODevice.ReadOnly)
            request.reply(content_type, buffer)
        else:
            request.fail(QWebEngineUrlRequestJob.UrlNotFound)


class EpubReaderPanel(QWidget):
    """Widget pour afficher et naviguer dans un fichier EPUB."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.book = None
        self.chapters = []
        self.current_chapter_index = 0
        self.search_text = ""
        self.book_title = ""
        self.book_author = ""

        # Initialiser le gestionnaire de schéma et le profil WebEngine
        self.scheme_handler = EpubSchemeHandler()
        self.profile = QWebEngineProfile()  # Utiliser un profil non-défaut
        self.profile.installUrlSchemeHandler(b"epub", self.scheme_handler)

        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur du panneau."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # En-tête de panneau
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Lecteur")
        label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa; padding: 8px 12px; font-weight: bold;
                color: #24292e; border: 1px solid #d1d5da; border-bottom: none;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            """
        )
        header_layout.addWidget(label)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)

        # Splitter pour TOC et contenu
        splitter = QSplitter(Qt.Horizontal)

        # Panneau TOC
        self.toc_widget = QWidget()
        toc_layout = QVBoxLayout(self.toc_widget)
        toc_layout.addWidget(QLabel("Table des matières"))
        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.load_chapter_from_list)
        toc_layout.addWidget(self.toc_list)
        splitter.addWidget(self.toc_widget)

        # Panneau Contenu
        reader_content_widget = QWidget()
        reader_layout = QVBoxLayout(reader_content_widget)

        # Barre de recherche
        search_layout = QHBoxLayout()
        # V3.0.1 - Bouton pour masquer/afficher la table des matières
        self.toggle_toc_btn = QPushButton("<")
        self.toggle_toc_btn.setFixedWidth(30)
        self.toggle_toc_btn.clicked.connect(self.toggle_toc_visibility)
        search_layout.addWidget(self.toggle_toc_btn)
        self.search_input = QLineEdit(placeholderText="Rechercher...")
        self.search_input.returnPressed.connect(self.search_in_text)
        search_layout.addWidget(self.search_input)
        self.search_btn = QPushButton("Rechercher")
        self.search_btn.clicked.connect(self.search_in_text)
        search_layout.addWidget(self.search_btn)
        self.search_next_btn = QPushButton("Suivant")
        self.search_next_btn.clicked.connect(self.find_next)
        search_layout.addWidget(self.search_next_btn)
        self.search_prev_btn = QPushButton("Précédent")
        self.search_prev_btn.clicked.connect(self.find_previous)
        search_layout.addWidget(self.search_prev_btn)
        self.clear_search_btn = QPushButton("Effacer")
        self.clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_btn)
        reader_layout.addLayout(search_layout)

        # Vue Web
        self.web_view = QWebEngineView()
        self.web_page = QWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        # V3.0.1 - Ajouter un facteur d'étirement pour que la vue web prenne tout l'espace vertical
        # Le '1' indique que ce widget doit s'étirer pour remplir l'espace disponible.
        reader_layout.addWidget(self.web_view, 1)

        # Barre de navigation
        nav_layout = QHBoxLayout()
        self.first_chapter_btn = QPushButton("⏮")
        self.first_chapter_btn.clicked.connect(self.first_chapter)
        nav_layout.addWidget(self.first_chapter_btn)
        self.prev_chapter_btn = QPushButton("◀")
        self.prev_chapter_btn.clicked.connect(self.previous_chapter)
        nav_layout.addWidget(self.prev_chapter_btn)
        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self.load_chapter_from_combo)
        nav_layout.addWidget(self.chapter_combo, 1)
        self.next_chapter_btn = QPushButton("▶")
        self.next_chapter_btn.clicked.connect(self.next_chapter)
        nav_layout.addWidget(self.next_chapter_btn)
        self.last_chapter_btn = QPushButton("⏭")
        self.last_chapter_btn.clicked.connect(self.last_chapter)
        nav_layout.addWidget(self.last_chapter_btn)
        reader_layout.addLayout(nav_layout)

        self.position_label = QLabel("Chapitre: - / -")
        reader_layout.addWidget(self.position_label, 0, Qt.AlignCenter)

        splitter.addWidget(reader_content_widget)
        splitter.setSizes([200, 600])
        # V3.0.1 - Ajouter un facteur d'étirement pour que le splitter prenne tout l'espace vertical
        # Le '1' indique que ce widget doit s'étirer pour remplir l'espace disponible.
        main_layout.addWidget(splitter, 1)

        self.enable_navigation(False)

    def load_document(self, filepath):
        """Charge un document EPUB."""
        if not filepath or not os.path.exists(filepath):
            self.web_view.setHtml("<h1>Fichier non trouvé</h1>")
            return

        try:
            self.book = epub.read_epub(filepath)
            self.scheme_handler.set_book(self.book)

            # V3.0.1 - Extraire le titre et l'auteur
            title_metadata = self.book.get_metadata("DC", "title")
            if title_metadata:
                self.book_title = title_metadata[0][0]
            else:
                self.book_title = "Titre inconnu"

            author_metadata = self.book.get_metadata("DC", "creator")
            if author_metadata:
                self.book_author = author_metadata[0][0]
            else:
                self.book_author = "Auteur inconnu"

            self.chapters = [
                item
                for item in self.book.get_items()
                if item.get_type() == ebooklib.ITEM_DOCUMENT
            ]

            if not self.chapters:
                QMessageBox.warning(self, "Erreur", "Aucun chapitre trouvé.")
                return

            self.toc_list.clear()
            self.chapter_combo.clear()

            for idx, chapter in enumerate(self.chapters):
                title = self._extract_title_from_content(
                    chapter.get_content()
                ) or os.path.basename(chapter.get_name())
                display_name = f"{idx + 1}. {title}"
                self.toc_list.addItem(display_name)
                self.chapter_combo.addItem(display_name)

            self.current_chapter_index = 0
            self.load_current_chapter()
            self.enable_navigation(True)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement EPUB", str(e))
            self.enable_navigation(False)

    def _extract_title_from_content(self, content):
        """Extrait le titre du contenu HTML."""
        try:
            content_str = content.decode("utf-8", errors="ignore")
            title_match = re.search(r"<title>(.*?)</title>", content_str, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()
            for tag in ["h1", "h2", "h3"]:
                heading_match = re.search(
                    f"<{tag}[^>]*>(.*?)</{tag}>", content_str, re.IGNORECASE
                )
                if heading_match:
                    return re.sub("<[^<]+?>", "", heading_match.group(1)).strip()
        except Exception:
            pass
        return None

    def load_current_chapter(self):
        """Charge le chapitre actuel dans la vue web."""
        if not self.chapters:
            return

        chapter = self.chapters[self.current_chapter_index]
        html_content = chapter.get_content().decode("utf-8", errors="ignore")

        # Utiliser une URL de base avec notre schéma personnalisé
        self.web_view.setHtml(html_content, QUrl("epub://local/"))

        self.toc_list.setCurrentRow(self.current_chapter_index)
        self.chapter_combo.setCurrentIndex(self.current_chapter_index)
        self.update_position_label()

    def update_position_label(self):
        if self.chapters:
            total = len(self.chapters)
            current = self.current_chapter_index + 1
            self.position_label.setText(
                f"<b>{self.book_title}</b> par <b>{self.book_author}</b> - Chapitre: {current} / {total}"
            )

    def load_chapter_from_list(self, item):
        self.current_chapter_index = self.toc_list.currentRow()
        self.load_current_chapter()

    def load_chapter_from_combo(self, index):
        if index >= 0 and index != self.current_chapter_index:
            self.current_chapter_index = index
            self.load_current_chapter()

    def previous_chapter(self):
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.load_current_chapter()

    def next_chapter(self):
        if self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            self.load_current_chapter()

    def first_chapter(self):
        if self.chapters:
            self.current_chapter_index = 0
            self.load_current_chapter()

    def last_chapter(self):
        if self.chapters:
            self.current_chapter_index = len(self.chapters) - 1
            self.load_current_chapter()

    def search_in_text(self):
        search_text = self.search_input.text()
        if search_text:
            self.search_text = search_text
            self.web_page.findText(search_text)

    def find_next(self):
        if self.search_text:
            self.web_page.findText(self.search_text)

    def find_previous(self):
        if self.search_text:
            self.web_page.findText(self.search_text, QWebEnginePage.FindBackward)

    def clear_search(self):
        self.search_input.clear()
        self.search_text = ""
        self.web_page.findText("")

    def enable_navigation(self, enabled):
        """Active ou désactive les contrôles de navigation."""
        self.first_chapter_btn.setEnabled(enabled)
        self.prev_chapter_btn.setEnabled(enabled)
        self.next_chapter_btn.setEnabled(enabled)
        self.last_chapter_btn.setEnabled(enabled)
        self.chapter_combo.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        self.search_next_btn.setEnabled(enabled)
        self.search_prev_btn.setEnabled(enabled)
        self.clear_search_btn.setEnabled(enabled)
        self.toc_list.setEnabled(enabled)

    def has_document(self):
        """Retourne True si un document est chargé."""
        return self.book is not None

    def toggle_toc_visibility(self):
        """Affiche ou masque le panneau de la table des matières."""
        if self.toc_widget.isVisible():
            self.toc_widget.hide()
            self.toggle_toc_btn.setText("▶")
        else:
            self.toc_widget.show()
            self.toggle_toc_btn.setText("◀")

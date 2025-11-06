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
from .pdf_viewer import PdfViewer
import ebooklib

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QPushButton,
    QComboBox,
    QStackedWidget,
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
                    content = item.get_content()

                    # Stocker avec le chemin complet
                    self.resources[filename] = content

                    # Stocker avec le nom de base
                    basename = os.path.basename(filename)
                    if basename not in self.resources:
                        self.resources[basename] = content

                    # Stocker avec les chemins partiels
                    parts = filename.split("/")
                    for i in range(len(parts)):
                        partial_path = "/".join(parts[i:])
                        if partial_path not in self.resources:
                            self.resources[partial_path] = content

    def requestStarted(self, request):
        """Gérer les requêtes de ressources."""
        url = request.requestUrl()
        path = url.path()

        if path.startswith("/"):
            path = path[1:]

        path = path.replace("\\", "/")

        # Chercher la ressource avec différentes stratégies
        content = None
        found_key = None

        if path in self.resources:
            content = self.resources[path]
            found_key = path
        else:
            dir_name = os.path.dirname(path)
            base_name = os.path.basename(path)

            # Stratégie 1: Chercher par nom de fichier dans le même dossier ou similaire
            for key in self.resources.keys():
                if key == path:
                    content = self.resources[key]
                    found_key = key
                    break
                elif os.path.basename(key) == base_name:
                    key_dir = os.path.dirname(key)
                    if (
                        dir_name in key_dir
                        or key_dir in dir_name
                        or dir_name == key_dir
                    ):
                        content = self.resources[key]
                        found_key = key
                        break

            # Stratégie 2: Chercher juste par nom de fichier
            if not content:
                for key in self.resources.keys():
                    if os.path.basename(key) == base_name:
                        content = self.resources[key]
                        found_key = key
                        break

        if content:
            content_type = b"application/octet-stream"
            path_lower = path.lower()
            if path_lower.endswith((".jpg", ".jpeg")):
                content_type = b"image/jpeg"
            elif path_lower.endswith(".png"):
                content_type = b"image/png"
            elif path_lower.endswith(".gif"):
                content_type = b"image/gif"
            elif path_lower.endswith(".svg"):
                content_type = b"image/svg+xml"
            elif path_lower.endswith(".webp"):
                content_type = b"image/webp"
            elif path_lower.endswith(".css"):
                content_type = b"text/css"
            elif path_lower.endswith(".js"):
                content_type = b"application/javascript"

            buffer = QBuffer(parent=self)
            buffer.setData(QByteArray(content))
            buffer.open(QIODevice.ReadOnly)
            request.reply(content_type, buffer)
        else:
            request.fail(QWebEngineUrlRequestJob.UrlNotFound)


# 3.0.7 Onglet Lecteur (epub) Fix [#46] Cannot scroll with mousewheel
class CustomWebEngineView(QWebEngineView):
    """Vue web personnalisée pour gérer le défilement par chapitre avec la molette."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.epub_reader_panel = parent

    def wheelEvent(self, event):
        """Gère les événements de la molette de la souris."""
        delta = event.angleDelta().y()

        def handle_scroll_check(at_end):
            if at_end:
                if delta < 0:  # Défilement vers le bas
                    self.epub_reader_panel.next_chapter()
                elif delta > 0:  # Défilement vers le haut
                    self.epub_reader_panel.previous_chapter()
            else:
                # Si on n'est pas au bout, on laisse l'événement de molette par défaut se produire
                super(CustomWebEngineView, self).wheelEvent(event)

        if delta < 0:  # Défilement vers le bas
            self.page().runJavaScript(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight - 2",
                handle_scroll_check,
            )
        elif delta > 0:  # Défilement vers le haut
            self.page().runJavaScript("window.scrollY === 0", handle_scroll_check)


class EpubReaderPanel(QWidget):
    """Widget pour afficher et naviguer dans un fichier EPUB."""

    def __init__(self, settings_manager=None, parent=None):
        super().__init__(parent)
        self.book = None
        self.chapters = []
        self.toc_items = []  # Liste des entrées TOC avec leur hiérarchie
        self.items_map = {}  # Mapping des items par nom/id
        self.current_chapter_index = 0
        self.current_toc_index = None  # Pour mémoriser l'entrée TOC sélectionnée
        self.search_text = ""
        self.book_title = ""
        self.book_author = ""

        # V3.0.5 - Ajout pour le lecteur PDF
        self.pdf_viewer = None
        self.current_doc_type = None  # 'epub' ou 'pdf'
        self.pdf_toc = []

        self.settings_manager = settings_manager
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
        self.toggle_toc_btn = QPushButton("◀")
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

        # V3.0.5 - Utiliser un QStackedWidget pour basculer entre les lecteurs
        self.stacked_viewer = QStackedWidget()

        # Lecteur EPUB (Vue Web)
        self.web_view = CustomWebEngineView(self)
        self.web_page = QWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        self.stacked_viewer.addWidget(self.web_view)

        # Lecteur PDF
        self.pdf_viewer = PdfViewer(settings_manager=self.settings_manager)
        self.pdf_viewer.page_changed_by_search.connect(self.on_pdf_page_changed)
        # V3.0.6 - Connecter le nouveau signal pour synchroniser l'UI
        self.pdf_viewer.page_changed.connect(self.on_pdf_page_changed)
        self.stacked_viewer.addWidget(self.pdf_viewer)
        # V3.0.1 - Ajouter un facteur d'étirement pour que la vue web prenne tout l'espace vertical
        # Le '1' indique que ce widget doit s'étirer pour remplir l'espace disponible.
        reader_layout.addWidget(self.stacked_viewer, 1)

        # Barre de navigation
        nav_layout = QHBoxLayout()
        self.first_chapter_btn = QPushButton("◀◀ Début")
        # self.first_chapter_btn.setFixedSize(50, 50)
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
        self.last_chapter_btn = QPushButton("Fin ▶▶")
        # self.last_chapter_btn.setFixedSize(50, 50)
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
            self.show_error("<h1>Fichier non trouvé</h1>")
            return

        _, ext = os.path.splitext(filepath)
        ext = ext.lower()

        if ext == ".epub":
            self.current_doc_type = "epub"
            self.stacked_viewer.setCurrentWidget(self.web_view)
            self.load_epub(filepath)
        elif ext == ".pdf":
            self.current_doc_type = "pdf"
            self.stacked_viewer.setCurrentWidget(self.pdf_viewer)
            self.load_pdf(filepath)
        else:
            self.show_error(f"<h1>Format de fichier non supporté : {ext}</h1>")

    def load_epub(self, filepath):
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

            # Créer un mapping des items par leur nom/id
            self.items_map = {}
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    self.items_map[item.get_name()] = item
                    if hasattr(item, "id") and item.id:
                        self.items_map[item.id] = item

            # Récupérer la table des matières depuis toc
            self.chapters = []
            self.toc_items = []

            if self.book.toc:
                # La TOC existe, l'utiliser
                self._parse_toc(self.book.toc, level=0)
            else:
                # Pas de TOC, utiliser tous les documents dans l'ordre du spine
                print("Pas de TOC trouvée, utilisation du spine")
                spine = self.book.spine
                for item_id, linear in spine:
                    if item_id in self.items_map:
                        item = self.items_map[item_id]
                        self.chapters.append(item)
                        title = self._extract_title_from_content(item.get_content())
                        if not title:
                            title = os.path.basename(item.get_name())
                        self.toc_items.append(
                            {
                                "title": title,
                                "item": item,
                                "chapter_index": len(self.chapters) - 1,
                                "level": 0,
                            }
                        )

            if not self.chapters:
                QMessageBox.warning(self, "Erreur", "Aucun chapitre trouvé.")
                return

            # Charger la table des matières dans l'interface
            self.toc_list.clear()
            self.chapter_combo.clear()

            for idx, toc_item in enumerate(self.toc_items):
                level = toc_item.get("level", 0)
                title = toc_item.get("title", "Titre inconnu")

                # Indenter selon le niveau
                indent = "  " * level
                display_name = f"{indent}{title}"

                # Mettre en gras les chapitres de niveau 0
                font = self.toc_list.font()
                if level == 0:
                    font.setBold(True)
                else:
                    font.setBold(False)

                item = QListWidgetItem(display_name)
                item.setFont(font)
                self.toc_list.addItem(item)
                self.chapter_combo.addItem(display_name)
                self.chapter_combo.setItemData(idx, font, Qt.FontRole)

            self.current_chapter_index = 0
            self.current_toc_index = None
            self.load_current_chapter()
            self.enable_navigation(True)

            print(f"📖 Livre chargé: {len(self.chapters)} chapitres trouvés")

        except Exception as e:
            import traceback

            traceback.print_exc()
            QMessageBox.critical(self, "Erreur de chargement EPUB", str(e))
            self.enable_navigation(False)

    def load_pdf(self, filepath):
        """Charge un document PDF."""
        self.pdf_viewer.document_loaded.connect(self.on_pdf_document_loaded)
        self.pdf_viewer.load_document(filepath)

    def on_pdf_document_loaded(self, success, title, author, toc, page_count):
        """Callback après le chargement du PDF."""
        self.pdf_viewer.document_loaded.disconnect(self.on_pdf_document_loaded)

        if not success:
            self.enable_navigation(False)
            return

        self.book_title = title
        self.book_author = author
        self.pdf_toc = toc
        self.chapters = list(range(page_count))  # Chaque page est un "chapitre"

        self.toc_list.clear()
        self.chapter_combo.clear()

        if toc:
            for level, toc_title, page_num in toc:
                # page_num est 1-based, on le veut 0-based
                item = QListWidgetItem("  " * (level - 1) + toc_title)
                font = self.toc_list.font()
                font.setBold(level == 1)
                item.setFont(font)
                self.toc_list.addItem(item)
                self.chapter_combo.addItem("  " * (level - 1) + toc_title)
        else:
            # Si pas de TOC, créer une entrée par page
            for i in range(page_count):
                title = f"Page {i + 1}"
                self.toc_list.addItem(title)
                self.chapter_combo.addItem(title)

        self.current_chapter_index = 0
        self.load_current_chapter()
        self.enable_navigation(True)

        print(f"📖 Livre PDF chargé: {page_count} pages trouvées")

    def _parse_toc(self, toc, level=0):
        """Parser récursivement la table des matières."""
        for item in toc:
            if isinstance(item, tuple):
                # C'est un item de TOC (Section, Link)
                section = item[0]

                # Extraire le titre
                if hasattr(section, "title"):
                    title = section.title
                else:
                    title = str(section)

                # Extraire le lien vers le document
                href = None
                if hasattr(section, "href"):
                    href = section.href

                # Trouver l'item correspondant
                if href:
                    clean_href = href.split("#")[0]

                    # Chercher l'item correspondant
                    item_found = None
                    for key, doc_item in self.items_map.items():
                        if clean_href in key or key in clean_href:
                            item_found = doc_item
                            break

                    if item_found:
                        # Ajouter à la liste seulement si pas déjà présent
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)

                        # Trouver l'index du chapitre
                        chapter_index = self.chapters.index(item_found)

                        # Ajouter à toc_items SEULEMENT si item trouvé
                        self.toc_items.append(
                            {
                                "title": title,
                                "item": item_found,
                                "chapter_index": chapter_index,
                                "level": level,
                                "href": href,
                            }
                        )
                    else:
                        print(f"Item TOC non trouvé: {title} -> {href}")

                # Parser les sous-éléments si présents
                if len(item) > 1 and isinstance(item[1], list):
                    self._parse_toc(item[1], level + 1)

            elif isinstance(item, list):
                # C'est une liste de sous-items
                self._parse_toc(item, level)

            else:
                # C'est un objet Link ou Section direct
                if hasattr(item, "title"):
                    title = item.title
                else:
                    title = str(item)

                href = None
                if hasattr(item, "href"):
                    href = item.href

                if href:
                    clean_href = href.split("#")[0]

                    item_found = None
                    for key, doc_item in self.items_map.items():
                        if clean_href in key or key in clean_href:
                            item_found = doc_item
                            break

                    if item_found:
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)

                        # Trouver l'index du chapitre
                        chapter_index = self.chapters.index(item_found)

                        # Ajouter à toc_items SEULEMENT si item trouvé
                        self.toc_items.append(
                            {
                                "title": title,
                                "item": item_found,
                                "chapter_index": chapter_index,
                                "level": level,
                                "href": href,
                            }
                        )
                    else:
                        print(f"Item TOC non trouvé: {title} -> {href}")

                # Vérifier les sous-éléments
                if hasattr(item, "__iter__") and not isinstance(item, str):
                    try:
                        self._parse_toc(list(item), level)
                    except:
                        pass

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
        if not self.chapters or self.current_chapter_index >= len(self.chapters):
            return

        if self.current_doc_type == "pdf":
            self.pdf_viewer.go_to_page(self.current_chapter_index)
            self.update_position_label()

            # V3.0.5 - Synchroniser la TOC et le ComboBox pour le PDF
            toc_index_to_select = -1
            if self.pdf_toc:
                # Trouver l'entrée TOC la plus proche de la page actuelle
                for i, (_, _, page_num) in reversed(list(enumerate(self.pdf_toc))):
                    if page_num - 1 <= self.current_chapter_index:
                        toc_index_to_select = i
                        break
            else:
                # Si pas de TOC, l'index de la page correspond à l'index de la liste
                toc_index_to_select = self.current_chapter_index

            if toc_index_to_select != -1:
                self.toc_list.blockSignals(True)
                self.chapter_combo.blockSignals(True)

                self.toc_list.setCurrentRow(toc_index_to_select)
                self.chapter_combo.setCurrentIndex(toc_index_to_select)

                self.toc_list.blockSignals(False)
                self.chapter_combo.blockSignals(False)
            return

        chapter = self.chapters[self.current_chapter_index]
        html_content = chapter.get_content().decode("utf-8", errors="ignore")

        # Remplacer les chemins des images pour utiliser notre schéma personnalisé
        html_content = re.sub(
            r'src=["\']([^"\']+)["\']',
            lambda m: f'src="epub://epub/{m.group(1)}"',
            html_content,
        )

        # Remplacer aussi les liens CSS
        html_content = re.sub(
            r'href=["\']([^"\']*\.css)["\']',
            lambda m: f'href="epub://epub/{m.group(1)}"',
            html_content,
        )

        # Trouver l'entrée TOC correspondant au chapitre actuel et à l'index TOC sélectionné
        toc_index = -1
        anchor = None

        # Si on a un current_toc_index, l'utiliser (défini lors du clic dans la TOC)
        if self.current_toc_index is not None and self.current_toc_index < len(
            self.toc_items
        ):
            toc_item = self.toc_items[self.current_toc_index]
            if toc_item["chapter_index"] == self.current_chapter_index:
                toc_index = self.current_toc_index
                if "href" in toc_item and "#" in toc_item["href"]:
                    anchor = toc_item["href"].split("#")[1]

        # Sinon, trouver la première entrée TOC pour ce chapitre
        if toc_index < 0:
            for idx, toc_item in enumerate(self.toc_items):
                if toc_item["chapter_index"] == self.current_chapter_index:
                    toc_index = idx
                    if "href" in toc_item and "#" in toc_item["href"]:
                        anchor = toc_item["href"].split("#")[1]
                    break

        # Injecter un script pour gérer le scroll après le chargement
        scroll_script = ""
        if anchor:
            print(f"Préparation scroll vers l'ancre: {anchor}")
            scroll_script = f"""
            <script>
            window.addEventListener('load', function() {{
                console.log('Page loaded, searching for anchor: {anchor}');
                
                // Chercher l'élément avec l'id
                var element = document.getElementById('{anchor}');
                if (!element) {{
                    console.log('Not found by ID, trying by name attribute');
                    element = document.querySelector('[name="{anchor}"]');
                }}
                if (!element) {{
                    console.log('Not found by name, trying by epub:type');
                    element = document.querySelector('[epub\\\\:type="{anchor}"]');
                }}
                
                if (element) {{
                    console.log('Element found, scrolling');
                    setTimeout(function() {{
                        element.scrollIntoView({{behavior: 'smooth', block: 'start'}});
                        // Highlight temporaire pour debug
                        element.style.backgroundColor = '#ffff99';
                        setTimeout(function() {{
                            element.style.backgroundColor = '';
                        }}, 2000);
                    }}, 100);
                }} else {{
                    console.log('Anchor not found: {anchor}');
                }}
            }});
            </script>
            """

        # Ajouter le script et utiliser une URL de base avec notre schéma personnalisé
        styled_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
            {scroll_script}
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        self.web_view.setHtml(styled_content, QUrl("epub://epub/"))

        # Mettre à jour l'interface seulement si on a trouvé l'entrée TOC
        if toc_index >= 0:
            self.toc_list.blockSignals(True)
            self.chapter_combo.blockSignals(True)

            self.toc_list.setCurrentRow(toc_index)
            self.chapter_combo.setCurrentIndex(toc_index)

            self.toc_list.blockSignals(False)
            self.chapter_combo.blockSignals(False)

        self.update_position_label()

    def update_position_label(self):
        if self.chapters:
            total = len(self.chapters)
            current = self.current_chapter_index + 1
            self.position_label.setText(
                f"<b>{self.book_title}</b> par <b>{self.book_author}</b> - Chapitre: {current} / {total}"
            )

    def load_chapter_from_list(self, item):
        """Charger un chapitre depuis la liste de la table des matières."""
        index = self.toc_list.currentRow()
        if index < 0:
            return

        if self.current_doc_type == "epub" and index < len(self.toc_items):
            # Stocker l'index TOC sélectionné
            self.current_toc_index = index
            # Utiliser l'index du chapitre stocké dans toc_items
            self.current_chapter_index = self.toc_items[index]["chapter_index"]

            # Afficher des infos de debug
            toc_item = self.toc_items[index]
            # print(
            #     f"Navigation TOC: {toc_item['title']} -> chapitre {self.current_chapter_index}"
            # )
            # if "href" in toc_item:
            #    print(f"  href: {toc_item['href']}")

            self.load_current_chapter()
        elif self.current_doc_type == "pdf":
            if self.pdf_toc:
                # Le numéro de page est 1-based dans la TOC de PyMuPDF
                page_num = self.pdf_toc[index][2] - 1
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index

            self.load_current_chapter()
            # V3.0.5 - Correction du debug pour PDF
            print(f"Navigation PDF TOC: page {self.current_chapter_index + 1}")

    def load_chapter_from_combo(self, index):
        """Charger un chapitre depuis le combo box."""
        if index < 0:
            return

        if self.current_doc_type == "epub" and index < len(self.toc_items):
            # Stocker l'index TOC sélectionné
            self.current_toc_index = index
            # Utiliser l'index du chapitre stocké dans toc_items
            self.current_chapter_index = self.toc_items[index]["chapter_index"]

            # Afficher des infos de debug
            toc_item = self.toc_items[index]
            # print( f"Navigation combo: {toc_item['title']} -> chapitre {self.current_chapter_index}"
            # )

            # if "href" in toc_item:
            #    print(f"  href: {toc_item['href']}")

            self.load_current_chapter()
        elif self.current_doc_type == "pdf":
            if self.pdf_toc:
                page_num = self.pdf_toc[index][2] - 1
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index

            self.load_current_chapter()
            # V3.0.5 - Correction du debug pour PDF
            # print(f"Navigation PDF combo: page {self.current_chapter_index + 1}")

    def previous_chapter(self):
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            # Réinitialiser current_toc_index pour utiliser la première entrée du chapitre
            self.current_toc_index = None
            self.load_current_chapter()

    def next_chapter(self):
        if self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            # Réinitialiser current_toc_index pour utiliser la première entrée du chapitre
            self.current_toc_index = None
            self.load_current_chapter()

    def first_chapter(self):
        if self.chapters:
            self.current_chapter_index = 0
            # Réinitialiser current_toc_index pour utiliser la première entrée du chapitre
            self.current_toc_index = None
            self.load_current_chapter()

    def last_chapter(self):
        if self.chapters:
            self.current_chapter_index = len(self.chapters) - 1
            # Réinitialiser current_toc_index pour utiliser la première entrée du chapitre
            self.current_toc_index = None
            self.load_current_chapter()

    def search_in_text(self):
        search_text = self.search_input.text()
        if search_text:
            self.search_text = search_text
            if self.current_doc_type == "epub":
                self.web_page.findText(search_text)
            elif self.current_doc_type == "pdf":
                self.pdf_viewer.find_text(search_text, new_search=True)

    def find_next(self):
        if self.search_text:
            if self.current_doc_type == "epub":
                self.web_page.findText(self.search_text)
            elif self.current_doc_type == "pdf":
                self.pdf_viewer.navigate_search_results(1)

    def find_previous(self):
        if self.search_text:
            if self.current_doc_type == "epub":
                self.web_page.findText(self.search_text, QWebEnginePage.FindBackward)
            elif self.current_doc_type == "pdf":
                self.pdf_viewer.navigate_search_results(-1)

    def clear_search(self):
        self.search_input.clear()
        self.search_text = ""
        if self.current_doc_type == "epub":
            self.web_page.findText("")
        elif self.current_doc_type == "pdf":
            self.pdf_viewer.clear_search()

    def on_pdf_page_changed(self, page_num):
        """Slot appelé lorsque le PdfViewer change de page (ex: via la recherche)."""
        if self.current_chapter_index != page_num:
            self.current_chapter_index = page_num
            self.load_current_chapter()

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

    def show_error(self, message):
        self.web_view.setHtml(message)
        self.stacked_viewer.setCurrentWidget(self.web_view)

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

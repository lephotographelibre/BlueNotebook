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
Panneau de lecture de documents EPUB et PDF pour BlueNotebook.
"""

import os
import re
import base64
from ebooklib import epub
from .pdf_viewer import PdfViewer
import ebooklib
import mimetypes

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QApplication,
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
    QFileDialog,
    QMenu,
    QAction,
)
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineContextMenuData,
)
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt5.QtCore import Qt, QUrl, QBuffer, QIODevice, QByteArray, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
from PIL import Image
import io
from pathlib import Path


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
            # Parcourir tous les éléments du livre et les stocker
            for item in self.book.get_items():
                # Stocker la ressource en utilisant son chemin canonique comme clé unique.
                # Cela évite les ambiguïtés et les collisions de noms.
                # ex: 'OEBPS/Images/cover.jpg'
                self.resources[item.get_name()] = item.get_content()

    def requestStarted(self, request):
        """Gérer les requêtes de ressources."""
        url = request.requestUrl()
        # Normaliser le chemin demandé en retirant le slash initial
        path = url.path().lstrip(self.tr("/"))

        # Tentative de trouver la ressource avec le chemin exact
        content = self.resources.get(path)

        # Si le chemin exact n'est pas trouvé (ex: requête pour 'Images/cover.jpg'
        # alors que la ressource est stockée sous 'OEBPS/Images/cover.jpg'),
        # on cherche une clé qui se termine par le chemin demandé.
        # C'est une manière robuste de résoudre les chemins relatifs sans ambiguïté.
        if content is None:
            for key, value in self.resources.items():
                # Utiliser os.path.normpath pour gérer les différences de slashes ( / vs \ )
                # et s'assurer que la comparaison est fiable.
                # La normalisation des chemins est implicite avec endswith sur des chemins propres.
                # On s'assure que les chemins sont propres (pas de './' ou '../' etc.)
                # en ne stockant que les chemins canoniques.
                normalized_key = key.replace(self.tr("\\"), self.tr("/"))
                if normalized_key.endswith(path):
                    content = value
                    break  # On a trouvé une correspondance, on s'arrête.

        if content:
            content_type = self.tr(b"application/octet-stream")
            path_lower = path.lower()
            if path_lower.endswith((".jpg", ".jpeg")):
                content_type = self.tr(b"image/jpeg")
            elif path_lower.endswith(".png"):
                content_type = self.tr(b"image/png")
            elif path_lower.endswith(".gif"):
                content_type = self.tr(b"image/gif")
            elif path_lower.endswith(".svg"):
                content_type = self.tr(b"image/svg+xml")
            elif path_lower.endswith(".webp"):
                content_type = self.tr(b"image/webp")
            elif path_lower.endswith(".css"):
                content_type = self.tr(b"text/css")
            elif path_lower.endswith(".js"):
                content_type = self.tr(b"application/javascript")

            buffer = QBuffer(parent=self)
            buffer.setData(QByteArray(content))
            buffer.open(QIODevice.ReadOnly)
            request.reply(content_type, buffer)
        else:
            request.fail(QWebEngineUrlRequestJob.UrlNotFound)


class CustomWebEngineView(QWebEngineView):
    """Vue web personnalisée pour gérer le défilement par chapitre avec la molette."""

    scroll_position_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.epub_reader_panel = parent
        self.page().scrollPositionChanged.connect(self._on_scroll_changed)

    def contextMenuEvent(self, event):
        """Gère le menu contextuel personnalisé."""
        menu = QMenu(self)
        context_data = self.page().contextMenuData()

        # Si c'est une image
        if context_data.mediaType() == QWebEngineContextMenuData.MediaTypeImage:
            save_image_action = QAction(self.tr("Sauvegarder l'image"), self)
            save_image_action.triggered.connect(lambda: self.save_image(context_data))
            menu.addAction(save_image_action)

            copy_image_action = QAction(self.tr("Copier l'image"), self)
            copy_image_action.triggered.connect(lambda: self.copy_image(context_data))
            menu.addAction(copy_image_action)

            copy_url_action = QAction(self.tr("Copier l'adresse de l'image"), self)
            copy_url_action.triggered.connect(lambda: self.copy_image_url(context_data))
            menu.addAction(copy_url_action)
        else:
            # Actions personnalisées pour le texte avec libellés en français
            copy_text_action = QAction(self.tr("Copier le texte sélectionné"), self)
            copy_text_action.setEnabled(self.page().selectedText().strip() != self.tr(""))
            copy_text_action.triggered.connect(
                lambda: self.page().triggerAction(QWebEnginePage.Copy)
            )
            menu.addAction(copy_text_action)

            select_all_text_action = QAction(self.tr("Tout sélectionner"), self)
            select_all_text_action.triggered.connect(
                lambda: self.page().triggerAction(QWebEnginePage.SelectAll)
            )
            menu.addAction(select_all_text_action)

            menu.addSeparator()

        menu.exec_(event.globalPos())

    def save_image(self, context_data):
        """Sauvegarde l'image sur le disque."""
        image_url = context_data.mediaUrl().toString()

        if not image_url:
            QMessageBox.warning(
                self, self.tr("Erreur"), self.tr("Impossible de récupérer l'URL de l'image")
            )
            return

        if image_url.startswith("epub://epub/"):
            image_path = image_url.replace(self.tr("epub://epub/"), self.tr(""))

            scheme_handler = self.epub_reader_panel.scheme_handler
            if image_path in scheme_handler.resources:
                image_data = scheme_handler.resources[image_path]

                base_name = os.path.splitext(os.path.basename(image_path))[0]
                suggested_filename = self.tr("%1.jpg").arg(base_name)

                last_save_dir = self.epub_reader_panel.settings_manager.get(
                    self.tr("reader.last_image_save_directory"), str(Path.home())
                )
                default_path = os.path.join(last_save_dir, suggested_filename)

                file_filter = self.tr("Image JPEG (*.jpg)")
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    self.tr("Sauvegarder l'image"),
                    default_path,
                    file_filter,
                )

                if save_path:
                    try:
                        img = Image.open(io.BytesIO(image_data))
                        if img.mode != self.tr("RGB"):
                            img = img.convert(self.tr("RGB"))
                        img.save(save_path, self.tr("JPEG"), quality=90)
                        new_save_dir = os.path.dirname(save_path)
                        self.epub_reader_panel.settings_manager.set(
                            self.tr("reader.last_image_save_directory"), new_save_dir
                        )
                        self.epub_reader_panel.settings_manager.save_settings()
                        QMessageBox.information(
                            self, self.tr("Succès"), self.tr("Image sauvegardée dans:\n%1").arg(save_path)
                        )
                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            self.tr("Erreur"),
                            self.tr("Impossible de convertir ou sauvegarder l'image:\n%1").arg(str(e)),
                        )
            else:
                QMessageBox.warning(
                    self, self.tr("Erreur"), self.tr("Image introuvable dans les ressources EPUB")
                )

    def copy_image(self, context_data):
        """Copie l'image dans le presse-papiers."""
        image_url = context_data.mediaUrl().toString()

        if not image_url or not image_url.startswith("epub://epub/"):
            return

        image_path = image_url.replace(self.tr("epub://epub/"), self.tr(""))
        scheme_handler = self.epub_reader_panel.scheme_handler

        if image_path in scheme_handler.resources:
            image_data = scheme_handler.resources[image_path]
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(image_data))

            if not pixmap.isNull():
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)
                self.epub_reader_panel.position_label.setText(
                    self.tr("Image copiée dans le presse-papiers")
                )
                QTimer.singleShot(
                    2000, lambda: self.epub_reader_panel.update_position_label()
                )

    def copy_image_url(self, context_data):
        """Copie l'URL de l'image dans le presse-papiers."""
        image_url = context_data.mediaUrl().toString()
        if image_url:
            clipboard = QApplication.clipboard()
            clipboard.setText(image_url)

    def wheelEvent(self, event):
        if self.epub_reader_panel.current_doc_type != self.tr("epub"):
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y()

        def handle_scroll_check(at_end):
            if at_end:
                if delta < 0:
                    self.epub_reader_panel.next_chapter()
                elif delta > 0:
                    self.epub_reader_panel.previous_chapter()

        if delta < 0:
            self.page().runJavaScript(
                self.tr("window.scrollY + window.innerHeight >= document.body.scrollHeight - 2"),
                handle_scroll_check,
            )
        elif delta > 0:
            self.page().runJavaScript(self.tr("window.scrollY === 0"), handle_scroll_check)

        super().wheelEvent(event)

    def _on_scroll_changed(self, pos):
        self.scroll_position_changed.emit(int(pos.y()))


class EpubReaderPanel(QWidget):
    """Widget pour afficher et naviguer dans un fichier EPUB ou PDF."""

    def __init__(self, settings_manager=None, parent=None):
        super().__init__(parent)
        self.book = None
        self.chapters = []
        self.toc_items = []
        self.items_map = {}
        self.current_chapter_index = 0
        self.current_toc_index = None
        self.search_text = self.tr("")
        self.book_title = self.tr("")
        self.book_author = self.tr("")
        self.pdf_viewer = None
        self.current_doc_type = None
        self.pdf_toc = []
        self.settings_manager = settings_manager
        self.scheme_handler = EpubSchemeHandler()
        self.profile = QWebEngineProfile()
        self.profile.installUrlSchemeHandler(self.tr(b"epub"), self.scheme_handler)
        self.search_results = []
        self.current_search_index = -1

        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur du panneau."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.tr("Lecteur"))
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

        splitter = QSplitter(Qt.Horizontal)

        self.toc_widget = QWidget()
        toc_layout = QVBoxLayout(self.toc_widget)
        toc_layout.addWidget(QLabel(self.tr("Table des matières")))
        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.load_chapter_from_list)
        toc_layout.addWidget(self.toc_list)
        splitter.addWidget(self.toc_widget)

        self.stacked_viewer = QStackedWidget()
        self.web_view = CustomWebEngineView(self)
        self.web_page = QWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        self.pdf_viewer = PdfViewer(settings_manager=self.settings_manager, parent=self)
        self.web_view.scroll_position_changed.connect(self.sync_toc_from_scroll)
        self.pdf_viewer.page_changed.connect(self.on_pdf_page_changed)
        self.pdf_viewer.document_loaded.connect(self.on_pdf_document_loaded)
        self.stacked_viewer.addWidget(self.web_view)
        self.stacked_viewer.addWidget(self.pdf_viewer)

        reader_content_widget = QWidget()
        reader_layout = QVBoxLayout(reader_content_widget)

        search_layout = QHBoxLayout()
        self.toggle_toc_btn = QPushButton(self.tr("◀"))
        self.toggle_toc_btn.setFixedWidth(30)
        self.toggle_toc_btn.clicked.connect(self.toggle_toc_visibility)
        search_layout.addWidget(self.toggle_toc_btn)
        self.search_input = QLineEdit(placeholderText=self.tr("Rechercher..."))
        self.search_input.returnPressed.connect(self.search_in_text)
        search_layout.addWidget(self.search_input)
        self.search_btn = QPushButton(self.tr("Rechercher"))
        self.search_btn.clicked.connect(self.search_in_text)
        search_layout.addWidget(self.search_btn)
        self.search_next_btn = QPushButton(self.tr("Suivant"))
        self.search_next_btn.clicked.connect(self.find_next)
        search_layout.addWidget(self.search_next_btn)
        self.search_prev_btn = QPushButton(self.tr("Précédent"))
        self.search_prev_btn.clicked.connect(self.find_previous)
        search_layout.addWidget(self.search_prev_btn)
        self.clear_search_btn = QPushButton(self.tr("Effacer"))
        self.clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_btn)
        reader_layout.addLayout(search_layout)

        reader_layout.addWidget(self.stacked_viewer, 1)

        nav_layout = QHBoxLayout()
        self.first_chapter_btn = QPushButton(self.tr("◀◀ Début"))
        self.first_chapter_btn.clicked.connect(self.first_chapter)
        nav_layout.addWidget(self.first_chapter_btn)
        self.prev_chapter_btn = QPushButton(self.tr("◀"))
        self.prev_chapter_btn.clicked.connect(self.previous_chapter)
        nav_layout.addWidget(self.prev_chapter_btn)
        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self.load_chapter_from_combo)
        nav_layout.addWidget(self.chapter_combo, 1)
        self.next_chapter_btn = QPushButton(self.tr("▶"))
        self.next_chapter_btn.clicked.connect(self.next_chapter)
        nav_layout.addWidget(self.next_chapter_btn)
        self.last_chapter_btn = QPushButton(self.tr("Fin ▶▶"))
        self.last_chapter_btn.clicked.connect(self.last_chapter)
        nav_layout.addWidget(self.last_chapter_btn)
        reader_layout.addLayout(nav_layout)

        self.position_label = QLabel(self.tr("Chapitre: - / -"))
        reader_layout.addWidget(self.position_label, 0, Qt.AlignCenter)

        splitter.addWidget(reader_content_widget)
        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter, 1)

        self.enable_navigation(False)

    def load_document(self, filepath):
        """Charge un document EPUB ou PDF."""
        if not filepath or not os.path.exists(filepath):
            self.show_error(self.tr("<h1>Fichier non trouvé</h1>"))
            return

        # V3.5.1.1 - Correction du problème de cache de couverture EPUB.
        # Vider le cache HTTP du profil web avant de charger un nouveau document.
        # Cela force le rechargement de toutes les ressources (images, etc.).
        self.profile.clearHttpCache()

        mime_type, _ = mimetypes.guess_type(filepath)
        file_ext = os.path.splitext(filepath)[1].lower()

        if mime_type == self.tr("application/pdf") or file_ext == self.tr(".pdf"):
            try:
                self.current_doc_type = self.tr("pdf")
                self.pdf_viewer.load_document(filepath)
                self.current_chapter_index = 0
            except Exception as e:
                self.show_error(self.tr("<h1>Erreur lors du chargement du PDF : %1</h1>").arg(str(e)))
            return

        try:
            self.current_doc_type = self.tr("epub")
            self.book = epub.read_epub(filepath)
            self.scheme_handler.set_book(self.book)

            title_metadata = self.book.get_metadata(self.tr("DC"), self.tr("title"))
            if title_metadata:
                self.book_title = title_metadata[0][0]
            else:
                self.book_title = self.tr("Titre inconnu")

            author_metadata = self.book.get_metadata(self.tr("DC"), self.tr("creator"))
            if author_metadata:
                self.book_author = author_metadata[0][0]
            else:
                self.book_author = self.tr("Auteur inconnu")

            self.items_map = {}
            self.chapters = []
            self.toc_items = []
            self.current_chapter_index = 0
            self.current_toc_index = None

            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    self.items_map[item.get_name().replace(self.tr("\\"), self.tr("/"))] = item

            if self.book.toc:
                self._parse_toc(self.book.toc)

            self.toc_list.clear()
            self.chapter_combo.clear()

            for toc_item in self.toc_items:
                title = toc_item[self.tr("title")]
                level = toc_item[self.tr("level")]
                indent = self.tr("  ") * level
                self.toc_list.addItem(QListWidgetItem(self.tr("%1%2").arg(indent).arg(title)))
                self.chapter_combo.addItem(self.tr("%1%2").arg(indent).arg(title))

            if not self.chapters:
                for item in self.book.spine:
                    item_id = item[0] if isinstance(item, tuple) else item
                    for doc_item in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                        if doc_item.id == item_id:
                            if doc_item not in self.chapters:
                                self.chapters.append(doc_item)
                            title = self._extract_title_from_content(
                                doc_item.get_content()
                            )
                            if not title:
                                title = doc_item.get_name()
                            self.toc_items.append(
                                {
                                    self.tr("title"): title,
                                    self.tr("item"): doc_item,
                                    self.tr("chapter_index"): self.chapters.index(doc_item),
                                    self.tr("level"): 0,
                                    self.tr("href"): doc_item.get_name(),
                                }
                            )
                            self.toc_list.addItem(QListWidgetItem(title))
                            self.chapter_combo.addItem(title)

            if self.chapters:
                self.enable_navigation(True)
                self.stacked_viewer.setCurrentWidget(self.web_view)
                self.load_current_chapter()

        except Exception as e:
            self.show_error(self.tr("<h1>Erreur lors du chargement de l'EPUB : %1</h1>").arg(str(e)))

    def _parse_toc(self, toc, level=0):
        """Parser récursivement la table des matières avec matching exact."""
        for item in toc:
            if isinstance(item, tuple):
                if hasattr(item[0], self.tr("title")) and hasattr(item[0], self.tr("href")):
                    title = item[0].title
                    href = item[0].href
                    clean_href = href.split(self.tr("#"))[0]
                    clean_href = os.path.normpath(clean_href.replace("\\", "/"))
                    item_found = None
                    for key in sorted(self.items_map.keys(), key=len, reverse=True):
                        norm_key = os.path.normpath(key.replace("\\", "/"))
                        if clean_href == norm_key:
                            item_found = self.items_map[key]
                            break
                    if item_found:
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)
                        chapter_index = self.chapters.index(item_found)
                        self.toc_items.append(
                            {
                                self.tr("title"): title,
                                self.tr("item"): item_found,
                                self.tr("chapter_index"): chapter_index,
                                self.tr("level"): level,
                                self.tr("href"): href,
                            }
                        )
                    if len(item) > 1 and isinstance(item[1], list):
                        self._parse_toc(item[1], level + 1)

            elif isinstance(item, list):
                self._parse_toc(item, level)

            else:
                if hasattr(item, self.tr("title")):
                    title = item.title
                else:
                    title = str(item)

                href = None
                if hasattr(item, self.tr("href")):
                    href = item.href

                if href:
                    clean_href = href.split(self.tr("#"))[0]
                    clean_href = os.path.normpath(clean_href.replace("\\", "/"))
                    item_found = None
                    for key in sorted(self.items_map.keys(), key=len, reverse=True):
                        norm_key = os.path.normpath(key.replace("\\", "/"))
                        if clean_href == norm_key:
                            item_found = self.items_map[key]
                            break
                    if item_found:
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)
                        chapter_index = self.chapters.index(item_found)
                        self.toc_items.append(
                            {
                                self.tr("title"): title,
                                self.tr("item"): item_found,
                                self.tr("chapter_index"): chapter_index,
                                self.tr("level"): level,
                                self.tr("href"): href,
                            }
                        )

                if hasattr(item, self.tr("__iter__")) and not isinstance(item, str):
                    try:
                        self._parse_toc(list(item), level)
                    except:
                        pass

    def _extract_title_from_content(self, content):
        """Extrait le titre du contenu HTML."""
        try:
            content_str = content.decode(self.tr("utf-8"), errors=self.tr("ignore"))
            title_match = re.search(self.tr(r"<title>(.*?)</title>"), content_str, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()
            for tag in [self.tr("h1"), self.tr("h2"), self.tr("h3")]:
                heading_match = re.search(
                    self.tr("<%1[^>]*>(.*?)</%2>").arg(tag).arg(tag), content_str, re.IGNORECASE
                )
                if heading_match:
                    return re.sub("<[^<]+?>", "", heading_match.group(1)).strip()
        except Exception:
            pass
        return None

    def load_current_chapter(self):
        """Charge le chapitre actuel dans la vue web ou PDF."""
        if not self.chapters:
            return

        if self.current_doc_type == self.tr("epub"):
            chapter = self.chapters[self.current_chapter_index]
            html_content = chapter.get_content().decode(self.tr("utf-8"), errors=self.tr("ignore"))

            html_content = re.sub(
                self.tr(r'src=["\']([^"\']+)["\']'),
                lambda m: self.tr("src="epub://epub/%1"").arg(m.group(1)),
                html_content,
            )

            html_content = re.sub(
                r'href=["\']([^"\']*\.css)["\']',
                lambda m: self.tr("href="epub://epub/%1"").arg(m.group(1)),
                html_content,
            )

            toc_index = -1
            anchor = None
            if self.current_toc_index is not None and self.current_toc_index < len(
                self.toc_items
            ):
                toc_item = self.toc_items[self.current_toc_index]
                if toc_item[self.tr("chapter_index")] == self.current_chapter_index:
                    toc_index = self.current_toc_index
                    if self.tr("href") in toc_item and self.tr("#") in toc_item[self.tr("href")]:
                        anchor = toc_item[self.tr("href")].split(self.tr("#"))[1]

            if toc_index < 0:
                for idx, toc_item in enumerate(self.toc_items):
                    if toc_item[self.tr("chapter_index")] == self.current_chapter_index:
                        toc_index = idx
                        if self.tr("href") in toc_item and self.tr("#") in toc_item[self.tr("href")]:
                            anchor = toc_item[self.tr("href")].split(self.tr("#"))[1]
                        break

            scroll_script = self.tr("")
            if anchor:
                scroll_script = self.tr("\n                <script>\n                window.addEventListener('load', function() %1');\n                    if (!element) %2\"]');\n                    }}\n                    if (!element) %3\"]');\n                    }}\n                    if (element) %4});\n                            element.style.backgroundColor = '#ffff99';\n                            setTimeout(function() %5}, 2000);\n                        }}, 100);\n                    }}\n                }});\n                </script>\n                ").arg({
                    var element = document.getElementById('{anchor).arg({
                        element = document.querySelector('[name="{anchor).arg({
                        element = document.querySelector('[epub\\\\).arg({
                        setTimeout(function() {{
                            element.scrollIntoView({{behavior).arg({
                                element.style.backgroundColor = '';)

            styled_content = self.tr("\n            <html>\n            <head>\n                <meta charset=\"UTF-8\">\n                %1\n            </head>\n            <body>\n                %2\n            </body>\n            </html>\n            ").arg(scroll_script).arg(html_content)

            self.web_view.setHtml(styled_content, QUrl(self.tr("epub://epub/")))
            self.stacked_viewer.setCurrentWidget(self.web_view)

            if toc_index >= 0:
                self.toc_list.blockSignals(True)
                self.chapter_combo.blockSignals(True)
                self.toc_list.setCurrentRow(toc_index)
                self.chapter_combo.setCurrentIndex(toc_index)
                self.toc_list.blockSignals(False)
                self.chapter_combo.blockSignals(False)

        elif self.current_doc_type == self.tr("pdf"):
            self.stacked_viewer.setCurrentWidget(self.pdf_viewer)
            self.pdf_viewer.go_to_page(self.current_chapter_index)

        self.update_position_label()

    def update_position_label(self):
        if self.chapters:
            total = len(self.chapters)
            current = self.current_chapter_index + 1
            self.position_label.setText(
                self.tr("<b>%1</b> par <b>%2</b> - Chapitre: %3 / %4").arg(self.book_title).arg(self.book_author).arg(current).arg(total)
            )

    def load_chapter_from_list(self, item):
        """Charger un chapitre depuis la liste de la table des matières."""
        index = self.toc_list.currentRow()
        if index < 0:
            return

        if self.current_doc_type == self.tr("epub") and index < len(self.toc_items):
            self.current_toc_index = index
            self.current_chapter_index = self.toc_items[index][self.tr("chapter_index")]
            self.load_current_chapter()
        elif self.current_doc_type == self.tr("pdf"):
            if self.pdf_toc:
                page_num = self.pdf_toc[index][2] - 1
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index
            self.load_current_chapter()
            self.chapter_combo.blockSignals(True)
            self.chapter_combo.setCurrentIndex(index)
            self.chapter_combo.blockSignals(False)

    def load_chapter_from_combo(self, index):
        """Charger un chapitre depuis le combo box."""
        if index < 0:
            return

        if self.current_doc_type == self.tr("epub") and index < len(self.toc_items):
            self.current_toc_index = index
            self.current_chapter_index = self.toc_items[index][self.tr("chapter_index")]
            self.load_current_chapter()
        elif self.current_doc_type == self.tr("pdf"):
            if self.pdf_toc:
                page_num = self.pdf_toc[index][2] - 1
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index
            self.load_current_chapter()
            self.toc_list.blockSignals(True)
            self.toc_list.setCurrentRow(index)
            self.toc_list.blockSignals(False)

    def previous_chapter(self):
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.current_toc_index = None
            self.load_current_chapter()

    def next_chapter(self):
        if self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            self.current_toc_index = None
            self.load_current_chapter()

    def first_chapter(self):
        if self.chapters:
            self.current_chapter_index = 0
            self.current_toc_index = None
            self.load_current_chapter()

    def last_chapter(self):
        if self.chapters:
            self.current_chapter_index = len(self.chapters) - 1
            self.current_toc_index = None
            self.load_current_chapter()

    def search_in_text(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.clear_search()
            return

        self.search_text = search_text
        self.search_results = []
        self.current_search_index = -1

        if self.current_doc_type == self.tr("epub"):
            for chapter_index, chapter in enumerate(self.chapters):
                content = chapter.get_content().decode(self.tr("utf-8"), errors=self.tr("ignore"))
                for match in re.finditer(
                    re.escape(search_text), content, re.IGNORECASE
                ):
                    self.search_results.append(
                        {self.tr("chapter_index"): chapter_index, self.tr("text_position"): match.start()}
                    )

            if self.search_results:
                QMessageBox.information(
                    self,
                    self.tr("Recherche"),
                    self.tr("%1 occurrence(s) trouvée(s) dans l'ensemble du document.").arg(len(self.search_results)),
                )
                self.find_next()
            else:
                QMessageBox.warning(
                    self, self.tr("Recherche"), self.tr("Aucune occurrence trouvée dans le document.")
                )
        elif self.current_doc_type == self.tr("pdf"):
            self.pdf_viewer.find_text(search_text, new_search=True)

    def find_next(self):
        if not self.search_text or (
            self.current_doc_type == self.tr("epub") and not self.search_results
        ):
            return

        if self.current_doc_type == self.tr("epub"):
            self.current_search_index = (self.current_search_index + 1) % len(
                self.search_results
            )
            result = self.search_results[self.current_search_index]
            if result[self.tr("chapter_index")] != self.current_chapter_index:
                self.current_chapter_index = result[self.tr("chapter_index")]
                self.current_toc_index = None
                self.load_current_chapter()

            def highlight_and_scroll():
                self.web_page.findText(self.search_text)
                content_length = len(
                    self.chapters[self.current_chapter_index].get_content()
                )
                if content_length > 0:
                    scroll_pos = (result[self.tr("text_position")] / content_length) * 100
                    js_scroll = self.tr("\n                    document.documentElement.scrollTop = (document.documentElement.scrollHeight * %1);\n                    ").arg(scroll_pos / 100)
                    self.web_page.runJavaScript(js_scroll)

            QTimer.singleShot(500, highlight_and_scroll)
        elif self.current_doc_type == self.tr("pdf"):
            self.pdf_viewer.navigate_search_results(1)

    def find_previous(self):
        if not self.search_text or (
            self.current_doc_type == self.tr("epub") and not self.search_results
        ):
            return

        if self.current_doc_type == self.tr("epub"):
            self.current_search_index = (self.current_search_index - 1) % len(
                self.search_results
            )
            result = self.search_results[self.current_search_index]
            if result[self.tr("chapter_index")] != self.current_chapter_index:
                self.current_chapter_index = result[self.tr("chapter_index")]
                self.current_toc_index = None
                self.load_current_chapter()

            def highlight_and_scroll():
                self.web_page.findText(self.search_text, QWebEnginePage.FindBackward)
                content_length = len(
                    self.chapters[self.current_chapter_index].get_content()
                )
                if content_length > 0:
                    scroll_pos = (result[self.tr("text_position")] / content_length) * 100
                    js_scroll = self.tr("\n                    document.documentElement.scrollTop = (document.documentElement.scrollHeight * %1);\n                    ").arg(scroll_pos / 100)
                    self.web_page.runJavaScript(js_scroll)

            QTimer.singleShot(500, highlight_and_scroll)
        elif self.current_doc_type == self.tr("pdf"):
            self.pdf_viewer.navigate_search_results(-1)

    def clear_search(self):
        self.search_input.clear()
        self.search_text = self.tr("")
        self.search_results = []
        self.current_search_index = -1
        if self.current_doc_type == self.tr("epub"):
            self.web_page.findText(self.tr(""))
        elif self.current_doc_type == self.tr("pdf"):
            self.pdf_viewer.clear_search()

    def on_pdf_page_changed(self, page_num):
        """Slot appelé lorsque le PdfViewer change de page (ex: via la recherche)."""
        if self.current_doc_type != self.tr("pdf"):
            return

        if self.current_chapter_index != page_num:
            self.current_chapter_index = page_num
            toc_index_to_select = -1
            if self.pdf_toc:
                for i, entry in reversed(list(enumerate(self.pdf_toc))):
                    if entry[2] - 1 <= page_num:
                        toc_index_to_select = i
                        break
            else:
                toc_index_to_select = page_num

            self.toc_list.blockSignals(True)
            self.chapter_combo.blockSignals(True)
            if 0 <= toc_index_to_select < self.toc_list.count():
                self.toc_list.setCurrentRow(toc_index_to_select)
                self.chapter_combo.setCurrentIndex(toc_index_to_select)
            self.toc_list.blockSignals(False)
            self.chapter_combo.blockSignals(False)

            # Ne pas appeler load_current_chapter ici pour éviter de réinitialiser la recherche
            # L'affichage est déjà géré par PdfViewer

    def on_pdf_document_loaded(self, success, title, author, toc, page_count):
        """Slot appelé lorsque le document PDF est chargé via le signal document_loaded."""
        if success:
            self.book_title = title
            self.book_author = author
            self.pdf_toc = toc
            self.chapters = list(range(page_count))

            self.toc_list.clear()
            self.chapter_combo.clear()
            if toc:
                for entry in toc:
                    if len(entry) >= 3:
                        entry_level, entry_title, page_num = entry[:3]
                    elif len(entry) == 2:
                        entry_level, entry_title = entry
                        page_num = 1
                    else:
                        continue
                    try:
                        level_int = int(entry_level)
                    except (ValueError, TypeError):
                        level_int = 0
                    indent = self.tr("  ") * level_int
                    self.toc_list.addItem(QListWidgetItem(self.tr("%1%2").arg(indent).arg(entry_title)))
                    self.chapter_combo.addItem(self.tr("%1%2").arg(indent).arg(entry_title))
            else:
                for i in range(page_count):
                    self.toc_list.addItem(QListWidgetItem(self.tr("Page %1").arg(i + 1)))
                    self.chapter_combo.addItem(self.tr("Page %1").arg(i + 1))

            self.enable_navigation(True)
            self.load_current_chapter()
        else:
            self.show_error(self.tr("<h1>Échec du chargement du PDF</h1>"))

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
        return self.book is not None or (
            self.pdf_viewer and self.pdf_viewer.has_document()
        )

    def toggle_toc_visibility(self):
        """Affiche ou masque le panneau de la table des matières."""
        if self.toc_widget.isVisible():
            self.toc_widget.hide()
            self.toggle_toc_btn.setText(self.tr("▶"))
        else:
            self.toc_widget.show()
            self.toggle_toc_btn.setText(self.tr("◀"))

    def sync_toc_from_scroll(self, scroll_y):
        """Synchronise la TOC en fonction de la position de défilement de l'EPUB."""
        if self.current_doc_type != self.tr("epub") or not self.chapters:
            return

        js_script = """
        (function() {
            let elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            let top_element_id = null;
            let min_offset = Infinity;

            for (let i = 0; i < elements.length; i++) {
                let elem = elements[i];
                if (!elem.id) {
                    elem.id = 'bn_autoid_' + i;
                }
                let rect = elem.getBoundingClientRect();
                if (rect.top >= 0 and rect.top < min_offset) {
                    min_offset = rect.top;
                    top_element_id = elem.id;
                }
            }
            return top_element_id;
        })();
        """

        def find_toc_entry(element_id):
            if not element_id:
                return

            anchor = element_id
            best_match_index = -1
            for i, toc_item in reversed(list(enumerate(self.toc_items))):
                if toc_item[self.tr("chapter_index")] == self.current_chapter_index:
                    href_anchor = toc_item.get(self.tr("href"), self.tr("")).split(self.tr("#"))[-1]
                    if href_anchor and href_anchor <= anchor:
                        best_match_index = i
                        break
            if (
                best_match_index != -1
                and self.toc_list.currentRow() != best_match_index
            ):
                self.toc_list.blockSignals(True)
                self.chapter_combo.blockSignals(True)
                self.toc_list.setCurrentRow(best_match_index)
                self.chapter_combo.setCurrentIndex(best_match_index)
                self.toc_list.blockSignals(False)
                self.chapter_combo.blockSignals(False)

        self.web_page.runJavaScript(js_script, find_toc_entry)

    def closeEvent(self, event):
        """
        V3.3.8 - S'assure que la page web est correctement libérée pour éviter
        l'erreur "WebEnginePage still not deleted".
        """
        self.web_view.setPage(None)
        self.web_view.deleteLater()
        if self.web_view:
            self.web_view.setPage(None)
            self.web_view.deleteLater()
        super().closeEvent(event)

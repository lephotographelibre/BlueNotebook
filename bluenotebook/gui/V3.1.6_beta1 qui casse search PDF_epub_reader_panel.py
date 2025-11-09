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
    QApplication,  # Ajout pour QApplication.clipboard()
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
from PyQt5.QtWebEngineWidgets import (
    QWebEngineView,
    QWebEnginePage,
    QWebEngineProfile,
    QWebEngineContextMenuData,
)
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlRequestJob
from PyQt5.QtCore import Qt, QUrl, QBuffer, QIODevice, QByteArray, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap

# Ajoutez ces imports en haut du fichier
from PyQt5.QtWidgets import QFileDialog, QMenu, QAction
from PyQt5.QtWebEngineWidgets import QWebEngineContextMenuData
from PIL import Image  # Nécessaire pour la sauvegarde d'image
import io  # Nécessaire pour la sauvegarde d'image
from pathlib import Path  # Nécessaire pour la sauvegarde d'image


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
            save_image_action = QAction("Sauvegarder l'image", self)
            save_image_action.triggered.connect(lambda: self.save_image(context_data))
            menu.addAction(save_image_action)

            copy_image_action = QAction("Copier l'image", self)
            copy_image_action.triggered.connect(lambda: self.copy_image(context_data))
            menu.addAction(copy_image_action)

            copy_url_action = QAction("Copier l'adresse de l'image", self)
            copy_url_action.triggered.connect(lambda: self.copy_image_url(context_data))
            menu.addAction(copy_url_action)
        else:
            # Actions personnalisées pour le texte avec libellés en français
            copy_text_action = QAction("Copier le texte sélectionné", self)
            # Vérifier si du texte est sélectionné pour activer l'action
            copy_text_action.setEnabled(self.page().selectedText().strip() != "")
            copy_text_action.triggered.connect(
                lambda: self.page().triggerAction(QWebEnginePage.Copy)
            )
            menu.addAction(copy_text_action)

            select_all_text_action = QAction("Tout sélectionner", self)
            select_all_text_action.triggered.connect(
                lambda: self.page().triggerAction(QWebEnginePage.SelectAll)
            )
            menu.addAction(select_all_text_action)

            # Ajouter un séparateur avant les actions standard si elles sont nécessaires
            menu.addSeparator()

        menu.exec_(event.globalPos())

    def save_image(self, context_data):
        """Sauvegarde l'image sur le disque."""
        image_url = context_data.mediaUrl().toString()

        if not image_url:
            QMessageBox.warning(
                self, "Erreur", "Impossible de récupérer l'URL de l'image"
            )
            return

        # Extraire le chemin de l'image depuis l'URL epub://
        if image_url.startswith("epub://epub/"):
            image_path = image_url.replace("epub://epub/", "")

            # Récupérer le contenu de l'image depuis le gestionnaire de schéma
            scheme_handler = self.epub_reader_panel.scheme_handler
            if image_path in scheme_handler.resources:
                image_data = scheme_handler.resources[image_path]

                # Changer l'extension du nom de fichier suggéré en .jpg
                base_name = os.path.splitext(os.path.basename(image_path))[0]
                suggested_filename = f"{base_name}.jpg"

                # Récupérer le dernier répertoire de sauvegarde utilisé
                last_save_dir = self.epub_reader_panel.settings_manager.get(
                    "reader.last_image_save_directory", str(Path.home())
                )
                default_path = os.path.join(last_save_dir, suggested_filename)

                # Demander à l'utilisateur où sauvegarder
                file_filter = "Image JPEG (*.jpg)"
                save_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Sauvegarder l'image",
                    default_path,
                    file_filter,
                )

                if save_path:
                    try:
                        # Utiliser Pillow pour convertir l'image en JPG
                        img = Image.open(io.BytesIO(image_data))

                        # Convertir en mode RGB si nécessaire (pour les PNG avec transparence, etc.)
                        if img.mode != "RGB":
                            img = img.convert("RGB")

                        img.save(save_path, "JPEG", quality=90)

                        # Mémoriser le répertoire pour la prochaine fois
                        new_save_dir = os.path.dirname(save_path)
                        self.epub_reader_panel.settings_manager.set(
                            "reader.last_image_save_directory", new_save_dir
                        )
                        self.epub_reader_panel.settings_manager.save_settings()

                        QMessageBox.information(
                            self, "Succès", f"Image sauvegardée dans:\n{save_path}"
                        )
                    except Exception as e:
                        QMessageBox.critical(
                            self,
                            "Erreur",
                            f"Impossible de convertir ou sauvegarder l'image:\n{str(e)}",
                        )
            else:
                QMessageBox.warning(
                    self, "Erreur", "Image introuvable dans les ressources EPUB"
                )

    def copy_image(self, context_data):
        """Copie l'image dans le presse-papiers."""
        image_url = context_data.mediaUrl().toString()

        if not image_url or not image_url.startswith("epub://epub/"):
            return

        image_path = image_url.replace("epub://epub/", "")
        scheme_handler = self.epub_reader_panel.scheme_handler

        if image_path in scheme_handler.resources:
            image_data = scheme_handler.resources[image_path]

            # Créer un QPixmap depuis les données
            pixmap = QPixmap()
            pixmap.loadFromData(QByteArray(image_data))

            if not pixmap.isNull():
                clipboard = QApplication.clipboard()
                clipboard.setPixmap(pixmap)

                # Optionnel: afficher une notification
                self.epub_reader_panel.position_label.setText(
                    "Image copiée dans le presse-papiers"
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
        """Gère les événements de la molette de la souris."""
        # Si ce n'est pas un EPUB, passer l'événement au parent et ne rien faire d'autre.
        if self.epub_reader_panel.current_doc_type != "epub":
            super().wheelEvent(event)
            return

        delta = event.angleDelta().y()

        def handle_scroll_check(at_end):
            if at_end:
                if delta < 0:  # Défilement vers le bas
                    self.epub_reader_panel.next_chapter()
                elif delta > 0:  # Défilement vers le haut
                    self.epub_reader_panel.previous_chapter()

        if delta < 0:  # Défilement vers le bas
            self.page().runJavaScript(
                "window.scrollY + window.innerHeight >= document.body.scrollHeight - 2",
                handle_scroll_check,
            )
        elif delta > 0:  # Défilement vers le haut
            self.page().runJavaScript("window.scrollY === 0", handle_scroll_check)

        super().wheelEvent(event)

    def _on_scroll_changed(self, pos):
        self.scroll_position_changed.emit(int(pos.y()))


class EpubReaderPanel(QWidget):
    """Widget pour afficher et naviguer dans un fichier EPUB ou PDF."""

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

        # Ajout pour le lecteur PDF
        self.pdf_viewer = None
        self.current_doc_type = None  # 'epub' ou 'pdf'
        self.pdf_toc = []

        self.settings_manager = settings_manager
        # Initialiser le gestionnaire de schéma et le profil WebEngine
        self.scheme_handler = EpubSchemeHandler()
        self.profile = QWebEngineProfile()  # Utiliser un profil non-défaut
        self.profile.installUrlSchemeHandler(b"epub", self.scheme_handler)

        self.search_results = (
            []
        )  # Liste des résultats : [{'chapter_index': int, 'text_position': int}, ...]
        self.current_search_index = -1

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

        # Panneau Contenu avec QStackedWidget pour basculer entre EPUB et PDF
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

        # Barre de recherche
        search_layout = QHBoxLayout()
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

        reader_layout.addWidget(self.stacked_viewer, 1)

        # Barre de navigation
        nav_layout = QHBoxLayout()
        self.first_chapter_btn = QPushButton("◀◀ Début")
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
        self.last_chapter_btn.clicked.connect(self.last_chapter)
        nav_layout.addWidget(self.last_chapter_btn)
        reader_layout.addLayout(nav_layout)

        self.position_label = QLabel("Chapitre: - / -")
        reader_layout.addWidget(self.position_label, 0, Qt.AlignCenter)

        splitter.addWidget(reader_content_widget)
        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter, 1)

        self.enable_navigation(False)

    def load_document(self, filepath):
        """Charge un document EPUB ou PDF."""
        if not filepath or not os.path.exists(filepath):
            self.show_error("<h1>Fichier non trouvé</h1>")
            return

        # Vérifier le type de fichier
        mime_type, _ = mimetypes.guess_type(filepath)
        file_ext = os.path.splitext(filepath)[1].lower()

        if mime_type == "application/pdf" or file_ext == ".pdf":
            try:
                self.current_doc_type = "pdf"
                self.pdf_viewer.load_document(filepath)
                self.current_chapter_index = 0
            except Exception as e:
                self.show_error(f"<h1>Erreur lors du chargement du PDF : {str(e)}</h1>")
            return

        # Gestion des EPUB
        try:
            self.current_doc_type = "epub"
            self.book = epub.read_epub(filepath)
            self.scheme_handler.set_book(self.book)

            # Extraire le titre et l'auteur
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

            # Créer un mapping des items
            self.items_map = {}
            self.chapters = []
            self.toc_items = []
            self.current_chapter_index = 0
            self.current_toc_index = None

            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    self.items_map[item.get_name().replace("\\", "/")] = item

            # Parser la table des matières avec matching exact
            if self.book.toc:
                self._parse_toc(self.book.toc)

            # Ajouter les items à la liste et au combo
            self.toc_list.clear()
            self.chapter_combo.clear()

            for toc_item in self.toc_items:
                title = toc_item["title"]
                level = toc_item["level"]
                indent = "  " * level
                self.toc_list.addItem(QListWidgetItem(f"{indent}{title}"))
                self.chapter_combo.addItem(f"{indent}{title}")

            # Charger les chapitres depuis le spine (si TOC vide)
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
                                    "title": title,
                                    "item": doc_item,
                                    "chapter_index": self.chapters.index(doc_item),
                                    "level": 0,
                                    "href": doc_item.get_name(),
                                }
                            )
                            self.toc_list.addItem(QListWidgetItem(title))
                            self.chapter_combo.addItem(title)

            # Activer la navigation
            if self.chapters:
                self.enable_navigation(True)
                self.stacked_viewer.setCurrentWidget(self.web_view)
                self.load_current_chapter()

            # Debug : Lister les chapitres et TOC
            # print(f"Chapters found: {len(self.chapters)}")
            # for i, chap in enumerate(self.chapters):
            #     print(f"Index {i}: {chap.get_name()}")
            # for toc in self.toc_items:
            #     print(
            #         f"TOC: {toc['title']} -> index {toc['chapter_index']} href {toc['href']}"
            #     )

        except Exception as e:
            self.show_error(f"<h1>Erreur lors du chargement de l'EPUB : {str(e)}</h1>")

    def _parse_toc(self, toc, level=0):
        """Parser récursivement la table des matières avec matching exact."""
        for item in toc:
            if isinstance(item, tuple):
                if hasattr(item[0], "title") and hasattr(item[0], "href"):
                    title = item[0].title
                    href = item[0].href
                    clean_href = href.split("#")[0]
                    clean_href = os.path.normpath(clean_href.replace("\\", "/"))
                    item_found = None
                    # Tri par longueur décroissante pour éviter les matchs ambigus
                    for key in sorted(self.items_map.keys(), key=len, reverse=True):
                        norm_key = os.path.normpath(key.replace("\\", "/"))
                        if clean_href == norm_key:
                            item_found = self.items_map[key]
                            # print(f"Matched {clean_href} to key {norm_key}")
                            break
                    if item_found:
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)
                        chapter_index = self.chapters.index(item_found)
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
                if len(item) > 1 and isinstance(item[1], list):
                    self._parse_toc(item[1], level + 1)

            elif isinstance(item, list):
                self._parse_toc(item, level)

            else:
                if hasattr(item, "title"):
                    title = item.title
                else:
                    title = str(item)

                href = None
                if hasattr(item, "href"):
                    href = item.href

                if href:
                    clean_href = href.split("#")[0]
                    clean_href = os.path.normpath(clean_href.replace("\\", "/"))
                    item_found = None
                    for key in sorted(self.items_map.keys(), key=len, reverse=True):
                        norm_key = os.path.normpath(key.replace("\\", "/"))
                        if clean_href == norm_key:
                            item_found = self.items_map[key]
                            # print(f"Matched {clean_href} to key {norm_key}")
                            break
                    if item_found:
                        if item_found not in self.chapters:
                            self.chapters.append(item_found)
                        chapter_index = self.chapters.index(item_found)
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
        """Charge le chapitre actuel dans la vue web ou PDF."""
        if not self.chapters:
            return

        if self.current_doc_type == "epub":
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
                # print(f"Préparation scroll vers l'ancre: {anchor}")
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
            self.stacked_viewer.setCurrentWidget(self.web_view)

            if toc_index >= 0:
                self.toc_list.blockSignals(True)
                self.chapter_combo.blockSignals(True)
                self.toc_list.setCurrentRow(toc_index)
                self.chapter_combo.setCurrentIndex(toc_index)
                self.toc_list.blockSignals(False)
                self.chapter_combo.blockSignals(False)

        elif self.current_doc_type == "pdf":
            self.pdf_viewer.go_to_page(self.current_chapter_index)
            self.stacked_viewer.setCurrentWidget(self.pdf_viewer)

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
            self.current_toc_index = index
            self.current_chapter_index = self.toc_items[index]["chapter_index"]
            toc_item = self.toc_items[index]
            # print(
            #     f"Navigation TOC: {toc_item['title']} -> chapitre {self.current_chapter_index}"
            # )
            # if "href" in toc_item:
            #     print(f"  href: {toc_item['href']}")
            self.load_current_chapter()
        elif self.current_doc_type == "pdf":
            if self.pdf_toc:
                page_num = self.pdf_toc[index][2] - 1  # PyMuPDF TOC est 1-based
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index
            self.load_current_chapter()
            self.chapter_combo.blockSignals(True)
            self.chapter_combo.setCurrentIndex(index)
            self.chapter_combo.blockSignals(False)
            # print(f"Navigation PDF TOC: page {self.current_chapter_index + 1}")

    def load_chapter_from_combo(self, index):
        """Charger un chapitre depuis le combo box."""
        if index < 0:
            return

        if self.current_doc_type == "epub" and index < len(self.toc_items):
            self.current_toc_index = index
            self.current_chapter_index = self.toc_items[index]["chapter_index"]
            toc_item = self.toc_items[index]
            # print(
            #     f"Navigation combo: {toc_item['title']} -> chapitre {self.current_chapter_index}"
            # )
            # if "href" in toc_item:
            #     print(f"  href: {toc_item['href']}")
            self.load_current_chapter()
        elif self.current_doc_type == "pdf":
            if self.pdf_toc:
                page_num = self.pdf_toc[index][2] - 1
                self.current_chapter_index = page_num
            else:
                self.current_chapter_index = index
            self.load_current_chapter()
            self.toc_list.blockSignals(True)
            self.toc_list.setCurrentRow(index)
            self.toc_list.blockSignals(False)
            # print(f"Navigation PDF combo: page {self.current_chapter_index + 1}")

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
            return

        self.search_text = search_text
        self.search_results = []
        self.current_search_index = -1

        if self.current_doc_type == "epub":
            # Recherche globale sur tous les chapitres
            for chapter_index, chapter in enumerate(self.chapters):
                content = chapter.get_content().decode("utf-8", errors="ignore")
                # Trouver toutes les positions (insensible à la casse)
                for match in re.finditer(
                    re.escape(search_text), content, re.IGNORECASE
                ):
                    self.search_results.append(
                        {
                            "chapter_index": chapter_index,
                            "text_position": match.start(),  # Position pour approximer le scroll
                        }
                    )

            if self.search_results:
                QMessageBox.information(
                    self,
                    "Recherche",
                    f"{len(self.search_results)} occurrence(s) trouvée(s) dans l'ensemble du document.",
                )
                self.find_next()  # Aller à la première occurrence
            else:
                QMessageBox.warning(
                    self, "Recherche", "Aucune occurrence trouvée dans le document."
                )
        elif self.current_doc_type == "pdf":
            self.pdf_viewer.find_text(search_text, new_search=True)

    def find_next(self):
        if not self.search_text or not self.search_results:
            return

        if self.current_doc_type == "epub":
            self.current_search_index = (self.current_search_index + 1) % len(
                self.search_results
            )
            result = self.search_results[self.current_search_index]
            if result["chapter_index"] != self.current_chapter_index:
                self.current_chapter_index = result["chapter_index"]
                self.current_toc_index = None  # Réinitialiser TOC si besoin
                self.load_current_chapter()

            # Une fois le chapitre chargé, surligner et scroller
            def highlight_and_scroll():
                self.web_page.findText(
                    self.search_text
                )  # Surligne la première occurrence
                # Script JS pour scroller vers l'occurrence approximative (basé sur position)
                content_length = len(
                    self.chapters[self.current_chapter_index].get_content()
                )
                if content_length > 0:
                    scroll_pos = (result["text_position"] / content_length) * 100
                    js_scroll = f"""
                    document.documentElement.scrollTop = (document.documentElement.scrollHeight * {scroll_pos / 100});
                    """
                    self.web_page.runJavaScript(js_scroll)

            # Attendre que la page soit chargée
            QTimer.singleShot(500, highlight_and_scroll)  # Délai empirique
        elif self.current_doc_type == "pdf":
            self.pdf_viewer.navigate_search_results(1)

    def find_previous(self):
        if not self.search_text or not self.search_results:
            return

        if self.current_doc_type == "epub":
            self.current_search_index = (self.current_search_index - 1) % len(
                self.search_results
            )
            result = self.search_results[self.current_search_index]
            if result["chapter_index"] != self.current_chapter_index:
                self.current_chapter_index = result["chapter_index"]
                self.current_toc_index = None
                self.load_current_chapter()

            # Une fois le chapitre chargé, surligner et scroller
            def highlight_and_scroll():
                self.web_page.findText(self.search_text, QWebEnginePage.FindBackward)
                # Script JS pour scroller vers l'occurrence approximative (basé sur position)
                content_length = len(
                    self.chapters[self.current_chapter_index].get_content()
                )
                if content_length > 0:
                    scroll_pos = (result["text_position"] / content_length) * 100
                    js_scroll = f"""
                    document.documentElement.scrollTop = (document.documentElement.scrollHeight * {scroll_pos / 100});
                    """
                    self.web_page.runJavaScript(js_scroll)

            # Attendre que la page soit chargée
            QTimer.singleShot(500, highlight_and_scroll)  # Délai empirique
        elif self.current_doc_type == "pdf":
            self.pdf_viewer.navigate_search_results(-1)

    def clear_search(self):
        self.search_input.clear()
        self.search_text = ""
        self.search_results = []
        self.current_search_index = -1
        if self.current_doc_type == "epub":
            self.web_page.findText("")
        elif self.current_doc_type == "pdf":
            self.pdf_viewer.clear_search()

    def on_pdf_page_changed(self, page_num):
        """Slot appelé lorsque le PdfViewer change de page (ex: via la recherche)."""
        if self.current_chapter_index != page_num:
            # Mettre à jour l'index du chapitre/page actuel
            self.current_chapter_index = page_num

            # Trouver l'index correspondant dans la TOC
            toc_index_to_select = -1
            if self.pdf_toc:
                # Chercher le chapitre qui commence à cette page ou juste avant
                for i, entry in reversed(list(enumerate(self.pdf_toc))):
                    if entry[2] - 1 <= page_num:
                        toc_index_to_select = i
                        break
            else:
                # Si pas de TOC, l'index est simplement le numéro de page
                toc_index_to_select = page_num

            # Mettre à jour l'interface utilisateur (TOC et ComboBox)
            self.toc_list.blockSignals(True)
            self.chapter_combo.blockSignals(True)
            if 0 <= toc_index_to_select < self.toc_list.count():
                self.toc_list.setCurrentRow(toc_index_to_select)
                self.chapter_combo.setCurrentIndex(toc_index_to_select)
            self.toc_list.blockSignals(False)
            self.chapter_combo.blockSignals(False)
            self.load_current_chapter()

    def on_pdf_document_loaded(self, success, title, author, toc, page_count):
        """Slot appelé lorsque le document PDF est chargé via le signal document_loaded."""
        if success:
            self.book_title = title
            self.book_author = author
            self.pdf_toc = toc
            self.chapters = list(range(page_count))  # Pages comme chapitres

            # Mettre à jour la TOC et le combo
            self.toc_list.clear()
            self.chapter_combo.clear()
            # print(f"TOC brute: {toc}")  # Trace pour déboguer la structure de la TOC
            if toc:
                for entry in toc:
                    # Vérifier la structure de l'entrée
                    if len(entry) >= 3:
                        entry_level, entry_title, page_num = entry[
                            :3
                        ]  # Corriger l'ordre : level, title, page_num
                    elif len(entry) == 2:
                        # Cas où level est manquant
                        entry_level, entry_title = entry
                        page_num = 1  # Page par défaut si absente
                        print(
                            f"Entrée TOC avec 2 éléments: {entry}, page_num défini à 1"
                        )
                    else:
                        print(f"Entrée TOC invalide: {entry}")
                        continue

                    # Convertir level en entier
                    try:
                        level_int = int(entry_level)
                    except (ValueError, TypeError):
                        print(
                            f"Erreur de conversion de level '{entry_level}' en entier, utilisation de 0"
                        )
                        level_int = 0  # Niveau par défaut si non numérique
                    indent = "  " * level_int
                    self.toc_list.addItem(QListWidgetItem(f"{indent}{entry_title}"))
                    self.chapter_combo.addItem(f"{indent}{entry_title}")
            else:
                # Si aucune TOC, afficher les pages
                for i in range(page_count):
                    self.toc_list.addItem(QListWidgetItem(f"Page {i + 1}"))
                    self.chapter_combo.addItem(f"Page {i + 1}")

            self.enable_navigation(True)
            self.load_current_chapter()
            print(
                f"📖 PDF chargé avec succès: {page_count} pages, TOC: {len(toc)} éléments"
            )
        else:
            self.show_error("<h1>Échec du chargement du PDF</h1>")

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
            self.toggle_toc_btn.setText("▶")
        else:
            self.toc_widget.show()
            self.toggle_toc_btn.setText("◀")

    def sync_toc_from_scroll(self, scroll_y):
        """Synchronise la TOC en fonction de la position de défilement de l'EPUB."""
        if self.current_doc_type != "epub" or not self.chapters:
            return

        # Script JS pour trouver l'élément de titre le plus haut visible dans la fenêtre
        js_script = """
        (function() {
            let elements = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            let top_element_id = null;
            let min_offset = Infinity;

            for (let i = 0; i < elements.length; i++) {
                let elem = elements[i];
                if (!elem.id) { // Assigner un ID unique si absent
                    elem.id = 'bn_autoid_' + i;
                }
                let rect = elem.getBoundingClientRect();
                // Chercher l'élément dont le haut est le plus proche de 0 (le haut de la vue)
                if (rect.top >= 0 && rect.top < min_offset) {
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

            # Extraire l'ancre de l'ID
            anchor = element_id

            # Trouver l'entrée correspondante dans la TOC
            best_match_index = -1
            # On parcourt la TOC à l'envers pour trouver le dernier élément qui correspond
            for i, toc_item in reversed(list(enumerate(self.toc_items))):
                # On ne considère que les entrées du chapitre actuel
                if toc_item["chapter_index"] == self.current_chapter_index:
                    href_anchor = toc_item.get("href", "").split("#")[-1]
                    # Si l'ancre de la TOC est vide, on ne peut pas la faire correspondre
                    if not href_anchor:
                        continue
                    # On cherche l'ancre la plus proche qui est avant ou égale à l'élément visible
                    if href_anchor <= anchor:
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

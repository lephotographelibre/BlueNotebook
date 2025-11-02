from PyQt5.QtWidgets import (
    QMainWindow,
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QListWidget,
    QSplitter,
    QLineEdit,
    QLabel,
    QFileDialog,
    QMessageBox,
    QComboBox,
    QToolBar,
    QAction,
    QDockWidget,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWebEngineCore import QWebEngineUrlSchemeHandler, QWebEngineUrlScheme
from PyQt5.QtCore import Qt, QUrl, QBuffer, QIODevice, QByteArray
from PyQt5.QtGui import QIcon, QKeySequence, QPixmap
from ebooklib import epub
import ebooklib
import sys
import os
import base64


class EpubSchemeHandler(QWebEngineUrlSchemeHandler):
    """Gestionnaire de schéma personnalisé pour charger les ressources EPUB"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.book = None
        self.resources = {}

    def set_book(self, book):
        """Définir le livre EPUB et charger les ressources"""
        self.book = book
        self.resources = {}

        if self.book:
            # Charger toutes les ressources (images, CSS, etc.)
            for item in self.book.get_items():
                if item.get_type() in [
                    ebooklib.ITEM_IMAGE,
                    ebooklib.ITEM_STYLE,
                    ebooklib.ITEM_SCRIPT,
                    ebooklib.ITEM_FONT,
                ]:
                    # Stocker avec le nom de fichier comme clé
                    filename = item.get_name()
                    content = item.get_content()

                    # Normaliser les chemins (remplacer \ par /)
                    filename = filename.replace("\\", "/")

                    # Stocker avec le chemin complet
                    self.resources[filename] = content

                    # Stocker aussi avec juste le nom de base
                    basename = os.path.basename(filename)
                    if basename not in self.resources:
                        self.resources[basename] = content

                    # Stocker avec toutes les variations possibles du chemin
                    parts = filename.split("/")
                    for i in range(len(parts)):
                        partial_path = "/".join(parts[i:])
                        if partial_path not in self.resources:
                            self.resources[partial_path] = content

    def requestStarted(self, request):
        """Gérer les requêtes de ressources"""
        url = request.requestUrl()
        path = url.path()

        # Enlever le slash initial
        if path.startswith("/"):
            path = path[1:]

        # Normaliser le chemin
        path = path.replace("\\", "/")

        # Chercher la ressource
        content = None
        content_type = "application/octet-stream"

        # Essayer de trouver la ressource avec différentes stratégies
        if path in self.resources:
            content = self.resources[path]
        else:
            # Chercher dans les chemins possibles
            for key in self.resources.keys():
                # Comparaison exacte
                if key == path:
                    content = self.resources[key]
                    break
                # Le chemin se termine par la clé
                elif key.endswith(path):
                    content = self.resources[key]
                    break
                # La clé se termine par le chemin
                elif path.endswith(key):
                    content = self.resources[key]
                    break

        if content:
            # Déterminer le type MIME
            path_lower = path.lower()
            if path_lower.endswith((".jpg", ".jpeg")):
                content_type = "image/jpeg"
            elif path_lower.endswith(".png"):
                content_type = "image/png"
            elif path_lower.endswith(".gif"):
                content_type = "image/gif"
            elif path_lower.endswith(".svg"):
                content_type = "image/svg+xml"
            elif path_lower.endswith(".webp"):
                content_type = "image/webp"
            elif path_lower.endswith(".css"):
                content_type = "text/css"
            elif path_lower.endswith(".js"):
                content_type = "application/javascript"

            # Créer un buffer avec le contenu
            buffer = QBuffer(parent=self)
            buffer.setData(QByteArray(content))
            buffer.open(QIODevice.ReadOnly)

            request.reply(content_type.encode(), buffer)
        else:
            # Ressource non trouvée - renvoyer une réponse vide
            print(f"Ressource non trouvée: {path}")
            print(f"Toutes les ressources disponibles:")
            for key in sorted(self.resources.keys()):
                print(f"  - {key}")
            buffer = QBuffer(parent=self)
            buffer.setData(QByteArray())
            buffer.open(QIODevice.ReadOnly)
            request.reply(b"text/plain", buffer)


class WebEnginePage(QWebEnginePage):
    """Page personnalisée pour gérer la recherche"""

    def __init__(self, profile, parent=None):
        super().__init__(profile, parent)


class EpubReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.book = None
        self.current_chapter_index = 0
        self.chapters = []
        self.search_text = ""

        # Initialiser le gestionnaire de schéma personnalisé
        self.scheme_handler = EpubSchemeHandler()

        # Créer un profil personnalisé pour WebEngine
        self.profile = QWebEngineProfile.defaultProfile()
        self.profile.installUrlSchemeHandler(b"epub", self.scheme_handler)

        self.setWindowTitle("Lecteur EPUB")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()
        self.create_menu_bar()
        self.create_toolbar()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Barre d'informations du livre avec couverture
        info_layout = QHBoxLayout()

        # Label pour la couverture miniature
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(60, 80)
        self.cover_label.setScaledContents(True)
        self.cover_label.setStyleSheet(
            "border: 1px solid #ccc; background-color: #f0f0f0;"
        )
        info_layout.addWidget(self.cover_label)

        self.book_title_label = QLabel("Aucun livre chargé")
        self.book_title_label.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 5px;"
        )
        info_layout.addWidget(self.book_title_label)

        # Bouton pour voir la couverture en grand
        self.view_cover_btn = QPushButton("📖 Voir la couverture")
        self.view_cover_btn.clicked.connect(self.show_cover)
        self.view_cover_btn.setEnabled(False)
        info_layout.addWidget(self.view_cover_btn)

        info_layout.addStretch()
        main_layout.addLayout(info_layout)

        # Splitter pour diviser la table des matières et le contenu
        splitter = QSplitter(Qt.Horizontal)

        # Panel de gauche - Table des matières
        toc_widget = QWidget()
        toc_layout = QVBoxLayout()
        toc_widget.setLayout(toc_layout)

        toc_label = QLabel("Table des matières")
        toc_label.setStyleSheet("font-weight: bold; padding: 5px;")
        toc_layout.addWidget(toc_label)

        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.load_chapter_from_list)
        toc_layout.addWidget(self.toc_list)

        splitter.addWidget(toc_widget)

        # Panel de droite - Contenu du livre
        content_widget = QWidget()
        content_layout = QVBoxLayout()
        content_widget.setLayout(content_layout)

        # Barre de recherche
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Rechercher dans le livre...")
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

        content_layout.addLayout(search_layout)

        # WebView pour afficher le contenu
        self.web_view = QWebEngineView()
        self.web_page = WebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.web_page)
        content_layout.addWidget(self.web_view)

        # Barre de navigation
        nav_layout = QHBoxLayout()

        self.first_chapter_btn = QPushButton("⏮ Premier")
        self.first_chapter_btn.clicked.connect(self.first_chapter)
        nav_layout.addWidget(self.first_chapter_btn)

        self.prev_chapter_btn = QPushButton("◀ Chapitre précédent")
        self.prev_chapter_btn.clicked.connect(self.previous_chapter)
        nav_layout.addWidget(self.prev_chapter_btn)

        self.chapter_combo = QComboBox()
        self.chapter_combo.currentIndexChanged.connect(self.load_chapter_from_combo)
        nav_layout.addWidget(self.chapter_combo, 2)

        self.next_chapter_btn = QPushButton("Chapitre suivant ▶")
        self.next_chapter_btn.clicked.connect(self.next_chapter)
        nav_layout.addWidget(self.next_chapter_btn)

        self.last_chapter_btn = QPushButton("Dernier ⏭")
        self.last_chapter_btn.clicked.connect(self.last_chapter)
        nav_layout.addWidget(self.last_chapter_btn)

        content_layout.addLayout(nav_layout)

        # Informations de position
        position_layout = QHBoxLayout()
        self.position_label = QLabel("Chapitre: - / -")
        position_layout.addWidget(self.position_label)
        position_layout.addStretch()
        content_layout.addLayout(position_layout)

        splitter.addWidget(content_widget)

        # Définir les proportions du splitter
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Désactiver les boutons au démarrage
        self.enable_navigation(False)

    def create_menu_bar(self):
        """Créer la barre de menu"""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("Fichier")

        open_action = QAction("Ouvrir EPUB...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_epub_dialog)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        cover_action = QAction("Voir la couverture", self)
        cover_action.triggered.connect(self.show_cover)
        file_menu.addAction(cover_action)

        file_menu.addSeparator()

        quit_action = QAction("Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Navigation
        nav_menu = menubar.addMenu("Navigation")

        first_action = QAction("Premier chapitre", self)
        first_action.setShortcut("Ctrl+Home")
        first_action.triggered.connect(self.first_chapter)
        nav_menu.addAction(first_action)

        prev_action = QAction("Chapitre précédent", self)
        prev_action.setShortcut("Ctrl+Left")
        prev_action.triggered.connect(self.previous_chapter)
        nav_menu.addAction(prev_action)

        next_action = QAction("Chapitre suivant", self)
        next_action.setShortcut("Ctrl+Right")
        next_action.triggered.connect(self.next_chapter)
        nav_menu.addAction(next_action)

        last_action = QAction("Dernier chapitre", self)
        last_action.setShortcut("Ctrl+End")
        last_action.triggered.connect(self.last_chapter)
        nav_menu.addAction(last_action)

        # Menu Recherche
        search_menu = menubar.addMenu("Recherche")

        search_action = QAction("Rechercher...", self)
        search_action.setShortcut(QKeySequence.Find)
        search_action.triggered.connect(lambda: self.search_input.setFocus())
        search_menu.addAction(search_action)

        find_next_action = QAction("Occurrence suivante", self)
        find_next_action.setShortcut(QKeySequence.FindNext)
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)

        find_prev_action = QAction("Occurrence précédente", self)
        find_prev_action.setShortcut(QKeySequence.FindPrevious)
        find_prev_action.triggered.connect(self.find_previous)
        search_menu.addAction(find_prev_action)

    def create_toolbar(self):
        """Créer la barre d'outils"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)

        open_action = QAction("Ouvrir", self)
        open_action.triggered.connect(self.open_epub_dialog)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        toolbar.addAction("⏮", self.first_chapter)
        toolbar.addAction("◀", self.previous_chapter)
        toolbar.addAction("▶", self.next_chapter)
        toolbar.addAction("⏭", self.last_chapter)

    def open_epub_dialog(self):
        """Ouvrir un dialogue pour sélectionner un fichier EPUB"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Ouvrir un fichier EPUB",
            "",
            "Fichiers EPUB (*.epub);;Tous les fichiers (*.*)",
        )

        if file_path:
            self.load_epub(file_path)

    def load_epub(self, filepath):
        """Charger un fichier EPUB"""
        try:
            self.book = epub.read_epub(filepath)

            # Passer le livre au gestionnaire de schéma
            self.scheme_handler.set_book(self.book)

            # Récupérer les informations du livre
            title = self.book.get_metadata("DC", "title")
            if title:
                book_title = title[0][0]
                self.book_title_label.setText(f"📖 {book_title}")
                self.setWindowTitle(f"Lecteur EPUB - {book_title}")

            # Charger la couverture
            self.load_cover()

            # Récupérer tous les chapitres (documents HTML)
            self.chapters = []
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    self.chapters.append(item)

            if not self.chapters:
                QMessageBox.warning(
                    self, "Erreur", "Aucun chapitre trouvé dans ce livre."
                )
                return

            # Charger la table des matières
            self.toc_list.clear()
            self.chapter_combo.clear()

            for idx, chapter in enumerate(self.chapters):
                chapter_name = chapter.get_name()
                # Essayer d'obtenir un titre plus lisible
                title = self._extract_title_from_content(chapter.get_content())
                if title:
                    display_name = f"{idx + 1}. {title}"
                else:
                    display_name = f"{idx + 1}. {os.path.basename(chapter_name)}"

                self.toc_list.addItem(display_name)
                self.chapter_combo.addItem(display_name)

            # Charger le premier chapitre
            self.current_chapter_index = 0
            self.load_current_chapter()
            self.enable_navigation(True)

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de charger le fichier EPUB:\n{str(e)}"
            )

    def load_cover(self):
        """Charger et afficher la couverture du livre"""
        try:
            # Méthode 1: Utiliser get_metadata pour trouver la couverture
            cover_item = None

            # Chercher dans les métadonnées
            for item in self.book.get_items():
                if item.get_type() == ebooklib.ITEM_COVER:
                    cover_item = item
                    break

            # Méthode 2: Chercher une image nommée "cover"
            if not cover_item:
                for item in self.book.get_items():
                    if item.get_type() == ebooklib.ITEM_IMAGE:
                        name = item.get_name().lower()
                        if "cover" in name:
                            cover_item = item
                            break

            # Méthode 3: Prendre la première image
            if not cover_item:
                for item in self.book.get_items():
                    if item.get_type() == ebooklib.ITEM_IMAGE:
                        cover_item = item
                        break

            if cover_item:
                # Charger l'image
                cover_data = cover_item.get_content()
                pixmap = QPixmap()
                pixmap.loadFromData(cover_data)

                if not pixmap.isNull():
                    # Afficher la miniature
                    scaled_pixmap = pixmap.scaled(
                        60, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    self.cover_label.setPixmap(scaled_pixmap)

                    # Stocker le pixmap original pour l'affichage en grand
                    self.cover_pixmap = pixmap
                    self.view_cover_btn.setEnabled(True)
                    return

            # Pas de couverture trouvée
            self.cover_label.setText("Pas de\ncouverture")
            self.view_cover_btn.setEnabled(False)

        except Exception as e:
            print(f"Erreur lors du chargement de la couverture: {e}")
            self.cover_label.setText("Erreur")
            self.view_cover_btn.setEnabled(False)

    def show_cover(self):
        """Afficher la couverture en pleine page dans le WebView"""
        if hasattr(self, "cover_pixmap") and not self.cover_pixmap.isNull():
            # Convertir le pixmap en base64 pour l'afficher dans WebView
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.WriteOnly)
            self.cover_pixmap.save(buffer, "PNG")

            img_base64 = base64.b64encode(byte_array.data()).decode()

            html = f"""
            <html>
            <head>
                <style>
                    body {{
                        margin: 0;
                        padding: 20px;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        background-color: #2c2c2c;
                    }}
                    img {{
                        max-width: 90%;
                        max-height: 90vh;
                        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
                    }}
                </style>
            </head>
            <body>
                <img src="data:image/png;base64,{img_base64}" alt="Couverture du livre"/>
            </body>
            </html>
            """

            self.web_view.setHtml(html)

    def _extract_title_from_content(self, content):
        """Extraire le titre du contenu HTML"""
        try:
            content_str = content.decode("utf-8")
            # Chercher les balises de titre
            import re

            title_match = re.search(r"<title>(.*?)</title>", content_str, re.IGNORECASE)
            if title_match:
                return title_match.group(1).strip()

            # Chercher les h1, h2, h3
            for tag in ["h1", "h2", "h3"]:
                heading_match = re.search(
                    f"<{tag}[^>]*>(.*?)</{tag}>", content_str, re.IGNORECASE
                )
                if heading_match:
                    # Enlever les balises HTML restantes
                    title = re.sub("<[^<]+?>", "", heading_match.group(1))
                    return title.strip()
        except:
            pass
        return None

    def load_current_chapter(self):
        """Charger le chapitre actuel"""
        if not self.chapters:
            return

        chapter = self.chapters[self.current_chapter_index]
        content = chapter.get_content()

        try:
            html_content = content.decode("utf-8")

            # Remplacer les chemins des images pour utiliser notre schéma personnalisé
            import re

            html_content = re.sub(
                r'src=["\']([^"\']+)["\']',
                lambda m: f'src="epub://epub/{m.group(1)}"',
                html_content,
            )

            # Remplacer aussi les liens CSS si nécessaire
            html_content = re.sub(
                r'href=["\']([^"\']*\.css)["\']',
                lambda m: f'href="epub://epub/{m.group(1)}"',
                html_content,
            )

            # Ajouter du CSS pour améliorer la lisibilité
            styled_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: 'Georgia', 'Times New Roman', serif;
                        font-size: 16px;
                        line-height: 1.6;
                        max-width: 800px;
                        margin: 20px auto;
                        padding: 20px;
                        background-color: #fafafa;
                    }}
                    p {{
                        text-align: justify;
                        margin: 1em 0;
                    }}
                    h1, h2, h3, h4, h5, h6 {{
                        color: #333;
                        margin-top: 1.5em;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                        display: block;
                        margin: 1em auto;
                    }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            # Utiliser setHtml avec une baseUrl utilisant notre schéma
            self.web_view.setHtml(styled_content, QUrl("epub://epub/"))

            # Mettre à jour l'interface
            self.toc_list.setCurrentRow(self.current_chapter_index)
            self.chapter_combo.setCurrentIndex(self.current_chapter_index)
            self.update_position_label()

        except Exception as e:
            QMessageBox.warning(
                self, "Erreur", f"Impossible de charger le chapitre:\n{str(e)}"
            )

    def update_position_label(self):
        """Mettre à jour le label de position"""
        if self.chapters:
            total = len(self.chapters)
            current = self.current_chapter_index + 1
            self.position_label.setText(f"Chapitre: {current} / {total}")

    def load_chapter_from_list(self, item):
        """Charger un chapitre depuis la liste de la table des matières"""
        self.current_chapter_index = self.toc_list.currentRow()
        self.load_current_chapter()

    def load_chapter_from_combo(self, index):
        """Charger un chapitre depuis le combo box"""
        if index >= 0:
            self.current_chapter_index = index
            self.load_current_chapter()

    def previous_chapter(self):
        """Aller au chapitre précédent"""
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            self.load_current_chapter()

    def next_chapter(self):
        """Aller au chapitre suivant"""
        if self.current_chapter_index < len(self.chapters) - 1:
            self.current_chapter_index += 1
            self.load_current_chapter()

    def first_chapter(self):
        """Aller au premier chapitre"""
        if self.chapters:
            self.current_chapter_index = 0
            self.load_current_chapter()

    def last_chapter(self):
        """Aller au dernier chapitre"""
        if self.chapters:
            self.current_chapter_index = len(self.chapters) - 1
            self.load_current_chapter()

    def search_in_text(self):
        """Rechercher du texte dans le contenu"""
        search_text = self.search_input.text()
        if search_text:
            self.search_text = search_text
            self.web_page.findText(search_text)

    def find_next(self):
        """Trouver l'occurrence suivante"""
        if self.search_text:
            self.web_page.findText(self.search_text)

    def find_previous(self):
        """Trouver l'occurrence précédente"""
        if self.search_text:
            self.web_page.findText(self.search_text, QWebEnginePage.FindBackward)

    def clear_search(self):
        """Effacer la recherche"""
        self.search_input.clear()
        self.search_text = ""
        self.web_page.findText("")

    def enable_navigation(self, enabled):
        """Activer/désactiver les boutons de navigation"""
        self.first_chapter_btn.setEnabled(enabled)
        self.prev_chapter_btn.setEnabled(enabled)
        self.next_chapter_btn.setEnabled(enabled)
        self.last_chapter_btn.setEnabled(enabled)
        self.chapter_combo.setEnabled(enabled)
        self.search_btn.setEnabled(enabled)
        self.search_next_btn.setEnabled(enabled)
        self.search_prev_btn.setEnabled(enabled)
        self.clear_search_btn.setEnabled(enabled)


# Enregistrer le schéma personnalisé avant de créer l'application
scheme = QWebEngineUrlScheme(b"epub")
scheme.setSyntax(QWebEngineUrlScheme.Syntax.Host)
scheme.setFlags(
    QWebEngineUrlScheme.SecureScheme
    | QWebEngineUrlScheme.LocalScheme
    | QWebEngineUrlScheme.LocalAccessAllowed
)
QWebEngineUrlScheme.registerScheme(scheme)


def main():
    app = QApplication(sys.argv)

    # Style de l'application
    app.setStyle("Fusion")

    reader = EpubReader()
    reader.show()

    # Si un fichier est passé en argument
    if len(sys.argv) > 1:
        epub_file = sys.argv[1]
        if os.path.exists(epub_file):
            reader.load_epub(epub_file)

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

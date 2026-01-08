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

Composant d'aperçu HTML du Markdown avec QWebEngine
"""

import os
from xml.etree import ElementTree

from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from pygments.formatters import HtmlFormatter
from markdown.inlinepatterns import InlineProcessor
import markdown
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile
from PyQt5.QtCore import QUrl, QEvent, Qt, QStandardPaths
from PyQt5.QtGui import QDesktopServices
import webbrowser


class CustomWebEnginePage(QWebEnginePage):
    """Page web personnalisée qui gère les clics sur les liens"""

    def acceptNavigationRequest(self, url, _type, isMainFrame):
        """
        Intercepte les tentatives de navigation.
        Si c'est un clic sur un lien, l'ouvre dans le navigateur/visionneuse par défaut.
        """
        if _type == QWebEnginePage.NavigationTypeTyped:
            return True
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            webbrowser.open(url.toString())
            return False
        return True

    def createWindow(self, window_type):
        """
        Gère les demandes de nouvelle fenêtre (ex: target="_blank").
        Crée une page fantôme qui ouvrira le lien externe.
        """
        return CustomWebEnginePage(self)


class TagInlineProcessor(InlineProcessor):
    """Traite les tags @@tag en les entourant d'une balise span."""

    def handleMatch(self, m, data):
        el = ElementTree.Element("span")
        el.set("class", "tag")
        el.text = m.group(0)
        return el, m.start(0), m.end(0)


# V2.8.1 Menu contextuel en Français
class MarkdownPreview(QWidget):
    """Aperçu HTML avec QWebEngine"""

    def __init__(self):
        super().__init__()
        self.current_html = ""
        self.current_markdown = ""
        self.setup_ui()
        self.default_css = self._load_default_css()
        self.pygments_css = HtmlFormatter(style="default").get_style_defs(".highlight")
        self.custom_css = ""
        self.setup_markdown()

        # === NOUVEAU : Désactiver le menu contextuel par défaut ===
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(self.tr("Aperçu HTML"))
        label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa;
                padding: 8px 12px;
                font-weight: bold;
                color: #24292e;
                border: 1px solid #d1d5da;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
        """
        )
        header_layout.addWidget(label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.web_view = QWebEngineView()

        # V4.2.0 Correction erreur "Failed to delete the database" & Crash
        # Le profil et la page doivent être des membres de l'instance (self) pour
        # éviter qu'ils ne soient détruits prématurément par le garbage collector.
        data_dir = QStandardPaths.writableLocation(QStandardPaths.GenericDataLocation)
        cache_path = os.path.join(data_dir, "bluenotebook", "cache")

        self.profile = QWebEngineProfile(self)  # Crée un profil enfant du widget
        self.profile.setCachePath(cache_path)
        self.profile.setPersistentStoragePath(cache_path)

        self.custom_page = CustomWebEnginePage(self.profile, self.web_view)
        self.web_view.setPage(self.custom_page)

        self.web_view.setStyleSheet(
            """
            QWebEngineView {
                border: 1px solid #d1d5da;
                border-radius: 4px;
                background-color: white;
            }
        """
        )

        layout.addWidget(self.web_view, 1)
        self.setLayout(layout)
        # V2.7.5 - Installer un filtre d'événements pour intercepter les clics
        # sur les images dans les liens, sans affecter les liens textuels.
        self.web_view.installEventFilter(self)

    def eventFilter(self, obj, event):
        """
        Filtre les événements de la souris pour gérer les clics sur les images
        qui sont à l'intérieur d'un lien.
        """
        if (
            obj is self.web_view
            and event.type() == QEvent.MouseButtonRelease
            and event.button() == Qt.LeftButton
        ):
            hit_test = self.web_view.page().hitTestContent(event.pos())
            is_on_image = hit_test.mediaType() == QWebEnginePage.MediaTypeImage
            is_on_link = hit_test.linkUrl().isValid()

            # Cas 1: Clic sur une image qui N'EST PAS dans un lien
            # (ex: une image Markdown simple `!`)
            if is_on_image and not is_on_link:
                image_url = hit_test.mediaUrl()
                if image_url.isValid() and image_url.isLocalFile():
                    QDesktopServices.openUrl(image_url)
                if image_url.isValid():
                    webbrowser.open(image_url.toString())
                    return True  # Événement traité

            # Cas 2: Clic sur un lien (contenant une image ou du texte)
            # On laisse CustomWebEnginePage gérer l'ouverture dans le navigateur
            # ou la visionneuse d'images. On ne fait rien ici.
            if is_on_link:
                # Laisser l'événement se propager pour que CustomWebEnginePage le gère
                pass

        # Renvoyer à l'implémentation parente pour tous les autres événements
        return super().eventFilter(obj, event)

    def setup_markdown(self):
        """Configuration du processeur Markdown"""
        self.md = markdown.Markdown(
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "toc",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "sane_lists",
                "smarty",
                "pymdownx.tilde",
                "pymdownx.mark",
            ],
            extension_configs={
                "codehilite": {"css_class": "highlight", "use_pygments": True},
                "toc": {"permalink": True},
            },
        )
        markdown.etree = ElementTree

        self.md.inlinePatterns.register(
            TagInlineProcessor(r"@@(\w{2,})\b", self.md), "tag", 175
        )

    def _load_css_from_file(self, filename):
        """Charge le contenu d'un fichier CSS depuis le répertoire des thèmes."""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            css_path = os.path.join(
                base_path, "..", "resources", "css_preview", filename
            )
            with open(css_path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError) as e:
            print(f"⚠️ Erreur: Impossible de charger le fichier CSS '{filename}': {e}")
            return f"/* CSS '{filename}' non trouvé */"

    def _load_default_css(self):
        """Charge le contenu du fichier CSS par défaut."""
        return self._load_css_from_file("default_bluenotebook.css")

    def set_css_theme(self, theme_filename):
        """Définit et applique un nouveau thème CSS pour l'aperçu."""
        if not theme_filename:
            theme_filename = "default_bluenotebook.css"

        self.default_css = self._load_css_from_file(theme_filename)

        if self.current_markdown:
            self.update_content(self.current_markdown)

    def create_html_template(self, content):
        """Créer le template HTML complet"""
        toc_html = ""
        if hasattr(self.md, "toc") and self.md.toc:
            # Correction i18n : Extraire self.tr() de la f-string pour que
            # l'outil de traduction (pylupdate5) puisse détecter la chaîne.
            toc_title = self.tr("📋 Table des matières")
            toc_html = f'<div class="toc"><h2>{toc_title}</h2>{self.md.toc}</div>'

        # V2.7.7 - Ajout d'un style pour limiter la taille des images Markdown
        # Cette règle s'applique aux images qui ne sont pas dans une <figure>
        # pour ne pas affecter les images HTML dont la taille est déjà définie.
        image_style = """
        body > p > img, body > p > a > img {
            max-width: 600px;
            max-height: 600px;
            height: auto; /* Conserve le ratio */
            display: block; /* Permet le centrage avec margin */
            margin: 1em auto; /* Centre l'image horizontalement */
        }
        """
        final_css = self.default_css + self.pygments_css + self.custom_css + image_style

        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>BlueNotebook Preview</title>
            <style>
                {final_css}
            </style>
        </head>
        <body>
            {toc_html}
            {content}
        </body>
        </html>
        """

    def show_welcome_content(self):
        """Afficher le contenu de bienvenue"""
        # Extraction des chaînes pour faciliter la détection par lupdate (i18n)
        title = self.tr("🔵 Bienvenue dans BlueNotebook")
        subtitle = self.tr(
            "Commencez à taper du Markdown dans l'éditeur pour voir l'aperçu ici."
        )
        syntax_header = self.tr("📝 Syntaxe Markdown supportée :")
        titles_header = self.tr("Titres")
        formatting_header = self.tr("Mise en forme")
        bold_label = self.tr("Gras")
        italic_label = self.tr("Italique")
        inline_code_label = self.tr("Code inline")
        lists_header = self.tr("Listes")
        bullet_list_label = self.tr("Liste à puces :")
        numbered_list_label = self.tr("Liste numérotée :")
        others_header = self.tr("Autres")
        quotes_label = self.tr("Citations :")
        links_label = self.tr("Liens :")
        images_label = self.tr("Images :")
        tables_label = self.tr("Tables :")
        code_label = self.tr("Code :")

        welcome_content = f"""
        <div style="text-align: center; padding: 40px;">
            <h1>{title}</h1>
            <p><em>{subtitle}</em></p>
            
            <div style="text-align: left; max-width: 600px; margin: 40px auto;">
                <h2>{syntax_header}</h2>
                
                <h3>{titles_header}</h3>
                <pre><code># Titre 1
## Titre 2
### Titre 3</code></pre>
                
                <h3>{formatting_header}</h3>
                <p><strong>{bold_label}</strong> : <code>**texte**</code> ou <code>__texte__</code></p>
                <p><em>{italic_label}</em> : <code>*texte*</code> ou <code>_texte_</code></p>
                <p><code>{inline_code_label}</code> : <code>`code`</code></p>
                
                <h3>{lists_header}</h3>
                <ul>
                    <li>{bullet_list_label} <code>- item</code></li>
                    <li>{numbered_list_label} <code>1. item</code></li>
                </ul>
                
                <h3>{others_header}</h3>
                <ul>
                    <li>{quotes_label} <code>&gt; texte</code></li>
                    <li>{links_label} <code>[texte](url)</code></li>
                    <li>{images_label} <code>![alt](url)</code></li>
                    <li>{tables_label} <code>| col1 | col2 |</code></li>
                    <li>{code_label} <code>```python</code></li>
                </ul>
            </div>
        </div>
        """
        self.web_view.setHtml(welcome_content)

    def update_content(self, markdown_content: str, journal_dir: str = None):
        """Mettre à jour le contenu de l'aperçu"""
        try:
            self.current_markdown = markdown_content

            if not markdown_content.strip():
                self.show_welcome_content()
                return

            self.md.reset()
            html_content = self.md.convert(markdown_content)
            full_html = self.create_html_template(html_content)

            if journal_dir:
                base_url = QUrl.fromLocalFile(journal_dir + os.path.sep)
            else:
                base_url = QUrl("file:///")

            # V3.3.9 - Ajout d'un script pour afficher l'URL au survol des liens
            script = """
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    var links = document.getElementsByTagName('a');
                    for (var i = 0; i < links.length; i++) {
                        links[i].setAttribute('title', links[i].href);
                    }
                });
            </script>
            """
            # Insérer le script juste avant la fermeture de la balise </body>
            full_html_with_script = full_html.replace("</body>", script + "</body>")

            self.web_view.setHtml(full_html_with_script, baseUrl=base_url)
            self.current_html = full_html

        except Exception as e:
            error_html = self.create_html_template(
                f"""
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 16px; border-radius: 4px;">
                    <h3>{self.tr("❌ Erreur de rendu")}</h3>
                    <p><strong>{self.tr("Erreur :")}</strong> {str(e)}</p>
                    <p><em>{self.tr("Vérifiez la syntaxe Markdown dans l'éditeur.")}</em></p>
                </div>
            """
            )
            self.web_view.setHtml(error_html)

    def get_html(self):
        """Récupérer le HTML complet pour l'export"""
        return self.current_html

    def scroll_to_percentage(self, percentage: float):
        """Fait défiler la vue web à un pourcentage donné de la hauteur totale."""
        if not (0.0 <= percentage <= 1.0):
            return

        js_code = f"""
            var scrollHeight = document.body.scrollHeight;
            var clientHeight = document.documentElement.clientHeight;
            var targetY = (scrollHeight - clientHeight) * {percentage};
            window.scrollTo(0, targetY);
        """
        self.web_view.page().runJavaScript(js_code)

    # V2.8.1 Menu contextuel en Français
    def show_context_menu(self, pos):
        """Affiche un menu contextuel personnalisé et traduisible"""
        menu = QMenu(self)

        # --- Sélection de texte ---
        has_selection = self.web_view.selectedText().strip() != ""

        # Action : Copier
        copy_action = QAction(self.tr("Copier"), self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)

        # Action : Tout sélectionner
        select_all_action = QAction(self.tr("Tout sélectionner"), self)
        select_all_action.triggered.connect(self.select_all)
        menu.addAction(select_all_action)

        menu.addSeparator()

        # Action : Recharger
        reload_action = QAction(self.tr("Recharger"), self)
        reload_action.triggered.connect(self.web_view.reload)
        menu.addAction(reload_action)

        # Action : Ouvrir dans le navigateur
        open_in_browser_action = QAction(self.tr("Ouvrir dans le navigateur"), self)
        open_in_browser_action.triggered.connect(self.open_in_browser)
        menu.addAction(open_in_browser_action)

        menu.addSeparator()

        # Action : Imprimer (optionnel)
        # print_action = QAction(self.tr("Imprimer..."), self)
        # print_action.triggered.connect(self.web_view.page().printRequested)
        # menu.addAction(print_action)

        # Exécuter le menu
        menu.exec_(self.web_view.mapToGlobal(pos))

    # === ACTIONS ASSOCIÉES ===
    def copy_selection(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.web_view.selectedText())

    def select_all(self):
        self.web_view.triggerPageAction(QWebEnginePage.SelectAll)

    def open_in_browser(self):
        url = self.web_view.page().url()
        if url.isValid():
            QDesktopServices.openUrl(url)

    # === POUR LA TRADUCTION : mise à jour dynamique ===
    def retranslate_ui(self):
        """À appeler quand on change de langue"""
        # Si le contenu markdown est vide, on réaffiche le message de bienvenue traduit
        if not self.current_markdown or not self.current_markdown.strip():
            self.show_welcome_content()

    # === Surcharge pour capter le changement de langue ===
    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

    def cleanup(self):
        """Libère les ressources de la vue web avant la fermeture."""
        self.web_view.setPage(None)
        if hasattr(self, "custom_page"):
            self.custom_page.deleteLater()

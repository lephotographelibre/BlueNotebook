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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
from markdown.inlinepatterns import InlineProcessor
import markdown


class TagInlineProcessor(InlineProcessor):
    """Traite les tags @@tag en les entourant d'une balise span."""

    def handleMatch(self, m, data):
        el = ElementTree.Element("span")
        el.set("class", "tag")
        el.text = m.group(0)
        return el, m.start(0), m.end(0)


class MarkdownPreview(QWidget):
    """Aperçu HTML avec QWebEngine"""

    def __init__(self):
        super().__init__()
        self.current_html = ""
        self.current_markdown = ""
        self.setup_ui()
        self.default_css = self._load_default_css()
        self.custom_css = ""
        self.setup_markdown()

    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        label = QLabel("👀 Aperçu HTML")
        label.setStyleSheet(
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
        label.setMaximumHeight(35)
        layout.addWidget(label)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet(
            """
            QWebEngineView {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
        """
        )

        layout.addWidget(self.web_view, 1)
        self.setLayout(layout)

        self.show_welcome_content()

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
        return self._load_css_from_file("default_preview.css")

    def set_css_theme(self, theme_filename):
        """Définit et applique un nouveau thème CSS pour l'aperçu."""
        if not theme_filename:
            theme_filename = "default_preview.css"

        self.default_css = self._load_css_from_file(theme_filename)
        
        if self.current_markdown:
            self.update_content(self.current_markdown)

    def create_html_template(self, content):
        """Créer le template HTML complet"""
        toc_html = ""
        if hasattr(self.md, "toc") and self.md.toc:
            toc_html = (
                f'<div class="toc"><h2>📋 Table des matières</h2>{self.md.toc}</div>'
            )
        
        final_css = self.default_css + self.custom_css

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
        welcome_content = """
        <div style="text-align: center; padding: 40px;">
            <h1>🔵 Bienvenue dans BlueNotebook</h1>
            <p><em>Commencez à taper du Markdown dans l'éditeur pour voir l'aperçu ici.</em></p>
            
            <div style="text-align: left; max-width: 600px; margin: 40px auto;">
                <h2>📝 Syntaxe Markdown supportée :</h2>
                
                <h3>Titres</h3>
                <pre><code># Titre 1
## Titre 2
### Titre 3</code></pre>
                
                <h3>Mise en forme</h3>
                <p><strong>Gras</strong> : <code>**texte**</code> ou <code>__texte__</code></p>
                <p><em>Italique</em> : <code>*texte*</code> ou <code>_texte_</code></p>
                <p><code>Code inline</code> : <code>`code`</code></p>
                
                <h3>Listes</h3>
                <ul>
                    <li>Liste à puces : <code>- item</code></li>
                    <li>Liste numérotée : <code>1. item</code></li>
                </ul>
                
                <h3>Autres</h3>
                <ul>
                    <li>Citations : <code>&gt; texte</code></li>
                    <li>Liens : <code>[texte](url)</code></li>
                    <li>Images : <code>![alt](url)</code></li>
                    <li>Tables : <code>| col1 | col2 |</code></li>
                    <li>Code : <code>```python</code></li>
                </ul>
            </div>
        </div>
        """
        self.web_view.setHtml(welcome_content)

    def update_content(self, markdown_content):
        """Mettre à jour le contenu de l'aperçu"""
        try:
            self.current_markdown = markdown_content

            if not markdown_content.strip():
                self.show_welcome_content()
                return

            self.md.reset()
            html_content = self.md.convert(markdown_content)
            full_html = self.create_html_template(html_content)

            self.web_view.setHtml(full_html, baseUrl=QUrl("file:///"))
            self.current_html = full_html

        except Exception as e:
            error_html = self.create_html_template(
                f"""
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 16px; border-radius: 4px;">
                    <h3>❌ Erreur de rendu</h3>
                    <p><strong>Erreur :</strong> {str(e)}</p>
                    <p><em>Vérifiez la syntaxe Markdown dans l'éditeur.</em></p>
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

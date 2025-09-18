"""
Composant d'aperçu HTML du Markdown avec QWebEngine
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, QTimer
import markdown
import tempfile
import os

class MarkdownPreview(QWidget):
    """Aperçu HTML avec QWebEngine"""
    
    def __init__(self):
        super().__init__()
        self.current_html = ""
        self.setup_ui()
        self.setup_markdown()
        
    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Label compact en haut
        label = QLabel("👀 Aperçu")
        label.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                padding: 8px; 
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #495057;
            }
        """)
        label.setMaximumHeight(35)
        layout.addWidget(label)
        
        # Vue web pour l'aperçu HTML - prend tout l'espace restant
        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("""
            QWebEngineView {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        # La vue web prend tout l'espace disponible
        layout.addWidget(self.web_view, 1)  # stretch factor = 1
        
        self.setLayout(layout)
        
        # Charger le contenu par défaut
        self.show_welcome_content()
        
    def setup_markdown(self):
        """Configuration du processeur Markdown"""
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code',
                'codehilite',
                'toc',
                'attr_list',
                'def_list',
                'footnotes',
                'md_in_html',
                'sane_lists',
                'smarty'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                },
                'toc': {
                    'permalink': True
                }
            }
        )
        
    def create_html_template(self, content):
        """Créer le template HTML complet"""
        # Ajouter la table des matières si elle existe
        toc_html = ""
        if hasattr(self.md, 'toc') and self.md.toc:
            toc_html = f'<div class="toc"><h2>📋 Table des matières</h2>{self.md.toc}</div>'
        
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BlueNotebook Preview</title>
            <style>
                /* Reset et base */
                * {{
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #24292e;
                    max-width: 980px;
                    margin: 0 auto;
                    padding: 45px;
                    background-color: #ffffff;
                    font-size: 16px;
                }}
                
                /* Titres */
                h1, h2, h3, h4, h5, h6 {{
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                    color: #1f2937;
                }}
                
                h1 {{
                    font-size: 2em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }}
                
                h2 {{
                    font-size: 1.5em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }}
                
                h3 {{ font-size: 1.25em; }}
                h4 {{ font-size: 1em; }}
                h5 {{ font-size: 0.875em; }}
                h6 {{ font-size: 0.85em; color: #6a737d; }}
                
                /* Paragraphes et texte */
                p {{
                    margin-top: 0;
                    margin-bottom: 16px;
                    text-align: justify;
                }}
                
                /* Mise en forme */
                strong {{
                    font-weight: 600;
                    color: #1f2937;
                }}
                
                em {{
                    font-style: italic;
                    color: #374151;
                }}
                
                /* Code */
                code {{
                    padding: 0.2em 0.4em;
                    margin: 0;
                    font-size: 85%;
                    background-color: rgba(27, 31, 35, 0.05);
                    border-radius: 6px;
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                    color: #e74c3c;
                }}
                
                pre {{
                    padding: 16px;
                    overflow: auto;
                    font-size: 85%;
                    line-height: 1.45;
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    border: 1px solid #e1e4e8;
                    margin-bottom: 16px;
                }}
                
                pre code {{
                    display: inline;
                    padding: 0;
                    margin: 0;
                    overflow: visible;
                    line-height: inherit;
                    word-wrap: normal;
                    background-color: transparent;
                    border: 0;
                    color: #24292e;
                }}
                
                /* Citations */
                blockquote {{
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                    margin: 0 0 16px 0;
                    font-style: italic;
                }}
                
                /* Listes */
                ul, ol {{
                    margin-top: 0;
                    margin-bottom: 16px;
                    padding-left: 2em;
                }}
                
                li {{
                    margin-bottom: 0.25em;
                }}
                
                /* Liens */
                a {{
                    color: #0366d6;
                    text-decoration: none;
                    font-weight: 500;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
                
                /* Images */
                img {{
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 10px 0;
                }}
                
                /* Tableaux */
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 16px;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    overflow: hidden;
                }}
                
                th, td {{
                    padding: 6px 13px;
                    border: 1px solid #e1e4e8;
                    text-align: left;
                }}
                
                th {{
                    font-weight: 600;
                    background-color: #f6f8fa;
                }}
                
                tr:nth-child(2n) {{
                    background-color: #f9f9f9;
                }}
                
                /* Règles horizontales */
                hr {{
                    height: 0.25em;
                    margin: 24px 0;
                    background-color: #e1e4e8;
                    border: 0;
                }}
                
                /* Coloration syntaxique */
                .highlight {{
                    background: #f8f8f8;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                    margin: 16px 0;
                }}
                
                .highlight .k {{ color: #d73a49; font-weight: bold; }}
                .highlight .s {{ color: #032f62; }}
                .highlight .c {{ color: #6a737d; font-style: italic; }}
                .highlight .nb {{ color: #005cc5; }}
                .highlight .nf {{ color: #6f42c1; }}
                
                /* Table des matières */
                .toc {{
                    background-color: #f8f9fa;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 16px;
                    margin: 16px 0;
                    float: right;
                    max-width: 300px;
                    margin-left: 20px;
                }}
                
                .toc h2 {{
                    margin-top: 0;
                    font-size: 1em;
                    border-bottom: none;
                    padding-bottom: 0;
                }}
                
                .toc ul {{
                    list-style: none;
                    padding-left: 0;
                }}
                
                .toc ul ul {{
                    padding-left: 20px;
                }}
                
                .toc a {{
                    text-decoration: none;
                    color: #0366d6;
                    font-size: 0.9em;
                }}
                
                /* Responsive */
                @media (max-width: 768px) {{
                    body {{
                        padding: 20px;
                        font-size: 14px;
                    }}
                    
                    .toc {{
                        float: none;
                        margin-left: 0;
                        max-width: 100%;
                    }}
                }}
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
            if not markdown_content.strip():
                self.show_welcome_content()
                return
                
            # Réinitialiser le parser
            self.md.reset()
            
            # Convertir Markdown en HTML
            html_content = self.md.convert(markdown_content)
            
            # Créer le HTML complet avec CSS
            full_html = self.create_html_template(html_content)
            
            # Mettre à jour la vue web
            self.web_view.setHtml(full_html)
            self.current_html = full_html
            
        except Exception as e:
            error_html = self.create_html_template(f"""
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 16px; border-radius: 4px;">
                    <h3>❌ Erreur de rendu</h3>
                    <p><strong>Erreur :</strong> {str(e)}</p>
                    <p><em>Vérifiez la syntaxe Markdown dans l'éditeur.</em></p>
                </div>
            """)
            self.web_view.setHtml(error_html)
            
    def get_html(self):
        """Récupérer le HTML complet pour l'export"""
        return self.current_html

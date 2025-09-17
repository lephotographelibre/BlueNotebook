"""
Composant d'aperçu HTML du Markdown avec rendu HTML complet
"""

import tkinter as tk
from tkinter import ttk
import markdown
from tkhtmlview import HTMLScrolledText

class MarkdownPreview:
    def __init__(self, parent):
        self.parent = parent
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite',
                'attr_list',
                'def_list',
                'footnotes',
                'md_in_html'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': True
                }
            }
        )
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Aperçu")
        label.pack(pady=(0, 5))
        
        # Zone de prévisualisation HTML avec scrollbar
        self.html_widget = HTMLScrolledText(
            self.frame,
            html="<h1>BlueNotebook</h1><p>Tapez du Markdown dans l'éditeur pour voir l'aperçu ici.</p>",
            height=20,
            width=50,
            wrap=tk.WORD,
            background="white"
        )
        self.html_widget.pack(fill=tk.BOTH, expand=True)
        
        # Appliquer le CSS par défaut
        self.apply_default_css()
        
    def apply_default_css(self):
        """Appliquer les styles CSS par défaut"""
        css = """
        <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 20px;
            background-color: #fff;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
            margin-top: 24px;
            margin-bottom: 16px;
            font-weight: 600;
        }
        
        h1 { 
            font-size: 2em; 
            border-bottom: 2px solid #eaecef; 
            padding-bottom: 8px; 
        }
        
        h2 { 
            font-size: 1.5em; 
            border-bottom: 1px solid #eaecef; 
            padding-bottom: 8px; 
        }
        
        h3 { font-size: 1.25em; }
        h4 { font-size: 1.1em; }
        h5 { font-size: 1em; }
        h6 { font-size: 0.9em; }
        
        p {
            margin-bottom: 16px;
            text-align: justify;
        }
        
        code {
            background-color: #f6f8fa;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            font-size: 0.9em;
            color: #d73a49;
        }
        
        pre {
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 16px 0;
            border: 1px solid #e1e4e8;
        }
        
        pre code {
            background: none;
            padding: 0;
            border-radius: 0;
            color: #24292e;
        }
        
        blockquote {
            border-left: 4px solid #dfe2e5;
            padding-left: 16px;
            color: #6a737d;
            margin: 16px 0;
            font-style: italic;
        }
        
        table {
            border-collapse: collapse;
            width: 100%;
            margin-bottom: 16px;
            border: 1px solid #e1e4e8;
        }
        
        th, td {
            border: 1px solid #e1e4e8;
            padding: 8px 12px;
            text-align: left;
        }
        
        th {
            background-color: #f6f8fa;
            font-weight: 600;
        }
        
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        ul, ol {
            margin-bottom: 16px;
            padding-left: 32px;
        }
        
        li {
            margin-bottom: 4px;
        }
        
        a {
            color: #0366d6;
            text-decoration: none;
        }
        
        a:hover {
            text-decoration: underline;
        }
        
        img {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .highlight {
            background-color: #f6f8fa;
            padding: 16px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #e1e4e8;
        }
        
        /* Coloration syntaxique pour le code */
        .highlight .k { color: #d73a49; font-weight: bold; } /* Keyword */
        .highlight .s { color: #032f62; } /* String */
        .highlight .c { color: #6a737d; font-style: italic; } /* Comment */
        .highlight .n { color: #24292e; } /* Name */
        .highlight .o { color: #d73a49; } /* Operator */
        .highlight .p { color: #24292e; } /* Punctuation */
        .highlight .nb { color: #005cc5; } /* Name.Builtin */
        .highlight .nf { color: #6f42c1; } /* Name.Function */
        
        /* Style pour les alertes */
        .alert {
            padding: 12px 16px;
            margin: 16px 0;
            border-radius: 6px;
            border-left: 4px solid;
        }
        
        .alert-info {
            background-color: #e6f7ff;
            border-left-color: #1890ff;
            color: #0050b3;
        }
        
        .alert-warning {
            background-color: #fffbe6;
            border-left-color: #faad14;
            color: #ad6800;
        }
        
        .alert-error {
            background-color: #fff2f0;
            border-left-color: #f5222d;
            color: #a8071a;
        }
        
        /* Table des matières */
        .toc {
            background-color: #f8f9fa;
            border: 1px solid #e1e4e8;
            border-radius: 6px;
            padding: 16px;
            margin: 16px 0;
        }
        
        .toc ul {
            list-style-type: none;
            padding-left: 20px;
        }
        
        .toc > ul {
            padding-left: 0;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            body {
                margin: 10px;
                font-size: 14px;
            }
            
            h1 { font-size: 1.5em; }
            h2 { font-size: 1.3em; }
            h3 { font-size: 1.1em; }
        }
        </style>
        """
        self.default_css = css
        
    def update_preview(self, markdown_content):
        """Mettre à jour l'aperçu avec rendu HTML complet"""
        try:
            if not markdown_content.strip():
                # Contenu par défaut si vide
                html_content = """
                <h1>🔵 BlueNotebook</h1>
                <p><em>Commencez à taper du Markdown dans l'éditeur pour voir l'aperçu ici.</em></p>
                
                <h2>Exemples de syntaxe Markdown :</h2>
                
                <h3>Titres</h3>
                <pre><code># Titre 1
## Titre 2
### Titre 3</code></pre>
                
                <h3>Mise en forme</h3>
                <pre><code>**Gras** ou __Gras__
*Italique* ou _Italique_
`Code inline`</code></pre>
                
                <h3>Listes</h3>
                <pre><code>- Item 1
- Item 2
  - Sous-item</code></pre>
                
                <h3>Citations</h3>
                <pre><code>> Ceci est une citation
> Sur plusieurs lignes</code></pre>
                """
            else:
                # Réinitialiser le parser pour éviter les conflits
                self.md.reset()
                
                # Conversion Markdown vers HTML
                html_content = self.md.convert(markdown_content)
                
                # Ajouter la table des matières si elle existe
                if hasattr(self.md, 'toc') and self.md.toc:
                    toc_html = f'<div class="toc"><h3>Table des matières</h3>{self.md.toc}</div>'
                    html_content = toc_html + html_content
            
            # Combiner CSS et contenu HTML
            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>BlueNotebook Preview</title>
                {self.default_css}
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Mettre à jour le widget HTML
            self.html_widget.set_html(full_html)
            
        except Exception as e:
            # Affichage d'erreur avec style
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                {self.default_css}
            </head>
            <body>
                <div class="alert alert-error">
                    <h3>❌ Erreur de prévisualisation</h3>
                    <p><strong>Erreur:</strong> {str(e)}</p>
                    <p><em>Vérifiez la syntaxe Markdown dans l'éditeur.</em></p>
                </div>
            </body>
            </html>
            """
            self.html_widget.set_html(error_html)

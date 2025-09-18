# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown moderne et professionnel développé en Python avec PyQt5 et QWebEngine.

## ✨ Fonctionnalités

- ✏️ **Édition avancée** avec coloration syntaxique Markdown
- 👀 **Aperçu HTML en temps réel** avec rendu parfait (QWebEngine)
- 💾 **Gestion de fichiers** complète (nouveau, ouvrir, sauvegarder)
- 🔍 **Recherche et remplacement** intégrés
- 📊 **Statistiques du document** (lignes, mots, caractères)
- 📤 **Export HTML** avec CSS professionnel
- 🌐 **Support complet Markdown** (tables, code, citations, etc.)
- 🎨 **Interface moderne** avec PyQt5
- 📋 **Table des matières** automatique
- ⌨️ **Raccourcis clavier** intuitifs

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- PyQt5 et PyQtWebEngine

### Installation rapide

1. **Créer le projet** :
```bash
# Exécuter le script de génération
./setup_bluenotebook.sh
cd bluenotebook
```

2. **Installer les dépendances** :
```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt
```

3. **Lancer l'application** :
```bash
python main.py
```

### Installation manuelle des dépendances

```bash
pip install PyQt5 PyQtWebEngine markdown pymdown-extensions Pygments
```

## 🎯 Utilisation

### Interface principale
- **Zone d'édition** (gauche) : Éditeur avec coloration syntaxique
- **Zone d'aperçu** (droite) : Rendu HTML en temps réel
- **Barre de statut** : Informations sur le fichier et statistiques

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+N` | Nouveau fichier |
| `Ctrl+O` | Ouvrir un fichier |
| `Ctrl+S` | Sauvegarder |
| `Ctrl+Shift+S` | Sauvegarder sous... |
| `Ctrl+Q` | Quitter |
| `Ctrl+Z` | Annuler |
| `Ctrl+Y` | Rétablir |
| `Ctrl+F` | Rechercher |
| `F5` | Basculer l'aperçu |

### Syntaxe Markdown supportée

```markdown
# Titres
## Sous-titres
### Titres de niveau 3

**Gras** et *italique*

`Code inline` et blocs de code :
```python
def hello():
    print("Hello BlueNotebook!")
```

> Citations
> sur plusieurs lignes

- Listes à puces
- Avec sous-éléments
  - Comme ça

1. Listes numérotées
2. Deuxième élément

| Tables | Colonnes |
|--------|----------|
| Data   | Values   |

[Liens](https://example.com) et ![Images](image.png)

---

Règles horizontales et plus !
```

## 🏗️ Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur PyQt5
│   ├── __init__.py
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur avec coloration syntaxique
│   └── preview.py       # Aperçu HTML avec QWebEngine
├── core/                # Logique métier
│   ├── __init__.py
│   ├── markdown_parser.py  # Gestionnaire Markdown
│   └── file_handler.py     # Gestionnaire de fichiers
├── resources/           # Ressources
│   └── styles.css"""
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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("👀 Aperçu")
        label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f8f9fa;")
        layout.addWidget(label)
        
        # Vue web pour l'aperçu HTML
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
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
        
    def get_css(self):
        """Retourner le CSS pour l'aperçu"""
        return """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>BlueNotebook Preview</title>
            <style>
                /* Reset et base */
                * {
                    box-sizing: border-box;
                }
                
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    line-height: 1.6;
                    color: #24292e;
                    max-width: 980px;
                    margin: 0 auto;
                    padding: 45px;
                    background-color: #ffffff;
                    font-size: 16px;
                }
                
                /* Titres */
                h1, h2, h3, h4, h5, h6 {
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                    color: #1f2937;
                }
                
                h1 {
                    font-size: 2em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }
                
                h2 {
                    font-size: 1.5em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }
                
                h3 { font-size: 1.25em; }
                h4 { font-size: 1em; }
                h5 { font-size: 0.875em; }
                h6 { font-size: 0.85em; color: #6a737d; }
                
                /* Paragraphes et texte */
                p {
                    margin-top: 0;
                    margin-bottom: 16px;
                    text-align: justify;
                }
                
                /* Mise en forme */
                strong {
                    font-weight: 600;
                    color: #1f2937;
                }
                
                em {
                    font-style: italic;
                    color: #374151;
                }
                
                /* Code */
                code {
                    padding: 0.2em 0.4em;
                    margin: 0;
                    font-size: 85%;
                    background-color: rgba(27, 31, 35, 0.05);
                    border-radius: 6px;
                    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
                    color: #e74c3c;
                }
                
                pre {
                    padding: 16px;
                    overflow: auto;
                    font-size: 85%;
                    line-height: 1.45;
                    background-color: #f6f8fa;
                    border-radius: 6px;
                    border: 1px solid #e1e4e8;
                    margin-bottom: 16px;
                }
                
                pre code {
                    display: inline;
                    padding: 0;
                    margin: 0;
                    overflow: visible;
                    line-height: inherit;
                    word-wrap: normal;
                    background-color: transparent;
                    border: 0;
                    color: #24292e;
                }
                
                /* Citations */
                blockquote {
                    padding: 0 1em;
                    color: #6a737d;
                    border-left: 0.25em solid #dfe2e5;
                    margin: 0 0 16px 0;
                    font-style: italic;
                }
                
                blockquote > :first-child {
                    margin-top: 0;
                }
                
                blockquote > :last-child {
                    margin-bottom: 0;
                }
                
                /* Listes */
                ul, ol {
                    margin-top: 0;
                    margin-bottom: 16px;
                    padding-left: 2em;
                }
                
                li {
                    margin-bottom: 0.25em;
                }
                
                li > p {
                    margin-top: 16px;
                }
                
                li + li {
                    margin-top: 0.25em;
                }
                
                /* Liens */
                a {
                    color: #0366d6;
                    text-decoration: none;
                    font-weight: 500;
                }
                
                a:hover {
                    text-decoration: underline;
                }
                
                a:visited {
                    color: #6f42c1;
                }
                
                /* Images */
                img {
                    max-width: 100%;
                    height: auto;
                    border-radius: 6px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 10px 0;
                }
                
                /* Tableaux */
                table {
                    border-collapse: collapse;
                    border-spacing: 0;
                    width: 100%;
                    margin-bottom: 16px;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    overflow: hidden;
                }
                
                th, td {
                    padding: 6px 13px;
                    border: 1px solid #e1e4e8;
                    text-align: left;
                }
                
                th {
                    font-weight: 600;
                    background-color: #f6f8fa;
                    color: #24292e;
                }
                
                tr:nth-child(2n) {
                    background-color: #f9f9f9;
                }
                
                /* Règles horizontales */
                hr {
                    height: 0.25em;
                    padding: 0;
                    margin: 24px 0;
                    background-color: #e1e4e8;
                    border: 0;
                }
                
                /* Coloration syntaxique Pygments */
                .codehilite {
                    background: #f8f8f8;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 16px;
                    overflow-x: auto;
                    margin: 16px 0;
                }
                
                .highlight .hll { background-color: #ffffcc }
                .highlight .c { color: #6a737d; font-style: italic } /* Comment */
                .highlight .err { color: #a61717; background-color: #e3d2d2 } /* Error */
                .highlight .k { color: #d73a49; font-weight: bold } /* Keyword */
                .highlight .o { font-weight: bold } /* Operator */
                .highlight .cm { color: #6a737d; font-style: italic } /* Comment.Multiline */
                .highlight .cp { color: #999999; font-weight: bold } /* Comment.Preproc */
                .highlight .c1 { color: #6a737d; font-style: italic } /* Comment.Single */
                .highlight .cs { color: #999999; font-weight: bold; font-style: italic } /* Comment.Special */
                .highlight .gd { color: #000000; background-color: #ffdddd } /* Generic.Deleted */
                .highlight .ge { font-style: italic } /* Generic.Emph */
                .highlight .gr { color: #aa0000 } /* Generic.Error */
                .highlight .gh { color: #999999 } /* Generic.Heading */
                .highlight .gi { color: #000000; background-color: #ddffdd } /* Generic.Inserted */
                .highlight .go { color: #888888 } /* Generic.Output */
                .highlight .gp { color: #555555 } /* Generic.Prompt */
                .highlight .gs { font-weight: bold } /* Generic.Strong */
                .highlight .gu { color: #aaaaaa } /* Generic.Subheading */
                .highlight .gt { color: #aa0000 } /* Generic.Traceback */
                .highlight .kc { color: #d73a49; font-weight: bold } /* Keyword.Constant */
                .highlight .kd { color: #d73a49; font-weight: bold } /* Keyword.Declaration */
                .highlight .kn { color: #d73a49; font-weight: bold } /* Keyword.Namespace */
                .highlight .kp { color: #d73a49; font-weight: bold } /* Keyword.Pseudo */
                .highlight .kr { color: #d73a49; font-weight: bold } /* Keyword.Reserved */
                .highlight .kt { color: #445588; font-weight: bold } /* Keyword.Type */
                .highlight .m { color: #009999 } /* Literal.Number */
                .highlight .s { color: #032f62 } /* Literal.String */
                .highlight .na { color: #008080 } /* Name.Attribute */
                .highlight .nb { color: #005cc5 } /* Name.Builtin */
                .highlight .nc { color: #445588; font-weight: bold } /* Name.Class */
                .highlight .no { color: #008080 } /* Name.Constant */
                .highlight .nd { color: #3c5d5d; font-weight: bold } /* Name.Decorator */
                .highlight .ni { color: #800080 } /* Name.Entity */
                .highlight .ne { color: #990000; font-weight: bold } /* Name.Exception */
                .highlight .nf { color: #6f42c1; font-weight: bold } /* Name.Function */
                .highlight .nl { color: #990000; font-weight: bold } /* Name.Label */
                .highlight .nn { color: #555555 } /* Name.Namespace */
                .highlight .nt { color: #22863a } /* Name.Tag */
                .highlight .nv { color: #008080 } /* Name.Variable */
                .highlight .ow { font-weight: bold } /* Operator.Word */
                .highlight .w { color: #bbbbbb } /* Text.Whitespace */
                .highlight .mf { color: #009999 } /* Literal.Number.Float */
                .highlight .mh { color: #009999 } /* Literal.Number.Hex */
                .highlight .mi { color: #009999 } /* Literal.Number.Integer */
                .highlight .mo { color: #009999 } /* Literal.Number.Oct */
                .highlight .sb { color: #032f62 } /* Literal.String.Backtick */
                .highlight .sc { color: #032f62 } /* Literal.String.Char */
                .highlight .sd { color: #032f62 } /* Literal.String.Doc */
                .highlight .s2 { color: #032f62 } /* Literal.String.Double */
                .highlight .se { color: #032f62 } /* Literal.String.Escape */
                .highlight .sh { color: #032f62 } /* Literal.String.Heredoc */
                .highlight .si { color: #032f62 } /* Literal.String.Interpol */
                .highlight .sx { color: #032f62 } /* Literal.String.Other */
                .highlight .sr { color: #009926 } /* Literal.String.Regex */
                .highlight .s1 { color: #032f62 } /* Literal.String.Single */
                .highlight .ss { color: #990073 } /* Literal.String.Symbol */
                .highlight .bp { color: #999999 } /* Name.Builtin.Pseudo */
                .highlight .vc { color: #008080 } /* Name.Variable.Class */
                .highlight .vg { color: #008080 } /* Name.Variable.Global */
                .highlight .vi { color: #008080 } /* Name.Variable.Instance */
                .highlight .il { color: #009999 } /* Literal.Number.Integer.Long */
                
                /* Table des matières */
                .toc {
                    background-color: #f8f9fa;
                    border: 1px solid #e1e4e8;
                    border-radius: 6px;
                    padding: 16px;
                    margin: 16px 0;
                    max-width: 300px;
                    float: right;
                    margin-left: 20px;
                }
                
                .toc h2 {
                    margin-top: 0;
                    font-size: 1em;
                    border-bottom: none;
                    padding-bottom: 0;
                }
                
                .toc ul {
                    list-style: none;
                    padding-left: 0;
                    margin: 10px 0;
                }
                
                .toc ul ul {
                    padding-left: 20px;
                    margin: 5px 0;
                }
                
                .toc li {
                    margin: 5px 0;
                }
                
                .toc a {
                    text-decoration: none;
                    color: #0366d6;
                    font-size: 0.9em;
                }
                
                .toc a:hover {
                    text-decoration: underline;
                }
                
                /* Responsive */
                @media (max-width: 768px) {
                    body {
                        padding: 20px;
                        font-size: 14px;
                    }
                    
                    .toc {
                        float: none;
                        margin-left: 0;
                        max-width: 100%;
                    }
                    
                    h1 { font-size: 1.6em; }
                    h2 { font-size: 1.3em; }
                    h3 { font-size: 1.1em; }
                    
                    pre {
                        padding: 12px;
                        font-size: 14px;
                    }
                    
                    table {
                        font-size: 14px;
                    }
                    
                    th, td {
                        padding: 4px 8px;
                    }
                }
                
                /* Animations légères */
                a {
                    transition: color 0.2s ease;
                }
                
                img {
                    transition: transform 0.2s ease;
                }
                
                img:hover {
                    transform: scale(1.02);
                }
                
                /* Focus pour l'accessibilité */
                a:focus {
                    outline: 2px solid #0366"""
Composant éditeur de texte BlueNotebook avec coloration syntaxique PyQt5
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                           QDialog, QHBoxLayout, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (QFont, QTextCharFormat, QColor, QSyntaxHighlighter, 
                       QTextDocument, QKeySequence)
import re

class MarkdownHighlighter(QSyntaxHighlighter):
    """Coloration syntaxique pour Markdown"""
    
    def __init__(self, document):
        super().__init__(document)
        self.setup_formats()
        
    def setup_formats(self):
        """Configuration des formats de coloration"""
        # Format pour les titres
        self.title_formats = []
        for i in range(1, 7):
            format = QTextCharFormat()
            format.setForeground(QColor("#2c3e50"))
            format.setFontWeight(QFont.Bold)
            format.setFontPointSize(16 - i)
            self.title_formats.append(format)
            
        # Format pour le gras
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Bold)
        self.bold_format.setForeground(QColor("#2c3e50"))
        
        # Format pour l'italique
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor("#7f8c8d"))
        
        # Format pour le code inline
        self.code_format = QTextCharFormat()
        self.code_format.setForeground(QColor("#e74c3c"))
        self.code_format.setBackground(QColor("#f8f9fa"))
        self.code_format.setFontFamily("Consolas, Monaco, monospace")
        
        # Format pour les liens
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#3498db"))
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        
        # Format pour les citations
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(QColor("#95a5a6"))
        self.quote_format.setFontItalic(True)
        
        # Format pour les listes
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#8e44ad"))
        
        # Format pour le code en bloc
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setBackground(QColor("#f8f9fa"))
        self.code_block_format.setForeground(QColor("#2c3e50"))
        self.code_block_format.setFontFamily("Consolas, Monaco, monospace")
        
    def highlightBlock(self, text):
        """Coloration d'un bloc de texte"""
        # Titres (# ## ### etc.)
        title_pattern = r'^(#{1,6})\s+(.+)#!/bin/bash

# Script de création de la structure de projet pour BlueNotebook - Éditeur Markdown Python
# Usage: ./setup_bluenotebook.sh [nom_du_projet]

PROJECT_NAME=${1:-"bluenotebook"}

echo "🚀 Création du projet $PROJECT_NAME..."

# Création du dossier principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Création de la structure des dossiers
echo "📁 Création de la structure des dossiers..."
mkdir -p gui
mkdir -p core
mkdir -p resources/icons
mkdir -p tests

# Création des fichiers __init__.py
echo "📄 Création des fichiers __init__.py..."
touch gui/__init__.py
touch core/__init__.py
touch tests/__init__.py

# Création du fichier principal
echo "📄 Création du fichier main.py..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Éditeur de texte Markdown BlueNotebook
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Création des fichiers GUI
echo "📄 Création des fichiers GUI..."

cat > gui/main_window.py << 'EOF'
"""
Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QMenuBar, QMenu, QAction, QFileDialog, 
                           QMessageBox, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        
        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        # Charger le contenu par défaut
        self.new_file()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("BlueNotebook - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central avec splitter horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Zone d'édition
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)
        
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        new_action = QAction("&Nouveau", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Créer un nouveau fichier")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Ouvrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Ouvrir un fichier existant")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Sauvegarder le fichier")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Sauvegarder &sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Sauvegarder sous un nouveau nom")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exporter HTML...", self)
        export_action.setStatusTip("Exporter en HTML")
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quitter l'application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")
        
        undo_action = QAction("&Annuler", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Rétablir", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Rechercher", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        
        toggle_preview = QAction("&Basculer l'aperçu", self)
        toggle_preview.setShortcut("F5")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self.statusbar.addWidget(self.file_label)
        
        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)
        
        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)
        
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()
        
        # Démarrer le timer pour la mise à jour de l'aperçu
        self.update_timer.start(300)  # 300ms de délai
        
    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        self.preview.update_content(content)
        
    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)
            
        if self.is_modified:
            self.setWindowTitle(f"BlueNotebook - {filename} *")
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(f"BlueNotebook - {filename}")
            self.modified_label.setText("")
            
    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        
        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")
        
    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            self.editor.set_text("""# Bienvenue dans BlueNotebook

## Éditeur Markdown moderne

**BlueNotebook** est un éditeur de texte Markdown avec aperçu en temps réel.

### Fonctionnalités

- ✏️ **Édition** avec coloration syntaxique
- 👀 **Aperçu HTML** en temps réel
- 💾 **Sauvegarde** automatique
- 🚀 **Interface moderne** avec PyQt5

### Syntaxe Markdown

Voici quelques exemples de syntaxe Markdown :

#### Mise en forme du texte
- **Gras** : `**texte**` ou `__texte__`
- *Italique* : `*texte*` ou `_texte_`
- `Code inline` : `code`

#### Listes
1. Premier élément
2. Deuxième élément
   - Sous-élément
   - Autre sous-élément

#### Code
```python
def hello_world():
    print("Hello, BlueNotebook!")
```

#### Citations
> Ceci est une citation
> sur plusieurs lignes

#### Liens et images
[Lien vers un site](https://example.com)

---

Commencez à taper pour voir la magie opérer ! ✨
""")
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()
        
    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)"
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.editor.set_text(content)
                    self.current_file = filename
                    self.is_modified = False
                    self.update_title()
                    self.update_stats()
                    self.update_preview()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Impossible d'ouvrir le fichier :\n{str(e)}"
                    )
                    
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith(('.md', '.markdown', '.txt')):
                filename += '.md'
            
            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )
            
    def export_html(self):
        """Exporter en HTML"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            "",
            "Fichiers HTML (*.html);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith('.html'):
                filename += '.html'
                
            try:
                html_content = self.preview.get_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'exporter en HTML :\n{str(e)}"
                )
                
    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()
            
    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            """<h2>BlueNotebook 1.0</h2>
            <p><b>Éditeur Markdown moderne</b></p>
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML</li>
            <li>Interface moderne</li>
            </ul>
            <p>© 2024 BlueNotebook</p>"""
        )
        
    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified  # Retourner False si la sauvegarde a échoué
            elif reply == QMessageBox.Cancel:
                return False
                
        return True
        
    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
EOF

cat > gui/editor.py << 'EOF'
"""
Composant éditeur de texte BlueNotebook avec coloration syntaxique PyQt5
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QLabel, 
                           QDialog, QHBoxLayout, QLineEdit, QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (QFont, QTextCharFormat, QColor, QSyntaxHighlighter, 
                       QTextDocument, QKeySequence)
import re

class MarkdownHighlighter(QSyntaxHighlighter):
    """Coloration syntaxique pour Markdown"""
    
    def __init__(self, document):
        super().__init__(document)
        self.setup_formats()
        
    def setup_formats(self):
        """Configuration des formats de coloration"""
        # Format pour les titres
        self.title_formats = []
        for i in range(1, 7):
            format = QTextCharFormat()
            format.setForeground(QColor("#2c3e50"))
            format.setFontWeight(QFont.Bold)
            format.setFontPointSize(16 - i)
            self.title_formats.append(format)
            
        # Format pour le gras
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Bold)
        self.bold_format.setForeground(QColor("#2c3e50"))
        
        # Format pour l'italique
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor("#7f8c8d"))
        
        # Format pour le code inline
        self.code_format = QTextCharFormat()
        self.code_format.setForeground(QColor("#e74c3c"))
        self.code_format.setBackground(QColor("#f8f9fa"))
        self.code_format.setFontFamily("Consolas, Monaco, monospace")
        
        # Format pour les liens
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#3498db"))
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)
        
        # Format pour les citations
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(QColor("#95a5a6"))
        self.quote_format.setFontItalic(True)
        
        # Format pour les listes
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#8e44ad"))
        
        # Format pour le code en bloc
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setBackground(QColor("#f8f9fa"))
        self.code_block_format.setForeground(QColor("#2c3e50"))
        self.code_block_format.setFontFamily("Consolas, Monaco, monospace")
        
    def highlightBlock(self, text):
        """Coloration d'un bloc de texte"""
        # Titres (# ## ### etc.)
        title_pattern = r'^(#{1,6})\s+(.+)
EOF

cat > gui/preview.py << 'EOF'
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
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("👀 Aperçu")
        label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f8f9fa;")
        layout.addWidget(label)
        
        # Vue web pour l'aperçu HTML
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
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
        
    def get_css(self):
        """Retourner le CSS pour l'aperçu"""
        return """
                /* Focus pour l'accessibilité */
                a:focus {
                    outline: 2px solid #0366d6;
                    outline-offset: 2px;
                }
                
                /* Style pour les notes */
                .note {
                    background-color: #e3f2fd;
                    border-left: 4px solid #2196f3;
                    padding: 12px 16px;
                    margin: 16px 0;
                    border-radius: 4px;
                }
                
                .warning {
                    background-color: #fff3e0;
                    border-left: 4px solid #ff9800;
                    padding: 12px 16px;
                    margin: 16px 0;
                    border-radius: 4px;
                }
                
                .error {
                    background-color: #ffebee;
                    border-left: 4px solid #f44336;
                    padding: 12px 16px;
                    margin: 16px 0;
                    border-radius: 4px;
                }
            </style>
        </head>
        <body>
        """
        
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── tests/               # Tests unitaires
│   ├── __init__.py
│   ├── test_markdown_parser.py
│   └── test_file_handler.py
├── requirements.txt     # Dépendances Python
├── README.md           # Documentation
└── .gitignore         # Fichiers à ignorer
```

## 🛠️ Développement

### Architecture
- **PyQt5** : Interface graphique moderne
- **QWebEngine** : Rendu HTML parfait (Chromium intégré)
- **Python-Markdown** : Conversion Markdown → HTML
- **Pygments** : Coloration syntaxique du code

### Ajouter des fonctionnalités

1. **Extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Interface utilisateur** : Modifier les fichiers dans `gui/`
3. **Nouvelles fonctions** : Ajouter dans `core/`

### Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=.

# Tests spécifiques
pytest tests/test_markdown_parser.py
```

### Packaging

```bash
# Créer un exécutable (optionnel)
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

## 🎨 Personnalisation

### Modifier le CSS de l'aperçu
Éditez `gui/preview.py` dans la méthode `create_html_template()` pour personnaliser l'apparence de l'aperçu.

### Ajouter des extensions Markdown
Modifiez `setup_markdown()` dans `gui/preview.py` :

```python
self.md = markdown.Markdown(
    extensions=[
        'tables', 'fenced_code', 'codehilite',
        'toc', 'attr_list', 'def_list',
        'footnotes', 'md_in_html',
        'admonition',  # ← Nouvelle extension
    ]
)
```

## 🐛 Dépannage

### Problèmes courants

**PyQt5 ne s'installe pas** :
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine

# macOS avec Homebrew
brew install pyqt5

# Windows : utiliser pip normalement
pip install PyQt5 PyQtWebEngine
```

**QWebEngine ne fonctionne pas** :
- Vérifiez que PyQtWebEngine est bien installé
- Sur Linux, installez `qtwebengine5-dev`
- Redémarrez l'application après installation

**Problèmes de police** :
- Modifiez la police dans `gui/editor.py`
- Installez les polices système manquantes

## 🗺️ Roadmap

### Version actuelle (1.0)
- [x] Éditeur avec coloration syntaxique
- [x] Aperçu HTML en temps réel
- [x] Gestion de fichiers complète
- [x] Export HTML
- [x] Interface PyQt5 moderne

### Prochaines versions
- [ ] **Thèmes personnalisables** (clair/sombre)
- [ ] **Mode plein écran** pour l'écriture
- [ ] **Export PDF** direct
- [ ] **Gestionnaire de projets** multi-fichiers
- [ ] **Plugin system** pour extensions
- [ ] **Aperçu synchronisé** (scroll lié)
- [ ] **Mode présentations** (révéal.js)
- [ ] **Collaboration en temps réel**
- [ ] **Support LaTeX/MathJax** pour formules
- [ ] **Gestionnaire d'images** intégré

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. **Fork** le projet
2. **Créer une branche** pour votre fonctionnalité
3. **Commiter** vos changements
4. **Push** vers la branche
5. **Ouvrir une Pull Request**

### Guidelines
- Respecter le style de code existant
- Ajouter des tests pour les nouvelles fonctionnalités
- Mettre à jour la documentation si nécessaire
- Tester sur plusieurs plateformes si possible

## 📄 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

## 🙏 Remerciements

- **Python-Markdown** pour le traitement Markdown
- **PyQt5** pour l'interface graphique
- **Pygments** pour la coloration syntaxique
- **QWebEngine** pour le rendu HTML parfait

---

**BlueNotebook** - Un éditeur Markdown moderne pour tous vos besoins d'écriture ! 🔵📓

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface PyQt5"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "⚡ Fonctionnalités incluses :"
echo "   - Interface PyQt5 moderne"
echo "   - Aperçu HTML parfait avec QWebEngine"
echo "   - Coloration syntaxique avancée"
echo "   - Export HTML professionnel"
echo "   - Recherche et remplacement"
echo ""
echo "🚀 Bon développement avec BlueNotebook !"
        for match in re.finditer(title_pattern, text, re.MULTILINE):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                self.setFormat(match.start(), match.end() - match.start(), 
                             self.title_formats[level])
        
        # Gras (**text** ou __text__)
        bold_pattern = r'(\*\*|__)([^*_]+)(\*\*|__)'
        for match in re.finditer(bold_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
            
        # Italique (*text* ou _text_)
        italic_pattern = r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)'
        for match in re.finditer(italic_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
            
        # Code inline (`code`)
        code_pattern = r'`([^#!/bin/bash

# Script de création de la structure de projet pour BlueNotebook - Éditeur Markdown Python
# Usage: ./setup_bluenotebook.sh [nom_du_projet]

PROJECT_NAME=${1:-"bluenotebook"}

echo "🚀 Création du projet $PROJECT_NAME..."

# Création du dossier principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Création de la structure des dossiers
echo "📁 Création de la structure des dossiers..."
mkdir -p gui
mkdir -p core
mkdir -p resources/icons
mkdir -p tests

# Création des fichiers __init__.py
echo "📄 Création des fichiers __init__.py..."
touch gui/__init__.py
touch core/__init__.py
touch tests/__init__.py

# Création du fichier principal
echo "📄 Création du fichier main.py..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Éditeur de texte Markdown BlueNotebook
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Création des fichiers GUI
echo "📄 Création des fichiers GUI..."

cat > gui/main_window.py << 'EOF'
"""
Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QMenuBar, QMenu, QAction, QFileDialog, 
                           QMessageBox, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        
        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        # Charger le contenu par défaut
        self.new_file()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("BlueNotebook - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central avec splitter horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Zone d'édition
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)
        
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        new_action = QAction("&Nouveau", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Créer un nouveau fichier")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Ouvrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Ouvrir un fichier existant")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Sauvegarder le fichier")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Sauvegarder &sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Sauvegarder sous un nouveau nom")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exporter HTML...", self)
        export_action.setStatusTip("Exporter en HTML")
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quitter l'application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")
        
        undo_action = QAction("&Annuler", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Rétablir", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Rechercher", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        
        toggle_preview = QAction("&Basculer l'aperçu", self)
        toggle_preview.setShortcut("F5")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self.statusbar.addWidget(self.file_label)
        
        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)
        
        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)
        
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()
        
        # Démarrer le timer pour la mise à jour de l'aperçu
        self.update_timer.start(300)  # 300ms de délai
        
    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        self.preview.update_content(content)
        
    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)
            
        if self.is_modified:
            self.setWindowTitle(f"BlueNotebook - {filename} *")
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(f"BlueNotebook - {filename}")
            self.modified_label.setText("")
            
    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        
        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")
        
    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            self.editor.set_text("""# Bienvenue dans BlueNotebook

## Éditeur Markdown moderne

**BlueNotebook** est un éditeur de texte Markdown avec aperçu en temps réel.

### Fonctionnalités

- ✏️ **Édition** avec coloration syntaxique
- 👀 **Aperçu HTML** en temps réel
- 💾 **Sauvegarde** automatique
- 🚀 **Interface moderne** avec PyQt5

### Syntaxe Markdown

Voici quelques exemples de syntaxe Markdown :

#### Mise en forme du texte
- **Gras** : `**texte**` ou `__texte__`
- *Italique* : `*texte*` ou `_texte_`
- `Code inline` : `code`

#### Listes
1. Premier élément
2. Deuxième élément
   - Sous-élément
   - Autre sous-élément

#### Code
```python
def hello_world():
    print("Hello, BlueNotebook!")
```

#### Citations
> Ceci est une citation
> sur plusieurs lignes

#### Liens et images
[Lien vers un site](https://example.com)

---

Commencez à taper pour voir la magie opérer ! ✨
""")
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()
        
    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)"
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.editor.set_text(content)
                    self.current_file = filename
                    self.is_modified = False
                    self.update_title()
                    self.update_stats()
                    self.update_preview()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Impossible d'ouvrir le fichier :\n{str(e)}"
                    )
                    
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith(('.md', '.markdown', '.txt')):
                filename += '.md'
            
            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )
            
    def export_html(self):
        """Exporter en HTML"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            "",
            "Fichiers HTML (*.html);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith('.html'):
                filename += '.html'
                
            try:
                html_content = self.preview.get_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'exporter en HTML :\n{str(e)}"
                )
                
    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()
            
    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            """<h2>BlueNotebook 1.0</h2>
            <p><b>Éditeur Markdown moderne</b></p>
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML</li>
            <li>Interface moderne</li>
            </ul>
            <p>© 2024 BlueNotebook</p>"""
        )
        
    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified  # Retourner False si la sauvegarde a échoué
            elif reply == QMessageBox.Cancel:
                return False
                
        return True
        
    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
EOF

cat > gui/editor.py << 'EOF'
"""
Composant éditeur de texte BlueNotebook avec coloration Markdown
"""

import tkinter as tk
from tkinter import ttk

class MarkdownEditor:
    def __init__(self, parent):
        self.parent = parent
        self.on_text_change = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface d'édition"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Éditeur")
        label.pack(pady=(0, 5))
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
            bg="#f8f9fa",
            fg="#343a40",
            insertbackground="#007bff",
            selectbackground="#007bff",
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Événements
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_text_change)
        
    def _on_text_change(self, event=None):
        """Callback pour changement de texte"""
        if self.on_text_change:
            content = self.get_content()
            self.on_text_change(content)
            
    def get_content(self):
        """Récupérer le contenu"""
        return self.text_widget.get("1.0", tk.END + "-1c")
        
    def set_content(self, content):
        """Définir le contenu"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        
    def clear(self):
        """Vider l'éditeur"""
        self.text_widget.delete("1.0", tk.END)
EOF

cat > gui/preview.py << 'EOF'
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "🚀 Bon développement !"
        for match in re.finditer(title_pattern, text, re.MULTILINE):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                self.setFormat(match.start(), match.end() - match.start(), 
                             self.title_formats[level])
        
        # Gras (**text** ou __text__)
        bold_pattern = r'(\*\*|__)([^*_]+)(\*\*|__)'
        for match in re.finditer(bold_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
            
        # Italique (*text* ou _text_)
        italic_pattern = r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)'
        for match in re.finditer(italic_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
            
        # Code inline (`code`)
        code_pattern = r'`([^`]+)`'
        for match in re.finditer(code_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.code_format)
            
        # Liens [text](url)
        link_pattern = r'\[([^\]]+)\]\([^)]+\)'
        for match in re.finditer(link_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)
            
        # Citations (> text)
        quote_pattern = r'^>\s*(.+)
EOF

cat > gui/preview.py << 'EOF'
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "🚀 Bon développement !"
        for match in re.finditer(title_pattern, text, re.MULTILINE):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                self.setFormat(match.start(), match.end() - match.start(), 
                             self.title_formats[level])
        
        # Gras (**text** ou __text__)
        bold_pattern = r'(\*\*|__)([^*_]+)(\*\*|__)'
        for match in re.finditer(bold_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
            
        # Italique (*text* ou _text_)
        italic_pattern = r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)'
        for match in re.finditer(italic_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
            
        # Code inline (`code`)
        code_pattern = r'`([^#!/bin/bash

# Script de création de la structure de projet pour BlueNotebook - Éditeur Markdown Python
# Usage: ./setup_bluenotebook.sh [nom_du_projet]

PROJECT_NAME=${1:-"bluenotebook"}

echo "🚀 Création du projet $PROJECT_NAME..."

# Création du dossier principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Création de la structure des dossiers
echo "📁 Création de la structure des dossiers..."
mkdir -p gui
mkdir -p core
mkdir -p resources/icons
mkdir -p tests

# Création des fichiers __init__.py
echo "📄 Création des fichiers __init__.py..."
touch gui/__init__.py
touch core/__init__.py
touch tests/__init__.py

# Création du fichier principal
echo "📄 Création du fichier main.py..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Éditeur de texte Markdown BlueNotebook
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Création des fichiers GUI
echo "📄 Création des fichiers GUI..."

cat > gui/main_window.py << 'EOF'
"""
Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QMenuBar, QMenu, QAction, QFileDialog, 
                           QMessageBox, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        
        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        # Charger le contenu par défaut
        self.new_file()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("BlueNotebook - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central avec splitter horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Zone d'édition
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)
        
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        new_action = QAction("&Nouveau", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Créer un nouveau fichier")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Ouvrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Ouvrir un fichier existant")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Sauvegarder le fichier")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Sauvegarder &sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Sauvegarder sous un nouveau nom")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exporter HTML...", self)
        export_action.setStatusTip("Exporter en HTML")
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quitter l'application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")
        
        undo_action = QAction("&Annuler", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Rétablir", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Rechercher", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        
        toggle_preview = QAction("&Basculer l'aperçu", self)
        toggle_preview.setShortcut("F5")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self.statusbar.addWidget(self.file_label)
        
        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)
        
        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)
        
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()
        
        # Démarrer le timer pour la mise à jour de l'aperçu
        self.update_timer.start(300)  # 300ms de délai
        
    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        self.preview.update_content(content)
        
    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)
            
        if self.is_modified:
            self.setWindowTitle(f"BlueNotebook - {filename} *")
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(f"BlueNotebook - {filename}")
            self.modified_label.setText("")
            
    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        
        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")
        
    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            self.editor.set_text("""# Bienvenue dans BlueNotebook

## Éditeur Markdown moderne

**BlueNotebook** est un éditeur de texte Markdown avec aperçu en temps réel.

### Fonctionnalités

- ✏️ **Édition** avec coloration syntaxique
- 👀 **Aperçu HTML** en temps réel
- 💾 **Sauvegarde** automatique
- 🚀 **Interface moderne** avec PyQt5

### Syntaxe Markdown

Voici quelques exemples de syntaxe Markdown :

#### Mise en forme du texte
- **Gras** : `**texte**` ou `__texte__`
- *Italique* : `*texte*` ou `_texte_`
- `Code inline` : `code`

#### Listes
1. Premier élément
2. Deuxième élément
   - Sous-élément
   - Autre sous-élément

#### Code
```python
def hello_world():
    print("Hello, BlueNotebook!")
```

#### Citations
> Ceci est une citation
> sur plusieurs lignes

#### Liens et images
[Lien vers un site](https://example.com)

---

Commencez à taper pour voir la magie opérer ! ✨
""")
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()
        
    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)"
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.editor.set_text(content)
                    self.current_file = filename
                    self.is_modified = False
                    self.update_title()
                    self.update_stats()
                    self.update_preview()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Impossible d'ouvrir le fichier :\n{str(e)}"
                    )
                    
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith(('.md', '.markdown', '.txt')):
                filename += '.md'
            
            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )
            
    def export_html(self):
        """Exporter en HTML"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            "",
            "Fichiers HTML (*.html);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith('.html'):
                filename += '.html'
                
            try:
                html_content = self.preview.get_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'exporter en HTML :\n{str(e)}"
                )
                
    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()
            
    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            """<h2>BlueNotebook 1.0</h2>
            <p><b>Éditeur Markdown moderne</b></p>
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML</li>
            <li>Interface moderne</li>
            </ul>
            <p>© 2024 BlueNotebook</p>"""
        )
        
    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified  # Retourner False si la sauvegarde a échoué
            elif reply == QMessageBox.Cancel:
                return False
                
        return True
        
    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
EOF

cat > gui/editor.py << 'EOF'
"""
Composant éditeur de texte BlueNotebook avec coloration Markdown
"""

import tkinter as tk
from tkinter import ttk

class MarkdownEditor:
    def __init__(self, parent):
        self.parent = parent
        self.on_text_change = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface d'édition"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Éditeur")
        label.pack(pady=(0, 5))
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
            bg="#f8f9fa",
            fg="#343a40",
            insertbackground="#007bff",
            selectbackground="#007bff",
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Événements
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_text_change)
        
    def _on_text_change(self, event=None):
        """Callback pour changement de texte"""
        if self.on_text_change:
            content = self.get_content()
            self.on_text_change(content)
            
    def get_content(self):
        """Récupérer le contenu"""
        return self.text_widget.get("1.0", tk.END + "-1c")
        
    def set_content(self, content):
        """Définir le contenu"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        
    def clear(self):
        """Vider l'éditeur"""
        self.text_widget.delete("1.0", tk.END)
EOF

cat > gui/preview.py << 'EOF'
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "🚀 Bon développement !"
        for match in re.finditer(quote_pattern, text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.quote_format)
            
        # Listes (- * + 1.)
        list_pattern = r'^[\s]*[-\*\+][\s]+|^[\s]*\d+\.[\s]+'
        for match in re.finditer(list_pattern, text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.list_format)
            
        # Code en bloc (```)
        if text.strip().startswith('```') or text.strip().startswith('    '):
            self.setFormat(0, len(text), self.code_block_format)

class FindDialog(QDialog):
    """Dialogue de recherche"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface de recherche"""
        self.setWindowTitle("Rechercher")
        self.setModal(True)
        self.resize(400, 100)
        
        layout = QVBoxLayout()
        
        # Champ de recherche
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher :"))
        
        self.search_edit = QLineEdit()
        self.search_edit.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.find_button = QPushButton("Suivant")
        self.find_button.clicked.connect(self.find_next)
        self.find_button.setDefault(True)
        button_layout.addWidget(self.find_button)
        
        self.replace_button = QPushButton("Remplacer")
        self.replace_button.clicked.connect(self.replace_current)
        button_layout.addWidget(self.replace_button)
        
        close_button = QPushButton("Fermer")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Champ de remplacement
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Remplacer par :"))
        
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        
        layout.addLayout(replace_layout)
        
        self.setLayout(layout)
        
    def find_next(self):
        """Rechercher le texte suivant"""
        if hasattr(self.parent(), 'find_text'):
            self.parent().find_text(self.search_edit.text())
            
    def replace_current(self):
        """Remplacer le texte actuel"""
        if hasattr(self.parent(), 'replace_text'):
            self.parent().replace_text(
                self.search_edit.text(), 
                self.replace_edit.text()
            )

class MarkdownEditor(QWidget):
    """Éditeur de texte avec coloration syntaxique Markdown"""
    
    textChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.find_dialog = None
        
    def setup_ui(self):
        """Configuration de l'interface d'édition"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        label = QLabel("📝 Éditeur")
        label.setStyleSheet("font-weight: bold; padding: 5px; background-color: #f8f9fa;")
        layout.addWidget(label)
        
        # Zone de texte
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)  # Texte brut seulement
        
        # Configuration de la police
        font = QFont("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(11)
        self.text_edit.setFont(font)
        
        # Style
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                selection-color: white;
            }
        """)
        
        # Coloration syntaxique
        self.highlighter = MarkdownHighlighter(self.text_edit.document())
        
        # Connexions
        self.text_edit.textChanged.connect(self.textChanged.emit)
        
        layout.addWidget(self.text_edit)
        self.setLayout(layout)
        
    def get_text(self):
        """Récupérer le texte"""
        return self.text_edit.toPlainText()
        
    def set_text(self, text):
        """Définir le texte"""
        self.text_edit.setPlainText(text)
        
    def undo(self):
        """Annuler"""
        self.text_edit.undo()
        
    def redo(self):
        """Rétablir"""
        self.text_edit.redo()
        
    def show_find_dialog(self):
        """Afficher le dialogue de recherche"""
        if not self.find_dialog:
            self.find_dialog = FindDialog(self)
            
        self.find_dialog.show()
        self.find_dialog.search_edit.setFocus()
        
    def find_text(self, text):
        """Rechercher du texte"""
        cursor = self.text_edit.textCursor()
        found = self.text_edit.find(text)
        
        if not found:
            # Recommencer depuis le début
            cursor.movePosition(cursor.Start)
            self.text_edit.setTextCursor(cursor)
            self.text_edit.find(text)
            
    def replace_text(self, find_text, replace_text):
        """Remplacer du texte"""
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == find_text:
            cursor.insertText(replace_text)
        
        # Rechercher la prochaine occurrence
        self.find_text(find_text)
EOF

cat > gui/preview.py << 'EOF'
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "🚀 Bon développement !"
        for match in re.finditer(title_pattern, text, re.MULTILINE):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                self.setFormat(match.start(), match.end() - match.start(), 
                             self.title_formats[level])
        
        # Gras (**text** ou __text__)
        bold_pattern = r'(\*\*|__)([^*_]+)(\*\*|__)'
        for match in re.finditer(bold_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)
            
        # Italique (*text* ou _text_)
        italic_pattern = r'(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)'
        for match in re.finditer(italic_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
            
        # Code inline (`code`)
        code_pattern = r'`([^#!/bin/bash

# Script de création de la structure de projet pour BlueNotebook - Éditeur Markdown Python
# Usage: ./setup_bluenotebook.sh [nom_du_projet]

PROJECT_NAME=${1:-"bluenotebook"}

echo "🚀 Création du projet $PROJECT_NAME..."

# Création du dossier principal
mkdir -p "$PROJECT_NAME"
cd "$PROJECT_NAME"

# Création de la structure des dossiers
echo "📁 Création de la structure des dossiers..."
mkdir -p gui
mkdir -p core
mkdir -p resources/icons
mkdir -p tests

# Création des fichiers __init__.py
echo "📄 Création des fichiers __init__.py..."
touch gui/__init__.py
touch core/__init__.py
touch tests/__init__.py

# Création du fichier principal
echo "📄 Création du fichier main.py..."
cat > main.py << 'EOF'
#!/usr/bin/env python3
"""
Éditeur de texte Markdown BlueNotebook
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
EOF

# Création des fichiers GUI
echo "📄 Création des fichiers GUI..."

cat > gui/main_window.py << 'EOF'
"""
Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                           QSplitter, QMenuBar, QMenu, QAction, QFileDialog, 
                           QMessageBox, QStatusBar, QLabel)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.is_modified = False
        
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        
        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)
        
        # Charger le contenu par défaut
        self.new_file()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle("BlueNotebook - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)
        
        # Widget central avec splitter horizontal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Zone d'édition
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)
        
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()
        
        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        
        new_action = QAction("&Nouveau", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Créer un nouveau fichier")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Ouvrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Ouvrir un fichier existant")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Sauvegarder le fichier")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Sauvegarder &sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Sauvegarder sous un nouveau nom")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Exporter HTML...", self)
        export_action.setStatusTip("Exporter en HTML")
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quitter l'application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")
        
        undo_action = QAction("&Annuler", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Rétablir", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        find_action = QAction("&Rechercher", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_dialog)
        edit_menu.addAction(find_action)
        
        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")
        
        toggle_preview = QAction("&Basculer l'aperçu", self)
        toggle_preview.setShortcut("F5")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)
        
        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        
        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self.statusbar.addWidget(self.file_label)
        
        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)
        
        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)
        
    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()
        
        # Démarrer le timer pour la mise à jour de l'aperçu
        self.update_timer.start(300)  # 300ms de délai
        
    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        self.preview.update_content(content)
        
    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)
            
        if self.is_modified:
            self.setWindowTitle(f"BlueNotebook - {filename} *")
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(f"BlueNotebook - {filename}")
            self.modified_label.setText("")
            
    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)
        
        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")
        
    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            self.editor.set_text("""# Bienvenue dans BlueNotebook

## Éditeur Markdown moderne

**BlueNotebook** est un éditeur de texte Markdown avec aperçu en temps réel.

### Fonctionnalités

- ✏️ **Édition** avec coloration syntaxique
- 👀 **Aperçu HTML** en temps réel
- 💾 **Sauvegarde** automatique
- 🚀 **Interface moderne** avec PyQt5

### Syntaxe Markdown

Voici quelques exemples de syntaxe Markdown :

#### Mise en forme du texte
- **Gras** : `**texte**` ou `__texte__`
- *Italique* : `*texte*` ou `_texte_`
- `Code inline` : `code`

#### Listes
1. Premier élément
2. Deuxième élément
   - Sous-élément
   - Autre sous-élément

#### Code
```python
def hello_world():
    print("Hello, BlueNotebook!")
```

#### Citations
> Ceci est une citation
> sur plusieurs lignes

#### Liens et images
[Lien vers un site](https://example.com)

---

Commencez à taper pour voir la magie opérer ! ✨
""")
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()
        
    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)"
            )
            
            if filename:
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    self.editor.set_text(content)
                    self.current_file = filename
                    self.is_modified = False
                    self.update_title()
                    self.update_stats()
                    self.update_preview()
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Impossible d'ouvrir le fichier :\n{str(e)}"
                    )
                    
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith(('.md', '.markdown', '.txt')):
                filename += '.md'
            
            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2000)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )
            
    def export_html(self):
        """Exporter en HTML"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            "",
            "Fichiers HTML (*.html);;Tous les fichiers (*)"
        )
        
        if filename:
            if not filename.endswith('.html'):
                filename += '.html'
                
            try:
                html_content = self.preview.get_html()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"Impossible d'exporter en HTML :\n{str(e)}"
                )
                
    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()
            
    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            """<h2>BlueNotebook 1.0</h2>
            <p><b>Éditeur Markdown moderne</b></p>
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML</li>
            <li>Interface moderne</li>
            </ul>
            <p>© 2024 BlueNotebook</p>"""
        )
        
    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save
            )
            
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified  # Retourner False si la sauvegarde a échoué
            elif reply == QMessageBox.Cancel:
                return False
                
        return True
        
    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()
EOF

cat > gui/editor.py << 'EOF'
"""
Composant éditeur de texte BlueNotebook avec coloration Markdown
"""

import tkinter as tk
from tkinter import ttk

class MarkdownEditor:
    def __init__(self, parent):
        self.parent = parent
        self.on_text_change = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface d'édition"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Éditeur")
        label.pack(pady=(0, 5))
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
            bg="#f8f9fa",
            fg="#343a40",
            insertbackground="#007bff",
            selectbackground="#007bff",
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Événements
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_text_change)
        
    def _on_text_change(self, event=None):
        """Callback pour changement de texte"""
        if self.on_text_change:
            content = self.get_content()
            self.on_text_change(content)
            
    def get_content(self):
        """Récupérer le contenu"""
        return self.text_widget.get("1.0", tk.END + "-1c")
        
    def set_content(self, content):
        """Définir le contenu"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        
    def clear(self):
        """Vider l'éditeur"""
        self.text_widget.delete("1.0", tk.END)
EOF

cat > gui/preview.py << 'EOF'
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
EOF

# Création des fichiers Core
echo "📄 Création des fichiers Core..."

cat > core/markdown_parser.py << 'EOF'
"""
Gestionnaire de parsing et conversion Markdown
"""

import markdown
from markdown.extensions import tables, fenced_code, toc

class MarkdownParser:
    def __init__(self):
        self.md = markdown.Markdown(
            extensions=[
                'tables',
                'fenced_code', 
                'toc',
                'codehilite'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight'
                }
            }
        )
    
    def to_html(self, markdown_text):
        """Convertir Markdown vers HTML"""
        try:
            return self.md.convert(markdown_text)
        except Exception as e:
            return f"<p>Erreur de conversion: {e}</p>"
    
    def reset(self):
        """Réinitialiser le parser"""
        self.md.reset()
EOF

cat > core/file_handler.py << 'EOF'
"""
Gestionnaire de fichiers pour l'éditeur
"""

import os
from pathlib import Path

class FileHandler:
    SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.txt']
    
    @staticmethod
    def read_file(file_path):
        """Lire un fichier"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # Tentative avec autre encodage
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    @staticmethod
    def write_file(file_path, content):
        """Écrire un fichier"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def is_markdown_file(file_path):
        """Vérifier si le fichier est un Markdown"""
        return Path(file_path).suffix.lower() in FileHandler.SUPPORTED_EXTENSIONS
    
    @staticmethod
    def get_backup_path(file_path):
        """Générer un chemin de sauvegarde"""
        path = Path(file_path)
        return path.with_suffix(path.suffix + '.bak')
EOF

# Création des fichiers de ressources
echo "📄 Création des fichiers de ressources..."

cat > resources/styles.css << 'EOF'
/* Styles CSS pour l'aperçu HTML */

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
}

h1, h2, h3, h4, h5, h6 {
    color: #2c3e50;
    margin-top: 24px;
    margin-bottom: 16px;
}

h1 { font-size: 2em; border-bottom: 2px solid #eaecef; padding-bottom: 8px; }
h2 { font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }
h3 { font-size: 1.25em; }

code {
    background-color: #f6f8fa;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
    font-size: 0.9em;
}

pre {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}

pre code {
    background: none;
    padding: 0;
}

blockquote {
    border-left: 4px solid #dfe2e5;
    padding-left: 16px;
    color: #6a737d;
    margin: 0;
    margin-bottom: 16px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 16px;
}

th, td {
    border: 1px solid #dfe2e5;
    padding: 8px 12px;
    text-align: left;
}

th {
    background-color: #f6f8fa;
    font-weight: 600;
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
}

.highlight {
    background-color: #f6f8fa;
    padding: 16px;
    border-radius: 6px;
    overflow-x: auto;
}
EOF

# Création du fichier requirements.txt
echo "📄 Création du fichier requirements.txt..."
cat > requirements.txt << 'EOF'
# Dépendances pour BlueNotebook - Éditeur Markdown Python

# Interface graphique PyQt5 avec navigateur intégré
PyQt5>=5.15.0
PyQtWebEngine>=5.15.0

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique alternative (tkinter)
# tkinter est inclus avec Python (bibliothèque standard)
# Si vous préférez revenir à tkinter :
# tkhtmlview>=0.2.0

# Export PDF (optionnel pour fonctionnalités avancées)
# weasyprint>=59.0
# reportlab>=4.0.0

# Traitement d'images (optionnel)
# Pillow>=10.0.0

# Tests et développement
pytest>=7.0.0
pytest-cov>=4.0.0

# Outils de développement (optionnel)
# black>=23.0.0      # Formatage de code
# flake8>=6.0.0      # Linting
# mypy>=1.0.0        # Vérification de types
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."
mkdir -p tests/gui tests/core

cat > tests/test_markdown_parser.py << 'EOF'
"""
Tests pour le parser Markdown
"""

import pytest
from core.markdown_parser import MarkdownParser

def test_markdown_parser_basic():
    parser = MarkdownParser()
    
    # Test titre
    result = parser.to_html("# Titre")
    assert "<h1>Titre</h1>" in result
    
    # Test paragraphe
    result = parser.to_html("Un paragraphe simple")
    assert "<p>Un paragraphe simple</p>" in result
    
    # Test code
    result = parser.to_html("`code`")
    assert "<code>code</code>" in result

def test_markdown_parser_table():
    parser = MarkdownParser()
    
    markdown_table = """
| Col1 | Col2 |
|------|------|
| A    | B    |
"""
    
    result = parser.to_html(markdown_table)
    assert "<table>" in result
    assert "<th>Col1</th>" in result
EOF

cat > tests/test_file_handler.py << 'EOF'
"""
Tests pour le gestionnaire de fichiers
"""

import pytest
import tempfile
import os
from core.file_handler import FileHandler

def test_file_handler_read_write():
    content = "# Test\n\nContenu de test"
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(content)
        temp_path = f.name
    
    try:
        # Test lecture
        read_content = FileHandler.read_file(temp_path)
        assert read_content == content
        
        # Test écriture
        new_content = "# Nouveau contenu"
        FileHandler.write_file(temp_path, new_content)
        
        read_new = FileHandler.read_file(temp_path)
        assert read_new == new_content
        
    finally:
        os.unlink(temp_path)

def test_is_markdown_file():
    assert FileHandler.is_markdown_file("test.md") == True
    assert FileHandler.is_markdown_file("test.markdown") == True
    assert FileHandler.is_markdown_file("test.txt") == True
    assert FileHandler.is_markdown_file("test.py") == False
EOF

# Création du fichier .gitignore
echo "📄 Création du fichier .gitignore..."
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Tests
.pytest_cache/
.coverage
htmlcov/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Backups
*.bak
*.tmp
EOF

# Rendre le script principal exécutable
chmod +x main.py

# Message de fin
echo ""
echo "✅ Structure du projet '$PROJECT_NAME' créée avec succès !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. cd $PROJECT_NAME"
echo "   2. python -m venv venv"
echo "   3. source venv/bin/activate  # ou venv\\Scripts\\activate sur Windows"
echo "   4. pip install -r requirements.txt"
echo "   5. python main.py"
echo ""
echo "🔧 Pour développer :"
echo "   - Modifier les fichiers dans gui/ pour l'interface"
echo "   - Modifier les fichiers dans core/ pour la logique"
echo "   - Lancer les tests avec: pytest tests/"
echo ""
echo "🚀 Bon développement !"
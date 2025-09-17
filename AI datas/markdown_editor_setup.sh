#!/bin/bash

# Script de création de la structure de projet pour éditeur Markdown Python
# Usage: ./setup_markdown_editor.sh [nom_du_projet]

PROJECT_NAME=${1:-"editeur_markdown"}

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
Éditeur de texte Markdown
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
Fenêtre principale de l'éditeur Markdown
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Éditeur Markdown")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Frame principal avec séparateur
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone d'édition
        self.editor = MarkdownEditor(main_frame)
        main_frame.add(self.editor.frame, weight=1)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview(main_frame)
        main_frame.add(self.preview.frame, weight=1)
        
        # Connecter l'éditeur au preview
        self.editor.on_text_change = self.preview.update_preview
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Raccourcis clavier
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        
    def new_file(self):
        """Créer un nouveau fichier"""
        self.editor.clear()
        self.current_file = None
        self.root.title("Éditeur Markdown - Nouveau fichier")
        
    def open_file(self):
        """Ouvrir un fichier"""
        filename = filedialog.askopenfilename(
            title="Ouvrir un fichier Markdown",
            filetypes=[("Fichiers Markdown", "*.md"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_content(content)
                self.current_file = filename
                self.root.title(f"Éditeur Markdown - {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")
                
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier",
            defaultextension=".md",
            filetypes=[("Fichiers Markdown", "*.md"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
            self.root.title(f"Éditeur Markdown - {filename}")
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_content())
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")
            
    def quit_app(self):
        """Quitter l'application"""
        self.root.quit()
        
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()
EOF

cat > gui/editor.py << 'EOF'
"""
Composant éditeur de texte avec coloration Markdown
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
Composant d'aperçu HTML du Markdown
"""

import tkinter as tk
from tkinter import ttk
import tkinter.html as tkhtml  # Fallback simple
import markdown

class MarkdownPreview:
    def __init__(self, parent):
        self.parent = parent
        self.md = markdown.Markdown(extensions=['tables', 'fenced_code', 'toc'])
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Aperçu")
        label.pack(pady=(0, 5))
        
        # Zone de prévisualisation avec scrollbar
        preview_frame = ttk.Frame(self.frame)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Utilisation d'un Text widget en lecture seule comme fallback
        self.preview_widget = tk.Text(
            preview_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            font=("Arial", 11),
            bg="white",
            fg="#333333"
        )
        
        scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_widget.yview)
        self.preview_widget.configure(yscrollcommand=scrollbar.set)
        
        self.preview_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def update_preview(self, markdown_content):
        """Mettre à jour l'aperçu"""
        try:
            # Conversion Markdown vers HTML
            html_content = self.md.convert(markdown_content)
            
            # Affichage simple dans le Text widget
            self.preview_widget.configure(state=tk.NORMAL)
            self.preview_widget.delete("1.0", tk.END)
            
            # Insertion du contenu (version simplifiée sans HTML)
            # TODO: Améliorer avec un vrai rendu HTML
            self.preview_widget.insert("1.0", self._html_to_text(html_content))
            
            self.preview_widget.configure(state=tk.DISABLED)
            
        except Exception as e:
            self.preview_widget.configure(state=tk.NORMAL)
            self.preview_widget.delete("1.0", tk.END)
            self.preview_widget.insert("1.0", f"Erreur de prévisualisation: {e}")
            self.preview_widget.configure(state=tk.DISABLED)
            
    def _html_to_text(self, html_content):
        """Conversion basique HTML vers texte (temporaire)"""
        import re
        # Suppression des balises HTML basiques
        text = re.sub('<[^<]+?>', '', html_content)
        # Décodage des entités HTML
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        return text
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
# Dépendances pour l'éditeur Markdown Python

# Traitement Markdown
markdown>=3.4.0
pymdown-extensions>=10.0.0

# Coloration syntaxique
Pygments>=2.15.0

# Interface graphique avancée (optionnel)
# PyQt5>=5.15.0
# ou
# tkinter (inclus avec Python)

# Export PDF (optionnel)
# weasyprint>=59.0

# Tests
pytest>=7.0.0
pytest-cov>=4.0.0
EOF

# Création du fichier README.md
echo "📄 Création du fichier README.md..."
cat > README.md << 'EOF'
# Éditeur Markdown Python

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
cd editeur_markdown
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
editeur_markdown/
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
#!/bin/bash

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
BlueNotebook - Éditeur de texte Markdown avec PyQt5
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("BlueNotebook")
        
        # Créer et afficher la fenêtre principale
        window = MainWindow()
        window.show()
        
        # Lancer la boucle d'événements
        sys.exit(app.exec_())
        
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
        
        # Définir l'icône de l'application
        self.set_application_icon()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #dee2e6;
                border: 1px solid #adb5bd;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """)
        
        # Zone d'édition (gauche)
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)
        
        # Zone d'aperçu (droite)  
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)
        
        # Configuration du splitter
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])
        
        # Empêcher la fermeture complète des panneaux
        splitter.setCollapsible(0, False)  # Éditeur
        splitter.setCollapsible(1, False)  # Aperçu
        
        # Tailles minimales pour éviter les problèmes d'affichage
        self.editor.setMinimumWidth(300)
        self.preview.setMinimumWidth(300)
        
        # Ajouter le splitter au layout principal
        main_layout.addWidget(splitter)
        
    def set_application_icon(self):
        """Définir l'icône de l'application"""
        import os
        
        # Chemins possibles pour l'icône
        icon_paths = [
            "resources/icons/bluenotebook.ico",
            "resources/icons/bluenotebook.png",
            "resources/icons/bluenotebook_64.png",
            "bluenotebook.ico",
            "bluenotebook.png"
        ]
        
        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        # Définir aussi l'icône de l'application
                        from PyQt5.QtWidgets import QApplication
                        QApplication.instance().setWindowIcon(icon)
                        print(f"✅ Icône chargée : {icon_path}")
                        return
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de {icon_path}: {e}")
                    continue
        
        print("ℹ️ Aucune icône trouvée, utilisation de l'icône par défaut")
        
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
        title_pattern = r'^(#{1,6})\s+(.+)$'
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
        quote_pattern = r'^>\s*(.+)$'
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
        self.resize(400, 150)
        
        layout = QVBoxLayout()
        
        # Champ de recherche
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Rechercher :"))
        
        self.search_edit = QLineEdit()
        self.search_edit.returnPressed.connect(self.find_next)
        search_layout.addWidget(self.search_edit)
        
        layout.addLayout(search_layout)
        
        # Champ de remplacement
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Remplacer par :"))
        
        self.replace_edit = QLineEdit()
        replace_layout.addWidget(self.replace_edit)
        
        layout.addLayout(replace_layout)
        
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
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Label compact en haut
        label = QLabel("📝 Éditeur")
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
        
        # Zone de texte - prend tout l'espace restant
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)  # Texte brut seulement
        
        # Configuration de la police
        font = QFont("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(11)
        self.text_edit.setFont(font)
        
        # Style amélioré
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                selection-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }
            
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """)
        
        # Coloration syntaxique
        self.highlighter = MarkdownHighlighter(self.text_edit.document())
        
        # Connexions
        self.text_edit.textChanged.connect(self.textChanged.emit)
        
        # L'éditeur prend tout l'espace disponible
        layout.addWidget(self.text_edit, 1)  # stretch factor = 1
        
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

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
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

## 🛠️ Développement

### Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=.
```

### Personnalisation

- **CSS de l'aperçu** : Modifier `gui/preview.py`
- **Extensions Markdown** : Modifier `setup_markdown()` dans `gui/preview.py`
- **Interface** : Modifier les fichiers dans `gui/`

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

## 📄 Licence

MIT License

---

**BlueNotebook** - Un éditeur Markdown moderne pour tous vos besoins d'écriture ! 🔵📓
EOF

# Création des fichiers de test
echo "📄 Création des fichiers de test..."

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
echo "🎨 Création des icônes par défaut..."
cd resources/icons
python3 create_icons.py 2>/dev/null || python create_icons.py 2>/dev/null || echo "⚠️ Impossible de créer les icônes automatiquement"
cd ../..
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
echo "🎨 Personnaliser l'icône :"
echo "   - Remplacez resources/icons/bluenotebook.ico (Windows)"
echo "   - Ou resources/icons/bluenotebook.png (multiplateforme)"
echo "   - Formats supportés: .ico, .png, .svg (64x64 recommandé)"
echo ""
echo "⚡ Fonctionnalités incluses :"
echo "   - Interface PyQt5 moderne"
echo "   - Aperçu HTML parfait avec QWebEngine"
echo "   - Coloration syntaxique avancée"
echo "   - Export HTML professionnel"
echo "   - Recherche et remplacement"
echo "   - Icône personnalisable"
echo ""
echo "🚀 Bon développement avec BlueNotebook !"
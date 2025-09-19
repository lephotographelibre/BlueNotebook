"""
Composant éditeur de texte BlueNotebook avec coloration syntaxique PyQt5
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QLabel,
    QDialog,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QFont,
    QTextCharFormat,
    QColor,
    QSyntaxHighlighter,
    QTextDocument,
    QKeySequence,
)
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
        title_pattern = r"^(#{1,6})\s+(.+)$"
        for match in re.finditer(title_pattern, text, re.MULTILINE):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                self.setFormat(
                    match.start(),
                    match.end() - match.start(),
                    self.title_formats[level],
                )

        # Gras (**text** ou __text__)
        bold_pattern = r"(\*\*|__)([^*_]+)(\*\*|__)"
        for match in re.finditer(bold_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)

        # Italique (*text* ou _text_)
        italic_pattern = r"(?<!\*)\*([^*]+)\*(?!\*)|(?<!_)_([^_]+)_(?!_)"
        for match in re.finditer(italic_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.italic_format
            )

        # Code inline (`code`)
        code_pattern = r"`([^`]+)`"
        for match in re.finditer(code_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.code_format)

        # Liens [text](url)
        link_pattern = r"\[([^\]]+)\]\([^)]+\)"
        for match in re.finditer(link_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)

        # Citations (> text)
        quote_pattern = r"^>\s*(.+)$"
        for match in re.finditer(quote_pattern, text, re.MULTILINE):
            self.setFormat(
                match.start(), match.end() - match.start(), self.quote_format
            )

        # Listes (- * + 1.)
        list_pattern = r"^[\s]*[-\*\+][\s]+|^[\s]*\d+\.[\s]+"
        for match in re.finditer(list_pattern, text, re.MULTILINE):
            self.setFormat(match.start(), match.end() - match.start(), self.list_format)

        # Code en bloc (```)
        if text.strip().startswith("```") or text.strip().startswith("    "):
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
        if hasattr(self.parent(), "find_text"):
            self.parent().find_text(self.search_edit.text())

    def replace_current(self):
        """Remplacer le texte actuel"""
        if hasattr(self.parent(), "replace_text"):
            self.parent().replace_text(
                self.search_edit.text(), self.replace_edit.text()
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

        # Zone de texte - prend tout l'espace restant
        self.text_edit = QTextEdit()
        self.text_edit.setAcceptRichText(False)  # Texte brut seulement

        # Configuration de la police
        font = QFont("Consolas, Monaco, 'Courier New', monospace")
        font.setPointSize(11)
        self.text_edit.setFont(font)

        # Style amélioré
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                color: #2c3e50;
                selection-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }
            
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """
        )

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

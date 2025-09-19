"""
Composant éditeur de texte BlueNotebook avec coloration syntaxique PyQt5
"""

import re
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
from PyQt5.QtWidgets import QDialogButtonBox, QFormLayout, QInputDialog

from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import (
    QFont,
    QTextCharFormat,
    QColor,
    QSyntaxHighlighter,
    QTextDocument,
    QKeySequence,
    QTextCursor,
)


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
        for match in re.finditer(
            title_pattern, text, re.MULTILINE
        ):  # pyright: ignore[reportArgumentType, reportCallIssue]
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


class LinkDialog(QDialog):
    """Boîte de dialogue pour insérer un lien Markdown."""

    def __init__(self, parent=None, selected_text=""):
        super().__init__(parent)
        self.setWindowTitle("Insérer un lien Markdown")

        self.layout = QFormLayout(self)

        self.text_edit = QLineEdit(self)
        self.text_edit.setText(selected_text)
        self.layout.addRow("Texte du lien:", self.text_edit)

        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText("https://example.com")
        self.layout.addRow("URL:", self.url_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

    def get_data(self):
        """Retourne le texte et l'URL saisis."""
        return self.text_edit.text(), self.url_edit.text()

    @staticmethod
    def get_link(parent=None, selected_text=""):
        """Méthode statique pour afficher le dialogue et obtenir les données."""
        dialog = LinkDialog(parent, selected_text)
        # Pré-remplir l'URL si le texte sélectionné est une URL
        if selected_text.startswith("http://") or selected_text.startswith("https://"):
            dialog.url_edit.setText(selected_text)
            dialog.text_edit.setText(
                ""
            )  # Vider le texte pour que l'utilisateur le saisisse
            dialog.text_edit.setFocus()
        else:
            dialog.url_edit.setFocus()

        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_data()
        return None, None


class MarkdownEditor(QWidget):
    """Éditeur de texte avec coloration syntaxique Markdown"""

    textChanged = pyqtSignal()

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
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

    def format_text(self, format_type):
        """Applique le formatage Markdown au texte sélectionné."""
        cursor = self.text_edit.textCursor()

        # Gérer l'insertion de la citation du jour, qui ne nécessite pas de sélection
        if format_type == "quote_of_the_day":
            if (
                self.main_window
                and hasattr(self.main_window, "daily_quote")
                and self.main_window.daily_quote
            ):
                quote_text = f"> {self.main_window.daily_quote}\n> \n> **{self.main_window.daily_author}**"
                cursor.insertText(quote_text)
            return

        if not cursor.hasSelection():
            # Gérer les insertions sans sélection comme la ligne horizontale et le tableau
            if format_type == "hr":
                cursor.insertText("\n---\n")
            elif format_type == "table":
                table_template = "| En-tête 1 | En-tête 2 |\n|---|---|\n| Cellule 1 | Cellule 2 |\n| Cellule 3 | Cellule 4 |"
                cursor.insertText(table_template)
            return

        selected_text = cursor.selectedText()

        # Formats qui s'appliquent sur la ligne entière
        if format_type in ["h1", "h2", "h3", "h4", "h5"]:
            prefix = {
                "h1": "# ",
                "h2": "## ",
                "h3": "### ",
                "h4": "#### ",
                "h5": "##### ",
            }[format_type]

            # Étendre la sélection à la ligne entière
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            cursor.setPosition(start_pos)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            line_text = cursor.selectedText()

            # Supprimer les anciens préfixes de titre
            line_text = re.sub(r"^\s*#+\s*", "", line_text)

            new_text = prefix + line_text
            cursor.insertText(new_text)
            return

        if format_type in ["quote", "ul", "ol", "task_list"]:
            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            cursor.setPosition(start_pos)
            cursor.movePosition(QTextCursor.StartOfLine)
            start_pos = cursor.position()
            cursor.setPosition(end_pos)
            cursor.movePosition(QTextCursor.EndOfLine)
            end_pos = cursor.position()
            cursor.setPosition(start_pos)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)

            lines = cursor.selectedText().splitlines()

            new_text = self._apply_line_prefix(lines, format_type)
            cursor.insertText(new_text)
            return

        # Formats qui entourent le texte
        wrappers = {
            "bold": "**",
            "italic": "*",
            "strikethrough": "~~",
            "inline_code": "`",
            "highlight": "==",
        }

        if format_type in wrappers:
            wrapper = wrappers[format_type]
            # Si le texte est déjà entouré, on enlève les wrappers
            if selected_text.startswith(wrapper) and selected_text.endswith(wrapper):
                new_text = selected_text[len(wrapper) : -len(wrapper)]
            else:
                new_text = f"{wrapper}{selected_text}{wrapper}"
            cursor.insertText(new_text)

        elif format_type == "table":
            table_template = "| En-tête 1 | En-tête 2 |\n|---|---|\n| Cellule 1 | Cellule 2 |\n| Cellule 3 | Cellule 4 |"
            cursor.insertText(table_template)

        elif format_type == "hr":
            # Insère une ligne horizontale après la sélection
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n\n---\n")

        elif format_type == "code_block":
            # Gérer les blocs de code sur plusieurs lignes
            if "\n" in selected_text:
                new_text = f"```\n{selected_text}\n```"
            else:
                new_text = f"```\n{selected_text}\n```"
            cursor.insertText(new_text)

        elif format_type == "url":
            new_text = f"<{selected_text}>"
            cursor.insertText(new_text)

        elif format_type == "image":
            # Pour l'image, on suppose que le texte sélectionné est une URL
            # Une boîte de dialogue serait mieux, mais pour l'instant on utilise une valeur par défaut
            new_text = f'<img src="{selected_text}" width="400">'
            cursor.insertText(new_text)

        elif format_type == "markdown_link":
            text, url = LinkDialog.get_link(self, selected_text)
            if text and url:
                new_text = f"[{text}]({url})"
                cursor.insertText(new_text)

    def clear_formatting(self):
        """Supprime le formatage Markdown de la sélection."""
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        selected_text = cursor.selectedText()

        # Expression régulière pour trouver les caractères de formatage Markdown
        # #, *, _, ~, `, [, ], (, ), !, <, >
        markdown_chars = r"([#*_~`\[\]\(\)!<>])"

        # Supprimer les préfixes de ligne (titre, citation, liste)
        cleaned_text = re.sub(
            r"^\s*([#>\-]+\s*|\d+\.\s*)", "", selected_text, flags=re.MULTILINE
        )

        # Supprimer les autres caractères de formatage
        cleaned_text = re.sub(markdown_chars, "", cleaned_text)

        # Cas spécifique des blocs de code
        cleaned_text = re.sub(r"```.*?\n", "", cleaned_text)
        cleaned_text = cleaned_text.replace("```", "")

        cursor.insertText(cleaned_text)

    def _apply_line_prefix(self, lines, format_type):
        """Applique un préfixe à chaque ligne pour les listes et citations."""
        new_lines = []
        if format_type == "quote":
            for line in lines:
                new_lines.append(f"> {line}")
        elif format_type == "task_list":
            for line in lines:
                # Enlever les préfixes de liste existants avant d'ajouter le nouveau
                cleaned_line = re.sub(r"^\s*-\s*\[[ x]\]\s*|\s*-\s*", "", line).strip()
                new_lines.append(f"- [ ] {cleaned_line}")
        elif format_type == "ul":
            for line in lines:
                new_lines.append(f"- {line}")
        elif format_type == "ol":
            for i, line in enumerate(lines):
                new_lines.append(f"{i + 1}. {line}")

        return "\n".join(new_lines)

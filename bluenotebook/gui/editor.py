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

Composant éditeur de texte BlueNotebook avec coloration syntaxique PyQt5
"""

from pathlib import Path
import os
import re
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFileDialog,
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


# V1.1.7 Fix Issue #2 Markdown editor - coloration syntaxique nefonctionne pas
class MarkdownHighlighter(QSyntaxHighlighter):
    """Coloration syntaxique pour Markdown (titres, gras, italique)"""

    # [Previous MarkdownHighlighter code remains unchanged]
    def __init__(self, document):
        super().__init__(document)
        self.heading_color = QColor("#208bd7")
        self.setup_formats()

    def update_heading_color(self, color):
        self.heading_color = color
        self.setup_formats()

    def setup_formats(self):
        """Configuration des formats de coloration"""
        # Format pour les titres
        base_font_size = 12  # Valeur par défaut
        if self.parent() and isinstance(self.parent(), QTextDocument):
            editor_widget = self.parent().parent()
            if editor_widget and isinstance(editor_widget, QTextEdit):
                base_font_size = editor_widget.font().pointSize()

        self.title_formats = []
        for i in range(1, 7):
            format = QTextCharFormat()
            format.setForeground(self.heading_color)
            format.setFontWeight(QFont.Bold)
            # Formule avec un écart de 2 points entre chaque niveau
            format.setFontPointSize(base_font_size + 2 * (6 - i))
            self.title_formats.append(format)

        # Format pour le gras
        self.bold_format = QTextCharFormat()
        self.bold_format.setFontWeight(QFont.Bold)
        self.bold_format.setForeground(QColor("#448C27"))

        # Format pour l'italique
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(QColor("#448C27"))

        # Format pour le code inline
        self.inline_code_format = QTextCharFormat()
        self.inline_code_format.setFontWeight(QFont.Bold)
        self.inline_code_format.setForeground(QColor("#d6336c"))  # Rose/Rouge
        self.inline_code_format.setBackground(QColor("#f2f07f"))
        self.inline_code_format.setFontFamily("Consolas, Monaco, monospace")

        # Format pour les blocs de code
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setBackground(QColor("#f0f0f0"))  # Gris clair
        self.code_block_format.setFontFamily("Consolas, Monaco, monospace")

        # Format pour les citations (blockquote)
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(QColor("#2B303B"))  # Gris
        self.quote_format.setFontItalic(True)

        # Format pour les listes
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(QColor("#AA3731"))  # Violet
        self.list_format.setFontWeight(QFont.Bold)

        # Format pour les liens Markdown
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(QColor("#0366d6"))  # Bleu
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)

        # Format pour les tags (#tag)
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(QColor("#d73a49"))  # Rouge
        self.tag_format.setFontWeight(QFont.Bold)

        # Format pour le texte barré (strikethrough)
        self.strikethrough_format = QTextCharFormat()
        self.strikethrough_format.setForeground(QColor("#448C27"))  # Gris moyen
        self.strikethrough_format.setFontStrikeOut(True)

        # Format pour le surlignage (highlight)
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(
            QColor("#FFC0CB")
        )  # Rose clair (Light Pink)

    def highlightBlock(self, text):
        """Coloration d'un bloc de texte"""
        # Gestion des blocs de code (```...```)
        self.setCurrentBlockState(0)
        if self.previousBlockState() == 1 or text.strip().startswith("```"):
            self.setFormat(0, len(text), self.code_block_format)
            if not text.strip().endswith("```"):
                self.setCurrentBlockState(1)

        title_pattern = r"^(#{1,6})\s*(.*)$"
        for match in re.finditer(title_pattern, text):
            level = len(match.group(1)) - 1
            if level < len(self.title_formats):
                # Colorer tout le titre (hashtags + texte)
                self.setFormat(
                    match.start(),
                    match.end() - match.start(),
                    self.title_formats[level],
                )

        # Gras (**text** ou __text__) - version simplifiée
        bold_star_pattern = r"\*\*(?!\s)(.*?)(?<!\s)\*\*"
        for match in re.finditer(bold_star_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)

        bold_underscore_pattern = r"__(?!\s)(.*?)(?<!\s)__"
        for match in re.finditer(bold_underscore_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)

        # Italique (*text* ou _text_) - version simplifiée
        italic_star_pattern = r"(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)"
        for match in re.finditer(italic_star_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.italic_format
            )

        italic_underscore_pattern = r"(?<!_)_(?!\s)(.*?)(?<!\s)_(?!_)"
        for match in re.finditer(italic_underscore_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.italic_format
            )

        # Code inline (`code`)
        inline_code_pattern = r"`([^`]+)`"
        for match in re.finditer(inline_code_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.inline_code_format
            )

        # Barré (~~texte~~)
        strikethrough_pattern = r"~~([^~]+)~~"
        for match in re.finditer(strikethrough_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.strikethrough_format
            )

        # Surlignage (==texte==)
        highlight_pattern = r"==([^=]+)=="
        for match in re.finditer(highlight_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.highlight_format
            )
        # Citations (> texte)
        quote_pattern = r"^>\s.*"
        for match in re.finditer(quote_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.quote_format
            )

        # Listes à puces et numérotées (-, *, +, 1.)
        list_pattern = r"^\s*([-*+]|\d+\.)\s"
        for match in re.finditer(list_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.list_format)

        # Liens Markdown ([texte](url))
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        for match in re.finditer(link_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)

        # Auto-liens (<url> ou <email>)
        autolink_pattern = r"<((?:https?://|mailto:)[^>]+|[^>@]+@[^>]+)>"
        for match in re.finditer(autolink_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)

        # Tags (@@tag, au moins 2 caractères après les @@)
        tag_pattern = r"@@(\w{2,})\b"
        for match in re.finditer(tag_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.tag_format)

        # Images HTML (<img ...>)
        image_pattern = r"<img[^>]+>"
        for match in re.finditer(image_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)


class FindDialog(QDialog):
    """Dialogue de recherche"""

    # [Previous FindDialog code remains unchanged]
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

    # [Previous LinkDialog code remains unchanged]
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
        if selected_text.startswith("http://") or selected_text.startswith("https://"):
            dialog.url_edit.setText(selected_text)
            dialog.text_edit.setText("")
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
        label = QLabel("📝 Éditeur Markdown")
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
        font = QFont("'Droid Sans Mono', 'monospace', monospace")
        font.setPointSize(12)
        self.text_edit.setFont(font)

        # Style amélioré couleur rouge
        # V1.4.4 Editeur Surlignage en Jaune lors de sélection
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                background-color: #d6ebff;
                selection-background-color: #e9e942; /* V1.4.2 Very light yellow for selection background */
                color: #2c3e50;
                selection-color: #ff0004;
            }
            
            QTextEdit:focus {
                border: 2px solid #3498db;
            }

            /* Style pour la barre de défilement verticale */
            QScrollBar:vertical {
                border: none;
                background: #e0e0e0; /* Fond de la barre de défilement */
                width: 12px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: #b0b0b0; /* Couleur de l'indicateur (gris clair) */
                min-height: 25px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0; /* Un peu plus foncé au survol */
            }
            /* Masquer les boutons fléchés en haut et en bas */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
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

    def insert_text(self, text):
        """Insère du texte à la position actuelle du curseur."""
        cursor = self.text_edit.textCursor()
        cursor.insertText(text)

    def format_text(self, format_type):
        """Applique le formatage Markdown au texte sélectionné."""
        cursor = self.text_edit.textCursor()

        if format_type == "quote_of_the_day":
            if (
                self.main_window
                and hasattr(self.main_window, "daily_quote")
                and self.main_window.daily_quote
            ):
                quote_text = f"> {self.main_window.daily_quote}\n> \n> **{self.main_window.daily_author}**"
                cursor.insertText(quote_text)
            return

        if format_type == "internal_link":
            start_dir = (
                str(self.main_window.journal_directory)
                if self.main_window and self.main_window.journal_directory
                else ""
            )
            filename, _ = QFileDialog.getOpenFileName(
                self, "Sélectionner un fichier à lier", start_dir
            )

            if filename:
                file_basename = os.path.basename(filename)
                file_uri = Path(filename).as_uri()
                new_text = f"[{file_basename}]({file_uri})"
                cursor.insertText(new_text)
            return

        if not cursor.hasSelection():
            if format_type == "hr":
                cursor.insertText("\n---\n")
            elif format_type == "table":
                table_template = "| En-tête 1 | En-tête 2 |\n|---|---|\n| Cellule 1 | Cellule 2 |\n| Cellule 3 | Cellule 4 |"
                cursor.insertText(table_template)
            elif format_type == "time":
                from datetime import datetime

                cursor.insertText(f"**{datetime.now().strftime('%H:%M')}**")
            return

        selected_text = cursor.selectedText()

        if format_type in ["h1", "h2", "h3", "h4", "h5"]:
            prefix = {
                "h1": "# ",
                "h2": "## ",
                "h3": "### ",
                "h4": "#### ",
                "h5": "##### ",
            }[format_type]

            start_pos = cursor.selectionStart()
            end_pos = cursor.selectionEnd()
            cursor.setPosition(start_pos)
            cursor.movePosition(QTextCursor.StartOfLine)
            cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
            cursor.movePosition(QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

            line_text = cursor.selectedText()
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

        wrappers = {
            "bold": "**",
            "italic": "*",
            "strikethrough": "~~",
            "inline_code": "`",
            "highlight": "==",
        }

        if format_type in wrappers:
            wrapper = wrappers[format_type]
            if selected_text.startswith(wrapper) and selected_text.endswith(wrapper):
                new_text = selected_text[len(wrapper) : -len(wrapper)]
            else:
                new_text = f"{wrapper}{selected_text}{wrapper}"
            cursor.insertText(new_text)

        elif format_type == "table":
            table_template = "| En-tête 1 | En-tête 2 |\n|---|---|\n| Cellule 1 | Cellule 2 |\n| Cellule 3 | Cellule 4 |"
            cursor.insertText(table_template)

        elif format_type == "hr":
            cursor.movePosition(QTextCursor.EndOfLine)
            cursor.insertText("\n\n---\n")

        elif format_type == "code_block":
            if "\n" in selected_text:
                new_text = f"```\n{selected_text}\n```"
            else:
                new_text = f"```\n{selected_text}\n```"
            cursor.insertText(new_text)

        elif format_type == "url":
            new_text = f"<{selected_text}>"
            cursor.insertText(new_text)

        elif format_type == "image":
            new_text = f'<img src="{selected_text}" width="400">'
            cursor.insertText(new_text)

        elif format_type == "markdown_link":
            text, url = LinkDialog.get_link(self, selected_text)
            if text and url:
                new_text = f"[{text}]({url})"
                cursor.insertText(new_text)

        elif format_type == "tag":
            new_text = f"@@{selected_text}"
            cursor.insertText(new_text)

    def clear_formatting(self):
        """Supprime le formatage Markdown de la sélection."""
        cursor = self.text_edit.textCursor()
        if not cursor.hasSelection():
            return

        selected_text = cursor.selectedText()
        markdown_chars = r"([#*_~`\[\]\(\)!<>])"

        cleaned_text = re.sub(
            r"^\s*([#>\-]+\s*|\d+\.\s*)", "", selected_text, flags=re.MULTILINE
        )
        cleaned_text = re.sub(markdown_chars, "", cleaned_text)
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
                cleaned_line = re.sub(r"^\s*-\s*\[[ x]\]\s*|\s*-\s*", "", line).strip()
                new_lines.append(f"- [ ] {cleaned_line}")
        elif format_type == "ul":
            for line in lines:
                new_lines.append(f"- {line}")
        elif format_type == "ol":
            for i, line in enumerate(lines):
                new_lines.append(f"{i + 1}. {line}")

        return "\n".join(new_lines)

    def wheelEvent(self, event):
        """Gère l'événement de la molette de la souris pour le zoom."""
        if event.modifiers() == Qt.ControlModifier:
            angle = event.angleDelta().y()
            if angle > 0:
                self.text_edit.zoomIn(1)
            elif angle < 0:
                self.text_edit.zoomOut(1)
            event.accept()
        else:
            super().wheelEvent(event)

    def set_font(self, font):
        """Définit la police de l'éditeur de texte."""
        self.text_edit.setFont(font)

    def set_background_color(self, color_hex):
        """Définit la couleur de fond de l'éditeur."""
        current_style = self.text_edit.styleSheet()
        if "background-color:" in current_style:
            new_style = re.sub(
                r"background-color:\s*[^;]+;",
                f"background-color: {color_hex};",
                current_style,
            )
        else:
            if "QTextEdit {" in current_style:
                new_style = current_style.replace(
                    "QTextEdit {",
                    f"QTextEdit {{\n                background-color: {color_hex};",
                )
            else:
                new_style = f"QTextEdit {{ background-color: {color_hex}; }}"
        self.text_edit.setStyleSheet(new_style)

    def set_text_color(self, color_hex):
        """Définit la couleur du texte de l'éditeur."""
        current_style = self.text_edit.styleSheet()
        if (
            "color:" in current_style
            and "background-color:"
            not in current_style.split("color:")[1].split(";")[0]
        ):
            new_style = re.sub(
                r"(?<!background-)(?<!selection-)color:\s*[^;]+;",
                f"color: {color_hex};",
                current_style,
            )
        else:
            if "QTextEdit {" in current_style:
                new_style = current_style.replace(
                    "QTextEdit {", f"QTextEdit {{\n                color: {color_hex};"
                )
            else:
                new_style = f"QTextEdit {{ color: {color_hex}; }}"
        self.text_edit.setStyleSheet(new_style)

    def set_heading_color(self, color_hex):
        """Définit la couleur des titres dans le surligneur syntaxique."""
        self.highlighter.update_heading_color(QColor(color_hex))
        # Forcer une nouvelle coloration de tout le document
        self.highlighter.rehighlight()

    def set_selection_text_color(self, color_hex):
        """Définit la couleur du texte sélectionné."""
        current_style = self.text_edit.styleSheet()
        if "selection-color:" in current_style:
            new_style = re.sub(
                r"selection-color:\s*[^;]+;",
                f"selection-color: {color_hex};",
                current_style,
            )
        else:
            if "QTextEdit {" in current_style:
                new_style = current_style.replace(
                    "QTextEdit {",
                    f"QTextEdit {{\n                selection-color: {color_hex};",
                )
            else:
                new_style = f"QTextEdit {{ selection-color: {color_hex}; }}"
        self.text_edit.setStyleSheet(new_style)

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
import shutil
from datetime import datetime
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
    QMenu,
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

# V1.9.3 Line numbers
"""
Widget de numéros de ligne pour QTextEdit
À intégrer dans votre editor.py
"""

from PyQt5.QtWidgets import QWidget, QTextEdit
from PyQt5.QtCore import Qt, QRect, QSize, QPointF
from PyQt5.QtGui import QColor, QPainter, QTextFormat


# V1.9.3 Line numbers


class LineNumberArea(QWidget):
    """Widget affichant les numéros de ligne"""

    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return QSize(self.code_editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class QTextEditWithLineNumbers(QTextEdit):
    """QTextEdit avec numéros de ligne"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Créer la zone des numéros de ligne
        self.line_number_area = LineNumberArea(self)

        # Connecter les signaux disponibles pour QTextEdit
        self.textChanged.connect(self.update_line_number_area_width)
        self.cursorPositionChanged.connect(self.update_line_numbers)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        self.verticalScrollBar().valueChanged.connect(self.update_line_numbers)

        # Initialiser
        self.update_line_number_area_width()
        self.highlight_current_line()

        # Couleurs par défaut
        self.line_number_bg_color = QColor("#f0f0f0")
        self.line_number_fg_color = QColor("#808080")
        self.current_line_number_color = QColor("#000000")

    def line_number_area_width(self):
        """Calcule la largeur nécessaire pour afficher les numéros de ligne"""
        # Compter le nombre de lignes dans le document
        digits = 1
        max_num = max(1, self.document().blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1

        # Largeur : 8px marge + largeur des chiffres + 8px marge
        space = 8 + self.fontMetrics().horizontalAdvance("9") * digits + 8
        return space

    def update_line_number_area_width(self):
        """Met à jour la largeur de la zone des numéros de ligne"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_numbers(self):
        """Force la mise à jour de l'affichage des numéros"""
        self.line_number_area.update()

    def resizeEvent(self, event):
        """Redimensionne la zone des numéros de ligne"""
        super().resizeEvent(event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height())
        )

    def scrollContentsBy(self, dx, dy):
        """Gère le défilement pour mettre à jour les numéros"""
        super().scrollContentsBy(dx, dy)
        self.line_number_area.update()

    def highlight_current_line(self):
        """Surligne la ligne courante"""
        extra_selections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()

            line_color = QColor("#e8f4ff")  # Bleu très clair
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        """Dessine les numéros de ligne"""
        painter = QPainter(self.line_number_area)

        # Fond de la zone des numéros
        painter.fillRect(event.rect(), self.line_number_bg_color)

        # Obtenir le document
        doc = self.document()
        layout = doc.documentLayout()

        # Hauteur de la police
        font_height = self.fontMetrics().height()

        # Position du curseur actuel
        current_line = self.textCursor().blockNumber()

        # Obtenir le rectangle du viewport
        viewport_rect = self.viewport().rect()

        # Trouver le premier bloc visible en haut du viewport
        top_left = viewport_rect.topLeft()
        cursor_at_top = self.cursorForPosition(top_left)
        first_visible_block = cursor_at_top.block()

        # Parcourir les blocs à partir du premier visible
        block = first_visible_block
        block_number = block.blockNumber()

        while block.isValid():
            # Obtenir la géométrie du bloc dans les coordonnées du document
            block_rect = layout.blockBoundingRect(block)

            # Convertir en coordonnées du viewport
            # Utiliser cursorRect pour obtenir la position visible
            cursor = self.textCursor()
            cursor.setPosition(block.position())
            cursor_rect = self.cursorRect(cursor)

            top = cursor_rect.top()
            bottom = top + block_rect.height()

            # Si on est en dessous de la zone visible, arrêter
            if top > viewport_rect.bottom():
                break

            # Dessiner seulement si visible
            if bottom >= 0 and top <= viewport_rect.bottom():
                number = str(block_number + 1)

                # Couleur différente pour la ligne courante
                if block_number == current_line:
                    painter.setPen(self.current_line_number_color)
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                else:
                    painter.setPen(self.line_number_fg_color)
                    font = painter.font()
                    font.setBold(False)
                    painter.setFont(font)

                # Dessiner le numéro aligné à droite
                painter.drawText(
                    0,
                    int(top),
                    self.line_number_area.width() - 5,
                    font_height,
                    Qt.AlignRight | Qt.AlignTop,
                    number,
                )

            block = block.next()
            block_number += 1

    def contentOffset(self):
        """Obtient le décalage du contenu dû au défilement"""
        # Cette méthode n'est plus utilisée mais gardée pour compatibilité
        return QPointF(0, 0)

    def set_line_number_colors(self, bg_color, fg_color, current_color):
        """Définit les couleurs des numéros de ligne"""
        self.line_number_bg_color = QColor(bg_color)
        self.line_number_fg_color = QColor(fg_color)
        self.current_line_number_color = QColor(current_color)
        self.line_number_area.update()

    def set_line_numbers_visible(self, visible):
        """Affiche ou masque la zone des numéros de ligne."""
        if visible:
            self.line_number_area.show()
            self.update_line_number_area_width()
        else:
            self.line_number_area.hide()
            self.setViewportMargins(0, 0, 0, 0)


# V1.1.7 Fix Issue #2 Markdown editor - coloration syntaxique nefonctionne pas
class MarkdownHighlighter(QSyntaxHighlighter):
    """Coloration syntaxique pour Markdown (titres, gras, italique)"""

    # [Previous MarkdownHighlighter code remains unchanged]
    def __init__(self, document):
        super().__init__(document)
        self.heading_color = QColor("#208bd7")
        # Par défaut, la couleur des listes est la même que celle des titres
        self.list_color = QColor("#208bd7")
        # Couleurs par défaut pour le code inline
        self.inline_code_text_color = QColor("#d6336c")
        self.inline_code_background_color = QColor("#f2f07f")
        # Couleurs par défaut pour les styles de texte
        self.bold_color = QColor("#448C27")
        self.italic_color = QColor("#448C27")
        self.strikethrough_color = QColor("#448C27")
        self.highlight_color = QColor("#FFC0CB")
        # Couleurs par défaut pour les tags et horodatage
        self.tag_color = QColor("#d73a49")
        self.timestamp_color = QColor("#005cc5")
        # Couleur par défaut pour le fond des blocs de code
        self.code_block_background_color = QColor("#f0f0f0")
        # V1.7.2 Ajout Paramètre Affichages Couleurs
        # Couleurs par défaut pour les citations et les liens
        self.quote_color = QColor("#2B303B")
        self.link_color = QColor("#0366d6")
        # Couleur par défaut pour les commentaires HTML
        self.html_comment_color = QColor("#a4b5cf")

        # Police par défaut pour le code
        self.code_font_family = "Consolas, Monaco, monospace"

        self.setup_formats()

    def update_heading_color(self, color):
        self.heading_color = color
        self.setup_formats()

    def update_list_color(self, color):
        self.list_color = color
        self.setup_formats()

    def update_inline_code_colors(self, text_color, background_color):
        """Met à jour les couleurs pour le code inline."""
        self.inline_code_text_color = text_color
        self.inline_code_background_color = background_color
        self.setup_formats()

    def update_text_style_colors(self, bold, italic, strikethrough, highlight):
        """Met à jour les couleurs pour les styles de texte."""
        self.bold_color = bold
        self.italic_color = italic
        self.strikethrough_color = strikethrough
        self.highlight_color = highlight
        self.setup_formats()

    def update_misc_colors(self, tag_color, timestamp_color):
        """Met à jour les couleurs pour les tags et l'horodatage."""
        self.tag_color = tag_color
        self.timestamp_color = timestamp_color
        self.setup_formats()

    # V1.7.2 Ajout Paramètre Affichages Couleurs
    def update_quote_link_colors(self, quote_color, link_color):
        """Met à jour les couleurs pour les citations et les liens."""
        self.quote_color = quote_color
        self.link_color = link_color
        self.setup_formats()

    def update_html_comment_color(self, color):
        """Met à jour la couleur pour les commentaires HTML."""
        self.html_comment_color = color
        self.setup_formats()

    def update_code_font(self, font_family):
        """Met à jour la police pour le code."""
        self.code_font_family = font_family
        self.setup_formats()

    def update_code_block_background_color(self, color):
        """Met à jour la couleur de fond pour les blocs de code."""
        self.code_block_background_color = color
        self.setup_formats()

    def update_base_font_size(self):
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
        self.bold_format.setForeground(self.bold_color)

        # Format pour l'italique
        self.italic_format = QTextCharFormat()
        self.italic_format.setFontItalic(True)
        self.italic_format.setForeground(self.italic_color)

        # Format pour le code inline
        self.inline_code_format = QTextCharFormat()
        self.inline_code_format.setFontWeight(QFont.Bold)
        self.inline_code_format.setForeground(self.inline_code_text_color)
        self.inline_code_format.setBackground(self.inline_code_background_color)
        self.inline_code_format.setFontFamily(self.code_font_family)

        # Format pour les blocs de code
        self.code_block_format = QTextCharFormat()
        self.code_block_format.setBackground(self.code_block_background_color)
        self.code_block_format.setFontFamily(self.code_font_family)

        # Format pour les citations (blockquote)
        self.quote_format = QTextCharFormat()
        self.quote_format.setForeground(self.quote_color)
        self.quote_format.setFontItalic(True)

        # Format pour les listes
        self.list_format = QTextCharFormat()
        self.list_format.setForeground(self.list_color)
        # Format pour les liens Markdown
        self.link_format = QTextCharFormat()
        self.link_format.setForeground(self.link_color)
        self.link_format.setUnderlineStyle(QTextCharFormat.SingleUnderline)

        # Format pour les tags (#tag)
        self.tag_format = QTextCharFormat()
        self.tag_format.setForeground(self.tag_color)
        self.tag_format.setFontWeight(QFont.Bold)

        # Format pour l'horodatage (HH:MM)
        self.timestamp_format = QTextCharFormat()
        self.timestamp_format.setForeground(self.timestamp_color)
        self.timestamp_format.setFontWeight(QFont.Bold)

        # Format pour le texte barré (strikethrough)
        self.strikethrough_format = QTextCharFormat()
        self.strikethrough_format.setForeground(self.strikethrough_color)
        self.strikethrough_format.setFontStrikeOut(True)

        # Format pour le surlignage (highlight)
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(self.highlight_color)

        # Format pour les commentaires HTML
        self.html_comment_format = QTextCharFormat()
        self.html_comment_format.setForeground(self.html_comment_color)
        self.html_comment_format.setFontItalic(True)

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

        # V1.7.2 Fix Issue #17 - Ordre d'application pour éviter conflit gras/italique
        # Gras (**text** ou __text__) - version simplifiée
        bold_star_pattern = r"\*\*(?!\s)(.*?)(?<!\s)\*\*"
        for match in re.finditer(bold_star_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)

        # Italique (*text*) - ne doit pas être appliqué sur du gras déjà traité
        italic_star_pattern = r"(?<!\*)\*(?!\s)(.*?)(?<!\s)\*(?!\*)"
        for match in re.finditer(italic_star_pattern, text):
            # Vérifier si le format est déjà appliqué pour éviter les conflits
            if self.format(match.start()) != self.bold_format:
                self.setFormat(
                    match.start(), match.end() - match.start(), self.italic_format
                )

        bold_underscore_pattern = r"__(?!\s)(.*?)(?<!\s)__"
        for match in re.finditer(bold_underscore_pattern, text):
            self.setFormat(match.start(), match.end() - match.start(), self.bold_format)

        # Règle améliorée pour l'italique avec underscore, qui ignore les `_` à l'intérieur des mots.
        # `(?<!\w)` et `(?!\w)` s'assurent que l'underscore n'est pas collé à un caractère alphanumérique.
        italic_underscore_pattern = r"(?<!\w)_([^_]+)_(?!\w)"
        for match in re.finditer(italic_underscore_pattern, text):
            if self.format(match.start()) != self.bold_format:
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
        list_pattern = r"^\s*([-*+]|\d+\.|\-\s\[[ x]\])\s"
        for match in re.finditer(list_pattern, text):
            # Appliquer le format uniquement au marqueur de la liste
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

        # Horodatage (HH:MM)
        timestamp_pattern = r"\b([0-1]?[0-9]|2[0-3]):[0-5][0-9]\b"
        for match in re.finditer(timestamp_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.timestamp_format
            )

        # Images HTML (<img ...>)
        image_pattern = r"<img[^>]+>"
        for match in re.finditer(image_pattern, text, re.IGNORECASE):
            self.setFormat(match.start(), match.end() - match.start(), self.link_format)

        # Commentaires HTML (<!-- ... -->)
        # Doit être appliqué après les autres pour ne pas être surchargé
        # par exemple par la coloration de lien si un lien est dans un commentaire.
        # Mais doit être avant le bloc de code pour ne pas colorer les commentaires dans les blocs.
        html_comment_pattern = r"<!--.*?-->"
        for match in re.finditer(html_comment_pattern, text):
            self.setFormat(
                match.start(), match.end() - match.start(), self.html_comment_format
            )


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


class ImageSourceDialog(QDialog):
    """
    Boîte de dialogue pour obtenir le chemin d'une image,
    soit via une URL, soit via un sélecteur de fichier.
    """

    def __init__(self, parent=None, initial_path=""):
        super().__init__(parent)
        self.setWindowTitle("Source de l'image")
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Champ pour le chemin/URL
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            "http://example.com/image.png ou /chemin/local"
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow("Chemin ou URL:", path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)",
        )
        if path:
            self.path_edit.setText(path)

    def get_path(self):
        return self.path_edit.text().strip()


class MarkdownEditor(QWidget):
    """Éditeur de texte avec coloration syntaxique Markdown"""

    textChanged = pyqtSignal()
    cursorPositionChanged = pyqtSignal()

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
        self.text_edit = QTextEditWithLineNumbers()
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
        self.text_edit.cursorPositionChanged.connect(self.cursorPositionChanged.emit)
        # V1.7.7 - Activer le menu contextuel personnalisé
        self.text_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.text_edit.customContextMenuRequested.connect(self.show_context_menu)
        # V1.1.12 Zoom Editeur avec la Molette
        self.text_edit.wheelEvent = self.wheelEvent

        # L'éditeur prend tout l'espace disponible
        layout.addWidget(self.text_edit, 1)  # stretch factor = 1

        self.setLayout(layout)

    def get_text(self):
        """Récupérer le texte"""
        return self.text_edit.toPlainText()

    def set_text(self, text):
        """Définir le texte"""
        self.text_edit.setPlainText(text)

    def show_context_menu(self, position):
        """Affiche le menu contextuel personnalisé."""
        # Créer le menu standard (Couper, Copier, Coller, etc.)
        menu = self.text_edit.createStandardContextMenu()

        # Ajouter des actions personnalisées uniquement si du texte est sélectionné
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            menu.addSeparator()

            # --- Style de texte ---
            style_menu = QMenu("🎨 Style de texte", self)
            bold_action = style_menu.addAction("🅱️ Gras")
            bold_action.triggered.connect(lambda: self.format_text("bold"))
            italic_action = style_menu.addAction("*️⃣ Italique")
            italic_action.triggered.connect(lambda: self.format_text("italic"))
            strikethrough_action = style_menu.addAction("~ Barré")
            strikethrough_action.triggered.connect(
                lambda: self.format_text("strikethrough")
            )
            highlight_action = style_menu.addAction("🖍️ Surligné")
            highlight_action.triggered.connect(lambda: self.format_text("highlight"))
            menu.addMenu(style_menu)

            # --- Code ---
            code_menu = QMenu("💻 Code", self)
            inline_code_action = code_menu.addAction("` Monospace (inline)")
            inline_code_action.triggered.connect(
                lambda: self.format_text("inline_code")
            )
            code_block_action = code_menu.addAction("``` Bloc de code")
            code_block_action.triggered.connect(lambda: self.format_text("code_block"))
            menu.addMenu(code_menu)

        # Afficher le menu à la position du curseur
        menu.exec_(self.text_edit.viewport().mapToGlobal(position))

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

        # Traiter en priorité les cas qui doivent fonctionner sans sélection
        if format_type == "markdown_image":
            self.insert_markdown_image()
            return

        # V1.7.8 - Correction: L'insertion d'image HTML a sa propre logique de sélection
        if format_type == "image":
            self.insert_html_image()
            return

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
                self.insert_text("\n---\n")
            elif format_type == "table":
                table_template = "| En-tête 1 | En-tête 2 |\n|---|---|\n| Cellule 1 | Cellule 2 |\n| Cellule 3 | Cellule 4 |"
                self.insert_text(table_template)
            elif format_type == "time":
                from datetime import datetime

                self.insert_text(f"**{datetime.now().strftime('%H:%M')}**")
            elif format_type == "html_comment":
                self.insert_text("<!-- texte du commentaire -->")
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

        elif format_type == "markdown_link":
            text, url = LinkDialog.get_link(self, selected_text.strip())
            if text and url:
                new_text = f"[{text}]({url})"
                cursor.insertText(new_text)

        elif format_type == "html_comment":
            new_text = f"<!-- {selected_text} -->"
            cursor.insertText(new_text)

    def insert_youtube_video(self, video_id, video_url, video_title="Vidéo YouTube"):
        """Insère le bloc de texte formaté pour une vidéo YouTube."""
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
        markdown_text = f"\n\n@@Video @@Youtube {video_title} <{video_url}>\n\n[![{video_title}]({thumbnail_url})]({video_url})\n\n⬆️**Cliquez sur l'image pour lancer la vidéo**⬆️\n"
        self.insert_text(markdown_text)

    def insert_html_image(self):
        """
        Insère une balise <img>.
        - Si un nom de fichier est sélectionné, l'utilise.
        - Sinon, ouvre une boîte de dialogue pour choisir un fichier.
        - Demande ensuite la largeur de l'image à l'utilisateur.
        """
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()
        file_path = ""

        # Si le texte sélectionné est un chemin de fichier valide, on l'utilise.
        if selected_text and Path(selected_text).is_file():
            file_path = selected_text
        elif not selected_text:
            # Ouvre une boîte de dialogue pour saisir une URL ou choisir un fichier
            dialog = ImageSourceDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                path = dialog.get_path()
                if path:
                    file_path = path
        else:  # Du texte est sélectionné, mais ce n'est pas un fichier
            file_path = selected_text

        if file_path:
            relative_path = self._copy_image_to_journal(file_path)

            width, ok = QInputDialog.getInt(
                self,
                "Largeur de l'image",
                "Largeur maximale en pixels :",
                400,
                1,
                10000,
                1,
            )
            if ok:
                cursor.insertText(f'<img src="{relative_path}" width="{width}">')

    def insert_markdown_image(self):
        """Insère une image au format Markdown ![](/chemin/vers/image)."""
        cursor = self.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        image_path = ""
        # V1.7.8 - Harmonisation avec l'insertion d'image HTML
        # Si le texte sélectionné est un chemin de fichier valide, on l'utilise.
        if selected_text and Path(selected_text).is_file():
            image_path = selected_text
        elif not selected_text:
            # Sinon, si rien n'est sélectionné, ouvrir la boîte de dialogue polyvalente
            dialog = ImageSourceDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                path = dialog.get_path()
                if path:
                    image_path = path
        else:  # Du texte est sélectionné, mais ce n'est pas un fichier (ex: une URL)
            image_path = selected_text

        if image_path:
            relative_path = self._copy_image_to_journal(image_path)
            # Utiliser des barres obliques pour la compatibilité web/markdown
            image_path_md = relative_path.replace("\\", "/")
            # Insérer le tag Markdown
            self.insert_text(f"![]({image_path_md})")

        self.text_edit.setFocus()

    def _copy_image_to_journal(self, source_path: str) -> str:
        """
        Copie une image locale dans le répertoire 'images' du journal,
        la renomme avec un horodatage et retourne le chemin relatif.
        Si le chemin est une URL, le retourne inchangé.
        """
        if not source_path or source_path.lower().startswith(("http://", "https://")):
            return source_path

        if not self.main_window or not self.main_window.journal_directory:
            return source_path  # Pas de journal défini, on utilise le chemin original

        source_file = Path(source_path)
        if not source_file.is_file():
            return source_path  # Ce n'est pas un fichier valide

        journal_images_dir = self.main_window.journal_directory / "images"
        journal_images_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        new_filename = f"{timestamp}_{source_file.name}"
        destination_file = journal_images_dir / new_filename

        try:
            shutil.copy2(source_file, destination_file)
            # Retourne le chemin relatif pour l'insertion dans le Markdown
            return f"images/{new_filename}"
        except Exception as e:
            print(f"Erreur lors de la copie de l'image : {e}")
            return source_path  # En cas d'erreur, on retourne le chemin original

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
            QTextEdit.wheelEvent(self.text_edit, event)

    def set_font(self, font):
        """Définit la police de l'éditeur de texte."""
        self.text_edit.setFont(font)
        self.highlighter.update_base_font_size()

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

    def set_list_color(self, color_hex):
        """Définit la couleur des listes dans le surligneur syntaxique."""
        self.highlighter.update_list_color(QColor(color_hex))
        # Forcer une nouvelle coloration de tout le document
        self.highlighter.rehighlight()

    def set_inline_code_colors(self, text_color_hex, background_color_hex):
        """Définit les couleurs pour le code inline dans le surligneur."""
        self.highlighter.update_inline_code_colors(
            QColor(text_color_hex), QColor(background_color_hex)
        )
        self.highlighter.rehighlight()

    def set_text_style_colors(
        self, bold_hex, italic_hex, strikethrough_hex, highlight_hex
    ):
        """Définit les couleurs pour les styles de texte dans le surligneur."""
        self.highlighter.update_text_style_colors(
            QColor(bold_hex),
            QColor(italic_hex),
            QColor(strikethrough_hex),
            QColor(highlight_hex),
        )
        self.highlighter.rehighlight()

    def set_misc_colors(self, tag_color_hex, timestamp_color_hex):
        """Définit les couleurs pour les tags et l'horodatage."""
        self.highlighter.update_misc_colors(
            QColor(tag_color_hex), QColor(timestamp_color_hex)
        )
        self.highlighter.rehighlight()

    # V1.7.2 Ajout Paramètre Affichages Couleurs
    def set_quote_link_colors(self, quote_color_hex, link_color_hex):
        """Définit les couleurs pour les citations et les liens."""
        self.highlighter.update_quote_link_colors(
            QColor(quote_color_hex), QColor(link_color_hex)
        )
        self.highlighter.rehighlight()

    def set_html_comment_color(self, color_hex):
        """Définit la couleur des commentaires HTML dans le surligneur."""
        self.highlighter.update_html_comment_color(QColor(color_hex))
        # Forcer une nouvelle coloration de tout le document
        self.highlighter.rehighlight()

    def set_code_font(self, font_family):
        """Définit la police pour les blocs de code et le code inline."""
        self.highlighter.update_code_font(font_family)
        self.highlighter.rehighlight()

    def set_code_block_background_color(self, color_hex):
        """Définit la couleur de fond pour les blocs de code."""
        self.highlighter.update_code_block_background_color(QColor(color_hex))
        self.highlighter.rehighlight()

    def set_line_numbers_visible(self, visible):
        """Transmet la visibilité des numéros de ligne au widget QTextEdit."""
        self.text_edit.set_line_numbers_visible(visible)

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

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

Tests pour le composant éditeur de texte (MarkdownEditor)
"""

import pytest
from PyQt5.QtWidgets import QApplication
from gui.editor import MarkdownEditor

# Créer une instance de QApplication pour les tests
app = QApplication([])


@pytest.fixture
def editor():
    """Fixture pour créer une instance de MarkdownEditor."""
    return MarkdownEditor()


def test_format_bold(editor):
    """Teste le formatage en gras."""
    editor.set_text(self.tr("un texte simple"))
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)

    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)  # sélectionne "texte"
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("bold"))
    assert editor.get_text() == self.tr("un **texte** simple")

    # Teste le dé-formatage
    editor.format_text(self.tr("bold"))
    assert editor.get_text() == self.tr("un texte simple")


def test_format_italic(editor):
    """Teste le formatage en italique."""
    editor.set_text(self.tr("un texte simple"))
    cursor = editor.text_edit.textCursor()
    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("italic"))
    assert editor.get_text() == self.tr("un *texte* simple")

    # Teste le dé-formatage
    editor.format_text(self.tr("italic"))
    assert editor.get_text() == self.tr("un texte simple")


def test_format_inline_code(editor):
    """Teste le formatage en code inline (monospace)."""
    editor.set_text(self.tr("un texte simple"))
    cursor = editor.text_edit.textCursor()
    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("inline_code"))
    assert editor.get_text() == self.tr("un `texte` simple")

    # Teste le dé-formatage
    editor.format_text(self.tr("inline_code"))
    assert editor.get_text() == self.tr("un texte simple")


def test_format_header(editor):
    """Teste le formatage des titres."""
    editor.set_text(self.tr("Ceci est un titre"))
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("h1"))
    assert editor.get_text() == self.tr("# Ceci est un titre")

    editor.format_text(self.tr("h2"))
    assert editor.get_text() == self.tr("## Ceci est un titre")

    # Teste le remplacement d'un titre existant
    editor.set_text(self.tr("### Ancien titre"))
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)
    editor.format_text(self.tr("h1"))
    assert editor.get_text() == self.tr("# Ancien titre")


def test_format_highlight(editor):
    """Teste le formatage de surlignage."""
    editor.set_text(self.tr("texte à surligner"))
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("highlight"))
    assert editor.get_text() == self.tr("==texte à surligner==")

    # Teste le dé-formatage
    editor.format_text(self.tr("highlight"))
    assert editor.get_text() == self.tr("texte à surligner")


def test_format_task_list(editor):
    """Teste le formatage de liste de tâches."""
    editor.set_text(self.tr("Première tâche\nDeuxième tâche"))
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text(self.tr("task_list"))
    assert editor.get_text() == self.tr("- [ ] Première tâche\n- [ ] Deuxième tâche")


def test_insert_horizontal_rule(editor):
    """Teste l'insertion d'une ligne horizontale."""
    editor.set_text(self.tr("texte"))
    cursor = editor.text_edit.textCursor()
    cursor.movePosition(cursor.End)
    editor.text_edit.setTextCursor(cursor)

    # Simule un appel sans sélection
    editor.format_text(self.tr("hr"))
    assert editor.get_text() == self.tr("texte\n---\n")


def test_insert_table(editor):
    """Teste l'insertion d'un tableau."""
    editor.set_text(self.tr(""))
    cursor = editor.text_edit.textCursor()
    editor.text_edit.setTextCursor(cursor)

    # Simule un appel sans sélection
    editor.format_text(self.tr("table"))
    expected_table = (
        self.tr("| En-tête 1 | En-tête 2 |\n")
        self.tr("|---|---|\n")
        self.tr("| Cellule 1 | Cellule 2 |\n")
        self.tr("| Cellule 3 | Cellule 4 |")
    )
    assert editor.get_text() == expected_table


def test_clear_formatting(editor):
    """Teste la suppression du formatage."""
    editor.set_text(self.tr("**# `Un texte` riche**"))
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.clear_formatting()
    assert self.tr("Un texte richeurl") in editor.get_text()

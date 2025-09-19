"""
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
    editor.set_text("un texte simple")
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)

    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)  # sélectionne "texte"
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("bold")
    assert editor.get_text() == "un **texte** simple"

    # Teste le dé-formatage
    editor.format_text("bold")
    assert editor.get_text() == "un texte simple"


def test_format_italic(editor):
    """Teste le formatage en italique."""
    editor.set_text("un texte simple")
    cursor = editor.text_edit.textCursor()
    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("italic")
    assert editor.get_text() == "un *texte* simple"

    # Teste le dé-formatage
    editor.format_text("italic")
    assert editor.get_text() == "un texte simple"


def test_format_inline_code(editor):
    """Teste le formatage en code inline (monospace)."""
    editor.set_text("un texte simple")
    cursor = editor.text_edit.textCursor()
    cursor.setPosition(3, cursor.MoveAnchor)
    cursor.setPosition(8, cursor.KeepAnchor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("inline_code")
    assert editor.get_text() == "un `texte` simple"

    # Teste le dé-formatage
    editor.format_text("inline_code")
    assert editor.get_text() == "un texte simple"


def test_format_header(editor):
    """Teste le formatage des titres."""
    editor.set_text("Ceci est un titre")
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("h1")
    assert editor.get_text() == "# Ceci est un titre"

    editor.format_text("h2")
    assert editor.get_text() == "## Ceci est un titre"

    # Teste le remplacement d'un titre existant
    editor.set_text("### Ancien titre")
    cursor.select(cursor.LineUnderCursor)
    editor.text_edit.setTextCursor(cursor)
    editor.format_text("h1")
    assert editor.get_text() == "# Ancien titre"


def test_format_highlight(editor):
    """Teste le formatage de surlignage."""
    editor.set_text("texte à surligner")
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("highlight")
    assert editor.get_text() == "==texte à surligner=="

    # Teste le dé-formatage
    editor.format_text("highlight")
    assert editor.get_text() == "texte à surligner"


def test_format_task_list(editor):
    """Teste le formatage de liste de tâches."""
    editor.set_text("Première tâche\nDeuxième tâche")
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.format_text("task_list")
    assert editor.get_text() == "- [ ] Première tâche\n- [ ] Deuxième tâche"


def test_insert_horizontal_rule(editor):
    """Teste l'insertion d'une ligne horizontale."""
    editor.set_text("texte")
    cursor = editor.text_edit.textCursor()
    cursor.movePosition(cursor.End)
    editor.text_edit.setTextCursor(cursor)

    # Simule un appel sans sélection
    editor.format_text("hr")
    assert editor.get_text() == "texte\n---\n"


def test_insert_table(editor):
    """Teste l'insertion d'un tableau."""
    editor.set_text("")
    cursor = editor.text_edit.textCursor()
    editor.text_edit.setTextCursor(cursor)

    # Simule un appel sans sélection
    editor.format_text("table")
    expected_table = (
        "| En-tête 1 | En-tête 2 |\n"
        "|---|---|\n"
        "| Cellule 1 | Cellule 2 |\n"
        "| Cellule 3 | Cellule 4 |"
    )
    assert editor.get_text() == expected_table


def test_clear_formatting(editor):
    """Teste la suppression du formatage."""
    editor.set_text("**# `Un texte` riche**")
    cursor = editor.text_edit.textCursor()
    cursor.select(cursor.Document)
    editor.text_edit.setTextCursor(cursor)

    editor.clear_formatting()
    assert "Un texte richeurl" in editor.get_text()

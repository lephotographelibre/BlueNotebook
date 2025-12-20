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

from PyQt5.QtWidgets import QInputDialog


def handle_insert_bookmark(main_window):
    """Gère l'insertion d'un bookmark à partir d'une URL."""
    cursor = main_window.editor.text_edit.textCursor()
    selected_text = cursor.selectedText().strip()

    url = ""
    if selected_text and selected_text.lower().startswith(("http", "ftp")):
        url = selected_text
    else:
        text, ok = QInputDialog.getText(
            main_window,
            main_window.tr("Insérer un Bookmark"),
            main_window.tr("Entrez l'URL de la page :"),
        )
        if ok and text:
            url = text.strip()

    if not url:
        return

    is_github = "github.com" in url.lower()
    icon = "🐙" if is_github else "🔖"

    if is_github:
        markdown_link = f"{icon} [Github | {url}]({url})"
    else:
        markdown_link = f"{icon} [Bookmark | {url}]({url})"

    cursor = main_window.editor.text_edit.textCursor()
    if cursor.hasSelection():
        cursor.removeSelectedText()
    main_window.editor.insert_text(markdown_link)
    main_window.statusbar.showMessage(
        main_window.tr("Bookmark inséré avec succès."), 3000
    )

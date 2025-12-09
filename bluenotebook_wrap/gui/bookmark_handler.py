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
#
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import requests
from bs4 import BeautifulSoup
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot
from PyQt5.QtWidgets import QInputDialog, QMessageBox


class BookmarkWorker(QRunnable):
    """Worker pour la récupération du titre d'une URL en arrière-plan."""

    class Signals(QObject):
        finished = pyqtSignal(str, str)  # url, title
        error = pyqtSignal(str, str)  # url, error_message

    def __init__(self, url):
        super().__init__()
        self.url = url
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        try:
            headers = {
                self.tr("User-Agent"): self.tr("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            }
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, self.tr("html.parser"))
            title = soup.title.string.strip() if soup.title else self.tr("")
            self.signals.finished.emit(self.url, title)
        except requests.exceptions.RequestException as e:
            self.signals.error.emit(self.url, self.tr("URL invalide ou inaccessible : %1").arg(e))
        except Exception as e:
            self.signals.error.emit(self.url, self.tr("Erreur inattendue : %1").arg(e))


def handle_insert_bookmark(main_window):
    """Gère l'insertion d'un bookmark à partir d'une URL."""
    cursor = main_window.editor.text_edit.textCursor()
    selected_text = cursor.selectedText().strip()

    url = self.tr("")
    if selected_text and selected_text.lower().startswith(("http", "ftp")):
        url = selected_text
    else:
        text, ok = QInputDialog.getText(
            main_window, self.tr("Insérer un Bookmark"), self.tr("Entrez l'URL de la page :")
        )
        if ok and text:
            url = text.strip()

    if not url:
        return

    def on_bookmark_finished(url, title):
        main_window._stop_bookmark_flashing()
        if title:
            markdown_link = self.tr("🔖 [Bookmark | %1 - %2](%3)").arg(title).arg(url).arg(url)
        else:
            markdown_link = self.tr("🔖 [Bookmark | %1](%2)").arg(url).arg(url)
        cursor = main_window.editor.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.removeSelectedText()
        main_window.editor.insert_text(markdown_link)
        main_window.statusbar.showMessage(self.tr("Bookmark inséré avec succès."), 3000)

    def on_bookmark_error(url, error_message):
        main_window._stop_bookmark_flashing()
        QMessageBox.warning(
            main_window,
            self.tr("Erreur de Bookmark"),
            self.tr("Impossible de traiter l'URL '%1':\n%2").arg(url).arg(error_message),
        )

    main_window._start_bookmark_flashing()
    worker = BookmarkWorker(url)
    worker.signals.finished.connect(on_bookmark_finished)
    worker.signals.error.connect(on_bookmark_error)
    main_window.thread_pool.start(worker)

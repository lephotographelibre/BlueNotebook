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

import os
import tempfile
import shutil
import requests
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError:
    MarkItDown = None

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


class PdfToMarkdownWorker(QRunnable):
    """
    Worker to convert a PDF to Markdown using the 'markit' tool in the background.
    """

    class Signals(QObject):
        finished = pyqtSignal(str)  # Emits the resulting markdown content
        error = pyqtSignal(str)

    def __init__(self, pdf_input_path: str):
        super().__init__()
        self.pdf_input_path = pdf_input_path
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        """Executes the conversion process."""
        if MarkItDown is None:
            self.signals.error.emit(
                self.tr("❌ Conversion PDF:La bibliothèque 'markitdown' est introuvable.\n\n")
                self.tr("Veuillez l'installer avec : pip install markitdown[pdf]")
            )
            return

        # We still use a temporary directory for downloaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                input_path = self.pdf_input_path
                # If it's a URL, download it first
                if input_path.startswith(("http://", "https://")):
                    response = requests.get(input_path, stream=True, timeout=30)
                    response.raise_for_status()
                    local_pdf_path = Path(temp_dir) / self.tr("temp.pdf")
                    with open(local_pdf_path, "wb") as f:
                        shutil.copyfileobj(response.raw, f)
                    input_path = str(local_pdf_path)

                # Initialize the converter
                md_converter = MarkItDown(enable_plugins=False)

                # Convert the PDF to Markdown
                result = md_converter.convert(input_path)

                # Emit the resulting markdown content
                self.signals.finished.emit(result.text_content)

            except Exception as e:
                self.signals.error.emit(
                    self.tr("❌ Conversion PDF: Une erreur est survenue lors de la conversion : %1\n\nAssurez-vous d'avoir installé 'markitdown[pdf]'.").arg(e)
                )

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
    import pymupdf4llm
except ImportError:
    pymupdf4llm = None

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QCoreApplication


class PdfConverterContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("PdfConverterContext", text)


class PdfToMarkdownWorker(QRunnable):
    """
    Worker to convert a PDF to Markdown using 'pymupdf4llm' in the background.
    """

    class Signals(QObject):
        finished = pyqtSignal(str)  # Emits the resulting markdown content
        error = pyqtSignal(str)

    def __init__(self, pdf_input_path: str, images_path: str = None):
        super().__init__()
        self.pdf_input_path = pdf_input_path
        self.images_path = images_path
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        """Executes the conversion process."""
        if pymupdf4llm is None:
            error_msg = PdfConverterContext.tr(
                "❌ Conversion PDF: La bibliothèque 'pymupdf4llm' est introuvable.\n\n"
                "Veuillez l'installer avec : pip install pymupdf4llm"
            )
            self.signals.error.emit(error_msg)
            return

        # We still use a temporary directory for downloaded files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                input_path = self.pdf_input_path
                # If it's a URL, download it first
                if input_path.startswith(("http://", "https://")):
                    response = requests.get(input_path, stream=True, timeout=30)
                    response.raise_for_status()
                    local_pdf_path = Path(temp_dir) / "temp.pdf"
                    with open(local_pdf_path, "wb") as f:
                        shutil.copyfileobj(response.raw, f)
                    input_path = str(local_pdf_path)

                # Convert the PDF to Markdown using pymupdf4llm
                kwargs = {}
                if self.images_path:
                    kwargs["write_images"] = True
                    kwargs["image_path"] = self.images_path

                md_text = pymupdf4llm.to_markdown(input_path, **kwargs)

                # Emit the resulting markdown content
                self.signals.finished.emit(md_text)

            except Exception as e:
                error_msg = PdfConverterContext.tr(
                    "❌ Conversion PDF: Une erreur est survenue lors de la conversion : {error}\n\n"
                    "Assurez-vous d'avoir installé 'pymupdf4llm'."
                ).format(error=str(e))
                self.signals.error.emit(error_msg)

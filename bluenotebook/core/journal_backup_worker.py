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
"""

import os
import zipfile
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QCoreApplication


class JournalBackupWorker(QRunnable):
    """
    Worker pour la sauvegarde du journal en arrière-plan.
    """

    class Signals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    def __init__(self, journal_directory: Path, backup_path: Path):
        super().__init__()
        self.journal_directory = journal_directory
        self.backup_path = backup_path
        self.signals = (
            self.Signals()
        )  # Correctement instancie la classe Signals imbriquée

    @pyqtSlot()
    def run(self):
        """Exécute la sauvegarde dans un thread séparé."""
        try:
            with zipfile.ZipFile(
                self.backup_path, "w", zipfile.ZIP_DEFLATED
            ) as zipf:  # Assure que zipfile et os sont importés
                # Parcourir tous les fichiers et dossiers du journal
                for root, dirs, files in os.walk(self.journal_directory):
                    # Exclure les répertoires de cache Python
                    if "__pycache__" in dirs:
                        dirs.remove("__pycache__")

                    for file in files:
                        file_path = Path(root) / file
                        # Calculer le chemin relatif pour l'archive
                        arcname = file_path.relative_to(self.journal_directory)
                        zipf.write(file_path, arcname)

            self.signals.finished.emit(str(self.backup_path))

        except Exception as e:
            # Astuce pour que pylupdate5 détecte la chaîne :
            # On simule un appel à tr() que l'outil adore.
            def tr(text):
                return QCoreApplication.translate("JournalBackupWorker", text)

            error_message = tr("Une erreur est survenue lors de la sauvegarde : %s") % e
            self.signals.error.emit(error_message)

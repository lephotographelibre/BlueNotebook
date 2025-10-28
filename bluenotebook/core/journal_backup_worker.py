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

import shutil
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


class JournalBackupSignals(QObject):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)


class JournalBackupWorker(QRunnable):
    def __init__(self, journal_directory: Path, backup_path: Path):
        super().__init__()
        self.journal_directory = journal_directory
        self.backup_path = backup_path
        self.signals = JournalBackupSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.backup_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.make_archive(
                base_name=str(self.backup_path.with_suffix("")),
                format="zip",
                root_dir=self.journal_directory,
            )
            self.signals.finished.emit(str(self.backup_path))
        except Exception as e:
            self.signals.error.emit(f"La sauvegarde a échoué : {e}")

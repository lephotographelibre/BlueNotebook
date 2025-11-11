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
Gère la logique de sauvegarde du journal.
"""

import os
from datetime import datetime
from pathlib import Path
import zipfile

from PyQt5.QtWidgets import QMessageBox, QFileDialog

from core.journal_backup_worker import JournalBackupWorker
from PyQt5.QtCore import Qt


def backup_journal(main_window):
    """Sauvegarde le répertoire du journal dans une archive ZIP."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            "Sauvegarde impossible",
            "Aucun répertoire de journal n'est actuellement défini.",
        )
        return

    initial_dir = main_window.settings_manager.get("backup.last_directory")
    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = str(main_window.journal_directory.parent)

    backup_filename_default = f"BlueNotebook-Backup-{main_window.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"
    default_path = os.path.join(initial_dir, backup_filename_default)

    backup_path, _ = QFileDialog.getSaveFileName(
        main_window, "Sauvegarder le journal", default_path, "Archives ZIP (*.zip)"
    )

    if backup_path:
        main_window._start_backup_flashing()
        worker = JournalBackupWorker(main_window.journal_directory, Path(backup_path))
        worker.signals.finished.connect(main_window._on_journal_backup_finished)
        worker.signals.error.connect(main_window._on_journal_backup_error)
        main_window.thread_pool.start(worker)

        main_window.settings_manager.set(
            "backup.last_directory", os.path.dirname(backup_path)
        )
        main_window.settings_manager.save_settings()
        main_window.statusbar.showMessage("Lancement de la sauvegarde...", 3000)


def restore_journal(main_window):
    """Restaure un journal depuis une archive ZIP."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            "Restauration impossible",
            "Aucun répertoire de journal de destination n'est défini.",
        )
        return

    zip_path, _ = QFileDialog.getOpenFileName(
        main_window, "Restaurer le journal", "", "Archives ZIP (*.zip)"
    )

    if not zip_path:
        return

    current_journal_backup_path = f"{main_window.journal_directory}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    msg_box = QMessageBox(main_window)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle("Confirmation de la restauration")
    msg_box.setTextFormat(Qt.RichText)
    msg_box.setText(
        f"<p>Vous êtes sur le point de restaurer le journal depuis '{os.path.basename(zip_path)}'.</p>"
        f"<p>Le journal actuel sera d'abord sauvegardé ici :<br><b>{current_journal_backup_path}</b></p>"
        f"<p>L'application va devoir être redémarrée après la restauration. Continuer ?</p>"
    )
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.button(QMessageBox.Yes).setText("Valider")
    msg_box.button(QMessageBox.No).setText("Annuler")
    msg_box.setDefaultButton(QMessageBox.No)
    reply = msg_box.exec_()

    if reply == QMessageBox.No:
        return

    try:
        os.rename(main_window.journal_directory, current_journal_backup_path)
        os.makedirs(main_window.journal_directory)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(main_window.journal_directory)

        QMessageBox.information(
            main_window,
            "Restauration terminée",
            "La restauration est terminée. L'application va maintenant se fermer.\n"
            "Veuillez la relancer pour utiliser le journal restauré.",
        )
        print(f"🔁 Restauration du journal terminée avec succès depuis : {zip_path}")
        main_window.close()

    except Exception as e:
        QMessageBox.critical(
            main_window, "Erreur de restauration", f"La restauration a échoué : {e}"
        )

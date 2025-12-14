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
from PyQt5.QtCore import Qt

from core.journal_backup_worker import JournalBackupWorker

# Pour la traduction j’ai utilisé main_window.tr(...) et pas self.tr(...) Parce que dans ce fichier backup_handler.py, il n’y a pas de self !

def backup_journal(main_window):
    """Sauvegarde le répertoire du journal dans une archive ZIP."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            main_window.tr("Sauvegarde impossible"),
            main_window.tr("Aucun répertoire de journal n'est actuellement défini."),
        )
        return

    initial_dir = main_window.settings_manager.get("backup.last_directory")
    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = str(main_window.journal_directory.parent)

    backup_filename_default = f"BlueNotebook-Backup-{main_window.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"
    default_path = os.path.join(initial_dir, backup_filename_default)

    backup_path, _ = QFileDialog.getSaveFileName(
        main_window,
        main_window.tr("Sauvegarder le journal"),
        default_path,
        main_window.tr("Archives ZIP (*.zip)")
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
        main_window.statusbar.showMessage(main_window.tr("Lancement de la sauvegarde..."), 3000)


def restore_journal(main_window):
    """Restaure un journal depuis une archive ZIP."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            main_window.tr("Restauration impossible"),
            main_window.tr("Aucun répertoire de journal de destination n'est défini."),
        )
        return

    zip_path, _ = QFileDialog.getOpenFileName(
        main_window,
        main_window.tr("Restaurer le journal"),
        "",
        main_window.tr("Archives ZIP (*.zip)")
    )

    if not zip_path:
        return

    current_journal_backup_path = f"{main_window.journal_directory}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    msg_box = QMessageBox(main_window)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(main_window.tr("Confirmation de la restauration"))
    msg_box.setTextFormat(Qt.RichText)

    # → Règle 4 : chaîne multi-lignes avec arguments
    message = main_window.tr(
        "<p>Vous êtes sur le point de restaurer le journal depuis '{filename}'.</p>"
        "<p>Le journal actuel sera d'abord sauvegardé ici :<br><b>{backup_path}</b></p>"
        "<p>L'application va devoir être redémarrée après la restauration. Continuer ?</p>"
    ).format(
        filename=os.path.basename(zip_path),
        backup_path=current_journal_backup_path
    )
    msg_box.setText(message)

    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.button(QMessageBox.Yes).setText(main_window.tr("Valider"))
    msg_box.button(QMessageBox.No).setText(main_window.tr("Annuler"))
    msg_box.setDefaultButton(QMessageBox.No)
    reply = msg_box.exec_()

    if reply == QMessageBox.No:
        return

    try:
        os.rename(main_window.journal_directory, current_journal_backup_path)
        os.makedirs(main_window.journal_directory)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(main_window.journal_directory)

        # → Règle 3 : multi-lignes sans argument
        QMessageBox.information(
            main_window,
            main_window.tr("Restauration terminée"),
            main_window.tr(
                "La restauration est terminée. L'application va maintenant se fermer.\n"
                "Veuillez la relancer pour utiliser le journal restauré."
            ),
        )
        # Message console → non encapsulé (selon consigne et reste en anglais)
        print(f"🔁 Restoration of the journal has been successfully completed since: {zip_path}")
        main_window.close()

    except Exception as e:
        # → Règle 2 : une ligne avec argument
        error_msg = main_window.tr(
            "La restauration a échoué : {error}"
        ).format(error=str(e))

        QMessageBox.critical(
            main_window,
            main_window.tr("Erreur de restauration"),
            error_msg
        )
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

from PyQt5.QtWidgets import (
    QMessageBox, QFileDialog, QDialog, QVBoxLayout, QLabel,
    QRadioButton, QPushButton, QButtonGroup, QDialogButtonBox
)
from PyQt5.QtCore import Qt, QCoreApplication

from core.journal_backup_worker import JournalBackupWorker
from core.journal_restore_worker import JournalRestoreWorker


class BackupHandlerContext:
    """Classe de contexte pour la traduction des chaînes de backup_handler.py"""
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("BackupHandlerContext", text)


class RestoreMergeDialog(QDialog):
    """Dialogue pour choisir la stratégie de fusion lors de la restauration."""

    def __init__(self, zip_path, journal_directory, parent=None):
        super().__init__(parent)
        self.zip_path = zip_path
        self.journal_directory = journal_directory
        self.merge_strategy = "smart_merge"  # Valeur par défaut
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur du dialogue."""
        self.setWindowTitle(self.tr("Stratégie de restauration"))
        self.setMinimumWidth(500)

        layout = QVBoxLayout()

        # Message d'introduction
        intro_message = self.tr(
            "Vous êtes sur le point de restaurer le journal depuis :\n"
            "{archive}\n\n"
            "Destination : {destination}\n\n"
            "Veuillez choisir la stratégie de restauration :"
        )
        intro_message = intro_message.format(
            archive=os.path.basename(self.zip_path),
            destination=str(self.journal_directory)
        )

        intro_label = QLabel(intro_message)
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        # Groupe de boutons radio
        self.button_group = QButtonGroup(self)

        # Option 1: Fusion intelligente (par défaut)
        self.smart_merge_radio = QRadioButton(self.tr("Fusion intelligente (recommandé)"))
        self.smart_merge_radio.setChecked(True)  # Sélectionné par défaut
        self.button_group.addButton(self.smart_merge_radio, 1)

        smart_merge_desc = QLabel(self.tr(
            "Les nouveaux fichiers de l'archive sont ajoutés au journal actuel. "
            "Les fichiers existants sont préservés. "
            "En cas de conflit (même date), le fichier de l'archive est renommé avec .restored"
        ))
        smart_merge_desc.setWordWrap(True)
        smart_merge_desc.setStyleSheet("color: #555; margin-left: 20px; margin-bottom: 10px;")

        layout.addWidget(self.smart_merge_radio)
        layout.addWidget(smart_merge_desc)

        # Option 2: Remplacement complet
        self.full_replace_radio = QRadioButton(self.tr("Remplacement complet"))
        self.button_group.addButton(self.full_replace_radio, 2)

        full_replace_desc = QLabel(self.tr(
            "Le contenu actuel du journal est complètement remplacé par celui de l'archive. "
            "Attention : toutes les données actuelles seront supprimées "
            "(une sauvegarde de sécurité sera créée)."
        ))
        full_replace_desc.setWordWrap(True)
        full_replace_desc.setStyleSheet("color: #d35400; margin-left: 20px; margin-bottom: 10px;")

        layout.addWidget(self.full_replace_radio)
        layout.addWidget(full_replace_desc)

        # Note de sécurité
        security_note = QLabel(self.tr(
            "Note : Dans les deux cas, une sauvegarde de sécurité "
            "de votre journal actuel sera créée avant la restauration."
        ))
        security_note.setWordWrap(True)
        security_note.setStyleSheet("color: #27ae60; font-weight: bold; margin-top: 10px;")
        layout.addWidget(security_note)

        # Boutons OK/Annuler
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText(self.tr("Restaurer"))
        button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        """Appelé quand l'utilisateur clique sur OK."""
        # Déterminer la stratégie choisie
        if self.smart_merge_radio.isChecked():
            self.merge_strategy = "smart_merge"
        else:
            self.merge_strategy = "replace"

        super().accept()

    def get_merge_strategy(self):
        """Retourne la stratégie de fusion choisie."""
        return self.merge_strategy


def backup_journal(main_window):
    """Sauvegarde le répertoire du journal dans une archive ZIP."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            BackupHandlerContext.tr("Sauvegarde impossible"),
            BackupHandlerContext.tr("Aucun répertoire de journal n'est actuellement défini."),
        )
        return

    initial_dir = main_window.settings_manager.get("backup.last_directory")
    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = str(main_window.journal_directory.parent)

    backup_filename_default = f"BlueNotebook-Backup-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"
    default_path = os.path.join(initial_dir, backup_filename_default)

    backup_path, _ = QFileDialog.getSaveFileName(
        main_window,
        BackupHandlerContext.tr("Sauvegarder le journal"),
        default_path,
        BackupHandlerContext.tr("Archives ZIP (*.zip)")
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
        main_window.statusbar.showMessage(BackupHandlerContext.tr("Lancement de la sauvegarde..."), 3000)


def restore_journal(main_window):
    """Restaure un journal depuis une archive ZIP de manière asynchrone."""
    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            BackupHandlerContext.tr("Restauration impossible"),
            BackupHandlerContext.tr("Aucun répertoire de journal de destination n'est défini."),
        )
        return

    # Récupérer le dernier répertoire utilisé pour les backups
    initial_dir = main_window.settings_manager.get("backup.last_directory")
    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = str(main_window.journal_directory.parent)

    # Sélection de l'archive ZIP
    zip_path, _ = QFileDialog.getOpenFileName(
        main_window,
        BackupHandlerContext.tr("Restaurer le journal"),
        initial_dir,
        BackupHandlerContext.tr("Archives ZIP (*.zip)")
    )

    if not zip_path:
        return

    # Afficher le dialogue de choix de stratégie de fusion
    merge_dialog = RestoreMergeDialog(
        zip_path=zip_path,
        journal_directory=main_window.journal_directory,
        parent=main_window
    )

    if merge_dialog.exec_() != QDialog.Accepted:
        return

    # Récupérer la stratégie choisie
    merge_strategy = merge_dialog.get_merge_strategy()

    # Démarrer l'animation de statut
    main_window._start_restore_flashing()

    # Créer et lancer le worker asynchrone
    worker = JournalRestoreWorker(
        zip_path=Path(zip_path),
        journal_directory=main_window.journal_directory,
        merge_strategy=merge_strategy
    )

    # Connecter les signaux aux callbacks
    worker.signals.progress.connect(main_window._on_restore_progress)
    worker.signals.finished.connect(main_window._on_restore_finished)
    worker.signals.error.connect(main_window._on_restore_error)

    # Lancer le worker dans le thread pool
    main_window.thread_pool.start(worker)

    # Sauvegarder le dernier répertoire utilisé
    main_window.settings_manager.set(
        "backup.last_directory", os.path.dirname(zip_path)
    )
    main_window.settings_manager.save_settings()

    # Message de statut
    main_window.statusbar.showMessage(
        BackupHandlerContext.tr("Lancement de la restauration..."),
        3000
    )
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

Écran de premier démarrage de BlueNotebook
"""

import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QSpacerItem,
    QSizePolicy,
    QFrame,
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

from core.settings import SettingsManager


class FirstStartWindow(QDialog):
    """Fenêtre de configuration affichée au premier démarrage."""

    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager

        self.setWindowTitle("BlueNotebook - Premier Démarrage")
        self.setFixedSize(800, 600)
        self.setModal(True)

        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # --- Titre et Logo ---
        header_layout = QHBoxLayout()
        logo_label = QLabel(self)
        base_path = Path(__file__).parent.parent
        logo_path = (
            base_path / "resources" / "images" / "bluenotebook_256-x256_fond_blanc.png"
        )
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            logo_label.setPixmap(
                pixmap.scaled(128, 128, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            header_layout.addWidget(logo_label)

        title_label = QLabel("Bienvenue dans BlueNotebook", self)
        font = QFont()
        # font.setPointSize(24)
        font.setBold(True)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label, 1)
        main_layout.addLayout(header_layout)

        # --- Texte d'introduction ---
        intro_label = QLabel(
            "Pour ce premier démarrage, nous allons définir quelques paramètres essentiels :",
            self,
        )
        main_layout.addWidget(intro_label)

        # --- Séparateur ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separator)

        # --- Langue ---
        lang_layout = QHBoxLayout()
        lang_label = QLabel("Langue de l'application :", self)
        self.lang_combo = QComboBox(self)
        self.lang_combo.addItems(["Français", "English"])
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_combo)
        main_layout.addLayout(lang_layout)

        # --- Répertoire du Journal ---
        journal_layout = QHBoxLayout()
        journal_label = QLabel("Répertoire du Journal :", self)
        self.journal_path_edit = QLineEdit(self)
        self.journal_path_edit.setReadOnly(True)
        self.journal_path_edit.setText(str(Path.home() / "BlueNotebookJournal"))
        journal_button = QPushButton("Choisir...", self)
        journal_layout.addWidget(journal_label)
        journal_layout.addWidget(self.journal_path_edit)
        journal_layout.addWidget(journal_button)
        main_layout.addLayout(journal_layout)
        self.journal_button = journal_button

        # --- Répertoire de Sauvegarde ---
        backup_layout = QHBoxLayout()
        backup_label = QLabel("Répertoire de Sauvegarde :", self)
        self.backup_path_edit = QLineEdit(self)
        self.backup_path_edit.setReadOnly(True)
        self.backup_path_edit.setText(str(Path.home() / "BlueNotebookBackup"))
        backup_button = QPushButton("Choisir...", self)
        backup_layout.addWidget(backup_label)
        backup_layout.addWidget(self.backup_path_edit)
        backup_layout.addWidget(backup_button)
        main_layout.addLayout(backup_layout)
        self.backup_button = backup_button

        # --- Espaceur et Bouton Terminé ---
        main_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self.finish_button = QPushButton("Terminé", self)
        self.finish_button.setMinimumSize(120, 40)
        button_layout.addWidget(self.finish_button)
        main_layout.addLayout(button_layout)

    def _connect_signals(self):
        """Connecte les signaux des widgets à leurs slots."""
        self.journal_button.clicked.connect(self._select_journal_directory)
        self.backup_button.clicked.connect(self._select_backup_directory)
        self.finish_button.clicked.connect(self._finish_setup)

    def _select_journal_directory(self):
        """Ouvre une boîte de dialogue pour choisir le répertoire parent du journal."""
        parent_dir = QFileDialog.getExistingDirectory(
            self, "Choisir l'emplacement du journal", str(Path.home())
        )
        if parent_dir:
            self.journal_path_edit.setText(
                str(Path(parent_dir) / "BlueNotebookJournal")
            )

    def _select_backup_directory(self):
        """Ouvre une boîte de dialogue pour choisir le répertoire parent de la sauvegarde."""
        parent_dir = QFileDialog.getExistingDirectory(
            self, "Choisir l'emplacement des sauvegardes", str(Path.home())
        )
        if parent_dir:
            self.backup_path_edit.setText(str(Path(parent_dir) / "BlueNotebookBackup"))

    def _finish_setup(self):
        """Valide les chemins, crée les répertoires, sauvegarde les paramètres et ferme la fenêtre."""
        journal_path = Path(self.journal_path_edit.text())
        backup_path = Path(self.backup_path_edit.text())

        # --- Création du répertoire du journal ---
        try:
            if journal_path.exists() and any(journal_path.iterdir()):
                reply = QMessageBox.question(
                    self,
                    "Répertoire existant",
                    f"Le répertoire '{journal_path.name}' existe déjà et n'est pas vide.\n"
                    "Voulez-vous quand même l'utiliser comme journal ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

            journal_path.mkdir(parents=True, exist_ok=True)
            # Créer les sous-répertoires
            for sub_dir in ["notes", "images", "attachments", "gpx"]:
                (journal_path / sub_dir).mkdir(exist_ok=True)

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de créer le répertoire du journal :\n{e}"
            )
            return

        # --- Création du répertoire de sauvegarde ---
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de créer le répertoire de sauvegarde :\n{e}",
            )
            return

        # --- Sauvegarde des paramètres ---
        lang_map = {"Français": "fr_FR", "English": "en_US"}
        selected_lang = self.lang_combo.currentText()
        self.settings_manager.set("app.language", lang_map.get(selected_lang, "en_US"))
        self.settings_manager.set("journal.directory", str(journal_path))
        self.settings_manager.set("backup.last_directory", str(backup_path))

        self.settings_manager.save_settings()

        QMessageBox.information(
            self, "Configuration terminée", "BlueNotebook est prêt. Bon journal !"
        )
        self.accept()

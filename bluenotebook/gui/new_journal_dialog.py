"""Dialogue pour créer ou importer un nouveau journal."""

from pathlib import Path

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QRadioButton,
    QButtonGroup,
    QPushButton,
    QDialogButtonBox,
    QFileDialog,
)
from PyQt5.QtCore import Qt


class NewJournalDialog(QDialog):
    """Dialogue pour choisir comment initialiser un nouveau journal."""

    def __init__(self, journal_path, parent=None):
        super().__init__(parent)
        self.journal_path = journal_path
        self.choice = "cancel"
        self.backup_path = None
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur du dialogue."""
        self.setWindowTitle(self.tr("Nouveau Journal"))
        self.setMinimumWidth(550)

        layout = QVBoxLayout()

        # Message d'introduction
        intro_message = self.tr(
            "Le répertoire sélectionné n'est pas un journal BlueNotebook valide.\n\n"
            "Répertoire : {journal_path}\n\n"
            "Comment souhaitez-vous procéder ?"
        )
        intro_message = intro_message.format(journal_path=str(self.journal_path))

        intro_label = QLabel(intro_message)
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)

        # Groupe de boutons radio
        self.button_group = QButtonGroup(self)

        # Option 1: Créer un journal vide (par défaut)
        self.create_empty_radio = QRadioButton(
            self.tr("Créer un nouveau journal vide")
        )
        self.create_empty_radio.setChecked(True)
        self.button_group.addButton(self.create_empty_radio, 1)

        create_empty_desc = QLabel(
            self.tr("(Créera les répertoires : notes/, images/, attachments/, gpx/)")
        )
        create_empty_desc.setWordWrap(True)
        create_empty_desc.setStyleSheet(
            "color: #555; margin-left: 20px; margin-bottom: 10px;"
        )

        layout.addWidget(self.create_empty_radio)
        layout.addWidget(create_empty_desc)

        # Option 2: Importer depuis une sauvegarde
        self.import_backup_radio = QRadioButton(
            self.tr("Importer depuis une sauvegarde")
        )
        self.button_group.addButton(self.import_backup_radio, 2)

        import_backup_desc = QLabel(
            self.tr(
                "Restaure un journal depuis un fichier ZIP de sauvegarde. "
                "Le contenu du fichier ZIP sera extrait dans le répertoire sélectionné."
            )
        )
        import_backup_desc.setWordWrap(True)
        import_backup_desc.setStyleSheet(
            "color: #555; margin-left: 20px; margin-bottom: 5px;"
        )

        layout.addWidget(self.import_backup_radio)
        layout.addWidget(import_backup_desc)

        # Sélecteur de fichier ZIP (pour l'option import)
        zip_layout = QHBoxLayout()
        zip_layout.setContentsMargins(20, 0, 0, 10)

        self.zip_file_label = QLabel(self.tr("Aucun fichier sélectionné"))
        self.zip_file_label.setStyleSheet("color: #888; font-style: italic;")

        self.choose_zip_button = QPushButton(self.tr("Choisir fichier ZIP..."))
        self.choose_zip_button.clicked.connect(self._choose_zip_file)
        self.choose_zip_button.setEnabled(False)

        zip_layout.addWidget(self.zip_file_label, 1)
        zip_layout.addWidget(self.choose_zip_button)

        layout.addLayout(zip_layout)

        # Connecter le signal pour activer/désactiver le bouton de sélection
        self.import_backup_radio.toggled.connect(self._on_import_toggled)

        # Boutons OK/Annuler
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText(self.tr("Valider"))
        button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def _on_import_toggled(self, checked):
        """Active/désactive le bouton de sélection de fichier ZIP."""
        self.choose_zip_button.setEnabled(checked)

    def _choose_zip_file(self):
        """Ouvre un dialogue pour choisir le fichier ZIP de sauvegarde."""
        zip_file, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Sélectionner le fichier de sauvegarde"),
            str(Path.home()),
            self.tr("Fichiers ZIP (*.zip)"),
        )

        if zip_file:
            self.backup_path = Path(zip_file)
            self.zip_file_label.setText(Path(zip_file).name)
            self.zip_file_label.setStyleSheet("color: #000;")

    def accept(self):
        """Appelé quand l'utilisateur clique sur OK."""
        # Déterminer le choix
        if self.create_empty_radio.isChecked():
            self.choice = "create_empty"
            self.backup_path = None
        elif self.import_backup_radio.isChecked():
            if self.backup_path is None:
                # L'utilisateur n'a pas sélectionné de fichier ZIP
                from PyQt5.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    self.tr("Fichier manquant"),
                    self.tr(
                        "Veuillez sélectionner un fichier ZIP de sauvegarde "
                        "ou choisir l'option 'Créer un nouveau journal vide'."
                    ),
                )
                return

            self.choice = "import_backup"

        super().accept()

    def get_selection(self):
        """Retourne le choix de l'utilisateur et le chemin du backup si applicable.

        Returns:
            tuple: (choice: str, backup_path: Path | None)
                choice peut être: "create_empty", "import_backup", "cancel"
        """
        return (self.choice, self.backup_path)

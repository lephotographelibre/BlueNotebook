from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QFormLayout,
    QDateEdit,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtCore import QDate, Qt


class DateRangeDialog(QDialog):
    """
    Boîte de dialogue pour sélectionner une plage de dates.
    """

    def __init__(
        self,
        start_date_default: QDate,
        end_date_default: QDate,
        min_date: QDate,
        max_date: QDate,
        default_title: str,
        default_cover_image: str,
        default_author: str,
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Options d'exportation du journal PDF")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateRange(min_date, max_date)
        self.start_date_edit.setDate(start_date_default)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDateRange(min_date, max_date)
        self.end_date_edit.setDate(end_date_default)

        self.title_edit = QLineEdit(self)
        self.title_edit.setText(default_title)

        self.author_edit = QLineEdit(self)
        self.author_edit.setText(default_author)

        # Champ pour l'image de couverture
        self.cover_image_path = default_cover_image
        self.cover_image_edit = QLineEdit(self)
        self.cover_image_edit.setText(self.cover_image_path)
        self.cover_image_edit.setReadOnly(True)
        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_for_image)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.cover_image_edit)
        image_layout.addWidget(browse_button)

        form_layout.addRow(QLabel("Première note à inclure :"), self.start_date_edit)
        form_layout.addRow(QLabel("Dernière note à inclure :"), self.end_date_edit)
        form_layout.addRow(QLabel("Titre du journal :"), self.title_edit)
        form_layout.addRow(QLabel("Nom de l'auteur (optionnel) :"), self.author_edit)
        form_layout.addRow(QLabel("Image de couverture :"), image_layout)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _browse_for_image(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier image."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner une image de couverture",
            "",
            "Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)",
        )
        if file_path:
            self.cover_image_path = file_path
            self.cover_image_edit.setText(file_path)

    def get_export_options(self) -> dict:
        """Retourne les options d'exportation sélectionnées."""
        return {
            "start_date": self.start_date_edit.date(),
            "end_date": self.end_date_edit.date(),
            "title": self.title_edit.text(),
            "author": self.author_edit.text(),
            "cover_image": self.cover_image_path,
        }

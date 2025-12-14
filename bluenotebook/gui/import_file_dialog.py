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
Boîte de dialogue pour importer un fichier local ou distant.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
    QFormLayout,
    QFileDialog,
)


class ImportFileDialog(QDialog):
    """
    Boîte de dialogue pour obtenir le chemin d'un fichier,
    soit via une URL, soit via un sélecteur de fichier.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Importer un fichier"))
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            self.tr("https://example.com/file.pdf ou /chemin/local/file.pdf")
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton(self.tr("Parcourir..."), self)
        browse_button.clicked.connect(
            lambda: self.path_edit.setText(
                QFileDialog.getOpenFileName(self, self.tr("Sélectionner un fichier"))[0]
            )
        )
        path_layout.addWidget(browse_button)

        form_layout.addRow("Chemin ou URL:", path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_path(self):
        return self.path_edit.text().strip()
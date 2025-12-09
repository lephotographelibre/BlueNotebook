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
Boîte de dialogue pour choisir le type de nouveau fichier à créer.
"""

from pathlib import Path
import locale
from datetime import datetime

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QRadioButton,
    QComboBox,
    QDialogButtonBox,
    QLabel,
)


class NewFileDialog(QDialog):
    """Boîte de dialogue pour choisir le type de nouveau fichier à créer."""

    def __init__(
        self, parent=None, use_template_by_default=False, default_template_name=None
    ):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Créer un nouveau document"))
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.blank_radio = QRadioButton(self.tr("Créer un fichier vierge"))
        self.template_radio = QRadioButton(self.tr("Utiliser un modèle :"))
        self.template_combo = QComboBox()

        self.layout.addWidget(self.blank_radio)
        self.layout.addWidget(self.template_radio)
        self.layout.addWidget(self.template_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Valider"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
        self.layout.addWidget(self.button_box)

        self.blank_radio.toggled.connect(self.template_combo.setDisabled)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self._populate_templates()

        if use_template_by_default and default_template_name:
            index = self.template_combo.findText(default_template_name)
            if index != -1:
                self.template_combo.setCurrentIndex(index)
                self.template_radio.setChecked(True)
            else:
                # Fallback si le template par défaut n'est pas trouvé
                self.blank_radio.setChecked(True)
        else:
            self.blank_radio.setChecked(True)

    def _populate_templates(self):
        """Remplit le combobox avec les modèles trouvés."""
        base_path = Path(__file__).parent.parent
        templates_dir = base_path / self.tr("resources") / self.tr("templates")
        if templates_dir.is_dir():
            template_files = sorted([f.name for f in templates_dir.glob("*.md")])
            self.template_combo.addItems(template_files)

    def get_selection(self):
        """Retourne le choix de l'utilisateur."""
        if self.blank_radio.isChecked():
            return self.tr("blank"), None
        else:
            if self.template_combo.count() > 0:
                return self.tr("template"), self.template_combo.currentText()
            else:
                # Fallback si aucun template n'est trouvé
                return self.tr("blank"), None

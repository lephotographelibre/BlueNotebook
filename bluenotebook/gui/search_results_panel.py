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

Panneau affichant les résultats de recherche.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PyQt5.QtCore import Qt, pyqtSignal


class SearchResultsPanel(QWidget):
    """
    Panneau affichant les résultats d'une recherche de tag ou de mot.
    """

    item_selected = pyqtSignal(str)  # Émet le nom du fichier à ouvrir

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.results_list.itemClicked.connect(self.on_item_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("🔍 Résultats de la Recherche")
        self.label.setStyleSheet(
            """
            QLabel {
                font-weight: bold;
                padding: 8px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                color: #495057;
            }
        """
        )
        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.results_list = QListWidget()
        self.results_list.setStyleSheet("border: none; background-color: transparent;")
        layout.addWidget(self.results_list)

        self.setLayout(layout)

    def update_results(self, results: list):
        """Met à jour la liste des résultats."""
        self.results_list.clear()
        if not results:
            self.results_list.addItem("Aucun résultat trouvé.")
        else:
            for item_text, filename in results:
                item = QListWidgetItem()
                item.setText(item_text)
                item.setData(Qt.UserRole, filename)  # Stocker le nom du fichier
                self.results_list.addItem(item)

    def on_item_clicked(self, item: QListWidgetItem):
        """Gère le clic sur un résultat de recherche."""
        filename = item.data(Qt.UserRole)
        if filename:
            self.item_selected.emit(filename)


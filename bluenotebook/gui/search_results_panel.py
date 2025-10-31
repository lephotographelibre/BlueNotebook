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
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
)
from PyQt5.QtCore import Qt, pyqtSignal


class SearchResultsPanel(QWidget):
    """
    Panneau affichant les résultats d'une recherche de tag ou de mot.
    """

    item_selected = pyqtSignal(str, int)  # Émet le nom du fichier et le numéro de ligne

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.results_tree.itemClicked.connect(self.on_item_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("🔍 Résultats de la Recherche")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(2)
        self.results_tree.setHeaderLabels(["Date", "Texte"])
        self.results_tree.setHeaderLabels(["🗓️", ""])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.setSortingEnabled(True)
        self.results_tree.sortByColumn(0, Qt.DescendingOrder)  # Trier par date
        self.results_tree.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.results_tree)

        self.setLayout(layout)

    def update_results(self, results: list):
        """Met à jour la liste des résultats."""
        self.results_tree.clear()
        if not results:
            item = QTreeWidgetItem(["Aucun résultat trouvé.", ""])
            self.results_tree.addTopLevelItem(item)
        else:
            # results est une liste de tuples (date, text, filename, line_number)
            for date, text, filename, line_number in results:
                item = QTreeWidgetItem([date, text])
                # Stocker le nom du fichier et le numéro de ligne dans les données de l'item
                item.setData(0, Qt.UserRole, filename)
                item.setData(1, Qt.UserRole, line_number)
                self.results_tree.addTopLevelItem(item)

    def on_item_clicked(self, item: QTreeWidgetItem, column: int):
        """Gère le clic sur un résultat de recherche."""
        filename = item.data(0, Qt.UserRole)
        line_number = item.data(1, Qt.UserRole)

        if filename:
            # Émettre le nom du fichier ET le numéro de ligne
            self.item_selected.emit(filename, line_number)

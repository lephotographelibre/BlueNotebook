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

Panneau d'affichage des résultats de recherche de BlueNotebook
"""

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QHeaderView,
)


class SearchResultsPanel(QWidget):
    """Panneau qui affiche les résultats d'une recherche par tag ou mot."""

    item_selected = pyqtSignal(str, int)
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.results_tree.itemDoubleClicked.connect(self.on_item_double_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("🔍 Résultats de la Recherche")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.setToolTip("Cliquez pour rafraîchir l'index des tags")
        self.label.mousePressEvent = self.on_title_clicked

        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(2)
        self.results_tree.setHeaderLabels(["Date", "Texte"])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.setSortingEnabled(True)
        self.results_tree.sortByColumn(0, Qt.DescendingOrder)
        layout.addWidget(self.results_tree)

        self.setLayout(layout)

    def update_results(self, results: list, search_query: str):
        """Met à jour la liste des résultats."""
        self.results_tree.clear()
        if search_query.lower() == "@@todo":
            self.label.setText("✔ Liste des Tâches @@TODO")
        else:
            self.label.setText("🔍 Résultats de la Recherche")

        for date, context, filename, line in results:
            item = QTreeWidgetItem([date, context])
            item.setData(0, Qt.UserRole, (filename, line))
            self.results_tree.addTopLevelItem(item)

    def on_item_double_clicked(self, item, column):
        """Émet un signal lorsqu'un élément est double-cliqué."""
        filename, line = item.data(0, Qt.UserRole)
        self.item_selected.emit(filename, line)

    def on_title_clicked(self, event):
        """Émet un signal lorsque le titre est cliqué."""
        self.refresh_requested.emit()
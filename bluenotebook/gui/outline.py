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

Panneau affichant le plan du document (Outline).
"""

import re
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont, QColor


class OutlinePanel(QWidget):
    """
    Panneau affichant la structure (hiérarchie des titres) du document Markdown.
    """

    # Signal émis lorsqu'un item est cliqué, transportant la position du bloc
    item_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.tree_widget.itemClicked.connect(self.on_item_clicked)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("📝 Plan du document")
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

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        layout.addWidget(self.tree_widget)

        self.setLayout(layout)

    def update_outline(self, document):
        """Met à jour le plan à partir du contenu du document."""
        self.tree_widget.clear()
        parent_items = [self.tree_widget] * 6  # Pour gérer les niveaux d'indentation

        for i in range(document.blockCount()):
            block = document.findBlockByNumber(i)
            text = block.text()
            match = re.match(r"^(#{1,6})\s+(.*)", text)

            if match:
                level = len(match.group(1))
                title = match.group(2).strip()

                item = QTreeWidgetItem()
                item.setText(0, title)
                item.setData(0, Qt.UserRole, block.position())  # Stocker la position

                parent = parent_items[level - 1]
                # Ajouter l'item au bon parent pour l'indentation
                if isinstance(parent, QTreeWidget):
                    parent.addTopLevelItem(item)
                else:
                    parent.addChild(item)
                # Mettre à jour les parents pour les niveaux inférieurs
                for j in range(level, 6):
                    parent_items[j] = item

    def on_item_clicked(self, item, column):
        """Gère le clic sur un élément du plan."""
        position = item.data(0, Qt.UserRole)
        if position is not None:
            self.item_clicked.emit(position)

    def apply_styles(self, font, heading_color, background_color):
        """Applique les styles de l'éditeur au panneau."""
        self.tree_widget.setFont(font)
        self.tree_widget.setStyleSheet(
            f"""
            QTreeWidget {{
                background-color: {background_color.name()};
                color: {heading_color.name()};
                border: none;
            }}
            QTreeWidget::item:hover {{
                background-color: {background_color.lighter(110).name()};
            }}
            QTreeWidget::item:selected {{
                background-color: {heading_color.name()};
                color: {background_color.name()};
            }}
        """
        )

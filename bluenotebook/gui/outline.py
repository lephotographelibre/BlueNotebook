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
    QHBoxLayout,
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

        # Layout pour l'en-tête pour contrôler son alignement
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        # En-tête de panneau (style onglet)
        self.label = QLabel("Plan du document")
        self.label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa;
                padding: 8px 12px;
                font-weight: bold;
                color: #24292e;
                border: 1px solid #d1d5da;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
        """
        )
        header_layout.addWidget(self.label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        layout.addWidget(self.tree_widget)

        self.setLayout(layout)

    def update_outline(self, document):
        """Met à jour le plan à partir du contenu du document."""
        self.tree_widget.clear()
        parent_items = [self.tree_widget] * 6  # Pour gérer les niveaux d'indentation

        block = document.firstBlock()
        while block.isValid():
            # V2.4.2 Fix: Ignorer les titres à l'intérieur des blocs de code
            # On vérifie que le bloc précédent est valide avant de lire son état.
            previous_block = block.previous()
            if previous_block.isValid() and previous_block.userState() == 1:
                # Ce bloc est à l'intérieur d'un bloc de code, on l'ignore.
                block = block.next()
                continue

            text = block.text().strip()
            match = re.match(r"^(#{1,6})\s*(.*)", text)
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

            block = block.next()

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
            
            /* Style pour la barre de défilement verticale */
            QScrollBar:vertical {{
                border: none;
                background: #e0e0e0; /* Fond de la barre de défilement */
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #b0b0b0; /* Couleur de l'indicateur (gris clair) */
                min-height: 25px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #a0a0a0; /* Un peu plus foncé au survol */
            }}

        """
        )

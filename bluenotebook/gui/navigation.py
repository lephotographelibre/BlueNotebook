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

Panneau de navigation de BlueNotebook
"""

from PyQt5.QtCore import QDate, pyqtSignal, Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QBrush, QFont, QIcon
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QCalendarWidget,
    QLabel,
    QPushButton,
    QToolBar,
    QAction,
)
from .tag_cloud import TagCloudPanel


class NavigationPanel(QWidget):
    """
    Panneau de navigation contenant un calendrier et d'autres outils
    de navigation futurs.
    """

    # Signal émis lorsqu'une date est cliquée dans le calendrier
    date_clicked = pyqtSignal(QDate)

    # Signal émis lorsque le bouton "Aujourd'hui" est cliqué
    today_button_clicked = pyqtSignal()

    # Signal émis lorsque le bouton "Jour Précédent" est cliqué
    prev_day_button_clicked = pyqtSignal()

    # Signal émis lorsque le bouton "Jour Suivant" est cliqué
    next_day_button_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Pas de marges extérieures
        layout.setSpacing(0)  # Pas d'espacement entre les widgets principaux

        # Titre du panneau
        title_label = QLabel("🧭 Navigation")
        title_label.setStyleSheet(
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
        title_label.setMaximumHeight(35)
        layout.addWidget(title_label)

        # Barre d'outils de navigation
        nav_toolbar = self._create_toolbar()
        layout.addWidget(nav_toolbar)

        # Calendrier
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Assurer que le calendrier garde une taille constante (carrée)
        # La largeur du panneau parent est fixée à 400px dans main_window.py
        self.calendar.setFixedSize(400, 250)
        self.calendar.clicked.connect(self.date_clicked.emit)
        layout.addWidget(self.calendar)

        # Nuage de tags
        self.tag_cloud = TagCloudPanel()
        self.tag_cloud.setFixedSize(400, 300)
        layout.addWidget(self.tag_cloud)

        # Ajouter un espace flexible pour pousser tous les widgets vers le haut
        layout.addStretch()

        self.setLayout(layout)

    def _create_toolbar(self):
        """Crée la barre d'outils de navigation."""
        # Utiliser un QWidget avec un QHBoxLayout pour un meilleur contrôle du rendu HTML
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)

        self.prev_day_button = QPushButton("Précédent")
        self.prev_day_button.setIcon(QIcon.fromTheme("go-previous"))
        self.prev_day_button.clicked.connect(self.prev_day_button_clicked.emit)

        self.today_button = QPushButton("Aujourd'hui")
        self.today_button.setIcon(QIcon.fromTheme("go-home"))
        self.today_button.clicked.connect(self.today_button_clicked.emit)

        self.next_day_button = QPushButton("Suivant")
        self.next_day_button.setIcon(QIcon.fromTheme("go-next"))
        self.next_day_button.setLayoutDirection(Qt.RightToLeft)
        self.next_day_button.clicked.connect(self.next_day_button_clicked.emit)

        toolbar_layout.addWidget(self.prev_day_button)
        toolbar_layout.addWidget(self.today_button)
        toolbar_layout.addWidget(self.next_day_button)

        return toolbar_widget

    def highlight_dates(self, dates):
        """
        Met en surbrillance les dates fournies dans le calendrier.

        :param dates: Une liste ou un set d'objets QDate à surligner.
        """
        # Format pour les dates avec une note
        date_format = QTextCharFormat()
        # Utilise la même couleur bleue que le label du journal
        date_format.setForeground(QBrush(QColor("#3498db")))
        date_format.setFontWeight(700)  # Gras

        for date in dates:
            self.calendar.setDateTextFormat(date, date_format)

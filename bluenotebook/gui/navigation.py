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

from PyQt5.QtCore import QDate, pyqtSignal
from PyQt5.QtGui import QTextCharFormat, QColor, QBrush
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QCalendarWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
)


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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        # Label compact en haut
        label = QLabel("🧭 Navigation")
        label.setStyleSheet(
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
        label.setMaximumHeight(35)
        layout.addWidget(label)

        # Barre de boutons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(5)

        self.prev_day_button = QPushButton("⬅️ Jour Précédent")
        self.prev_day_button.clicked.connect(self.prev_day_button_clicked.emit)
        self.today_button = QPushButton("📅 Aujourd'hui")
        self.today_button.clicked.connect(self.today_button_clicked.emit)
        self.next_day_button = QPushButton("Jour Suivant ➡️")
        self.next_day_button.clicked.connect(self.next_day_button_clicked.emit)

        button_layout.addWidget(self.prev_day_button)
        button_layout.addWidget(self.today_button)
        button_layout.addWidget(self.next_day_button)

        layout.addLayout(button_layout)

        self.calendar = QCalendarWidget()
        self.calendar.setFixedHeight(300)
        # Connecter le signal du calendrier à notre propre signal
        self.calendar.clicked.connect(self.date_clicked.emit)

        layout.addWidget(self.calendar)

        layout.addStretch()  # Pour pousser le calendrier en haut
        self.setLayout(layout)

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

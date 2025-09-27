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
    QSizePolicy,
    QLineEdit,
    QPushButton,
    QToolBar,
    QMenu,
    QAction,
    QToolButton,
)
from .word_cloud import WordCloudPanel
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

    # Signal pour la recherche de tag
    tag_search_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_tags = []
        self.setup_ui()
        self.tag_search_input.textChanged.connect(self.on_tag_search_changed)
        self.tag_search_input.returnPressed.connect(self.on_search_triggered)

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

        # Conteneur pour le champ de recherche et le bouton de menu déroulant
        search_container = QWidget()
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 5, 0, 5)
        search_layout.setSpacing(2)

        # Champ de recherche de tag
        self.tag_search_input = QLineEdit()
        self.tag_search_input.setPlaceholderText("tag")
        self.tag_search_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #ced4da;
                border-top-left-radius: 4px;
                border-bottom-left-radius: 4px;
                border-right: none; /* Fusionne avec le bouton */
            }
        """
        )
        # Action de recherche pour le QLineEdit
        search_action = QAction(self)
        search_action.setIcon(QIcon.fromTheme("edit-find"))
        search_action.triggered.connect(self.on_search_triggered)
        self.tag_search_input.addAction(search_action, QLineEdit.TrailingPosition)
        search_layout.addWidget(self.tag_search_input)

        # Bouton pour le menu déroulant des tags
        self.tag_dropdown_button = QPushButton()
        self.tag_dropdown_button.setFixedWidth(30)
        # Assure que le bouton s'étire verticalement pour correspondre au QLineEdit
        self.tag_dropdown_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        self.tag_dropdown_button.setIcon(QIcon.fromTheme("go-down"))
        self.tag_dropdown_button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #ced4da;
                border-top-right-radius: 4px;
                border-bottom-right-radius: 4px;
            }
        """
        )
        self.tag_dropdown_button.clicked.connect(self.show_tag_dropdown)
        search_layout.addWidget(self.tag_dropdown_button)

        layout.addWidget(search_container)

        # Nuage de tags
        self.tag_cloud = TagCloudPanel()
        self.tag_cloud.setFixedSize(400, 250)
        layout.addWidget(self.tag_cloud)

        # Nuage de mots
        self.word_cloud = WordCloudPanel()
        self.word_cloud.setFixedSize(400, 300)
        layout.addWidget(self.word_cloud)

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

    def on_tag_search_changed(self, text):
        """Ajoute automatiquement '@@' au début du champ de recherche de tag."""
        # Si le champ est vide ou commence déjà par '@@', ne rien faire.
        if not text or text.startswith("@@"):
            return

        # Bloquer les signaux pour éviter une boucle récursive
        self.tag_search_input.blockSignals(True)

        self.tag_search_input.setText(f"@@{text}")

        # Débloquer les signaux
        self.tag_search_input.blockSignals(False)

    def on_search_triggered(self):
        """Déclenché lorsque l'icône de recherche est cliquée ou sur Entrée."""
        search_text = self.tag_search_input.text()
        self.tag_search_triggered.emit(search_text)

    def set_available_tags(self, tags: list):
        """Reçoit la liste des tags disponibles depuis la MainWindow."""
        self.available_tags = tags

    def show_tag_dropdown(self):
        """Affiche le menu déroulant avec les tags disponibles."""
        if not self.available_tags:
            return

        menu = QMenu(self)
        for tag in self.available_tags:
            action = QAction(tag, self)
            action.triggered.connect(
                lambda checked, t=tag: self.tag_search_input.setText(t)
            )
            menu.addAction(action)

        # Positionner le menu sous le bouton
        button_pos = self.tag_dropdown_button.mapToGlobal(
            self.tag_dropdown_button.rect().bottomLeft()
        )
        menu.exec_(button_pos)

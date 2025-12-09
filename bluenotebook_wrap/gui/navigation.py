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
    QStackedWidget,
    QSizePolicy,
    QLineEdit,
    QPushButton,
    QToolBar,
    QMenu,
    QAction,
    QToolButton,
)
from .search_results_panel import SearchResultsPanel
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

    # Signal pour ouvrir un fichier depuis les résultats de recherche
    file_open_requested = pyqtSignal(str, int)

    # Signal pour demander un rafraîchissement de l'index
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_tags = []
        self.setup_ui()
        self.search_results_panel.refresh_requested.connect(self.refresh_requested.emit)
        self.tag_search_input.textChanged.connect(self.on_tag_search_changed)
        self.tag_search_input.returnPressed.connect(self.on_search_triggered)
        self.tag_cloud.tag_clicked.connect(self.on_tag_cloud_clicked)
        self.search_results_panel.item_selected.connect(self.file_open_requested.emit)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Pas de marges extérieures
        layout.setSpacing(0)  # Pas d'espacement entre les widgets principaux

        # V2.4.6 - Amélioration du style de l'en-tête pour un look d'onglet
        # V2.6.3 - Harmonisation du style de l'en-tête
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 5, 0, 0)  # Marge en haut pour l'esthétique

        self.title_label = QLabel(self.tr("Navigation Journal"))
        self.title_label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa;
                padding: 8px 12px;
                font-weight: bold;
                color: #24292e;
            }
        """
        )
        self.title_label.setCursor(Qt.PointingHandCursor)
        self.title_label.setToolTip(self.tr("Cliquez pour rafraîchir l'index des tags"))
        self.title_label.mousePressEvent = self.on_title_clicked
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Barre d'outils de navigation
        nav_toolbar = self._create_toolbar()
        layout.addWidget(nav_toolbar)

        # Calendrier
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Le calendrier s'adapte maintenant à la largeur du panneau
        self.calendar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.calendar.setFixedHeight(250)
        self.calendar.clicked.connect(self.date_clicked.emit)
        layout.addWidget(self.calendar)

        # Conteneur pour le champ de recherche et le bouton de menu déroulant
        search_container = QWidget()
        # Fixer la hauteur du conteneur pour éviter toute déformation verticale
        search_container.setFixedHeight(35)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 5, 0, 5)
        search_layout.setSpacing(2)

        # Champ de recherche de tag
        self.tag_search_input = QLineEdit()
        # V 1.6.9 Ajoute le bouton pour effacer le contenu du champ de recherche
        self.tag_search_input.setClearButtonEnabled(True)
        self.tag_search_input.setPlaceholderText(self.tr("@@tag"))

        # L'icône de loupe est maintenant gérée par le thème ou peut être ajoutée
        # via QSS si nécessaire, mais l'action est déclenchée par returnPressed.
        # Assurer que le champ de recherche s'étire verticalement
        self.tag_search_input.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        search_layout.addWidget(self.tag_search_input)

        # Bouton pour le menu déroulant des tags
        self.tag_dropdown_button = QToolButton()
        self.tag_dropdown_button.setFixedWidth(30)
        # Assurer que le bouton s'étire verticalement pour correspondre au QLineEdit
        self.tag_dropdown_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        self.tag_dropdown_button.setArrowType(Qt.DownArrow)
        self.tag_dropdown_button.clicked.connect(self.show_tag_dropdown)
        search_layout.addWidget(self.tag_dropdown_button)

        layout.addWidget(search_container)

        # Nuage de Tags (toujours visible)
        self.tag_cloud = TagCloudPanel()
        layout.addWidget(self.tag_cloud)

        # Panneau de résultats de recherche (toujours visible, prend l'espace restant)
        self.search_results_panel = SearchResultsPanel()
        layout.addWidget(
            self.search_results_panel, 1
        )  # Stretch factor to take remaining space

        # Ajouter un espace flexible pour pousser tous les widgets vers le haut
        # Supprimé car search_results_panel prend maintenant l'espace restant
        # layout.addStretch()

        self.setLayout(layout)

    """ def _create_toolbar(self):
        
        toolbar = QToolBar()
        toolbar.setMovable(False)

        # Bouton Jour Précédent
        self.prev_day_button = QToolButton()
        self.prev_day_button.setText("Précédent")
        self.prev_day_button.setIcon(QIcon.fromTheme("go-previous"))
        self.prev_day_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.prev_day_button.clicked.connect(self.prev_day_button_clicked.emit)
        self.prev_day_button.setAutoRaise(True)
        self.prev_day_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Bouton Aujourd'hui
        self.today_button = QToolButton()
        self.today_button.setText("Aujourd'hui")
        self.today_button.setIcon(QIcon.fromTheme("go-home"))
        self.today_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.today_button.clicked.connect(self.today_button_clicked.emit)
        self.today_button.setAutoRaise(True)
        self.today_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Bouton Jour Suivant
        self.next_day_button = QToolButton()
        self.next_day_button.setText("Suivant")
        self.next_day_button.setIcon(QIcon.fromTheme("go-next"))
        self.next_day_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.next_day_button.clicked.connect(self.next_day_button_clicked.emit)
        self.next_day_button.setLayoutDirection(Qt.RightToLeft)
        self.next_day_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.next_day_button.setAutoRaise(True)

        toolbar.addWidget(self.prev_day_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.today_button)
        toolbar.addSeparator()
        toolbar.addWidget(self.next_day_button)
        return toolbar
    """

    def _create_toolbar(self):
        """Crée la barre d'outils de navigation."""
        # Utiliser un QWidget avec un QHBoxLayout pour un meilleur contrôle du rendu HTML
        toolbar_widget = QWidget()
        # V2.6.3 - Forcer la couleur du texte des boutons de navigation
        # pour assurer la lisibilité sur tous les thèmes.

        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)

        self.prev_day_button = QPushButton(self.tr("◀️ Précédent"))
        self.prev_day_button.clicked.connect(self.prev_day_button_clicked.emit)

        self.today_button = QPushButton(self.tr("📅 Aujourd'hui"))
        self.today_button.clicked.connect(self.today_button_clicked.emit)

        self.next_day_button = QPushButton(self.tr("Suivant ▶️"))
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
        # Format pour les dates avec une note (non-aujourd'hui)
        date_format = QTextCharFormat()
        # Utilise la même couleur bleue que le label du journal
        date_format.setForeground(QBrush(QColor(self.tr("#3498db"))))
        date_format.setFontWeight(700)  # Gras

        # Format pour la date d'aujourd'hui avec une note
        today_format = QTextCharFormat()
        today_format.setForeground(QBrush(QColor(self.tr("#FFFF00"))))  # Jaune vif
        today_format.setFontWeight(QFont.Bold)
        # On peut aussi ajouter un fond pour améliorer la lisibilité
        today_format.setBackground(QBrush(QColor(self.tr("#3498db"))))

        today = QDate.currentDate()

        for date in dates:
            if date == today:
                self.calendar.setDateTextFormat(date, today_format)
            else:
                self.calendar.setDateTextFormat(date, date_format)

    def on_tag_search_changed(self, text):
        """Gère le changement de texte dans le champ de recherche."""
        # Si le champ de recherche est vidé, relancer la recherche par défaut sur @@TODO
        if not text:
            self.tag_search_triggered.emit(self.tr("@@TODO"))

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
                lambda checked, t=tag: self.on_tag_selected_from_dropdown(t)
            )
            menu.addAction(action)

        # Positionner le menu sous le bouton
        button_pos = self.tag_dropdown_button.mapToGlobal(
            self.tag_dropdown_button.rect().bottomLeft()
        )
        menu.exec_(button_pos)

    def on_tag_selected_from_dropdown(self, tag: str):
        """Met à jour le champ de recherche et lance la recherche."""
        self.tag_search_input.setText(tag)
        self.on_search_triggered()

    def on_tag_cloud_clicked(self, tag_name: str):
        """Met à jour le champ de recherche lorsqu'un tag est cliqué dans le nuage."""
        self.tag_search_input.setText(self.tr("@@%1").arg(tag_name))
        self.on_search_triggered()

    def show_search_results(self, results: list, search_query: str):
        """Met à jour le panneau de résultats avec les résultats et la requête."""
        self.search_results_panel.update_results(results, search_query)

    def on_title_clicked(self, event):
        """Émet un signal lorsque le titre est cliqué."""
        self.refresh_requested.emit()

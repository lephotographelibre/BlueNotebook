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

    # Signal pour ouvrir un fichier depuis les résultats de recherche
    file_open_requested = pyqtSignal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.available_tags = []
        self.setup_ui()
        self.tag_search_input.textChanged.connect(self.on_tag_search_changed)
        self.tag_search_input.returnPressed.connect(self.on_search_triggered)
        self.tag_cloud.tag_clicked.connect(self.on_tag_cloud_clicked)
        self.word_cloud.word_clicked.connect(self.on_word_cloud_clicked)
        self.search_results_panel.item_selected.connect(self.file_open_requested.emit)

    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Pas de marges extérieures
        layout.setSpacing(0)  # Pas d'espacement entre les widgets principaux

        # V2.4.6 - Amélioration du style de l'en-tête pour un look d'onglet
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel("Navigation Journal")
        title_label.setStyleSheet(
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
        header_layout.addWidget(title_label)
        header_layout.addStretch()  # Pousse le label vers la gauche
        layout.addLayout(header_layout)

        # Barre d'outils de navigation
        nav_toolbar = self._create_toolbar()
        layout.addWidget(nav_toolbar)

        # Calendrier
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Assurer que le calendrier garde une taille constante (carrée)
        # V2.6.3 - Forcer la couleur du texte de la barre de navigation du calendrier
        # pour assurer la lisibilité sur tous les thèmes.
        self.calendar.setStyleSheet(
            """
            QCalendarWidget QToolButton {
                color: #333333; /* Gris foncé pour une bonne lisibilité */
            }
            QCalendarWidget QSpinBox {
                color: #333333;
                background-color: transparent;
                border: none;
            }
            """
        )
        # La largeur du panneau parent est fixée à 400px dans main_window.py
        self.calendar.setFixedSize(400, 250)

        # V2.6.3 - Remplacer les flèches de navigation du calendrier par des émojis (Correctif)
        # Méthode robuste pour trouver les boutons par leur nom d'objet interne
        prev_button = self.calendar.findChild(QToolButton, "qt_calendar_prevmonth")
        next_button = self.calendar.findChild(QToolButton, "qt_calendar_nextmonth")

        if prev_button:
            prev_button.setText("◀️")
            prev_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
            prev_button.setFont(QFont("Arial", 14))

        if next_button:
            next_button.setText("▶️")
            next_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
            next_button.setFont(QFont("Arial", 14))

        # V2.6.3 - Forcer la couleur des jours sans note en gris clair
        # On récupère le format d'un jour de semaine (ex: Lundi) pour le modifier
        weekday_format = self.calendar.weekdayTextFormat(Qt.Monday)
        weekday_format.setForeground(QColor("#d7d6d6"))

        # On applique ce format à tous les jours de la semaine, y compris le week-end
        for day in [
            Qt.Monday,
            Qt.Tuesday,
            Qt.Wednesday,
            Qt.Thursday,
            Qt.Friday,
            Qt.Saturday,
            Qt.Sunday,
        ]:
            self.calendar.setWeekdayTextFormat(day, weekday_format)

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
        self.tag_search_input.setPlaceholderText("@@tag ou mot")
        self.tag_search_input.setStyleSheet(
            """
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                background-color: white; /* Fond blanc pour la lisibilité */
                color: #333333; /* Couleur du texte saisi */
                padding-right: 20px; /* Espace pour l'icône de loupe */
            }
            QLineEdit::placeholder {
                color: #868e96; /* Gris plus foncé pour le texte d'aide */
            }
            /* Style pour le bouton d'effacement natif (masqué) */
            QLineEdit::clear-button {
                image: url(none); /* Masquer l'image par défaut si nécessaire */
                background-image: url(none); /* Alternative pour certains thèmes */
                /* Si vous voulez utiliser une icône de votre thème : */
                /* image: url(path/to/your/clear-icon.png); */
            }
        """
        )
        # L'icône de loupe est maintenant gérée par le thème ou peut être ajoutée
        # via QSS si nécessaire, mais l'action est déclenchée par returnPressed.
        # Assurer que le champ de recherche s'étire verticalement
        self.tag_search_input.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding
        )
        search_layout.addWidget(self.tag_search_input)

        # Bouton pour le menu déroulant des tags
        self.tag_dropdown_button = QPushButton()
        self.tag_dropdown_button.setFixedWidth(30)
        # Assurer que le bouton s'étire verticalement pour correspondre au QLineEdit
        self.tag_dropdown_button.setSizePolicy(
            QSizePolicy.Preferred, QSizePolicy.Expanding
        )
        # V2.6.3 - Remplacer l'icône par un émoji pour une meilleure cohérence
        self.tag_dropdown_button.setText("▼")
        self.tag_dropdown_button.setFont(QFont("Arial", 12))
        self.tag_dropdown_button.setStyleSheet(
            """
            QPushButton {
                border: 1px solid #ced4da;
                border-radius: 4px;
                margin-left: 2px;
                color: #333333; /* Couleur de l'émoji */
                padding-bottom: 2px; /* Ajustement vertical de l'émoji */
            }
        """
        )
        self.tag_dropdown_button.clicked.connect(self.show_tag_dropdown)
        search_layout.addWidget(self.tag_dropdown_button)

        layout.addWidget(search_container)

        # Stacked widget pour basculer entre les nuages et les résultats de recherche
        self.stacked_widget = QStackedWidget()

        # Widget conteneur pour les deux nuages
        clouds_container = QWidget()
        clouds_layout = QVBoxLayout(clouds_container)
        clouds_layout.setContentsMargins(0, 0, 0, 0)
        clouds_layout.setSpacing(0)

        # Nuage de tags
        self.tag_cloud = TagCloudPanel()
        self.tag_cloud.setFixedSize(400, 250)
        clouds_layout.addWidget(self.tag_cloud)

        # Nuage de mots
        self.word_cloud = WordCloudPanel()
        self.word_cloud.setFixedSize(400, 300)
        clouds_layout.addWidget(self.word_cloud)

        self.stacked_widget.addWidget(clouds_container)
        self.search_results_panel = SearchResultsPanel()
        self.stacked_widget.addWidget(self.search_results_panel)

        layout.addWidget(self.stacked_widget)

        # Ajouter un espace flexible pour pousser tous les widgets vers le haut
        layout.addStretch()

        self.setLayout(layout)

    def _create_toolbar(self):
        """Crée la barre d'outils de navigation."""
        # Utiliser un QWidget avec un QHBoxLayout pour un meilleur contrôle du rendu HTML
        toolbar_widget = QWidget()
        # V2.6.3 - Forcer la couleur du texte des boutons de navigation
        # pour assurer la lisibilité sur tous les thèmes.
        toolbar_widget.setStyleSheet(
            """
            QPushButton {
                color: #333333; /* Gris foncé pour une bonne lisibilité */
            }
            """
        )
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(5, 2, 5, 2)
        toolbar_layout.setSpacing(5)

        self.prev_day_button = QPushButton("◀️ Précédent")
        self.prev_day_button.clicked.connect(self.prev_day_button_clicked.emit)

        self.today_button = QPushButton("📅 Aujourd'hui")
        self.today_button.clicked.connect(self.today_button_clicked.emit)

        self.next_day_button = QPushButton("Suivant ▶️")
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
        date_format.setForeground(QBrush(QColor("#3498db")))
        date_format.setFontWeight(700)  # Gras

        # Format pour la date d'aujourd'hui avec une note
        today_format = QTextCharFormat()
        today_format.setForeground(QBrush(QColor("#FFFF00")))  # Jaune vif
        today_format.setFontWeight(QFont.Bold)
        # On peut aussi ajouter un fond pour améliorer la lisibilité
        today_format.setBackground(QBrush(QColor("#3498db")))

        today = QDate.currentDate()

        for date in dates:
            if date == today:
                self.calendar.setDateTextFormat(date, today_format)
            else:
                self.calendar.setDateTextFormat(date, date_format)

    def on_tag_search_changed(self, text):
        """Gère le changement de texte dans le champ de recherche."""
        if not text:
            self.show_clouds()

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
        # V2.6.3 - Forcer la couleur de la police pour la liste déroulante des tags
        menu.setStyleSheet(
            """
            QMenu {
                background-color: white;
                border: 1px solid #ced4da;
            }
            QMenu::item {
                color: #333333;
            }
            QMenu::item:selected {
                background-color: #3498db;
            }
        """
        )
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
        self.tag_search_input.setText(f"@@{tag_name}")
        self.on_search_triggered()

    def on_word_cloud_clicked(self, word: str):
        """Met à jour le champ de recherche lorsqu'un mot est cliqué dans le nuage."""
        self.tag_search_input.setText(word)
        self.on_search_triggered()

    def show_search_results(self, results: list):
        """Affiche le panneau de résultats et masque les nuages."""
        self.search_results_panel.update_results(results)
        self.stacked_widget.setCurrentWidget(self.search_results_panel)

    def show_clouds(self):
        """Affiche les nuages et masque le panneau de résultats."""
        self.stacked_widget.setCurrentIndex(0)

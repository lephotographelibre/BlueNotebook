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

Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import webbrowser
import locale
import functools
import os
import re
import json
import shutil
from datetime import datetime
import zipfile
from datetime import datetime

from PyQt5.QtWebEngineWidgets import QWebEngineView
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QMenuBar,
    QMenu,
    QAction,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QDialog,
    QDialogButtonBox,
    QProgressDialog,
    QInputDialog,
    QToolBar,
    QPushButton,
    QRadioButton,
    QComboBox,
)
from PyQt5.QtWidgets import QFormLayout, QLineEdit
from PyQt5.QtWidgets import QSplitterHandle, QToolButton

from PyQt5.QtCore import Qt, QTimer, QDate, QUrl
from PyQt5.QtCore import (
    QThreadPool,
    QPropertyAnimation,
    QRect,
    QEasingCurve,
    pyqtProperty,
)
from PyQt5.QtGui import QKeySequence, QIcon, QFont, QPainter
from PyQt5.QtGui import QColor

from .custom_widgets import CenteredStatusBarLabel
from .editor import MarkdownEditor
from .preview import MarkdownPreview
from .navigation import NavigationPanel
from .outline import OutlinePanel
from .date_range_dialog import DateRangeDialog
from .preferences_dialog import PreferencesDialog
from core.journal_backup_worker import JournalBackupWorker
from core.quote_fetcher import QuoteFetcher
from .word_cloud import WordCloudPanel
from core.default_excluded_words import DEFAULT_EXCLUDED_WORDS
from integrations.weather import get_weather_markdown
import requests
from bs4 import BeautifulSoup
from integrations.gps_map_generator import get_location_name, create_gps_map
from core.word_indexer import start_word_indexing

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from integrations.epub_exporter import EpubExportWorker
from integrations.gpx_trace_generator import (
    create_gpx_trace_map,
    get_gpx_data,
)
from integrations.pdf_exporter import create_pdf_export_worker, PdfExportWorker
from integrations.amazon_books import (
    get_book_info_from_amazon,
    generate_book_markdown_fragment,
)
from integrations.youtube_video import (
    get_youtube_video_details,
    generate_youtube_markdown_block,
)
from integrations.sun_moon import get_sun_moon_markdown
from integrations.gps_map_handler import generate_gps_map_markdown

from integrations.pdf_converter import PdfToMarkdownWorker
from integrations.image_exif import format_exif_as_markdown


class BookWorker(QRunnable):
    """Worker pour la recherche de livre Amazon en arrière-plan."""

    class Signals(QObject):
        finished = pyqtSignal(str, bool)  # markdown_fragment, has_selection
        error = pyqtSignal(str)

    def __init__(self, isbn, has_selection):
        super().__init__()
        self.isbn = isbn
        self.has_selection = has_selection
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        try:
            book_data_json = get_book_info_from_amazon(self.isbn)  # Renamed function
            markdown_fragment = generate_book_markdown_fragment(
                book_data_json
            )  # Renamed function
            self.signals.finished.emit(
                markdown_fragment, self.has_selection
            )  # Renamed variable
        except Exception as e:
            self.signals.error.emit(str(e))


class SunMoonWorker(QRunnable):
    """Worker pour la recherche des données astro en arrière-plan."""

    class Signals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    def __init__(self, city, latitude, longitude):
        super().__init__()
        self.city = city
        self.latitude = latitude
        self.longitude = longitude
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        html_fragment, error_message = get_sun_moon_markdown(
            self.city, self.latitude, self.longitude
        )
        if error_message:
            self.signals.error.emit(error_message)
        else:
            self.signals.finished.emit(html_fragment)


class NewFileDialog(QDialog):
    """Boîte de dialogue pour choisir le type de nouveau fichier à créer."""

    def __init__(
        self, parent=None, use_template_by_default=False, default_template_name=None
    ):
        super().__init__(parent)
        self.setWindowTitle("Créer un nouveau document")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.blank_radio = QRadioButton("Créer un fichier vierge")
        self.template_radio = QRadioButton("Utiliser un modèle :")
        self.template_combo = QComboBox()

        self.layout.addWidget(self.blank_radio)
        self.layout.addWidget(self.template_radio)
        self.layout.addWidget(self.template_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText("Valider")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.layout.addWidget(self.button_box)

        self.blank_radio.toggled.connect(self.template_combo.setDisabled)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self._populate_templates()

        if use_template_by_default and default_template_name:
            index = self.template_combo.findText(default_template_name)
            if index != -1:
                self.template_combo.setCurrentIndex(index)
                self.template_radio.setChecked(True)
            else:
                # Fallback si le template par défaut n'est pas trouvé
                self.blank_radio.setChecked(True)
        else:
            self.blank_radio.setChecked(True)

    def _populate_templates(self):
        """Remplit le combobox avec les modèles trouvés."""
        base_path = Path(__file__).parent.parent
        templates_dir = base_path / "resources" / "templates"
        if templates_dir.is_dir():
            template_files = sorted([f.name for f in templates_dir.glob("*.md")])
            self.template_combo.addItems(template_files)

    def get_selection(self):
        """Retourne le choix de l'utilisateur."""
        if self.blank_radio.isChecked():
            return "blank", None
        else:
            if self.template_combo.count() > 0:
                return "template", self.template_combo.currentText()
            else:
                # Fallback si aucun template n'est trouvé
                return "blank", None


class SwitchButton(QPushButton):
    """Un bouton de type interrupteur (switch) inspiré de QtQuick.Controls."""

    def __init__(self, parent=None, text=""):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumHeight(24)

        # Calculer la largeur minimale en fonction du texte pour un ajustement parfait
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(
            text + "  "
        )  # Ajouter un peu d'espace
        self.setMinimumWidth(30 + text_width + 24)  # Marge gauche + texte + cercle

        self._circle_pos = 3
        self._animation = QPropertyAnimation(self, b"circle_pos", self)
        self._animation.setDuration(200)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)

        self.toggled.connect(self._on_toggled)
        # Mettre à jour la position initiale sans animation lorsque l'état est défini par programme
        self.toggled.connect(self._update_circle_pos_no_anim)

    def showEvent(self, event):
        """Initialise la position du cercle lorsque le widget est affiché."""
        self._circle_pos = self.width() - 23 if self.isChecked() else 2
        super().showEvent(event)
        # Forcer une mise à jour visuelle
        self.update()

    def _update_circle_pos_no_anim(self, checked):
        # Mettre à jour la position uniquement si l'animation n'est pas en cours
        if self._animation.state() != QPropertyAnimation.Running:
            self._circle_pos = self.width() - 23 if checked else 2

    def _get_circle_pos(self):
        return self._circle_pos

    def _set_circle_pos(self, pos):
        self._circle_pos = pos
        self.update()

    circle_pos = pyqtProperty(int, fget=_get_circle_pos, fset=_set_circle_pos)

    def _on_toggled(self, checked):
        end_pos = self.width() - 23 if checked else 2
        self._animation.setEndValue(end_pos)
        self._animation.start()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Solution robuste : Mettre à jour la position du cercle juste avant de dessiner,
        # mais seulement si aucune animation n'est en cours.
        if self._animation.state() != QPropertyAnimation.Running:
            self._circle_pos = self.width() - 23 if self.isChecked() else 2

        painter.setRenderHint(QPainter.Antialiasing)

        # Couleurs
        bg_color_off = QColor("#d1d5da")
        bg_color_on = QColor("#3498db")
        circle_color = QColor("#ffffff")
        text_color = QColor("#24292e")

        # Fond
        rect = self.rect()
        bg_rect = QRect(0, 0, rect.width(), rect.height())
        painter.setPen(Qt.NoPen)

        if self.isEnabled():
            bg_color = bg_color_on if self.isChecked() else bg_color_off
        else:
            bg_color = bg_color_on if self.isChecked() else QColor("#e0e0e0")

        painter.setBrush(bg_color)
        painter.drawRoundedRect(bg_rect, 14, 14)

        # Cercle
        painter.setBrush(circle_color)
        painter.drawEllipse(self._circle_pos, 2, 20, 20)

        # Texte
        painter.setPen(text_color)
        font = self.font()
        font.setBold(True)
        painter.setFont(font)
        text_rect = self.rect()
        text_rect.setLeft(30)
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, self.text())


class GpsInputDialog(QDialog):
    """Boîte de dialogue pour saisir les coordonnées GPS."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Coordonnées GPS")
        self.setMinimumWidth(300)

        self.layout = QFormLayout(self)

        self.lat_edit = QLineEdit(self)
        self.lon_edit = QLineEdit(self)

        self.layout.addRow("Latitude:", self.lat_edit)
        self.layout.addRow("Longitude:", self.lon_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText("Valider")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.layout.addRow(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    def get_coordinates(self):
        """Retourne la latitude et la longitude saisies."""
        lat_str = self.lat_edit.text().strip().replace(",", ".")
        lon_str = self.lon_edit.text().strip().replace(",", ".")
        try:
            return float(lat_str), float(lon_str)
        except (ValueError, TypeError):
            return None, None


class GpxSourceDialog(QDialog):
    """
    Boîte de dialogue pour obtenir le chemin d'un fichier GPX,
    soit via une URL, soit via un sélecteur de fichier.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Source du fichier GPX")
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Champ pour le chemin/URL
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            "https://example.com/trace.gpx ou /chemin/local/trace.gpx"
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow("Chemin ou URL:", path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier GPX", "", "Fichiers GPX (*.gpx)"
        )
        if path:
            self.path_edit.setText(path)

    def get_path(self):
        return self.path_edit.text().strip()


class PdfSourceDialog(QDialog):
    """
    Boîte de dialogue pour obtenir le chemin d'un fichier PDF,
    soit via une URL, soit via un sélecteur de fichier.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Source du fichier PDF")
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            "https://example.com/document.pdf ou /chemin/local/document.pdf"
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow("Chemin ou URL:", path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier PDF", "", "Fichiers PDF (*.pdf)"
        )
        if path:
            self.path_edit.setText(path)

    def get_path(self):
        return self.path_edit.text().strip()


class CollapsibleSplitterHandle(QSplitterHandle):
    """Poignée de splitter avec des boutons pour réduire/restaurer les panneaux."""

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.splitter = parent

        layout = (
            QHBoxLayout(self) if orientation == Qt.Horizontal else QVBoxLayout(self)
        )
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.button_left = QToolButton(self)
        self.button_right = QToolButton(self)

        if orientation == Qt.Horizontal:
            self.button_left.setArrowType(Qt.LeftArrow)
            self.button_right.setArrowType(Qt.RightArrow)
            layout.addWidget(self.button_left)
            layout.addStretch()
            layout.addWidget(self.button_right)
        else:  # Vertical
            self.button_left.setArrowType(Qt.UpArrow)
            self.button_right.setArrowType(Qt.DownArrow)
            layout.addWidget(self.button_left)
            layout.addStretch()
            layout.addWidget(self.button_right)

        self.button_left.setFixedSize(12, 12)
        self.button_right.setFixedSize(12, 12)

        # Style pour rendre les flèches plus visibles
        button_style = """
            QToolButton {
                border: none;
                background-color: #e0e0e0;
                border-radius: 6px;
            }
            QToolButton:hover {
                background-color: #3498db;
            }
        """
        self.button_left.setStyleSheet(button_style)
        self.button_right.setStyleSheet(button_style)

        self.button_left.clicked.connect(lambda: self.collapse_or_expand(is_left=True))
        self.button_right.clicked.connect(
            lambda: self.collapse_or_expand(is_left=False)
        )

    def collapse_or_expand(self, is_left):
        """Réduit ou restaure les panneaux adjacents."""
        sizes = self.splitter.sizes()
        handle_index = self.splitter.indexOf(self)
        if is_left:
            # Collapse left widget
            if sizes[handle_index - 1] > 0:
                sizes[handle_index - 1] = 0
            else:  # Restore
                total = sum(sizes)
                if total > 0:
                    sizes[handle_index - 1] = int(total * 0.25)  # Restore to 25%
        else:  # button_right
            # Collapse right widget
            if sizes[handle_index] > 0:
                sizes[handle_index] = 0
            else:  # Restore
                total = sum(sizes)
                if total > 0:
                    sizes[handle_index] = int(total * 0.25)  # Restore to 25%

        # Redistribute remaining space
        total = sum(sizes)
        non_zero_widgets = [i for i, size in enumerate(sizes) if size > 0]
        if non_zero_widgets:
            extra_space = self.splitter.width() - total
            per_widget_extra = extra_space / len(non_zero_widgets)
            for i in non_zero_widgets:
                sizes[i] += per_widget_extra

        self.splitter.setSizes([int(s) for s in sizes])


class CollapsibleSplitter(QSplitter):
    def createHandle(self):
        return CollapsibleSplitterHandle(self.orientation(), self)


class InsertTemplateDialog(QDialog):
    """Boîte de dialogue pour choisir un modèle à insérer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Insérer un modèle")
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("Choisir un modèle à insérer :")
        self.template_combo = QComboBox()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.template_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText("Insérer")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.layout.addWidget(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self._populate_templates()

    def _populate_templates(self):
        """Remplit le combobox avec les modèles trouvés."""
        base_path = Path(__file__).parent.parent
        templates_dir = base_path / "resources" / "templates"
        if templates_dir.is_dir():
            template_files = sorted([f.name for f in templates_dir.glob("*.md")])
            self.template_combo.addItems(template_files)


class MainWindow(QMainWindow):
    def __init__(self, journal_dir_arg=None, app_version="2.4.4"):
        super().__init__()
        self.journal_dir_arg = journal_dir_arg
        self.app_version = app_version
        self.journal_directory = None
        self.current_file = None
        self.is_modified = False
        self.daily_quote = None
        self.daily_author = None
        self.tag_index_count = -1
        self.word_index_count = -1

        from core.settings import SettingsManager

        self.settings_manager = SettingsManager()

        # Initialiser le pool de threads pour les tâches de fond
        self.thread_pool = QThreadPool()

        self.setup_ui()
        self.setup_menu()
        self.setup_panels_toolbar()
        self.setup_statusbar()
        self.apply_settings()
        self.setup_connections()
        self.setup_journal_directory()

        # Timer pour mettre à jour l'aperçu
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)

        # Timer pour la synchronisation du curseur
        self.cursor_sync_timer = QTimer()
        self.cursor_sync_timer.setSingleShot(True)
        self.cursor_sync_timer.timeout.connect(self.sync_preview_to_cursor)

        # Lancer les tâches de fond après que la fenêtre principale soit prête
        QTimer.singleShot(0, self.run_startup_tasks)

    def run_startup_tasks(self):
        """Exécute les tâches qui peuvent être lancées après l'affichage de l'UI."""
        self.load_initial_file()
        self.show_quote_of_the_day()
        self.start_initial_indexing()
        self.update_calendar_highlights()

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle(f"BlueNotebook V{self.app_version} - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)

        self.set_application_icon()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Appliquer un fond neutre à la fenêtre principale
        # central_widget.setStyleSheet("background-color: #f0f2f5;")

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)

        main_splitter = CollapsibleSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(4)
        main_splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: transparent;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """
        )
        self.navigation_panel = NavigationPanel()
        main_splitter.addWidget(self.navigation_panel)

        self.outline_panel = OutlinePanel()
        main_splitter.addWidget(self.outline_panel)

        # --- Splitter interne ---
        editor_preview_splitter = CollapsibleSplitter(Qt.Horizontal)
        editor_preview_splitter.setHandleWidth(4)
        editor_preview_splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: transparent;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """
        )
        self.editor = MarkdownEditor(main_window=self)
        editor_preview_splitter.addWidget(self.editor)

        self.preview = MarkdownPreview()
        editor_preview_splitter.addWidget(self.preview)

        editor_preview_splitter.setSizes([700, 700])
        editor_preview_splitter.setCollapsible(0, False)
        editor_preview_splitter.setCollapsible(1, False)
        main_splitter.addWidget(editor_preview_splitter)

        self.navigation_panel.setFixedWidth(400)
        self.outline_panel.setFixedWidth(400)
        main_splitter.setSizes([400, 400, 1400])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(2, False)

        main_layout.addWidget(main_splitter)

    def set_application_icon(self):
        """Définir l'icône de l'application"""
        base_path = os.path.dirname(os.path.abspath(__file__))

        icon_paths = [
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook.ico"),
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook.png"),
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook_64.png"),
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        from PyQt5.QtWidgets import QApplication

                        QApplication.instance().setWindowIcon(icon)
                        print(f"✅ Icône chargée : {icon_path}")
                        return
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de {icon_path}: {e}")
                    continue

        print("ℹ️ Aucune icône trouvée, utilisation de l'icône par défaut")

    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()

        self._create_actions()

        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_template_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_journal_action)
        file_menu.addAction(self.backup_journal_action)
        file_menu.addAction(self.restore_journal_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addAction(self.export_journal_epub_action)
        file_menu.addAction(self.export_journal_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.preferences_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")
        edit_menu.addAction(self.insert_template_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)

        # Les actions de basculement des panneaux sont conservées pour les raccourcis clavier
        self.addAction(self.toggle_navigation_action)
        self.addAction(self.toggle_outline_action)
        self.addAction(self.toggle_preview_action)

        # Menu Formatter
        format_menu = menubar.addMenu("F&ormater")
        self._setup_format_menu(format_menu)

        # Menu Insérer
        insert_menu = menubar.addMenu("&Insérer")
        self._setup_insert_menu(insert_menu)

        # Menu Intégrations
        integrations_menu = menubar.addMenu("&Intégrations")
        integrations_menu.addAction(self.insert_quote_day_action)
        integrations_menu.addAction(self.insert_gpx_trace_action)
        integrations_menu.addAction(self.insert_gps_map_action)
        integrations_menu.addAction(self.insert_youtube_video_action)
        integrations_menu.addAction(self.insert_weather_action)
        integrations_menu.addAction(self.insert_amazon_book_action)
        integrations_menu.addAction(self.insert_sun_moon_action)
        integrations_menu.addAction(self.convert_pdf_markdown_action)

        # Menu Aide
        help_menu = menubar.addMenu("&Aide")
        help_menu.addAction(self.online_help_action)
        help_menu.addAction(self.about_action)

    def _create_actions(self):
        """Crée toutes les actions de l'application."""
        self.new_action = QAction(
            "Nouveau",
            self,
            shortcut=QKeySequence.New,
            statusTip="Créer un nouveau fichier",
            triggered=self.new_file,
        )
        self.open_action = QAction(
            "Ouvrir",
            self,
            shortcut=QKeySequence.Open,
            statusTip="Ouvrir un fichier existant",
            triggered=self.open_file,
        )
        self.open_journal_action = QAction(
            "Ouvrir Journal",
            self,
            statusTip="Ouvrir un répertoire de journal",
            triggered=self.open_journal,
        )
        self.save_action = QAction(
            "Sauvegarder dans Journal",
            self,
            shortcut=QKeySequence.Save,
            statusTip="Sauvegarder le fichier dans le journal",
            triggered=self.save_file,
        )
        self.save_as_action = QAction(
            "Sauvegarder sous...",
            self,
            shortcut=QKeySequence.SaveAs,
            statusTip="Sauvegarder sous un nouveau nom",
            triggered=self.save_file_as,
        )
        self.save_as_template_action = QAction(
            "Sauvegarder comme Modèle...",
            self,
            statusTip="Sauvegarder le document actuel comme un nouveau modèle",
            triggered=self.save_as_template,
        )
        self.backup_journal_action = QAction(
            "Sauvegarde Journal...",
            self,
            statusTip="Sauvegarder le journal complet dans une archive ZIP",
            triggered=self.backup_journal,
        )
        self.restore_journal_action = QAction(
            "Restauration Journal...",
            self,
            statusTip="Restaurer le journal depuis une archive ZIP",
            triggered=self.restore_journal,
        )
        self.export_action = QAction(
            "Exporter HTML...",
            self,
            statusTip="Exporter en HTML",
            triggered=self.export_html,
        )
        self.export_journal_pdf_action = QAction(
            "Exporter Journal PDF...",
            self,
            statusTip="Exporter le journal complet en PDF",
            triggered=self.export_journal_pdf,
        )
        self.export_journal_epub_action = QAction(
            "Exporter Journal EPUB...",
            self,
            statusTip="Exporter le journal complet en EPUB",
            triggered=self.export_journal_epub,
        )
        self.preferences_action = QAction(
            "Préférences...",
            self,
            statusTip="Ouvrir les préférences de l'application",
            triggered=self.open_preferences,
        )
        self.quit_action = QAction(
            "Quitter",
            self,
            shortcut=QKeySequence.Quit,
            statusTip="Quitter l'application",
            triggered=self.close,
        )

        self.undo_action = QAction(
            "Annuler", self, shortcut=QKeySequence.Undo, triggered=self.editor.undo
        )
        self.redo_action = QAction(
            "Rétablir", self, shortcut=QKeySequence.Redo, triggered=self.editor.redo
        )
        self.find_action = QAction(
            "Rechercher",
            self,
            shortcut=QKeySequence.Find,
            triggered=self.editor.show_find_dialog,
        )
        self.toggle_navigation_action = QAction(
            "Basculer Navigation Journal",
            self,
            shortcut="F6",
            checkable=True,
            triggered=self.toggle_navigation,
        )
        self.toggle_outline_action = QAction(
            "Basculer Plan du document",
            self,
            shortcut="F7",
            checkable=True,
            triggered=self.toggle_outline,
        )
        self.toggle_preview_action = QAction(
            "Basculer Aperçu HTML",
            self,
            shortcut="F5",
            checkable=True,
            triggered=self.toggle_preview,
        )
        self.about_action = QAction(
            "À propos",
            self,
            triggered=self.show_about,
        )

        self.online_help_action = QAction(
            "Documentation en ligne",
            self,
            triggered=self.show_online_help,
        )

        self.insert_quote_day_action = QAction(
            "Citation du jour",
            self,
            triggered=self.insert_quote_of_the_day,
        )

        self.insert_youtube_video_action = QAction(
            "Vidéo YouTube",
            self,
            icon=QIcon("bluenotebook/resources/icons/youtube_32px.png"),
            statusTip="Insérer une vidéo YouTube",
            triggered=self.insert_youtube_video,
        )
        self.insert_template_action = QAction(
            "Insérer un modèle...",
            self,
            statusTip="Insérer le contenu d'un modèle à la position du curseur",
            triggered=self.insert_template,
        )
        self.insert_gps_map_action = QAction(
            "Carte GPS",
            self,
            statusTip="Insérer une carte statique à partir de coordonnées GPS",
            triggered=self.insert_gps_map,
        )
        self.insert_gpx_trace_action = QAction(
            "Trace GPX",
            self,
            statusTip="Insérer une carte à partir d'une trace GPX",
            triggered=self.insert_gpx_trace,
        )
        self.insert_weather_action = QAction(
            "Météo Weatherapi.com",
            self,
            statusTip="Insérer la météo actuelle",
            triggered=self.insert_weather,
        )
        self.insert_amazon_book_action = QAction(
            "Amazon ISBN",
            self,
            statusTip="Insérer les informations d'un livre depuis Amazon via son ISBN",
            triggered=self.insert_amazon_book,
        )
        self.insert_sun_moon_action = QAction(
            "Astro du jour",
            self,
            statusTip="Insérer les données astronomiques du jour",
            triggered=self.insert_sun_moon_data,
        )
        self.convert_pdf_markdown_action = QAction(
            "Conversion PDF-Markdown",
            self,
            statusTip="Convertir un fichier PDF en Markdown avec 'markit'",
            triggered=self.convert_pdf_to_markdown,
        )

    def _setup_format_menu(self, format_menu):
        """Configure le menu de formatage de manière dynamique."""
        # Sous-menu Titre
        title_menu = QMenu("Titres", self)
        title_actions_data = [
            ("Niv 1 (#)", "h1"),
            ("Niv 2 (##)", "h2"),
            ("Niv 3 (###)", "h3"),
            ("Niv 4 (####)", "h4"),
            ("Niv 5 (#####)", "h5"),
        ]
        for name, data in title_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            title_menu.addAction(action)
        format_menu.addMenu(title_menu)

        # Sous-menu Style de texte
        style_menu = QMenu("Style de texte", self)
        style_actions_data = [
            ("Gras (**texte**)", "bold", QKeySequence.Bold),
            ("Italique (*texte*)", "italic"),
            ("Barré (~~texte~~)", "strikethrough"),
            ("Surligné (==texte==)", "highlight"),
        ]
        for name, data, *shortcut in style_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            if shortcut:
                action.setShortcut(shortcut[0])
            style_menu.addAction(action)
        format_menu.addMenu(style_menu)

        # Sous-menu Code
        code_menu = QMenu("Code", self)
        code_actions_data = [
            ("Monospace (inline)", "inline_code"),
            ("Bloc de code", "code_block"),
        ]
        for name, data in code_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            code_menu.addAction(action)
        format_menu.addMenu(code_menu)

        # Sous-menu Listes
        list_menu = QMenu("Listes", self)
        list_actions_data = [
            ("• Liste non ordonnée", "ul"),
            ("1. Liste ordonnée", "ol"),
            ("☑️ Liste de tâches", "task_list"),
        ]
        for name, data in list_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            list_menu.addAction(action)
        format_menu.addMenu(list_menu)

        format_menu.addSeparator()

        clear_action = QAction("RaZ (Effacer le formatage)", self)
        clear_action.triggered.connect(self.editor.clear_formatting)
        format_menu.addAction(clear_action)

    def _setup_insert_menu(self, insert_menu):
        """Configure le menu d'insertion de manière dynamique."""
        action_img_html = QAction("Image (<img ...>)", self)
        action_img_html.setShortcut(QKeySequence.Italic)
        action_img_html.triggered.connect(self.insert_html_image)
        insert_menu.addAction(action_img_html)

        insert_actions_data = [
            (
                "Image Markdown",
                "markdown_image",
                QKeySequence("Ctrl+Shift+I"),
            ),
            ("Lien Markdown", "markdown_link"),
            ("Lien URL/Email", "url_link"),
            ("📎 Attachement", "attachment"),
        ]

        for name, data, *shortcut in insert_actions_data:  # type: ignore
            action = QAction(name, self)
            action.triggered.connect(functools.partial(self.editor.format_text, data))
            if shortcut:
                action.setShortcut(shortcut[0])
            insert_menu.addAction(action)

        insert_menu.addSeparator()

        insert_hr_action = QAction("Ligne Horizontale", self)
        insert_hr_action.triggered.connect(lambda: self.editor.format_text("hr"))

        insert_comment_action = QAction("Commentaire HTML", self)
        insert_comment_action.triggered.connect(
            lambda: self.editor.format_text("html_comment")
        )

        insert_table_action = QAction("Tableau", self)
        insert_table_action.triggered.connect(lambda: self.editor.format_text("table"))
        insert_quote_action = QAction("Citation", self)
        insert_quote_action.triggered.connect(lambda: self.editor.format_text("quote"))

        insert_menu.addAction(insert_hr_action)
        insert_menu.addAction(insert_comment_action)
        insert_menu.addAction(insert_table_action)
        insert_menu.addAction(insert_quote_action)
        insert_menu.addSeparator()

        insert_tag_action = QAction("Tag (@@)", self)
        insert_tag_action.triggered.connect(lambda: self.editor.format_text("tag"))
        insert_menu.addAction(insert_tag_action)

        insert_time_action = QAction("Heure", self)
        insert_time_action.triggered.connect(lambda: self.editor.format_text("time"))
        insert_menu.addAction(insert_time_action)
        insert_menu.addSeparator()

        # Sous-menu Emoji
        emoji_menu = QMenu("Emoji", self)
        emoji_actions_data = [
            ("📖 Livre", "📖"),
            ("🎵 Musique", "🎵"),
            ("📚 À Lire", "📚"),
            ("🎬 À Regarder", "🎬"),
            ("🎧 A Ecouter", "🎧"),
            ("✈️ Voyage", "✈️"),
            ("❤️ Santé", "❤️"),
            ("☀️ Soleil", "☀️"),
            ("☁️ Nuage", "☁️"),
            ("🌧️ Pluie", "🌧️"),
            ("🌬️ Vent", "🌬️"),
            ("😊 Content", "😊"),
            ("😠 Mécontent", "😠"),
            ("😢 Triste", "😢"),
            ("✅ Fait", "✅"),
            ("❌ Annulé", "❌"),
            ("⚠️ Attention", "⚠️"),
            ("📝 Mémo", "📝"),
            ("❓ Question", "❓"),
            ("❗ Exclamation", "❗"),
        ]
        for name, emoji in emoji_actions_data:
            action = QAction(
                name, self, triggered=functools.partial(self.editor.insert_text, emoji)
            )
            emoji_menu.addAction(action)
        insert_menu.addMenu(emoji_menu)

    def setup_panels_toolbar(self):
        """Configure la barre d'outils pour basculer les panneaux."""
        self.panels_toolbar = QToolBar("Panneaux")
        self.panels_toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.panels_toolbar)

        # Style pour la barre d'outils pour un fond uni
        self.panels_toolbar.setStyleSheet("QToolBar { border: none; }")

        # Bouton Navigation
        self.nav_button = SwitchButton(text="Navigation")
        self.nav_button.toggled.connect(self.navigation_panel.setVisible)
        self.panels_toolbar.addWidget(self.nav_button)

        # Bouton Plan
        self.outline_button = SwitchButton(text="Plan")
        self.outline_button.toggled.connect(self.outline_panel.setVisible)
        self.panels_toolbar.addWidget(self.outline_button)

        # Bouton Éditeur (toujours visible et désactivé)
        self.editor_button = SwitchButton(text="Éditeur")
        self.editor_button.setChecked(True)
        self.editor_button.setEnabled(False)
        self.panels_toolbar.addWidget(self.editor_button)

        # Bouton Aperçu
        self.preview_button = SwitchButton(text="Aperçu")
        self.preview_button.toggled.connect(self.preview.setVisible)
        self.panels_toolbar.addWidget(self.preview_button)

        # Note: Les états initiaux seront définis dans apply_settings() après le chargement des préférences

    def _sync_panel_controls(self):
        """Synchronise l'état des boutons et des menus avec la visibilité des panneaux."""
        # Bloquer les signaux pour éviter les boucles de rappel
        self.nav_button.blockSignals(True)
        self.outline_button.blockSignals(True)
        self.preview_button.blockSignals(True)

        self.nav_button.setChecked(self.navigation_panel.isVisible())
        self.toggle_navigation_action.setChecked(self.navigation_panel.isVisible())

        self.outline_button.setChecked(self.outline_panel.isVisible())
        self.toggle_outline_action.setChecked(self.outline_panel.isVisible())

        self.preview_button.setChecked(self.preview.isVisible())
        self.toggle_preview_action.setChecked(self.preview.isVisible())

        # Rétablir les signaux
        self.nav_button.blockSignals(False)
        self.outline_button.blockSignals(False)
        self.preview_button.blockSignals(False)

    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.file_label = QLabel("Nouveau fichier")
        self._set_file_label_color("gray")
        self.statusbar.addWidget(self.file_label)

        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)

        self.stats_label = QLabel("")
        self.statusbar.addWidget(self.stats_label)

        self.journal_dir_label = QLabel("")
        self.journal_dir_label.setStyleSheet("color: #3498db;")
        self.statusbar.addPermanentWidget(self.journal_dir_label)

        self.tag_index_status_label = QLabel("")
        self.tag_index_status_label.setStyleSheet("color: #3498db;")
        self.statusbar.addPermanentWidget(self.tag_index_status_label)

        # Label pour les messages de sauvegarde, centré et vert
        self.save_status_label = CenteredStatusBarLabel("")
        self.save_status_label.setStyleSheet("color: green; font-weight: bold;")
        self.save_status_label.setVisible(False)
        self.statusbar.addWidget(self.save_status_label, 1)

        self.backup_status_label = CenteredStatusBarLabel(
            self.tr("Sauvegarde en cours...")
        )
        self.backup_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.backup_status_label.setVisible(False)
        self.statusbar.addWidget(self.backup_status_label, 1)

        self.pdf_convert_status_label = CenteredStatusBarLabel(
            self.tr("Conversion PDF en cours...")
        )
        self.pdf_convert_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.pdf_convert_status_label.setVisible(False)
        self.statusbar.addWidget(self.pdf_convert_status_label, 1)

    def setup_connections(self):
        self.pdf_flash_timer = QTimer(self)
        self.pdf_flash_timer.setInterval(500)
        self.pdf_flash_timer.timeout.connect(self._toggle_pdf_status_visibility)

        self.pdf_status_label = CenteredStatusBarLabel(self.tr("Veuillez patienter..."))
        self.pdf_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.pdf_status_label.setVisible(False)
        self.statusbar.addWidget(self.pdf_status_label, 1)

        self.book_search_flash_timer = QTimer(self)
        self.book_search_flash_timer.setInterval(500)
        self.book_search_flash_timer.timeout.connect(
            self._toggle_book_search_status_visibility
        )
        self.book_search_status_label = CenteredStatusBarLabel("Recherche du livre...")
        self.book_search_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.book_search_status_label.setVisible(False)
        self.statusbar.addWidget(self.book_search_status_label, 1)

        self.backup_flash_timer = QTimer(self)
        self.backup_flash_timer.setInterval(500)
        self.backup_flash_timer.timeout.connect(self._toggle_backup_status_visibility)

        self.pdf_convert_flash_timer = QTimer(self)
        self.pdf_convert_flash_timer.setInterval(500)
        self.pdf_convert_flash_timer.timeout.connect(
            self._toggle_pdf_convert_status_visibility
        )

        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.text_edit.verticalScrollBar().valueChanged.connect(
            self.sync_preview_scroll
        )
        self.editor.cursorPositionChanged.connect(
            lambda: self.cursor_sync_timer.start(100)
        )
        self.navigation_panel.prev_day_button_clicked.connect(
            self.on_prev_day_button_clicked
        )
        self.navigation_panel.next_day_button_clicked.connect(
            self.on_next_day_button_clicked
        )
        self.navigation_panel.today_button_clicked.connect(self.on_today_button_clicked)
        self.navigation_panel.date_clicked.connect(self.on_calendar_date_clicked)
        self.outline_panel.item_clicked.connect(self.on_outline_item_clicked)
        self.navigation_panel.tag_search_triggered.connect(self.perform_search)
        self.navigation_panel.file_open_requested.connect(self.open_file_from_search)

    def setup_journal_directory(self):
        """Initialise le répertoire du journal au lancement."""
        journal_path = None

        if self.journal_dir_arg and Path(self.journal_dir_arg).is_dir():
            journal_path = Path(self.journal_dir_arg).resolve()
        elif "JOURNAL_DIRECTORY" in os.environ:
            env_path = Path(os.environ["JOURNAL_DIRECTORY"])
            if env_path.is_dir():
                journal_path = env_path.resolve()
        else:
            default_dir = Path.home() / "bluenotebook"
            if default_dir.is_dir():
                journal_path = default_dir.resolve()
            else:
                try:
                    default_dir.mkdir(parents=True, exist_ok=True)
                    journal_path = default_dir.resolve()
                except OSError as e:
                    QMessageBox.warning(
                        self,
                        "Erreur de Journal",
                        f"Impossible de créer le répertoire de journal par défaut:\n{e}",
                    )
                    journal_path = None

        self.journal_directory = journal_path
        self.update_journal_dir_label()
        if self.journal_directory:
            print(f"📔 Répertoire du journal: {self.journal_directory}")
        else:
            print("⚠️ Répertoire du journal non défini.")

    def update_journal_dir_label(self):
        """Met à jour le label du répertoire de journal dans la barre de statut."""
        if self.journal_directory:
            self.journal_dir_label.setText(f"Journal: {self.journal_directory}")
        else:
            self.journal_dir_label.setText("Journal: Non défini")

    def load_initial_file(self):
        """Charge le fichier journal du jour s'il existe, sinon un nouveau fichier."""
        if self.journal_directory:
            today_str = datetime.now().strftime("%Y%m%d")
            journal_file_path = self.journal_directory / f"{today_str}.md"

            if journal_file_path.exists():
                self.open_specific_file(str(journal_file_path))
                return

        self.new_file()

    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()

        self.update_timer.start(300)
        self.outline_panel.update_outline(self.editor.text_edit.document())

    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        journal_dir_str = (
            str(self.journal_directory) if self.journal_directory else None
        )
        self.preview.update_content(content, journal_dir=journal_dir_str)

    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)

        if self.is_modified:
            self._set_file_label_color("red")
            self.setWindowTitle(f"BlueNotebook V{self.app_version} - {filename} *")
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(f"BlueNotebook V{self.app_version} - {filename}")
            self.modified_label.setText("")

    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)

        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")

    def new_file(self):
        """Créer un nouveau fichier"""
        if not self.check_save_changes():
            return

        # Déterminer si la note du jour existe déjà
        today_note_exists = False
        if self.journal_directory:
            today_str = datetime.now().strftime("%Y%m%d")
            journal_file_path = self.journal_directory / f"{today_str}.md"
            if journal_file_path.exists():
                today_note_exists = True

        # Configurer la boîte de dialogue en fonction de l'existence de la note du jour
        if not today_note_exists:
            # Première note de la journée : proposer un template par défaut
            current_locale = locale.getlocale(locale.LC_TIME)[0]
            if current_locale and current_locale.startswith("fr"):
                default_template = "[Fr]Page_Journal_Standard.md"
            else:
                default_template = "[en-US]default.md"
            dialog = NewFileDialog(
                self,
                use_template_by_default=True,
                default_template_name=default_template,
            )
        else:
            # La note existe déjà : proposer un fichier vierge
            dialog = NewFileDialog(self)

        if dialog.exec_() != QDialog.Accepted:
            return

        choice, template_name = dialog.get_selection()
        content = ""

        try:
            locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
        except locale.Error:
            locale.setlocale(locale.LC_TIME, "")

        today_str = datetime.now().strftime("%A %d %B %Y").title()
        timestamp_str = datetime.now().strftime("%H:%M")

        if choice == "blank":
            content = ""
        elif choice == "template" and template_name:
            try:
                base_path = Path(__file__).parent.parent
                template_path = base_path / "resources" / "templates" / template_name

                if not template_path.exists():
                    raise FileNotFoundError(
                        f"Le fichier template '{template_name}' est introuvable."
                    )

                with open(template_path, "r", encoding="utf-8") as f:
                    template_content = f.read()

                # Remplacer les placeholders
                content = template_content.replace("{{date}}", today_str)
                content = content.replace("{{horodatage}}", timestamp_str)

            except FileNotFoundError as e:
                QMessageBox.warning(self, "Template manquant", str(e))
                content = f"# {today_str}\n\n"

        self.editor.set_text(content)
        self.current_file = None
        self.is_modified = False
        self.update_title()
        self.update_stats()
        self._set_file_label_color("gray")
        self.update_preview()
        self.expand_outline()

    def open_journal(self):
        """Ouvre un dialogue pour sélectionner un nouveau répertoire de journal."""
        dir_name = QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire du Journal"
        )
        if dir_name:
            new_journal_path = Path(dir_name).resolve()
            if new_journal_path.is_dir():
                self.journal_directory = new_journal_path
                self.update_journal_dir_label()
                QMessageBox.information(
                    self,
                    "Journal",
                    f"Le répertoire du journal est maintenant :\n{self.journal_directory}",
                )
                self.start_initial_indexing()
                self.update_calendar_highlights()
                self.update_word_cloud()
                self.update_tag_cloud()

    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)",
            )

            self.open_specific_file(filename)

    def open_specific_file(self, filename):
        """Ouvre un fichier spécifique depuis son chemin."""
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            self.editor.set_text(content)
            self.current_file = filename
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self._set_file_label_color("gray")
            self.update_preview()
            self.expand_outline()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ouvrir le fichier :\n{str(e)}"
            )

    def save_file(self):
        """Sauvegarder le fichier"""
        if not self.journal_directory:
            self.save_file_as()
            return

        file_to_save_path = None
        if self.current_file:
            file_to_save_path = Path(self.current_file)
        else:
            today_str = datetime.now().strftime("%Y%m%d")
            file_to_save_path = self.journal_directory / f"{today_str}.md"

        if not str(file_to_save_path).startswith(str(self.journal_directory)):
            self._save_to_file(str(file_to_save_path))
            return

        journal_file_path = file_to_save_path

        if journal_file_path.exists():
            dialog = QDialog(self)
            dialog.setWindowTitle("Fichier Journal déjà existant")
            layout = QVBoxLayout()
            layout.addWidget(
                QLabel(f"Le fichier journal '{journal_file_path.name}' existe déjà.")
            )

            buttons = QDialogButtonBox()
            replace_button = buttons.addButton(
                "Remplacer", QDialogButtonBox.DestructiveRole
            )
            append_button = buttons.addButton(
                "Ajouter à la fin", QDialogButtonBox.AcceptRole
            )
            cancel_button = buttons.addButton("Annuler", QDialogButtonBox.RejectRole)
            layout.addWidget(buttons)
            dialog.setLayout(layout)

            replace_button.clicked.connect(lambda: dialog.done(1))
            append_button.clicked.connect(lambda: dialog.done(2))
            cancel_button.clicked.connect(dialog.reject)

            result = dialog.exec_()

            if result == 1:
                self._save_to_file(str(journal_file_path))
            elif result == 2:
                self._append_to_file(str(journal_file_path))
            else:
                return
        else:
            self._save_to_file(str(journal_file_path))

        self.current_file = str(journal_file_path)
        self.update_title()

    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)",
        )

        if filename:
            if not filename.endswith((".md", ".markdown", ".txt")):
                filename += ".md"

            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()

    def save_as_template(self):
        """Sauvegarde le contenu actuel comme un nouveau modèle."""
        base_path = Path(__file__).parent.parent
        templates_dir = base_path / "resources" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder comme modèle",
            str(templates_dir),
            "Fichiers Markdown (*.md)",
        )

        if not filename:
            return

        if not filename.endswith(".md"):
            filename += ".md"

        try:
            content = self.editor.get_text()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            self.statusbar.showMessage(
                f"Modèle sauvegardé : {Path(filename).name}", 3000
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de sauvegarder le modèle :\n{str(e)}"
            )

    def insert_template(self):
        """Ouvre une dialogue pour insérer un modèle à la position du curseur."""
        dialog = InsertTemplateDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        template_name = dialog.template_combo.currentText()
        if not template_name:
            return

        try:
            base_path = Path(__file__).parent.parent
            template_path = base_path / "resources" / "templates" / template_name

            if not template_path.exists():
                raise FileNotFoundError(
                    f"Le fichier modèle '{template_name}' est introuvable."
                )

            with open(template_path, "r", encoding="utf-8") as f:
                template_content = f.read()

            # Remplacer les placeholders
            try:
                locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
            except locale.Error:
                locale.setlocale(locale.LC_TIME, "")

            today_str = datetime.now().strftime("%A %d %B %Y").title()
            timestamp_str = datetime.now().strftime("%H:%M")

            content = template_content.replace("{{date}}", today_str)
            content = content.replace("{{horodatage}}", timestamp_str)

            # Insérer le contenu dans l'éditeur
            self.editor.insert_text(content)

        except FileNotFoundError as e:
            QMessageBox.warning(self, "Modèle manquant", str(e))

    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            self.is_modified = False
            self.update_title()
            self._set_file_label_color("green")
            self._show_transient_save_status(f"Fichier sauvegardé : {filename}")
            # Mettre à jour le calendrier pour refléter la nouvelle note
            self.update_calendar_highlights()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )

    def _append_to_file(self, filename):
        """Ajoute le contenu de l'éditeur à la fin d'un fichier."""
        try:
            content = self.editor.get_text()
            with open(filename, "a", encoding="utf-8") as f:
                f.write("\n\n---\n\n" + content)

            self.is_modified = False
            self.update_title()
            self._set_file_label_color("green")
            self._show_transient_save_status(f"Contenu ajouté à : {filename}")
            # Mettre à jour le calendrier pour refléter la nouvelle note
            self.update_calendar_highlights()
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ajouter au fichier :\n{str(e)}"
            )

    def export_html(self):
        """Exporter en HTML"""
        # Construire un nom de fichier par défaut
        if self.current_file:
            base_name = os.path.basename(self.current_file)
            file_stem = os.path.splitext(base_name)[0]
            clean_filename = file_stem.lower().replace(" ", "-")
        else:
            clean_filename = "nouveau-fichier"

        date_str = datetime.now().strftime("%Y_%m_%d")

        # Récupérer le dernier répertoire utilisé pour l'export HTML
        last_html_dir = self.settings_manager.get("html.last_directory")
        if not last_html_dir or not Path(last_html_dir).is_dir():
            last_html_dir = str(Path.home())

        default_filename = f"BlueNotebook-{clean_filename}-{date_str}.html"
        default_path = os.path.join(last_html_dir, default_filename)

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            default_path,
            "Fichiers HTML (*.html);;Tous les fichiers (*)",
        )

        if filename:
            if not filename.endswith(".html"):
                filename += ".html"

            try:
                html_content = self.preview.get_html()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html_content)

                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)

                # Mémoriser le répertoire de destination pour la prochaine fois
                new_html_dir = str(Path(filename).parent)
                self.settings_manager.set("html.last_directory", new_html_dir)
                self.settings_manager.save_settings()

            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur", f"Impossible d'exporter en HTML :\n{str(e)}"
                )

    def export_journal_pdf(self):
        """Exporte l'ensemble du journal dans un unique fichier PDF avec WeasyPrint."""
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            QMessageBox.critical(
                self,
                "Module manquant",
                "WeasyPrint n'est pas installé.\n\n"
                "Pour utiliser cette fonctionnalité, installez-le avec:\n"
                "pip install weasyprint",
            )
            return

        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Exportation impossible",
                "Aucun répertoire de journal n'est actuellement défini.",
            )
            return

        # V2.9.2 - Charger les tags disponibles pour le filtre
        available_tags = []
        tags_index_path = self.journal_directory / "index_tags.json"
        if tags_index_path.exists():
            try:
                with open(tags_index_path, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                    # On trie les tags par ordre alphabétique pour la liste déroulante
                    available_tags = sorted(tags_data.keys())
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Erreur de lecture de l'index des tags : {e}")

        # Récupérer et trier toutes les notes du journal
        note_files = []
        for filename in os.listdir(self.journal_directory):
            if filename.endswith(".md") and re.match(r"^\d{8}\.md$", filename):
                note_files.append(filename)

        if not note_files:
            QMessageBox.information(
                self, "Journal vide", "Aucune note à exporter dans le journal."
            )
            return

        note_files.sort()

        # Récupérer la dernière destination PDF enregistrée
        last_pdf_dir = self.settings_manager.get("pdf.last_directory")
        if not last_pdf_dir or not Path(last_pdf_dir).is_dir():
            last_pdf_dir = str(self.journal_directory.parent)

        # Déterminer les dates min/max pour la boîte de dialogue
        first_note_date_str = os.path.splitext(note_files[0])[0]
        first_note_date_obj = datetime.strptime(first_note_date_str, "%Y%m%d")
        min_date_q = QDate(
            first_note_date_obj.year,
            first_note_date_obj.month,
            first_note_date_obj.day,
        )
        today_q = QDate.currentDate()

        # Récupérer le dernier nom d'auteur utilisé
        last_author = self.settings_manager.get("pdf.last_author", "")

        # Récupérer le dernier titre utilisé, avec "BlueNotebook Journal" comme valeur par défaut
        last_title = self.settings_manager.get("pdf.last_title", "BlueNotebook Journal")

        # Définir l'image de couverture par défaut
        default_logo_path = (
            Path(__file__).parent.parent
            / "resources"
            / "images"
            / "bluenotebook_256-x256_fond_blanc.png"
        )
        # Afficher la boîte de dialogue de sélection de dates
        date_dialog = DateRangeDialog(
            start_date_default=min_date_q,
            end_date_default=today_q,
            min_date=min_date_q,
            max_date=today_q,
            available_tags=available_tags,
            default_title=last_title,
            default_cover_image=str(default_logo_path),
            default_author=last_author,
            parent=self,
        )

        if date_dialog.exec_() != QDialog.Accepted:
            return  # L'utilisateur a annulé

        options = date_dialog.get_export_options()
        start_date_q = options["start_date"]
        end_date_q = options["end_date"]
        pdf_title = options["title"]
        pdf_author = options["author"]
        cover_image_path = options["cover_image"]
        selected_tag = options.get("selected_tag")

        # Proposer un nom de fichier par défaut
        default_filename = f"Journal-{start_date_q.toString('ddMMyyyy')}-{end_date_q.toString('ddMMyyyy')}.pdf"
        default_path = os.path.join(last_pdf_dir, default_filename)

        # Demander à l'utilisateur où sauvegarder le PDF
        pdf_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter le journal en PDF",
            default_path,
            "Fichiers PDF (*.pdf)",
        )

        if not pdf_path:
            return

        # V2.9.2 - Logique de filtrage combiné (dates et tag)
        # 1. Filtrer par date
        filtered_notes = []
        for note_file in note_files:
            note_date_str = os.path.splitext(note_file)[0]
            note_date_obj = datetime.strptime(note_date_str, "%Y%m%d").date()
            if start_date_q.toPyDate() <= note_date_obj <= end_date_q.toPyDate():
                filtered_notes.append(note_file)

        # 2. Si un tag est sélectionné, filtrer davantage
        if selected_tag:
            try:
                with open(tags_index_path, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                # Obtenir la liste des noms de fichiers contenant le tag
                files_with_tag = {
                    d["filename"] for d in tags_data[selected_tag]["details"]
                }
                # Conserver uniquement les notes qui sont dans la plage de dates ET qui ont le tag
                filtered_notes = [
                    note for note in filtered_notes if note in files_with_tag
                ]
            except (KeyError, FileNotFoundError) as e:
                print(f"⚠️ Erreur lors du filtrage par tag : {e}")
                filtered_notes = []

        if not filtered_notes:
            QMessageBox.information(
                self,
                "Aucune note",
                "Aucune note trouvée dans la plage de dates sélectionnée.",
            )
            return

        all_html_content = ""

        # Page de garde
        notes_data = []
        for note_file in filtered_notes:
            try:
                with open(
                    self.journal_directory / note_file, "r", encoding="utf-8"
                ) as f:
                    markdown_content = f.read()
                self.preview.md.reset()
                html_note = self.preview.md.convert(markdown_content)
                date_obj = datetime.strptime(os.path.splitext(note_file)[0], "%Y%m%d")
                notes_data.append((date_obj, html_note))
            except Exception as e:
                print(f"Erreur de lecture du fichier {note_file}: {e}")
                continue

        # Générer le PDF avec WeasyPrint
        try:
            self._start_export_flashing()

            # V2.9.1 - Charger le thème CSS pour le contenu du PDF
            pdf_theme_filename = self.settings_manager.get(
                "pdf.css_theme", "default_preview.css"
            )
            # Le thème peut être dans css_pdf ou css_preview
            base_path = Path(__file__).parent.parent
            css_pdf_path = base_path / "resources" / "css_pdf" / pdf_theme_filename
            css_preview_path = (
                base_path / "resources" / "css_preview" / pdf_theme_filename
            )

            content_css_string = ""
            css_path_to_load = (
                css_pdf_path if css_pdf_path.exists() else css_preview_path
            )
            if css_path_to_load.exists():
                with open(css_path_to_load, "r", encoding="utf-8") as f:
                    content_css_string = f.read()

            worker = create_pdf_export_worker(
                options=options,
                notes_data=notes_data,
                content_css_string=content_css_string,
                journal_dir=self.journal_directory,
                output_path=pdf_path,
            )
            worker.signals.finished.connect(self._on_export_finished)
            worker.signals.error.connect(self._on_export_error)

            self.thread_pool.start(worker)

            # Mémoriser le répertoire de destination pour la prochaine fois
            self.settings_manager.set("pdf.last_directory", str(Path(pdf_path).parent))
            # Mémoriser le nom de l'auteur pour la prochaine fois
            if pdf_author:
                self.settings_manager.set("pdf.last_author", pdf_author)
            # Mémoriser le titre pour la prochaine fois (toujours, même s'il est vide)
            self.settings_manager.set("pdf.last_title", pdf_title)
            self.settings_manager.save_settings()

        except Exception as e:
            self._stop_export_flashing()
            QMessageBox.critical(
                self,
                "Erreur d'exportation",
                f"Une erreur est survenue lors de la création du PDF :\n{str(e)}",
            )

    def _on_export_finished(self, file_path):
        """Callback générique pour la fin d'un export."""
        self._stop_export_flashing()
        file_type = Path(file_path).suffix.upper()[1:]
        QMessageBox.information(
            self,
            "Exportation terminée",
            f"Le journal a été exporté avec succès au format {file_type} dans :\n{file_path}",
        )

    def _on_export_error(self, error_message):
        """Callback générique en cas d'erreur d'export."""
        self._stop_export_flashing()
        QMessageBox.critical(
            self,
            "Erreur d'exportation",
            f"Une erreur est survenue lors de la création du fichier :\n{error_message}",
        )

    def export_journal_epub(self):
        """Exporte l'ensemble du journal dans un unique fichier EPUB."""
        try:
            from ebooklib import epub
            from PIL import Image
        except ImportError:
            QMessageBox.critical(
                self,
                "Modules manquants",
                "Les bibliothèques 'EbookLib' et 'Pillow' sont requises.\n\n"
                "Pour utiliser cette fonctionnalité, installez-les avec:\n"
                "pip install EbookLib Pillow",
            )
            return

        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Exportation impossible",
                "Aucun répertoire de journal n'est actuellement défini.",
            )
            return

        # Récupérer et trier toutes les notes du journal
        note_files = sorted(
            [
                f
                for f in os.listdir(self.journal_directory)
                if f.endswith(".md") and re.match(r"^\d{8}\.md$", f)
            ]
        )

        if not note_files:
            QMessageBox.information(
                self, "Journal vide", "Aucune note à exporter dans le journal."
            )
            return

        # Déterminer les dates min/max pour la boîte de dialogue
        min_date_obj = datetime.strptime(os.path.splitext(note_files[0])[0], "%Y%m%d")
        min_date_q = QDate(min_date_obj.year, min_date_obj.month, min_date_obj.day)
        today_q = QDate.currentDate()

        # Récupérer les derniers paramètres utilisés
        last_author = self.settings_manager.get("epub.last_author", "")
        last_title = self.settings_manager.get(
            "epub.last_title", "BlueNotebook Journal"
        )
        default_logo_path = (
            Path(__file__).parent.parent
            / "resources"
            / "images"
            / "bluenotebook_256-x256_fond_blanc.png"
        )

        # Afficher la boîte de dialogue de sélection (identique à celle du PDF)
        date_dialog = DateRangeDialog(
            start_date_default=min_date_q,
            end_date_default=today_q,
            min_date=min_date_q,
            max_date=today_q,
            default_title=last_title,
            default_cover_image=str(default_logo_path),
            default_author=last_author,
            parent=self,
        )
        date_dialog.setWindowTitle("Options d'exportation du Journal EPUB")

        if date_dialog.exec_() != QDialog.Accepted:
            return

        options = date_dialog.get_export_options()

        # Demander où sauvegarder le fichier EPUB
        last_epub_dir = self.settings_manager.get("epub.last_directory")
        if not last_epub_dir or not Path(last_epub_dir).is_dir():
            last_epub_dir = str(self.journal_directory.parent)

        default_filename = f"Journal-{options['start_date'].toString('ddMMyyyy')}-{options['end_date'].toString('ddMMyyyy')}.epub"
        default_path = os.path.join(last_epub_dir, default_filename)

        epub_path, _ = QFileDialog.getSaveFileName(
            self, "Exporter le journal en EPUB", default_path, "Fichiers EPUB (*.epub)"
        )

        if not epub_path:
            return

        # Filtrer les notes et préparer les données
        notes_data = []
        for note_file in note_files:
            note_date_str = os.path.splitext(note_file)[0]
            note_date_obj = datetime.strptime(note_date_str, "%Y%m%d").date()
            if (
                options["start_date"].toPyDate()
                <= note_date_obj
                <= options["end_date"].toPyDate()
            ):
                with open(
                    self.journal_directory / note_file, "r", encoding="utf-8"
                ) as f:
                    markdown_content = f.read()
                self.preview.md.reset()
                html_note = self.preview.md.convert(markdown_content)
                notes_data.append((note_date_obj, html_note))

        # Lancer le worker en arrière-plan
        self._start_export_flashing()
        worker = EpubExportWorker(
            options, notes_data, epub_path, self.journal_directory
        )
        worker.signals.finished.connect(self._on_export_finished)
        worker.signals.error.connect(self._on_export_error)
        self.thread_pool.start(worker)

        # Mémoriser les paramètres pour la prochaine fois
        self.settings_manager.set("epub.last_directory", str(Path(epub_path).parent))
        self.settings_manager.set("epub.last_author", options["author"])
        self.settings_manager.set("epub.last_title", options["title"])
        self.settings_manager.save_settings()

    def backup_journal(self):
        """Sauvegarde le répertoire du journal dans une archive ZIP."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Sauvegarde impossible",
                "Aucun répertoire de journal n'est actuellement défini.",
            )
            return

        initial_dir = os.getenv("BACKUP_DIRECTORY")
        if not initial_dir or not os.path.isdir(initial_dir):
            initial_dir = self.settings_manager.get("backup.last_directory")
            if not initial_dir or not os.path.isdir(initial_dir):
                initial_dir = str(self.journal_directory.parent)

        backup_filename_default = f"BlueNotebook-Backup-{self.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"
        default_path = os.path.join(initial_dir, backup_filename_default)

        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le journal",
            default_path,
            "Archives ZIP (*.zip)",
            options=QFileDialog.DontConfirmOverwrite,
        )

        if backup_path:
            # Démarrer le worker de sauvegarde en arrière-plan
            self._start_backup_flashing()
            worker = JournalBackupWorker(self.journal_directory, Path(backup_path))
            worker.signals.finished.connect(self._on_journal_backup_finished)
            worker.signals.error.connect(self._on_journal_backup_error)
            self.thread_pool.start(worker)

            # Mémoriser le répertoire de destination
            new_backup_dir = os.path.dirname(backup_path)
            self.settings_manager.set("backup.last_directory", new_backup_dir)
            self.settings_manager.save_settings()

            # Afficher un message immédiat (le message de fin viendra du worker)
            self.statusbar.showMessage("Lancement de la sauvegarde...", 3000)

    def restore_journal(self):
        """Restaure un journal depuis une archive ZIP."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Restauration impossible",
                "Aucun répertoire de journal de destination n'est défini.",
            )
            return

        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Restaurer le journal", "", "Archives ZIP (*.zip)"
        )

        if not zip_path:
            return

        current_journal_backup_path = (
            f"{self.journal_directory}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation de la restauration")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(
            f"<p>Vous êtes sur le point de restaurer le journal depuis '{os.path.basename(zip_path)}'.</p>"
            f"<p>Le journal actuel sera d'abord sauvegardé ici :<br><b>{current_journal_backup_path}</b></p>"
            f"<p>L'application va devoir être redémarrée après la restauration. Continuer ?</p>"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Valider")
        msg_box.button(QMessageBox.No).setText("Annuler")
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            os.rename(self.journal_directory, current_journal_backup_path)
            os.makedirs(self.journal_directory)

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.journal_directory)

            QMessageBox.information(
                self,
                "Restauration terminée",
                "La restauration est terminée. L'application va maintenant se fermer.\n"
                "Veuillez la relancer pour utiliser le journal restauré.",
            )
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur de restauration", f"La restauration a échoué : {e}"
            )

    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()
        self._sync_panel_controls()

    def toggle_navigation(self):
        """Basculer la visibilité du panneau de navigation."""
        if self.navigation_panel.isVisible():
            self.navigation_panel.hide()
        else:
            self.navigation_panel.show()
        self._sync_panel_controls()

    def toggle_outline(self):
        """Basculer la visibilité du panneau de plan."""
        if self.outline_panel.isVisible():
            self.outline_panel.hide()
        else:
            self.outline_panel.show()
        self._sync_panel_controls()

    def show_online_help(self):
        """Affiche la page d'aide HTML dans le navigateur par défaut."""
        base_path = os.path.dirname(os.path.abspath(__file__))
        help_file_path = os.path.join(
            base_path, "..", "resources", "html", "aide_en_ligne.html"
        )

        if os.path.exists(help_file_path):
            url = f"file:///{os.path.abspath(help_file_path)}"
            webbrowser.open(url)
        else:
            QMessageBox.warning(
                self,
                "Aide non trouvée",
                f"Le fichier d'aide n'a pas été trouvé:\n{help_file_path}",
            )

    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            f"""<h2>BlueNotebook V{self.app_version}</h2>
            <p><b>Éditeur de journal Markdown </b></p> 
            <p>Basé sur un éditeur de texte Markdown avec aperçu HTML en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p>Très inspiré du logiciel <a href="https://github.com/jendrikseipp/rednotebook">RedNotebook</a>  développé par Jendrik Seipp</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Gestion d'un journal Personnel</li>
            <li>Navigation simple dans les notes du journal</li>
            <li>Sauvegarde/Restauration</li>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML des pages du journal</li>
            <li>Export PDF du journal complet ou partiel</li>
            <li>Gestion de Templates</li>
            <li>Gestion de tags / Recherche par tags/mots-clés</li>
            <li>Insertion Cartes OpenStreetMap, Trace GPX, Videos Youtube et Météo</li>
            </ul>
            <p>Dépôt GitHub : <a href="https://github.com/lephotographelibre/BlueNotebook">BlueNotebook</a></p>
            <p>Licence : <a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPLv3</a></p>
            <p>© 2025 BlueNotebook by Jean-Marc DIGNE</p>""",
        )

    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Modifications non sauvegardées")
            msg_box.setText(
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?"
            )
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            msg_box.button(QMessageBox.Save).setText("Sauvegarder")
            msg_box.button(QMessageBox.Discard).setText("Ne pas sauvegarder")
            msg_box.button(QMessageBox.Cancel).setText("Annuler")
            msg_box.setDefaultButton(QMessageBox.Save)

            reply = msg_box.exec_()
            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified
            elif reply == QMessageBox.Cancel:
                return False

        return True

    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            self.save_panel_visibility_settings()
            event.accept()
        else:
            event.ignore()

    def show_quote_of_the_day(self):
        """Affiche la citation du jour dans une boîte de dialogue."""
        if self.settings_manager.get("integrations.show_quote_of_the_day"):
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()
            if self.daily_quote and self.daily_author:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Citation du Jour")
                msg_box.setText(
                    f"<blockquote><i>« {self.daily_quote} »</i></blockquote>"
                )
                msg_box.setInformativeText(f"<b>{self.daily_author}</b>")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()

    def insert_quote_of_the_day(self):
        """Insère la citation du jour dans l'éditeur, en la récupérant si nécessaire."""
        if not self.daily_quote:
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()

        if self.daily_quote and self.daily_author:
            self.editor.format_text("quote_of_the_day")
        else:
            QMessageBox.warning(
                self, "Erreur", "Impossible de récupérer la citation du jour."
            )

    def insert_youtube_video(self):
        """Gère la logique d'insertion d'une vidéo YouTube."""
        cursor = self.editor.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        video_url = ""
        if selected_text:
            video_url = selected_text
        else:
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Vidéo ou Playlist YouTube")
            dialog.setLabelText("Entrez l'URL de la vidéo ou playlist Youtube:")
            dialog.setTextEchoMode(QLineEdit.Normal)
            # Augmenter la largeur pour les longues URL
            dialog.setMinimumWidth(600)
            ok = dialog.exec_()
            url = ""
            if ok:
                url = dialog.textValue()

            if ok and url:
                video_url = url.strip()

        if not video_url:
            return

        result = get_youtube_video_details(video_url)

        if isinstance(result, str):  # C'est une chaîne d'erreur
            QMessageBox.warning(
                self,
                "Erreur d'intégration YouTube",
                result,
            )
        else:  # C'est un dictionnaire de détails
            markdown_block = generate_youtube_markdown_block(result)
            self.editor.insert_text(f"\n{markdown_block}\n")

    def insert_gps_map(self):
        """Gère la logique d'insertion d'une carte GPS."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Journal non défini",
                "Veuillez définir un répertoire de journal avant d'insérer une carte.",
            )
            return

        lat, lon = None, None
        selected_text = self.editor.text_edit.textCursor().selectedText().strip()
        if (
            selected_text
            and selected_text.startswith("[")
            and selected_text.endswith("]")
        ):
            try:
                coords = json.loads(selected_text)
                if isinstance(coords, list) and len(coords) == 2:
                    lat, lon = float(coords[0]), float(coords[1])
            except (json.JSONDecodeError, ValueError, TypeError):
                pass  # Si le parsing échoue, on ouvre la boîte de dialogue

        if lat is None:
            gps_dialog = GpsInputDialog(self)
            if gps_dialog.exec_() == QDialog.Accepted:
                lat, lon = gps_dialog.get_coordinates()

        if lat is None or lon is None:
            return

        width, ok = QInputDialog.getInt(
            self,
            "Taille de la carte",
            "Largeur de l'image (en pixels):",
            800,
            200,
            2000,
            50,
        )
        if not ok:
            return

        markdown_block, message = generate_gps_map_markdown(
            lat, lon, width, self.journal_directory
        )

        if markdown_block:
            self.editor.insert_text(f"\n{markdown_block}\n")
            self.statusbar.showMessage(message, 5000)
        else:
            QMessageBox.critical(self, "Erreur de création de carte", message)

    def insert_gpx_trace(self):
        """Gère la logique d'insertion d'une carte à partir d'une trace GPX."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Journal non défini",
                "Veuillez définir un répertoire de journal avant d'insérer une trace GPX.",
            )
            return

        # Utiliser la nouvelle boîte de dialogue
        dialog = GpxSourceDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        gpx_input = dialog.get_path()
        if not gpx_input:
            return

        width, ok = QInputDialog.getInt(
            self,
            "Taille de la carte",
            "Largeur de l'image (en pixels):",
            800,
            200,
            2000,
            50,
        )
        if not ok:
            return

        # Récupérer le contenu du GPX
        gpx_content = get_gpx_data(gpx_input)
        if not gpx_content:
            QMessageBox.warning(
                self,
                "Fichier GPX introuvable",
                f"Impossible de lire le fichier GPX depuis :\n{gpx_input}",
            )
            return

        # Chemin vers l'icône de départ
        base_path = Path(__file__).parent.parent
        start_icon_path = base_path / "resources" / "icons" / "start.png"

        # Appeler le générateur
        markdown_block, message = create_gpx_trace_map(
            gpx_content, self.journal_directory, width, str(start_icon_path)
        )

        if markdown_block:
            self.editor.insert_text(f"\n{markdown_block}\n")
            self.statusbar.showMessage(message, 5000)
        else:
            # 'message' contient l'erreur dans ce cas
            QMessageBox.critical(self, "Erreur de création de la trace", message)

    def insert_html_image(self):
        """Gère la logique d'insertion d'une image HTML avec gestion EXIF."""
        image_path, is_local = self.editor.get_image_path_from_user()
        if not image_path:
            return

        width, ok = QInputDialog.getInt(
            self, "Taille de l'image", "Largeur maximale en pixels:", 400, 100, 2000, 50
        )
        if not ok:
            return

        # V2.6.4 - L'image est maintenant cliquable pour l'agrandir
        img_tag = (
            f'<a href="{image_path}" target="_blank">'
            f'<img src="{image_path}" width="{width}" alt="Image">'
            f"</a>"
        )
        exif_caption = None

        if is_local and self.journal_directory:
            full_image_path = self.journal_directory / image_path
            exif_caption = format_exif_as_markdown(str(full_image_path))

        if exif_caption:
            reply = QMessageBox.question(
                self,
                "Données EXIF trouvées",
                "Des données EXIF ont été trouvées dans l'image. "
                "Voulez-vous les insérer sous l'image ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.Yes:
                figure_html = f'\n<figure style="text-align: center;">\n    {img_tag}\n    {exif_caption}\n</figure>\n'
                self.editor.insert_text(figure_html)
            else:
                self.editor.insert_text(img_tag)
        else:
            self.editor.insert_text(img_tag)

    def insert_weather(self):
        """Récupère et insère la météo actuelle dans l'éditeur."""
        city = self.settings_manager.get("integrations.weather.city")
        api_key = self.settings_manager.get("integrations.weather.api_key")

        markdown_fragment, error_message = get_weather_markdown(city, api_key)

        if error_message:
            QMessageBox.warning(
                self,
                "Erreur Météo",
                error_message,
            )
            return

        if markdown_fragment:
            self.editor.insert_text(markdown_fragment)
            self.statusbar.showMessage("Météo insérée avec succès.", 3000)

    def insert_amazon_book(self):
        """Récupère et insère les informations d'un livre depuis Amazon via ISBN."""
        has_selection = False
        cursor = self.editor.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        isbn = ""
        if selected_text:
            isbn = selected_text
        else:
            has_selection = True
            text, ok = QInputDialog.getText(
                self, "Recherche de livre par ISBN", "Entrez le code ISBN du livre:"
            )
            if ok and text:
                isbn = text.strip()

        if not isbn:
            return

        # Afficher un message d'attente
        self._start_book_search_flashing()
        worker = self._create_book_worker(isbn, has_selection)
        worker.signals.finished.connect(self.on_book_search_finished)
        worker.signals.error.connect(self.on_book_search_error)
        self.thread_pool.start(worker)

    def insert_sun_moon_data(self):
        """Récupère et insère les données astro du jour."""
        city = self.settings_manager.get("integrations.sun_moon.city")
        latitude = self.settings_manager.get("integrations.sun_moon.latitude")
        longitude = self.settings_manager.get("integrations.sun_moon.longitude")

        if not all([city, latitude, longitude]):
            QMessageBox.warning(
                self,
                "Configuration requise",
                "Veuillez configurer votre ville dans 'Préférences > Intégrations' "
                "pour utiliser cette fonctionnalité.",
            )
            return

        # Afficher un message d'attente
        self.statusbar.showMessage("Récupération des données astronomiques...", 0)

        worker = SunMoonWorker(city, latitude, longitude)
        worker.signals.finished.connect(self.on_sun_moon_finished)
        worker.signals.error.connect(self.on_sun_moon_error)
        self.thread_pool.start(worker)

    def on_sun_moon_finished(self, html_fragment):
        """Insère le fragment Markdown des données astro."""
        self.statusbar.clearMessage()
        self.editor.insert_text(f"\n{html_fragment}\n")
        self.statusbar.showMessage("Données astronomiques insérées.", 3000)

    def on_sun_moon_error(self, error_message):
        """Affiche une erreur si la recherche astro a échoué."""
        self.statusbar.clearMessage()
        QMessageBox.critical(self, "Erreur Astro", error_message)

    def _create_book_worker(self, isbn, has_selection):
        """Crée et retourne un worker pour la recherche de livre."""
        return BookWorker(isbn, has_selection)

    def on_book_search_finished(self, markdown_fragment, has_selection):
        """Insère le fragment Markdown du livre dans l'éditeur."""
        self._stop_book_search_flashing()
        if has_selection:
            self.editor.text_edit.textCursor().removeSelectedText()
        self.editor.insert_text(f"\n{markdown_fragment}\n")
        self.statusbar.showMessage("Informations du livre insérées avec succès.", 5000)

    def on_book_search_error(self, error_message):
        """Affiche une erreur si la recherche de livre a échoué."""
        self._stop_book_search_flashing()
        self.statusbar.clearMessage()
        QMessageBox.critical(self, "Erreur de recherche", error_message)

    def _start_book_search_flashing(self):
        """Démarre le message clignotant pour la recherche de livre."""
        self.book_search_status_label.setVisible(True)
        self.book_search_flash_timer.start()

    def _stop_book_search_flashing(self):
        """Arrête le message clignotant de recherche de livre."""
        self.book_search_flash_timer.stop()
        self.book_search_status_label.setVisible(False)

    def _toggle_book_search_status_visibility(self):
        """Bascule la visibilité du label de statut de recherche de livre."""
        self.book_search_status_label.setVisible(
            not self.book_search_status_label.isVisible()
        )

    def _start_backup_flashing(self):
        """Démarre le message clignotant pour la sauvegarde."""
        self.backup_status_label.setVisible(True)
        self.backup_flash_timer.start()

    def _stop_backup_flashing(self):
        """Arrête le message clignotant de sauvegarde."""
        self.backup_flash_timer.stop()
        self.backup_status_label.setVisible(False)

    def _start_pdf_convert_flashing(self):
        """Démarre le message clignotant pour la conversion PDF."""
        self.pdf_convert_status_label.setVisible(True)
        self.pdf_convert_flash_timer.start()

    def _stop_pdf_convert_flashing(self):
        """Arrête le message clignotant de conversion PDF."""
        self.pdf_convert_flash_timer.stop()
        self.pdf_convert_status_label.setVisible(False)

    def _toggle_pdf_convert_status_visibility(self):
        """Bascule la visibilité du label de statut de conversion PDF."""
        self.pdf_convert_status_label.setVisible(
            not self.pdf_convert_status_label.isVisible()
        )

    def on_pdf_convert_finished(self, markdown_content):
        """Callback pour la fin de la conversion PDF."""
        self._stop_pdf_convert_flashing()
        self.editor.set_text(markdown_content)
        self.current_file = None
        self.is_modified = True
        self.update_title()
        self.update_stats()
        self._set_file_label_color("red")
        self.update_preview()
        self.expand_outline()
        QMessageBox.information(
            self, "Conversion terminée", "Le fichier PDF a été converti avec succès."
        )

    def on_pdf_convert_error(self, error_message):
        """Callback en cas d'erreur de conversion PDF."""
        self._stop_pdf_convert_flashing()
        QMessageBox.critical(self, "Erreur de conversion", error_message)

    def _toggle_backup_status_visibility(self):
        """Bascule la visibilité du label de statut de sauvegarde."""
        self.backup_status_label.setVisible(not self.backup_status_label.isVisible())

    def _on_journal_backup_finished(self, backup_path: str):
        """Slot appelé lorsque la sauvegarde du journal est terminée avec succès."""
        self._stop_backup_flashing()
        QMessageBox.information(
            self,
            "Sauvegarde terminée",
            f"Le journal a été sauvegardé avec succès dans :\n{backup_path}",
        )

    def _on_journal_backup_error(self, error_message: str):
        """Slot appelé en cas d'erreur lors de la sauvegarde du journal."""
        self._stop_backup_flashing()
        QMessageBox.critical(self, "Erreur de sauvegarde", error_message)

    def convert_pdf_to_markdown(self):
        """Gère la conversion d'un PDF en Markdown."""
        if not self.check_save_changes():
            return

        dialog = PdfSourceDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        pdf_path = dialog.get_path()
        if not pdf_path:
            return

        self._start_pdf_convert_flashing()

        worker = PdfToMarkdownWorker(pdf_path)
        worker.signals.finished.connect(self.on_pdf_convert_finished)
        worker.signals.error.connect(self.on_pdf_convert_error)

        self.thread_pool.start(worker)

    def sync_preview_scroll(self, value):
        """Synchronise le défilement de l'aperçu avec celui de l'éditeur."""
        editor_scrollbar = self.editor.text_edit.verticalScrollBar()
        preview_page = self.preview.web_view.page()

        scroll_max = editor_scrollbar.maximum()
        if scroll_max == 0:
            relative_pos = 0.0
        else:
            relative_pos = value / scroll_max

        js_code = f"window.scrollTo(0, document.body.scrollHeight * {relative_pos});"
        preview_page.runJavaScript(js_code)

    def sync_preview_to_cursor(self):
        """Synchronise la vue de l'aperçu sur la position actuelle du curseur."""
        cursor = self.editor.text_edit.textCursor()
        block = cursor.block()
        if not block.isValid():
            return

        total_blocks = self.editor.text_edit.document().blockCount()
        if total_blocks == 0:
            return

        relative_pos = block.blockNumber() / total_blocks
        self.preview.scroll_to_percentage(relative_pos)

    def start_initial_indexing(self):
        """Lance l'indexation des tags pour le répertoire de journal actuel."""
        from core.tag_indexer import start_tag_indexing

        start_tag_indexing(
            self.journal_directory, self.thread_pool, self.on_indexing_finished
        )

        user_excluded = self.settings_manager.get("indexing.user_excluded_words", [])
        excluded_words_set = set(DEFAULT_EXCLUDED_WORDS) | set(user_excluded)
        start_word_indexing(
            self.journal_directory,
            excluded_words_set,
            self.thread_pool,
            self.on_word_indexing_finished,
        )

    def on_indexing_finished(self, unique_tag_count):
        """Callback exécuté à la fin de l'indexation."""
        self.tag_index_count = unique_tag_count
        self.update_indexing_status_label()

    def on_word_indexing_finished(self, unique_word_count):
        """Callback exécuté à la fin de l'indexation des mots."""
        self.word_index_count = unique_word_count
        self.update_indexing_status_label()

    def update_indexing_status_label(self):
        """Met à jour la barre de statut avec les résultats des deux indexations."""
        if self.tag_index_count == -1 or self.word_index_count == -1:
            return

        tag_msg = "Erreur tags"
        if self.tag_index_count >= 0:
            tag_msg = f"{self.tag_index_count} tags"

        word_msg = "Erreur mots"
        if self.word_index_count >= 0:
            word_msg = f"{self.word_index_count} mots"

        full_message = f"Index: {tag_msg} | {word_msg}"
        print(f"✅ {full_message}")
        self.tag_index_status_label.setText(full_message)

        if not self.settings_manager.get("ui.show_indexing_stats", True):
            QTimer.singleShot(15000, lambda: self.tag_index_status_label.clear())

        self.update_tag_cloud()
        self.update_word_cloud()
        self.update_navigation_panel_data()

    def on_prev_day_button_clicked(self):
        """Trouve la note existante la plus proche avant la date actuelle et l'ouvre."""
        if not self.journal_directory:
            return

        start_date = QDate.currentDate()
        if self.current_file:
            try:
                filename = Path(self.current_file).stem
                current_date_obj = datetime.strptime(filename, "%Y%m%d").date()
                start_date = QDate(
                    current_date_obj.year,
                    current_date_obj.month,
                    current_date_obj.day,
                )
            except ValueError:
                pass

        current_check_date = start_date.addDays(-1)
        for _ in range(365 * 5):
            filename = current_check_date.toString("yyyyMMdd") + ".md"
            file_path = self.journal_directory / filename

            if file_path.exists():
                self.navigation_panel.calendar.setSelectedDate(current_check_date)
                self.on_calendar_date_clicked(current_check_date)
                return

            current_check_date = current_check_date.addDays(-1)

        self.statusbar.showMessage(
            "Aucune note précédente trouvée dans le journal.", 3000
        )

    def on_next_day_button_clicked(self):
        """Trouve la note existante la plus proche après la date actuelle et l'ouvre."""
        if not self.journal_directory:
            return

        start_date = QDate.currentDate()
        if self.current_file:
            try:
                filename = Path(self.current_file).stem
                current_date_obj = datetime.strptime(filename, "%Y%m%d").date()
                start_date = QDate(
                    current_date_obj.year,
                    current_date_obj.month,
                    current_date_obj.day,
                )
            except ValueError:
                pass

        current_check_date = start_date.addDays(1)
        for _ in range(365 * 5):
            filename = current_check_date.toString("yyyyMMdd") + ".md"
            file_path = self.journal_directory / filename

            if file_path.exists():
                self.navigation_panel.calendar.setSelectedDate(current_check_date)
                self.on_calendar_date_clicked(current_check_date)
                return

            current_check_date = current_check_date.addDays(1)

        self.statusbar.showMessage(
            "Aucune note suivante trouvée dans le journal.", 3000
        )

    def on_today_button_clicked(self):
        """Sélectionne la date du jour et ouvre la note correspondante."""
        today = QDate.currentDate()
        self.navigation_panel.calendar.setSelectedDate(today)
        self.on_calendar_date_clicked(today)

    def on_calendar_date_clicked(self, date):
        """Ouvre le fichier journal correspondant à la date cliquée."""
        if not self.journal_directory:
            return

        filename = date.toString("yyyyMMdd") + ".md"
        file_path = self.journal_directory / filename

        if file_path.exists():
            if self.check_save_changes():
                self.open_specific_file(str(file_path))
        else:
            self.statusbar.showMessage(
                f"Aucune note pour le {date.toString('dd/MM/yyyy')}", 3000
            )

    def on_outline_item_clicked(self, position):
        """Déplace le curseur vers la position cliquée dans le plan."""
        from PyQt5.QtGui import QTextCursor

        block = self.editor.text_edit.document().findBlock(position)
        cursor = self.editor.text_edit.textCursor()
        cursor.setPosition(block.position())
        self.editor.text_edit.setTextCursor(cursor)

        scrollbar = self.editor.text_edit.verticalScrollBar()
        text_edit = self.editor.text_edit

        text_edit.ensureCursorVisible()

        for attempt in range(3):
            cursor_rect = text_edit.cursorRect()

            if cursor_rect.top() <= 20:
                break

            scroll_adjustment = cursor_rect.top() - 10
            current_scroll = scrollbar.value()
            new_scroll = current_scroll + scroll_adjustment
            new_scroll = max(0, min(new_scroll, scrollbar.maximum()))

            scrollbar.setValue(new_scroll)

            from PyQt5.QtWidgets import QApplication

            QApplication.processEvents()

        text_edit.setFocus()

    def update_calendar_highlights(self):
        """Scanne le répertoire du journal et met en évidence les dates dans le calendrier."""
        if not self.journal_directory:
            return

        dates_with_notes = set()
        try:
            for filename in os.listdir(self.journal_directory):
                if filename.endswith(".md"):
                    try:
                        date_str = os.path.splitext(filename)[0]
                        date = datetime.strptime(date_str, "%Y%m%d").date()
                        dates_with_notes.add(QDate(date.year, date.month, date.day))
                    except ValueError:
                        continue
            self.navigation_panel.highlight_dates(dates_with_notes)
        except FileNotFoundError:
            print(
                f"Répertoire du journal non trouvé pour la mise à jour du calendrier: {self.journal_directory}"
            )
        self.update_tag_cloud()
        self.update_word_cloud()

    def _set_file_label_color(self, color):
        """Définit la couleur du texte pour le label du nom de fichier."""
        self.file_label.setStyleSheet(f"color: {color};")

    def _start_export_flashing(self):
        """Démarre le message clignotant pour un export."""
        self.pdf_status_label.setVisible(True)
        self.pdf_flash_timer.start()

    def _stop_export_flashing(self):
        """Arrête le message clignotant."""
        self.pdf_flash_timer.stop()
        self.pdf_status_label.setVisible(False)

    def _toggle_pdf_status_visibility(self):
        """Bascule la visibilité du label de statut PDF."""
        self.pdf_status_label.setVisible(not self.pdf_status_label.isVisible())

    def _show_transient_save_status(self, message, timeout=3000):
        """Affiche un message de sauvegarde vert et centré pendant un temps donné."""
        self.save_status_label.setText(message)
        self.save_status_label.setVisible(True)
        QTimer.singleShot(timeout, lambda: self.save_status_label.setVisible(False))

    def open_preferences(self):
        """Ouvre la boîte de dialogue des préférences."""
        dialog = PreferencesDialog(self.settings_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.settings_manager.set(
                "editor.font_family", dialog.current_font.family()
            )
            self.settings_manager.set(
                "editor.font_size", dialog.current_font.pointSize()
            )
            self.settings_manager.set(
                "editor.background_color", dialog.current_color.name()
            )
            self.settings_manager.set(
                "editor.text_color", dialog.current_text_color.name()
            )
            self.settings_manager.set(
                "editor.heading_color", dialog.current_heading_color.name()
            )
            self.settings_manager.set(
                "editor.list_color", dialog.current_list_color.name()
            )
            self.settings_manager.set(
                "editor.selection_text_color",
                dialog.current_selection_text_color.name(),
            )
            self.settings_manager.set(
                "editor.inline_code_text_color",
                dialog.current_inline_code_text_color.name(),
            )
            self.settings_manager.set(
                "editor.inline_code_background_color",
                dialog.current_inline_code_bg_color.name(),
            )
            self.settings_manager.set(
                "editor.code_block_background_color",
                dialog.current_code_block_bg_color.name(),
            )
            self.settings_manager.set(
                "editor.bold_color", dialog.current_bold_color.name()
            )
            self.settings_manager.set(
                "editor.italic_color", dialog.current_italic_color.name()
            )
            self.settings_manager.set(
                "editor.strikethrough_color",
                dialog.current_strikethrough_color.name(),
            )
            self.settings_manager.set(
                "editor.highlight_color",
                dialog.current_highlight_color.name(),
            )
            self.settings_manager.set(
                "editor.tag_color", dialog.current_tag_color.name()
            )
            self.settings_manager.set(
                "editor.timestamp_color", dialog.current_timestamp_color.name()
            )
            self.settings_manager.set(
                "editor.quote_color", dialog.current_quote_color.name()
            )
            self.settings_manager.set(
                "editor.link_color", dialog.current_link_color.name()
            )
            self.settings_manager.set(
                "editor.code_font_family", dialog.current_code_font.family()
            )
            self.settings_manager.set(
                "outline.font_family", dialog.current_outline_font.family()
            )
            self.settings_manager.set(
                "outline.font_size", dialog.current_outline_font.pointSize()
            )
            self.settings_manager.set(
                "editor.html_comment_color",
                dialog.current_html_comment_color.name(),
            )
            self.settings_manager.set(
                "editor.show_line_numbers",
                dialog.show_line_numbers_checkbox.isChecked(),
            )
            self.settings_manager.set(
                "integrations.show_quote_of_the_day",
                dialog.show_quote_checkbox.isChecked(),
            )
            self.settings_manager.set(
                "integrations.youtube_enabled",
                dialog.youtube_integration_checkbox.isChecked(),
            )

            self.settings_manager.set(
                "ui.show_indexing_stats",
                dialog.show_indexing_stats_checkbox.isChecked(),
            )

            user_words_text = dialog.excluded_words_edit.toPlainText()
            user_words_list = [
                word.strip().lower()
                for word in user_words_text.split(",")
                if word.strip()
            ]
            self.settings_manager.set("indexing.user_excluded_words", user_words_list)

            excluded_tags_text = dialog.excluded_tags_edit.toPlainText()
            excluded_tags_list = [
                tag.strip().lower()
                for tag in excluded_tags_text.split(",")
                if tag.strip()
            ]
            self.settings_manager.set(
                "indexing.excluded_tags_from_cloud", excluded_tags_list
            )

            excluded_words_cloud_text = dialog.excluded_words_cloud_edit.toPlainText()
            excluded_words_cloud_list = [
                word.strip().lower()
                for word in excluded_words_cloud_text.split(",")
                if word.strip()
            ]
            self.settings_manager.set(
                "indexing.excluded_words_from_cloud", excluded_words_cloud_list
            )

            self.settings_manager.set(
                "ui.show_navigation_panel", dialog.show_nav_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_outline_panel", dialog.show_outline_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_preview_panel", dialog.show_preview_checkbox.isChecked()
            )

            self.settings_manager.save_settings()
            self.apply_settings()

    def save_panel_visibility_settings(self):
        """Sauvegarde l'état de visibilité actuel des panneaux."""
        self.settings_manager.set(
            "ui.show_navigation_panel", self.navigation_panel.isVisible()
        )
        self.settings_manager.set(
            "ui.show_outline_panel", self.outline_panel.isVisible()
        )
        self.settings_manager.set("ui.show_preview_panel", self.preview.isVisible())
        self.settings_manager.save_settings()

    def apply_settings(self):
        """Applique les paramètres chargés à l'interface utilisateur."""
        # Récupérer l'état des panneaux depuis les paramètres
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        show_outline = self.settings_manager.get("ui.show_outline_panel", False)
        show_preview = self.settings_manager.get("ui.show_preview_panel", True)

        # Bloquer temporairement les signaux pour éviter les appels en cascade
        self.nav_button.blockSignals(True)
        self.outline_button.blockSignals(True)
        self.preview_button.blockSignals(True)

        # Appliquer la visibilité des panneaux
        self.navigation_panel.setVisible(show_nav)
        self.outline_panel.setVisible(show_outline)
        self.preview.setVisible(show_preview)

        # Synchroniser les switchs avec l'état des panneaux
        self.nav_button.setChecked(show_nav)
        self.outline_button.setChecked(show_outline)
        self.preview_button.setChecked(show_preview)

        # Débloquer les signaux
        self.nav_button.blockSignals(False)
        self.outline_button.blockSignals(False)
        self.preview_button.blockSignals(False)

        # Synchroniser également les actions du menu
        self.toggle_navigation_action.setChecked(show_nav)
        self.toggle_outline_action.setChecked(show_outline)
        self.toggle_preview_action.setChecked(show_preview)

        # Appliquer les paramètres de l'éditeur
        show_stats = self.settings_manager.get("ui.show_indexing_stats", True)
        if not show_stats:
            self.tag_index_status_label.clear()

        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        font = QFont(font_family, font_size)
        self.editor.set_font(font)

        bg_color = self.settings_manager.get("editor.background_color")
        self.editor.set_background_color(bg_color)

        text_color = self.settings_manager.get("editor.text_color")
        self.editor.set_text_color(text_color)

        heading_color = self.settings_manager.get("editor.heading_color")
        self.editor.set_heading_color(heading_color)

        list_color = self.settings_manager.get("editor.list_color")
        self.editor.set_list_color(list_color)

        selection_text_color = self.settings_manager.get("editor.selection_text_color")
        self.editor.set_selection_text_color(selection_text_color)

        inline_text_color = self.settings_manager.get("editor.inline_code_text_color")
        inline_bg_color = self.settings_manager.get(
            "editor.inline_code_background_color"
        )
        self.editor.set_inline_code_colors(inline_text_color, inline_bg_color)

        code_block_bg_color = self.settings_manager.get(
            "editor.code_block_background_color"
        )
        self.editor.set_code_block_background_color(code_block_bg_color)

        bold_color = self.settings_manager.get("editor.bold_color")
        italic_color = self.settings_manager.get("editor.italic_color")
        strikethrough_color = self.settings_manager.get("editor.strikethrough_color")
        highlight_color = self.settings_manager.get("editor.highlight_color")
        self.editor.set_text_style_colors(
            bold_color, italic_color, strikethrough_color, highlight_color
        )

        tag_color = self.settings_manager.get("editor.tag_color")
        timestamp_color = self.settings_manager.get("editor.timestamp_color")
        self.editor.set_misc_colors(tag_color, timestamp_color)

        quote_color = self.settings_manager.get("editor.quote_color")
        link_color = self.settings_manager.get("editor.link_color")
        self.editor.set_quote_link_colors(quote_color, link_color)

        code_font = self.settings_manager.get("editor.code_font_family")
        self.editor.set_code_font(code_font)

        html_comment_color = self.settings_manager.get(
            "editor.html_comment_color", "#a4b5cf"
        )
        self.editor.set_html_comment_color(html_comment_color)

        show_line_numbers = self.settings_manager.get("editor.show_line_numbers", False)
        if hasattr(self.editor, "set_line_numbers_visible"):
            self.editor.set_line_numbers_visible(show_line_numbers)

        css_theme = self.settings_manager.get(
            "preview.css_theme", "default_preview.css"
        )
        self.preview.set_css_theme(css_theme)

        youtube_enabled = self.settings_manager.get(
            "integrations.youtube_enabled", True
        )
        self.insert_youtube_video_action.setEnabled(youtube_enabled)

        # Appliquer les styles au panneau du plan
        outline_font_family = self.settings_manager.get(
            "outline.font_family", font_family
        )
        outline_font_size = self.settings_manager.get("outline.font_size", font_size)
        outline_font = QFont(outline_font_family, outline_font_size)

        self.outline_panel.apply_styles(
            outline_font, QColor(heading_color), QColor(bg_color)
        )

        # Note: La synchronisation des contrôles de panneaux est déjà faite plus haut
        # Pas besoin d'appeler _sync_panel_controls() ici

    def update_tag_cloud(self):
        """Met à jour le contenu du nuage de tags."""
        excluded_tags_list = self.settings_manager.get(
            "indexing.excluded_tags_from_cloud", []
        )
        excluded_tags_set = set(excluded_tags_list)
        self.navigation_panel.tag_cloud.update_cloud(
            self.journal_directory, excluded_tags_set
        )

    def update_word_cloud(self):
        """Met à jour le contenu du nuage de mots."""
        excluded_words_list = self.settings_manager.get(
            "indexing.excluded_words_from_cloud", []
        )
        excluded_words_set = set(excluded_words_list)
        self.navigation_panel.word_cloud.update_cloud(
            self.journal_directory, excluded_words_set
        )

    def perform_search(self, query: str):
        """Effectue une recherche dans les index et affiche les résultats."""
        if not query or not self.journal_directory:
            self.navigation_panel.show_clouds()
            return

        results = []
        query_lower = query.lower()

        if query_lower.startswith("@@"):
            index_file = self.journal_directory / "index_tags.json"
            if index_file.exists() and len(query_lower) > 2:
                with open(index_file, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                for tag_key, tag_value in tags_data.items():
                    if tag_key.lower() == query_lower:
                        for detail in tag_value["details"]:
                            results.append(
                                (
                                    detail["date"],
                                    detail["context"],
                                    detail["filename"],
                                    detail.get("line", 1),
                                )
                            )
                        break
        else:
            index_file = self.journal_directory / "index_words.json"
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    words_data = json.load(f)
                if query_lower in words_data:
                    for detail in words_data[query_lower]["details"]:
                        results.append(
                            (
                                detail["date"],
                                detail["context"],
                                detail["filename"],
                                detail.get("line", 1),
                            )
                        )

        self.navigation_panel.show_search_results(results)

    def open_file_from_search(self, filename: str, line_number: int):
        """Ouvre un fichier sélectionné depuis les résultats de recherche."""
        if not self.journal_directory or not filename:
            return

        file_path = self.journal_directory / filename
        if file_path.exists():
            if self.check_save_changes():
                self.open_specific_file(str(file_path))
                self.go_to_line(line_number)
        else:
            QMessageBox.warning(
                self, "Fichier non trouvé", f"Le fichier '{filename}' n'existe plus."
            )

    def go_to_line(self, line_number: int):
        """Déplace le curseur à la ligne spécifiée et la positionne en haut de l'éditeur."""
        if line_number <= 0:
            return

        from PyQt5.QtGui import QTextCursor

        text_edit = self.editor.text_edit
        doc = text_edit.document()

        block = doc.findBlockByNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            text_edit.setTextCursor(cursor)

            scrollbar = text_edit.verticalScrollBar()
            cursor_rect = text_edit.cursorRect()
            scrollbar.setValue(scrollbar.value() + cursor_rect.top())

            text_edit.setFocus()

    def update_navigation_panel_data(self):
        """Met à jour les données nécessaires au panneau de navigation."""
        if not self.journal_directory:
            return

        tags_list = []
        index_file = self.journal_directory / "index_tags.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                tags_list = sorted(tags_data.keys())
            except (json.JSONDecodeError, IOError) as e:
                print(f"Erreur de lecture de l'index des tags pour le menu: {e}")

        self.navigation_panel.set_available_tags(tags_list)

    def expand_outline(self):
        """Déplie entièrement l'arborescence du plan du document."""
        self.outline_panel.tree_widget.expandAll()

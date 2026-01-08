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
#
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
import platform  # Ajout pour récupérer l'info OS
import sys
from urllib.parse import quote
from datetime import datetime
import requests

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
    QApplication,
    QToolBar,
)
from PyQt5.QtWidgets import QFormLayout, QLineEdit
from PyQt5.QtWidgets import QSplitterHandle, QToolButton
from PyQt5.QtWidgets import (
    QPushButton,
    QRadioButton,
    QComboBox,  # Keep these if they are used elsewhere in MainWindow
)
from PyQt5.QtCore import Qt, QTimer, QDate, QUrl, QLocale
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
from .notes_panel import NotesPanel
from .new_note_dialog import NewFileDialog
from .bookmark_handler import handle_insert_bookmark
from .epub_reader_panel import EpubReaderPanel
from .date_range_dialog import DateRangeDialog
from .backup_handler import backup_journal, restore_journal
from .preferences_dialog import PreferencesDialog
from .on_line_help import OnlineHelpWindow
from core.journal_backup_worker import JournalBackupWorker
from core.quote_fetcher import QuoteFetcher

from integrations.weather import get_weather_markdown
from bs4 import BeautifulSoup
from integrations.gps_map_generator import get_location_name, create_gps_map


from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot

from integrations.epub_exporter import EpubExportWorker
from integrations.epub_exporter import export_journal_to_epub
from integrations.gpx_trace_generator import (
    create_gpx_trace_map,
    get_gpx_data,
)
from integrations.pdf_exporter import (
    create_pdf_export_worker,
    export_journal_to_pdf,
    export_single_pdf,
)
from integrations.pdf_exporter import (
    get_pdf_theme_css,
)  # V3.1.5 - Import the new helper
from integrations.amazon_books import (  # V3.1.5 - Keep existing imports
    get_book_info_from_amazon,
    generate_book_markdown_fragment,
)
from integrations.youtube_video import (
    get_youtube_video_details,
    generate_youtube_markdown_block,
    get_youtube_transcript,
    TranscriptWorker,
)
from integrations.sun_moon import get_sun_moon_markdown
from integrations.gps_map_handler import (
    generate_gps_map_markdown,
    parse_gps_coordinates,
)
from integrations.url_to_markdown_handler import (
    run_url_to_markdown_conversion,
)
from integrations.image_exif import format_exif_as_markdown

# V3.0.1 - Enregistrer le schéma personnalisé avant de créer l'application
from PyQt5.QtWebEngineCore import QWebEngineUrlScheme

scheme = QWebEngineUrlScheme(b"epub")
scheme.setSyntax(QWebEngineUrlScheme.Syntax.Host)
scheme.setFlags(
    QWebEngineUrlScheme.SecureScheme
    | QWebEngineUrlScheme.LocalScheme
    | QWebEngineUrlScheme.LocalAccessAllowed
)
QWebEngineUrlScheme.registerScheme(scheme)

from PyQt5.QtCore import QCoreApplication


class MainWindowContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("MainWindowContext", text)


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
        self.setWindowTitle(self.tr("Créer un nouveau document"))
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.blank_radio = QRadioButton(self.tr("Créer un fichier vierge"))
        self.template_radio = QRadioButton(self.tr("Utiliser un modèle :"))
        self.template_combo = QComboBox()

        self.layout.addWidget(self.blank_radio)
        self.layout.addWidget(self.template_radio)
        self.layout.addWidget(self.template_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Valider"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
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
        # V3.3.8 - Utiliser la police par défaut de l'application
        app_font = QApplication.font()
        self.setFont(app_font)

        self.setCheckable(True)
        self.setMinimumHeight(24)

        # Calculer la largeur minimale en fonction du texte pour un ajustement parfait
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(
            text + "  "  # Ajouter un peu d'espace
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
        self.setWindowTitle(self.tr("Coordonnées GPS"))
        self.setMinimumWidth(300)

        self.layout = QFormLayout(self)

        self.lat_edit = QLineEdit(self)
        self.lon_edit = QLineEdit(self)

        self.layout.addRow(self.tr("Latitude:"), self.lat_edit)
        self.layout.addRow(self.tr("Longitude:"), self.lon_edit)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Valider"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
        self.layout.addRow(self.button_box)

        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # V3.3.8 - Appliquer la police système
        self.setFont(QApplication.font())

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
        self.setWindowTitle(self.tr("Source du fichier GPX"))
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        # Champ pour le chemin/URL
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            self.tr("https://example.com/trace.gpx ou /chemin/local/trace.gpx")
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton(self.tr("Parcourir..."), self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow(self.tr("Chemin ou URL:"), path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # V3.3.8 - Appliquer la police système
        self.setFont(QApplication.font())

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Sélectionner un fichier GPX"),
            "",
            self.tr("Fichiers GPX (*.gpx)"),
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
        self.setWindowTitle(self.tr("Source du fichier PDF"))
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            self.tr("https://example.com/document.pdf ou /chemin/local/document.pdf")
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton(self.tr("Parcourir..."), self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow(self.tr("Chemin ou URL:"), path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        # V3.3.8 - Appliquer la police système
        self.setFont(QApplication.font())

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Sélectionner un fichier PDF"),
            "",
            self.tr("Fichiers PDF (*.pdf)"),
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
        self.setWindowTitle(self.tr("Insérer un modèle"))
        self.setMinimumWidth(400)

        self.layout = QVBoxLayout(self)

        self.label = QLabel(self.tr("Choisir un modèle à insérer :"))
        self.template_combo = QComboBox()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.template_combo)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Insérer"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
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


class InsertLinkDialog(QDialog):
    """Boîte de dialogue pour insérer un lien Markdown (local ou distant)."""

    def __init__(self, parent=None, journal_dir=None, selected_text=""):
        super().__init__(parent)
        self.journal_dir = journal_dir
        self.setWindowTitle(self.tr("Insérer un lien"))
        self.setMinimumWidth(500)

        self.layout = QFormLayout(self)

        self.text_edit = QLineEdit(selected_text, self)
        self.url_layout = QHBoxLayout()
        self.url_edit = QLineEdit(self)
        self.url_edit.setPlaceholderText(
            self.tr("https://... ou chemin/local/fichier.ext")
        )
        self.url_layout.addWidget(self.url_edit)

        if self.journal_dir:
            self.browse_button = QPushButton(self.tr("Parcourir..."), self)
            self.browse_button.clicked.connect(self._browse_local_file)
            self.url_layout.addWidget(self.browse_button)

        self.layout.addRow(self.tr("Texte du lien:"), self.text_edit)
        self.layout.addRow(self.tr("URL ou chemin:"), self.url_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Insérer"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        # V3.3.8 - Appliquer la police système
        self.setFont(QApplication.font())

        self.layout.addRow(self.button_box)

    def _browse_local_file(self):
        """Ouvre un sélecteur de fichier pour les fichiers locaux."""
        start_dir = (
            str(self.journal_dir)
            if self.journal_dir and self.journal_dir.is_dir()
            else str(Path.home())
        )
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Sélectionner un fichier local"),
            start_dir,
            self.tr("Tous les fichiers (*)"),
        )
        if path:
            # Si le journal_dir n'était pas défini, on le met à jour si possible
            if not self.journal_dir and "bluenotebook" in path.lower():
                # Heuristique simple pour trouver la racine du journal
                self.journal_dir = Path(path.split("bluenotebook")[0])
            self.url_edit.setText(path)
            if not self.text_edit.text():
                # Pré-remplir le texte du lien avec le nom du fichier sans extension
                file_name = Path(path).stem
                self.text_edit.setText(file_name)

    def validate_and_accept(self):
        """Vérifie que les champs ne sont pas vides avant d'accepter."""
        link_text = self.text_edit.text().strip()
        url_text = self.url_edit.text().strip()

        if not link_text or not url_text:
            QMessageBox.warning(
                self,
                self.tr("Champs requis"),
                self.tr(
                    "Le texte du lien et l'URL/chemin sont tous les deux obligatoires."
                ),
            )
        else:
            self.accept()

    def get_link_data(self):
        """Retourne le texte du lien et l'URL/chemin."""
        link_path = self.url_edit.text().strip()
        link_text = self.text_edit.text().strip()

        # Si le chemin est local (ne commence pas par http/ftp), forcer le texte du lien
        if not link_path.lower().startswith(("http://", "https://", "ftp://")):
            link_text = Path(link_path).stem

        return link_text, link_path


class MainWindow(QMainWindow):
    def __init__(self, journal_dir_arg=None, app_version="2.4.4"):
        super().__init__()
        self.journal_dir_arg = journal_dir_arg
        self.app_version = app_version
        self.journal_directory = None
        self.current_file = None
        self.is_modified = False

        self.daily_quote = None
        self.last_document_reader = None
        self.daily_author = None
        self.tag_index_count = -1  # Only tag count remains

        from core.settings import SettingsManager

        self.settings_manager = SettingsManager()

        # APRÈS (ne rien mettre, ce sera géré dans main.py)
        # Le bloc est complètement supprimé du __init__ de MainWindow

        # ============================================================
        # Dans la méthode apply_settings(), MODIFIEZ ce bloc :
        # ============================================================

        # Initialiser le pool de threads pour les tâches de fond
        self.thread_pool = QThreadPool()

        self.setup_ui()
        self.setup_statusbar()
        self.setup_journal_directory()
        self.setup_menu()
        self.setup_panels_toolbar()
        self.setup_notes_panel()
        self.apply_settings()
        self.setup_connections()

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
        self.load_initial_document_reader()

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle(
            self.tr("BlueNotebook V{app_version} - Éditeur Markdown").format(
                app_version=self.app_version
            )
        )
        self.setGeometry(100, 100, 1400, 900)

        self.set_application_icon()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Appliquer un fond neutre à la fenêtre principale
        # central_widget.setStyleSheet("background-color: #f0f2f5;")

        # V3.3.8 - Appliquer la police système à la fenêtre principale
        self.setFont(QApplication.font())

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
        self.notes_panel = NotesPanel(settings_manager=self.settings_manager)
        main_splitter.addWidget(self.notes_panel)

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

        self.epub_reader_panel = EpubReaderPanel(settings_manager=self.settings_manager)
        main_splitter.addWidget(self.epub_reader_panel)

        # V3.2.2 - Supprimer la largeur fixe pour permettre le redimensionnement
        # self.notes_panel.setFixedWidth(400)
        # Rendre le panneau de navigation redimensionnable
        # self.navigation_panel.setFixedWidth(500)
        self.outline_panel.setFixedWidth(400)
        # V3.0.1 - Supprimer la largeur fixe pour permettre le redimensionnement
        # self.epub_reader_panel.setFixedWidth(600)
        main_splitter.setSizes([400, 400, 400, 1400, 400])
        main_splitter.setCollapsible(0, False)
        # V3.0.1 - Permettre au panneau lecteur d'être réduit
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
                        print(f"✅ Loaded icon: : {icon_path}")
                        return
                except Exception as e:
                    print(f"⚠️ Error loading {icon_path}: {e}")
                    continue

        print(f"ℹ️ No icon found, using the default icon")

    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()

        self._create_actions()

        # Menu Fichier
        file_menu = menubar.addMenu(self.tr("&Fichier"))
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_any_file_action)
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
        file_menu.addAction(self.export_pdf_action)
        file_menu.addAction(self.export_journal_epub_action)
        file_menu.addAction(self.export_journal_pdf_action)
        file_menu.addSeparator()
        file_menu.addAction(self.preferences_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        # Menu Edition
        edit_menu = menubar.addMenu(self.tr("&Edition"))
        edit_menu.addAction(self.insert_template_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)

        # Les actions de basculement des panneaux sont conservées pour les raccourcis clavier
        self.addAction(self.toggle_navigation_action)
        self.addAction(self.toggle_outline_action)
        self.addAction(self.toggle_notes_details_action)
        self.addAction(self.toggle_preview_action)
        self.addAction(self.toggle_reader_action)

        # Menu Formatter
        format_menu = menubar.addMenu(self.tr("F&ormater"))
        self._setup_format_menu(format_menu)

        # Menu Insérer
        insert_menu = menubar.addMenu(self.tr("&Insérer"))
        self._setup_insert_menu(insert_menu)

        # Menu Intégrations
        integrations_menu = menubar.addMenu(self.tr("&Intégrations"))
        integrations_menu.addAction(self.insert_quote_day_action)
        integrations_menu.addAction(self.insert_gpx_trace_action)
        integrations_menu.addAction(self.insert_gps_map_action)
        integrations_menu.addAction(self.insert_youtube_video_action)
        integrations_menu.addAction(self.insert_weather_action)
        integrations_menu.addAction(self.insert_amazon_book_action)
        integrations_menu.addAction(self.insert_sun_moon_action)
        integrations_menu.addAction(self.convert_pdf_markdown_action)
        integrations_menu.addAction(self.convert_url_markdown_action)

        # Menu Aide
        help_menu = menubar.addMenu(self.tr("&Aide"))
        help_menu.addAction(self.online_help_action)
        help_menu.addAction(self.about_action)

    def _create_actions(self):
        """Crée toutes les actions de l'application."""
        self.new_action = QAction(
            self.tr("Nouveau"),
            self,
            shortcut=QKeySequence.New,
            statusTip=self.tr("Créer un nouveau fichier"),
            triggered=self.new_file,
        )
        self.open_any_file_action = QAction(
            self.tr("Ouvrir..."),
            self,
            shortcut=QKeySequence.Open,
            statusTip=self.tr("Ouvrir un fichier existant"),
            triggered=self.open_any_file,
        )
        self.open_journal_action = QAction(
            self.tr("Ouvrir Journal"),
            self,
            statusTip=self.tr("Ouvrir un répertoire de journal"),
            triggered=self.open_journal,
        )
        self.open_document_action = QAction(
            self.tr("Ouvrir Document..."),
            self,
            statusTip=self.tr("Ouvrir un document EPUB ou PDF dans le lecteur"),
            triggered=self.open_document_for_reader,
        )
        self.save_action = QAction(
            self.tr("Sauvegarder dans Journal"),
            self,
            shortcut=QKeySequence.Save,
            statusTip=self.tr("Sauvegarder le fichier dans le journal"),
            triggered=self.save_file,
        )
        self.save_as_action = QAction(
            self.tr("Sauvegarder sous..."),
            self,
            shortcut=QKeySequence.SaveAs,
            statusTip=self.tr("Sauvegarder sous un nouveau nom"),
            triggered=self.save_file_as,
        )
        self.save_as_template_action = QAction(
            self.tr("Sauvegarder comme Modèle..."),
            self,
            statusTip=self.tr("Sauvegarder le document actuel comme un nouveau modèle"),
            triggered=self.save_as_template,
        )
        self.backup_journal_action = QAction(
            self.tr("Sauvegarde Journal..."),
            self,
            statusTip=self.tr("Sauvegarder le journal complet dans une archive ZIP"),
            triggered=self.backup_journal,
        )
        self.restore_journal_action = QAction(
            self.tr("Restauration Journal..."),
            self,
            statusTip=self.tr("Restaurer le journal depuis une archive ZIP"),
            triggered=self.restore_journal,
        )
        self.export_action = QAction(
            self.tr("Exporter HTML..."),
            self,
            statusTip=self.tr("Exporter en HTML"),
            triggered=self.export_html,
        )
        self.export_pdf_action = QAction(
            self.tr("Exporter en PDF..."),
            self,
            statusTip=self.tr("Exporter le fichier actuel en PDF"),
            triggered=self.export_pdf,
        )
        self.export_journal_pdf_action = QAction(
            self.tr("Exporter Journal PDF..."),
            self,
            statusTip=self.tr("Exporter le journal complet en PDF"),
            triggered=self.export_journal_pdf,
        )
        self.export_journal_epub_action = QAction(
            self.tr("Exporter Journal EPUB..."),
            self,
            statusTip=self.tr("Exporter le journal complet en EPUB"),
            triggered=self.export_journal_epub,
        )
        self.preferences_action = QAction(
            self.tr("Préférences..."),
            self,
            statusTip=self.tr("Ouvrir les préférences de l'application"),
            triggered=self.open_preferences,
        )
        self.quit_action = QAction(
            self.tr("Quitter"),
            self,
            shortcut=QKeySequence.Quit,
            statusTip=self.tr("Quitter l'application"),
            triggered=self.close,
        )

        self.undo_action = QAction(
            self.tr("Annuler"),
            self,
            shortcut=QKeySequence.Undo,
            triggered=self.editor.undo,
        )
        self.redo_action = QAction(
            self.tr("Rétablir"),
            self,
            shortcut=QKeySequence.Redo,
            triggered=self.editor.redo,
        )
        self.find_action = QAction(
            self.tr("Rechercher"),
            self,
            # V3.2.1 - Add Notes Panel
            shortcut=QKeySequence.Find,
            triggered=self.editor.show_find_dialog,
        )
        self.toggle_navigation_action = QAction(
            self.tr("Basculer Navigation Journal"),
            self,
            shortcut="F6",
            checkable=True,
            triggered=self.toggle_navigation,
        )
        self.toggle_notes_action = QAction(
            self.tr("Basculer Explorateur de Notes"),
            self,
            shortcut="F9",
            checkable=True,
            triggered=self.toggle_notes,
        )
        # V3.2.2 - Action pour afficher/masquer les détails dans le panneau de notes
        self.toggle_notes_details_action = QAction(
            self.tr("Afficher/Masquer les détails des notes"),
            self,
            shortcut="Ctrl+M",
            triggered=self.notes_panel.toggle_details_columns,
        )
        self.toggle_outline_action = QAction(
            self.tr("Basculer Plan du document"),
            self,
            shortcut="F7",
            checkable=True,
            triggered=self.toggle_outline,
        )
        self.toggle_preview_action = QAction(
            self.tr("Basculer Aperçu HTML"),
            self,
            shortcut="F5",
            checkable=True,
            triggered=self.toggle_preview,
        )
        self.toggle_reader_action = QAction(
            self.tr("Basculer Lecteur"),
            self,
            shortcut="F8",
            checkable=True,
            triggered=self.toggle_reader,
        )
        self.about_action = QAction(
            self.tr("À propos"),
            self,
            triggered=self.show_about,
        )

        self.online_help_action = QAction(
            self.tr("Documentation en ligne"),
            self,
            triggered=self.show_online_help,
        )

        self.insert_quote_day_action = QAction(
            self.tr("Citation du jour"),
            self,
            triggered=self.insert_quote_of_the_day,
        )

        self.insert_youtube_video_action = QAction(
            self.tr("Vidéo YouTube"),
            self,
            icon=QIcon("bluenotebook/resources/icons/youtube_32px.png"),
            statusTip=self.tr("Insérer une vidéo YouTube"),
            triggered=self.insert_youtube_video,
        )
        self.insert_template_action = QAction(
            self.tr("Insérer un modèle..."),
            self,
            statusTip=self.tr(
                "Insérer le contenu d'un modèle à la position du curseur"
            ),
            triggered=self.insert_template,
        )
        self.insert_gps_map_action = QAction(
            self.tr("Carte GPS"),
            self,
            statusTip=self.tr("Insérer une carte statique à partir de coordonnées GPS"),
            triggered=self.insert_gps_map,
        )
        self.insert_gpx_trace_action = QAction(
            self.tr("Trace GPX"),
            self,
            statusTip=self.tr("Insérer une carte à partir d'une trace GPX"),
            triggered=self.insert_gpx_trace,
        )
        self.insert_weather_action = QAction(
            self.tr("Météo Weatherapi.com"),
            self,
            statusTip=self.tr("Insérer la météo actuelle"),
            triggered=self.insert_weather,
        )
        self.insert_amazon_book_action = QAction(
            self.tr("Amazon ISBN"),
            self,
            statusTip=self.tr(
                "Insérer les informations d'un livre depuis Amazon via son ISBN"
            ),
            triggered=self.insert_amazon_book,
        )
        self.insert_sun_moon_action = QAction(
            self.tr("Astro du jour"),
            self,
            statusTip=self.tr("Insérer les données astronomiques du jour"),
            triggered=self.insert_sun_moon_data,
        )
        self.convert_pdf_markdown_action = QAction(
            self.tr("Conversion PDF-Markdown"),
            self,
            statusTip=self.tr("Convertir un fichier PDF en Markdown avec 'markitdown'"),
            triggered=self.convert_pdf_to_markdown,
        )
        self.convert_url_markdown_action = QAction(
            self.tr("Conversion URL(HTML)-Markdown"),
            self,
            statusTip=self.tr(
                "Convertir une page Web (URL ou fichier local) en Markdown"
            ),
            triggered=self.convert_url_to_markdown,
        )
        self.insert_bookmark_action = QAction(
            self.tr("🔖 Bookmark"),
            self,
            statusTip=self.tr("Insérer un signet à partir d'une URL"),
            triggered=lambda: handle_insert_bookmark(self),
        )

    def _setup_format_menu(self, format_menu):
        """Configure le menu de formatage de manière dynamique."""
        # Sous-menu Titre
        title_menu = QMenu(self.tr("Titres"), self)
        title_actions_data = [
            (self.tr("Niv 1 (#)"), "h1"),
            (self.tr("Niv 2 (##)"), "h2"),
            (self.tr("Niv 3 (###)"), "h3"),
            (self.tr("Niv 4 (####)"), "h4"),
            (self.tr("Niv 5 (#####)"), "h5"),
        ]
        for name, data in title_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            title_menu.addAction(action)
        format_menu.addMenu(title_menu)

        # Sous-menu Style de texte
        style_menu = QMenu(self.tr("Style de texte"), self)
        style_actions_data = [
            (self.tr("Gras (**texte**)"), "bold", QKeySequence.Bold),
            (self.tr("Italique (*texte*)"), "italic"),
            (self.tr("Barré (~~texte~~)"), "strikethrough"),
            (self.tr("Surligné (==texte==)"), "highlight"),
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
        code_menu = QMenu(self.tr("Code"), self)
        code_actions_data = [
            (self.tr("Monospace (inline)"), "inline_code"),
            (self.tr("Bloc de code"), "code_block"),
        ]
        for name, data in code_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            code_menu.addAction(action)
        format_menu.addMenu(code_menu)

        # Sous-menu Listes
        list_menu = QMenu(self.tr("Listes"), self)
        list_actions_data = [
            (self.tr("• Liste non ordonnée"), "ul"),
            (self.tr("1. Liste ordonnée"), "ol"),
            (self.tr("☑️ Liste de tâches"), "task_list"),
        ]
        for name, data in list_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            list_menu.addAction(action)
        format_menu.addMenu(list_menu)

        format_menu.addSeparator()

        clear_action = QAction(self.tr("RaZ (Effacer le formatage)"), self)
        clear_action.triggered.connect(self.editor.clear_formatting)
        format_menu.addAction(clear_action)

    def _setup_insert_menu(self, insert_menu):
        """Configure le menu d'insertion de manière dynamique."""
        insert_actions_data = [
            (
                self.tr("Image"),
                "markdown_image",
                QKeySequence("Ctrl+Shift+I"),
            ),
            (self.tr("🔗 Lien"), "markdown_link"),
            (self.tr("<> Lien URL/Email"), "url_link"),
            (self.tr("📎 Attachement"), "attachment"),
        ]

        for name, data, *shortcut in insert_actions_data:  # type: ignore
            action = QAction(name, self)
            if data == "markdown_link":
                action.triggered.connect(self._handle_markdown_link)
            elif data == "attachment":
                action.triggered.connect(self.editor.insert_attachment)
            else:
                action.triggered.connect(
                    functools.partial(self.editor.format_text, data)
                )
            if shortcut:
                action.setShortcut(shortcut[0])
            insert_menu.addAction(action)

        insert_menu.addAction(self.insert_bookmark_action)

        insert_menu.addSeparator()

        insert_hr_action = QAction(self.tr("Ligne Horizontale"), self)
        insert_hr_action.triggered.connect(lambda: self.editor.format_text("hr"))

        insert_comment_action = QAction(self.tr("Commentaire HTML"), self)
        insert_comment_action.triggered.connect(
            lambda: self.editor.format_text("html_comment")
        )

        insert_table_action = QAction(self.tr("Tableau"), self)
        insert_table_action.triggered.connect(lambda: self.editor.format_text("table"))
        insert_quote_action = QAction(self.tr("Citation"), self)
        insert_quote_action.triggered.connect(lambda: self.editor.format_text("quote"))

        insert_menu.addAction(insert_hr_action)
        insert_menu.addAction(insert_comment_action)
        insert_menu.addAction(insert_table_action)
        insert_menu.addAction(insert_quote_action)
        insert_menu.addSeparator()

        insert_tag_action = QAction(self.tr("Tag (@@)"), self)
        insert_tag_action.triggered.connect(lambda: self.editor.format_text("tag"))
        insert_menu.addAction(insert_tag_action)

        insert_time_action = QAction(self.tr("Horodatage"), self)
        insert_time_action.triggered.connect(lambda: self.editor.format_text("time"))
        insert_menu.addAction(insert_time_action)
        insert_menu.addSeparator()

        # Sous-menu Emoji
        emoji_menu = QMenu(self.tr("Emoji"), self)
        emoji_actions_data = [
            (self.tr("📖 Livre"), "📖"),
            (self.tr("🎵 Musique"), "🎵"),
            (self.tr("📚 À Lire"), "📚"),
            (self.tr("🎬 À Regarder"), "🎬"),
            (self.tr("🎧 A Ecouter"), "🎧"),
            (self.tr("✈️ Voyage"), "✈️"),
            (self.tr("❤️ Santé"), "❤️"),
            (self.tr("☀️ Soleil"), "☀️"),
            (self.tr("☁️ Nuage"), "☁️"),
            (self.tr("🌧️ Pluie"), "🌧️"),
            (self.tr("🌬️ Vent"), "🌬️"),
            (self.tr("😊 Content"), "😊"),
            (self.tr("😠 Mécontent"), "😠"),
            (self.tr("😢 Triste"), "😢"),
            (self.tr("✅ Fait"), "✅"),
            (self.tr("❌ Annulé"), "❌"),
            (self.tr("⚠️ Attention"), "⚠️"),
            (self.tr("📝 Mémo"), "📝"),
            (self.tr("📌 Note"), "📌"),
            (self.tr("❓ Question"), "❓"),
            (self.tr("❗ Exclamation"), "❗"),
        ]
        for name, emoji in emoji_actions_data:
            action = QAction(
                name, self, triggered=functools.partial(self.editor.insert_text, emoji)
            )
            emoji_menu.addAction(action)
        insert_menu.addMenu(emoji_menu)

    def setup_panels_toolbar(self):
        """Configure la barre d'outils pour basculer les panneaux."""
        self.panels_toolbar = QToolBar(self.tr("Panneaux"))
        self.panels_toolbar.setObjectName("panelsToolbar")
        self.panels_toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, self.panels_toolbar)

        # V3.3.8 - Appliquer la police système
        self.panels_toolbar.setFont(QApplication.font())

        # Style pour la barre d'outils pour un fond uni
        self.panels_toolbar.setStyleSheet("QToolBar { border: none; }")

        # Bouton Notes
        self.notes_button = SwitchButton(text=self.tr("Notes"))
        self.notes_button.toggled.connect(self.notes_panel.setVisible)
        self.panels_toolbar.addWidget(self.notes_button)

        # Bouton Navigation
        self.nav_button = SwitchButton(text=self.tr("Navigation"))
        self.nav_button.toggled.connect(self.navigation_panel.setVisible)
        self.panels_toolbar.addWidget(self.nav_button)

        # Bouton Plan
        self.outline_button = SwitchButton(text=self.tr("Plan"))
        self.outline_button.toggled.connect(self.outline_panel.setVisible)
        self.panels_toolbar.addWidget(self.outline_button)

        # Bouton Éditeur (toujours visible et désactivé)
        self.editor_button = SwitchButton(text=self.tr("Éditeur"))
        self.editor_button.setChecked(True)
        self.editor_button.setEnabled(False)
        self.panels_toolbar.addWidget(self.editor_button)

        # Bouton Aperçu
        self.preview_button = SwitchButton(text=self.tr("Aperçu"))
        self.preview_button.toggled.connect(self.preview.setVisible)
        self.panels_toolbar.addWidget(self.preview_button)

        # Bouton Lecteur
        self.reader_button = SwitchButton(text=self.tr("Lecteur"))
        self.reader_button.toggled.connect(self.toggle_reader_from_button)
        self.panels_toolbar.addWidget(self.reader_button)

        # Note: Les états initiaux seront définis dans apply_settings() après le chargement des préférences

    def _sync_panel_controls(self):
        """Synchronise l'état des boutons et des menus avec la visibilité des panneaux."""
        # Bloquer les signaux pour éviter les boucles de rappel
        self.notes_button.blockSignals(True)
        self.reader_button.blockSignals(True)
        self.nav_button.blockSignals(True)
        self.outline_button.blockSignals(True)
        self.preview_button.blockSignals(True)

        self.notes_button.setChecked(self.notes_panel.isVisible())
        self.toggle_notes_action.setChecked(self.notes_panel.isVisible())

        self.nav_button.setChecked(self.navigation_panel.isVisible())
        self.toggle_navigation_action.setChecked(self.navigation_panel.isVisible())

        self.outline_button.setChecked(self.outline_panel.isVisible())
        self.toggle_outline_action.setChecked(self.outline_panel.isVisible())

        self.preview_button.setChecked(self.preview.isVisible())
        self.toggle_preview_action.setChecked(self.preview.isVisible())

        self.reader_button.setChecked(self.epub_reader_panel.isVisible())
        self.toggle_reader_action.setChecked(self.epub_reader_panel.isVisible())

        # Rétablir les signaux
        self.notes_button.blockSignals(False)
        self.reader_button.blockSignals(False)
        self.nav_button.blockSignals(False)
        self.outline_button.blockSignals(False)
        self.preview_button.blockSignals(False)

    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        self.file_label = QLabel(self.tr("Nouveau fichier"))
        self._set_file_label_color("gray")
        self.statusbar.addWidget(self.file_label)

        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)

        self.stats_label = QLabel("")
        self.statusbar.addWidget(self.stats_label)

        self.journal_dir_label = QLabel("")
        # V3.3.8 - Appliquer la police système pour éviter les overrides
        self._set_styled_label_font(self.journal_dir_label, "#3498db")
        self.statusbar.addPermanentWidget(self.journal_dir_label)

        # V3.2.3 - Rendre le label de l'index cliquable pour le rafraîchissement
        self.tag_index_status_label = QLabel("")
        # V3.3.8 - Appliquer la police système pour éviter les overrides
        self._set_styled_label_font(
            self.tag_index_status_label, "#3498db", underline=True
        )
        self.tag_index_status_label.setCursor(Qt.PointingHandCursor)
        self.tag_index_status_label.setToolTip(
            self.tr("Cliquez pour rafraîchir l'index des tags")
        )
        self.tag_index_status_label.mousePressEvent = self.refresh_tag_index
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

        self.transcript_status_label = CenteredStatusBarLabel(
            self.tr("Récupération de la transcription en cours...")
        )
        self.transcript_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.transcript_status_label.setVisible(False)
        self.statusbar.addWidget(self.transcript_status_label, 1)

        self.bookmark_status_label = CenteredStatusBarLabel(
            self.tr("Vérification de l'URL...")
        )
        self.bookmark_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.bookmark_status_label.setVisible(False)
        self.statusbar.addWidget(self.bookmark_status_label, 1)

        # V3.5.0 - Status label for URL to Markdown conversion
        self.url_convert_status_label = CenteredStatusBarLabel(
            self.tr("Conversion URL en cours...")
        )
        self.url_convert_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.url_convert_status_label.setVisible(False)
        self.statusbar.addWidget(self.url_convert_status_label, 1)

        # V3.5.0 - Label générique pour les tâches de fond
        self.task_status_label = CenteredStatusBarLabel("")
        self.task_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.task_status_label.setVisible(False)
        self.statusbar.addWidget(self.task_status_label, 1)

        # V3.5.0 - Timer générique pour le clignotement
        self.task_flash_timer = QTimer(self)
        self.task_flash_timer.setInterval(500)
        self.task_flash_timer.timeout.connect(self._toggle_task_status_visibility)

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
        self.book_search_status_label = CenteredStatusBarLabel(
            self.tr("Recherche du livre...")
        )
        self.book_search_status_label.setStyleSheet("color: red; font-weight: bold;")
        self.book_search_status_label.setVisible(False)
        self.statusbar.addWidget(self.book_search_status_label, 1)

        # ──────────────────────────────────────────────────────────────
        # Timer pour faire clignoter le message de sauvegarde du journal
        # ──────────────────────────────────────────────────────────────
        self.backup_flash_timer = QTimer(self)
        self.backup_flash_timer.setInterval(600)

        # On réutilise la même fonction que pour l’export PDF → ça marche parfaitement
        self.backup_flash_timer.timeout.connect(self._toggle_pdf_status_visibility)

        # Label qui clignote pendant la sauvegarde (réutilisé aussi pour le backup)
        self.backup_status_label = QLabel(self.tr("Sauvegarde en cours…"))
        self.backup_status_label.setStyleSheet("color: #d35400; font-weight: bold;")
        self.backup_status_label.setAlignment(Qt.AlignCenter)
        self.backup_status_label.setVisible(False)

        self.statusbar.addPermanentWidget(self.backup_status_label)

        self.pdf_convert_flash_timer = QTimer(self)
        self.pdf_convert_flash_timer.setInterval(500)
        self.pdf_convert_flash_timer.timeout.connect(
            self._toggle_pdf_convert_status_visibility
        )

        self.transcript_flash_timer = QTimer(self)
        self.transcript_flash_timer.setInterval(500)
        self.transcript_flash_timer.timeout.connect(
            self._toggle_transcript_status_visibility
        )

        self.bookmark_flash_timer = QTimer(self)
        self.bookmark_flash_timer.setInterval(500)
        self.bookmark_flash_timer.timeout.connect(
            self._toggle_bookmark_status_visibility
        )

        self.url_convert_flash_timer = QTimer(self)
        self.url_convert_flash_timer.setInterval(500)
        self.url_convert_flash_timer.timeout.connect(
            self._toggle_url_convert_status_visibility
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

        # Connexions pour le nouveau panneau de notes
        self.navigation_panel.refresh_requested.connect(self.refresh_tag_index_from_nav)
        self.notes_panel.file_open_request.connect(self.open_file_from_notes)
        self.notes_panel.directory_selected.connect(self.on_notes_dir_selected)
        self.notes_panel.url_to_markdown_request.connect(
            self.convert_url_to_markdown_from_notes
        )
        self.notes_panel.pdf_to_markdown_request.connect(
            self.convert_pdf_to_markdown_from_notes
        )

    def setup_journal_directory(self):
        """Initialise le répertoire du journal au lancement."""
        journal_path = None

        if self.journal_dir_arg and Path(self.journal_dir_arg).is_dir():
            journal_path = Path(self.journal_dir_arg).resolve()
        elif self.settings_manager.get("journal.directory"):
            # Priorité aux paramètres définis lors du premier démarrage
            journal_path = Path(
                self.settings_manager.get("journal.directory")
            ).resolve()
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
                        self.tr("Erreur de Journal"),
                        self.tr(
                            "Impossible de créer le répertoire de journal par défaut:\n{e}"
                        ).format(e=e),
                    )
                    journal_path = None

        self.journal_directory = journal_path
        self.update_journal_dir_label()
        # V4.0.3 Fix Bug Windows

        if self.journal_directory:
            print(f"📔 Journal directory: {self.journal_directory}")
        else:
            print(f"⚠️ Journal directory not defined.")

    def setup_notes_panel(self):
        """Configure le panneau de notes avec le répertoire du journal."""
        if self.journal_directory:
            self.notes_panel.set_journal_directory(self.journal_directory)
            last_dir = self.settings_manager.get("notes.last_selected_dir")
            self.notes_panel.select_path(last_dir)

    def update_journal_dir_label(self):
        """Met à jour le label du répertoire de journal dans la barre de statut."""
        if self.journal_directory:
            self.journal_dir_label.setText(
                self.tr("Journal: {0}").format(self.journal_directory)
            )
        else:
            self.journal_dir_label.setText(self.tr("Journal: Non défini"))

    def load_initial_file(self):
        """Charge le fichier journal du jour s'il existe, sinon un nouveau fichier."""
        if self.journal_directory:
            today_str = datetime.now().strftime("%Y%m%d")
            journal_file_path = self.journal_directory / f"{today_str}.md"

            if journal_file_path.exists():
                self.open_specific_file(str(journal_file_path))
                return

        self.new_file()

    def load_initial_document_reader(self):
        """Charge le dernier document ouvert dans le lecteur."""
        last_doc = self.settings_manager.get("reader.last_document")
        if last_doc and os.path.exists(last_doc):
            self.last_document_reader = last_doc
            self.epub_reader_panel.load_document(last_doc)

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
            filename = self.tr("Nouveau fichier")
            self.file_label.setText(filename)

        if self.is_modified:
            self._set_file_label_color("red")
            self.setWindowTitle(
                self.tr("BlueNotebook V{app_version} - {filename} *").format(
                    app_version=self.app_version, filename=filename
                )
            )
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(
                self.tr("BlueNotebook V{app_version} - {filename}").format(
                    app_version=self.app_version, filename=filename
                )
            )
            self.modified_label.setText("")

    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)

        self.stats_label.setText(
            self.tr("{lines} lignes | {words} mots | {chars} caractères").format(
                lines=lines, words=words, chars=chars
            )
        )

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
                        self.tr(
                            "Le fichier template '{template_name}' est introuvable."
                        ).format(template_name=template_name)
                    )

                with open(template_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # --- V3.3.3 - Remplacement des placeholders pour TOUS les templates ---
                # Remplacer {{date}} par la date formatée
                if "{{date}}" in content:
                    content = content.replace("{{date}}", today_str)
                # Remplacer {{horodatage}} par l'heure actuelle
                if "{{horodatage}}" in content:
                    content = content.replace("{{horodatage}}", timestamp_str)

            except FileNotFoundError as e:
                QMessageBox.warning(self, self.tr("Template manquant"), str(e))
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
            self, self.tr("Sélectionner le répertoire du Journal")
        )
        if dir_name:
            new_journal_path = Path(dir_name).resolve()
            if new_journal_path.is_dir():
                self.journal_directory = new_journal_path
                self.update_journal_dir_label()
                QMessageBox.information(
                    self,
                    self.tr("Journal"),
                    self.tr("Le répertoire du journal est maintenant :\n{0}").format(
                        self.journal_directory
                    ),
                )
                self.start_initial_indexing()
                self.update_calendar_highlights()
                # Mettre à jour le panneau de notes avec le nouveau journal
                self.notes_panel.set_journal_directory(self.journal_directory)
                self.update_tag_cloud()

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
                self,
                self.tr("Erreur"),
                self.tr("Impossible d'ouvrir le fichier :\n{0}").format(str(e)),
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
            dialog.setWindowTitle(self.tr("Fichier Journal déjà existant"))
            layout = QVBoxLayout()
            layout.addWidget(
                QLabel(
                    self.tr("Le fichier journal '{0}' existe déjà.").format(
                        journal_file_path.name
                    )
                )
            )

            buttons = QDialogButtonBox()
            replace_button = buttons.addButton(
                self.tr("Remplacer"), QDialogButtonBox.DestructiveRole
            )
            append_button = buttons.addButton(
                self.tr("Ajouter à la fin"), QDialogButtonBox.AcceptRole
            )
            cancel_button = buttons.addButton(
                self.tr("Annuler"), QDialogButtonBox.RejectRole
            )
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
            self.tr("Sauvegarder le fichier"),
            "",
            self.tr(
                "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)"
            ),
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
            self.tr("Sauvegarder comme modèle"),
            str(templates_dir),
            self.tr("Fichiers Markdown (*.md)"),
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
                self.tr("Modèle sauvegardé : {0}").format(Path(filename).name), 3000
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Erreur"),
                self.tr("Impossible de sauvegarder le modèle :\n{0}").format(str(e)),
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
                    self.tr("Le fichier modèle '{0}' est introuvable.").format(
                        template_name
                    )
                )

            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()

            # --- V3.3.3 - Remplacement des placeholders pour l'insertion de template ---
            today_str = datetime.now().strftime("%A %d %B %Y").title()
            timestamp_str = datetime.now().strftime("%H:%M")

            if "{{date}}" in content:
                content = content.replace("{{date}}", today_str)
            if "{{horodatage}}" in content:
                content = content.replace("{{horodatage}}", timestamp_str)

            # Insérer le contenu dans l'éditeur
            self.editor.insert_text(content)

        except FileNotFoundError as e:
            QMessageBox.warning(self, self.tr("Modèle manquant"), str(e))

    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            self.is_modified = False
            self.update_title()
            self._set_file_label_color("green")
            self._show_transient_save_status(
                self.tr("Fichier sauvegardé : {0}").format(filename)
            )
            # Mettre à jour le calendrier pour refléter la nouvelle note
            self.update_calendar_highlights()

        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Erreur"),
                self.tr("Impossible de sauvegarder le fichier :\n{0}").format(str(e)),
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
            self._show_transient_save_status(
                self.tr("Contenu ajouté à : {0}").format(filename)
            )
            # Mettre à jour le calendrier pour refléter la nouvelle note
            self.update_calendar_highlights()
        except Exception as e:
            QMessageBox.critical(
                self,
                self.tr("Erreur"),
                self.tr("Impossible d'ajouter au fichier :\n{0}").format(str(e)),
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
            self.tr("Exporter en HTML"),
            default_path,
            self.tr("Fichiers HTML (*.html);;Tous les fichiers (*)"),
        )

        if filename:
            if not filename.endswith(".html"):
                filename += ".html"

            try:
                html_content = self.preview.get_html()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html_content)

                self.statusbar.showMessage(
                    self.tr("Exporté en HTML : {0}").format(filename), 3000
                )

                # Mémoriser le répertoire de destination pour la prochaine fois
                new_html_dir = str(Path(filename).parent)
                self.settings_manager.set("html.last_directory", new_html_dir)
                self.settings_manager.save_settings()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Erreur"),
                    self.tr("Impossible d'exporter en HTML :\n{0}").format(str(e)),
                )

    def export_pdf(self):
        """Exporter le fichier actuel en PDF avec WeasyPrint."""
        export_single_pdf(self)

    def export_journal_pdf(self):
        """Exporte l'ensemble du journal dans un unique fichier PDF avec WeasyPrint."""
        export_journal_to_pdf(self)

    def _on_export_finished(self, file_path):
        """Callback générique pour la fin d'un export."""
        self._stop_export_flashing()
        file_type = Path(file_path).suffix.upper()[1:]
        QMessageBox.information(
            self,
            self.tr("Exportation terminée"),
            self.tr(
                "Le journal a été exporté avec succès au format {0} dans :\n{1}"
            ).format(file_type, file_path),
        )

    def _on_export_error(self, error_message):
        """Callback générique en cas d'erreur d'export."""
        self._stop_export_flashing()
        QMessageBox.critical(
            self,
            self.tr("Erreur d'exportation"),
            self.tr(
                "Une erreur est survenue lors de la création du fichier :\n{0}"
            ).format(error_message),
        )

    def export_journal_epub(self):
        """Exporte l'ensemble du journal dans un unique fichier EPUB."""
        export_journal_to_epub(self)

    def backup_journal(self):
        """Sauvegarde le répertoire du journal dans une archive ZIP."""
        backup_journal(self)

    def restore_journal(self):
        """Restaure un journal depuis une archive ZIP."""
        restore_journal(self)

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

    def toggle_notes(self):
        """Basculer la visibilité du panneau de notes."""
        if self.notes_panel.isVisible():
            self.notes_panel.hide()
        else:
            self.notes_panel.show()
        self._sync_panel_controls()

    def toggle_outline(self):
        """Basculer la visibilité du panneau de plan."""
        if self.outline_panel.isVisible():
            self.outline_panel.hide()
        else:
            self.outline_panel.show()
        self._sync_panel_controls()

    def toggle_reader(self):
        """Basculer la visibilité du panneau lecteur."""
        if self.epub_reader_panel.isVisible():
            self.epub_reader_panel.hide()
        else:
            if not self.epub_reader_panel.has_document():
                self.open_document_for_reader()
            else:
                self.epub_reader_panel.show()
        self._sync_panel_controls()

    def toggle_reader_from_button(self, checked):
        """Gère le clic sur le bouton switch du lecteur."""
        self.toggle_reader()

    def show_online_help(self):
        """Affiche la page d'aide HTML dans une fenêtre interne."""
        # Déterminer le fichier d'aide en fonction de la langue de l'application
        app_locale = QLocale()
        if app_locale.language() == QLocale.English:
            help_filename = "online_help.html"
        else:
            help_filename = "aide_en_ligne.html"  # Par défaut en français

        base_path = os.path.dirname(os.path.abspath(__file__))
        help_file_path = os.path.join(
            base_path, "..", "resources", "html", help_filename
        )

        final_url = None
        if os.path.exists(help_file_path):
            final_url = QUrl.fromLocalFile(os.path.abspath(help_file_path)).toString()
        else:
            # Si le fichier spécifique à la langue n'est pas trouvé, essayer l'autre en fallback
            fallback_filename = (
                "aide_en_ligne.html"
                if help_filename == "online_help.html"
                else "online_help.html"
            )
            fallback_path = os.path.join(
                base_path, "..", "resources", "html", fallback_filename
            )
            if os.path.exists(fallback_path):
                final_url = QUrl.fromLocalFile(
                    os.path.abspath(fallback_path)
                ).toString()
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Aide non trouvée"),
                    self.tr("Le fichier d'aide n'a pas été trouvé:\n{0}").format(
                        help_file_path
                    ),
                )
                return

        if final_url:
            self.help_window = OnlineHelpWindow(final_url, self)
            self.help_window.show()

    def show_about(self):
        """Afficher la boîte À propos"""
        # V4.0.7 Récupération du nom de l'OS
        os_name = "Système inconnu"
        try:
            if platform.system() == "Linux":
                try:
                    # Python 3.10+
                    os_release = platform.freedesktop_os_release()
                    os_name = os_release.get("PRETTY_NAME", "Linux")
                except (AttributeError, OSError):
                    os_name = "Linux"
            elif platform.system() == "Windows":
                try:
                    if hasattr(sys, "getwindowsversion"):
                        version = sys.getwindowsversion()
                        if version.major == 10 and version.build >= 22000:
                            os_name = "Windows 11"
                        else:
                            os_name = f"Windows {platform.release()}"
                    else:
                        os_name = f"Windows {platform.release()}"
                except Exception:
                    os_name = f"Windows {platform.release()}"
            elif platform.system() == "Darwin":
                os_name = f"macOS {platform.mac_ver()[0]}"
            else:
                os_name = platform.system()
        except Exception:
            os_name = platform.platform()

        about_box = QMessageBox(self)
        about_box.setWindowTitle(self.tr("À propos de BlueNotebook"))
        about_box.setIcon(QMessageBox.Information)
        about_box.setTextFormat(Qt.RichText)
        about_text = self.tr(
            "<h2> BlueNotebook V{app_version}</h2>"
            "<p> Motorisé par {os_name} </p>"
            "<h2>_____________________________________________________________</h2>"
            "<p><b>Éditeur de journal personnel </b></p>"
            "<p>Basé sur un éditeur de texte Markdown avec aperçu HTML en temps réel,"
            "développé avec PyQt5 et QWebEngine.</p>"
            "<p>A partir d'une idée initiale de Jendrik Seipp <a href='https://github.com/jendrikseipp/rednotebook'>RedNotebook</a> </p>"
            "<h2>_____________________________________________________________</h2>"
            "<p><b>Fonctionnalités :</b></p>"
            "<ul>"
            "<li>Gestion d'un journal Personnel</li>"
            "<li>Navigation simple dans les notes du journal</li>"
            "<li>Sauvegarde/Restauration Journal</li>"
            "<li>Édition avec coloration syntaxique </li>"
            "<li>Aperçu HTML en temps réel</li>"
            "<li>Export HTML/PDF du journal complet ou partiel</li>"
            "<li>Gestion de Templates personnalisables</li>"
            "<li>Gestion de tags / Recherche par tags</li>"
            "<li>Insertion Cartes OpenStreetMap, Trace GPX, Videos Youtube et Météo</li>"
            "<li>Lecteur EPUB/PDF intégré avec recherche</li>"
            "<li>Gestion de tâches / TODO Listes</li>"
            "<li>Prise de Notes et Gestion des liens inter-notes</li>"
            "</ul>"
            "<h2>_____________________________________________________________</h2>"
            "<p>Dépôt GitHub : <a href='https://github.com/lephotographelibre/BlueNotebook'>BlueNotebook</a></p>"
            "<p>Licence : <a href='https://www.gnu.org/licenses/gpl-3.0.html'>GNU GPLv3</a></p>"
            "<p>© 2025-2026 BlueNotebook - Jean-Marc DIGNE</p>"
        ).format(app_version=self.app_version, os_name=os_name)
        about_box.setText(about_text)
        about_box.setStandardButtons(QMessageBox.Ok)
        about_box.resize(800, about_box.height())
        about_box.exec_()

    def open_document_for_reader(self):
        """Ouvre un document EPUB ou PDF dans le panneau lecteur."""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir un document"),
            self.settings_manager.get("reader.last_directory", str(Path.home())),
            self.tr(
                "Documents (*.epub *.pdf);;Fichiers EPUB (*.epub);;Fichiers PDF (*.pdf)"
            ),
        )

        if filename:
            file_ext = filename.lower()
            if file_ext.endswith(".epub") or file_ext.endswith(".pdf"):
                self.epub_reader_panel.load_document(filename)
                self.epub_reader_panel.show()
                self._sync_panel_controls()

                # Sauvegarder le chemin pour la prochaine fois
                self.last_document_reader = filename
                self.settings_manager.set("reader.last_document", filename)
                self.settings_manager.set(
                    "reader.last_directory", os.path.dirname(filename)
                )
                self.settings_manager.save_settings()
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Format non supporté"),
                    self.tr("Ce format de fichier n'est pas supporté."),
                )

    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle(self.tr("Modifications non sauvegardées"))
            msg_box.setText(
                self.tr(
                    "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?"
                )
            )
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            msg_box.button(QMessageBox.Save).setText(self.tr("Sauvegarder"))
            msg_box.button(QMessageBox.Discard).setText(self.tr("Ne pas sauvegarder"))
            msg_box.button(QMessageBox.Cancel).setText(self.tr("Annuler"))
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
            # V3.3.8 - Assurer la suppression propre des widgets complexes
            # pour éviter les erreurs "WebEnginePage still not deleted".
            self.epub_reader_panel.deleteLater()
            self.preview.deleteLater()

        else:
            event.ignore()

    def open_any_file(self):
        """Ouvre un fichier et l'aiguille vers l'éditeur ou le lecteur."""
        if not self.check_save_changes():
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Ouvrir un document"),
            self.settings_manager.get("reader.last_directory", str(Path.home())),
            self.tr(
                "Tous les documents supportés (*.md *.markdown *.txt *.epub *.pdf);;"
                "Fichiers Markdown (*.md *.markdown *.txt);;"
                "Documents EPUB (*.epub);;"
                "Documents PDF (*.pdf);;"
                "Tous les fichiers (*)"
            ),
        )

        if not filename:
            return

        file_ext = filename.lower()

        if file_ext.endswith((".epub", ".pdf")):
            # Ouvrir dans le lecteur de documents
            self.epub_reader_panel.load_document(filename)
            self.epub_reader_panel.show()
            self._sync_panel_controls()

            # Sauvegarder le chemin pour la prochaine fois
            self.last_document_reader = filename
            self.settings_manager.set("reader.last_document", filename)
            self.settings_manager.set(
                "reader.last_directory", os.path.dirname(filename)
            )
            self.settings_manager.save_settings()
        else:
            # Ouvrir dans l'éditeur Markdown (par défaut pour les autres types)
            self.open_specific_file(filename)

    def show_quote_of_the_day(self):
        """Affiche la citation du jour dans une boîte de dialogue."""
        # V4.1.6 - Fix Issue #131: Quote service is only in French
        app_locale = QLocale()
        if app_locale.language() != QLocale.French:
            # Ne rien faire si la langue n'est pas le français
            return

        if self.settings_manager.get("integrations.show_quote_of_the_day"):
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()
            if self.daily_quote and self.daily_author:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle(self.tr("Citation du Jour"))
                msg_box.setText(
                    self.tr("<blockquote><i>« {0} »</i></blockquote>").format(
                        self.daily_quote
                    )
                )
                msg_box.setInformativeText(f"<b>{self.daily_author}</b>")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()

    def insert_quote_of_the_day(self):
        """Insère la citation du jour dans l'éditeur, en la récupérant si nécessaire."""
        # V4.1.6 - Fix Issue #131: Quote service is only in French
        app_locale = QLocale()
        if app_locale.language() != QLocale.French:
            QMessageBox.information(
                self,
                self.tr("Service non disponible"),
                self.tr("Ce service n'est pas disponible dans votre langue."),
            )
            return

        if not self.daily_quote:
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()

        if self.daily_quote and self.daily_author:
            self.editor.format_text("quote_of_the_day")
        else:
            QMessageBox.warning(
                self,
                self.tr("Erreur"),
                self.tr("Impossible de récupérer la citation du jour."),
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
            dialog.setWindowTitle(self.tr("Vidéo ou Playlist YouTube"))
            dialog.setLabelText(
                self.tr("Entrez l'URL de la vidéo ou playlist Youtube:")
            )
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
                self.tr("Erreur d'intégration YouTube"),
                result,
            )
        else:  # C'est un dictionnaire de détails
            # On insère immédiatement le bloc Markdown de la vidéo
            markdown_block = generate_youtube_markdown_block(result)
            self.editor.insert_text(f"\n{markdown_block}\n")

            # On lance la recherche de transcription en arrière-plan
            transcript_enabled = self.settings_manager.get(
                "integrations.youtube_transcript_enabled", True
            )
            if transcript_enabled and result["type"] == "video":
                self._start_transcript_flashing()
                worker = TranscriptWorker(result["video_id"])
                worker.signals.finished.connect(self.on_transcript_finished)
                worker.signals.error.connect(self.on_transcript_error)
                worker.signals.no_transcript.connect(self.on_no_transcript)
                self.thread_pool.start(worker)

    def insert_gps_map(self):
        """Gère la logique d'insertion d'une carte GPS."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                self.tr("Journal non défini"),
                self.tr(
                    "Veuillez définir un répertoire de journal avant d'insérer une carte."
                ),
            )
            return

        lat, lon = None, None
        selected_text = self.editor.text_edit.textCursor().selectedText().strip()
        if selected_text:
            lat, lon = parse_gps_coordinates(selected_text)

        if lat is None:
            gps_dialog = GpsInputDialog(self)
            if gps_dialog.exec_() == QDialog.Accepted:
                lat, lon = gps_dialog.get_coordinates()

        if lat is None or lon is None:
            return

        width, ok = QInputDialog.getInt(
            self,
            self.tr("Taille de la carte"),
            self.tr("Largeur de l'image (en pixels):"),
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
            QMessageBox.critical(self, self.tr("Erreur de création de carte"), message)

    def insert_gpx_trace(self):
        """Gère la logique d'insertion d'une carte à partir d'une trace GPX."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                self.tr("Journal non défini"),
                self.tr(
                    "Veuillez définir un répertoire de journal avant d'insérer une trace GPX."
                ),
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
            self.tr("Taille de la carte"),
            self.tr("Largeur de l'image (en pixels):"),
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
                self.tr("Fichier GPX introuvable"),
                self.tr("Impossible de lire le fichier GPX depuis :\n{0}").format(
                    gpx_input
                ),
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
            QMessageBox.critical(
                self, self.tr("Erreur de création de la trace"), message
            )

    def insert_html_image(self):
        """Gère la logique d'insertion d'une image HTML avec gestion EXIF."""
        image_path, is_local = self.editor.get_image_path_from_user()
        if not image_path:
            return

        width, ok = QInputDialog.getInt(
            self,
            self.tr("Taille de l'image"),
            self.tr("Largeur maximale en pixels:"),
            400,
            100,
            2000,
            50,
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
                self.tr("Données EXIF trouvées"),
                self.tr(
                    "Des données EXIF ont été trouvées dans l'image. "
                    "Voulez-vous les insérer sous l'image ?"
                ),
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

    def _handle_markdown_link(self):
        """Gère l'insertion d'un lien Markdown (local ou distant)."""
        selected_text = self.editor.text_edit.textCursor().selectedText().strip()

        dialog = InsertLinkDialog(self, self.journal_directory, selected_text)
        if dialog.exec_() != QDialog.Accepted:
            return

        link_text, link_path = dialog.get_link_data()

        # Si c'est une URL distante, on insère directement
        if link_path.lower().startswith(("http://", "https://", "ftp://")):
            markdown_link = f"[{link_text}]({link_path})"
            self.editor.insert_text(markdown_link)
            return

        # C'est un chemin local
        local_path = Path(link_path)
        if not local_path.exists():
            QMessageBox.warning(
                self,
                self.tr("Fichier non trouvé"),
                self.tr("Le fichier local '{0}' n'existe pas.").format(link_path),
            )
            return

        final_relative_path = None

        # Cas 1: Le fichier est déjà dans le journal
        if self.journal_directory and local_path.is_relative_to(self.journal_directory):
            final_relative_path = local_path.relative_to(self.journal_directory)

        # Cas 2: Le fichier est en dehors du journal
        else:
            reply = QMessageBox.question(
                self,
                self.tr("Fichier hors du journal"),
                self.tr(
                    "Le fichier que vous avez sélectionné est en dehors du répertoire du journal.\n\n"
                    "Voulez-vous le copier dans le journal pour garantir la portabilité de vos notes ?"
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.No:
                # L'utilisateur veut un lien absolu, on le crée
                final_absolute_path = local_path.as_uri()
                markdown_link = f"[{link_text}]({final_absolute_path})"
                self.editor.insert_text(markdown_link)
                return

            # L'utilisateur veut copier le fichier
            notes_dir = self.journal_directory / "notes"
            attachments_dir = self.journal_directory / "attachments"
            default_dir = (
                str(notes_dir)
                if notes_dir.is_dir()
                else (
                    str(attachments_dir)
                    if attachments_dir.is_dir()
                    else str(self.journal_directory)
                )
            )

            dest_dir_str = QFileDialog.getExistingDirectory(
                self,
                self.tr("Choisir un dossier de destination dans le journal"),
                default_dir,
            )
            if not dest_dir_str:
                return  # Annulé par l'utilisateur

            dest_dir = Path(dest_dir_str)
            dest_path = dest_dir / local_path.name

            try:
                shutil.copy2(local_path, dest_path)
                final_relative_path = dest_path.relative_to(self.journal_directory)
                self.statusbar.showMessage(
                    self.tr("Fichier copié dans {0}").format(final_relative_path), 4000
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    self.tr("Erreur de copie"),
                    self.tr("Impossible de copier le fichier :\n{0}").format(e),
                )
                return

        if final_relative_path:
            # URL-encode le chemin pour gérer les espaces et caractères spéciaux
            encoded_path = quote(str(final_relative_path).replace(os.sep, "/"))
            markdown_link = f"🔗 [[[{link_text}]]]({encoded_path})"
            self.editor.insert_text(markdown_link)

    def insert_weather(self):
        """Récupère et insère la météo actuelle dans l'éditeur."""
        city = self.settings_manager.get("integrations.weather.city")
        api_key = self.settings_manager.get("integrations.weather.api_key")
        # Récupérer la langue de l'application (ex: "fr_FR" -> "fr")
        app_lang = self.settings_manager.get("app.language", "fr_FR")
        lang_code = app_lang.split("_")[0] if "_" in app_lang else app_lang
        print(f"🌍 Weather app_lang: {app_lang} lang_code: {lang_code}")

        markdown_fragment, error_message = get_weather_markdown(
            city, api_key, lang=lang_code
        )

        if error_message:
            QMessageBox.warning(
                self,
                self.tr("Erreur Météo"),
                error_message,
            )
            return

        if markdown_fragment:
            self.editor.insert_text(markdown_fragment)
            self.statusbar.showMessage(self.tr("Météo insérée avec succès."), 3000)

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
                self,
                self.tr("Recherche de livre par ISBN"),
                self.tr("Entrez le code ISBN du livre:"),
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
                self.tr("Configuration requise"),
                self.tr(
                    "Veuillez configurer votre ville dans 'Préférences > Intégrations' "
                    "pour utiliser cette fonctionnalité."
                ),
            )
            return

        # Afficher un message d'attente
        self.statusbar.showMessage(
            self.tr("Récupération des données astronomiques..."), 0
        )

        worker = SunMoonWorker(city, latitude, longitude)
        worker.signals.finished.connect(self.on_sun_moon_finished)
        worker.signals.error.connect(self.on_sun_moon_error)
        self.thread_pool.start(worker)

    def on_sun_moon_finished(self, html_fragment):
        """Insère le fragment Markdown des données astro."""
        self.statusbar.clearMessage()
        self.editor.insert_text(f"\n{html_fragment}\n")
        self.statusbar.showMessage(self.tr("Données astronomiques insérées."), 3000)

    def on_sun_moon_error(self, error_message):
        """Affiche une erreur si la recherche astro a échoué."""
        self.statusbar.clearMessage()
        QMessageBox.critical(self, self.tr("Erreur Astro"), error_message)

    def _create_book_worker(self, isbn, has_selection):
        """Crée et retourne un worker pour la recherche de livre."""
        return BookWorker(isbn, has_selection)

    def on_book_search_finished(self, markdown_fragment, has_selection):
        """Insère le fragment Markdown du livre dans l'éditeur."""
        self._stop_book_search_flashing()
        if has_selection:
            self.editor.text_edit.textCursor().removeSelectedText()
        self.editor.insert_text(f"\n{markdown_fragment}\n")
        self.statusbar.showMessage(
            self.tr("Informations du livre insérées avec succès."), 5000
        )

    def on_book_search_error(self, error_message):
        """Affiche une erreur si la recherche de livre a échoué."""
        self._stop_book_search_flashing()
        self.statusbar.clearMessage()
        QMessageBox.critical(self, self.tr("Erreur de recherche"), error_message)

    def on_transcript_finished(self, transcript, lang):
        """Callback quand une transcription est trouvée."""
        self._stop_transcript_flashing()
        if not transcript:
            return

        reply = QMessageBox.question(
            self,
            self.tr("Transcription trouvée"),
            self.tr(
                "Une transcription en '{0}' existe pour cette vidéo. Voulez-vous l'ajouter ?"
            ).format(lang),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            transcript_header = self.tr("\n\n**Transcription de la video Youtube**\n\n")
            full_transcript_block = transcript_header + transcript
            self.editor.insert_text(f"\n{full_transcript_block}\n")

    def on_transcript_error(self, error_message):
        """Callback en cas d'erreur de transcription."""
        self._stop_transcript_flashing()
        QMessageBox.warning(
            self,
            self.tr("Erreur de Transcription"),
            error_message,
        )

    def on_no_transcript(self):
        """Callback quand aucune transcription n'est trouvée."""
        self._stop_transcript_flashing()
        # Pas de message à l'utilisateur, c'est un comportement normal
        print(f"ℹ️ No transcript found for this video.")

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
        """Démarre le clignotement pendant une sauvegarde de journal"""
        self.backup_status_label.setVisible(True)
        self.backup_flash_timer.start()

    def _stop_backup_flashing(self):
        """Arrête le clignotement à la fin de la sauvegarde"""
        self.backup_flash_timer.stop()
        self.backup_status_label.setVisible(False)
        # V4.1.6 Fix Issue: Ensure "Veuillez patienter" is also hidden
        self.pdf_status_label.setVisible(False)

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

    def _start_transcript_flashing(self):
        """Démarre le message clignotant pour la transcription."""
        self.transcript_status_label.setVisible(True)
        self.transcript_flash_timer.start()

    def _stop_transcript_flashing(self):
        """Arrête le message clignotant de transcription."""
        self.transcript_flash_timer.stop()
        self.transcript_status_label.setVisible(False)

    def _toggle_transcript_status_visibility(self):
        """Bascule la visibilité du label de statut de transcription."""
        self.transcript_status_label.setVisible(
            not self.transcript_status_label.isVisible()
        )

    def _start_bookmark_flashing(self):
        """Démarre le message clignotant pour la vérification d'URL."""
        self.bookmark_status_label.setVisible(True)
        self.bookmark_flash_timer.start()

    def _stop_bookmark_flashing(self):
        """Arrête le message clignotant de vérification d'URL."""
        self.bookmark_flash_timer.stop()
        self.bookmark_status_label.setVisible(False)

    def _toggle_bookmark_status_visibility(self):
        """Bascule la visibilité du label de statut de vérification d'URL."""
        self.bookmark_status_label.setVisible(
            not self.bookmark_status_label.isVisible()
        )

    def _start_url_convert_flashing(self):
        """Démarre le message clignotant pour la conversion URL."""
        self.url_convert_status_label.setVisible(True)
        self.url_convert_flash_timer.start()

    def _stop_url_convert_flashing(self):
        """Arrête le message clignotant de conversion URL."""
        self.url_convert_flash_timer.stop()
        self.url_convert_status_label.setVisible(False)

    def _toggle_url_convert_status_visibility(self):
        """Bascule la visibilité du label de statut de conversion URL."""
        self.url_convert_status_label.setVisible(
            not self.url_convert_status_label.isVisible()
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
            self,
            self.tr("Conversion terminée"),
            self.tr("Le fichier PDF a été converti avec succès."),
        )

    def on_pdf_convert_error(self, error_message):
        """Callback en cas d'erreur de conversion PDF."""
        self._stop_pdf_convert_flashing()
        QMessageBox.critical(self, self.tr("Erreur de conversion"), error_message)

    def _on_journal_backup_finished(self, backup_path: str):
        """Slot appelé lorsque la sauvegarde du journal est terminée avec succès."""
        self._stop_backup_flashing()
        QMessageBox.information(
            self,
            self.tr("Sauvegarde terminée"),
            self.tr("Le journal a été sauvegardé avec succès dans :\n{0}").format(
                backup_path
            ),
        )
        print(f"🔁 Log backup successfully completed in: {backup_path}")

    def _on_journal_backup_error(self, error_message: str):
        """Slot appelé en cas d'erreur lors de la sauvegarde du journal."""
        self._stop_backup_flashing()
        QMessageBox.critical(self, self.tr("Erreur de sauvegarde"), error_message)

    def start_task(self, message):
        """Démarre un message de tâche de fond clignotant."""
        self.task_status_label.setText(message)
        self.task_status_label.setVisible(True)
        self.task_flash_timer.start()

    def stop_task(self):
        """Arrête le message de tâche de fond clignotant."""
        self.task_flash_timer.stop()
        self.task_status_label.setVisible(False)

    def _toggle_task_status_visibility(self):
        self.task_status_label.setVisible(not self.task_status_label.isVisible())

    def on_task_error(self, error_message):
        self.stop_task()
        QMessageBox.critical(self, self.tr("Erreur de tâche"), error_message)

    def convert_url_to_markdown(self):
        """Gère la conversion d'une URL/HTML en Markdown."""
        if not self.check_save_changes():
            return

        cursor = self.editor.text_edit.textCursor()
        selected_text = cursor.selectedText().strip()

        run_url_to_markdown_conversion(self, initial_url=selected_text)

    def convert_url_to_markdown_from_notes(self, directory):
        """Gère la conversion URL -> MD depuis le panneau de notes."""
        if not self.check_save_changes():
            return
        run_url_to_markdown_conversion(self, initial_url="", default_save_dir=directory)

    def on_url_to_markdown_finished(self, markdown_content, output_file_path):
        """Slot appelé lorsque la conversion URL -> MD est terminée."""
        self.stop_task()

        # V4.1.5 Fix Issue #140: Force .md extension
        path_obj = Path(output_file_path)
        if path_obj.suffix.lower() != ".md":
            output_file_path = str(path_obj.with_suffix(".md"))

        try:
            with open(output_file_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            QMessageBox.information(
                self,
                self.tr("Conversion terminée"),
                self.tr("La page a été convertie et sauvegardée dans :\n{0}").format(
                    output_file_path
                ),
            )
            self.open_specific_file(output_file_path)
        except Exception as e:
            pass

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

        from integrations.pdf_converter import PdfToMarkdownWorker

        worker = PdfToMarkdownWorker(pdf_path)
        worker.signals.finished.connect(self.on_pdf_convert_finished)
        worker.signals.error.connect(self.on_pdf_convert_error)

        self.thread_pool.start(worker)

    def convert_pdf_to_markdown_from_notes(self, directory):
        """Gère la conversion PDF -> MD depuis le panneau de notes."""
        if not self.check_save_changes():
            return

        dialog = PdfSourceDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        pdf_path = dialog.get_path()
        if not pdf_path:
            return

        self._start_pdf_convert_flashing()

        from integrations.pdf_converter import PdfToMarkdownWorker

        worker = PdfToMarkdownWorker(pdf_path)
        worker.signals.finished.connect(
            lambda content: self.on_pdf_convert_from_notes_finished(
                content, directory, pdf_path
            )
        )
        worker.signals.error.connect(self.on_pdf_convert_error)

        self.thread_pool.start(worker)

    def on_pdf_convert_from_notes_finished(self, markdown_content, directory, pdf_path):
        """Slot appelé lorsque la conversion PDF -> MD depuis notes est terminée."""
        self._stop_pdf_convert_flashing()

        pdf_name = Path(pdf_path).stem
        default_path = os.path.join(directory, f"{pdf_name}.md")

        destination_path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("Sauvegarder le fichier Markdown"),
            default_path,
            self.tr("Fichiers Markdown (*.md)"),
        )

        if not destination_path:
            return

        try:
            with open(destination_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            QMessageBox.information(
                self,
                self.tr("Conversion terminée"),
                self.tr(
                    "Le fichier PDF a été converti et sauvegardé dans :\n{0}"
                ).format(destination_path),
            )
            self.open_specific_file(destination_path)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Erreur"), str(e))

    def _on_journal_backup_finished(self, backup_path: str):
        """Slot appelé lorsque la sauvegarde du journal est terminée avec succès."""
        self._stop_backup_flashing()
        QMessageBox.information(
            self,
            "Sauvegarde terminée",
            f"Le journal a été sauvegardé avec succès dans :\n{backup_path}",
        )
        print(f"🔁 Log backup successfully completed in: {backup_path}")

    def _on_journal_backup_error(self, error_message: str):
        """Slot appelé en cas d'erreur lors de la sauvegarde du journal."""
        self._stop_backup_flashing()
        QMessageBox.critical(self, "Erreur de sauvegarde", error_message)

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

    def refresh_tag_index(self, event):
        """Rafraîchit l'index des tags sur demande de l'utilisateur."""
        if event.button() == Qt.LeftButton:
            print(f"🔄 Manual refresh of tag index requested.")
            self.tag_index_status_label.setText(self.tr("Indexation en cours..."))
            # Force l'interface à se mettre à jour avant de lancer la tâche de fond
            self.tag_index_status_label.repaint()
            self.start_initial_indexing()

    def refresh_tag_index_from_nav(self):
        """Rafraîchit l'index des tags sur demande depuis le panneau de navigation."""
        print(f"🔄 Manually refresh the tag index requested from the navigation.")

        self.tag_index_status_label.setText(self.tr("Indexation en cours..."))
        self.tag_index_status_label.repaint()
        self.start_initial_indexing()

    def on_indexing_finished(self, unique_tag_count):
        """Callback exécuté à la fin de l'indexation."""
        self.tag_index_count = unique_tag_count
        self.update_indexing_status_label()

        # V3.1.1 - Lancer la recherche par défaut sur @@TODO après l'indexation
        self.perform_search("@@TODO")

    def update_indexing_status_label(self):
        """Met à jour la barre de statut avec les résultats des deux indexations."""
        # Now only checks for tag index count
        if self.tag_index_count == -1:
            return

        tag_msg = self.tr("{0} tags").format(self.tag_index_count)
        full_message = self.tr("Index: {0}").format(tag_msg)
        print(f"✅ {full_message}")
        self.tag_index_status_label.setText(full_message)

        if not self.settings_manager.get("ui.show_indexing_stats", True):
            QTimer.singleShot(15000, lambda: self.tag_index_status_label.clear())

        self.update_tag_cloud()
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
            self.tr("Aucune note précédente trouvée dans le journal."), 3000
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
            self.tr("Aucune note suivante trouvée dans le journal."), 3000
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
                self.tr("Aucune note pour le {0}").format(date.toString("dd/MM/yyyy")),
                3000,
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
                f"❌ Journal directory not found for calendar update: {self.journal_directory}"
            )
        self.update_tag_cloud()

    def _set_styled_label_font(self, label, color, underline=False):
        """Applique un style à un QLabel tout en conservant la police système."""
        # V3.3.8 - Helper pour s'assurer que la police système est respectée
        from PyQt5.QtWidgets import QApplication

        app_font = QApplication.font()
        label.setFont(app_font)
        style = f"color: {color};"
        if underline:
            style += " text-decoration: underline;"
        label.setStyleSheet(style)

    def _set_file_label_color(self, color):
        """Définit la couleur du texte pour le label du nom de fichier."""
        # V3.3.8 - Appliquer la police système pour éviter les overrides de style
        from PyQt5.QtWidgets import QApplication

        app_font = QApplication.font()
        self.file_label.setFont(app_font)
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
                "ui.show_navigation_panel", dialog.show_nav_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_outline_panel", dialog.show_outline_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_preview_panel", dialog.show_preview_checkbox.isChecked()
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
                "integrations.youtube_transcript_enabled",
                dialog.youtube_transcript_checkbox.isChecked(),
            )

            self.settings_manager.set(
                "ui.show_indexing_stats",
                dialog.show_indexing_stats_checkbox.isChecked(),
            )

            excluded_tags_text = dialog.excluded_tags_edit.toPlainText()
            excluded_tags_list = [
                tag.strip().lower()
                for tag in excluded_tags_text.split(",")
                if tag.strip()
            ]
            self.settings_manager.set(
                "indexing.excluded_tags_from_cloud", excluded_tags_list
            )
            # V3.3.8 - Sauvegarde des paramètres de police de l'application
            self.settings_manager.set(
                "ui.app_font_family", dialog.current_app_font.family()
            )
            self.settings_manager.set(
                "ui.app_font_size", dialog.current_app_font.pointSize()
            )
            QMessageBox.information(
                self,
                self.tr("Redémarrage requis"),
                self.tr(
                    "Certains changements, comme la police de l'application, nécessitent un redémarrage pour être pleinement appliqués."
                ),
            )

            self.settings_manager.save_settings()
            self.apply_settings()

    def save_panel_visibility_settings(self):
        """Sauvegarde l'état de visibilité actuel des panneaux."""
        self.settings_manager.set("ui.show_notes_panel", self.notes_panel.isVisible())
        self.settings_manager.set(
            "ui.show_navigation_panel", self.navigation_panel.isVisible()
        )
        self.settings_manager.set(
            "ui.show_outline_panel", self.outline_panel.isVisible()
        )
        self.settings_manager.set("ui.show_preview_panel", self.preview.isVisible())
        self.settings_manager.set(
            "ui.show_reader_panel", self.epub_reader_panel.isVisible()
        )
        self.settings_manager.save_settings()

    def apply_settings(self):
        """Applique les paramètres chargés à l'interface utilisateur."""
        # Récupérer l'état des panneaux depuis les paramètres
        show_notes = self.settings_manager.get("ui.show_notes_panel", True)
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        show_outline = self.settings_manager.get("ui.show_outline_panel", False)
        show_preview = self.settings_manager.get("ui.show_preview_panel", True)
        show_reader = self.settings_manager.get("ui.show_reader_panel", False)

        # Bloquer temporairement les signaux pour éviter les appels en cascade
        self.notes_button.blockSignals(True)
        self.nav_button.blockSignals(True)
        self.outline_button.blockSignals(True)
        self.preview_button.blockSignals(True)
        self.reader_button.blockSignals(True)

        # Appliquer la visibilité des panneaux
        self.notes_panel.setVisible(show_notes)
        self.navigation_panel.setVisible(show_nav)
        self.outline_panel.setVisible(show_outline)
        self.preview.setVisible(show_preview)
        self.epub_reader_panel.setVisible(show_reader)

        # Synchroniser les switchs avec l'état des panneaux
        self.notes_button.setChecked(show_notes)
        self.nav_button.setChecked(show_nav)
        self.outline_button.setChecked(show_outline)
        self.preview_button.setChecked(show_preview)
        self.reader_button.setChecked(show_reader)

        # Débloquer les signaux
        self.notes_button.blockSignals(False)
        self.nav_button.blockSignals(False)
        self.outline_button.blockSignals(False)
        self.preview_button.blockSignals(False)
        self.reader_button.blockSignals(False)

        # V3.3.8 - Police globale appliquée au démarrage dans main.py
        # Ne pas réappliquer ici pour éviter de réinitialiser les traductions
        app = QApplication.instance()
        if app:
            app_font_family = self.settings_manager.get(
                "ui.app_font_family", app.font().family()
            )
            app_font_size = self.settings_manager.get(
                "ui.app_font_size", app.font().pointSize()
            )
            global_font = QFont(app_font_family, app_font_size)
            # app.setFont(global_font)  # <-- COMMENTÉ : fait dans main.py
            self.setFont(global_font)  # Appliquer seulement à la fenêtre principale
            print(f"ℹ️ Modified font --")

        self.toggle_notes_action.setChecked(show_notes)
        self.toggle_navigation_action.setChecked(show_nav)
        self.toggle_outline_action.setChecked(show_outline)
        self.toggle_preview_action.setChecked(show_preview)

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

        youtube_transcript_enabled = self.settings_manager.get(
            "integrations.youtube_transcript_enabled", True
        )
        # L'action globale dépend des deux settings
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

    def perform_search(self, query: str):
        """Effectue une recherche dans les index et affiche les résultats."""
        if not query or not self.journal_directory:
            self.perform_search(
                "@@TODO"
            )  # Si la recherche est vide, afficher les TODO par défaut
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
                        break  # Break from the inner loop after finding the tag
        # If query is not a tag, it will not be processed further

        self.navigation_panel.show_search_results(results, query)

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
                self,
                self.tr("Fichier non trouvé"),
                self.tr("Le fichier '{0}' n'existe plus.").format(filename),
            )

    def open_file_from_notes(self, file_path: str, open_with: str):
        """Ouvre un fichier sélectionné depuis le panneau de notes."""
        if not self.check_save_changes():
            return

        if open_with == "editor":
            self.open_specific_file(file_path)
        elif open_with == "reader":
            self.epub_reader_panel.load_document(file_path)
            if not self.epub_reader_panel.isVisible():
                self.epub_reader_panel.show()
                self._sync_panel_controls()
        elif open_with == "external":
            webbrowser.open(f"file:///{os.path.abspath(file_path)}")
        else:
            QMessageBox.warning(
                self,
                self.tr("Fichier non trouvé"),
                self.tr("Le fichier '{0}' n'existe plus.").format(filename),
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
                print(f"❌ Error reading the tag index for the menu: {e}")

        self.navigation_panel.set_available_tags(tags_list)

    def expand_outline(self):
        """Déplie entièrement l'arborescence du plan du document."""
        self.outline_panel.tree_widget.expandAll()

    def on_notes_dir_selected(self, dir_path):
        """Sauvegarde le dernier répertoire sélectionné dans le panneau de notes."""
        self.settings_manager.set("notes.last_selected_dir", dir_path)

    def closeEvent(self, event):
        """Gère la fermeture propre de l'application."""
        if not self.check_save_changes():
            event.ignore()
            return

        # V4.2.0 - Nettoyage explicite pour éviter l'erreur "WebEnginePage still not deleted"
        self.preview.cleanup()
        self.epub_reader_panel.close()

        # V3.2.1 - Sauvegarde des derniers réglages
        if self.epub_reader_panel.has_document():
            self.settings_manager.set("reader.last_document", self.last_document_reader)
        if self.notes_panel.tree_view.currentIndex().isValid():
            source_index = self.notes_panel.proxy_model.mapToSource(
                self.notes_panel.tree_view.currentIndex()
            )
            last_dir = self.notes_panel.model.filePath(source_index)
            self.settings_manager.set("notes.last_selected_dir", last_dir)

        # Sauvegarder la géométrie et l'état de la fenêtre
        self.settings_manager.set("window.geometry", self.saveGeometry().data().hex())
        self.settings_manager.set("window.state", self.saveState().data().hex())

        # Sauvegarder la visibilité des panneaux
        self.settings_manager.set("ui.show_notes_panel", self.notes_panel.isVisible())
        self.settings_manager.set(
            "ui.show_navigation_panel", self.navigation_panel.isVisible()
        )
        self.settings_manager.set(
            "ui.show_outline_panel", self.outline_panel.isVisible()
        )
        self.settings_manager.set("ui.show_preview_panel", self.preview.isVisible())
        self.settings_manager.set(
            "ui.show_reader_panel", self.epub_reader_panel.isVisible()
        )

        self.settings_manager.save_settings()

        event.accept()

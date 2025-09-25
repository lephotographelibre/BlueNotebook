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

Boîte de dialogue pour les préférences de BlueNotebook.
"""

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTabWidget,
    QWidget,
    QFormLayout,
    QFontDialog,
    QPushButton,
    QColorDialog,
    QCheckBox,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
)
from PyQt5.QtGui import QFont, QColor


class PreferencesDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Préférences")
        self.setMinimumWidth(500)

        # Créer les onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_general_tab(), "Général")
        self.tabs.addTab(self._create_display_tab(), "Affichage")
        self.tabs.addTab(self._create_integrations_tab(), "Intégrations")

        # Boutons Valider/Annuler
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText("Valider")
        self.button_box.button(QDialogButtonBox.Cancel).setText("Annuler")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tabs)
        main_layout.addWidget(self.button_box)
        self.setLayout(main_layout)

    def _create_general_tab(self):
        """Crée l'onglet 'Général'."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Police de l'éditeur
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        self.current_font = QFont(font_family, font_size)

        self.font_button = QPushButton(f"{font_family}, {font_size}pt")
        self.font_button.clicked.connect(self._select_font)
        layout.addRow("Police de l'éditeur:", self.font_button)

        # Bouton de réinitialisation
        reset_button = QPushButton("Remise à 0")
        reset_button.setToolTip(
            "Réinitialise toutes les préférences à leurs valeurs par défaut."
        )
        reset_button.clicked.connect(self._reset_settings)
        layout.addRow(reset_button)

        return widget

    def _create_display_tab(self):
        """Crée l'onglet 'Affichage'."""
        widget = QWidget()
        layout = QFormLayout(widget)

        # Couleur de fond de l'éditeur
        color_hex = self.settings_manager.get("editor.background_color")
        self.current_color = QColor(color_hex)

        self.color_button = QPushButton()
        self.color_button.setStyleSheet(f"background-color: {color_hex};")
        self.color_button.clicked.connect(self._select_color)
        layout.addRow("Couleur de fond de l'éditeur:", self.color_button)

        # Couleur du texte de l'éditeur
        text_color_hex = self.settings_manager.get("editor.text_color")
        self.current_text_color = QColor(text_color_hex)

        self.text_color_button = QPushButton()
        self.text_color_button.setStyleSheet(f"background-color: {text_color_hex};")
        self.text_color_button.clicked.connect(self._select_text_color)
        layout.addRow("Couleur de la police de l'éditeur:", self.text_color_button)

        return widget

    def _create_integrations_tab(self):
        """Crée l'onglet 'Intégrations'."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.show_quote_checkbox = QCheckBox(
            "Afficher la citation du jour au démarrage"
        )
        is_checked = self.settings_manager.get("integrations.show_quote_of_the_day")
        self.show_quote_checkbox.setChecked(is_checked)
        layout.addWidget(self.show_quote_checkbox)

        return widget

    def _select_font(self):
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            self.font_button.setText(f"{font.family()}, {font.pointSize()}pt")

    def _select_color(self):
        color = QColorDialog.getColor(self.current_color, self)
        if color.isValid():
            self.current_color = color
            self.color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_text_color(self):
        color = QColorDialog.getColor(self.current_text_color, self)
        if color.isValid():
            self.current_text_color = color
            self.text_color_button.setStyleSheet(f"background-color: {color.name()};")

    # Fix Claude V1.4.1
    def _reset_settings(self):
        """Affiche une confirmation et réinitialise les paramètres."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir réinitialiser toutes les préférences aux valeurs par défaut ?\n"
            "L'application devra être redémarrée pour appliquer tous les changements.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.settings_manager.reset_to_defaults()
            QMessageBox.information(
                self, "Préférences réinitialisées", "Veuillez redémarrer l'application."
            )
            # IMPORTANT: Utiliser reject() au lieu de accept() pour éviter de sauvegarder
            # les valeurs actuelles du dialogue par-dessus les valeurs par défaut
            self.reject()  # Ferme la boîte de dialogue sans déclencher la sauvegarde

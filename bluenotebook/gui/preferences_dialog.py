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
    QTextEdit,
    QMessageBox,
    QFontComboBox,
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


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
        self.tabs.addTab(self._create_panels_tab(), "Panneaux")
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
        layout.setSpacing(10)

        # Case pour l'affichage des statistiques d'indexation
        self.show_indexing_stats_checkbox = QCheckBox(
            "Afficher les statistiques d'indexation (mots et tags) dans la barre d'état"
        )
        self.show_indexing_stats_checkbox.setChecked(
            self.settings_manager.get("ui.show_indexing_stats", True)
        )
        layout.addRow(self.show_indexing_stats_checkbox)

        # Mots à exclure de l'indexation
        user_excluded_words = self.settings_manager.get(
            "indexing.user_excluded_words", []
        )
        self.excluded_words_edit = QTextEdit()
        self.excluded_words_edit.setPlainText(", ".join(sorted(user_excluded_words)))
        self.excluded_words_edit.setToolTip(
            "Ajoutez ici des mots personnalisés (séparés par des virgules) à ignorer lors de l'indexation."
        )
        self.excluded_words_edit.setMinimumHeight(150)

        label = QLabel("Mots personnalisés à exclure de l'indexation:")
        label.setToolTip(
            "Ces mots (en minuscules) ne seront pas inclus dans les fichiers d'index de mots."
        )
        layout.addRow(label, self.excluded_words_edit)

        # V1.6.2 Tags à exclure du nuage
        excluded_tags_list = self.settings_manager.get(
            "indexing.excluded_tags_from_cloud", []
        )
        self.excluded_tags_edit = QTextEdit()
        self.excluded_tags_edit.setPlainText(", ".join(sorted(excluded_tags_list)))
        self.excluded_tags_edit.setToolTip(
            "Liste de tags (sans @@, séparés par des virgules) à ne pas afficher dans le nuage de tags."
        )
        self.excluded_tags_edit.setMaximumHeight(80)

        label_tags = QLabel("Tags à exclure du nuage:")
        label_tags.setToolTip(
            "Ces tags n'apparaîtront pas dans le panneau 'Nuage de Tags'."
        )
        layout.addRow(label_tags, self.excluded_tags_edit)

        # Mots à exclure du nuage de mots
        excluded_words_cloud_list = self.settings_manager.get(
            "indexing.excluded_words_from_cloud", []
        )
        self.excluded_words_cloud_edit = QTextEdit()
        self.excluded_words_cloud_edit.setPlainText(
            ", ".join(sorted(excluded_words_cloud_list))
        )
        self.excluded_words_cloud_edit.setToolTip(
            "Liste de mots (séparés par des virgules) à ne pas afficher dans le nuage de mots."
        )
        self.excluded_words_cloud_edit.setMaximumHeight(80)

        label_words_cloud = QLabel("Mots à exclure du nuage de mots:")
        label_words_cloud.setToolTip(
            "Ces mots n'apparaîtront pas dans le panneau 'Nuage de Mots'."
        )
        layout.addRow(label_words_cloud, self.excluded_words_cloud_edit)

        return widget

    def _create_display_tab(self):
        """Crée l'onglet 'Affichage'."""
        widget = QWidget()
        layout = QFormLayout(widget)
        layout.setSpacing(15)

        # Police de l'éditeur (déplacé depuis l'onglet Général)
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        self.current_font = QFont(font_family, font_size)

        self.font_button = QPushButton(f"{font_family}, {font_size}pt")
        self.font_button.clicked.connect(self._select_font)
        layout.addRow("Police de l'éditeur:", self.font_button)

        # V1.7.2 Ajout Paramètre Affichages Couleurs
        # Police pour le code
        code_font_family = self.settings_manager.get(
            "editor.code_font_family", "Consolas, Monaco, monospace"
        )
        self.current_code_font = QFont(code_font_family)

        self.code_font_button = QPushButton(f"{code_font_family}")
        self.code_font_button.setToolTip(
            "Choisir la police pour le code inline et les blocs de code."
        )
        self.code_font_button.clicked.connect(self._select_code_font)
        layout.addRow("Police des extraits de code:", self.code_font_button)

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

        # Couleur des titres
        heading_color_hex = self.settings_manager.get("editor.heading_color")
        self.current_heading_color = QColor(heading_color_hex)
        self.heading_color_button = QPushButton()
        self.heading_color_button.setStyleSheet(
            f"background-color: {heading_color_hex};"
        )
        self.heading_color_button.clicked.connect(self._select_heading_color)
        layout.addRow("Couleur des titres Markdown:", self.heading_color_button)

        # Couleur des listes
        list_color_hex = self.settings_manager.get(
            "editor.list_color", self.settings_manager.get("editor.heading_color")
        )
        self.current_list_color = QColor(list_color_hex)
        self.list_color_button = QPushButton()
        self.list_color_button.setStyleSheet(f"background-color: {list_color_hex};")
        self.list_color_button.clicked.connect(self._select_list_color)
        layout.addRow("Couleur des listes Markdown:", self.list_color_button)

        # Couleur du texte sélectionné
        selection_text_color_hex = self.settings_manager.get(
            "editor.selection_text_color"
        )
        self.current_selection_text_color = QColor(selection_text_color_hex)
        self.selection_text_color_button = QPushButton()
        self.selection_text_color_button.setStyleSheet(
            f"background-color: {selection_text_color_hex};"
        )
        self.selection_text_color_button.clicked.connect(
            self._select_selection_text_color
        )
        layout.addRow("Couleur du texte sélectionné:", self.selection_text_color_button)

        # Couleur du texte du code inline
        inline_code_text_color_hex = self.settings_manager.get(
            "editor.inline_code_text_color"
        )
        self.current_inline_code_text_color = QColor(inline_code_text_color_hex)
        self.inline_code_text_color_button = QPushButton()
        self.inline_code_text_color_button.setStyleSheet(
            f"background-color: {inline_code_text_color_hex};"
        )
        self.inline_code_text_color_button.clicked.connect(
            self._select_inline_code_text_color
        )
        layout.addRow("Couleur texte code inline:", self.inline_code_text_color_button)

        # Couleur de fond du code inline
        inline_code_bg_color_hex = self.settings_manager.get(
            "editor.inline_code_background_color"
        )
        self.current_inline_code_bg_color = QColor(inline_code_bg_color_hex)
        self.inline_code_bg_color_button = QPushButton()
        self.inline_code_bg_color_button.setStyleSheet(
            f"background-color: {inline_code_bg_color_hex};"
        )
        self.inline_code_bg_color_button.clicked.connect(
            self._select_inline_code_bg_color
        )
        layout.addRow("Couleur fond code inline:", self.inline_code_bg_color_button)

        # Couleur de fond des blocs de code
        code_block_bg_color_hex = self.settings_manager.get(
            "editor.code_block_background_color"
        )
        self.current_code_block_bg_color = QColor(code_block_bg_color_hex)
        self.code_block_bg_color_button = QPushButton()
        self.code_block_bg_color_button.setStyleSheet(
            f"background-color: {code_block_bg_color_hex};"
        )
        self.code_block_bg_color_button.clicked.connect(
            self._select_code_block_bg_color
        )
        layout.addRow("Couleur fond bloc de code:", self.code_block_bg_color_button)

        # Couleur pour le gras
        bold_color_hex = self.settings_manager.get("editor.bold_color")
        self.current_bold_color = QColor(bold_color_hex)
        self.bold_color_button = QPushButton()
        self.bold_color_button.setStyleSheet(f"background-color: {bold_color_hex};")
        self.bold_color_button.clicked.connect(self._select_bold_color)
        layout.addRow("Couleur du texte en gras:", self.bold_color_button)

        # Couleur pour l'italique
        italic_color_hex = self.settings_manager.get("editor.italic_color")
        self.current_italic_color = QColor(italic_color_hex)
        self.italic_color_button = QPushButton()
        self.italic_color_button.setStyleSheet(f"background-color: {italic_color_hex};")
        self.italic_color_button.clicked.connect(self._select_italic_color)
        layout.addRow("Couleur du texte en italique:", self.italic_color_button)

        # Couleur pour le barré
        strikethrough_color_hex = self.settings_manager.get(
            "editor.strikethrough_color"
        )
        self.current_strikethrough_color = QColor(strikethrough_color_hex)
        self.strikethrough_color_button = QPushButton()
        self.strikethrough_color_button.setStyleSheet(
            f"background-color: {strikethrough_color_hex};"
        )
        self.strikethrough_color_button.clicked.connect(
            self._select_strikethrough_color
        )
        layout.addRow("Couleur du texte barré:", self.strikethrough_color_button)

        # Couleur pour le surlignage
        highlight_color_hex = self.settings_manager.get("editor.highlight_color")
        self.current_highlight_color = QColor(highlight_color_hex)
        self.highlight_color_button = QPushButton()
        self.highlight_color_button.setStyleSheet(
            f"background-color: {highlight_color_hex};"
        )
        self.highlight_color_button.clicked.connect(self._select_highlight_color)
        layout.addRow("Couleur de fond du surlignage:", self.highlight_color_button)

        # V1.7.2 Ajout Paramètre Affichages Couleurs
        # Couleur des citations
        quote_color_hex = self.settings_manager.get("editor.quote_color", "#2B303B")
        self.current_quote_color = QColor(quote_color_hex)
        self.quote_color_button = QPushButton()
        self.quote_color_button.setStyleSheet(f"background-color: {quote_color_hex};")
        self.quote_color_button.clicked.connect(self._select_quote_color)
        layout.addRow("Couleur des citations:", self.quote_color_button)

        # Couleur des liens
        link_color_hex = self.settings_manager.get("editor.link_color", "#0366d6")
        self.current_link_color = QColor(link_color_hex)
        self.link_color_button = QPushButton()
        self.link_color_button.setStyleSheet(f"background-color: {link_color_hex};")
        self.link_color_button.clicked.connect(self._select_link_color)
        layout.addRow("Couleur des liens:", self.link_color_button)
        # Fin V1.7.2

        # Couleur des commentaires HTML
        html_comment_color_hex = self.settings_manager.get(
            "editor.html_comment_color", "#a4b5cf"
        )
        self.current_html_comment_color = QColor(html_comment_color_hex)
        self.html_comment_color_button = QPushButton()
        self.html_comment_color_button.setStyleSheet(
            f"background-color: {html_comment_color_hex};"
        )
        self.html_comment_color_button.clicked.connect(self._select_html_comment_color)
        layout.addRow("Couleur des commentaires HTML:", self.html_comment_color_button)

        # Couleur pour les tags
        tag_color_hex = self.settings_manager.get("editor.tag_color")
        self.current_tag_color = QColor(tag_color_hex)
        self.tag_color_button = QPushButton()
        self.tag_color_button.setStyleSheet(f"background-color: {tag_color_hex};")
        self.tag_color_button.clicked.connect(self._select_tag_color)
        layout.addRow("Couleur des tags (@@tag):", self.tag_color_button)

        # Couleur pour l'horodatage
        timestamp_color_hex = self.settings_manager.get("editor.timestamp_color")
        self.current_timestamp_color = QColor(timestamp_color_hex)
        self.timestamp_color_button = QPushButton()
        self.timestamp_color_button.setStyleSheet(
            f"background-color: {timestamp_color_hex};"
        )
        self.timestamp_color_button.clicked.connect(self._select_timestamp_color)
        layout.addRow("Couleur de l'horodatage (HH:MM):", self.timestamp_color_button)

        # Bouton de réinitialisation (déplacé et renommé)
        reset_button = QPushButton("Valeurs par défaut")
        reset_button.setToolTip(
            "Réinitialise les préférences de l'interface (affichage, panneaux, intégrations) à leurs valeurs par défaut."
        )
        reset_button.clicked.connect(self._reset_settings)

        # Ajouter un peu d'espace avant le bouton
        layout.addRow(QLabel(""))  # Ligne vide pour l'espacement
        layout.addRow(reset_button)

        return widget

    def _create_panels_tab(self):
        """Crée l'onglet 'Panneaux' pour gérer la visibilité au démarrage."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Case pour le panneau de Navigation
        self.show_nav_checkbox = QCheckBox("Afficher le panneau de Navigation")
        self.show_nav_checkbox.setChecked(
            self.settings_manager.get("ui.show_navigation_panel", False)
        )
        layout.addWidget(self.show_nav_checkbox)

        # Case pour le panneau Plan du document
        self.show_outline_checkbox = QCheckBox("Afficher le panneau 'Plan du document'")
        self.show_outline_checkbox.setChecked(
            self.settings_manager.get("ui.show_outline_panel", True)
        )
        layout.addWidget(self.show_outline_checkbox)

        # Case pour le panneau Éditeur (toujours visible et désactivé)
        self.show_editor_checkbox = QCheckBox("Afficher le panneau Éditeur")
        self.show_editor_checkbox.setChecked(True)
        self.show_editor_checkbox.setEnabled(False)
        layout.addWidget(self.show_editor_checkbox)

        # Case pour le panneau Aperçu HTML
        self.show_preview_checkbox = QCheckBox("Afficher le panneau 'Aperçu HTML'")
        self.show_preview_checkbox.setChecked(
            self.settings_manager.get("ui.show_preview_panel", False)
        )
        layout.addWidget(self.show_preview_checkbox)

        layout.addStretch()  # Pour pousser les cases vers le haut
        return widget

    def _create_integrations_tab(self):
        """Crée l'onglet 'Intégrations'."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.show_quote_checkbox = QCheckBox(
            "Afficher la citation du jour au démarrage"
        )
        # V1.4.2 Fix bug Crash if show_quote_of_the_day is false - set a default value
        # is_checked = self.settings_manager.get("integrations.show_quote_of_the_day")
        is_checked = self.settings_manager.get(
            "integrations.show_quote_of_the_day", False
        )
        self.show_quote_checkbox.setChecked(is_checked)
        layout.addWidget(self.show_quote_checkbox)

        return widget

    def _select_font(self):
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            self.font_button.setText(f"{font.family()}, {font.pointSize()}pt")

    # V1.7.2 Ajout Paramètre Affichages Couleurs
    def _select_code_font(self):
        """Sélectionne la police pour le code."""
        font, ok = QFontDialog.getFont(self.current_code_font, self)
        if ok:
            self.current_code_font = font
            self.code_font_button.setText(font.family())

    def _select_quote_color(self):
        """Sélectionne la couleur pour les citations."""
        color = QColorDialog.getColor(self.current_quote_color, self)
        if color.isValid():
            self.current_quote_color = color
            self.quote_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_link_color(self):
        """Sélectionne la couleur pour les liens."""
        color = QColorDialog.getColor(self.current_link_color, self)
        if color.isValid():
            self.current_link_color = color
            self.link_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_html_comment_color(self):
        """Sélectionne la couleur pour les commentaires HTML."""
        color = QColorDialog.getColor(self.current_html_comment_color, self)
        if color.isValid():
            self.current_html_comment_color = color
            self.html_comment_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    # Fin V1.7.2

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

    def _select_heading_color(self):
        color = QColorDialog.getColor(self.current_heading_color, self)
        if color.isValid():
            self.current_heading_color = color
            self.heading_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_list_color(self):
        """Sélectionne la couleur pour les listes."""
        color = QColorDialog.getColor(self.current_list_color, self)
        if color.isValid():
            self.current_list_color = color
            self.list_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_selection_text_color(self):
        color = QColorDialog.getColor(self.current_selection_text_color, self)
        if color.isValid():
            self.current_selection_text_color = color
            self.selection_text_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_inline_code_text_color(self):
        """Sélectionne la couleur pour le texte du code inline."""
        color = QColorDialog.getColor(self.current_inline_code_text_color, self)
        if color.isValid():
            self.current_inline_code_text_color = color
            self.inline_code_text_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_inline_code_bg_color(self):
        """Sélectionne la couleur pour le fond du code inline."""
        color = QColorDialog.getColor(self.current_inline_code_bg_color, self)
        if color.isValid():
            self.current_inline_code_bg_color = color
            self.inline_code_bg_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_code_block_bg_color(self):
        """Sélectionne la couleur pour le fond des blocs de code."""
        color = QColorDialog.getColor(self.current_code_block_bg_color, self)
        if color.isValid():
            self.current_code_block_bg_color = color
            self.code_block_bg_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_bold_color(self):
        """Sélectionne la couleur pour le texte en gras."""
        color = QColorDialog.getColor(self.current_bold_color, self)
        if color.isValid():
            self.current_bold_color = color
            self.bold_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_italic_color(self):
        """Sélectionne la couleur pour le texte en italique."""
        color = QColorDialog.getColor(self.current_italic_color, self)
        if color.isValid():
            self.current_italic_color = color
            self.italic_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_strikethrough_color(self):
        """Sélectionne la couleur pour le texte barré."""
        color = QColorDialog.getColor(self.current_strikethrough_color, self)
        if color.isValid():
            self.current_strikethrough_color = color
            self.strikethrough_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_highlight_color(self):
        """Sélectionne la couleur pour le fond du surlignage."""
        color = QColorDialog.getColor(self.current_highlight_color, self)
        if color.isValid():
            self.current_highlight_color = color
            self.highlight_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    def _select_tag_color(self):
        """Sélectionne la couleur pour les tags."""
        color = QColorDialog.getColor(self.current_tag_color, self)
        if color.isValid():
            self.current_tag_color = color
            self.tag_color_button.setStyleSheet(f"background-color: {color.name()};")

    def _select_timestamp_color(self):
        """Sélectionne la couleur pour l'horodatage."""
        color = QColorDialog.getColor(self.current_timestamp_color, self)
        if color.isValid():
            self.current_timestamp_color = color
            self.timestamp_color_button.setStyleSheet(
                f"background-color: {color.name()};"
            )

    # Fix Claude V1.4.1
    def _reset_settings(self):
        """Affiche une confirmation et réinitialise les paramètres."""
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(
            """
            <p>Êtes-vous sûr de vouloir réinitialiser les préférences de l'interface ?</p>
            <p>Cela inclut :</p>
            <ul>
                <li>La police et les couleurs de l'éditeur.</li>
                <li>La visibilité par défaut des panneaux (Navigation, Plan, etc.).</li>
                <li>Les paramètres d'intégrations (ex: citation du jour).</li>
            </ul>
            <p>L'application devra être redémarrée pour appliquer les changements.</p>
        """
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Valider")
        msg_box.button(QMessageBox.No).setText("Annuler")
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            self.settings_manager.reset_gui_settings_to_defaults()
            QMessageBox.information(
                self, "Préférences réinitialisées", "Veuillez redémarrer l'application."
            )
            # IMPORTANT: Utiliser reject() au lieu de accept() pour éviter de sauvegarder
            # les valeurs actuelles du dialogue par-dessus les valeurs par défaut
            self.reject()  # Ferme la boîte de dialogue sans déclencher la sauvegarde

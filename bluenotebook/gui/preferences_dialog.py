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

import os
import json
from PyQt5.QtWebEngineWidgets import QWebEngineView
import re
from pathlib import Path
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
    QGridLayout,
    QScrollArea,
    QInputDialog,
    QFileDialog,
    QLineEdit,
    QComboBox,
)
from PyQt5.QtCore import QDir
from geopy.geocoders import Nominatim
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

SAMPLE_HTML_FOR_PREVIEW = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {css_content}
    </style>
</head>
<body>
    <h1>Titre de niveau 1</h1>
    <h2>Titre de niveau 2</h2>
    <p>Ceci est un paragraphe de texte normal. Il contient un <a href="#">lien hypertexte</a> pour voir le style des liens. Il contient aussi du <code>code en ligne</code>.</p>
    <blockquote><p>Ceci est une citation. Elle est souvent utilisée pour mettre en évidence une pensée importante.</p></blockquote>
    <pre><code># Bloc de code
def hello_world():
    print("Hello, World!")
    </code></pre>
    <hr>
    <table><thead><tr><th>En-tête 1</th><th>En-tête 2</th></tr></thead><tbody><tr><td>Cellule 1</td><td>Cellule 2</td></tr><tr><td>Cellule 3</td><td>Cellule 4</td></tr></tbody></table>
</body>
</html>
"""


class PreferencesDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle(self.tr("Préférences"))
        self.setMinimumWidth(1050)  # Largeur augmentée pour un affichage optimal
        self.setMinimumHeight(850)  # Hauteur minimale augmentée

        # Charger le thème CSS de l'aperçu actuel AVANT de créer les onglets
        self.selected_html_theme = self.settings_manager.get(
            "preview.css_theme", "default_preview.css"
        )
        self.selected_pdf_theme = self.settings_manager.get(
            "pdf.css_theme", "default_preview.css"
        )

        # Créer les onglets
        self.tabs = QTabWidget()
        self.tabs.addTab(self._create_general_tab(), self.tr("Général"))
        self.tabs.addTab(self._create_display_tab(), self.tr("Affichage"))
        self.tabs.addTab(self._create_panels_tab(), self.tr("Panneaux"))
        self.tabs.addTab(self._create_integrations_tab(), self.tr("Intégrations"))

        # Boutons Valider/Annuler
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.button(QDialogButtonBox.Ok).setText(self.tr("Valider"))
        self.button_box.button(QDialogButtonBox.Cancel).setText(self.tr("Annuler"))
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
        layout = QGridLayout(widget)
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1)

        # --- Langue de l'application ---
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([self.tr("Français"), self.tr("English")])
        current_lang = self.settings_manager.get("app.language", "fr_FR")
        if current_lang == "en_US":
            self.lang_combo.setCurrentIndex(1)
        else:
            self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setToolTip(
            self.tr("Définit la langue de l'interface. Un redémarrage est nécessaire.")
        )
        layout.addWidget(QLabel(self.tr("Langue de l'application:")), 0, 0)
        layout.addWidget(self.lang_combo, 0, 1)

        # --- Police de l'application ---
        app_font_family = self.settings_manager.get("ui.app_font_family", "Noto Sans")
        app_font_size = self.settings_manager.get("ui.app_font_size", 10)
        self.current_app_font = QFont(app_font_family, app_font_size)
        self.app_font_button = QPushButton(
            f"{self.current_app_font.family()}, {self.current_app_font.pointSize()}pt"
        )
        self.app_font_button.setToolTip(
            self.tr("Définit la police et la taille de base pour l'ensemble de l'application.")
        )
        self.app_font_button.clicked.connect(self._select_app_font)
        layout.addWidget(QLabel(self.tr("Police de l'application:")), 1, 0)
        layout.addWidget(self.app_font_button, 1, 1)

        # --- Ligne de séparation ---
        separator1 = QLabel()
        separator1.setMinimumHeight(20)
        layout.addWidget(separator1, 2, 0, 1, 2)

        # --- Options d'affichage ---
        self.show_indexing_stats_checkbox = QCheckBox(
            self.tr("Afficher les statistiques d'indexation (mots et tags) dans la barre d'état")
        )
        show_indexing_stats = self.settings_manager.get("ui.show_indexing_stats", True)
        self.show_indexing_stats_checkbox.setChecked(
            str(show_indexing_stats).lower() == "true"
        )
        layout.addWidget(self.show_indexing_stats_checkbox, 3, 0, 1, 2)

        # --- Ligne de séparation ---
        separator2 = QLabel()
        separator2.setMinimumHeight(20)
        layout.addWidget(separator2, 4, 0, 1, 2)

        # --- Tags à exclure ---
        excluded_tags_list = self.settings_manager.get(
            "indexing.excluded_tags_from_cloud", []
        )
        self.excluded_tags_edit = QTextEdit()
        self.excluded_tags_edit.setPlainText(", ".join(sorted(excluded_tags_list)))
        self.excluded_tags_edit.setToolTip(
            self.tr("Liste de tags (sans @@, séparés par des virgules) à ne pas afficher dans le nuage de tags.")
        )
        layout.addWidget(QLabel(self.tr("Tags à exclure du nuage:")), 5, 0, Qt.AlignTop)
        layout.addWidget(self.excluded_tags_edit, 5, 1)

        layout.setRowStretch(6, 1)  # Pousse les éléments vers le haut
        return widget

    def _select_app_font(self):
        """Sélectionne la police pour l'application."""
        font, ok = QFontDialog.getFont(self.current_app_font, self)
        if ok:
            self.current_app_font = font
            self.app_font_button.setText(f"{font.family()}, {font.pointSize()}pt")

    def _create_display_tab(self):
        """Crée l'onglet 'Affichage' avec layout en grille."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Créer le QTabWidget pour les sous-onglets
        sub_tabs = QTabWidget()
        sub_tabs.addTab(self._create_markdown_editor_sub_tab(), self.tr("Editeur Markdown"))
        sub_tabs.addTab(self._create_html_preview_sub_tab(), self.tr("Aperçu HTML"))
        sub_tabs.addTab(self._create_pdf_export_sub_tab(), self.tr("Export PDF"))

        # "Editeur Markdown" est l'onglet par défaut
        sub_tabs.setCurrentIndex(0)

        # Bouton de réinitialisation, maintenant visible pour tous les sous-onglets
        reset_button = QPushButton(self.tr("Valeurs d'affichage par défaut"))
        reset_button.setToolTip(
            self.tr("Réinitialise les préférences de l'interface à leurs valeurs par défaut.")
        )
        reset_button.clicked.connect(self._reset_settings)

        # Layout pour le bouton pour le centrer et ajouter des marges
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(reset_button)
        button_layout.addStretch()

        layout.addWidget(sub_tabs)
        layout.addLayout(button_layout)  # Ajouter le layout du bouton en bas
        return widget

    def _create_markdown_editor_sub_tab(self):
        """Crée le sous-onglet pour les paramètres de l'éditeur Markdown."""
        # Créer un widget avec scroll pour gérer le grand nombre de paramètres
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.NoFrame)

        content_widget = QWidget()
        # Utiliser un QGridLayout pour mieux contrôler les colonnes
        layout = QGridLayout(content_widget)
        layout.setSpacing(15)
        layout.setColumnStretch(1, 1)  # Colonne des widgets s'étire
        layout.setColumnStretch(3, 1)  # Colonne des widgets s'étire

        row = 0

        # === SECTION GESTION DES THÈMES ===
        # Boutons pour sauvegarder et charger des thèmes
        theme_layout = QHBoxLayout()

        save_theme_button = QPushButton(self.tr("Sauvegarder comme thème"))
        save_theme_button.setToolTip(
            self.tr("Sauvegarder les paramètres actuels comme un nouveau thème")
        )
        save_theme_button.clicked.connect(self._save_as_theme)
        theme_layout.addWidget(save_theme_button)

        load_theme_button = QPushButton(self.tr("Sélectionner un thème"))
        load_theme_button.setToolTip(self.tr("Charger un thème existant"))
        load_theme_button.clicked.connect(self._load_theme)
        theme_layout.addWidget(load_theme_button)

        theme_layout.addStretch()

        layout.addLayout(theme_layout, row, 0, 1, 4)
        row += 1

        # Ligne de séparation
        layout.addWidget(QLabel(""), row, 0, 1, 4)
        row += 1

        # === SECTION AFFICHAGE LIGNES ===
        self.show_line_numbers_checkbox = QCheckBox(self.tr("Affichage des numéros de lignes ?"))
        show_line_numbers_setting = self.settings_manager.get(
            "editor.show_line_numbers", False
        )
        is_checked = str(show_line_numbers_setting).lower() == "true"
        self.show_line_numbers_checkbox.setChecked(is_checked)
        layout.addWidget(self.show_line_numbers_checkbox, row, 0, 1, 4)
        row += 1

        # Ligne de séparation
        layout.addWidget(QLabel(""), row, 0, 1, 4)
        row += 1

        # === SECTION POLICES ===
        # Police de l'éditeur
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        self.current_font = QFont(font_family, font_size)

        self.font_button = QPushButton(f"{font_family}, {font_size}pt")
        self.font_button.setMinimumWidth(250)  # Largeur minimale pour lisibilité
        self.font_button.clicked.connect(self._select_font)
        layout.addWidget(QLabel(self.tr("Police de l'éditeur:")), row, 0)
        layout.addWidget(self.font_button, row, 1)
        row += 1

        # Police pour le code
        code_font_family = self.settings_manager.get(
            "editor.code_font_family", "Consolas, Monaco, monospace"
        )
        self.current_code_font = QFont(code_font_family)

        self.code_font_button = QPushButton(f"{code_font_family}")
        self.code_font_button.setMinimumWidth(250)
        self.code_font_button.setToolTip(
            self.tr("Choisir la police pour le code inline et les blocs de code.")
        )
        self.code_font_button.clicked.connect(self._select_code_font)
        layout.addWidget(QLabel(self.tr("Police des extraits de code:")), row, 0)
        layout.addWidget(self.code_font_button, row, 1)
        row += 1

        # Police du Plan du Document
        outline_font_family = self.settings_manager.get(
            "outline.font_family", font_family
        )
        outline_font_size = self.settings_manager.get("outline.font_size", font_size)
        self.current_outline_font = QFont(outline_font_family, outline_font_size)

        self.outline_font_button = QPushButton(
            f"{outline_font_family}, {outline_font_size}pt"
        )
        self.outline_font_button.setMinimumWidth(250)
        self.outline_font_button.setToolTip(
            self.tr("Choisir la police pour le plan du document.")
        )
        self.outline_font_button.clicked.connect(self._select_outline_font)
        layout.addWidget(QLabel(self.tr("Police du Plan du Document:")), row, 0)
        layout.addWidget(self.outline_font_button, row, 1)
        row += 1

        # Ligne de séparation
        layout.addWidget(QLabel(""), row, 0, 1, 4)
        row += 1

        # === SECTION COULEURS (réparties sur 2 colonnes) ===
        col1_row = 0
        col2_row = 0

        # Liste des couleurs à afficher (label, clé_paramètre, attribut_widget, button_name)
        colors_config = [
            # Colonne 1
            (
                self.tr("Fond éditeur:"),
                "editor.background_color",
                "current_color",
                "color_button",
            ),
            (
                self.tr("Police éditeur:"),
                "editor.text_color",
                "current_text_color",
                "text_color_button",
            ),
            (
                self.tr("Titres Markdown:"),
                "editor.heading_color",
                "current_heading_color",
                "heading_color_button",
            ),
            (
                self.tr("Listes Markdown:"),
                "editor.list_color",
                "current_list_color",
                "list_color_button",
            ),
            (
                self.tr("Texte sélectionné:"),
                "editor.selection_text_color",
                "current_selection_text_color",
                "selection_text_color_button",
            ),
            (
                self.tr("Texte code inline:"),
                "editor.inline_code_text_color",
                "current_inline_code_text_color",
                "inline_code_text_color_button",
            ),
            (
                self.tr("Fond code inline:"),
                "editor.inline_code_background_color",
                "current_inline_code_bg_color",
                "inline_code_bg_color_button",
            ),
            (
                self.tr("Fond bloc code:"),
                "editor.code_block_background_color",
                "current_code_block_bg_color",
                "code_block_bg_color_button",
            ),
            # Colonne 2
            (
                self.tr("Texte gras:"),
                "editor.bold_color",
                "current_bold_color",
                "bold_color_button",
            ),
            (
                self.tr("Texte italique:"),
                "editor.italic_color",
                "current_italic_color",
                "italic_color_button",
            ),
            (
                self.tr("Texte barré:"),
                "editor.strikethrough_color",
                "current_strikethrough_color",
                "strikethrough_color_button",
            ),
            (
                self.tr("Fond surlignage:"),
                "editor.highlight_color",
                "current_highlight_color",
                "highlight_color_button",
            ),
            (
                self.tr("Citations:"),
                "editor.quote_color",
                "current_quote_color",
                "quote_color_button",
            ),
            (self.tr("Liens:"), "editor.link_color", "current_link_color", "link_color_button"),
            (
                self.tr("Commentaires HTML:"),
                "editor.html_comment_color",
                "current_html_comment_color",
                "html_comment_color_button",
            ),
            (
                self.tr("Tags (@@tag):"),
                "editor.tag_color",
                "current_tag_color",
                "tag_color_button",
            ),
            (
                self.tr("Horodatage (HH:MM):"),
                "editor.timestamp_color",
                "current_timestamp_color",
                "timestamp_color_button",
            ),
        ]

        # Séparer en deux colonnes
        mid_point = (len(colors_config) + 1) // 2
        col1_colors = colors_config[:mid_point]
        col2_colors = colors_config[mid_point:]

        # Colonne 1
        for label_text, setting_key, attr_name, button_name in col1_colors:
            color_hex = self.settings_manager.get(setting_key)
            setattr(self, attr_name, QColor(color_hex))
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color_hex};")
            button.setMinimumHeight(30)
            button.clicked.connect(self._make_color_selector(attr_name, button_name))
            setattr(self, button_name, button)

            layout.addWidget(QLabel(label_text), row + col1_row, 0)
            layout.addWidget(button, row + col1_row, 1)
            col1_row += 1

        # Colonne 2
        for label_text, setting_key, attr_name, button_name in col2_colors:
            color_hex = self.settings_manager.get(setting_key)
            setattr(self, attr_name, QColor(color_hex))
            button = QPushButton()
            button.setStyleSheet(f"background-color: {color_hex};")
            button.setMinimumHeight(30)
            button.clicked.connect(self._make_color_selector(attr_name, button_name))
            setattr(self, button_name, button)

            layout.addWidget(QLabel(label_text), row + col2_row, 2)
            layout.addWidget(button, row + col2_row, 3)
            col2_row += 1

        row += max(col1_row, col2_row)

        scroll.setWidget(content_widget)

        return scroll  # Retourner le widget scrollable

    def _create_html_preview_sub_tab(self):
        """Crée le sous-onglet (vide pour l'instant) pour l'aperçu HTML."""
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setSpacing(15)

        row = 0

        # === SECTION GESTION DES THÈMES CSS ===
        theme_layout = QHBoxLayout()

        self.html_theme_button = QPushButton(self.tr("Sélectionner un thème CSS"))
        self.html_theme_button.setToolTip(self.tr("Sélectionner un thème CSS pour l'aperçu"))
        self.html_theme_button.clicked.connect(self._select_css_theme)
        theme_layout.addWidget(self.html_theme_button)

        # Label pour afficher le thème actuellement sélectionné
        label_text = self.tr("<b>Actuel :</b> {}")
        self.current_html_theme_label = QLabel(
            label_text.format(self.selected_html_theme)
        )
        self.current_html_theme_label.setStyleSheet("margin-left: 10px;")
        theme_layout.addWidget(self.current_html_theme_label)

        theme_layout.addStretch()

        layout.addLayout(theme_layout, row, 0, 1, 4)
        row += 1

        # === SECTION MINI-APERÇU HTML ===
        self.html_preview_widget = QWebEngineView()
        self.html_preview_widget.setMinimumHeight(300)
        layout.addWidget(self.html_preview_widget, row, 0, 1, 4)

        layout.setRowStretch(row, 1)  # Pousse les éléments vers le haut

        return content_widget

    def _select_css_theme(self, pdf=False):
        """
        Ouvre une boîte de dialogue pour sélectionner un thème CSS pour l'aperçu HTML ou l'export PDF.
        """
        base_path = Path(__file__).parent.parent

        if pdf:
            css_dir = base_path / "resources" / "css_pdf"
            dialog_title = self.tr("Choisir un thème pour l'export PDF")
        else:
            css_dir = base_path / "resources" / "css_preview"
            dialog_title = self.tr("Choisir un thème pour l'aperçu HTML")

        if not css_dir.exists():
            msg = self.tr("Le répertoire des thèmes '{}' est introuvable.")
            QMessageBox.warning(
                self,
                self.tr("Erreur"),
                msg.format(css_dir.name),
            )
            return

        # Utiliser QDir pour lister les fichiers avec un filtre
        dir = QDir(str(css_dir))
        dir.setNameFilters(["*.css"])
        theme_files = dir.entryList()

        if not theme_files:
            QMessageBox.information(
                self, self.tr("Aucun thème"), self.tr("Aucun thème CSS trouvé dans le répertoire.")
            )
            return

        # Déterminer le thème actuel en fonction du contexte (HTML ou PDF)
        current_theme = self.selected_pdf_theme if pdf else self.selected_html_theme

        current_theme_index = (
            theme_files.index(current_theme) if current_theme in theme_files else 0
        )

        theme_name, ok = QInputDialog.getItem(
            self,
            self.tr("Sélection de thème"),
            dialog_title,
            theme_files,
            current_theme_index,
            False,
        )

        if ok and theme_name:
            css_file_path = css_dir / theme_name
            if pdf:
                self.selected_pdf_theme = theme_name
                label_text = self.tr("<b>Actuel :</b> {}")
                self.current_pdf_theme_label.setText(label_text.format(theme_name))
                # Mettre à jour le mini-aperçu PDF
                self._update_pdf_preview_style(css_file_path)
            else:
                self.selected_html_theme = theme_name
                label_text = self.tr("<b>Actuel :</b> {}")
                self.current_html_theme_label.setText(label_text.format(theme_name))
                self._update_html_preview_style(css_file_path)

    def _create_pdf_export_sub_tab(self):
        """Crée le sous-onglet (vide pour l'instant) pour l'export PDF."""
        content_widget = QWidget()
        layout = QGridLayout(content_widget)
        layout.setSpacing(15)

        row = 0

        # === SECTION GESTION DES THÈMES CSS POUR PDF ===
        theme_layout = QHBoxLayout()

        self.pdf_theme_button = QPushButton(self.tr("Sélectionner un thème CSS pour le PDF"))
        self.pdf_theme_button.setToolTip(
            self.tr("Sélectionner un thème CSS pour les exports PDF")
        )
        self.pdf_theme_button.clicked.connect(lambda: self._select_css_theme(pdf=True))
        theme_layout.addWidget(self.pdf_theme_button)

        # Label pour afficher le thème PDF actuellement sélectionné
        label_text = self.tr("<b>Actuel :</b> {}")
        self.current_pdf_theme_label = QLabel(
            label_text.format(self.selected_pdf_theme)
        )
        self.current_pdf_theme_label.setStyleSheet("margin-left: 10px;")
        theme_layout.addWidget(self.current_pdf_theme_label)

        theme_layout.addStretch()

        layout.addLayout(theme_layout, row, 0, 1, 4)
        row += 1

        # === SECTION MINI-APERÇU PDF ===
        self.pdf_preview_widget = QWebEngineView()
        self.pdf_preview_widget.setMinimumHeight(300)
        layout.addWidget(self.pdf_preview_widget, row, 0, 1, 4)

        layout.setRowStretch(row, 1)  # Pousse les éléments vers le haut

        return content_widget

    def _update_html_preview_style(self, css_file_path):
        """Met à jour le mini-aperçu HTML avec le style du fichier CSS donné."""
        css_content = ""
        if not css_file_path.exists():
            print(f"❌ Warning: The CSS file {css_file_path} could not be found.")
        else:
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()

        full_html = SAMPLE_HTML_FOR_PREVIEW.format(css_content=css_content)
        self.html_preview_widget.setHtml(full_html)

    def _update_pdf_preview_style(self, css_file_path):
        """Met à jour le mini-aperçu PDF avec le style du fichier CSS donné."""
        css_content = ""
        if not css_file_path.exists():
            print(f"❌ Warning: The CSS file {css_file_path} could not be found.")
        else:
            with open(css_file_path, "r", encoding="utf-8") as f:
                css_content = f.read()

        full_html = SAMPLE_HTML_FOR_PREVIEW.format(css_content=css_content)
        self.pdf_preview_widget.setHtml(full_html)

    def showEvent(self, event):
        """Appelé lorsque la boîte de dialogue est affichée."""
        super().showEvent(event)
        # Mettre à jour les mini-aperçus au premier affichage
        base_path = Path(__file__).parent.parent
        css_preview_dir = base_path / "resources" / "css_preview"
        css_pdf_dir = base_path / "resources" / "css_pdf"
        self._update_html_preview_style(css_preview_dir / self.selected_html_theme)
        self._update_pdf_preview_style(css_pdf_dir / self.selected_pdf_theme)

    def _create_panels_tab(self):
        """Crée l'onglet 'Panneaux' pour gérer la visibilité au démarrage."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(10)

        # Case pour le panneau de Notes
        self.show_notes_checkbox = QCheckBox(self.tr("Afficher le panneau 'Notes'"))
        show_notes = self.settings_manager.get("ui.show_notes_panel", True)
        self.show_notes_checkbox.setChecked(str(show_notes).lower() == "true")
        layout.addWidget(self.show_notes_checkbox)

        # Case pour le panneau de Navigation
        self.show_nav_checkbox = QCheckBox(self.tr("Afficher le panneau de Navigation"))
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        self.show_nav_checkbox.setChecked(str(show_nav).lower() == "true")
        layout.addWidget(self.show_nav_checkbox)

        # Case pour le panneau Plan du document
        self.show_outline_checkbox = QCheckBox(self.tr("Afficher le panneau 'Plan du document'"))
        show_outline = self.settings_manager.get("ui.show_outline_panel", True)
        self.show_outline_checkbox.setChecked(str(show_outline).lower() == "true")
        layout.addWidget(self.show_outline_checkbox)

        # Case pour le panneau Éditeur (toujours visible et désactivé)
        self.show_editor_checkbox = QCheckBox(self.tr("Afficher le panneau Éditeur"))
        self.show_editor_checkbox.setChecked(True)
        self.show_editor_checkbox.setEnabled(False)
        layout.addWidget(self.show_editor_checkbox)

        # Case pour le panneau Aperçu HTML
        self.show_preview_checkbox = QCheckBox(self.tr("Afficher le panneau 'Aperçu HTML'"))
        show_preview = self.settings_manager.get("ui.show_preview_panel", False)
        self.show_preview_checkbox.setChecked(str(show_preview).lower() == "true")
        layout.addWidget(self.show_preview_checkbox)

        # Case pour le panneau Lecteur
        self.show_reader_checkbox = QCheckBox(self.tr("Afficher le panneau 'Lecteur'"))
        show_reader = self.settings_manager.get("ui.show_reader_panel", False)
        self.show_reader_checkbox.setChecked(str(show_reader).lower() == "true")
        layout.addWidget(self.show_reader_checkbox)

        layout.addStretch()  # Pour pousser les cases vers le haut
        return widget

    def _create_integrations_tab(self):
        """Crée l'onglet 'Intégrations'."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.show_quote_checkbox = QCheckBox(
            self.tr("Afficher la citation du jour au démarrage")
        )
        show_quote = self.settings_manager.get(
            "integrations.show_quote_of_the_day", False
        )
        self.show_quote_checkbox.setChecked(str(show_quote).lower() == "true")
        layout.addWidget(self.show_quote_checkbox)

        self.youtube_integration_checkbox = QCheckBox(
            self.tr("Autoriser l'intégration de vidéo Youtube dans l'editeur Markdown")
        )
        is_youtube_enabled = self.settings_manager.get(
            "integrations.youtube_enabled", True
        )
        self.youtube_integration_checkbox.setChecked(
            str(is_youtube_enabled).lower() == "true"
        )
        layout.addWidget(self.youtube_integration_checkbox)

        self.youtube_transcript_checkbox = QCheckBox(
            self.tr("Autoriser l'affichage des transcripts de vidéo Youtube dans l'éditeur Markdown")
        )
        is_transcript_enabled = self.settings_manager.get(
            "integrations.youtube_transcript_enabled", True
        )
        self.youtube_transcript_checkbox.setChecked(
            str(is_transcript_enabled).lower() == "true"
        )
        self.youtube_transcript_checkbox.setEnabled(
            str(is_youtube_enabled).lower() == "true"
        )
        layout.addWidget(self.youtube_transcript_checkbox)

        # Lier les deux cases à cocher
        self.youtube_integration_checkbox.toggled.connect(
            self.youtube_transcript_checkbox.setEnabled
        )

        # Météo Weatherapi.com
        weather_layout = QHBoxLayout()
        weather_layout.addWidget(QLabel(self.tr("Météo Weatherapi.com")))

        weather_layout.addWidget(QLabel(self.tr("Ville :")))
        self.weather_city_edit = QLineEdit()
        self.weather_city_edit.setMaxLength(20)
        self.weather_city_edit.setText(
            self.settings_manager.get("integrations.weather.city")
        )
        weather_layout.addWidget(self.weather_city_edit)

        weather_layout.addWidget(QLabel(self.tr("Clé API :")))
        self.weather_api_key_edit = QLineEdit()
        self.weather_api_key_edit.setMaxLength(32)
        self.weather_api_key_edit.setEchoMode(QLineEdit.Password)
        self.weather_api_key_edit.setText(
            self.settings_manager.get("integrations.weather.api_key")
        )
        weather_layout.addWidget(self.weather_api_key_edit)

        weather_layout.addStretch()

        # Wrapper widget for the weather layout
        weather_widget = QWidget()
        weather_widget.setLayout(weather_layout)

        layout.addWidget(weather_widget)

        # Astro Soleil et Lune
        astro_layout = QHBoxLayout()
        astro_layout.addWidget(QLabel(self.tr("Astro Soleil et Lune Ville :")))
        self.astro_city_edit = QLineEdit()
        self.astro_city_edit.setText(
            self.settings_manager.get("integrations.sun_moon.city", "")
        )
        astro_layout.addWidget(self.astro_city_edit)

        self.astro_search_button = QPushButton(self.tr("Rechercher"))
        self.astro_search_button.clicked.connect(self._search_city_coords)
        astro_layout.addWidget(self.astro_search_button)

        astro_layout.addWidget(QLabel(self.tr("Latitude:")))
        self.astro_lat_edit = QLineEdit()
        self.astro_lat_edit.setReadOnly(True)
        self.astro_lat_edit.setText(
            self.settings_manager.get("integrations.sun_moon.latitude", "")
        )
        astro_layout.addWidget(self.astro_lat_edit)

        astro_layout.addWidget(QLabel(self.tr("Longitude:")))
        self.astro_lon_edit = QLineEdit()
        self.astro_lon_edit.setReadOnly(True)
        self.astro_lon_edit.setText(
            self.settings_manager.get("integrations.sun_moon.longitude", "")
        )
        astro_layout.addWidget(self.astro_lon_edit)

        astro_layout.addStretch()
        astro_widget = QWidget()
        astro_widget.setLayout(astro_layout)
        layout.addWidget(astro_widget)

        layout.addStretch()
        return widget

    def _select_font(self):
        """Sélectionne la police pour l'éditeur."""
        font, ok = QFontDialog.getFont(self.current_font, self)
        if ok:
            self.current_font = font
            self.font_button.setText(f"{font.family()}, {font.pointSize()}pt")

    def _select_code_font(self):
        """Sélectionne la police pour le code."""
        font, ok = QFontDialog.getFont(self.current_code_font, self)
        if ok:
            self.current_code_font = font
            self.code_font_button.setText(font.family())

    def _select_outline_font(self):
        """Sélectionne la police pour le plan du document."""
        font, ok = QFontDialog.getFont(self.current_outline_font, self)
        if ok:
            self.current_outline_font = font
            self.outline_font_button.setText(f"{font.family()}, {font.pointSize()}pt")

    def _make_color_selector(self, attr_name, button_name):
        """Crée une fonction de sélection de couleur pour un attribut donné."""

        def selector():
            current_color = getattr(self, attr_name)
            color = QColorDialog.getColor(current_color, self)
            if color.isValid():
                setattr(self, attr_name, color)
                button = getattr(self, button_name)
                button.setStyleSheet(f"background-color: {color.name()};")

        return selector

    def _search_city_coords(self):
        """Recherche les coordonnées GPS d'une ville."""
        city_name = self.astro_city_edit.text().strip()
        if not city_name:
            QMessageBox.warning(self, self.tr("Recherche"), self.tr("Veuillez saisir un nom de ville."))
            return

        try:
            geolocator = Nominatim(user_agent="bluenotebook_app")
            location = geolocator.geocode(city_name)
            if location:
                self.astro_lat_edit.setText(f"{location.latitude:.6f}")
                self.astro_lon_edit.setText(f"{location.longitude:.6f}")
            else:
                msg = self.tr("Impossible de trouver les coordonnées pour '{}'.")
                QMessageBox.warning(
                    self,
                    self.tr("Recherche"),
                    msg.format(city_name),
                )
        except Exception as e:
            msg = self.tr("Une erreur est survenue : {}")
            QMessageBox.critical(
                self, self.tr("Erreur de géolocalisation"), msg.format(e)
            )

    def _save_as_theme(self):
        """Sauvegarde les paramètres actuels comme un nouveau thème."""
        theme_name, ok = QInputDialog.getText(
            self, self.tr("Sauvegarder le thème"), self.tr("Nom du thème:"), text="Mon Thème"
        )

        if not ok or not theme_name:
            return

        # Nettoyer le nom du thème pour en faire un nom de fichier valide
        safe_name = "".join(
            c for c in theme_name if c.isalnum() or c in (" ", "-", "_")
        ).strip()
        safe_name = safe_name.replace(" ", "_")

        if not safe_name:
            QMessageBox.warning(self, self.tr("Erreur"), self.tr("Le nom du thème n'est pas valide."))
            return

        # Construire le chemin du fichier thème
        base_path = Path(__file__).parent.parent
        themes_dir = base_path / "resources" / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)

        theme_file = themes_dir / f"{safe_name}.json"

        # Vérifier si le fichier existe déjà
        if theme_file.exists():
            msg = self.tr("Un thème nommé '{}' existe déjà. Voulez-vous le remplacer?")
            reply = QMessageBox.question(
                self,
                self.tr("Fichier existant"),
                msg.format(safe_name),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return

        # Créer le dictionnaire du thème
        theme_data = {
            "name": theme_name,
            "font": {
                "family": self.current_font.family(),
                "size": self.current_font.pointSize(),
                "code_family": self.current_code_font.family(),
            },
            "outline": {
                "family": self.current_outline_font.family(),
                "size": self.current_outline_font.pointSize(),
            },
            "colors": {
                "background_color": self.current_color.name(),
                "text_color": self.current_text_color.name(),
                "heading_color": self.current_heading_color.name(),
                "list_color": self.current_list_color.name(),
                "selection_text_color": self.current_selection_text_color.name(),
                "inline_code_text_color": self.current_inline_code_text_color.name(),
                "inline_code_background_color": self.current_inline_code_bg_color.name(),
                "code_block_background_color": self.current_code_block_bg_color.name(),
                "bold_color": self.current_bold_color.name(),
                "italic_color": self.current_italic_color.name(),
                "strikethrough_color": self.current_strikethrough_color.name(),
                "highlight_color": self.current_highlight_color.name(),
                "quote_color": self.current_quote_color.name(),
                "link_color": self.current_link_color.name(),
                "html_comment_color": self.current_html_comment_color.name(),
                "tag_color": self.current_tag_color.name(),
                "timestamp_color": self.current_timestamp_color.name(),
            },
        }

        # Sauvegarder le thème
        try:
            with open(theme_file, "w", encoding="utf-8") as f:
                json.dump(theme_data, f, indent=4)

            msg = self.tr("Le thème '{}' a été sauvegardé avec succès.")
            QMessageBox.information(
                self,
                self.tr("Thème sauvegardé"),
                msg.format(theme_name),
            )
        except Exception as e:
            msg = self.tr("Impossible de sauvegarder le thème:\n{}")
            QMessageBox.critical(
                self, self.tr("Erreur"), msg.format(e)
            )

    def _load_theme(self):
        """Charge un thème existant."""
        base_path = Path(__file__).parent.parent
        themes_dir = base_path / "resources" / "themes"

        if not themes_dir.exists():
            QMessageBox.information(
                self,
                self.tr("Aucun thème"),
                self.tr("Aucun thème n'est disponible. Créez-en un avec 'Sauvegarder comme thème'."),
            )
            return

        # Lister les thèmes disponibles
        theme_files = list(themes_dir.glob("*.json"))

        if not theme_files:
            QMessageBox.information(
                self,
                self.tr("Aucun thème"),
                self.tr("Aucun thème n'est disponible. Créez-en un avec 'Sauvegarder comme thème'."),
            )
            return

        # Créer la liste des noms de thèmes
        theme_names = []
        theme_map = {}

        for theme_file in theme_files:
            try:
                with open(theme_file, "r", encoding="utf-8") as f:
                    theme_data = json.load(f)
                    name = theme_data.get("name", theme_file.stem)
                    theme_names.append(name)
                    theme_map[name] = theme_file
            except:
                continue

        if not theme_names:
            QMessageBox.warning(self, self.tr("Erreur"), self.tr("Aucun thème valide trouvé."))
            return

        # Demander à l'utilisateur de choisir un thème
        dialog = QInputDialog(self)
        dialog.setWindowTitle(self.tr("Thème"))
        dialog.setLabelText(self.tr("Choisissez un thème:"))
        dialog.setComboBoxItems(theme_names)
        dialog.setOption(QInputDialog.UseListViewForComboBoxItems, True)

        # Augmenter la largeur de la boîte de dialogue
        dialog.setMinimumWidth(600)

        ok = dialog.exec_()
        if not ok:
            return

        theme_name = dialog.textValue()

        # Charger le thème sélectionné
        theme_file = theme_map[theme_name]

        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)

            # Appliquer les polices
            font_info = theme_data.get("font", {})
            self.current_font = QFont(
                font_info.get("family", "Arial"), font_info.get("size", 12)
            )
            self.font_button.setText(
                f"{self.current_font.family()}, {self.current_font.pointSize()}pt"
            )

            self.current_code_font = QFont(font_info.get("code_family", "Courier New"))
            self.code_font_button.setText(self.current_code_font.family())

            # Appliquer la police du plan
            outline_font_info = theme_data.get(
                "outline", font_info
            )  # Fallback sur la police éditeur
            self.current_outline_font = QFont(
                outline_font_info.get("family", self.current_font.family()),
                outline_font_info.get("size", self.current_font.pointSize()),
            )
            self.outline_font_button.setText(
                f"{self.current_outline_font.family()}, {self.current_outline_font.pointSize()}pt"
            )
            # Appliquer les couleurs
            colors = theme_data.get("colors", {})
            color_mappings = [
                ("background_color", "current_color", "color_button"),
                ("text_color", "current_text_color", "text_color_button"),
                ("heading_color", "current_heading_color", "heading_color_button"),
                ("list_color", "current_list_color", "list_color_button"),
                (
                    "selection_text_color",
                    "current_selection_text_color",
                    "selection_text_color_button",
                ),
                (
                    "inline_code_text_color",
                    "current_inline_code_text_color",
                    "inline_code_text_color_button",
                ),
                (
                    "inline_code_background_color",
                    "current_inline_code_bg_color",
                    "inline_code_bg_color_button",
                ),
                (
                    "code_block_background_color",
                    "current_code_block_bg_color",
                    "code_block_bg_color_button",
                ),
                ("bold_color", "current_bold_color", "bold_color_button"),
                ("italic_color", "current_italic_color", "italic_color_button"),
                (
                    "strikethrough_color",
                    "current_strikethrough_color",
                    "strikethrough_color_button",
                ),
                (
                    "highlight_color",
                    "current_highlight_color",
                    "highlight_color_button",
                ),
                ("quote_color", "current_quote_color", "quote_color_button"),
                ("link_color", "current_link_color", "link_color_button"),
                (
                    "html_comment_color",
                    "current_html_comment_color",
                    "html_comment_color_button",
                ),
                ("tag_color", "current_tag_color", "tag_color_button"),
                (
                    "timestamp_color",
                    "current_timestamp_color",
                    "timestamp_color_button",
                ),
            ]

            for color_key, attr_name, button_name in color_mappings:
                if color_key in colors:
                    color = QColor(colors[color_key])
                    setattr(self, attr_name, color)
                    button = getattr(self, button_name)
                    button.setStyleSheet(f"background-color: {color.name()};")

            msg = self.tr(
                "Le thème '{}' a été appliqué.\n"
                "Cliquez sur 'Valider' pour enregistrer les modifications."
            )
            QMessageBox.information(
                self,
                self.tr("Thème chargé"),
                msg.format(theme_name),
            )

        except Exception as e:
            msg = self.tr("Impossible de charger le thème:\n{}")
            QMessageBox.critical(
                self, self.tr("Erreur"), msg.format(e)
            )

    def _load_defaults_in_ui(self):
        """Charge les valeurs par défaut dans les widgets de l'onglet Affichage."""
        # Obtenir une copie des paramètres par défaut
        defaults = self.settings_manager.get_default_settings()

        # Appliquer les polices par défaut
        font_info = defaults.get("editor", {})
        self.current_font = QFont(
            font_info.get("font_family", "Arial"), font_info.get("font_size", 12)
        )
        self.font_button.setText(
            f"{self.current_font.family()}, {self.current_font.pointSize()}pt"
        )

        self.current_code_font = QFont(font_info.get("code_font_family", "Courier New"))
        self.code_font_button.setText(self.current_code_font.family())

        # Appliquer la police du plan par défaut
        outline_font_info = defaults.get("outline", font_info)
        self.current_outline_font = QFont(
            outline_font_info.get("font_family", self.current_font.family()),
            outline_font_info.get("font_size", self.current_font.pointSize()),
        )
        self.outline_font_button.setText(
            f"{self.current_outline_font.family()}, {self.current_outline_font.pointSize()}pt"
        )
        # Appliquer les couleurs par défaut
        colors = defaults.get("editor", {})
        color_mappings = [
            ("background_color", "current_color", "color_button"),
            ("text_color", "current_text_color", "text_color_button"),
            ("heading_color", "current_heading_color", "heading_color_button"),
            ("list_color", "current_list_color", "list_color_button"),
            (
                "selection_text_color",
                "current_selection_text_color",
                "selection_text_color_button",
            ),
            (
                "inline_code_text_color",
                "current_inline_code_text_color",
                "inline_code_text_color_button",
            ),
            (
                "inline_code_background_color",
                "current_inline_code_bg_color",
                "inline_code_bg_color_button",
            ),
            (
                "code_block_background_color",
                "current_code_block_bg_color",
                "code_block_bg_color_button",
            ),
            ("bold_color", "current_bold_color", "bold_color_button"),
            ("italic_color", "current_italic_color", "italic_color_button"),
            (
                "strikethrough_color",
                "current_strikethrough_color",
                "strikethrough_color_button",
            ),
            ("highlight_color", "current_highlight_color", "highlight_color_button"),
            ("quote_color", "current_quote_color", "quote_color_button"),
            ("link_color", "current_link_color", "link_color_button"),
            (
                "html_comment_color",
                "current_html_comment_color",
                "html_comment_color_button",
            ),
            ("tag_color", "current_tag_color", "tag_color_button"),
            ("timestamp_color", "current_timestamp_color", "timestamp_color_button"),
        ]

        for color_key, attr_name, button_name in color_mappings:
            if color_key in colors:
                color = QColor(colors[color_key])
                setattr(self, attr_name, color)
                button = getattr(self, button_name)
                button.setStyleSheet(f"background-color: {color.name()};")

        # Réinitialiser le thème de l'aperçu HTML
        default_html_theme = defaults.get("preview", {}).get(
            "css_theme", "default_preview.css"
        )
        self.selected_html_theme = default_html_theme
        label_text = self.tr("<b>Actuel :</b> {}")
        self.current_html_theme_label.setText(label_text.format(default_html_theme))

    def _reset_settings(self):
        """Affiche une confirmation et réinitialise les paramètres."""
        # Recharge les valeurs par défaut dans l'interface pour que l'utilisateur les voie
        self._load_defaults_in_ui()

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.tr("Confirmation"))
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(
            self.tr(
                "<p>Êtes-vous sûr de vouloir réinitialiser les préférences d'affichage ?</p>\n\n"
                "<p>Les changements seront appliqués après avoir cliqué sur \"Valider\".</p>"
            )
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText(self.tr("Valider"))
        msg_box.button(QMessageBox.No).setText(self.tr("Annuler"))
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.Yes:
            # Pas besoin de sauvegarder ici, _load_defaults_in_ui a déjà mis à jour l'UI.
            # La sauvegarde se fera si l'utilisateur clique sur "Valider".
            QMessageBox.information(
                self,
                self.tr("Préférences réinitialisées"),
                self.tr("Les valeurs par défaut ont été chargées. Cliquez sur 'Valider' pour les sauvegarder."),
            )

    def accept(self):
        """Sauvegarde les paramètres lorsque l'utilisateur clique sur 'Valider'."""
        # --- Onglet Général ---
        # Sauvegarde de la langue
        lang_map = {self.tr("Français"): "fr_FR", self.tr("English"): "en_US"}
        selected_lang = self.lang_combo.currentText()
        self.settings_manager.set("app.language", lang_map.get(selected_lang, "fr_FR"))

        # ... (sauvegarde des autres paramètres)
        # V3.3.8 - Sauvegarde de la police de l'application
        self.settings_manager.set("ui.app_font_family", self.current_app_font.family())
        self.settings_manager.set("ui.app_font_size", self.current_app_font.pointSize())

        # Sauvegarde du thème CSS de l'aperçu
        self.settings_manager.set("preview.css_theme", self.selected_html_theme)

        # Sauvegarde du thème CSS de l'export PDF
        self.settings_manager.set("pdf.css_theme", self.selected_pdf_theme)

        # Sauvegarde des paramètres d'intégration météo
        self.settings_manager.set(
            "integrations.weather.city", self.weather_city_edit.text()
        )
        self.settings_manager.set(
            "integrations.weather.api_key", self.weather_api_key_edit.text()
        )

        # Sauvegarde des paramètres d'intégration astro
        self.settings_manager.set(
            "integrations.sun_moon.city", self.astro_city_edit.text()
        )
        self.settings_manager.set(
            "integrations.sun_moon.latitude", self.astro_lat_edit.text()
        )
        self.settings_manager.set(
            "integrations.sun_moon.longitude", self.astro_lon_edit.text()
        )
        # ... (le reste de la méthode accept originale)
        # NOTE: La logique de sauvegarde des autres onglets doit être ajoutée ici.
        # Pour l'instant, on appelle juste super().accept()

        super().accept()

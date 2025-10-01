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
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt


class PreferencesDialog(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Préférences")
        self.setMinimumWidth(700)  # Augmenté pour meilleure lisibilité
        self.setMinimumHeight(600)  # Hauteur minimale

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

        # Tags à exclure du nuage
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
        """Crée l'onglet 'Affichage' avec layout en grille."""
        widget = QWidget()
        
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
        
        save_theme_button = QPushButton("💾 Sauvegarder comme thème")
        save_theme_button.setToolTip("Sauvegarder les paramètres actuels comme un nouveau thème")
        save_theme_button.clicked.connect(self._save_as_theme)
        theme_layout.addWidget(save_theme_button)
        
        load_theme_button = QPushButton("🎨 Sélectionner un thème")
        load_theme_button.setToolTip("Charger un thème existant")
        load_theme_button.clicked.connect(self._load_theme)
        theme_layout.addWidget(load_theme_button)
        
        theme_layout.addStretch()
        
        layout.addLayout(theme_layout, row, 0, 1, 4)
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
        layout.addWidget(QLabel("Police de l'éditeur:"), row, 0)
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
            "Choisir la police pour le code inline et les blocs de code."
        )
        self.code_font_button.clicked.connect(self._select_code_font)
        layout.addWidget(QLabel("Police des extraits de code:"), row, 0)
        layout.addWidget(self.code_font_button, row, 1)
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
            ("Fond éditeur:", "editor.background_color", "current_color", "color_button"),
            ("Police éditeur:", "editor.text_color", "current_text_color", "text_color_button"),
            ("Titres Markdown:", "editor.heading_color", "current_heading_color", "heading_color_button"),
            ("Listes Markdown:", "editor.list_color", "current_list_color", "list_color_button"),
            ("Texte sélectionné:", "editor.selection_text_color", "current_selection_text_color", "selection_text_color_button"),
            ("Texte code inline:", "editor.inline_code_text_color", "current_inline_code_text_color", "inline_code_text_color_button"),
            ("Fond code inline:", "editor.inline_code_background_color", "current_inline_code_bg_color", "inline_code_bg_color_button"),
            ("Fond bloc code:", "editor.code_block_background_color", "current_code_block_bg_color", "code_block_bg_color_button"),
            # Colonne 2
            ("Texte gras:", "editor.bold_color", "current_bold_color", "bold_color_button"),
            ("Texte italique:", "editor.italic_color", "current_italic_color", "italic_color_button"),
            ("Texte barré:", "editor.strikethrough_color", "current_strikethrough_color", "strikethrough_color_button"),
            ("Fond surlignage:", "editor.highlight_color", "current_highlight_color", "highlight_color_button"),
            ("Citations:", "editor.quote_color", "current_quote_color", "quote_color_button"),
            ("Liens:", "editor.link_color", "current_link_color", "link_color_button"),
            ("Commentaires HTML:", "editor.html_comment_color", "current_html_comment_color", "html_comment_color_button"),
            ("Tags (@@tag):", "editor.tag_color", "current_tag_color", "tag_color_button"),
            ("Horodatage (HH:MM):", "editor.timestamp_color", "current_timestamp_color", "timestamp_color_button"),
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
        
        # Bouton de réinitialisation
        layout.addWidget(QLabel(""), row, 0)  # Ligne vide
        row += 1
        
        reset_button = QPushButton("🔄 Valeurs par défaut")
        reset_button.setToolTip(
            "Réinitialise les préférences de l'interface à leurs valeurs par défaut."
        )
        reset_button.clicked.connect(self._reset_settings)
        layout.addWidget(reset_button, row, 0, 1, 4)  # Span sur 4 colonnes
        
        scroll.setWidget(content_widget)
        
        main_layout = QVBoxLayout(widget)
        main_layout.addWidget(scroll)
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
        is_checked = self.settings_manager.get(
            "integrations.show_quote_of_the_day", False
        )
        self.show_quote_checkbox.setChecked(is_checked)
        layout.addWidget(self.show_quote_checkbox)

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

    def _save_as_theme(self):
        """Sauvegarde les paramètres actuels comme un nouveau thème."""
        theme_name, ok = QInputDialog.getText(
            self,
            "Sauvegarder le thème",
            "Nom du thème:",
            text="Mon Thème"
        )
        
        if not ok or not theme_name:
            return
        
        # Nettoyer le nom du thème pour en faire un nom de fichier valide
        safe_name = "".join(c for c in theme_name if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_name = safe_name.replace(' ', '_')
        
        if not safe_name:
            QMessageBox.warning(self, "Erreur", "Le nom du thème n'est pas valide.")
            return
        
        # Construire le chemin du fichier thème
        base_path = Path(__file__).parent.parent
        themes_dir = base_path / "resources" / "themes"
        themes_dir.mkdir(parents=True, exist_ok=True)
        
        theme_file = themes_dir / f"{safe_name}.json"
        
        # Vérifier si le fichier existe déjà
        if theme_file.exists():
            reply = QMessageBox.question(
                self,
                "Fichier existant",
                f"Un thème nommé '{safe_name}' existe déjà. Voulez-vous le remplacer?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Créer le dictionnaire du thème
        theme_data = {
            "name": theme_name,
            "font": {
                "family": self.current_font.family(),
                "size": self.current_font.pointSize(),
                "code_family": self.current_code_font.family()
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
                "timestamp_color": self.current_timestamp_color.name()
            }
        }
        
        # Sauvegarder le thème
        try:
            with open(theme_file, 'w', encoding='utf-8') as f:
                json.dump(theme_data, f, indent=4)
            
            QMessageBox.information(
                self,
                "Thème sauvegardé",
                f"Le thème '{theme_name}' a été sauvegardé avec succès."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de sauvegarder le thème:\n{e}"
            )

    def _load_theme(self):
        """Charge un thème existant."""
        base_path = Path(__file__).parent.parent
        themes_dir = base_path / "resources" / "themes"
        
        if not themes_dir.exists():
            QMessageBox.information(
                self,
                "Aucun thème",
                "Aucun thème n'est disponible. Créez-en un avec 'Sauvegarder comme thème'."
            )
            return
        
        # Lister les thèmes disponibles
        theme_files = list(themes_dir.glob("*.json"))
        
        if not theme_files:
            QMessageBox.information(
                self,
                "Aucun thème",
                "Aucun thème n'est disponible. Créez-en un avec 'Sauvegarder comme thème'."
            )
            return
        
        # Créer la liste des noms de thèmes
        theme_names = []
        theme_map = {}
        
        for theme_file in theme_files:
            try:
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_data = json.load(f)
                    name = theme_data.get("name", theme_file.stem)
                    theme_names.append(name)
                    theme_map[name] = theme_file
            except:
                continue
        
        if not theme_names:
            QMessageBox.warning(
                self,
                "Erreur",
                "Aucun thème valide trouvé."
            )
            return
        
        # Demander à l'utilisateur de choisir un thème
        theme_name, ok = QInputDialog.getItem(
            self,
            "Sélectionner un thème",
            "Choisissez un thème:",
            theme_names,
            0,
            False
        )
        
        if not ok:
            return
        
        # Charger le thème sélectionné
        theme_file = theme_map[theme_name]
        
        try:
            with open(theme_file, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            # Appliquer les polices
            font_info = theme_data.get("font", {})
            self.current_font = QFont(
                font_info.get("family", "Arial"),
                font_info.get("size", 12)
            )
            self.font_button.setText(
                f"{self.current_font.family()}, {self.current_font.pointSize()}pt"
            )
            
            self.current_code_font = QFont(font_info.get("code_family", "Courier New"))
            self.code_font_button.setText(self.current_code_font.family())
            
            # Appliquer les couleurs
            colors = theme_data.get("colors", {})
            color_mappings = [
                ("background_color", "current_color", "color_button"),
                ("text_color", "current_text_color", "text_color_button"),
                ("heading_color", "current_heading_color", "heading_color_button"),
                ("list_color", "current_list_color", "list_color_button"),
                ("selection_text_color", "current_selection_text_color", "selection_text_color_button"),
                ("inline_code_text_color", "current_inline_code_text_color", "inline_code_text_color_button"),
                ("inline_code_background_color", "current_inline_code_bg_color", "inline_code_bg_color_button"),
                ("code_block_background_color", "current_code_block_bg_color", "code_block_bg_color_button"),
                ("bold_color", "current_bold_color", "bold_color_button"),
                ("italic_color", "current_italic_color", "italic_color_button"),
                ("strikethrough_color", "current_strikethrough_color", "strikethrough_color_button"),
                ("highlight_color", "current_highlight_color", "highlight_color_button"),
                ("quote_color", "current_quote_color", "quote_color_button"),
                ("link_color", "current_link_color", "link_color_button"),
                ("html_comment_color", "current_html_comment_color", "html_comment_color_button"),
                ("tag_color", "current_tag_color", "tag_color_button"),
                ("timestamp_color", "current_timestamp_color", "timestamp_color_button"),
            ]
            
            for color_key, attr_name, button_name in color_mappings:
                if color_key in colors:
                    color = QColor(colors[color_key])
                    setattr(self, attr_name, color)
                    button = getattr(self, button_name)
                    button.setStyleSheet(f"background-color: {color.name()};")
            
            QMessageBox.information(
                self,
                "Thème chargé",
                f"Le thème '{theme_name}' a été appliqué.\nCliquez sur 'Valider' pour enregistrer les modifications."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Impossible de charger le thème:\n{e}"
            )

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
            self.reject()  # Ferme la boîte de dialogue sans sauvegarder

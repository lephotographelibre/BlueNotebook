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

Gestion des préférences de l'application BlueNotebook.
"""

import json
from pathlib import Path


class SettingsManager:
    """Gère le chargement et la sauvegarde des paramètres de l'application."""

    def __init__(self):
        # Définir le chemin du fichier de configuration
        self.settings_path = Path.home() / ".config" / "BlueNotebook" / "settings.json"
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        # Définir les paramètres par défaut
        self.defaults = {
            self.tr("app"): {
                self.tr("language"): self.tr("fr_FR"),
            },
            self.tr("editor"): {
                self.tr("font_family"): self.tr("Noto Sans"),
                self.tr("font_size"): 14,
                self.tr("background_color"): self.tr("#f0f2f5"),
                self.tr("text_color"): self.tr("#16191b"),
                self.tr("selection_text_color"): self.tr("#d0c9c8"),
                self.tr("show_line_numbers"): self.tr("true"),
                # Couleurs de syntaxe
                self.tr("heading_color"): self.tr("#d06146"),
                self.tr("list_color"): self.tr("#d06146"),
                self.tr("inline_code_text_color"): self.tr("#6a4041"),
                self.tr("inline_code_background_color"): self.tr("#edf0e9"),
                self.tr("code_block_background_color"): self.tr("#f0f2f5"),
                self.tr("bold_color"): self.tr("#6a4041"),
                self.tr("italic_color"): self.tr("#6a4041"),
                self.tr("strikethrough_color"): self.tr("#6a4041"),
                self.tr("highlight_color"): self.tr("#fffec7"),
                self.tr("tag_color"): self.tr("#6a4041"),
                self.tr("timestamp_color"): self.tr("#6a4041"),
                self.tr("quote_color"): self.tr("#363c42"),
                self.tr("link_color"): self.tr("#6a4041"),
                self.tr("code_font_family"): self.tr("Courier New"),
                self.tr("html_comment_color"): self.tr("#9ca3af"),
            },
            self.tr("outline"): {
                self.tr("font_family"): self.tr("Noto Sans"),
                self.tr("font_size"): 12,
            },
            "preview": {"css_theme": "default_preview.css"},
            self.tr("integrations"): {
                self.tr("show_quote_of_the_day"): False,
                self.tr("weather"): {
                    self.tr("city"): self.tr(""),
                    self.tr("api_key"): self.tr(""),
                },
                self.tr("sun_moon"): {
                    self.tr("city"): self.tr(""),
                    self.tr("latitude"): self.tr(""),
                    self.tr("longitude"): self.tr(""),
                },
            },
            self.tr("ui"): {
                self.tr("app_font_family"): self.tr("Noto Sans"),
                self.tr("app_font_size"): 10,
                self.tr("show_notes_panel"): True,  # Par défaut, visible
                self.tr("show_navigation_panel"): False,  # Par défaut, masqué
                self.tr("show_outline_panel"): False,  # Par défaut, masqué
                self.tr("show_preview_panel"): True,  # Par défaut, visible
                self.tr("show_indexing_stats"): True,
            },
            self.tr("indexing"): {
                self.tr("user_excluded_words"): [],
                self.tr("excluded_tags_from_cloud"): [],
                self.tr("excluded_words_from_cloud"): [],
            },
            self.tr("notes"): {
                self.tr("user_excluded_words"): [],
                self.tr("excluded_tags_from_cloud"): [],
                self.tr("excluded_words_from_cloud"): [],
                self.tr("folder_colors"): {},
            },
            self.tr("pdf"): {
                self.tr("last_directory"): str(Path.home()),
                self.tr("last_author"): self.tr(""),
                self.tr("last_title"): self.tr("BlueNotebook Journal"),
                self.tr("last_image_save_directory"): str(Path.home()),
            },
            self.tr("backup"): {
                self.tr("last_directory"): self.tr(""),
            },
        }

        # Charger les paramètres
        self.settings = self.load_settings()

    def _deep_merge(self, source, destination):
        """Fusionne récursivement deux dictionnaires."""
        for key, value in source.items():
            if isinstance(value, dict):
                # Obtenir le dictionnaire à fusionner ou un dictionnaire vide
                node = destination.setdefault(key, {})
                self._deep_merge(value, node)
            else:
                destination.setdefault(key, value)
        return destination

    def load_settings(self):
        """Charge les paramètres depuis le fichier JSON, en utilisant les valeurs par défaut si nécessaire."""
        defaults = self.defaults.copy()
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                return self._deep_merge(defaults, loaded_settings)
            except (json.JSONDecodeError, TypeError):
                return defaults
        return defaults

    def save_settings(self):
        """Sauvegarde les paramètres actuels dans le fichier JSON."""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(self.tr("Erreur lors de la sauvegarde des paramètres : %1").arg(e))

    def get(self, key, default=None):
        """Récupère une valeur de paramètre. Ex: 'editor.font_family'"""
        keys = key.split(self.tr("."))
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        """Définit une valeur de paramètre. Ex: 'editor.font_family'"""
        keys = key.split(self.tr("."))
        d = self.settings
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def reset_to_defaults(self):
        """Réinitialise les paramètres actuels aux valeurs par défaut."""
        self.settings = self.defaults.copy()
        self.save_settings()

    def reset_display_settings_to_defaults(self):
        """Réinitialise uniquement les paramètres d'affichage (polices, couleurs, etc.)."""
        if self.tr("editor") in self.defaults:
            self.settings[self.tr("editor")] = self.defaults[self.tr("editor")].copy()
        if self.tr("preview") in self.defaults:
            self.settings[self.tr("preview")] = self.defaults[self.tr("preview")].copy()
        # Ne touche pas aux sections "ui" et "integrations"
        self.save_settings()

    def get_default_settings(self):
        """Retourne une copie du dictionnaire des paramètres par défaut."""
        return self.defaults.copy()

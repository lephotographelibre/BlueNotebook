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
        # Définir les paramètres par défaut
        self.defaults = {
            "app": {
                "language": "en_US",
            },
            "editor": {
                "font_family": "Noto Sans",
                "font_size": 12,
                "background_color": "#ffffff",
                "text_color": "#253443",
                "selection_text_color": "#a4b5cf",
                "show_line_numbers": True,
                "heading_color": "#4c6eab",
                "list_color": "#a4b5cf",
                "inline_code_text_color": "#4c6eab",
                "inline_code_background_color": "#f7f8fa",
                "code_block_background_color": "#f7f8fa",
                "bold_color": "#4c6eab",
                "italic_color": "#253443",
                "strikethrough_color": "#253443",
                "highlight_color": "#fffec7",
                "tag_color": "#4c6eab",
                "timestamp_color": "#1d4ed8",
                "quote_color": "#4c6eab",
                "link_color": "#4c6eab",
                "code_font_family": "Courier New",
                "html_comment_color": "#9ca3af",
            },
            "outline": {
                "font_family": "Noto Sans",
                "font_size": 12,
            },
            "preview": {"css_theme": "default_preview.css"},
            "integrations": {
                "show_quote_of_the_day": False,
                "weather": {"city": "", "api_key": ""},
                "sun_moon": {"city": "", "latitude": "", "longitude": ""},
            },
            "ui": {
                "app_font_family": "Noto Sans",
                "app_font_size": 10,
                "show_notes_panel": True,  # Par défaut, visible
                "show_navigation_panel": False,  # Par défaut, masqué
                "show_outline_panel": False,  # Par défaut, masqué
                "show_preview_panel": True,  # Par défaut, visible
                "show_indexing_stats": True,
            },
            "indexing": {
                "user_excluded_words": [],
                "excluded_tags_from_cloud": [],
                "excluded_words_from_cloud": [],
            },
            "notes": {
                "user_excluded_words": [],
                "excluded_tags_from_cloud": [],
                "excluded_words_from_cloud": [],
                "folder_colors": {},
            },
            "pdf": {
                "last_directory": str(Path.home()),
                "last_author": "",
                "last_title": "BlueNotebook Journal",
                "last_image_save_directory": str(Path.home()),
            },
            "backup": {
                "last_directory": "",
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
        # PAS d'ENCAPSULATION  anglais   conservé,
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"❌ Error saving settings: {e}")

    def get(self, key, default=None):
        """Récupère une valeur de paramètre. Ex: 'editor.font_family'"""
        keys = key.split(".")
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key, value):
        """Définit une valeur de paramètre. Ex: 'editor.font_family'"""
        keys = key.split(".")
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
        if "editor" in self.defaults:
            self.settings["editor"] = self.defaults["editor"].copy()
        if "preview" in self.defaults:
            self.settings["preview"] = self.defaults["preview"].copy()
        # Ne touche pas aux sections "ui" et "integrations"
        self.save_settings()

    def get_default_settings(self):
        """Retourne une copie du dictionnaire des paramètres par défaut."""
        return self.defaults.copy()

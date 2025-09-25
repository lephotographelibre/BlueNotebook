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
            "editor": {
                "font_family": "Droid Sans Mono",
                "font_size": 12,
                "background_color": "#d6ebff",
                "text_color": "#2c3e50",
            },
            "integrations": {"show_quote_of_the_day": True},
        }

        # Charger les paramètres
        self.settings = self.load_settings()

    def load_settings(self):
        """Charge les paramètres depuis le fichier JSON, en utilisant les valeurs par défaut si nécessaire."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    loaded_settings = json.load(f)
                # Fusionner avec les valeurs par défaut pour garantir que toutes les clés sont présentes
                # Ceci est une fusion simple ; une fusion profonde serait plus robuste
                settings = self.defaults.copy()
                settings.update(loaded_settings)
                return settings
            except (json.JSONDecodeError, TypeError):
                return self.defaults.copy()
        return self.defaults.copy()

    def save_settings(self):
        """Sauvegarde les paramètres actuels dans le fichier JSON."""
        try:
            with open(self.settings_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4)
        except IOError as e:
            print(f"Erreur lors de la sauvegarde des paramètres : {e}")

    def get(self, key, default=None):
        """Récupère une valeur de paramètre. Ex: 'editor.font_family'"""
        keys = key.split(".")
        value = self.settings
        for k in keys:
            value = value.get(k, {})
        return value if value else default

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

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


Module pour récupérer la citation du jour depuis ouest-france.fr
"""

import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import date
from appdirs import user_cache_dir
from PyQt5.QtCore import QCoreApplication


class QuoteFetcher:
    """Classe pour récupérer la citation du jour."""

    URL = "https://citations.ouest-france.fr/"

    @staticmethod
    def _get_cache_path():
        """Retourne le chemin du fichier de cache."""
        # Utilise appdirs pour un chemin de cache multi-plateforme correct
        cache_dir = Path(user_cache_dir("BlueNotebook", "BlueNotebook"))
        return cache_dir / "quote_cache.json"

    @staticmethod
    def _read_from_cache():
        """Lit la citation depuis le cache si elle est valide pour aujourd'hui."""
        cache_file = QuoteFetcher._get_cache_path()
        today_str = str(date.today())

        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("date") == today_str:
                    return data.get("quote"), data.get("author")
            except (json.JSONDecodeError, IOError) as e:

                def tr(text):
                    return QCoreApplication.translate("QuoteFetcher", text)

                error_message = tr("Erreur de lecture du cache : %s") % e
                print(error_message)

        return None, None

    @staticmethod
    def get_quote_of_the_day():
        """
        Récupère la citation et l'auteur du jour.

        Returns:
            tuple: (citation, auteur) ou (None, None) en cas d'erreur.
        """
        # 1. Essayer de lire depuis le cache
        cached_quote, cached_author = QuoteFetcher._read_from_cache()
        if cached_quote and cached_author:
            return cached_quote, cached_author

        try:
            response = requests.get(QuoteFetcher.URL, timeout=5)
            response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

            soup = BeautifulSoup(response.content, "html.parser")

            # Trouver la citation
            quote_tag = soup.find("blockquote")
            quote = quote_tag.get_text(strip=True) if quote_tag else None

            # Trouver l'auteur
            author_tag = soup.select_one(".quotenav .who a")
            author = (
                author_tag.get_text(strip=True)
                if author_tag
                else QCoreApplication.translate("QuoteFetcher", "Auteur inconnu")
            )
            if quote:
                # 2. Sauvegarder dans le cache si la récupération a réussi
                cache_file = QuoteFetcher._get_cache_path()
                cache_file.parent.mkdir(parents=True, exist_ok=True)
                cache_data = {
                    "date": str(date.today()),
                    "quote": quote,
                    "author": author,
                }
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
                return quote, author

        except requests.RequestException as e:

            def tr(text):
                return QCoreApplication.translate("QuoteFetcher", text)

            error_message = tr("Erreur lors de la récupération de la citation : %s") % e
            print(error_message)

        return None, None

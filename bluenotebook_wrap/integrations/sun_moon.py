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

"""
Intégration pour récupérer les données astronomiques du jour (soleil, lune)
depuis l'API de l'U.S. Naval Observatory (USNO).
"""

import requests
import json
from datetime import date
from typing import List, Dict, Any, Optional

# Dictionnaire de traduction pour les phases de la lune
MOON_PHASES_TRANSLATION = {
    "New Moon": ("Nouvelle Lune", "🌑"),
    "Waxing Crescent": ("Croissant Ascendant", "🌒"),
    "First Quarter": ("Premier Quartier", "🌓"),
    "Waxing Gibbous": ("Gibbeuse Ascendante", "🌔"),
    "Full Moon": ("Pleine Lune", "🌕"),
    "Waning Gibbous": ("Gibbeuse Descendante", "🌖"),
    "Last Quarter": ("Dernier Quartier", "🌗"),
    "Waning Crescent": ("Croissant Descendant", "🌘"),
}


def find_phenomenon_time(
    data_list: List[Dict[str, Any]], phenomenon: str
) -> Optional[str]:
    """Trouve l'heure d'un phénomène ('Rise', 'Set') dans une liste de données."""
    for item in data_list:
        phen_value = item.get(self.tr("phen"), self.tr(""))
        if phen_value.lower() == phenomenon.lower():
            return item.get(self.tr("time"), self.tr("")).split()[0]
    return None


def generate_sun_moon_markdown(
    city: str,
    sun_rise: Optional[str],
    sun_set: Optional[str],
    moon_phase: str,
    moon_emoji: str,
    illumination: str,
) -> str:
    """Génère un fragment Markdown à partir des données du soleil et de la lune."""
    sun_rise_str = sun_rise or self.tr("N/A")
    sun_set_str = sun_set or self.tr("N/A")

    markdown = (
        self.tr("**Données Astronomiques du jour pour %1**\n\n").arg(city)
        self.tr("🌅 Lever: **%1** - 🌇 Coucher: **%2**\n").arg(sun_rise_str).arg(sun_set_str)
        self.tr("%1 Phase lune: %2 (%3 illuminée)").arg(moon_emoji).arg(moon_phase).arg(illumination)
    )
    return markdown


def get_sun_moon_markdown(
    city: str, latitude: str, longitude: str
) -> tuple[str | None, str | None]:
    """
    Fonction principale qui récupère les données et retourne le fragment Markdown.
    """
    today = date.today().strftime("%Y-%m-%d")
    # L'API USNO nécessite dst=true pour l'heure d'été, et tz est le décalage standard.
    # Pour la France, tz=1 (hiver) et dst=true (été).
    url = self.tr("https://aa.usno.navy.mil/api/rstt/oneday?date=%1&coords=%2,%3&tz=1&dst=true").arg(today).arg(latitude).arg(longitude)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get(self.tr("error")):
            return None, data.get(self.tr("message"), self.tr("Erreur inconnue de l'API."))
        if self.tr("properties") not in data or self.tr("data") not in data[self.tr("properties")]:
            return None, self.tr("Structure de la réponse JSON inattendue.")

        api_data = data[self.tr("properties")][self.tr("data")]
        sun_rise_time = find_phenomenon_time(api_data.get(self.tr("sundata"), []), self.tr("Rise"))
        sun_set_time = find_phenomenon_time(api_data.get(self.tr("sundata"), []), self.tr("Set"))
        moon_phase_en = api_data.get(self.tr("curphase"), self.tr("Inconnue"))
        frac_illum = api_data.get(self.tr("fracillum"), self.tr("N/A"))

        moon_phase_fr, moon_emoji = MOON_PHASES_TRANSLATION.get(
            moon_phase_en, (moon_phase_en, self.tr("❔"))
        )

        markdown_fragment = generate_sun_moon_markdown(
            city, sun_rise_time, sun_set_time, moon_phase_fr, moon_emoji, frac_illum
        )
        return markdown_fragment, None

    except requests.exceptions.RequestException as e:
        return None, self.tr("Erreur de requête HTTP : %1").arg(e)
    except Exception as e:
        return None, self.tr("Une erreur inattendue est survenue : %1").arg(e)

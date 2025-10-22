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
        phen_value = item.get("phen", "")
        if phen_value.lower() == phenomenon.lower():
            return item.get("time", "").split()[0]
    return None


def generate_sun_moon_html(
    city: str,
    sun_rise: Optional[str],
    sun_set: Optional[str],
    moon_phase: str,
    moon_emoji: str,
    illumination: str,
) -> str:
    """Génère un fragment HTML à partir des données du soleil et de la lune."""
    sun_rise_str = sun_rise or "N/A"
    sun_set_str = sun_set or "N/A"

    print(f"☀️ Données Astronomiques du jour pour <strong>{city}")

    html = f"""
<div class="sun-moon-container">
    <div class="sun-moon-row">
        <span class="sun-moon-text">Données Astronomiques du jour pour {city} </span>
    </div>
    <div class="sun-moon-row sun-moon-row-split">
        <span class="sun-moon-item"><span class="sun-moon-emoji">🌅</span><span class="sun-moon-text">Lever: <strong>{sun_rise_str}</strong></span></span>
        <span class="sun-moon-item"><span class="sun-moon-emoji">🌇</span><span class="sun-moon-text">Coucher: <strong>{sun_set_str}</strong></span></span>
    </div>
    <div class="sun-moon-row">
        <span class="sun-moon-item"><span class="sun-moon-emoji">{moon_emoji}</span><span class="sun-moon-text">Phase lune: {moon_phase} ({illumination} illuminée)</span></span>
    </div>
</div>
"""
    return html


def get_sun_moon_html(
    city: str, latitude: str, longitude: str
) -> tuple[str | None, str | None]:
    """
    Fonction principale qui récupère les données et retourne le fragment HTML.
    """
    today = date.today().strftime("%Y-%m-%d")
    # L'API USNO nécessite dst=true pour l'heure d'été, et tz est le décalage standard.
    # Pour la France, tz=1 (hiver) et dst=true (été).
    url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={today}&coords={latitude},{longitude}&tz=1&dst=true"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return None, data.get("message", "Erreur inconnue de l'API.")
        if "properties" not in data or "data" not in data["properties"]:
            return None, "Structure de la réponse JSON inattendue."

        api_data = data["properties"]["data"]
        sun_rise_time = find_phenomenon_time(api_data.get("sundata", []), "Rise")
        sun_set_time = find_phenomenon_time(api_data.get("sundata", []), "Set")
        moon_phase_en = api_data.get("curphase", "Inconnue")
        frac_illum = api_data.get("fracillum", "N/A")

        moon_phase_fr, moon_emoji = MOON_PHASES_TRANSLATION.get(
            moon_phase_en, (moon_phase_en, "❔")
        )

        html_fragment = generate_sun_moon_html(
            city, sun_rise_time, sun_set_time, moon_phase_fr, moon_emoji, frac_illum
        )
        return html_fragment, None

    except requests.exceptions.RequestException as e:
        return None, f"Erreur de requête HTTP : {e}"
    except Exception as e:
        return None, f"Une erreur inattendue est survenue : {e}"

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

from PyQt5.QtCore import QCoreApplication


class SunMoonContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("SunMoonContext", text)


def find_phenomenon_time(
    data_list: List[Dict[str, Any]], phenomenon: str
) -> Optional[str]:
    """Trouve l'heure d'un phénomène ('Rise', 'Set') dans une liste de données."""
    for item in data_list:
        phen_value = item.get("phen", "")
        if phen_value.lower() == phenomenon.lower():
            return item.get("time", "").split()[0]
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
    sun_rise_str = sun_rise or SunMoonContext.tr("N/A")
    sun_set_str = sun_set or SunMoonContext.tr("N/A")

    markdown = (
        SunMoonContext.tr("**Données Astronomiques du jour pour {city}**\n\n").format(
            city=city
        )
        + SunMoonContext.tr("🌅 Lever: **{rise}** - 🌇 Coucher: **{set}**\n").format(
            rise=sun_rise_str, set=sun_set_str
        )
        + SunMoonContext.tr("{emoji} Phase lune: {phase} ({illum} illuminée)").format(
            emoji=moon_emoji, phase=moon_phase, illum=illumination
        )
    )
    return markdown


def get_sun_moon_markdown(
    city: str, latitude: str, longitude: str
) -> tuple[str | None, str | None]:
    """
    Fonction principale qui récupère les données et retourne le fragment Markdown.
    """
    # Dictionnaire de traduction pour les phases de la lune
    # Déplacé ici pour que la traduction soit dynamique au moment de l'appel
    moon_phases_translation = {
        "New Moon": (SunMoonContext.tr("Nouvelle Lune"), "🌑"),
        "Waxing Crescent": (SunMoonContext.tr("Croissant Ascendant"), "🌒"),
        "First Quarter": (SunMoonContext.tr("Premier Quartier"), "🌓"),
        "Waxing Gibbous": (SunMoonContext.tr("Gibbeuse Ascendante"), "🌔"),
        "Full Moon": (SunMoonContext.tr("Pleine Lune"), "🌕"),
        "Waning Gibbous": (SunMoonContext.tr("Gibbeuse Descendante"), "🌖"),
        "Last Quarter": (SunMoonContext.tr("Dernier Quartier"), "🌗"),
        "Waning Crescent": (SunMoonContext.tr("Croissant Descendant"), "🌘"),
    }

    today = date.today().strftime("%Y-%m-%d")
    # L'API USNO nécessite dst=true pour l'heure d'été, et tz est le décalage standard.
    # Pour la France, tz=1 (hiver) et dst=true (été).
    url = f"https://aa.usno.navy.mil/api/rstt/oneday?date={today}&coords={latitude},{longitude}&tz=1&dst=true"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("error"):
            return None, data.get(
                "message", SunMoonContext.tr("Erreur inconnue de l'API.")
            )
        if "properties" not in data or "data" not in data["properties"]:
            return None, SunMoonContext.tr("Structure de la réponse JSON inattendue.")

        api_data = data["properties"]["data"]
        sun_rise_time = find_phenomenon_time(api_data.get("sundata", []), "Rise")
        sun_set_time = find_phenomenon_time(api_data.get("sundata", []), "Set")
        moon_phase_en = api_data.get("curphase", SunMoonContext.tr("Inconnue"))
        frac_illum = api_data.get("fracillum", "N/A")

        moon_phase_fr, moon_emoji = moon_phases_translation.get(
            moon_phase_en, (moon_phase_en, "❔")
        )

        markdown_fragment = generate_sun_moon_markdown(
            city, sun_rise_time, sun_set_time, moon_phase_fr, moon_emoji, frac_illum
        )
        return markdown_fragment, None

    except requests.exceptions.RequestException as e:
        return None, SunMoonContext.tr("Erreur de requête HTTP : {error}").format(
            error=e
        )
    except Exception as e:
        return None, SunMoonContext.tr(
            "Une erreur inattendue est survenue : {error}"
        ).format(error=e)

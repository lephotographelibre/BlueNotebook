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
    """
    Trouve l'heure d'un phénomène ('R' pour lever, 'S' pour coucher) dans une liste de données.
    Gère les anciennes ('R', 'S') et nouvelles ('Rise', 'Set') notations de l'API.
    """
    for item in data_list:
        phen_value = item.get("phen", "")
        # Comparaison insensible à la casse et gestion des abréviations
        if phen_value.lower() == phenomenon.lower() or (
            phenomenon in ("R", "S") and phen_value.startswith(phenomenon)
        ):
            # Nettoie l'heure pour ne garder que HH:MM
            return item.get("time", "").split()[0]
    return None


def generate_sun_html(
    sun_rise: Optional[str],
    sun_set: Optional[str],
    moon_phase: str,
    moon_emoji: str,
    illumination: str,
) -> str:
    """Génère un fragment HTML à partir des données du soleil et de la lune."""
    sun_rise_str = sun_rise or "N/A"
    sun_set_str = sun_set or "N/A"

    html = f"""
<div class="sun-moon-container">
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


# Utiliser la date du jour pour éviter les erreurs de date future
today = date.today().strftime("%Y-%m-%d")
url = f"https://aa.usno.navy.mil/api/rstt/oneday?date=2025-10-22&coords=46.56890409839087,0.34354146083074305&tz=1&dst=true"

try:
    response = requests.get(url, timeout=10)
    # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
    response.raise_for_status()

    data = response.json()

    # Vérifier la présence d'une erreur applicative dans le JSON
    if data.get("error"):
        print(f"Erreur de l'API: {data.get('message', 'Erreur inconnue.')}")
    elif "properties" not in data or "data" not in data["properties"]:
        print("Erreur: La structure de la réponse JSON est inattendue.")
        print(json.dumps(data, indent=2))
    else:
        api_data = data["properties"]["data"]

        # Extraire les données en utilisant la nouvelle structure
        sun_rise_time = find_phenomenon_time(api_data.get("sundata", []), "Rise")
        sun_set_time = find_phenomenon_time(api_data.get("sundata", []), "Set")
        moon_phase_en = api_data.get("curphase", "Inconnue")
        frac_illum = api_data.get("fracillum", "N/A")

        # Traduire la phase de la lune et obtenir l'emoji
        moon_phase_fr, moon_emoji = MOON_PHASES_TRANSLATION.get(
            moon_phase_en, (moon_phase_en, "❔")
        )

        print(f"Lever soleil 🌅: {sun_rise_time or 'Non disponible'}")
        print(f"Coucher soleil 🌇: {sun_set_time or 'Non disponible'}")
        print(f"Phase lune: {moon_phase_fr} {moon_emoji} ({frac_illum} illuminée)")

        # Générer et afficher le fragment HTML
        html_fragment = generate_sun_html(
            sun_rise_time,
            sun_set_time,
            moon_phase_fr,
            moon_emoji,
            frac_illum,
        )
        print("\n--- Fragment HTML généré ---")
        print(html_fragment)

except requests.exceptions.RequestException as e:
    print(f"Erreur de requête HTTP: {e}")

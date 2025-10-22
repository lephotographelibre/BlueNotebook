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
Intégration pour récupérer les données météo depuis WeatherAPI.com.
"""

import requests


def get_weather_html(city: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Récupère les données météo et retourne un fragment HTML ou un message d'erreur.

    :param city: Le nom de la ville.
    :param api_key: La clé API pour WeatherAPI.com.
    :return: Un tuple (html_fragment, None) en cas de succès,
             ou (None, error_message) en cas d'échec.
    """
    if not city or not api_key:
        return (
            None,
            "La ville et la clé API doivent être renseignées dans les Préférences.",
        )

    print(f"☀️ Récupération des données météo pour {city} ")

    # url = "http://api.weatherapi.com/v1/current.json"
    params = {"key": api_key, "q": city, "aqi": "no", "lang": "fr"}
    url = (
        "http://api.weatherapi.com/v1/current.json"
        + "?key="
        + api_key
        + "&q="
        + city
        + "&aqi=no&lang=fr"
    )
    # print(f"Météo URL  : {url}")

    try:
        response = requests.get(url, timeout=10)
        # response = requests.get(
        #    "http://api.weatherapi.com/v1/current.json?key=9d0c712506214035838132544251410&#q=Poitiers&aqi=no&lang=fr")
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        data = response.json()

        # Extraction des données
        location = data.get("location", {})
        current = data.get("current", {})
        condition = current.get("condition", {})

        city_name = location.get("name", city)
        localtime_str = location.get("localtime", "")
        temp_c = current.get("temp_c", "N/A")
        condition_text = condition.get("text", "N/A")
        icon_url = condition.get("icon", "")
        wind_kph = current.get("wind_kph", "N/A")
        humidity = current.get("humidity", "N/A")

        # Extraction de l'heure au format HH:MM
        time_str = ""
        if localtime_str:
            try:
                time_str = localtime_str.split(" ")[1]
            except IndexError:
                pass  # L'heure ne sera pas affichée si le format est inattendu

        # Construction du fragment HTML
        # Utilisation de styles inline pour un affichage simple et portable
        html_fragment = f"""
<div class="weather-container">
    <img src="https:{icon_url}" alt="{condition_text}" class="weather-icon">
    <div class="weather-details">
        <span class="weather-location">{city_name}:</span> {condition_text}, <strong class="weather-temp">{temp_c}°C</strong> à {time_str}<br>
        <span class="weather-extra">Vent: {wind_kph} km/h, Humidité: {humidity}%</span>
    </div>
</div>"""
        return html_fragment.strip(), None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return None, "Erreur d'authentification. Vérifiez votre clé API."
        elif e.response.status_code == 400:
            return None, f"Ville non trouvée : '{city}'. Vérifiez le nom de la ville."
        else:
            return None, f"Erreur HTTP : {e}"
    except requests.exceptions.RequestException as e:
        return None, f"Erreur de connexion : {e}"
    except Exception as e:
        return None, f"Une erreur inattendue est survenue : {e}"

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

# Table de correspondance entre les codes de condition de WeatherAPI et les emojis
WEATHER_CODE_TO_EMOJI = {
    1000: "☀️",  # Sunny
    1003: "⛅",  # Partly cloudy
    1006: "☁️",  # Cloudy
    1009: "🌥️",  # Overcast
    1030: "🌫️",  # Mist
    1063: "🌦️",  # Patchy rain possible
    1066: "🌨️",  # Patchy snow possible
    1069: "🌨️",  # Patchy sleet possible
    1072: "🌨️",  # Patchy freezing drizzle possible
    1087: "⛈️",  # Thundery outbreaks possible
    1114: "🌬️",  # Blowing snow
    1117: " Blizzard",  # Blizzard
    1135: "🌫️",  # Fog
    1147: "🌫️",  # Freezing fog
    1150: "🌦️",  # Patchy light drizzle
    1153: "🌦️",  # Light drizzle
    1168: "🌧️",  # Freezing drizzle
    1171: "🌧️",  # Heavy freezing drizzle
    1180: "🌦️",  # Patchy light rain
    1183: "🌧️",  # Light rain
    1186: "🌧️",  # Moderate rain at times
    1189: "🌧️",  # Moderate rain
    1192: "🌧️",  # Heavy rain at times
    1195: "🌧️",  # Heavy rain
    1198: "🌧️❄️",  # Light freezing rain
    1201: "🌧️❄️",  # Moderate or heavy freezing rain
    1204: "🌨️",  # Light sleet
    1207: "🌨️",  # Moderate or heavy sleet
    1210: "🌨️",  # Patchy light snow
    1213: "🌨️",  # Light snow
    1216: "🌨️",  # Patchy moderate snow
    1219: "🌨️",  # Moderate snow
    1222: "🌨️",  # Patchy heavy snow
    1225: "🌨️",  # Heavy snow
    1237: "🌨️",  # Ice pellets
    1240: "🌦️",  # Light rain shower
    1243: "🌧️",  # Moderate or heavy rain shower
    1246: "🌧️",  # Torrential rain shower
    1249: "🌨️",  # Light sleet showers
    1252: "🌨️",  # Moderate or heavy sleet showers
    1255: "🌨️",  # Light snow showers
    1258: "🌨️",  # Moderate or heavy snow showers
    1261: "🌨️",  # Light showers of ice pellets
    1264: "🌨️",  # Moderate or heavy showers of ice pellets
    1273: "⛈️",  # Patchy light rain with thunder
    1276: "⛈️",  # Moderate or heavy rain with thunder
    1279: "⛈️",  # Patchy light snow with thunder
    1282: "⛈️",  # Moderate or heavy snow with thunder
}


def get_weather_markdown(city: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Récupère les données météo et retourne un fragment Markdown ou un message d'erreur.

    :param city: Le nom de la ville.
    :param api_key: La clé API pour WeatherAPI.com.
    :return: Un tuple (markdown_fragment, None) en cas de succès,
             ou (None, error_message) en cas d'échec.
    """
    if not city or not api_key:
        return (
            None,
            self.tr("La ville et la clé API doivent être renseignées dans les Préférences."),
        )

    print(self.tr("☀️ Récupération des données météo pour %1 ").arg(city))

    # url = "http://api.weatherapi.com/v1/current.json"
    params = {self.tr("key"): api_key, self.tr("q"): city, self.tr("aqi"): self.tr("no"), self.tr("lang"): self.tr("fr")}
    url = (
        "http://api.weatherapi.com/v1/current.json"
        + self.tr("?key=")
        + api_key
        + self.tr("&q=")
        + city
        + self.tr("&aqi=no&lang=fr")
    )
    # print(self.tr("Météo URL  : %1").arg(url))

    try:
        response = requests.get(url, timeout=10)
        # response = requests.get(
        #    "http://api.weatherapi.com/v1/current.json?key=9d0c712506214035838132544251410&#q=Poitiers&aqi=no&lang=fr")
        response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP

        data = response.json()

        # Extraction des données
        location = data.get(self.tr("location"), {})
        current = data.get(self.tr("current"), {})
        condition = current.get(self.tr("condition"), {})

        city_name = location.get(self.tr("name"), city)
        localtime_str = location.get(self.tr("localtime"), self.tr(""))
        temp_c = current.get(self.tr("temp_c"), self.tr("N/A"))
        condition_text = condition.get(self.tr("text"), self.tr("N/A"))
        condition_code = condition.get(self.tr("code"))
        wind_kph = current.get(self.tr("wind_kph"), self.tr("N/A"))
        humidity = current.get(self.tr("humidity"), self.tr("N/A"))

        # Extraction de l'heure au format HH:MM
        time_str = self.tr("")
        if localtime_str:
            try:
                time_str = localtime_str.split(self.tr(" "))[1]
            except IndexError:
                pass  # L'heure ne sera pas affichée si le format est inattendu

        # Obtenir l'emoji correspondant au code météo
        weather_emoji = WEATHER_CODE_TO_EMOJI.get(condition_code, self.tr("❔"))

        # Construction du fragment Markdown
        markdown_fragment = self.tr("**%1 Météo pour %2 :** %3, **%4°C** à %5  Vent : %6 km/h, Humidité : %7%").arg(weather_emoji).arg(city_name).arg(condition_text).arg(temp_c).arg(time_str).arg(wind_kph).arg(humidity)
        return markdown_fragment, None

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return None, self.tr("Erreur d'authentification. Vérifiez votre clé API.")
        elif e.response.status_code == 400:
            return None, self.tr("Ville non trouvée : '%1'. Vérifiez le nom de la ville.").arg(city)
        else:
            return None, self.tr("Erreur HTTP : %1").arg(e)
    except requests.exceptions.RequestException as e:
        return None, self.tr("Erreur de connexion : %1").arg(e)
    except Exception as e:
        return None, self.tr("Une erreur inattendue est survenue : %1").arg(e)

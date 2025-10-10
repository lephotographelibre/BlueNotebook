"""
Module pour la génération de cartes statiques à partir de coordonnées GPS.
"""

import staticmaps
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable


def get_location_name(lat, lon):
    """
    Récupère le nom de la localité la plus proche pour des coordonnées GPS données.
    """
    try:
        geolocator = Nominatim(user_agent="bluenotebook-app")
        # Utilise 'reverse' pour obtenir l'adresse à partir des coordonnées
        location = geolocator.reverse((lat, lon), exactly_one=True, language="fr")
        if location:
            address = location.raw.get("address", {})
            # Essayer de trouver la ville, le village, etc.
            city = (
                address.get("city")
                or address.get("town")
                or address.get("village")
                or address.get("hamlet", "Lieu inconnu")
            )
            return city
        return "Lieu inconnu"
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Service de géolocalisation indisponible"
    except Exception:
        return "Lieu inconnu"


def create_gps_map(lat, lon, width, height, output_path):
    """
    Crée une carte statique PNG à partir de coordonnées GPS.

    :param lat: Latitude
    :param lon: Longitude
    :param width: Largeur de l'image en pixels
    :param height: Hauteur de l'image en pixels
    :param output_path: Chemin de sauvegarde de l'image PNG
    :return: True si la création a réussi, False sinon.
    """
    if not staticmaps.cairo_is_supported():
        print("⚠️ Cairo n'est pas supporté. Impossible de générer la carte.")
        return False

    try:
        context = staticmaps.Context()
        context.set_tile_provider(staticmaps.tile_provider_OSM)

        place = staticmaps.create_latlng(lat, lon)
        context.add_object(staticmaps.Marker(place, color=staticmaps.RED, size=12))

        # Rendu de l'image
        cairo_image = context.render_cairo(width, height)
        cairo_image.write_to_png(output_path)
        return True
    except Exception as e:
        print(f"Erreur lors de la création de la carte : {e}")
        return False

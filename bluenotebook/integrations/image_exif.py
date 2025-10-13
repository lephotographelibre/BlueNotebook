from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from datetime import datetime


def _get_exif_data(image_path):
    """Extrait les données EXIF brutes d'une image."""
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    except Exception:
        return None


def _get_decimal_from_dms(dms, ref):
    """Convertit les coordonnées GPS DMS en format décimal."""
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0

    decimal = degrees + minutes + seconds
    if ref in ["S", "W"]:
        decimal = -decimal
    return decimal


def _get_gps_info(exif_data):
    """Extrait et convertit les informations GPS des données EXIF."""
    if "GPSInfo" not in exif_data:
        return None, None

    gps_info = {
        GPSTAGS.get(tag, tag): value for tag, value in exif_data["GPSInfo"].items()
    }

    lat_dms = gps_info.get("GPSLatitude")
    lon_dms = gps_info.get("GPSLongitude")
    lat_ref = gps_info.get("GPSLatitudeRef")
    lon_ref = gps_info.get("GPSLongitudeRef")

    if lat_dms and lon_dms and lat_ref and lon_ref:
        lat = _get_decimal_from_dms(lat_dms, lat_ref)
        lon = _get_decimal_from_dms(lon_dms, lon_ref)
        return lat, lon
    return None, None


def get_location_name_from_gps(lat, lon):
    """Trouve le nom du lieu à partir des coordonnées GPS."""
    if not lat or not lon:
        return "Lieu inconnu"
    try:
        geolocator = Nominatim(user_agent="bluenotebook_app")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="fr")
        if location:
            address = location.raw.get("address", {})
            # Essayer de trouver la ville, le village, etc.
            city = address.get("city", address.get("town", address.get("village", "")))
            return city if city else location.address.split(",")[0]
        return "Lieu inconnu"
    except (GeocoderTimedOut, GeocoderUnavailable):
        return "Service de géolocalisation indisponible"
    except Exception:
        return "Erreur de géolocalisation"


def format_exif_as_markdown(image_path):
    """Extrait les données EXIF et les formate en bloc HTML <figure>."""
    exif_data = _get_exif_data(image_path)
    if not exif_data:
        return None

    lat, lon = _get_gps_info(exif_data)

    # Si aucune donnée EXIF utile n'est trouvée, on ne retourne rien.
    if not any(
        [
            lat,
            exif_data.get("DateTimeOriginal"),
            exif_data.get("Model"),
        ]
    ):
        return None

    caption_parts = []

    if lat and lon:
        location_name = get_location_name_from_gps(lat, lon) or "Lieu"
        osm_link = f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=16/{lat:.6f}/{lon:.6f}"
        caption_parts.append(f'<a href="{osm_link}">{location_name}</a>')

    if dt_original := exif_data.get("DateTimeOriginal"):
        try:
            dt_obj = datetime.strptime(dt_original, "%Y:%m:%d %H:%M:%S")
            caption_parts.append(dt_obj.strftime("%d/%m/%Y %H:%M"))
        except (ValueError, TypeError):
            pass

    if make := exif_data.get("Make", "").strip():
        caption_parts.append(make)
    if model := exif_data.get("Model", "").strip():
        caption_parts.append(model)

    if f_number := exif_data.get("FNumber"):
        caption_parts.append(f"ƒ/{f_number}")

    if exposure_time := exif_data.get("ExposureTime"):
        try:
            if exposure_time > 0:
                speed = f"1/{int(1/exposure_time)}s"
            else:
                speed = f"{exposure_time}s"
        except (ZeroDivisionError, ValueError):
            speed = f"{exposure_time}"
        caption_parts.append(f"Vitesse: {speed}")

    if focal_length := exif_data.get("FocalLength"):
        caption_parts.append(f"Focale: {focal_length}mm")

    if iso := exif_data.get("ISOSpeedRatings"):
        caption_parts.append(f"ISO: {iso}")

    caption_text = " : ".join(filter(None, caption_parts))
    return f'<figcaption style="font-weight: bold;">{caption_text}</figcaption>'

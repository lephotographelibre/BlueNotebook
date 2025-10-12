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
    """Extrait les données EXIF et les formate en tableau Markdown."""
    exif_data = _get_exif_data(image_path)
    if not exif_data:
        return None

    lat, lon = _get_gps_info(exif_data)
    location_name = get_location_name_from_gps(lat, lon) if lat and lon else None

    dt_original = exif_data.get("DateTimeOriginal")
    make = exif_data.get("Make", "").strip()
    model = exif_data.get("Model", "").strip()
    f_number = exif_data.get("FNumber")
    exposure_time = exif_data.get("ExposureTime")
    focal_length = exif_data.get("FocalLength")
    iso = exif_data.get("ISOSpeedRatings")

    # Si aucune donnée utile n'est trouvée, on ne retourne rien
    if not any([lat, dt_original, model]):
        return None

    # Toujours commencer par un en-tête pour un tableau propre
    md_table = "\n| Propriété | Valeur |\n|---|---|\n"

    if location_name:
        md_table += f"| Lieu | {location_name} |\n"
    if lat and lon:
        md_table += f"| Coordonnées GPS | [{lat:.6f}, {lon:.6f}] |\n"
        md_table += f"| OpenStreetMap | <https://www.openstreetmap.org/#map=16/{lat:.6f}/{lon:.6f}> |\n"
    if dt_original:
        try:
            dt_obj = datetime.strptime(dt_original, "%Y:%m:%d %H:%M:%S")
            md_table += f"| Date et Heure de la prise de vue | {dt_obj.strftime('%d/%m/%Y %H:%M')} |\n"
        except (ValueError, TypeError):
            pass
    if make or model:
        md_table += f"| Appareil | {make} {model} |\n"
    if f_number:
        md_table += f"| Ouverture | ƒ/{f_number} |\n"
    if exposure_time:
        try:
            speed = (
                f"1/{int(1/exposure_time)}" if exposure_time > 0 else f"{exposure_time}"
            )
        except (ZeroDivisionError, ValueError):
            speed = f"{exposure_time}"
        md_table += f"| Vitesse | {speed} |\n"
    if focal_length:
        md_table += f"| Focale | {focal_length}mm |\n"
    if iso:
        md_table += f"| ISO | {iso} |\n"

    return md_table

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
Module pour la génération de cartes statiques à partir de fichiers de trace GPX.
"""

import os
import re
import datetime
from pathlib import Path

import gpxpy
import requests
import staticmaps

from .gps_map_generator import get_location_name


def get_gpx_data(gpx_input: str) -> bytes | None:
    """
    Récupère le contenu d'un fichier GPX, qu'il soit local ou distant (URL).
    """
    if gpx_input.startswith(("http://", "https://")):
        try:
            response = requests.get(gpx_input, timeout=15)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            print(f"Erreur de téléchargement du fichier GPX : {e}")
            return None
    else:
        gpx_path = Path(gpx_input)
        if gpx_path.exists():
            return gpx_path.read_bytes()
        else:
            print(f"Fichier GPX local non trouvé : {gpx_input}")
            return None


def create_gpx_trace_map(
    gpx_content: bytes,
    journal_dir: Path,
    width: int,
    start_icon_path: str,
) -> dict | str:
    """
    Analyse un GPX, génère une carte, sauvegarde les fichiers et retourne les informations pour l'HTML.
    """
    if not staticmaps.cairo_is_supported():
        return "❌ Carte GPX: La bibliothèque Cairo n'est pas installée ou supportée. Impossible de générer la carte."

    try:
        gpx = gpxpy.parse(gpx_content)
    except gpxpy.gpx.GPXException as e:
        return f"❌ Carte GPX:Erreur lors de l'analyse du fichier GPX : {e}"

    # Extraire les informations du GPX
    start_time, end_time = gpx.get_time_bounds()
    start_point = next(gpx.walk(only_points=True), None)

    if not start_point:
        return "❌ Carte GPX:Le fichier GPX ne contient aucun point de trace."

    if not start_time:
        start_time = datetime.datetime.now()

    # Déterminer le nom du lieu et les chemins de sauvegarde
    location_name = get_location_name(start_point.latitude, start_point.longitude)
    safe_location_name = re.sub(r"[^a-zA-Z0-9_-]", "", location_name.replace(" ", "_"))
    date_str = start_time.strftime("%Y%m%d")

    # Sauvegarder le fichier GPX dans le journal
    gpx_dir = journal_dir / "gpx"
    gpx_dir.mkdir(exist_ok=True)
    gpx_filename = f"{date_str}_{safe_location_name}.gpx"
    gpx_save_path = gpx_dir / gpx_filename
    gpx_save_path.write_bytes(gpx_content)

    # Créer le contexte de la carte
    context = staticmaps.Context()
    context.set_tile_provider(staticmaps.tile_provider_OSM)

    # Ajouter la trace GPX
    for track in gpx.tracks:
        for segment in track.segments:
            line = [
                staticmaps.create_latlng(p.latitude, p.longitude)
                for p in segment.points
            ]
            context.add_object(staticmaps.Line(line))

    # Ajouter le marqueur de départ
    start_pos = staticmaps.create_latlng(start_point.latitude, start_point.longitude)
    if Path(start_icon_path).exists():
        marker = staticmaps.ImageMarker(
            start_pos, start_icon_path, origin_x=13, origin_y=24
        )
        context.add_object(marker)
    else:
        # Fallback si l'icône n'est pas trouvée
        context.add_object(staticmaps.Marker(start_pos, color=staticmaps.RED, size=12))

    # Générer et sauvegarder l'image de la carte
    images_dir = journal_dir / "images"
    images_dir.mkdir(exist_ok=True)
    image_filename = f"{date_str}_{safe_location_name}_gpx.png"
    image_path = images_dir / image_filename
    height = int(width * (10 / 16))  # Ratio 16:10

    try:
        image = context.render_cairo(width, height)
        image.write_to_png(str(image_path))
    except Exception as e:
        return f"❌ Carte GPX:Erreur lors de la génération de l'image de la carte : {e}"

    # Préparer les informations pour le bloc HTML
    osm_link = f"https://www.openstreetmap.org/#map=16/{start_point.latitude}/{start_point.longitude}"
    location_osm_link = f"https://www.openstreetmap.org/?mlat={start_point.latitude}&mlon={start_point.longitude}#map=16/{start_point.latitude}/{start_point.longitude}"
    alt_text = f"Trace GPX - {location_name}"

    # Formatage de la légende
    start_str = start_time.strftime("%d/%m/%Y à %H:%M")

    # Rendre le nom du lieu cliquable dans la légende
    location_html = f'<a href="{location_osm_link}" target="_blank">{location_name}</a>'
    caption_parts = [f"Trace GPX: {location_html}", start_str]

    if end_time:
        duration = end_time - start_time
        duration_str = str(datetime.timedelta(seconds=int(duration.total_seconds())))
        caption_parts.append(f"Durée: {duration_str}")

    caption = " - ".join(caption_parts)

    return {
        "relative_image_path": f"images/{image_filename}",
        "osm_link": osm_link,
        "alt_text": alt_text,
        "caption": caption,
        "width": width,
    }

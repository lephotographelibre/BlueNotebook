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
Gère la logique d'insertion d'une carte statique à partir de coordonnées GPS.
"""

import re
from datetime import datetime
from pathlib import Path

from .gps_map_generator import get_location_name, create_gps_map


def generate_gps_map_markdown(
    lat: float, lon: float, width: int, journal_dir: Path
) -> tuple[str | None, str | None]:
    """
    Génère une carte GPS, la sauvegarde et retourne le fragment Markdown correspondant.

    :param lat: Latitude.
    :param lon: Longitude.
    :param width: Largeur de l'image en pixels.
    :param journal_dir: Chemin du répertoire du journal.
    :return: Un tuple (markdown_fragment, status_message) en cas de succès,
             ou (None, error_message) en cas d'échec.
    """
    # Valider les coordonnées
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return (
            None,
            self.tr("Coordonnées invalides. La latitude doit être entre -90 et 90, et la longitude entre -180 et 180."),
        )

    # Calculer la hauteur (ratio 16:10)
    height = int(width * (10 / 16))

    # Créer le sous-dossier 'images' s'il n'existe pas
    images_dir = journal_dir / self.tr("images")
    images_dir.mkdir(exist_ok=True)

    # Trouver le nom du lieu
    location_name = get_location_name(lat, lon)
    # Nettoyer le nom pour le nom de fichier
    safe_location_name = re.sub(r"[^a-zA-Z0-9_-]", "", location_name.replace(" ", "_"))

    # Générer le nom de fichier de l'image
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    image_filename = self.tr("%1_carte_%2.png").arg(timestamp).arg(safe_location_name)
    image_path = images_dir / image_filename

    # Générer la carte
    success = create_gps_map(lat, lon, width, height, str(image_path))

    if not success:
        return (
            None,
            self.tr("Impossible de générer l'image de la carte. Vérifiez que Cairo est installé."),
        )

    # Construire le bloc Markdown
    relative_image_path = self.tr("images/%1").arg(image_filename)
    osm_link = (
        self.tr("https://www.openstreetmap.org/?mlat=%1&mlon=%2#map=16/%3/%4").arg(lat).arg(lon).arg(lat).arg(lon)
    )
    alt_text = self.tr("Carte de %1, coordonnées %2, %3").arg(location_name).arg(lat).arg(lon)

    markdown_block = (
        self.tr("[![%1](%2)](%3)\n\n").arg(alt_text).arg(relative_image_path).arg(osm_link)
        self.tr("**GPS :** [%1, %2] - [%3](%4)").arg(lat).arg(lon).arg(location_name).arg(osm_link)
    )

    status_message = self.tr("Carte pour '%1' insérée avec succès.").arg(location_name)
    return markdown_block, status_message

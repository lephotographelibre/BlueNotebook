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
Module pour l'intégration des vidéos YouTube.
"""

import re
import requests
from bs4 import BeautifulSoup
import os


def _extract_youtube_id(url: str) -> str | None:
    """Extrait l'ID de la vidéo à partir de différentes formes d'URL YouTube."""
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None


def get_youtube_video_details(url: str) -> dict | str:
    """
    Récupère les détails d'une vidéo YouTube (ID et titre) à partir d'une URL.

    :param url: L'URL de la vidéo YouTube.
    :return: Un dictionnaire avec les détails en cas de succès, ou une chaîne d'erreur en cas d'échec.
    """
    video_id = _extract_youtube_id(url)
    if not video_id:
        return "L'URL YouTube fournie n'est pas valide."

    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return "La vidéo YouTube demandée n'existe pas ou est privée."

        soup = BeautifulSoup(response.text, "html.parser")
        video_title = "Vidéo YouTube"  # Titre par défaut
        if soup.title and soup.title.string:
            title_text = soup.title.string
            # Nettoyer le titre (ex: "Mon Titre - YouTube" -> "Mon Titre")
            if " - YouTube" in title_text:
                video_title = title_text.rsplit(" - YouTube", 1)[0]
            else:
                video_title = title_text

        return {"video_id": video_id, "title": video_title, "url": url}

    except requests.RequestException as e:
        return f"Impossible de vérifier la vidéo : {e}"


def generate_youtube_html_block(video_id, video_url, video_title) -> str:
    """
    Génère le fragment HTML complet pour une vidéo YouTube, incluant le style CSS.
    """
    thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"

    html_block = f"""
@@Video @@Youtube {video_title} <{video_url}>
<figure class="youtube-video-figure">
    <a href="{video_url}" target="_blank" title="Lancer la vidéo dans le navigateur">
        <img src="{thumbnail_url}" alt="{video_title}" style="max-width: 480px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    </a>
    <figcaption style="font-size: 0.9em; margin-top: 0.5em;">
        <a href="{video_url}" target="_blank" style="text-decoration: none; color: #ff0000;">
            <span>Voir sur YouTube : {video_url}</span>
        </a>
    </figcaption>
</figure>
"""
    return html_block

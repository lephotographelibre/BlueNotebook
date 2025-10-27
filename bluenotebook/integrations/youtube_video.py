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
import json


def _extract_youtube_id(url: str) -> str | None:
    """Extrait l'ID de la vidéo à partir de différentes formes d'URL YouTube."""
    regex = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None


def _extract_playlist_id(url: str) -> str | None:
    """Extrait l'ID de la playlist à partir d'une URL YouTube."""
    regex = r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)"
    match = re.search(regex, url)
    return match.group(1) if match else None


def get_youtube_video_details(url: str) -> dict | str:
    """
    Récupère les détails d'une vidéo YouTube (ID et titre) à partir d'une URL.

    :param url: L'URL de la vidéo YouTube.
    :return: Un dictionnaire avec les détails en cas de succès, ou une chaîne d'erreur en cas d'échec.
    """
    playlist_id = _extract_playlist_id(url)
    if playlist_id:
        return _get_playlist_details(url, playlist_id)

    video_id = _extract_youtube_id(url)
    if video_id:
        return _get_video_details(url, video_id)

    return "L'URL fournie n'est pas une URL de vidéo ou de playlist YouTube valide."


def _get_video_details(url: str, video_id: str) -> dict | str:
    """Récupère les détails pour une seule vidéo."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        video_title = "Vidéo YouTube"
        if soup.title and soup.title.string:
            title_text = soup.title.string
            if " - YouTube" in title_text:
                video_title = title_text.rsplit(" - YouTube", 1)[0]
            else:
                video_title = title_text

        return {
            "type": "video",
            "video_id": video_id,
            "title": video_title,
            "url": url,
        }
    except requests.RequestException as e:
        return f"Impossible de vérifier la vidéo : {e}"


def _get_playlist_details(url: str, playlist_id: str) -> dict | str:
    """Récupère les détails pour une playlist."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # YouTube charge les données via JavaScript. On va chercher le JSON initial.
        match = re.search(r"var ytInitialData = ({.*?});", response.text)
        if not match:
            return "Impossible de trouver les données initiales de la playlist."

        data = json.loads(match.group(1))

        # Naviguer dans la structure JSON pour trouver les informations
        header = data.get("header", {}).get("playlistHeaderRenderer", {})

        title = header.get("title", {}).get("simpleText", "Playlist YouTube")

        # L'auteur peut être dans plusieurs endroits selon le type de playlist
        owner_text_runs = header.get("ownerText", {}).get("runs")
        if owner_text_runs:
            owner_text = owner_text_runs[0].get("text", "Inconnu")
        else:
            # Fallback pour les playlists d'albums (ex: "Topic")
            owner_text = header.get("subtitle", {}).get("simpleText", "Inconnu")

        # Le nombre de pistes est dans les "stats" ou dans le "subtitle" pour les albums
        stats = header.get("stats", [])
        track_count = "N/A"
        if stats:
            for stat in stats:
                text_runs = stat.get("runs")
                if text_runs and "vidéo" in text_runs[0].get("text", ""):
                    track_count = "".join([run.get("text", "") for run in text_runs])
                    break
        else:
            # Fallback pour les playlists d'albums
            if subtitle_runs := header.get("subtitle", {}).get("runs"):
                if len(subtitle_runs) > 2 and "vidéo" in subtitle_runs[2].get(
                    "text", ""
                ):
                    track_count = subtitle_runs[2].get("text")

        # La miniature est dans le premier élément de la liste de vidéos
        thumbnail_url = ""
        try:
            first_video_renderer = data["contents"]["twoColumnBrowseResultsRenderer"][
                "tabs"
            ][0]["tabRenderer"]["content"]["sectionListRenderer"]["contents"][0][
                "itemSectionRenderer"
            ][
                "contents"
            ][
                0
            ][
                "playlistVideoListRenderer"
            ][
                "contents"
            ][
                0
            ][
                "playlistVideoRenderer"
            ]
            thumbnails = first_video_renderer.get("thumbnail", {}).get("thumbnails", [])
            if thumbnails:
                # On prend la meilleure qualité disponible (la dernière de la liste)
                thumbnail_url = thumbnails[-1].get("url")
        except (KeyError, IndexError):
            # Si la structure est différente ou la liste est vide, on n'a pas de miniature
            pass

        return {
            "type": "playlist",
            "playlist_id": playlist_id,
            "title": title,
            "author": owner_text,
            "track_count": track_count,
            "thumbnail_url": thumbnail_url,
            "url": url,
        }
    except requests.RequestException as e:
        return f"Impossible de vérifier la playlist : {e}"


def generate_youtube_markdown_block(details: dict) -> str:
    """
    Génère le fragment Markdown complet pour une vidéo ou une playlist YouTube.
    """
    if details["type"] == "video":
        tags = f"@@Video @@Youtube {details['title']} [Voir sur YouTube : {details['url']}]({details['url']})"
        thumbnail_url = (
            f"https://img.youtube.com/vi/{details['video_id']}/hqdefault.jpg"
        )
    elif details["type"] == "playlist":
        tags = f"@@Musique @@Youtube @@Playlist {details['title']} [{details['author']} - {details['track_count']}]({details['url']})"
        thumbnail_url = details["thumbnail_url"]
    else:
        return ""

    # Format Markdown : Tags et lien texte sur la première ligne, image cliquable sur la seconde.
    markdown_block = f"""
{tags}

[![{details['title']}]({thumbnail_url})]({details['url']})
"""
    return markdown_block.strip()

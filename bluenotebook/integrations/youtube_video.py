"""
Module pour l'intégration des vidéos YouTube.
"""

import re
import requests
from bs4 import BeautifulSoup


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

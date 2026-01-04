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

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import Formatter
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QCoreApplication


class YoutubeVideoContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("YoutubeVideoContext", text)


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

    return YoutubeVideoContext.tr(
        "L'URL fournie n'est pas une URL de vidéo ou de playlist YouTube valide."
    )


def _get_video_details(url: str, video_id: str) -> dict | str:
    """Récupère les détails pour une seule vidéo."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        video_title = YoutubeVideoContext.tr("Vidéo YouTube")
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
        return YoutubeVideoContext.tr(
            "Impossible de vérifier la vidéo : {error}"
        ).format(error=e)


def _get_playlist_details(url: str, playlist_id: str) -> dict | str:
    """Récupère les détails pour une playlist."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        match = re.search(r"var ytInitialData = ({.*?});", response.text)
        if not match:
            return YoutubeVideoContext.tr(
                "Impossible de trouver les données initiales de la playlist."
            )

        data = json.loads(match.group(1))

        header = data.get("header", {}).get("playlistHeaderRenderer", {})

        title = header.get("title", {}).get(
            "simpleText", YoutubeVideoContext.tr("Playlist YouTube")
        )

        owner_text_runs = header.get("ownerText", {}).get("runs")
        if owner_text_runs:
            owner_text = owner_text_runs[0].get(
                "text", YoutubeVideoContext.tr("Inconnu")
            )
        else:
            owner_text = header.get("subtitle", {}).get(
                "simpleText", YoutubeVideoContext.tr("Inconnu")
            )

        track_count = "N/A"

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
                thumbnail_url = thumbnails[-1].get("url")
        except (KeyError, IndexError):
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
        return YoutubeVideoContext.tr(
            "Impossible de vérifier la playlist : {error}"
        ).format(error=e)


def generate_youtube_markdown_block(details: dict) -> str:
    """
    Génère le fragment Markdown complet pour une vidéo ou une playlist YouTube.
    """
    if details["type"] == "video":
        tags = YoutubeVideoContext.tr(
            "@@Youtube {title} [Voir sur YouTube : {url}]({url})"
        ).format(title=details["title"], url=details["url"])
        thumbnail_url = (
            f"https://img.youtube.com/vi/{details['video_id']}/hqdefault.jpg"
        )
    elif details["type"] == "playlist":
        tags = YoutubeVideoContext.tr(
            "@@Youtube Playlist {title} [{author} - {count}]({url})"
        ).format(
            title=details["title"],
            author=details["author"],
            count=details["track_count"],
            url=details["url"],
        )
        thumbnail_url = details["thumbnail_url"]
    else:
        return ""

    alt_text = details["title"]

    markdown_block = f"""
{tags}

[![{alt_text}]({thumbnail_url})]({details['url']})
"""
    return markdown_block.strip()


class ParagraphFormatter(Formatter):
    """
    Formate le transcript en paragraphes en se basant sur les pauses temporelles
    et la ponctuation de fin de phrase.
    """

    def format_transcript(self, transcript, pause_threshold=1.0):
        """
        Formate le transcript en paragraphes.
        :param transcript: Liste de snippets du transcript.
        :param pause_threshold: Seuil de pause (en secondes) pour séparer les paragraphes.
        :return: Texte formaté en paragraphes.
        """
        paragraphs = []
        current_paragraph = []
        previous_end_time = 0

        for snippet in transcript:
            text = snippet.text.strip()
            start_time = snippet.start
            duration = snippet.duration
            end_time = start_time + duration

            if not text or re.match(r"^\[.*\]$", text):
                continue

            pause = start_time - previous_end_time if current_paragraph else 0

            is_sentence_end = text.endswith((".", "!", "?"))
            if pause > pause_threshold or (is_sentence_end and current_paragraph):
                if current_paragraph:
                    paragraphs.append(" ".join(current_paragraph))
                    current_paragraph = []

            current_paragraph.append(text)
            previous_end_time = end_time

        if current_paragraph:
            paragraphs.append(" ".join(current_paragraph))

        return "\n\n".join(paragraphs)


def get_youtube_transcript(video_id: str) -> tuple[str | None, str | None]:
    """
    Tente de récupérer et de formater la transcription pour une vidéo YouTube.

    :param video_id: L'ID de la vidéo YouTube.
    :return: Un tuple (formatted_transcript, language_code) ou (None, None) en cas d'échec.
    """
    print(f"🎥 [Transcript] Looking for a transcript for video ID: {video_id}")
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        print(
            f"🎥 [Transcript] Available languages found: {[t.language_code for t in transcript_list]}"
        )

        target_transcript = None
        for lang in ["fr", "en"]:
            try:
                target_transcript = transcript_list.find_transcript([lang])
                print(f"🎥 [Transcript] Transcript found for the language: '{lang}'")
                break
            except Exception:
                print(f"🎥 [Transcript] No Transcript found for the language: '{lang}'")
                continue

        if not target_transcript:
            print("🎥 [Transcript] No transcript found in 'fr' or 'en'. Abandoned.")
            return None, None

        fetched_transcript = target_transcript.fetch()
        if not fetched_transcript:
            print("🎥 [Transcript] Error: The transcript is empty after retrieval.")
            return None, None

        print("🎥 [Transcript] Text formatting...")
        formatter = ParagraphFormatter()
        formatted_text = formatter.format_transcript(
            fetched_transcript, pause_threshold=1.5
        )
        return formatted_text, target_transcript.language_code
    except Exception as e:
        print(f"❌ [Transcript] An error has occurred: {e}")
        return None, None


class TranscriptWorker(QRunnable):
    """Worker pour récupérer la transcription en arrière-plan."""

    class Signals(QObject):
        finished = pyqtSignal(str, str)  # transcript, lang
        error = pyqtSignal(str)
        no_transcript = pyqtSignal()

    def __init__(self, video_id: str):
        super().__init__()
        self.video_id = video_id
        self.signals = self.Signals()

    @pyqtSlot()
    def run(self):
        """Exécute la tâche de récupération."""
        try:
            ytt_api = YouTubeTranscriptApi()
            transcript_list = ytt_api.list(self.video_id)

            target_transcript = None
            for lang in ["fr", "en"]:
                try:
                    target_transcript = transcript_list.find_transcript([lang])
                    break
                except Exception:
                    continue

            if not target_transcript:
                self.signals.no_transcript.emit()
                return

            fetched_transcript = target_transcript.fetch()
            if not fetched_transcript:
                self.signals.no_transcript.emit()
                return

            formatter = ParagraphFormatter()
            formatted_text = formatter.format_transcript(
                fetched_transcript, pause_threshold=1.5
            )
            self.signals.finished.emit(formatted_text, target_transcript.language_code)

        except Exception as e:
            message = YoutubeVideoContext.tr(
                "Erreur lors de la récupération de la transcription : {error}"
            ).format(error=e)
            self.signals.error.emit(message)

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
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


def _extract_youtube_id(url: str) -> str | None:
    """Extrait l'ID de la vidéo à partir de différentes formes d'URL YouTube."""
    regex = self.tr(r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})")
    match = re.search(regex, url)
    return match.group(1) if match else None


def _extract_playlist_id(url: str) -> str | None:
    """Extrait l'ID de la playlist à partir d'une URL YouTube."""
    regex = self.tr(r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/playlist\?list=([a-zA-Z0-9_-]+)")
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

    return self.tr("L'URL fournie n'est pas une URL de vidéo ou de playlist YouTube valide.")


def _get_video_details(url: str, video_id: str) -> dict | str:
    """Récupère les détails pour une seule vidéo."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, self.tr("html.parser"))
        video_title = self.tr("Vidéo YouTube")
        if soup.title and soup.title.string:
            title_text = soup.title.string
            if self.tr(" - YouTube") in title_text:
                video_title = title_text.rsplit(self.tr(" - YouTube"), 1)[0]
            else:
                video_title = title_text

        return {
            self.tr("type"): self.tr("video"),
            self.tr("video_id"): video_id,
            self.tr("title"): video_title,
            self.tr("url"): url,
        }
    except requests.RequestException as e:
        return self.tr("Impossible de vérifier la vidéo : %1").arg(e)


def _get_playlist_details(url: str, playlist_id: str) -> dict | str:
    """Récupère les détails pour une playlist."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # YouTube charge les données via JavaScript. On va chercher le JSON initial.
        match = re.search(self.tr(r"var ytInitialData = ({.*?});"), response.text)
        if not match:
            return self.tr("Impossible de trouver les données initiales de la playlist.")

        data = json.loads(match.group(1))

        # Naviguer dans la structure JSON pour trouver les informations
        header = data.get(self.tr("header"), {}).get(self.tr("playlistHeaderRenderer"), {})

        title = header.get(self.tr("title"), {}).get(self.tr("simpleText"), self.tr("Playlist YouTube"))

        # L'auteur peut être dans plusieurs endroits selon le type de playlist
        owner_text_runs = header.get(self.tr("ownerText"), {}).get(self.tr("runs"))
        if owner_text_runs:
            owner_text = owner_text_runs[0].get(self.tr("text"), self.tr("Inconnu"))
        else:
            # Fallback pour les playlists d'albums (ex: "Topic")
            owner_text = header.get(self.tr("subtitle"), {}).get(self.tr("simpleText"), self.tr("Inconnu"))

        # Le nombre de pistes est dans les "stats" ou dans le "subtitle" pour les albums
        stats = header.get(self.tr("stats"), [])
        track_count = self.tr("N/A")
        if stats:
            for stat in stats:
                text_runs = stat.get(self.tr("runs"))
                if text_runs and self.tr("vidéo") in text_runs[0].get(self.tr("text"), self.tr("")):
                    track_count = self.tr("").join([run.get(self.tr("text"), self.tr("")) for run in text_runs])
                    break
        else:
            # Fallback pour les playlists d'albums
            if subtitle_runs := header.get(self.tr("subtitle"), {}).get(self.tr("runs")):
                if len(subtitle_runs) > 2 and self.tr("vidéo") in subtitle_runs[2].get(
                    self.tr("text"), self.tr("")
                ):
                    track_count = subtitle_runs[2].get(self.tr("text"))

        # La miniature est dans le premier élément de la liste de vidéos
        thumbnail_url = self.tr("")
        try:
            first_video_renderer = data[self.tr("contents")][self.tr("twoColumnBrowseResultsRenderer")][
                self.tr("tabs")
            ][0][self.tr("tabRenderer")][self.tr("content")][self.tr("sectionListRenderer")][self.tr("contents")][0][
                self.tr("itemSectionRenderer")
            ][
                self.tr("contents")
            ][
                0
            ][
                self.tr("playlistVideoListRenderer")
            ][
                self.tr("contents")
            ][
                0
            ][
                self.tr("playlistVideoRenderer")
            ]
            thumbnails = first_video_renderer.get(self.tr("thumbnail"), {}).get(self.tr("thumbnails"), [])
            if thumbnails:
                # On prend la meilleure qualité disponible (la dernière de la liste)
                thumbnail_url = thumbnails[-1].get(self.tr("url"))
        except (KeyError, IndexError):
            # Si la structure est différente ou la liste est vide, on n'a pas de miniature
            pass

        return {
            self.tr("type"): self.tr("playlist"),
            self.tr("playlist_id"): playlist_id,
            self.tr("title"): title,
            self.tr("author"): owner_text,
            self.tr("track_count"): track_count,
            self.tr("thumbnail_url"): thumbnail_url,
            self.tr("url"): url,
        }
    except requests.RequestException as e:
        return self.tr("Impossible de vérifier la playlist : %1").arg(e)


def generate_youtube_markdown_block(details: dict) -> str:
    """
    Génère le fragment Markdown complet pour une vidéo ou une playlist YouTube.
    """
    if details[self.tr("type")] == self.tr("video"):
        tags = self.tr("@@Youtube %1 [Voir sur YouTube : %2](%3)").arg(details[self.tr('title')]).arg(details[self.tr('url')]).arg(details[self.tr('url')])
        thumbnail_url = (
            self.tr("https://img.youtube.com/vi/%1/hqdefault.jpg").arg(details[self.tr('video_id')])
        )
    elif details[self.tr("type")] == self.tr("playlist"):
        tags = self.tr("@@Musique @@Youtube @@Playlist %1 [%2 - %3](%4)").arg(details[self.tr('title')]).arg(details[self.tr('author')]).arg(details[self.tr('track_count')]).arg(details[self.tr('url')])
        thumbnail_url = details[self.tr("thumbnail_url")]
    else:
        return self.tr("")

    # Format Markdown : Tags et lien texte sur la première ligne, image cliquable sur la seconde.
    markdown_block = self.tr("\n%1\n\n[![%2](%3)](%4)\n").arg(tags).arg(details[self.tr('title')]).arg(thumbnail_url).arg(details[self.tr('url')])
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

            # Ignorer les snippets vides ou les annotations comme [Musique]
            if not text or re.match(r"^\[.*\]$", text):
                continue

            # Calculer la pause avec le snippet précédent
            pause = start_time - previous_end_time if current_paragraph else 0

            # Créer un nouveau paragraphe si la pause est significative ou si une phrase se termine
            is_sentence_end = text.endswith((".", "!", "?"))
            if pause > pause_threshold or (is_sentence_end and current_paragraph):
                if current_paragraph:
                    paragraphs.append(self.tr(" ").join(current_paragraph))
                    current_paragraph = []

            current_paragraph.append(text)
            previous_end_time = end_time

        # Ajouter le dernier paragraphe s'il existe
        if current_paragraph:
            paragraphs.append(self.tr(" ").join(current_paragraph))

        return self.tr("\n\n").join(paragraphs)


def get_youtube_transcript(video_id: str) -> tuple[str | None, str | None]:
    """
    Tente de récupérer et de formater la transcription pour une vidéo YouTube.

    :param video_id: L'ID de la vidéo YouTube.
    :return: Un tuple (formatted_transcript, language_code) ou (None, None) en cas d'échec.
    """
    print(self.tr("🎥 [Transcript] Recherche de transcription pour la vidéo ID : %1").arg(video_id))
    try:
        ytt_api = YouTubeTranscriptApi()
        # V3.0.3 - Utilisation de la méthode .list() qui est correcte pour la version installée
        transcript_list = ytt_api.list(video_id)
        print(
            self.tr("🎥 [Transcript] Langues disponibles trouvées : %1").arg([t.language_code for t in transcript_list])
        )

        # Essayer de trouver une transcription en français ou en anglais
        target_transcript = None
        for lang in [self.tr("fr"), self.tr("en")]:
            try:
                target_transcript = transcript_list.find_transcript([lang])
                print(
                    self.tr("🎥 [Transcript] Transcription trouvée pour la langue : '%1'").arg(lang)
                )
                break
            except Exception:
                print(self.tr("🎥 [Transcript] Pas de transcription pour la langue : '%1'").arg(lang))
                continue

        if not target_transcript:
            print(
                self.tr("🎥 [Transcript] Aucune transcription trouvée en 'fr' ou 'en'. Abandon.")
            )
            return None, None

        fetched_transcript = target_transcript.fetch()
        if not fetched_transcript:
            print(
                self.tr("🎥 [Transcript] Erreur : La transcription est vide après récupération.")
            )
            return None, None

        print(self.tr("🎥 [Transcript] Formatage du texte..."))
        formatter = ParagraphFormatter()
        formatted_text = formatter.format_transcript(
            fetched_transcript, pause_threshold=1.5
        )
        return formatted_text, target_transcript.language_code
    except Exception as e:
        print(self.tr("❌ [Transcript] Une erreur est survenue : %1").arg(e))
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
            for lang in [self.tr("fr"), self.tr("en")]:
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
            self.signals.error.emit(
                self.tr("Erreur lors de la récupération de la transcription : %1").arg(e)
            )

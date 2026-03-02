"""
# Copyright (C) 2026 Jean-Marc DIGNE
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

Intégration pour récupérer les métadonnées d'un album de musique via l'API Discogs.
Supporte la recherche par code-barres (EAN/UPC) ou par release ID Discogs."""

import re
import requests

from PyQt5.QtCore import QCoreApplication


DISCOGS_API_URL = "https://api.discogs.com"


class DiscogsContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("DiscogsContext", text)


def _make_headers(token: str) -> dict:
    """Construit les en-têtes HTTP pour l'API Discogs."""
    return {
        "User-Agent": "BlueNotebook/5.0",
        "Authorization": f"Discogs token={token}",
    }


def _parse_query(query: str) -> tuple[str, str]:
    """
    Détermine si la requête est un code-barres ou un release ID Discogs.

    Retourne (type, value) où type est 'barcode' ou 'release_id'.
    """
    query = query.strip()

    # Format [r12345], r12345 ou R12345
    match = re.match(r"^\[?[rR](\d+)\]?$", query)
    if match:
        return "release_id", match.group(1)

    # Chiffres uniquement (espaces tolérés pour les codes-barres)
    digits_only = re.sub(r"\s+", "", query)
    if digits_only.isdigit():
        # Les release IDs Discogs ont généralement < 10 chiffres
        # Les codes-barres EAN-8/UPC-A/EAN-13 ont 8, 12 ou 13 chiffres
        if len(digits_only) >= 10:
            return "barcode", digits_only
        else:
            return "release_id", digits_only

    # Par défaut, traiter comme code-barres (suppression des espaces)
    return "barcode", digits_only


def _get_release_by_id(release_id: str, token: str) -> tuple[dict | None, str | None]:
    """
    Récupère les détails complets d'un album par son release ID Discogs.

    :param release_id: L'identifiant numérique de la release.
    :param token: Le token API Discogs.
    :return: (release_data, None) en cas de succès, (None, error_message) sinon.
    """
    url = f"{DISCOGS_API_URL}/releases/{release_id}"
    try:
        response = requests.get(url, headers=_make_headers(token), timeout=15)
        if response.status_code == 401:
            return None, DiscogsContext.tr(
                "Token Discogs invalide. Vérifiez vos préférences."
            )
        if response.status_code == 404:
            return None, DiscogsContext.tr(
                "Aucun album trouvé pour l'identifiant « {release_id} »."
            ).format(release_id=release_id)
        response.raise_for_status()
        return response.json(), None
    except requests.RequestException as e:
        return None, DiscogsContext.tr(
            "Erreur réseau lors de la récupération de l'album : {error}"
        ).format(error=str(e))


def _search_by_barcode(barcode: str, token: str) -> tuple[dict | None, str | None]:
    """
    Recherche un album par code-barres via l'API Discogs, puis récupère ses détails.

    :param barcode: Le code-barres nettoyé (chiffres uniquement).
    :param token: Le token API Discogs.
    :return: (release_data, None) en cas de succès, (None, error_message) sinon.
    """
    url = f"{DISCOGS_API_URL}/database/search"
    params = {"barcode": barcode, "type": "release"}
    try:
        response = requests.get(
            url, headers=_make_headers(token), params=params, timeout=15
        )
        if response.status_code == 401:
            return None, DiscogsContext.tr(
                "Token Discogs invalide. Vérifiez vos préférences."
            )
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        if not results:
            return None, DiscogsContext.tr(
                "Aucun album trouvé pour le code-barres « {barcode} »."
            ).format(barcode=barcode)
        release_id = str(results[0].get("id", ""))
        if not release_id:
            return None, DiscogsContext.tr(
                "Impossible d'extraire l'identifiant de l'album depuis les résultats."
            )
        print(f"🎵 Discogs : Barcode {barcode} → release ID {release_id}")
        return _get_release_by_id(release_id, token)
    except requests.RequestException as e:
        return None, DiscogsContext.tr(
            "Erreur réseau lors de la recherche par code-barres : {error}"
        ).format(error=str(e))


def get_discogs_album(query: str, token: str) -> tuple[dict | None, str | None]:
    """
    Récupère les métadonnées d'un album Discogs à partir d'un code-barres ou d'un release ID.

    :param query: Code-barres (ex: '5 099703 203226') ou release ID
                  (ex: 'r29696215', '[r29696215]', ou '29696215').
    :param token: Token API Discogs.
    :return: (release_data, None) en cas de succès, (None, error_message) sinon.
    """
    if not token:
        return None, DiscogsContext.tr(
            "Le token Discogs n'est pas configuré. "
            "Veuillez le renseigner dans 'Préférences > Intégrations'."
        )

    query = query.strip()
    if not query:
        return None, DiscogsContext.tr(
            "Veuillez saisir un code-barres ou un identifiant de release."
        )

    query_type, value = _parse_query(query)

    if query_type == "release_id":
        print(f"🎵 Discogs : search using release ID {value}")
        return _get_release_by_id(value, token)
    else:
        print(f"🎵 Discogs : search using barcode {value}")
        return _search_by_barcode(value, token)


def generate_discogs_markdown(release_data: dict) -> str:
    """
    Génère un fragment Markdown à partir des données d'un album Discogs.

    :param release_data: Dictionnaire des données de la release retourné par l'API.
    :return: Fragment Markdown formaté.
    """
    release_id = release_data.get("id", "")
    title = release_data.get("title", DiscogsContext.tr("Titre inconnu"))

    # Artistes principaux
    artists = release_data.get("artists", [])
    artist_name = artists[0].get("name", "").rstrip("*").strip() if artists else ""

    # Labels
    labels_list = release_data.get("labels", [])
    labels_parts = []
    for lbl in labels_list:
        name = lbl.get("name", "")
        catno = lbl.get("catno", "")
        if catno and catno.upper() != "NONE":
            labels_parts.append(f"{name} – {catno}")
        elif name:
            labels_parts.append(name)
    labels_str = ", ".join(labels_parts)

    # Formats
    formats_list = release_data.get("formats", [])
    formats_parts = []
    for fmt in formats_list:
        name = fmt.get("name", "")
        descs = fmt.get("descriptions", [])
        if descs:
            formats_parts.append(f"{name}, {', '.join(descs)}")
        else:
            formats_parts.append(name)
    formats_str = " / ".join(formats_parts)

    country = release_data.get("country", "")
    year = release_data.get("year", "")

    genres = release_data.get("genres", [])
    styles = release_data.get("styles", [])
    genres_str = ", ".join(genres + styles)

    # URL Discogs (le champ uri peut être une URL complète ou un chemin relatif)
    uri = release_data.get("uri", f"/releases/{release_id}")
    if uri.startswith("http"):
        discogs_url = uri
    else:
        discogs_url = f"https://www.discogs.com{uri}" if uri else ""

    # Pochette (image de type "primary" en priorité)
    images = release_data.get("images", [])
    cover_url = ""
    for img in images:
        if img.get("type") == "primary":
            cover_url = img.get("uri", "")
            break
    if not cover_url and images:
        cover_url = images[0].get("uri", "")

    # Tracklist
    tracklist = release_data.get("tracklist", [])

    # Vidéos YouTube proposées par Discogs
    videos = release_data.get("videos", [])
    youtube_videos = [v for v in videos if "youtube.com" in v.get("uri", "")]

    lines = []

    # En-tête avec tag @@Musique : artiste en gras, titre, lien Discogs
    if discogs_url:
        lines.append(
            f"@@Musique **{artist_name}**  {title} [{discogs_url}]({discogs_url})"
        )
    else:
        lines.append(f"@@Musique **{artist_name}**  {title}")
    lines.append("")

    # Pochette
    if cover_url:
        alt_text = DiscogsContext.tr("Pochette de l'album {title}").format(title=title)
        lines.append(f"![{alt_text}]({cover_url})")
        lines.append("")

    # Métadonnées
    if labels_str:
        lines.append(
            DiscogsContext.tr("- **Label**: {labels}").format(labels=labels_str)
        )
    if formats_str:
        lines.append(
            DiscogsContext.tr("- **Format**: {formats}").format(formats=formats_str)
        )
    if country:
        lines.append(DiscogsContext.tr("- **Pays**: {country}").format(country=country))
    if year:
        lines.append(DiscogsContext.tr("- **Sortie**: {year}").format(year=year))
    if genres_str:
        lines.append(
            DiscogsContext.tr("- **Genre**: {genres}").format(genres=genres_str)
        )

    # Tracklist
    if tracklist:
        lines.append("")
        lines.append(DiscogsContext.tr("**Liste des Morceaux**:"))
        lines.append("")
        lines.append(
            DiscogsContext.tr("| Position | Titre | Artiste | Album | Durée |")
        )
        lines.append("|----------|-------|---------|-------|-------|")
        for track in tracklist:
            position = track.get("position", "")
            track_title = track.get("title", "")
            duration = track.get("duration", "")
            # Artiste du morceau (peut différer de l'artiste de l'album)
            track_artists = track.get("artists", [])
            track_artist = (
                track_artists[0].get("name", "").rstrip("*").strip()
                if track_artists
                else artist_name
            )
            lines.append(
                f"| {position} | {track_title} | {track_artist} | {title} | {duration} |"
            )

    # Vidéos YouTube
    if youtube_videos:
        lines.append("")
        lines.append(
            DiscogsContext.tr("**Liste des vidéos Youtube fournies par Discogs**:")
        )
        lines.append("")
        for i, video in enumerate(youtube_videos, 1):
            uri_video = video.get("uri", "")
            video_title = video.get("title", "")
            if video_title:
                lines.append(f"- {i} - [{video_title}]({uri_video})")
            else:
                lines.append(f"- {i} - <{uri_video}>")

    return "\n".join(lines)

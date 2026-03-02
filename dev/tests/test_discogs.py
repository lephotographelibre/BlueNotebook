#!/usr/bin/env python3
"""
test_discogs.py - Récupère les informations d'un album via l'API Discogs
                  et génère un fragment Markdown.

Usage:
    python test_discogs.py <barcode>
    python test_discogs.py <release_id>
    python test_discogs.py --token <TOKEN> <identifiant>

Exemples:
    python test_discogs.py "5 099703 203226"
    python test_discogs.py 5099703203226
    python test_discogs.py r29696215
    python test_discogs.py "[r29696215]"
    python test_discogs.py 29696215
    python test_discogs.py --token MonToken r29696215
"""

import sys
import re
import argparse
import requests

# ── Paramètres ─────────────────────────────────────────────────────────────────
DISCOGS_API_URL = "https://api.discogs.com"
DISCOGS_TOKEN   = "LECkrKUybXFHslaTBcZVwpmjMGntjjSOYRisskYl"  # Remplacez par votre token si necessaire

def build_headers(token: str) -> dict:
    return {
        "User-Agent":    "JMClientRESTCli/1.0",
        "Authorization": f"Discogs token={token}",
    }


# ── Détection automatique du type d'identifiant ────────────────────────────────

def parse_identifier(arg: str):
    """
    Retourne ('release', id_str) ou ('barcode', digits_str).
    Reconnaît :
      - [r12345]  / r12345          → release
      - 12345 (< 8 chiffres)        → release
      - 5 099703 203226  (avec espaces ou 8/12/13 chiffres) → barcode
    """
    arg = arg.strip()

    # Release ID explicite : [r12345] ou r12345
    m = re.match(r'^\[?r(\d+)\]?$', arg, re.IGNORECASE)
    if m:
        return 'release', m.group(1)

    # Retire les espaces pour travailler sur les chiffres bruts
    digits = re.sub(r'\s+', '', arg)

    if re.match(r'^\d+$', digits):
        original_has_spaces = bool(re.search(r'\s', arg))
        n = len(digits)
        # Longueurs EAN-8 (8), UPC-A (12), EAN-13 (13) → code-barre
        # Présence d'espaces dans l'original → code-barre
        if original_has_spaces or n in (8, 12, 13) or n >= 14:
            return 'barcode', digits
        # Nombre court sans espace ni préfixe r → release ID
        return 'release', digits

    return None, None


# ── Appels API ──────────────────────────────────────────────────────────────────

def search_by_barcode(barcode: str, headers: dict) -> str:
    """Cherche une release par code-barre, retourne le premier release_id."""
    url    = f"{DISCOGS_API_URL}/database/search"
    params = {"barcode": barcode, "type": "release"}

    print(f"[INFO] Recherche par code-barre : {barcode}", file=sys.stderr)
    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()
    data    = resp.json()
    results = data.get("results", [])

    if not results:
        print(f"[ERREUR] Aucun résultat pour le code-barre : {barcode}", file=sys.stderr)
        sys.exit(1)

    # Affiche les 5 premiers résultats pour information
    if len(results) > 1:
        print(f"[INFO] {len(results)} résultat(s) – utilisation du premier :", file=sys.stderr)
        for i, r in enumerate(results[:5]):
            print(f"  [{i+1}] ID={r.get('id')}  {r.get('title','?')}  ({r.get('year','?')})",
                  file=sys.stderr)

    return str(results[0]["id"])


def get_release(release_id: str, headers: dict) -> dict:
    """Récupère le détail d'une release Discogs."""
    url = f"{DISCOGS_API_URL}/releases/{release_id}"
    print(f"[INFO] Récupération release ID : {release_id}", file=sys.stderr)
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Helpers ─────────────────────────────────────────────────────────────────────

def format_artists(artists_list: list) -> str:
    """Convertit la liste d'artistes Discogs en chaîne lisible."""
    parts = []
    for a in artists_list:
        name = re.sub(r'\s*\(\d+\)\s*$', '', a.get("name", "")).strip()
        join = a.get("join", "").strip()
        parts.append(name)
        if join and join != ",":
            parts.append(join)
    return " ".join(parts).strip()


def slugify(text: str) -> str:
    """Version simplifiée pour construire un slug d'URL."""
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')


def discogs_web_url(release_id, artists_str: str, title: str) -> str:
    return (
        f"https://www.discogs.com/fr/release/"
        f"{release_id}-{slugify(artists_str)}-{slugify(title)}"
    )


# ── Génération Markdown ──────────────────────────────────────────────────────────

def generate_markdown(release: dict) -> str:
    release_id  = release.get("id", "")
    artists_str = format_artists(release.get("artists", []))
    title       = release.get("title", "Unknown")

    # URL Discogs
    url = discogs_web_url(release_id, artists_str, title)

    # Pochette : préférer l'image "primary", sinon la première
    images    = release.get("images", [])
    cover_url = ""
    for img in images:
        if img.get("type") == "primary":
            cover_url = img.get("uri", "")
            break
    if not cover_url and images:
        cover_url = images[0].get("uri", "")

    # Labels & numéros de catalogue
    labels    = release.get("labels", [])
    label_str = ", ".join(
        f"{l['name']} – {l.get('catno', '')}".rstrip(" –")
        for l in labels if l.get("name")
    ) or "N/A"

    # Format
    formats      = release.get("formats", [])
    format_parts = []
    for f in formats:
        descs      = f.get("descriptions", [])
        qty        = f.get("qty", "1")
        name       = f.get("name", "")
        components = ([f"{qty}×"] if qty != "1" else []) + [name] + descs
        format_parts.append(", ".join(filter(None, components)))
    format_str = " + ".join(format_parts) or "N/A"

    # Pays / Année / Genres
    country   = release.get("country", "N/A")
    year      = release.get("year",    "N/A")
    genres    = release.get("genres",  [])
    styles    = release.get("styles",  [])
    genre_str = ", ".join(genres + styles) or "N/A"
    main_genre = genres[0] if genres else "N/A"

    # Tracklist (uniquement les vraies pistes, pas les titres de section)
    tracklist = [
        t for t in release.get("tracklist", [])
        if t.get("type_", "track") == "track"
    ]

    # Vidéos YouTube
    videos         = release.get("videos", [])
    youtube_links  = [
        v.get("uri", "")
        for v in videos
        if "youtube.com" in v.get("uri", "")
    ]

    # ── Construction du fragment Markdown ─────────────────────────────────────
    L = []

    L.append(f"@@Musique Album  **{artists_str} – {title}** [{url}]({url})")
    L.append("")

    if cover_url:
        L.append(f"![Pochette de l'album {artists_str} - {title}]({cover_url})")
        L.append("")

    L.append(f"**Label**: {label_str}")
    L.append(f"**Format**: {format_str}")
    L.append(f"**Pays**: {country}")
    L.append(f"**Sortie**: {year}")
    L.append(f"**Genre**: {genre_str}")
    L.append("")
    L.append("**Liste des Morceaux**: ")
    L.append("")

    # Largeurs fixes pour l'alignement
    L.append("| Position | Titre                            | Artiste        | Album   | Genre            |")
    L.append("|----------|----------------------------------|----------------|---------|------------------|")

    for track in tracklist:
        pos     = track.get("position", "")
        t_title = track.get("title",    "")
        t_artists_raw = track.get("artists", [])
        t_artist = format_artists(t_artists_raw) if t_artists_raw else artists_str
        L.append(f"| {pos:<8} | {t_title:<32} | {t_artist:<14} | {title:<7} | {main_genre:<16} |")

    L.append("")
    L.append("**Liste des vidéos Youtube fournies par discogs**:")
    L.append("")

    if youtube_links:
        for i, link in enumerate(youtube_links, 1):
            L.append(f"{i} - <{link}>")
    else:
        L.append("*(Aucune vidéo YouTube disponible)*")

    return "\n".join(L)


# ── Point d'entrée ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Génère un fragment Markdown à partir d'un album Discogs.",
        epilog=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "identifier",
        nargs="+",
        help="Code-barre (ex: '5 099703 203226') ou release ID (ex: r29696215)",
    )
    parser.add_argument(
        "--token",
        default=DISCOGS_TOKEN,
        metavar="TOKEN",
        help="Token d'authentification Discogs (écrase la constante du script)",
    )

    args    = parser.parse_args()
    headers = build_headers(args.token)

    # Reconstitue l'identifiant (gère les codes-barres avec espaces passés sans guillemets)
    raw = " ".join(args.identifier)

    input_type, value = parse_identifier(raw)

    if input_type is None:
        parser.error(
            f"Impossible d'interpréter '{raw}' comme un code-barre ou un release ID.\n"
            "  Code-barre : suite de 8/12/13 chiffres (espaces autorisés)\n"
            "  Release ID : r<chiffres>  ou  [r<chiffres>]"
        )

    if input_type == 'barcode':
        release_id = search_by_barcode(value, headers)
    else:
        release_id = value

    release  = get_release(release_id, headers)
    markdown = generate_markdown(release)
    print(markdown)


if __name__ == "__main__":
    main()

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

Intégration pour récupérer les métadonnées d'un livre par ISBN via Google Books API
(sans authentification) avec fallback sur Open Library."""

import re
import requests

from PyQt5.QtCore import QCoreApplication


class GoogleBooksContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("GoogleBooksContext", text)


def _clean_isbn(isbn: str) -> str:
    """Nettoie un ISBN en supprimant les espaces, tirets et autres caractères non numériques."""
    return re.sub(r"[^0-9X]", "", isbn.upper())


def _validate_isbn(isbn: str) -> bool:
    """Valide qu'un ISBN contient 10 ou 13 caractères alphanumériques."""
    return len(isbn) in (10, 13)


def _fetch_google_books(isbn: str) -> dict | None:
    """Récupère les métadonnées depuis Google Books API (sans clé)."""
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("totalItems", 0) == 0 or not data.get("items"):
            return None

        item = data["items"][0]
        volume_info = item.get("volumeInfo", {})

        # Couverture en HTTPS
        image_links = volume_info.get("imageLinks", {})
        cover_url = image_links.get("thumbnail", image_links.get("smallThumbnail", ""))
        if cover_url:
            cover_url = cover_url.replace("http://", "https://")

        # ISBN-13 et ISBN-10
        isbn_13 = isbn if len(isbn) == 13 else ""
        isbn_10 = isbn if len(isbn) == 10 else ""
        for identifier in volume_info.get("industryIdentifiers", []):
            if identifier.get("type") == "ISBN_13":
                isbn_13 = identifier.get("identifier", isbn_13)
            elif identifier.get("type") == "ISBN_10":
                isbn_10 = identifier.get("identifier", isbn_10)

        return {
            "title": volume_info.get("title", ""),
            "subtitle": volume_info.get("subtitle", ""),
            "authors": volume_info.get("authors", []),
            "publisher": volume_info.get("publisher", ""),
            "published_date": volume_info.get("publishedDate", ""),
            "description": volume_info.get("description", ""),
            "page_count": volume_info.get("pageCount", 0),
            "categories": volume_info.get("categories", []),
            "language": volume_info.get("language", ""),
            "cover_url": cover_url,
            "isbn_13": isbn_13,
            "isbn_10": isbn_10,
            "book_url": f"https://books.google.com/books?id={item.get('id', '')}",
            "source": "Google Books",
        }
    except Exception:
        return None


def _fetch_open_library(isbn: str) -> dict | None:
    """Récupère les métadonnées depuis Open Library API (fallback)."""
    url = (
        f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&jscmd=data&format=json"
    )
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        key = f"ISBN:{isbn}"
        if key not in data:
            return None

        book = data[key]

        authors = [a.get("name", "") for a in book.get("authors", [])]
        publishers = [p.get("name", "") for p in book.get("publishers", [])]
        publisher = publishers[0] if publishers else ""

        # Couverture
        covers = book.get("cover", {})
        cover_url = covers.get("large", covers.get("medium", covers.get("small", "")))
        if not cover_url:
            cover_url = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"

        isbn_13 = isbn if len(isbn) == 13 else ""
        isbn_10 = isbn if len(isbn) == 10 else ""
        for id_type, id_values in book.get("identifiers", {}).items():
            if id_type == "isbn_13" and id_values:
                isbn_13 = id_values[0]
            elif id_type == "isbn_10" and id_values:
                isbn_10 = id_values[0]

        ol_key = book.get("key", "")
        book_url = f"https://openlibrary.org{ol_key}" if ol_key else ""

        return {
            "title": book.get("title", ""),
            "subtitle": book.get("subtitle", ""),
            "authors": authors,
            "publisher": publisher,
            "published_date": book.get("publish_date", ""),
            "description": "",  # Open Library fournit rarement des descriptions
            "page_count": book.get("number_of_pages", 0),
            "categories": [s.get("name", "") for s in book.get("subjects", [])[:3]],
            "language": "",
            "cover_url": cover_url,
            "isbn_13": isbn_13,
            "isbn_10": isbn_10,
            "book_url": book_url,
            "source": "Open Library",
        }
    except Exception:
        return None


def get_book_metadata(isbn: str) -> tuple[dict | None, str | None]:
    """
    Récupère les métadonnées d'un livre par ISBN.
    Essaie Google Books en premier, puis Open Library en fallback.

    :param isbn: L'ISBN du livre (10 ou 13 chiffres).
    :return: Un tuple (book_data, None) en cas de succès,
             ou (None, error_message) en cas d'échec.
    """
    clean = _clean_isbn(isbn)

    if not clean:
        return None, GoogleBooksContext.tr("Veuillez saisir un ISBN valide.")

    if not _validate_isbn(clean):
        return None, GoogleBooksContext.tr(
            "L'ISBN « {isbn} » n'est pas valide. Un ISBN doit contenir 10 ou 13 chiffres."
        ).format(isbn=isbn)

    print(f"📚 Recherche des métadonnées pour ISBN : {clean}")

    book_data = _fetch_google_books(clean)
    if book_data:
        print(f"📚 Google Books : trouvé → {book_data.get('title', 'N/A')}")
        return book_data, None

    print("📚 Google Books : non trouvé, tentative avec Open Library...")
    book_data = _fetch_open_library(clean)
    if book_data:
        print(f"📚 Open Library : trouvé → {book_data.get('title', 'N/A')}")
        return book_data, None

    return None, GoogleBooksContext.tr(
        "Aucun livre trouvé pour l'ISBN « {isbn} ».\n"
        "Vérifiez l'ISBN et votre connexion internet."
    ).format(isbn=isbn)


def generate_book_markdown_fragment(book_data: dict) -> str:
    """
    Génère un fragment Markdown à partir des métadonnées d'un livre.

    :param book_data: Dictionnaire contenant les métadonnées du livre.
    :return: Un fragment Markdown formaté.
    """
    title = book_data.get("title") or GoogleBooksContext.tr("Titre inconnu")
    subtitle = book_data.get("subtitle", "")
    authors = book_data.get("authors", [])
    publisher = book_data.get("publisher", "")
    published_date = book_data.get("published_date", "")
    description = book_data.get("description", "")
    page_count = book_data.get("page_count", 0)
    cover_url = book_data.get("cover_url", "")
    isbn_13 = book_data.get("isbn_13", "")
    isbn_10 = book_data.get("isbn_10", "")
    book_url = book_data.get("book_url", "")
    source = book_data.get("source", "")

    full_title = f"{title} : {subtitle}" if subtitle else title
    authors_str = (
        ", ".join(authors) if authors else GoogleBooksContext.tr("Auteur inconnu")
    )

    lines = []

    # Titre en tant qu'en-tête avec lien
    if book_url:
        lines.append(f"@@Book 📚 [{full_title}]({book_url}) - {authors_str}")
    else:
        lines.append(f"@@Book 📚 {full_title} - {authors_str}")

    lines.append("")

    # Tableau : couverture | métadonnées
    meta_parts = []
    meta_parts.append(
        GoogleBooksContext.tr("**Auteur(s) :** {authors}").format(authors=authors_str)
    )
    if publisher:
        meta_parts.append(
            GoogleBooksContext.tr("**Éditeur :** {publisher}").format(
                publisher=publisher
            )
        )
    if published_date:
        meta_parts.append(
            GoogleBooksContext.tr("**Publication :** {date}").format(
                date=published_date
            )
        )
    if page_count:
        meta_parts.append(
            GoogleBooksContext.tr("**Pages :** {pages}").format(pages=page_count)
        )
    if isbn_13:
        meta_parts.append(f"**ISBN-13 :** {isbn_13}")
    if isbn_10:
        meta_parts.append(f"**ISBN-10 :** {isbn_10}")

    meta_cell = "<br>".join(meta_parts)

    if cover_url:
        cover_cell = (
            f"[![{full_title}]({cover_url})]({book_url})"
            if book_url
            else f"![{full_title}]({cover_url})"
        )
        lines.append("| | |")
        lines.append("|:---:|---|")
        lines.append(f"| {cover_cell} | {meta_cell} |")
    else:
        # Sans couverture : liste simple
        for part in meta_parts:
            lines.append(f"- {part}")

    # Description
    if description:
        max_len = 500
        lines.append("")
        if len(description) > max_len:
            short_desc = description[:max_len].rstrip() + "…"
            lines.append(f"> {short_desc}")
            if book_url:
                read_more = GoogleBooksContext.tr("[Lire la suite]({url})").format(
                    url=book_url
                )
                lines.append(f"> {read_more}")
        else:
            lines.append(f"> {description}")

    # Source
    if source:
        lines.append("")
        lines.append(GoogleBooksContext.tr("*Source : {source}*").format(source=source))

    return "\n".join(lines)

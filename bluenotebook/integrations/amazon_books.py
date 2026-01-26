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
Logique pour l'intégration de la recherche de livres par ISBN sur Amazon.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from PyQt5.QtCore import QCoreApplication


class AmazonBooksContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("AmazonBooksContext", text)


def get_book_info_from_amazon(isbn, region="fr"):
    """
    Récupère les métadonnées d'un livre Amazon via ISBN.
    :param isbn: ISBN-13 sans tirets (ex: '9782743664060')
    :param region: 'fr' pour amazon.fr, 'com' pour amazon.com, etc.
    :return: JSON avec métadonnées
    """
    # Nettoie l'ISBN
    isbn = re.sub(r"[^0-9]", "", isbn)
    if len(isbn) not in (10, 13):
        return json.dumps(
            {"error": AmazonBooksContext.tr("ISBN invalide")},
            ensure_ascii=False,
            indent=4,
        )

    # URL de recherche Amazon
    domain = f"amazon.{region}"
    search_url = f"https://www.{domain}/s?k={isbn}&i=stripbooks"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": f"https://www.{domain}/",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # Étape 1: Recherche
        # print(f"Recherche sur {search_url}")
        time.sleep(1)  # Délai politeness
        response = session.get(search_url, timeout=10)
        response.raise_for_status()

        # Parse le HTML
        soup = BeautifulSoup(response.content, "lxml")

        # Vérifie si la page contient un CAPTCHA
        if soup.select_one('form[action="/errors/validateCaptcha"]'):
            return json.dumps(
                {
                    "error": AmazonBooksContext.tr(
                        "CAPTCHA détecté, requête bloquée par Amazon"
                    )
                },
                ensure_ascii=False,
                indent=4,
            )

        # Trouve les liens de produits
        product_links = soup.select(
            'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]'
        )
        product_url = None
        if product_links:
            # Sélectionne le lien pertinent
            for link in product_links:
                href = link.get("href", "")
                asin_match = re.search(r"/dp/([A-Z0-9]{10})", href)
                if asin_match:
                    asin = asin_match.group(1)
                    product_url = f"https://www.{domain}/dp/{asin}"
                    print(f"📚 Amazon ISBN: Selected product link: {product_url}")
                    break

        if not product_url:
            return json.dumps(
                {"error": AmazonBooksContext.tr("Aucun produit trouvé pour cet ISBN")},
                ensure_ascii=False,
                indent=4,
            )

        # Étape 2: Page produit
        print(f"📚 Amazon ISBN: Product page: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Vérifie si la page produit contient un CAPTCHA
        if soup.select_one('form[action="/errors/validateCaptcha"]'):
            return json.dumps(
                {
                    "error": AmazonBooksContext.tr(
                        "CAPTCHA détecté sur la page produit, requête bloquée par Amazon"
                    )
                },
                ensure_ascii=False,
                indent=4,
            )

        # Extraction des métadonnées
        book_data = {}
        title_node = soup.select_one("#productTitle") or soup.select_one(
            "#ebooksProductTitle"
        )
        book_data["titre"] = (
            title_node.get_text(strip=True)
            if title_node
            else AmazonBooksContext.tr("Inconnu")
        )
        authors = soup.select(
            "a.a-link-normal.contributorName, .author a.a-link-normal, span.author a"
        )
        book_data["auteur"] = (
            "; ".join([a.get_text(strip=True) for a in authors])
            if authors
            else AmazonBooksContext.tr("Inconnu")
        )

        # Éditeur
        pub_elem = soup.select_one(
            'div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:-soup-contains("Éditeur") + span, td:-soup-contains("Éditeur") + td'
        )
        book_data["editeur"] = (
            pub_elem.get_text(strip=True)
            if pub_elem
            else AmazonBooksContext.tr("Inconnu")
        )

        # Date publication
        date_elem = soup.select_one(
            'div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:-soup-contains("Date") + span, td:-soup-contains("Date") + td'
        )
        book_data["date_publication"] = (
            date_elem.get_text(strip=True)
            if date_elem
            else AmazonBooksContext.tr("Inconnu")
        )

        # Description
        desc_elem = soup.select_one("#productDescription, #bookDescription_feature_div")
        if desc_elem:
            # Nettoyer le résumé pour enlever les "En lire plus" etc.
            for hidden_span in desc_elem.select("span[style*='display: none']"):
                hidden_span.decompose()
            raw_summary = desc_elem.get_text(strip=True)

            if len(raw_summary) > 500:
                # Tronquer à la fin de la dernière phrase avant 500 caractères
                trunc_limit = 500
                last_period_index = raw_summary.rfind(".", 0, trunc_limit)
                if last_period_index != -1:
                    truncated_summary = raw_summary[: last_period_index + 1]
                else:
                    # Si pas de phrase, couper au dernier mot
                    last_space_index = raw_summary.rfind(" ", 0, trunc_limit)
                    truncated_summary = (
                        raw_summary[:last_space_index]
                        if last_space_index != -1
                        else raw_summary[:trunc_limit]
                    )
                book_data["resume"] = (
                    truncated_summary
                    + "<br>"
                    + AmazonBooksContext.tr("En lire plus...")
                )
            else:
                book_data["resume"] = raw_summary
        else:
            book_data["resume"] = AmazonBooksContext.tr("Non disponible")

        # Pages
        pages_elem = soup.select_one(
            'div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:-soup-contains("pages") + span, td:-soup-contains("pages") + td'
        )
        book_data["pages"] = (
            pages_elem.get_text(strip=True)
            if pages_elem
            else AmazonBooksContext.tr("Inconnu")
        )

        # Note (étoiles)
        rating_elem = soup.select_one("#acrPopover + span .a-icon-alt")
        book_data["note"] = (
            rating_elem.get_text(strip=True)
            if rating_elem
            else AmazonBooksContext.tr("Inconnu")
        )

        book_data["isbn"] = isbn
        book_data["couverture_url"] = (
            soup.select_one("#imgBlkFront, #main-image-container img")["src"]
            if soup.select_one("#imgBlkFront, #main-image-container img")
            else AmazonBooksContext.tr("Non disponible")
        )
        book_data["product_url"] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps(
            {"error": AmazonBooksContext.tr("Erreur de requête : {}").format(str(e))},
            ensure_ascii=False,
            indent=4,
        )
    except Exception as e:
        return json.dumps(
            {"error": AmazonBooksContext.tr("Erreur inattendue : {}").format(str(e))},
            ensure_ascii=False,
            indent=4,
        )


def generate_book_markdown_fragment(book_data_json: str) -> str:
    """
    Génère un fragment Markdown pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment Markdown
    """
    try:
        book_data = json.loads(book_data_json)
        if "error" in book_data:
            return AmazonBooksContext.tr(
                "**Erreur lors de la récupération des informations du livre :** {}"
            ).format(book_data["error"])

        title = book_data.get("titre", AmazonBooksContext.tr("Inconnu"))
        cover_url = book_data.get("couverture_url", "https://via.placeholder.com/150")
        author = book_data.get("auteur", AmazonBooksContext.tr("Inconnu"))
        publisher = book_data.get("editeur", AmazonBooksContext.tr("Inconnu"))
        pub_date = book_data.get("date_publication", AmazonBooksContext.tr("Inconnu"))
        isbn = book_data.get("isbn", AmazonBooksContext.tr("Inconnu"))
        pages = book_data.get("pages", AmazonBooksContext.tr("Inconnu"))
        note = book_data.get("note", AmazonBooksContext.tr("Inconnu"))
        product_url = book_data.get("product_url", "#")

        # Handle summary and "En lire plus..." link
        raw_resume = book_data.get("resume", AmazonBooksContext.tr("Non disponible"))
        resume_text = raw_resume
        resume_more_link_markdown = ""

        en_lire_plus = AmazonBooksContext.tr("En lire plus...")
        split_marker = f"<br>{en_lire_plus}"

        if split_marker in raw_resume:
            parts = raw_resume.split(split_marker)
            resume_text = parts[0].strip()
            if product_url != "#":
                resume_more_link_markdown = AmazonBooksContext.tr(
                    "[{plus}]({url})"
                ).format(plus=en_lire_plus, url=product_url)

        markdown_template = (
            "@@Book **{title} de {author}**\n\n"
            "![{cover_alt}]({cover_url})\n\n"
            "**{author_label}** {author}  \n"
            "**{publisher_label}** {publisher}  \n"
            "**{pub_date_label}** {pub_date}  \n"
            "**{isbn_label}** {isbn}  \n"
            "**{pages_label}** {pages}  \n"
            "**{note_label}** {note}  \n\n"
            "**{summary_label}** {resume_text}  \n"
            "{resume_more_link}\n\n"
            "[{amazon_link_text}]({product_url})"
        )

        markdown_fragment = markdown_template.format(
            title=title,
            author=author,
            cover_alt=AmazonBooksContext.tr("Couverture"),
            cover_url=cover_url,
            author_label=AmazonBooksContext.tr("Auteur :"),
            publisher_label=AmazonBooksContext.tr("Éditeur :"),
            publisher=publisher,
            pub_date_label=AmazonBooksContext.tr("Date de publication :"),
            pub_date=pub_date,
            isbn_label=AmazonBooksContext.tr("ISBN :"),
            isbn=isbn,
            pages_label=AmazonBooksContext.tr("Pages :"),
            pages=pages,
            note_label=AmazonBooksContext.tr("Note :"),
            note=note,
            summary_label=AmazonBooksContext.tr("Résumé :"),
            resume_text=resume_text,
            resume_more_link=resume_more_link_markdown,
            amazon_link_text=AmazonBooksContext.tr("Voir sur Amazon.fr"),
            product_url=product_url,
        )
        return markdown_fragment.strip()

    except json.JSONDecodeError:
        return AmazonBooksContext.tr(
            "**Erreur :** Erreur lors du traitement des données JSON du livre."
        )
    except Exception as e:
        return AmazonBooksContext.tr(
            "**Erreur inattendue lors de la génération du Markdown :** {}"
        ).format(e)

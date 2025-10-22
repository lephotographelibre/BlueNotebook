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
        return json.dumps({"error": "ISBN invalide"}, ensure_ascii=False, indent=4)

    # URL de recherche Amazon
    domain = f"amazon.{region}"
    search_url = f"https://www.{domain}/s?k={isbn}&i=stripbooks"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Referer": f"https://www.{domain}/",
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
                {"error": "CAPTCHA détecté, requête bloquée par Amazon"},
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
                    print(f"📚 Amazon ISBN:Lien produit sélectionné: {product_url}")
                    break

        if not product_url:
            return json.dumps(
                {"error": "Aucun produit trouvé pour cet ISBN"},
                ensure_ascii=False,
                indent=4,
            )

        # Étape 2: Page produit
        print(f"📚 Amazon ISBN:Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        # Extraction des métadonnées
        book_data = {}
        book_data["titre"] = (
            soup.select_one("#productTitle").get_text(strip=True)
            if soup.select_one("#productTitle")
            else "Inconnu"
        )
        authors = soup.select(
            "a.a-link-normal.contributorName, .author a.a-link-normal, span.author a"
        )
        book_data["auteur"] = (
            "; ".join([a.get_text(strip=True) for a in authors])
            if authors
            else "Inconnu"
        )

        # Éditeur
        pub_elem = soup.select_one(
            'div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:-soup-contains("Éditeur") + span, td:-soup-contains("Éditeur") + td'
        )
        book_data["editeur"] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one(
            'div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:-soup-contains("Date") + span, td:-soup-contains("Date") + td'
        )
        book_data["date_publication"] = (
            date_elem.get_text(strip=True) if date_elem else "Inconnu"
        )

        # Description
        desc_elem = soup.select_one("#productDescription, #bookDescription_feature_div")
        if desc_elem:
            # Nettoyer le résumé pour enlever les "En lire plus" etc.
            for hidden_span in desc_elem.select("span[style*='display: none']"):
                hidden_span.decompose()
            raw_summary = desc_elem.get_text(strip=True)

            if len(raw_summary) > 200:
                # Tronquer à la fin de la dernière phrase avant 200 caractères
                trunc_limit = 200
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
                book_data["resume"] = truncated_summary + "<br>En lire plus..."
            else:
                book_data["resume"] = raw_summary
        else:
            book_data["resume"] = "Non disponible"

        # Pages
        pages_elem = soup.select_one(
            'div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:-soup-contains("pages") + span, td:-soup-contains("pages") + td'
        )
        book_data["pages"] = (
            pages_elem.get_text(strip=True) if pages_elem else "Inconnu"
        )

        # Note (étoiles)
        rating_elem = soup.select_one("#acrPopover + span .a-icon-alt")
        book_data["note"] = (
            rating_elem.get_text(strip=True) if rating_elem else "Inconnu"
        )

        book_data["isbn"] = isbn
        book_data["couverture_url"] = (
            soup.select_one("#imgBlkFront, #main-image-container img")["src"]
            if soup.select_one("#imgBlkFront, #main-image-container img")
            else "Non disponible"
        )
        book_data["product_url"] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps(
            {"error": f"Erreur de requête: {str(e)}"}, ensure_ascii=False, indent=4
        )
    except Exception as e:
        return json.dumps(
            {"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4
        )


def generate_html_fragment(book_data_json):
    """
    Génère un fragment HTML pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment HTML
    """
    try:
        book_data = json.loads(book_data_json)
        if "error" in book_data:
            return f"""<div class="book-error"><h2>Erreur</h2><p>{book_data['error']}</p></div>"""

        # Construction du fragment HTML
        html = f"""
<div class="book-container">
    <h2>{book_data.get('titre', 'Inconnu')}</h2>
    <div class="book-content">
        <div class="book-image">
            <img src="{book_data.get('couverture_url', 'https://via.placeholder.com/150')}" alt="Couverture">
        </div>
        <div class="book-details">
            <p><strong>Auteur :</strong> {book_data.get('auteur', 'Inconnu')}</p>
            <p><strong>Éditeur :</strong> {book_data.get('editeur', 'Inconnu')}</p>
            <p><strong>Date de publication :</strong> {book_data.get('date_publication', 'Inconnu')}</p>
            <p><strong>ISBN :</strong> {book_data.get('isbn', 'Inconnu')}</p>
            <p><strong>Pages :</strong> {book_data.get('pages', 'Inconnu')}</p>
            <p><strong>Note :</strong> {book_data.get('note', 'Inconnu')}</p>
            <p><strong>Résumé :</strong> {book_data.get('resume', 'Non disponible')}</p>
            <p><a href="{book_data.get('product_url', '#')}" target="_blank">Voir sur Amazon.fr</a></p>
        </div>
    </div>
</div>
"""
        return html

    except json.JSONDecodeError:
        return """<div class="book-error"><h2>Erreur</h2><p>Erreur lors du traitement des données JSON.</p></div>"""

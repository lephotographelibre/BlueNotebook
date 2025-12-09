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
        return json.dumps({self.tr("error"): self.tr("ISBN invalide")}, ensure_ascii=False, indent=4)

    # URL de recherche Amazon
    domain = self.tr("amazon.%1").arg(region)
    search_url = self.tr("https://www.%1/s?k=%2&i=stripbooks").arg(domain).arg(isbn)

    headers = {
        self.tr("User-Agent"): self.tr("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"),
        self.tr("Accept-Language"): self.tr("fr-FR,fr;q=0.9,en;q=0.8"),
        self.tr("Referer"): self.tr("https://www.%1/").arg(domain),
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # Étape 1: Recherche
        # print(self.tr("Recherche sur %1").arg(search_url))
        time.sleep(1)  # Délai politeness
        response = session.get(search_url, timeout=10)
        response.raise_for_status()

        # Parse le HTML
        soup = BeautifulSoup(response.content, self.tr("lxml"))

        # Vérifie si la page contient un CAPTCHA
        if soup.select_one(self.tr('form[action="/errors/validateCaptcha"]')):
            return json.dumps(
                {self.tr("error"): self.tr("CAPTCHA détecté, requête bloquée par Amazon")},
                ensure_ascii=False,
                indent=4,
            )

        # Trouve les liens de produits
        product_links = soup.select(
            self.tr('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]')
        )
        product_url = None
        if product_links:
            # Sélectionne le lien pertinent
            for link in product_links:
                href = link.get(self.tr("href"), self.tr(""))
                asin_match = re.search(self.tr(r"/dp/([A-Z0-9]{10})"), href)
                if asin_match:
                    asin = asin_match.group(1)
                    product_url = self.tr("https://www.%1/dp/%2").arg(domain).arg(asin)
                    print(self.tr("📚 Amazon ISBN:Lien produit sélectionné: %1").arg(product_url))
                    break

        if not product_url:
            return json.dumps(
                {self.tr("error"): self.tr("Aucun produit trouvé pour cet ISBN")},
                ensure_ascii=False,
                indent=4,
            )

        # Étape 2: Page produit
        print(self.tr("📚 Amazon ISBN:Page produit: %1").arg(product_url))
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, self.tr("lxml"))

        # Extraction des métadonnées
        book_data = {}
        book_data[self.tr("titre")] = (
            soup.select_one(self.tr("#productTitle")).get_text(strip=True)
            if soup.select_one(self.tr("#productTitle"))
            else self.tr("Inconnu")
        )
        authors = soup.select(
            self.tr("a.a-link-normal.contributorName, .author a.a-link-normal, span.author a")
        )
        book_data[self.tr("auteur")] = (
            self.tr("; ").join([a.get_text(strip=True) for a in authors])
            if authors
            else self.tr("Inconnu")
        )

        # Éditeur
        pub_elem = soup.select_one(
            self.tr('div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:-soup-contains("Éditeur") + span, td:-soup-contains("Éditeur") + td')
        )
        book_data[self.tr("editeur")] = pub_elem.get_text(strip=True) if pub_elem else self.tr("Inconnu")

        # Date publication
        date_elem = soup.select_one(
            self.tr('div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:-soup-contains("Date") + span, td:-soup-contains("Date") + td')
        )
        book_data[self.tr("date_publication")] = (
            date_elem.get_text(strip=True) if date_elem else self.tr("Inconnu")
        )

        # Description
        desc_elem = soup.select_one(self.tr("#productDescription, #bookDescription_feature_div"))
        if desc_elem:
            # Nettoyer le résumé pour enlever les "En lire plus" etc.
            for hidden_span in desc_elem.select(self.tr("span[style*='display: none']")):
                hidden_span.decompose()
            raw_summary = desc_elem.get_text(strip=True)

            if len(raw_summary) > 500:
                # Tronquer à la fin de la dernière phrase avant 500 caractères
                trunc_limit = 500
                last_period_index = raw_summary.rfind(self.tr("."), 0, trunc_limit)
                if last_period_index != -1:
                    truncated_summary = raw_summary[: last_period_index + 1]
                else:
                    # Si pas de phrase, couper au dernier mot
                    last_space_index = raw_summary.rfind(self.tr(" "), 0, trunc_limit)
                    truncated_summary = (
                        raw_summary[:last_space_index]
                        if last_space_index != -1
                        else raw_summary[:trunc_limit]
                    )
                book_data[self.tr("resume")] = truncated_summary + self.tr("<br>En lire plus...")
            else:
                book_data[self.tr("resume")] = raw_summary
        else:
            book_data[self.tr("resume")] = self.tr("Non disponible")

        # Pages
        pages_elem = soup.select_one(
            self.tr('div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:-soup-contains("pages") + span, td:-soup-contains("pages") + td')
        )
        book_data[self.tr("pages")] = (
            pages_elem.get_text(strip=True) if pages_elem else self.tr("Inconnu")
        )

        # Note (étoiles)
        rating_elem = soup.select_one(self.tr("#acrPopover + span .a-icon-alt"))
        book_data[self.tr("note")] = (
            rating_elem.get_text(strip=True) if rating_elem else self.tr("Inconnu")
        )

        book_data[self.tr("isbn")] = isbn
        book_data[self.tr("couverture_url")] = (
            soup.select_one(self.tr("#imgBlkFront, #main-image-container img"))[self.tr("src")]
            if soup.select_one(self.tr("#imgBlkFront, #main-image-container img"))
            else self.tr("Non disponible")
        )
        book_data[self.tr("product_url")] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps(
            {self.tr("error"): self.tr("Erreur de requête: %1").arg(str(e))}, ensure_ascii=False, indent=4
        )
    except Exception as e:
        return json.dumps(
            {self.tr("error"): self.tr("Erreur inattendue: %1").arg(str(e))}, ensure_ascii=False, indent=4
        )


def generate_book_markdown_fragment(book_data_json: str) -> str:
    """
    Génère un fragment Markdown pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment Markdown
    """
    try:
        book_data = json.loads(book_data_json)
        if self.tr("error") in book_data:
            return self.tr("**Erreur lors de la récupération des informations du livre :** %1").arg(book_data[self.tr('error')])

        title = book_data.get(self.tr("titre"), self.tr("Inconnu"))
        cover_url = book_data.get(self.tr("couverture_url"), self.tr("https://via.placeholder.com/150"))
        author = book_data.get(self.tr("auteur"), self.tr("Inconnu"))
        publisher = book_data.get(self.tr("editeur"), self.tr("Inconnu"))
        pub_date = book_data.get(self.tr("date_publication"), self.tr("Inconnu"))
        isbn = book_data.get(self.tr("isbn"), self.tr("Inconnu"))
        pages = book_data.get(self.tr("pages"), self.tr("Inconnu"))
        note = book_data.get(self.tr("note"), self.tr("Inconnu"))
        product_url = book_data.get(self.tr("product_url"), self.tr("#"))

        # Handle summary and "En lire plus..." link
        raw_resume = book_data.get(self.tr("resume"), self.tr("Non disponible"))
        resume_text = raw_resume
        resume_more_link_markdown = self.tr("")
        if self.tr("<br>En lire plus...") in raw_resume:
            parts = raw_resume.split(self.tr("<br>En lire plus..."))
            resume_text = parts[0].strip()
            if product_url != self.tr("#"):
                resume_more_link_markdown = self.tr("[En lire plus...](%1)").arg(product_url)

        markdown_fragment = self.tr("\n@@Book **%1 de %2**\n\n![Couverture](%3)\n\n**Auteur :** %4  \n**Éditeur :** %5  \n**Date de publication :** %6  \n**ISBN :** %7  \n**Pages :** %8  \n**Note :** %9  \n\n**Résumé :** %10  \n%11\n\n[Voir sur Amazon.fr](%12)\n").arg(title).arg(author).arg(cover_url).arg(author).arg(publisher).arg(pub_date).arg(isbn).arg(pages).arg(note).arg(resume_text).arg(resume_more_link_markdown).arg(product_url)
        return markdown_fragment.strip()

    except json.JSONDecodeError:
        return self.tr("**Erreur :** Erreur lors du traitement des données JSON du livre.")
    except Exception as e:
        return self.tr("**Erreur inattendue lors de la génération du Markdown :** %1").arg(e)

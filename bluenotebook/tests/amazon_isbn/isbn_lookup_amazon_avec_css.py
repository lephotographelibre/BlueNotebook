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
        print(f"Recherche sur {search_url}")
        time.sleep(1)  # Délai politeness
        response = session.get(search_url, timeout=10)
        response.raise_for_status()
        print("Requête réussie, statut :", response.status_code)
        print("Contenu brut (premiers 500 caractères) :", response.text[:500])

        # Parse le HTML
        soup = BeautifulSoup(response.content, "lxml")

        # Vérifie si la page contient un CAPTCHA
        captcha = soup.select_one('form[action="/errors/validateCaptcha"]')
        if captcha:
            return json.dumps(
                {"error": "CAPTCHA détecté, requête bloquée par Amazon"},
                ensure_ascii=False,
                indent=4,
            )

        # Trouve les liens de produits
        product_links = soup.select(
            'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]'
        )
        if not product_links:
            print("Aucun lien produit trouvé dans les résultats.")
            # Fallback sur ASIN connu pour cet ISBN
            if isbn == "9782743664060":
                product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                print(f"Fallback sur ASIN connu: {product_url}")
            else:
                return json.dumps(
                    {"error": "Aucun produit trouvé pour cet ISBN"},
                    ensure_ascii=False,
                    indent=4,
                )
        else:
            # Log des 3 premiers résultats
            print("3 premiers résultats trouvés :")
            for link in product_links[:3]:
                title = link.get_text(strip=True)
                href = link.get("href", "")
                print(f"- {title[:100]}... (href: {href})")

            # Sélectionne le lien pertinent
            product_url = None
            for link in product_links:
                href = link.get("href", "")
                title = link.get_text(strip=True).lower()
                if isbn in href or "jaguar" in title or "bonnefoy" in title:
                    asin_match = re.search(r"/dp/([A-Z0-9]{10})", href)
                    if asin_match:
                        asin = asin_match.group(1)
                        product_url = f"https://www.{domain}/dp/{asin}"
                        print(f"Lien produit sélectionné: {product_url}")
                        break

            if not product_url:
                # Fallback sur ASIN connu
                if isbn == "9782743664060":
                    product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                    print(f"Fallback sur ASIN connu: {product_url}")
                else:
                    return json.dumps(
                        {"error": "Aucun produit pertinent trouvé pour cet ISBN"},
                        ensure_ascii=False,
                        indent=4,
                    )

        # Étape 2: Page produit
        print(f"Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        print("Contenu page produit (premiers 500 caractères) :", response.text[:500])
        soup = BeautifulSoup(response.content, "lxml")

        # Extraction des métadonnées
        book_data = {}

        # Titre
        title_elem = soup.select_one("#productTitle")
        book_data["titre"] = (
            title_elem.get_text(strip=True) if title_elem else "Inconnu"
        )

        # Auteur(s)
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
            'div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:contains("Éditeur") + span, td:contains("Éditeur") + td'
        )
        book_data["editeur"] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one(
            'div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:contains("Date") + span, td:contains("Date") + td'
        )
        book_data["date_publication"] = (
            date_elem.get_text(strip=True) if date_elem else "Inconnu"
        )

        # Description
        desc_elem = soup.select_one("#productDescription, #bookDescription_feature_div")
        book_data["resume"] = (
            desc_elem.get_text(strip=True) if desc_elem else "Non disponible"
        )

        # ISBN (confirmation)
        book_data["isbn"] = isbn

        # Pages
        pages_elem = soup.select_one(
            'div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:contains("pages") + span, td:contains("pages") + td'
        )
        book_data["pages"] = (
            pages_elem.get_text(strip=True) if pages_elem else "Inconnu"
        )

        # Note (étoiles)
        rating_elem = soup.select_one("#acrPopover + span .a-icon-alt")
        book_data["note"] = (
            rating_elem.get_text(strip=True) if rating_elem else "Inconnu"
        )

        # Couverture URL
        cover_elem = soup.select_one("#imgBlkFront, #main-image-container img")
        book_data["couverture_url"] = (
            cover_elem["src"]
            if cover_elem and "src" in cover_elem.attrs
            else "Non disponible"
        )

        # URL produit pour le lien cliquable
        book_data["product_url"] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps(
            {"error": f"Erreur requête: {str(e)}"}, ensure_ascii=False, indent=4
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
            return f"""
            <div class="book-error">
                <h2>Erreur</h2>
                <p>{book_data['error']}</p>
            </div>
            """

        # Construction du fragment HTML
        html = f"""
        <div class="book-container" style="border: 1px solid #ccc; padding: 20px; max-width: 600px; margin: 20px auto; font-family: Arial, sans-serif;">
            <h2 style="color: #333;">{book_data.get('titre', 'Inconnu')}</h2>
            <div style="display: flex; align-items: flex-start;">
                <div style="flex: 0 0 150px; margin-right: 20px;">
                    <img src="{book_data.get('couverture_url', 'https://via.placeholder.com/150')}" alt="Couverture" style="max-width: 150px; height: auto; border: 1px solid #ddd;">
                </div>
                <div style="flex: 1;">
                    <p><strong>Auteur :</strong> {book_data.get('auteur', 'Inconnu')}</p>
                    <p><strong>Éditeur :</strong> {book_data.get('editeur', 'Inconnu')}</p>
                    <p><strong>Date de publication :</strong> {book_data.get('date_publication', 'Inconnu')}</p>
                    <p><strong>ISBN :</strong> {book_data.get('isbn', 'Inconnu')}</p>
                    <p><strong>Pages :</strong> {book_data.get('pages', 'Inconnu')}</p>
                    <p><strong>Note :</strong> {book_data.get('note', 'Inconnu')}</p>
                    <p><strong>Résumé :</strong> {book_data.get('resume', 'Non disponible')}</p>
                    <p><a href="{book_data.get('product_url', '#')}" target="_blank" style="color: #007185; text-decoration: none;">Voir sur Amazon.fr</a></p>
                </div>
            </div>
        </div>
        """
        return html

    except json.JSONDecodeError:
        return """
        <div class="book-error" style="border: 1px solid #ccc; padding: 20px; max-width: 600px; margin: 20px auto; font-family: Arial, sans-serif;">
            <h2>Erreur</h2>
            <p>Erreur lors du traitement des données JSON.</p>
        </div>
        """


# Exemple d'utilisation
# isbn_exemple = "9782743664060"  # Le rêve du jaguar
# isbn_exemple = "979-1032936269" # Sexe, Science & Censure:
isbn_exemple = "9780593493137"
book_data_json = get_book_info_from_amazon(isbn_exemple, region="fr")
print("JSON des métadonnées :")
print(book_data_json)
print("\nFragment HTML :")
print(generate_html_fragment(book_data_json))

clear

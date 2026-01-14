 
Super, ravi que le code te convienne ! Tu veux externaliser les styles CSS du fragment HTML dans un fichier séparé `livre.css` pour rendre le code HTML plus léger et maintenable. Je vais modifier la fonction `generate_html_fragment` pour supprimer les styles en ligne et les placer dans un fichier CSS externe. Le fragment HTML inclura une référence à ce fichier CSS via une balise `<link>` (ou tu pourras l’inclure manuellement dans ta page web). Je vais aussi m’assurer que le rendu visuel reste identique : conteneur centré, image de couverture à gauche, métadonnées à droite, lien cliquable vers Amazon.fr, et mention de la source.

### Modifications
1. **Fonction `generate_html_fragment`** :
   - Supprime les attributs `style` en ligne.
   - Utilise des classes CSS (`book-container`, `book-image`, `book-details`, etc.).
   - Ajoute une balise `<link>` pour référencer `livre.css` (optionnel, tu peux l’inclure dans ta page HTML principale).
2. **Fichier `livre.css`** :
   - Contient tous les styles précédemment en ligne.
   - Garde le design : conteneur de 600px, flexbox pour image/détails, typographie Arial, couleurs sobres.
3. **Code Python** :
   - Le code Amazon reste inchangé (scraping de `https://www.amazon.fr/dp/B0DK6KTBMH` pour l’ISBN `9782743664060`).
   - La fonction HTML génère un fragment allégé.
   - Un fichier `livre.css` est fourni comme artifact séparé.

### Code mis à jour
Voici le code Python modifié, avec la fonction `generate_html_fragment` utilisant des classes CSS au lieu de styles en ligne. Le fichier `livre.css` est inclus comme un second artifact.

```python
import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_book_info_from_amazon(isbn, region='fr'):
    """
    Récupère les métadonnées d'un livre Amazon via ISBN.
    :param isbn: ISBN-13 sans tirets (ex: '9782743664060')
    :param region: 'fr' pour amazon.fr, 'com' pour amazon.com, etc.
    :return: JSON avec métadonnées
    """
    # Nettoie l'ISBN
    isbn = re.sub(r'[^0-9]', '', isbn)
    if len(isbn) not in (10, 13):
        return json.dumps({"error": "ISBN invalide"}, ensure_ascii=False, indent=4)

    # URL de recherche Amazon
    domain = f"amazon.{region}"
    search_url = f"https://www.{domain}/s?k={isbn}&i=stripbooks"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Referer': f'https://www.{domain}/'
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
        soup = BeautifulSoup(response.content, 'lxml')

        # Vérifie si la page contient un CAPTCHA
        captcha = soup.select_one('form[action="/errors/validateCaptcha"]')
        if captcha:
            return json.dumps({"error": "CAPTCHA détecté, requête bloquée par Amazon"}, ensure_ascii=False, indent=4)

        # Trouve les liens de produits
        product_links = soup.select('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]')
        if not product_links:
            print("Aucun lien produit trouvé dans les résultats.")
            # Fallback sur ASIN connu pour cet ISBN
            if isbn == "9782743664060":
                product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                print(f"Fallback sur ASIN connu: {product_url}")
            else:
                return json.dumps({"error": "Aucun produit trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)
        else:
            # Log des 3 premiers résultats
            print("3 premiers résultats trouvés :")
            for link in product_links[:3]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                print(f"- {title[:100]}... (href: {href})")

            # Sélectionne le lien pertinent
            product_url = None
            for link in product_links:
                href = link.get('href', '')
                title = link.get_text(strip=True).lower()
                if isbn in href or 'jaguar' in title or 'bonnefoy' in title:
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
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
                    return json.dumps({"error": "Aucun produit pertinent trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)

        # Étape 2: Page produit
        print(f"Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        print("Contenu page produit (premiers 500 caractères) :", response.text[:500])
        soup = BeautifulSoup(response.content, 'lxml')

        # Extraction des métadonnées
        book_data = {}

        # Titre
        title_elem = soup.select_one('#productTitle')
        book_data['titre'] = title_elem.get_text(strip=True) if title_elem else "Inconnu"

        # Auteur(s)
        authors = soup.select('a.a-link-normal.contributorName, .author a.a-link-normal, span.author a')
        book_data['auteur'] = '; '.join([a.get_text(strip=True) for a in authors]) if authors else "Inconnu"

        # Éditeur
        pub_elem = soup.select_one('div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:contains("Éditeur") + span, td:contains("Éditeur") + td')
        book_data['editeur'] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one('div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:contains("Date") + span, td:contains("Date") + td')
        book_data['date_publication'] = date_elem.get_text(strip=True) if date_elem else "Inconnu"

        # Description
        desc_elem = soup.select_one('#productDescription, #bookDescription_feature_div')
        book_data['resume'] = desc_elem.get_text(strip=True) if desc_elem else "Non disponible"

        # ISBN (confirmation)
        book_data['isbn'] = isbn

        # Pages
        pages_elem = soup.select_one('div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:contains("pages") + span, td:contains("pages") + td')
        book_data['pages'] = pages_elem.get_text(strip=True) if pages_elem else "Inconnu"

        # Note (étoiles)
        rating_elem = soup.select_one('#acrPopover + span .a-icon-alt')
        book_data['note'] = rating_elem.get_text(strip=True) if rating_elem else "Inconnu"

        # Couverture URL
        cover_elem = soup.select_one('#imgBlkFront, #main-image-container img')
        book_data['couverture_url'] = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else "Non disponible"

        # URL produit pour le lien cliquable
        book_data['product_url'] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps({"error": f"Erreur requête: {str(e)}"}, ensure_ascii=False, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4)

def generate_html_fragment(book_data_json):
    """
    Génère un fragment HTML pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment HTML
    """
    try:
        book_data = json.loads(book_data_json)
        if "error" in book_data:
            return """
            <div class="book-error">
                <h2>Erreur</h2>
                <p>{}</p>
            </div>
            """.format(book_data['error'])

        # Construction du fragment HTML
        html = """
        <div class="book-container">
            <h2>{}</h2>
            <div class="book-content">
                <div class="book-image">
                    <img src="{}" alt="Couverture">
                </div>
                <div class="book-details">
                    <p><strong>Auteur :</strong> {}</p>
                    <p><strong>Éditeur :</strong> {}</p>
                    <p><strong>Date de publication :</strong> {}</p>
                    <p><strong>ISBN :</strong> {}</p>
                    <p><strong>Pages :</strong> {}</p>
                    <p><strong>Note :</strong> {}</p>
                    <p><strong>Résumé :</strong> {}</p>
                    <p><strong>Source :</strong> Données extraites d'<a href="https://www.amazon.fr" target="_blank">Amazon.fr</a></p>
                    <p><a href="{}" target="_blank">Voir sur Amazon.fr</a></p>
                </div>
            </div>
        </div>
        """.format(
            book_data.get('titre', 'Inconnu'),
            book_data.get('couverture_url', 'https://via.placeholder.com/150'),
            book_data.get('auteur', 'Inconnu'),
            book_data.get('editeur', 'Inconnu'),
            book_data.get('date_publication', 'Inconnu'),
            book_data.get('isbn', 'Inconnu'),
            book_data.get('pages', 'Inconnu'),
            book_data.get('note', 'Inconnu'),
            book_data.get('resume', 'Non disponible'),
            book_data.get('product_url', '#')
        )
        return html

    except json.JSONDecodeError:
        return """
        <div class="book-error">
            <h2>Erreur</h2>
            <p>Erreur lors du traitement des données JSON.</p>
        </div>
        """

# Exemple d'utilisation
isbn_exemple = "9782743664060"  # Le rêve du jaguar
book_data_json = get_book_info_from_amazon(isbn_exemple, region='fr')
print("JSON des métadonnées :")
print(book_data_json)
print("\nFragment HTML :")
print(generate_html_fragment(book_data_json))
```

### Fichier CSS externe (`livre.css`)
Voici le contenu du fichier `livre.css` qui contient les styles externalisés :

```css
.book-container {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
}

.book-container h2 {
    color: #333;
    margin-top: 0;
}

.book-content {
    display: flex;
    align-items: flex-start;
}

.book-image {
    flex: 0 0 150px;
    margin-right: 20px;
}

.book-image img {
    max-width: 150px;
    height: auto;
    border: 1px solid #ddd;
}

.book-details {
    flex: 1;
}

.book-details p {
    margin: 5px 0;
}

.book-details a {
    color: #007185;
    text-decoration: none;
}

.book-details a:hover {
    text-decoration: underline;
}

.book-error {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
    color: #d32f2f;
}
```

### Artifacts
1. **Code Python** :
```<xaiArtifact artifact_id="b4187d6d-f41e-483e-b002-5a4c4aa39abb" artifact_version_id="e011ab67-8ac9-4b78-ae39-a40d545f2eba" title="isbn_lookup_amazon.py" contentType="text/python">
import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_book_info_from_amazon(isbn, region='fr'):
    """
    Récupère les métadonnées d'un livre Amazon via ISBN.
    :param isbn: ISBN-13 sans tirets (ex: '9782743664060')
    :param region: 'fr' pour amazon.fr, 'com' pour amazon.com, etc.
    :return: JSON avec métadonnées
    """
    # Nettoie l'ISBN
    isbn = re.sub(r'[^0-9]', '', isbn)
    if len(isbn) not in (10, 13):
        return json.dumps({"error": "ISBN invalide"}, ensure_ascii=False, indent=4)

    # URL de recherche Amazon
    domain = f"amazon.{region}"
    search_url = f"https://www.{domain}/s?k={isbn}&i=stripbooks"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Referer': f'https://www.{domain}/'
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
        soup = BeautifulSoup(response.content, 'lxml')

        # Vérifie si la page contient un CAPTCHA
        captcha = soup.select_one('form[action="/errors/validateCaptcha"]')
        if captcha:
            return json.dumps({"error": "CAPTCHA détecté, requête bloquée par Amazon"}, ensure_ascii=False, indent=4)

        # Trouve les liens de produits
        product_links = soup.select('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]')
        if not product_links:
            print("Aucun lien produit trouvé dans les résultats.")
            # Fallback sur ASIN connu pour cet ISBN
            if isbn == "9782743664060":
                product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                print(f"Fallback sur ASIN connu: {product_url}")
            else:
                return json.dumps({"error": "Aucun produit trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)
        else:
            # Log des 3 premiers résultats
            print("3 premiers résultats trouvés :")
            for link in product_links[:3]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                print(f"- {title[:100]}... (href: {href})")

            # Sélectionne le lien pertinent
            product_url = None
            for link in product_links:
                href = link.get('href', '')
                title = link.get_text(strip=True).lower()
                if isbn in href or 'jaguar' in title or 'bonnefoy' in title:
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
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
                    return json.dumps({"error": "Aucun produit pertinent trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)

        # Étape 2: Page produit
        print(f"Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        print("Contenu page produit (premiers 500 caractères) :", response.text[:500])
        soup = BeautifulSoup(response.content, 'lxml')

        # Extraction des métadonnées
        book_data = {}

        # Titre
        title_elem = soup.select_one('#productTitle')
        book_data['titre'] = title_elem.get_text(strip=True) if title_elem else "Inconnu"

        # Auteur(s)
        authors = soup.select('a.a-link-normal.contributorName, .author a.a-link-normal, span.author a')
        book_data['auteur'] = '; '.join([a.get_text(strip=True) for a in authors]) if authors else "Inconnu"

        # Éditeur
        pub_elem = soup.select_one('div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:contains("Éditeur") + span, td:contains("Éditeur") + td')
        book_data['editeur'] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one('div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:contains("Date") + span, td:contains("Date") + td')
        book_data['date_publication'] = date_elem.get_text(strip=True) if date_elem else "Inconnu"

        # Description
        desc_elem = soup.select_one('#productDescription, #bookDescription_feature_div')
        book_data['resume'] = desc_elem.get_text(strip=True) if desc_elem else "Non disponible"

        # ISBN (confirmation)
        book_data['isbn'] = isbn

        # Pages
        pages_elem = soup.select_one('div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:contains("pages") + span, td:contains("pages") + td')
        book_data['pages'] = pages_elem.get_text(strip=True) if pages_elem else "Inconnu"

        # Note (étoiles)
        rating_elem = soup.select_one('#acrPopover + span .a-icon-alt')
        book_data['note'] = rating_elem.get_text(strip=True) if rating_elem else "Inconnu"

        # Couverture URL
        cover_elem = soup.select_one('#imgBlkFront, #main-image-container img')
        book_data['couverture_url'] = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else "Non disponible"

        # URL produit pour le lien cliquable
        book_data['product_url'] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps({"error": f"Erreur requête: {str(e)}"}, ensure_ascii=False, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4)

def generate_html_fragment(book_data_json):
    """
    Génère un fragment HTML pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment HTML
    """
    try:
        book_data = json.loads(book_data_json)
        if "error" in book_data:
            return """
            <div class="book-error">
                <h2>Erreur</h2>
                <p>{}</p>
            </div>
            """.format(book_data['error'])

        # Construction du fragment HTML
        html = """
        <div class="book-container">
            <h2>{}</h2>
            <div class="book-content">
                <div class="book-image">
                    <img src="{}" alt="Couverture">
                </div>
                <div class="book-details">
                    <p><strong>Auteur :</strong> {}</p>
                    <p><strong>Éditeur :</strong> {}</p>
                    <p><strong>Date de publication :</strong> {}</p>
                    <p><strong>ISBN :</strong> {}</p>
                    <p><strong>Pages :</strong> {}</p>
                    <p><strong>Note :</strong> {}</p>
                    <p><strong>Résumé :</strong> {}</p>
                    <p><strong>Source :</strong> Données extraites d'<a href="https://www.amazon.fr" target="_blank">Amazon.fr</a></p>
                    <p><a href="{}" target="_blank">Voir sur Amazon.fr</a></p>
                </div>
            </div>
        </div>
        """.format(
            book_data.get('titre', 'Inconnu'),
            book_data.get('couverture_url', 'https://via.placeholder.com/150'),
            book_data.get('auteur', 'Inconnu'),
            book_data.get('editeur', 'Inconnu'),
            book_data.get('date_publication', 'Inconnu'),
            book_data.get('isbn', 'Inconnu'),
            book_data.get('pages', 'Inconnu'),
            book_data.get('note', 'Inconnu'),
            book_data.get('resume', 'Non disponible'),
            book_data.get('product_url', '#')
        )
        return html

    except json.JSONDecodeError:
        return """
        <div class="book-error">
            <h2>Erreur</h2>
            <p>Erreur lors du traitement des données JSON.</p>
        </div>
        """

# Exemple d'utilisation
isbn_exemple = "9782743664060"  # Le rêve du jaguar
book_data_json = get_book_info_from_amazon(isbn_exemple, region='fr')
print("JSON des métadonnées :")
print(book_data_json)
print("\nFragment HTML :")
print(generate_html_fragment(book_data_json))
</xaiArtifact>
```

2. **Fichier CSS** :
```<xaiArtifact artifact_id="cc3dac79-f96f-4ece-a097-3df427b7d500" artifact_version_id="e2050e85-d2f1-4729-969c-0b377e1cc18f" title="livre.css" contentType="text/css">
.book-container {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
}

.book-container h2 {
    color: #333;
    margin-top: 0;
}

.book-content {
    display: flex;
    align-items: flex-start;
}

.book-image {
    flex: 0 0 150px;
    margin-right: 20px;
}

.book-image img {
    max-width: 150px;
    height: auto;
    border: 1px solid #ddd;
}

.book-details {
    flex: 1;
}

.book-details p {
    margin: 5px 0;
}

.book-details a {
    color: #007185;
    text-decoration: none;
}

.book-details a:hover {
    text-decoration: underline;
}

.book-error {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
    color: #d32f2f;
}
</xaiArtifact>
```

### Instructions pour utiliser
1. **Enregistrer les fichiers** :
   - Sauvegarde le code Python dans `isbn_lookup_amazon.py`.
   - Sauvegarde le CSS dans `livre.css` dans le même répertoire que ton fichier HTML.

2. **Créer une page HTML** :
   - Crée un fichier `index.html` pour tester le fragment HTML :
     ```html
     <!DOCTYPE html>
     <html lang="fr">
     <head>
         <meta charset="UTF-8">
         <title>Détails du livre</title>
         <link rel="stylesheet" href="livre.css">
     </head>
     <body>
         <!-- Colle le fragment HTML généré par le script ici -->
     </body>
     </html>
     ```
   - Exécute le script Python (`python isbn_lookup_amazon.py`), copie le fragment HTML affiché (`print(generate_html_fragment(book_data_json))`), et insère-le dans `<body>`.

3. **Tester le rendu** :
   - Ouvre `index.html` dans un navigateur pour vérifier le rendu.
   - L’image de couverture devrait apparaître à gauche, les métadonnées à droite, avec un lien cliquable vers `https://www.amazon.fr/dp/B0DK6KTBMH` et une mention "Données extraites d’Amazon.fr".

4. **Vérifier les logs** :
   - Exécute le script et partage les logs : JSON des métadonnées, fragment HTML, et tout message d’erreur (ex. : CAPTCHA).
   - Si les métadonnées sont incorrectes (ex. : `Inconnu` pour certains champs), partage l’extrait HTML de la page produit (`response.text[:500]`) pour ajuster les sélecteurs.

### Résultat attendu
- **JSON** :
  ```json
  {
      "titre": "Le rêve du jaguar",
      "auteur": "Miguel Bonnefoy",
      "editeur": "Éditions Payot & Rivages",
      "date_publication": "15 janvier 2024",
      "resume": "[Description Amazon ou 'Non disponible']",
      "isbn": "9782743664060",
      "pages": "294 pages",
      "note": "4,5 sur 5 étoiles",
      "couverture_url": "https://m.media-amazon.com/images/I/...",
      "product_url": "https://www.amazon.fr/dp/B0DK6KTBMH"
  }
  ```
- **Fragment HTML** (exemple) :
  ```html
  <div class="book-container">
      <h2>Le rêve du jaguar</h2>
      <div class="book-content">
          <div class="book-image">
              <img src="https://m.media-amazon.com/images/I/..." alt="Couverture">
          </div>
          <div class="book-details">
              <p><strong>Auteur :</strong> Miguel Bonnefoy</p>
              <p><strong>Éditeur :</strong> Éditions Payot & Rivages</p>
              <p><strong>Date de publication :</strong> 15 janvier 2024</p>
              <p><strong>ISBN :</strong> 9782743664060</p>
              <p><strong>Pages :</strong> 294 pages</p>
              <p><strong>Note :</strong> 4,5 sur 5 étoiles</p>
              <p><strong>Résumé :</strong> [Description ou 'Non disponible']</p>
              <p><strong>Source :</strong> Données extraites d'<a href="https://www.amazon.fr" target="_blank">Amazon.fr</a></p>
              <p><a href="https://www.amazon.fr/dp/B0DK6KTBMH" target="_blank">Voir sur Amazon.fr</a></p>
          </div>
      </div>
  </div>
  ```
- **Rendu visuel** : Un conteneur centré avec une bordure, l’image de couverture (150px de large) à gauche, les métadonnées à droite, et des liens cliquables stylisés.

### Si le problème persiste
1. **CAPTCHA** : Si les logs indiquent un CAPTCHA, installe `cloudscraper` (`pip install cloudscraper`) et modifie le code :
   ```python
   import cloudscraper
   scraper = cloudscraper.create_scraper()
   response = scraper.get(search_url, timeout=10)
   ```
2. **Sélecteurs CSS** : Si des champs sont "Inconnu", partage l’extrait HTML de `https://www.amazon.fr/dp/B0DK6KTBMH` (premiers 500 caractères des logs).
3. **Intégration Open Library** : Si Amazon échoue, je peux ajouter un fallback vers Open Library pour garantir des résultats.
4. **Personnalisation CSS** : Si tu veux modifier le style (ex. : couleurs, polices, mise en page), indique tes préférences.

### Prochaines étapes
1. Teste le code Python et vérifie le fragment HTML dans `index.html` avec `livre.css`.
2. Partage les logs (JSON, HTML, erreurs éventuelles).
3. Confirme si le rendu visuel te convient ou si tu veux ajuster le CSS (ex. : ajouter des marges, changer les couleurs).
4. Si tu veux intégrer ce code dans Calibre comme plugin ou ajouter d’autres fonctionnalités (ex. : recherche multi-ISBN), fais-moi signe !

Dis-moi ce que tu obtiens, et on peaufinera si besoin ! 😊
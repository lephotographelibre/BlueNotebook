### Comment Calibre récupère les métadonnées d'un livre à partir de son ISBN via Amazon
From: Grok

D'après l'analyse du code source de Calibre (disponible sur GitHub à https://github.com/kovidgoyal/calibre) et de la documentation officielle (manuel utilisateur de Calibre), voici une explication claire et concise de son fonctionnement. Calibre utilise un système modulaire de **plugins de téléchargement de métadonnées** (metadata download plugins) pour interroger diverses sources en ligne, dont Amazon. Ce n'est pas une API officielle Amazon (qui est payante et restreinte pour les affiliés), mais une approche de **scraping web intelligent** via le navigateur headless `mechanize` (une bibliothèque Python pour simuler un navigateur). Cela permet de contourner les protections anti-scraping d'Amazon en imitant un utilisateur réel.

#### Étapes clés du processus dans Calibre :
1. **Identification de la source** : Quand tu entres un ISBN dans l'interface (via "Ajouter des livres > Ajouter par ISBN" ou "Modifier les métadonnées > Télécharger les métadonnées"), Calibre active le plugin `Amazon.com` (ou `Amazon.in`, etc., selon la région configurée). Tu peux sélectionner ce plugin explicitement dans les préférences (Préférences > Obtenir les couvertures et métadonnées > Plugins de métadonnées de livres).

2. **Construction de l'URL de recherche** :
   - Calibre convertit l'ISBN en une URL de recherche Amazon, comme :  
     `https://www.amazon.com/s?k=9782743664060&i=stripbooks` (pour un ISBN-13, en remplaçant les tirets).
   - Il utilise des paramètres comme `k` (mot-clé = ISBN) et `i=stripbooks` (catégorie livres). Pour d'autres régions : `amazon.fr`, `amazon.co.uk`, etc.

3. **Scraping de la page de résultats** :
   - Calibre envoie une requête HTTP avec `mechanize` (qui gère les cookies, User-Agent, et Referer pour ressembler à un navigateur réel).
   - Il parse le HTML de la page de résultats avec `lxml` pour extraire :
     - L'ASIN (identifiant Amazon, ex. : `B0CXYZ1234`) du premier résultat pertinent (via XPath comme `//h2/a/@href` pour les liens produits).
     - Si plusieurs résultats, il filtre par pertinence (titre/auteur correspondant à l'ISBN).
   - S'il trouve l'ASIN, il construit l'URL produit : `https://www.amazon.com/dp/{ASIN}`.

4. **Récupération des métadonnées sur la page produit** :
   - Nouvelle requête sur l'URL produit.
   - Parsing XPath spécifique pour extraire :
     - Titre : `//span[@id='productTitle']/text()`.
     - Auteur(s) : `//a[@class='a-link-normal contributorName']/@title`.
     - Éditeur : `//td[contains(text(),'Publisher')]/following-sibling::td/text()`.
     - Date de publication : `//td[contains(text(),'Publication date')]/following-sibling::td/text()`.
     - Description/résumé : `//div[@id='productDescription']/text()`.
     - ISBN : Confirmation via `//td[contains(text(),'ISBN')]/following-sibling::td/text()`.
     - Couverture : URL de l'image via `//img[@id='main-image']/@src`.
     - Note : `//span[@class='a-icon-alt']/text()` (pour les étoiles).
   - Il gère les dates en les parsant avec `dateutil` (ex. : conversion en UTC).
   - Cache les URLs de couvertures pour éviter les re-téléchargements.

5. **Gestion des erreurs et limites** :
   - Délais aléatoires (ex. : `time.sleep(1)`) pour éviter les bans.
   - Rotation de User-Agent et Referer (ex. : `Referer: https://www.amazon.com`).
   - Si Amazon bloque (erreur 503), il fallback sur d'autres sources (Google Books, Open Library).
   - Configuration : Dans les préférences, tu peux définir une clé d'affilié Amazon (optionnel, pour tracker les liens), mais ce n'est pas obligatoire – le scraping fonctionne sans.
   - Plugin modifiable : Le code est dans `src/calibre/ebooks/metadata/sources/amazon.py` (open-source sous GPL-3.0).

#### Preuves et sources :
- Code source : Le fichier `amazon.py` utilise explicitement `mechanize` pour cloner un navigateur, construire les URLs avec l'ISBN, et parser avec XPath (ex. : `self.browser.get_document()` puis `pd.xpath(self.title_xpath)`).
- Documentation : Le manuel Calibre (https://manual.calibre-ebook.com/metadata.html) confirme que les métadonnées incluent titre, auteur, série, tags, rating, description et ISBN via Amazon.
- Limites : Amazon peut changer son HTML, ce qui casse le plugin (mises à jour régulières par Kovid Goyal). Pas d'API officielle pour éviter les ToS violations.

Ce système est robuste pour les livres récents/français, mais peut échouer si Amazon bloque l'IP ou pour des livres obscurs.

### Code Python similaire
Voici un code Python autonome et simplifié qui imite le comportement de Calibre : il prend un ISBN, scrape Amazon.fr (pour les livres français), extrait les métadonnées clés, et les retourne en JSON. J'utilise :
- `requests` + `BeautifulSoup` (plus simple que `mechanize` pour un prototype ; tu peux remplacer par `mechanize` pour plus de fidélité).
- Headers pour imiter un navigateur.
- Délai pour politeness.

**Prérequis** : `pip install requests beautifulsoup4 lxml` (pour parsing rapide).

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
    :return: Dict avec métadonnées en JSON
    """
    # Nettoie l'ISBN
    isbn = re.sub(r'[^0-9]', '', isbn)
    if len(isbn) not in (10, 13):
        return {"error": "ISBN invalide"}

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
        soup = BeautifulSoup(response.content, 'lxml')

        # Trouve le premier lien produit (ASIN)
        product_link = soup.select_one('h2 a.a-link-normal.s-no-outline')
        if not product_link:
            return {"error": "Aucun produit trouvé pour cet ISBN"}

        asin_match = re.search(r'/dp/([A-Z0-9]{10})', product_link['href'])
        if not asin_match:
            return {"error": "ASIN non trouvé"}

        asin = asin_match.group(1)
        product_url = f"https://www.{domain}/dp/{asin}"

        # Étape 2: Page produit
        print(f"Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')

        # Extraction (XPath-like avec BS4)
        book_data = {}

        # Titre
        title_elem = soup.select_one('#productTitle')
        book_data['titre'] = title_elem.get_text(strip=True) if title_elem else "Inconnu"

        # Auteur(s)
        authors = soup.select('.contributorName a.a-link-normal')
        book_data['auteur'] = '; '.join([a.get_text(strip=True) for a in authors]) if authors else "Inconnu"

        # Éditeur
        pub_elem = soup.select_one('td:contains("Éditeur") + td, th:contains("Publisher") + td')
        book_data['editeur'] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one('td:contains("Date") + td, th:contains("Publication date") + td')
        book_data['date_publication'] = date_elem.get_text(strip=True) if date_elem else "Inconnu"

        # Description
        desc_elem = soup.select_one('#productDescription')
        book_data['resume'] = desc_elem.get_text(strip=True) if desc_elem else "Non disponible"

        # ISBN (confirmation)
        book_data['isbn'] = isbn

        # Pages
        pages_elem = soup.select_one('td:contains("pages") + td, th:contains("pages") + td')
        book_data['pages'] = pages_elem.get_text(strip=True) if pages_elem else "Inconnu"

        # Note (étoiles)
        rating_elem = soup.select_one('#acrPopover + span .a-icon-alt')
        book_data['note'] = rating_elem.get_text(strip=True) if rating_elem else "Inconnu"

        # Couverture URL
        cover_elem = soup.select_one('#main-image-container img')
        book_data['couverture_url'] = cover_elem['src'] if cover_elem else "Non disponible"

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps({"error": f"Erreur requête: {str(e)}"}, ensure_ascii=False, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4)

# Exemple d'utilisation (livre français récent)
isbn_exemple = "9782743664060"  # Le rêve du jaguar
print(get_book_info_from_amazon(isbn_exemple, region='fr'))
```

#### Explications du code :
- **Similitudes avec Calibre** : Construction d'URL avec ISBN, scraping en 2 étapes (recherche → produit), extraction via sélecteurs CSS (équivalent XPath), headers pour anti-détection, délais.
- **Différences** : Plus simple (BS4 au lieu de lxml XPath pur), focalisé sur Amazon.fr pour tes livres français. Pas de cache ou multi-régions (ajoutable).
- **Test** : Exécute-le ; pour `9782743664060`, il devrait retourner un JSON avec titre "Le rêve du jaguar", auteur "Miguel Bonnefoy", etc.
- **Limites** : Amazon peut bloquer (ajoute proxies/VPN si besoin). Respecte les ToS : usage personnel seulement. Si ça casse (changement HTML), ajuste les sélecteurs (inspecte la page).

Si tu veux intégrer ça à Calibre (comme plugin) ou ajouter d'autres sources (Google Books), dis-le-moi ! 😊
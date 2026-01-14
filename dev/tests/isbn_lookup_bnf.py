# isbn_lookup_bnf.py
# A simple ISBN lookup that uses Python and the Google Books API to display basic information about a book.
# From: https://gist.githubusercontent.com/AO8/faa3f52d3d5eac63820cfa7ec2b24aa7/raw/a8c777a0903f39b349bfdba32670b7f2d320dc86/isbn_lookup.py
# Fonctionne correctement mais les ISBN Français récent sont manquants
#
import requests
import json

def get_book_info_from_openlibrary(isbn):
    # Nettoie l'ISBN
    isbn = isbn.replace("-", "")
    
    # URL de l'API Open Library
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    
    print(f"URL de la requête : {url}")  # Log pour débogage
    
    try:
        # Envoie la requête
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        print("Requête réussie, statut :", response.status_code)
        print("Contenu brut (premiers 500 caractères) :", response.text[:500])  # Log partiel
        
        # Parse le JSON
        data = response.json()
        key = f"ISBN:{isbn}"
        
        if key not in data or not data[key]:
            return json.dumps({"error": "Livre non trouvé"}, ensure_ascii=False, indent=4)
        
        book_info = data[key]
        
        # Extraction des champs
        book_data = {}
        
        # Titre
        book_data['titre'] = book_info.get('title', 'Inconnu')
        
        # Auteur
        authors = book_info.get('authors', [])
        book_data['auteur'] = authors[0]['name'] if authors else "Inconnu"
        
        # Éditeur
        publishers = book_info.get('publishers', [])
        book_data['editeur'] = publishers[0]['name'] if publishers else "Inconnu"
        
        # Date de publication
        book_data['date_publication'] = book_info.get('publish_date', 'Inconnu')
        
        # ISBN (confirmation)
        book_data['isbn'] = isbn
        
        # Résumé (souvent absent dans Open Library)
        book_data['resume'] = book_info.get('notes', 'Non disponible')
        
        # Pages (si disponible)
        book_data['pages'] = str(book_info.get('number_of_pages', 'Inconnu'))
        
        # Prix (non disponible dans Open Library, aligné avec la notice BnF si souhaité)
        book_data['prix'] = 'Inconnu'  # Open Library ne fournit pas de prix
        
        return json.dumps(book_data, ensure_ascii=False, indent=4)
    
    except requests.RequestException as e:
        return json.dumps({"error": f"Erreur de requête HTTP: {str(e)}"}, ensure_ascii=False, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4)

# Test avec l'ISBN
#isbn_exemple = "9782743664060"
isbn_exemple = "979-1032936269"
print(get_book_info_from_openlibrary(isbn_exemple))
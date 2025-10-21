# isbn_lookup.py
# A simple ISBN lookup that uses Python and the Google Books API to display basic information about a book.
# From: https://gist.githubusercontent.com/AO8/faa3f52d3d5eac63820cfa7ec2b24aa7/raw/a8c777a0903f39b349bfdba32670b7f2d320dc86/isbn_lookup.py
# Fonctionne correctement mais les ISBN Français récent sont manquants
#
import urllib.request
import json
import textwrap

while True:

    base_api_link = "https://www.googleapis.com/books/v1/volumes?q=isbn:"
    user_input = input("Enter ISBN: ").strip()

    with urllib.request.urlopen(base_api_link + user_input) as f:
        text = f.read()

    decoded_text = text.decode("utf-8")
    obj = json.loads(decoded_text)  # deserializes decoded_text to a Python object

    if "items" not in obj:
        print(f"\nAucun livre trouvé pour l'ISBN : {user_input}")
    else:
        # Accès sécurisé aux données
        book_info = obj["items"][0]
        volume_info = book_info.get("volumeInfo", {})
        search_info = book_info.get("searchInfo", {})
        access_info = book_info.get("accessInfo", {})

        title = volume_info.get("title", "Titre non disponible")
        authors = volume_info.get("authors", ["Auteur non disponible"])
        summary = search_info.get("textSnippet", "Résumé non disponible.")
        page_count = volume_info.get("pageCount", "N/A")
        language = volume_info.get("language", "N/A")
        public_domain = access_info.get("publicDomain", "N/A")

        print(f"\nTitle: {title}")
        print("\nSummary:\n")
        print(textwrap.fill(summary, width=65))
        print(f"\nAuthor(s): {', '.join(authors)}")
        print(f"\nPublic Domain: {public_domain}")
        print(f"\nPage count: {page_count}")
        print(f"\nLanguage: {language}")
        print("\n***")

    status_update = input("\nEnter another ISBN? y or n: ").lower().strip()

    if status_update == "n":
        print("\nThank you! Have a nice day.")
        break

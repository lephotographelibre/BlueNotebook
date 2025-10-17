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
Logique pour l'exportation du journal au format EPUB.
"""

import os
from pathlib import Path
from datetime import datetime
import io
import requests
from bs4 import BeautifulSoup

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    Image = ImageDraw = ImageFont = None

try:
    import ebooklib
    from ebooklib import epub
except ImportError:
    ebooklib = epub = None

try:
    import cairosvg
except ImportError:
    cairosvg = None


def create_cover_image(
    original_image_path: str, title: str, author: str, date_range: str, output_path: str
):
    """
    Crée une image de couverture composite.
    """
    if not all([Image, ImageDraw, ImageFont]):
        raise ImportError("Pillow n'est pas installé.")

    cover_width, cover_height = 600, 800
    bg_color = "white"
    text_color = "black"

    # Créer une image de fond blanche
    cover_image = Image.new("RGB", (cover_width, cover_height), bg_color)
    draw = ImageDraw.Draw(cover_image)

    # Partie supérieure : image de l'utilisateur
    if original_image_path and Path(original_image_path).exists():
        try:
            user_img = Image.open(original_image_path)
            user_img.thumbnail((cover_width, cover_height // 2))
            # Centrer l'image de l'utilisateur dans la moitié supérieure
            paste_x = (cover_width - user_img.width) // 2
            paste_y = ((cover_height // 2) - user_img.height) // 2
            cover_image.paste(user_img, (paste_x, paste_y))
        except Exception as e:
            print(f"Erreur lors du chargement de l'image de couverture : {e}")

    # Partie inférieure : texte
    text_y_start = cover_height // 2 + 40

    try:
        # Essayer de charger une police standard
        title_font = ImageFont.truetype("DejaVuSans-Bold.ttf", 36)
        author_font = ImageFont.truetype("DejaVuSans.ttf", 24)
        date_font = ImageFont.truetype("DejaVuSans-Oblique.ttf", 18)
    except IOError:
        # Fallback sur la police par défaut si non trouvée
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        date_font = ImageFont.load_default()

    # Titre
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(
        ((cover_width - title_width) / 2, text_y_start),
        title,
        font=title_font,
        fill=text_color,
    )

    # Auteur
    if author:
        author_bbox = draw.textbbox((0, 0), author, font=author_font)
        author_width = author_bbox[2] - author_bbox[0]
        draw.text(
            ((cover_width - author_width) / 2, text_y_start + 60),
            author,
            font=author_font,
            fill=text_color,
        )

    # Plage de dates
    date_bbox = draw.textbbox((0, 0), date_range, font=date_font)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text(
        ((cover_width - date_width) / 2, text_y_start + 120),
        date_range,
        font=date_font,
        fill=text_color,
    )

    cover_image.save(output_path, "JPEG")


class EpubExportWorker(QRunnable):
    """Worker pour générer l'EPUB en arrière-plan."""

    class Signals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    def __init__(self, options, notes_data, output_path, journal_dir):
        super().__init__()
        self.signals = self.Signals()
        self.options = options
        self.notes_data = notes_data
        self.output_path = output_path
        self.journal_dir = journal_dir

    def _process_html_tags(self, html_content, chapter, tag_locations, tag_counter):
        """Trouve les tags, insère des ancres et les indexe."""
        soup = BeautifulSoup(html_content, "html.parser")
        # Les tags @@mot sont convertis en <span class="tag">mot</span> par le parser Markdown
        tag_spans = soup.find_all("span", class_="tag")

        for span in tag_spans:
            if not span.string:
                continue

            tag_name = f"@@{span.string.strip()}"
            anchor_id = f"tag_anchor_{tag_counter}"

            # Insérer une ancre juste avant le tag pour pouvoir y lier
            anchor_tag = soup.new_tag("a", id=anchor_id)
            span.insert_before(anchor_tag)

            if tag_name not in tag_locations:
                tag_locations[tag_name] = []
            tag_locations[tag_name].append({"chapter": chapter, "anchor_id": anchor_id})
            tag_counter += 1

        return str(soup), tag_counter

    def _process_html_images(self, html_content, book, image_map, image_counter):
        """Trouve, traite et remplace les images dans le contenu HTML."""
        soup = BeautifulSoup(html_content, "html.parser")
        img_tags = soup.find_all("img")

        for img_tag in img_tags:
            original_src = img_tag.get("src")
            if not original_src:
                continue

            # Si l'image a déjà été traitée, on réutilise le lien
            if original_src in image_map:
                img_tag["src"] = image_map[original_src]
                continue

            image_data = None
            is_svg = original_src.lower().endswith(".svg")
            try:
                if original_src.startswith(("http://", "https://")):
                    # Image depuis une URL
                    response = requests.get(original_src, timeout=10)
                    response.raise_for_status()
                    image_data = response.content
                    content_type = response.headers.get("content-type", "").lower()
                    if "image/svg+xml" in content_type:
                        is_svg = True
                else:
                    # Image locale
                    image_path = self.journal_dir / original_src
                    if image_path.exists():
                        with open(image_path, "rb") as f:
                            image_data = f.read()

                if not image_data:
                    continue

                # Si l'image est un SVG, la convertir en PNG
                if is_svg:
                    if not cairosvg:
                        print(
                            f"Impossible de traiter l'image SVG {original_src}: la bibliothèque 'cairosvg' est requise."
                        )
                        continue
                    try:
                        image_data = cairosvg.svg2png(bytestring=image_data)
                    except Exception as svg_error:
                        print(
                            f"Erreur de conversion SVG pour {original_src}: {svg_error}"
                        )
                        continue

                if not image_data:
                    continue

                # Traitement de l'image avec Pillow
                img = Image.open(io.BytesIO(image_data))
                img.thumbnail((800, 800))  # Taille maxi 800x800

                # Conversion en JPG avec compression
                img_byte_arr = io.BytesIO()
                # Convertir en RGB si nécessaire (pour les PNG avec transparence)
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                img.save(img_byte_arr, format="JPEG", quality=80)
                processed_image_data = img_byte_arr.getvalue()

                # Ajout de l'image à l'EPUB
                epub_img_filename = f"Images/img_{image_counter}.jpg"
                epub_img = epub.EpubImage(
                    uid=f"img_{image_counter}",
                    file_name=epub_img_filename,
                    media_type="image/jpeg",
                    content=processed_image_data,
                )
                book.add_item(epub_img)

                # Mise à jour du src dans le HTML et dans le map
                img_tag["src"] = epub_img_filename
                image_map[original_src] = epub_img_filename
                image_counter += 1

            except Exception as e:
                print(f"Impossible de traiter l'image {original_src}: {e}")

        return str(soup), image_counter

    def run(self):
        if not all([ebooklib, epub]):
            self.signals.error.emit(
                "La bibliothèque 'EbookLib' est requise.\nInstallez-la avec : pip install EbookLib"
            )
            return
        if not all([Image, ImageDraw, ImageFont]):
            self.signals.error.emit(
                "Les bibliothèques 'EbookLib' et 'Pillow' sont requises.\n"
                "Installez-les avec : pip install EbookLib Pillow"
            )
            return

        try:
            book = epub.EpubBook()

            # Métadonnées
            book.set_identifier(f"urn:uuid:{datetime.now().strftime('%Y%m%d%H%M%S')}")
            book.set_title(self.options["title"])
            book.set_language("fr")
            if self.options["author"]:
                book.add_author(self.options["author"])

            # Création de la couverture
            cover_image_path = self.journal_dir / "images" / "epub_cover.jpg"
            cover_image_path.parent.mkdir(exist_ok=True)
            date_range_str = f"Du {self.options['start_date'].toString('d MMMM yyyy')} au {self.options['end_date'].toString('d MMMM yyyy')}"

            create_cover_image(
                self.options["cover_image"],
                self.options["title"],
                self.options["author"],
                date_range_str,
                str(cover_image_path),
            )

            # Vérifier que le fichier existe et le lire correctement
            if cover_image_path.exists():
                with open(cover_image_path, "rb") as cover_file:
                    cover_data = cover_file.read()
                book.set_cover("cover.jpg", cover_data, create_page=True)
            else:
                print("Attention: la couverture n'a pas pu être créée")

            # Création des chapitres
            chapters = []
            image_map = {}
            tag_locations = {}
            image_counter = 1
            toc_structure = []
            tag_counter = 1

            for i, (note_date, html_content) in enumerate(self.notes_data):
                chapter_title = note_date.strftime("%A %d %B %Y")
                file_name = f"chap_{i+1}.xhtml"
                chapter = epub.EpubHtml(
                    title=chapter_title, file_name=file_name, lang="fr"
                )

                sub_chapters = []

                # 1. Traiter les images
                processed_html, image_counter = self._process_html_images(
                    html_content, book, image_map, image_counter
                )

                # 2. Traiter les tags et insérer les ancres
                processed_html, tag_counter = self._process_html_tags(
                    processed_html, chapter, tag_locations, tag_counter
                )

                # 3. Analyser les H1/H2 pour la table des matières
                soup = BeautifulSoup(processed_html, "html.parser")
                for j, header_tag in enumerate(soup.find_all(["h1", "h2"])):
                    header_title = header_tag.get_text(strip=True)
                    if not header_title:
                        continue

                    # Créer une ancre pour le lien
                    anchor_id = f"header_{i+1}_{j}"
                    header_tag["id"] = anchor_id

                    # Créer un lien pour la table des matières
                    # S'assurer que tous les paramètres sont des chaînes non vides
                    link_href = f"{file_name}#{anchor_id}"
                    link_title = str(header_title)
                    link_uid = f"link_{i+1}_{j}"

                    # print(
                    #    f"DEBUG: Création lien - href: {link_href}, title: {link_title}, uid: #{link_uid}"
                    # )

                    try:
                        link = epub.Link(link_href, link_title, link_uid)
                        sub_chapters.append(link)
                    except Exception as link_error:
                        print(f"DEBUG: Erreur création lien: {link_error}")
                        continue

                processed_html = str(soup)

                # Utiliser le HTML avec les chemins d'images mis à jour
                chapter.content = f"<h1>{chapter_title}</h1>{processed_html}"

                book.add_item(chapter)
                chapters.append(chapter)
                toc_structure.append((chapter, tuple(sub_chapters)))

            # Création de la page d'index des tags
            index_page = None
            if tag_locations:
                index_title = "Index de Tags"
                index_file_name = "index_tags.xhtml"
                index_page = epub.EpubHtml(
                    title=index_title, file_name=index_file_name, lang="fr"
                )

                index_content = f"<h1>{index_title}</h1>"
                index_content += (
                    '<div style="columns: 2; -webkit-columns: 2; -moz-columns: 2;">'
                )

                # Trier les tags par ordre alphabétique
                for tag_name in sorted(tag_locations.keys()):
                    index_content += f"<h2>{tag_name}</h2><ul>"
                    for i, loc in enumerate(tag_locations[tag_name]):
                        link_href = f"{loc['chapter'].file_name}#{loc['anchor_id']}"
                        index_content += (
                            f'<li><a href="{link_href}">Page {i+1}</a></li>'
                        )
                    index_content += "</ul>"

                index_content += "</div>"
                index_page.content = index_content
                book.add_item(index_page)

            # Table des matières
            book.toc = []

            # print(
            #    f"DEBUG: Nombre de chapitres dans toc_structure: {len(toc_structure)}"
            # )

            for idx, (main_chap, sub_links) in enumerate(toc_structure):
                # print(
                #    f"DEBUG: Chapitre {idx}: {main_chap.title}, sous-liens: {len(sub_links)}"
                # )
                if sub_links:
                    # Vérifier que tous les liens sont valides
                    valid_links = []
                    for link in sub_links:
                        if link and hasattr(link, "href") and hasattr(link, "title"):
                            # print(f"DEBUG: Lien valide: {link.title} -> {link.href}")
                            valid_links.append(link)
                        else:
                            print(f"DEBUG: Lien invalide détecté: {link}")

                    if valid_links:
                        # Si des sous-chapitres existent, créer une entrée hiérarchique
                        book.toc.append((main_chap, valid_links))
                    else:
                        # Pas de sous-liens valides, ajouter juste le chapitre
                        book.toc.append(main_chap)
                else:
                    # Sinon, ajouter simplement le chapitre
                    book.toc.append(main_chap)

            # Ajouter l'index des tags à la fin
            if index_page:
                # print(f"DEBUG: Ajout de l'index des tags: {index_page.title}")
                book.toc.append(
                    epub.Link(index_page.file_name, index_page.title, "index-link")
                )

            # Ajout de la navigation
            book.add_item(epub.EpubNcx())
            book.add_item(epub.EpubNav())

            # Définition du style (simple)
            style = """
BODY { 
    font-family: serif; 
}
.tag {
    background-color: #f0f0f0;
    padding: 2px 6px;
    border-radius: 3px;
    font-weight: bold;
}
"""
            nav_css = epub.EpubItem(
                uid="style_nav",
                file_name="style/nav.css",
                media_type="text/css",
                content=style,
            )
            book.add_item(nav_css)

            # Définition du "spine" (ordre de lecture)
            spine_items = ["cover", "nav"] + chapters
            if index_page:
                spine_items.append(index_page)

            book.spine = spine_items

            # Définition du guide (pour la compatibilité)
            if cover_image_path.exists():
                book.guide.append(
                    {"href": "cover.xhtml", "title": "Couverture", "type": "cover"}
                )

            # Écriture du fichier EPUB
            # print(f"DEBUG: Écriture de l'EPUB avec {len(book.toc)} entrées dans la TOC")
            # print(f"DEBUG: Structure de book.toc: {book.toc}")

            try:
                epub.write_epub(self.output_path, book, {})
                print("📚 Livre EPUB écrit avec succès")
            except Exception as write_error:
                # print(f"DEBUG: Erreur lors de l'écriture: {write_error}")
                import traceback

                traceback.print_exc()
                raise

            # Nettoyage de l'image de couverture temporaire
            if cover_image_path.exists():
                try:
                    os.remove(cover_image_path)
                except Exception as cleanup_error:
                    print(
                        f"Impossible de supprimer l'image temporaire : {cleanup_error}"
                    )

            self.signals.finished.emit(self.output_path)

        except Exception as e:
            self.signals.error.emit(str(e))

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

import re
import os
from pathlib import Path
from datetime import datetime
import io
import requests
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QMessageBox, QDialog, QFileDialog
from PyQt5.QtCore import QDate
from gui.date_range_dialog import DateRangeDialog

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
        raise ImportError(self.tr("Pillow n'est pas installé."))

    cover_width, cover_height = 600, 800
    bg_color = self.tr("white")
    text_color = self.tr("black")

    # Créer une image de fond blanche
    cover_image = Image.new(self.tr("RGB"), (cover_width, cover_height), bg_color)
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
            print(self.tr("Erreur lors du chargement de l'image de couverture : %1").arg(e))

    # Partie inférieure : texte
    text_y_start = cover_height // 2 + 40

    try:
        # Essayer de charger une police standard
        title_font = ImageFont.truetype(self.tr("DejaVuSans-Bold.ttf"), 36)
        author_font = ImageFont.truetype(self.tr("DejaVuSans.ttf"), 24)
        date_font = ImageFont.truetype(self.tr("DejaVuSans-Oblique.ttf"), 18)
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

    cover_image.save(output_path, self.tr("JPEG"))


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
        soup = BeautifulSoup(html_content, self.tr("html.parser"))
        # Les tags @@mot sont convertis en <span class="tag">mot</span> par le parser Markdown
        tag_spans = soup.find_all(self.tr("span"), class_=self.tr("tag"))

        for span in tag_spans:
            if not span.string:
                continue

            tag_name = self.tr("@@%1").arg(span.string.strip())
            anchor_id = self.tr("tag_anchor_%1").arg(tag_counter)

            # Insérer une ancre juste avant le tag pour pouvoir y lier
            anchor_tag = soup.new_tag(self.tr("a"), id=anchor_id)
            span.insert_before(anchor_tag)

            if tag_name not in tag_locations:
                tag_locations[tag_name] = []
            tag_locations[tag_name].append({self.tr("chapter"): chapter, self.tr("anchor_id"): anchor_id})
            tag_counter += 1

        return str(soup), tag_counter

    def _process_html_images(self, html_content, book, image_map, image_counter):
        """Trouve, traite et remplace les images dans le contenu HTML."""
        soup = BeautifulSoup(html_content, self.tr("html.parser"))
        img_tags = soup.find_all(self.tr("img"))

        for img_tag in img_tags:
            original_src = img_tag.get(self.tr("src"))
            if not original_src:
                continue

            # Si l'image a déjà été traitée, on réutilise le lien
            if original_src in image_map:
                img_tag[self.tr("src")] = image_map[original_src]
                continue

            image_data = None
            is_svg = original_src.lower().endswith(".svg")
            try:
                if original_src.startswith(("http://", "https://")):
                    # Image depuis une URL
                    response = requests.get(original_src, timeout=10)
                    response.raise_for_status()
                    image_data = response.content
                    content_type = response.headers.get(self.tr("content-type"), self.tr("")).lower()
                    if self.tr("image/svg+xml") in content_type:
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
                            self.tr("Impossible de traiter l'image SVG %1: la bibliothèque 'cairosvg' est requise.").arg(original_src)
                        )
                        continue
                    try:
                        image_data = cairosvg.svg2png(bytestring=image_data)
                    except Exception as svg_error:
                        print(
                            self.tr("Erreur de conversion SVG pour %1: %2").arg(original_src).arg(svg_error)
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
                if img.mode in (self.tr("RGBA"), self.tr("P")):
                    img = img.convert(self.tr("RGB"))
                img.save(img_byte_arr, format=self.tr("JPEG"), quality=80)
                processed_image_data = img_byte_arr.getvalue()

                # Ajout de l'image à l'EPUB
                epub_img_filename = self.tr("Images/img_%1.jpg").arg(image_counter)
                epub_img = epub.EpubImage(
                    uid=self.tr("img_%1").arg(image_counter),
                    file_name=epub_img_filename,
                    media_type=self.tr("image/jpeg"),
                    content=processed_image_data,
                )
                book.add_item(epub_img)

                # Mise à jour du src dans le HTML et dans le map
                img_tag[self.tr("src")] = epub_img_filename
                image_map[original_src] = epub_img_filename
                image_counter += 1

            except Exception as e:
                print(self.tr("Impossible de traiter l'image %1: %2").arg(original_src).arg(e))

        return str(soup), image_counter

    def run(self):
        if not all([ebooklib, epub]):
            self.signals.error.emit(
                self.tr("La bibliothèque 'EbookLib' est requise.\nInstallez-la avec : pip install EbookLib")
            )
            return
        if not all([Image, ImageDraw, ImageFont]):
            self.signals.error.emit(
                self.tr("Les bibliothèques 'EbookLib' et 'Pillow' sont requises.\n")
                self.tr("Installez-les avec : pip install EbookLib Pillow")
            )
            return

        try:
            book = epub.EpubBook()

            # Métadonnées
            book.set_identifier(self.tr("urn:uuid:%1").arg(datetime.now().strftime('%Y%m%d%H%M%S')))
            book.set_title(self.options[self.tr("title")])
            book.set_language(self.tr("fr"))
            if self.options[self.tr("author")]:
                book.add_author(self.options[self.tr("author")])

            # Création de la couverture
            cover_image_path = self.journal_dir / self.tr("images") / self.tr("epub_cover.jpg")
            cover_image_path.parent.mkdir(exist_ok=True)
            date_range_str = self.tr("Du %1 au %2").arg(self.options[self.tr('start_date')].toString(self.tr('d MMMM yyyy'))).arg(self.options[self.tr('end_date')].toString(self.tr('d MMMM yyyy')))

            create_cover_image(
                self.options[self.tr("cover_image")],
                self.options[self.tr("title")],
                self.options[self.tr("author")],
                date_range_str,
                str(cover_image_path),
            )

            # Vérifier que le fichier existe et le lire correctement
            if cover_image_path.exists():
                with open(cover_image_path, "rb") as cover_file:
                    cover_data = cover_file.read()
                book.set_cover(self.tr("cover.jpg"), cover_data, create_page=True)
            else:
                print(self.tr("Attention: la couverture n'a pas pu être créée"))

            # Création des chapitres
            chapters = []
            image_map = {}
            tag_locations = {}
            image_counter = 1
            toc_structure = []
            tag_counter = 1

            for i, (note_date, html_content) in enumerate(self.notes_data):
                chapter_title = note_date.strftime("%A %d %B %Y")
                file_name = self.tr("chap_%1.xhtml").arg(i+1)
                chapter = epub.EpubHtml(
                    title=chapter_title, file_name=file_name, lang=self.tr("fr")
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
                soup = BeautifulSoup(processed_html, self.tr("html.parser"))
                for j, header_tag in enumerate(soup.find_all([self.tr("h1"), self.tr("h2")])):
                    header_title = header_tag.get_text(strip=True)
                    if not header_title:
                        continue

                    # Créer une ancre pour le lien
                    anchor_id = self.tr("header_%1_%2").arg(i+1).arg(j)
                    header_tag[self.tr("id")] = anchor_id

                    # Créer un lien pour la table des matières
                    # S'assurer que tous les paramètres sont des chaînes non vides
                    link_href = self.tr("%1#%2").arg(file_name).arg(anchor_id)
                    link_title = str(header_title)
                    link_uid = self.tr("link_%1_%2").arg(i+1).arg(j)

                    # print(
                    #    self.tr("DEBUG: Création lien - href: %1, title: %2, uid: #%3").arg(link_href).arg(link_title).arg(link_uid)
                    # )

                    try:
                        link = epub.Link(link_href, link_title, link_uid)
                        sub_chapters.append(link)
                    except Exception as link_error:
                        print(self.tr("DEBUG: Erreur création lien: %1").arg(link_error))
                        continue

                processed_html = str(soup)

                # Utiliser le HTML avec les chemins d'images mis à jour
                chapter.content = self.tr("<h1>%1</h1>%2").arg(chapter_title).arg(processed_html)

                book.add_item(chapter)
                chapters.append(chapter)
                toc_structure.append((chapter, tuple(sub_chapters)))

            # Création de la page d'index des tags
            index_page = None
            if tag_locations:
                index_title = self.tr("Index de Tags")
                index_file_name = self.tr("index_tags.xhtml")
                index_page = epub.EpubHtml(
                    title=index_title, file_name=index_file_name, lang=self.tr("fr")
                )

                index_content = self.tr("<h1>%1</h1>").arg(index_title)
                index_content += (
                    self.tr('<div style="columns: 2; -webkit-columns: 2; -moz-columns: 2;">')
                )

                # Trier les tags par ordre alphabétique
                for tag_name in sorted(tag_locations.keys()):
                    index_content += self.tr("<h2>%1</h2><ul>").arg(tag_name)
                    for i, loc in enumerate(tag_locations[tag_name]):
                        link_href = self.tr("%1#%2").arg(loc[self.tr('chapter')].file_name).arg(loc[self.tr('anchor_id')])
                        index_content += (
                            self.tr("<li><a href="%1">Page %2</a></li>").arg(link_href).arg(i+1)
                        )
                    index_content += self.tr("</ul>")

                index_content += self.tr("</div>")
                index_page.content = index_content
                book.add_item(index_page)

            # Table des matières
            book.toc = []

            # print(
            #    self.tr("DEBUG: Nombre de chapitres dans toc_structure: %1").arg(len(toc_structure))
            # )

            for idx, (main_chap, sub_links) in enumerate(toc_structure):
                # print(
                #    self.tr("DEBUG: Chapitre %1: %2, sous-liens: %3").arg(idx).arg(main_chap.title).arg(len(sub_links))
                # )
                if sub_links:
                    # Vérifier que tous les liens sont valides
                    valid_links = []
                    for link in sub_links:
                        if link and hasattr(link, self.tr("href")) and hasattr(link, self.tr("title")):
                            # print(self.tr("DEBUG: Lien valide: %1 -> %2").arg(link.title).arg(link.href))
                            valid_links.append(link)
                        else:
                            print(self.tr("DEBUG: Lien invalide détecté: %1").arg(link))

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
                # print(self.tr("DEBUG: Ajout de l'index des tags: %1").arg(index_page.title))
                book.toc.append(
                    epub.Link(index_page.file_name, index_page.title, self.tr("index-link"))
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
                uid=self.tr("style_nav"),
                file_name="style/nav.css",
                media_type=self.tr("text/css"),
                content=style,
            )
            book.add_item(nav_css)

            # Définition du "spine" (ordre de lecture)
            spine_items = [self.tr("cover"), self.tr("nav")] + chapters
            if index_page:
                spine_items.append(index_page)

            book.spine = spine_items

            # Définition du guide (pour la compatibilité)
            if cover_image_path.exists():
                book.guide.append(
                    {self.tr("href"): self.tr("cover.xhtml"), self.tr("title"): self.tr("Couverture"), self.tr("type"): self.tr("cover")}
                )

            # Écriture du fichier EPUB
            # print(self.tr("DEBUG: Écriture de l'EPUB avec %1 entrées dans la TOC").arg(len(book.toc)))
            # print(self.tr("DEBUG: Structure de book.toc: %1").arg(book.toc))

            try:
                epub.write_epub(self.output_path, book, {})
                print(self.tr("📚 Livre EPUB écrit avec succès"))
            except Exception as write_error:
                # print(self.tr("DEBUG: Erreur lors de l'écriture: %1").arg(write_error))
                import traceback

                traceback.print_exc()
                raise

            # Nettoyage de l'image de couverture temporaire
            if cover_image_path.exists():
                try:
                    os.remove(cover_image_path)
                except Exception as cleanup_error:
                    print(
                        self.tr("Impossible de supprimer l'image temporaire : %1").arg(cleanup_error)
                    )

            self.signals.finished.emit(self.output_path)

        except Exception as e:
            self.signals.error.emit(str(e))


def export_journal_epub_worker(main_window, options, note_files, epub_path):
    """Filtre les notes et lance le worker d'exportation EPUB."""
    # Filtrer les notes et préparer les données
    notes_data = []
    for note_file in note_files:
        note_date_str = os.path.splitext(note_file)[0]
        note_date_obj = datetime.strptime(note_date_str, "%Y%m%d").date()
        if (
            options[self.tr("start_date")].toPyDate()
            <= note_date_obj
            <= options[self.tr("end_date")].toPyDate()
        ):
            with open(
                main_window.journal_directory / note_file, "r", encoding="utf-8"
            ) as f:
                markdown_content = f.read()
            main_window.preview.md.reset()
            html_note = main_window.preview.md.convert(markdown_content)
            notes_data.append((note_date_obj, html_note))

    # Lancer le worker en arrière-plan
    main_window._start_export_flashing()
    worker = EpubExportWorker(
        options, notes_data, epub_path, main_window.journal_directory
    )
    worker.signals.finished.connect(main_window._on_export_finished)
    worker.signals.error.connect(main_window._on_export_error)
    main_window.thread_pool.start(worker)

    # Mémoriser les paramètres pour la prochaine fois
    main_window.settings_manager.set(self.tr("epub.last_directory"), str(Path(epub_path).parent))
    main_window.settings_manager.set(self.tr("epub.last_author"), options[self.tr("author")])
    main_window.settings_manager.set(self.tr("epub.last_title"), options[self.tr("title")])
    main_window.settings_manager.save_settings()


def export_journal_to_epub(main_window):
    """Exporte l'ensemble du journal dans un unique fichier EPUB."""
    try:
        from ebooklib import epub
        from PIL import Image
    except ImportError:
        QMessageBox.critical(
            main_window,
            self.tr("Modules manquants"),
            self.tr("Les bibliothèques 'EbookLib' et 'Pillow' sont requises.\n\n")
            self.tr("Pour utiliser cette fonctionnalité, installez-les avec:\n")
            self.tr("pip install EbookLib Pillow"),
        )
        return

    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            self.tr("Exportation impossible"),
            self.tr("Aucun répertoire de journal n'est actuellement défini."),
        )
        return

    note_files = sorted(
        [
            f
            for f in os.listdir(main_window.journal_directory)
            if f.endswith(".md") and re.match(r"^\d{8}\.md$", f)
        ]
    )

    if not note_files:
        QMessageBox.information(
            main_window, self.tr("Journal vide"), self.tr("Aucune note à exporter dans le journal.")
        )
        return

    min_date_obj = datetime.strptime(os.path.splitext(note_files[0])[0], "%Y%m%d")
    min_date_q = QDate(min_date_obj.year, min_date_obj.month, min_date_obj.day)
    today_q = QDate.currentDate()

    last_author = main_window.settings_manager.get(self.tr("epub.last_author"), self.tr(""))
    last_title = main_window.settings_manager.get(
        self.tr("epub.last_title"), self.tr("BlueNotebook Journal")
    )
    default_logo_path = (
        Path(__file__).parent.parent
        / self.tr("resources")
        / self.tr("images")
        / self.tr("bluenotebook_256-x256_fond_blanc.png")
    )

    date_dialog = DateRangeDialog(
        start_date_default=min_date_q,
        end_date_default=today_q,
        min_date=min_date_q,
        max_date=today_q,
        default_title=last_title,
        default_cover_image=str(default_logo_path),
        default_author=last_author,
        parent=main_window,
    )
    date_dialog.setWindowTitle(self.tr("Options d'exportation du Journal EPUB"))

    if date_dialog.exec_() != QDialog.Accepted:
        return

    options = date_dialog.get_export_options()

    last_epub_dir = main_window.settings_manager.get(self.tr("epub.last_directory"))
    if not last_epub_dir or not Path(last_epub_dir).is_dir():
        last_epub_dir = str(main_window.journal_directory.parent)

    default_filename = self.tr("Journal-%1-%2.epub").arg(options[self.tr('start_date')].toString(self.tr('ddMMyyyy'))).arg(options[self.tr('end_date')].toString(self.tr('ddMMyyyy')))
    default_path = os.path.join(last_epub_dir, default_filename)

    epub_path, _ = QFileDialog.getSaveFileName(
        main_window,
        self.tr("Exporter le journal en EPUB"),
        default_path,
        self.tr("Fichiers EPUB (*.epub)"),
    )

    if not epub_path:
        return

    export_journal_epub_worker(main_window, options, note_files, epub_path)

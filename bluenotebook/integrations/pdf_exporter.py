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
Logique pour l'exportation au format PDF.
"""
import json
import os
import re
from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, QDate, QCoreApplication
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog
from pathlib import Path

from bs4 import BeautifulSoup

from gui.date_range_dialog import DateRangeDialog

# This will create a circular import if MainWindow is imported directly.
# We will pass MainWindow as an argument to the functions.


class PdfExporterContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("PdfExporterContext", text)


def get_pdf_theme_css(settings_manager) -> str:
    """
    Charge et retourne la chaîne de caractères du thème CSS pour les exports PDF.
    """
    pdf_theme_filename = settings_manager.get("pdf.css_theme", "default_preview.css")
    base_path = Path(__file__).parent.parent

    # Le thème peut être dans css_pdf ou css_preview
    css_pdf_path = base_path / "resources" / "css_pdf" / pdf_theme_filename
    css_preview_path = base_path / "resources" / "css_preview" / pdf_theme_filename

    css_path_to_load = css_pdf_path if css_pdf_path.exists() else css_preview_path

    content_css_string = ""
    if css_path_to_load.exists():
        try:
            with open(css_path_to_load, "r", encoding="utf-8") as f:
                content_css_string = f.read()
        except IOError as e:
            print(f"⚠️ Error reading CSS file: '{css_path_to_load}': {e}")

    return content_css_string


class PdfExportWorker(QRunnable):
    """Worker pour générer le PDF en arrière-plan, incluant la préparation du HTML."""

    class Signals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    def __init__(self, options, notes_data, content_css_string, base_url, output_path):
        super().__init__()
        self.signals = self.Signals()
        self.options = options
        self.notes_data = notes_data
        self.content_css_string = content_css_string
        self.base_url = base_url
        self.output_path = output_path

    @staticmethod
    def _build_html_and_css(
        options, notes_data, content_css_string
    ) -> (str, list[str]):
        """Construit le contenu HTML et CSS complet pour l'export PDF."""
        all_html_content = ""

        # 1. Page de garde
        cover_image_path = options.get("cover_image", "")
        image_abs_path = ""
        if cover_image_path and Path(cover_image_path).exists():
            image_abs_path = str(Path(cover_image_path).resolve())

        image_html = (
            f'<img src="{image_abs_path}" alt="Image de couverture" style="max-width: 400px; max-height: 400px; width: auto; height: auto;">'
            if image_abs_path
            else ""
        )

        pdf_author = options.get("author", "")
        author_html = ""
        if pdf_author:
            # Correction i18n : Extraire tr() de la f-string pour que l'outil de traduction détecte la chaîne
            author_fmt = PdfExporterContext.tr("Auteur : {author}")
            author_html = (
                f'<p class="cover-author">{author_fmt.format(author=pdf_author)}</p>'
            )

        # V2.9.2 - Ajouter le tag de filtre sur la page de garde s'il existe
        selected_tag = options.get("selected_tag")
        tag_html = ""
        if selected_tag:
            # Correction i18n : Extraire tr() de la f-string
            tag_fmt = PdfExporterContext.tr("Filtré par tag : <strong>{tag}</strong>")
            tag_html = f'<p class="cover-tag">{tag_fmt.format(tag=selected_tag)}</p>'

        period_text = PdfExporterContext.tr("Période du {start} au {end}").format(
            start=options["start_date"].toString("d MMMM yyyy"),
            end=options["end_date"].toString("d MMMM yyyy"),
        )

        cover_page_html = f"""
        <div class="cover-page">
            {image_html}
            <h1>{options.get('title', PdfExporterContext.tr("Journal"))}</h1>
            {author_html}
            <p class="cover-date">{period_text}</p>
            {tag_html}
        </div>
        """
        all_html_content += cover_page_html

        # 2. Contenu des notes
        for note_date, html_note in notes_data:
            date_formatted = note_date.strftime("%A %d %B %Y").capitalize()
            all_html_content += f"""
            <div class="journal-entry">
                <h2 class="entry-date">{date_formatted}</h2>
                {html_note}
            </div>
            """

        # 3. CSS pour WeasyPrint
        # Charger le CSS de base depuis un fichier externe
        base_css_path = (
            Path(__file__).parent.parent / "resources" / "css_pdf" / "default_pdf.css"
        )
        try:
            with open(base_css_path, "r", encoding="utf-8") as f:
                base_weasyprint_css = f.read()
        except FileNotFoundError:
            print(f"⚠️ Default CSS file not found : {base_css_path}")
            base_weasyprint_css = ""

        # Gérer le titre dynamique qui ne peut pas être dans le fichier CSS statique
        escaped_pdf_title = options.get("title", "").replace('"', '\\"')
        dynamic_css = f"""
        @page {{ 
            @bottom-left {{
                content: "{escaped_pdf_title}";
                font-size: 8pt; color: #999;
            }}
        }}
        """

        # Combiner le CSS de base et le CSS dynamique
        weasyprint_css = base_weasyprint_css + dynamic_css

        # Le CSS du contenu est maintenant passé en paramètre
        all_css = [weasyprint_css, content_css_string]

        # 4. HTML final
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head><meta charset="UTF-8"><title>{options.get('title', PdfExporterContext.tr("Journal"))}</title></head>
        <body>{all_html_content}</body>
        </html>
        """
        return full_html, all_css

    def run(self):
        """Exécute la conversion en PDF."""
        try:
            from weasyprint import HTML, CSS

            html_string, css_strings = self._build_html_and_css(
                self.options, self.notes_data, self.content_css_string
            )

            html_doc = HTML(string=html_string, base_url=self.base_url)
            stylesheets = [CSS(string=css) for css in css_strings]
            html_doc.write_pdf(self.output_path, stylesheets=stylesheets)
            self.signals.finished.emit(self.output_path)

        except ImportError:
            message = PdfExporterContext.tr(
                "La bibliothèque 'WeasyPrint' est requise.\n"
                "Installez-la avec : pip install WeasyPrint"
            )
            self.signals.error.emit(message)
        except Exception as e:
            self.signals.error.emit(str(e))


# Constructeur mis à jour pour la nouvelle logique
def create_pdf_export_worker(
    options, notes_data, content_css_string, journal_dir, output_path
):
    return PdfExportWorker(
        options=options,
        notes_data=notes_data,
        content_css_string=content_css_string,
        base_url=str(journal_dir),
        output_path=output_path,
    )


def export_single_pdf(main_window):
    """Exporter le fichier actuel en PDF avec WeasyPrint."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        QMessageBox.critical(
            main_window,
            PdfExporterContext.tr("Module manquant"),
            PdfExporterContext.tr(
                "WeasyPrint n'est pas installé.\n\n"
                "Pour utiliser cette fonctionnalité, installez-le avec:\n"
                "pip install weasyprint"
            ),
        )
        return

    if main_window.current_file:
        base_name = os.path.basename(main_window.current_file)
        file_stem = os.path.splitext(base_name)[0]
        clean_filename = file_stem.lower().replace(" ", "-")
    else:
        clean_filename = "nouveau-fichier"

    last_pdf_dir = main_window.settings_manager.get("pdf.last_directory")
    if not last_pdf_dir or not Path(last_pdf_dir).is_dir():
        last_pdf_dir = str(Path.home())

    default_filename = f"{clean_filename}.pdf"
    default_path = os.path.join(last_pdf_dir, default_filename)

    filename, _ = QFileDialog.getSaveFileName(
        main_window,
        PdfExporterContext.tr("Exporter en PDF"),
        default_path,
        PdfExporterContext.tr("Fichiers PDF (*.pdf)"),
    )

    if not filename:
        return

    try:
        if (
            main_window.journal_directory
            and main_window.current_file
            and str(main_window.current_file).startswith(
                str(main_window.journal_directory)
            )
        ):
            base_url = str(main_window.journal_directory)
        elif main_window.current_file:
            base_url = str(Path(main_window.current_file).parent)
        else:
            base_url = str(Path.home())

        html_content = main_window.preview.get_html()

        if main_window.journal_directory and main_window.current_file:
            soup = BeautifulSoup(html_content, "html.parser")
            for img in soup.find_all("img"):
                src = img.get("src")
                if src and not src.startswith(
                    ("http://", "https://", "data:", "file://")
                ):
                    full_path = (main_window.journal_directory / src).resolve()
                    if full_path.exists():
                        img["src"] = str(full_path)
            for link in soup.find_all("a"):
                href = link.get("href")
                if href and not href.startswith(
                    ("http://", "https://", "data:", "file://", "#")
                ):
                    full_path = (main_window.journal_directory / href).resolve()
                    if full_path.exists():
                        link["href"] = str(full_path)
            html_content = str(soup)

        content_css_string = get_pdf_theme_css(main_window.settings_manager)

        html = HTML(string=html_content, base_url=base_url)
        html.write_pdf(filename, stylesheets=[CSS(string=content_css_string)])

        main_window.statusbar.showMessage(
            PdfExporterContext.tr("Exporté en PDF : {filename}").format(
                filename=filename
            ),
            3000,
        )
        main_window.settings_manager.set(
            "pdf.last_directory", str(Path(filename).parent)
        )
        main_window.settings_manager.save_settings()
    except Exception as e:
        QMessageBox.critical(
            main_window,
            PdfExporterContext.tr("Erreur"),
            PdfExporterContext.tr("Impossible d'exporter en PDF :\n{error}").format(
                error=str(e)
            ),
        )


def export_journal_to_pdf(main_window):
    """Exporte l'ensemble du journal dans un unique fichier PDF avec WeasyPrint."""
    try:
        from weasyprint import HTML, CSS
    except ImportError:
        QMessageBox.critical(
            main_window,
            PdfExporterContext.tr("Module manquant"),
            PdfExporterContext.tr(
                "WeasyPrint n'est pas installé.\n\n"
                "Pour utiliser cette fonctionnalité, installez-le avec:\n"
                "pip install weasyprint"
            ),
        )
        return

    if not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            PdfExporterContext.tr("Exportation impossible"),
            PdfExporterContext.tr(
                "Aucun répertoire de journal n'est actuellement défini."
            ),
        )
        return

    tags_index_path = main_window.journal_directory / "index_tags.json"
    available_tags = []
    if tags_index_path.exists():
        try:
            with open(tags_index_path, "r", encoding="utf-8") as f:
                tags_data = json.load(f)
                available_tags = sorted(tags_data.keys())
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️ Error reading tag index : {e}")

    note_files = sorted(
        [
            f
            for f in os.listdir(main_window.journal_directory)
            if f.endswith(".md") and re.match(r"^\d{8}\.md$", f)
        ]
    )

    if not note_files:
        QMessageBox.information(
            main_window,
            PdfExporterContext.tr("Journal vide"),
            PdfExporterContext.tr("Aucune note à exporter dans le journal."),
        )
        return

    first_note_date_obj = datetime.strptime(
        os.path.splitext(note_files[0])[0], "%Y%m%d"
    )
    min_date_q = QDate(
        first_note_date_obj.year, first_note_date_obj.month, first_note_date_obj.day
    )
    today_q = QDate.currentDate()

    last_author = main_window.settings_manager.get("pdf.last_author", "")
    last_title = main_window.settings_manager.get(
        "pdf.last_title", "BlueNotebook Journal"
    )
    default_logo_path = (
        Path(__file__).parent.parent
        / "resources"
        / "images"
        / "bluenotebook_256-x256_fond_blanc.png"
    )

    date_dialog = DateRangeDialog(
        start_date_default=min_date_q,
        end_date_default=today_q,
        min_date=min_date_q,
        max_date=today_q,
        available_tags=available_tags,
        default_title=last_title,
        default_cover_image=str(default_logo_path),
        default_author=last_author,
        parent=main_window,
    )

    if date_dialog.exec_() != QDialog.Accepted:
        return

    options = date_dialog.get_export_options()
    export_journal_to_pdf_worker(main_window, options, note_files, tags_index_path)


def export_journal_to_pdf_worker(main_window, options, note_files, tags_index_path):
    start_date_q = options["start_date"]
    end_date_q = options["end_date"]
    selected_tag = options.get("selected_tag")

    filtered_notes = []
    for note_file in note_files:
        note_date_str = os.path.splitext(note_file)[0]
        note_date_obj = datetime.strptime(note_date_str, "%Y%m%d").date()
        if start_date_q.toPyDate() <= note_date_obj <= end_date_q.toPyDate():
            filtered_notes.append(note_file)

    if selected_tag:
        try:
            with open(tags_index_path, "r", encoding="utf-8") as f:
                tags_data = json.load(f)
            files_with_tag = {d["filename"] for d in tags_data[selected_tag]["details"]}
            filtered_notes = [note for note in filtered_notes if note in files_with_tag]
        except (KeyError, FileNotFoundError) as e:
            print(f"⚠️ Error filtering by tag: {e}")
            filtered_notes = []

    if not filtered_notes:
        QMessageBox.information(
            main_window,
            PdfExporterContext.tr("Aucune note"),
            PdfExporterContext.tr(
                "Aucune note trouvée pour les critères sélectionnés."
            ),
        )
        return

    last_pdf_dir = main_window.settings_manager.get("pdf.last_directory")
    if not last_pdf_dir or not Path(last_pdf_dir).is_dir():
        last_pdf_dir = str(main_window.journal_directory.parent)

    default_filename = f"Journal-{start_date_q.toString('ddMMyyyy')}-{end_date_q.toString('ddMMyyyy')}.pdf"
    default_path = os.path.join(last_pdf_dir, default_filename)

    pdf_path, _ = QFileDialog.getSaveFileName(
        main_window,
        PdfExporterContext.tr("Exporter le journal en PDF"),
        default_path,
        PdfExporterContext.tr("Fichiers PDF (*.pdf)"),
    )

    if not pdf_path:
        return

    notes_data = []
    for note_file in filtered_notes:
        try:
            with open(
                main_window.journal_directory / note_file, "r", encoding="utf-8"
            ) as f:
                markdown_content = f.read()
            main_window.preview.md.reset()
            html_note = main_window.preview.md.convert(markdown_content)
            date_obj = datetime.strptime(os.path.splitext(note_file)[0], "%Y%m%d")
            notes_data.append((date_obj, html_note))
        except Exception as e:
            print(f"❌ File read error :  {note_file}: {e}")
            continue

    try:
        main_window._start_export_flashing()
        content_css_string = get_pdf_theme_css(main_window.settings_manager)

        worker = create_pdf_export_worker(
            options=options,
            notes_data=notes_data,
            content_css_string=content_css_string,
            journal_dir=main_window.journal_directory,
            output_path=pdf_path,
        )
        worker.signals.finished.connect(main_window._on_export_finished)
        worker.signals.error.connect(main_window._on_export_error)

        main_window.thread_pool.start(worker)

        main_window.settings_manager.set(
            "pdf.last_directory", str(Path(pdf_path).parent)
        )
        if options["author"]:
            main_window.settings_manager.set("pdf.last_author", options["author"])
        main_window.settings_manager.set("pdf.last_title", options["title"])
        main_window.settings_manager.save_settings()

    except Exception as e:
        main_window._stop_export_flashing()
        QMessageBox.critical(
            main_window,
            PdfExporterContext.tr("Erreur d'exportation"),
            PdfExporterContext.tr(
                "Une erreur est survenue lors de la création du PDF :\n{error}"
            ).format(error=str(e)),
        )

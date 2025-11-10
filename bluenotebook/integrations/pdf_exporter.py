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
Logique pour l'exportation du journal au format PDF.
"""

from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from pathlib import Path


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
            print(f"⚠️ Erreur de lecture du fichier CSS '{css_path_to_load}': {e}")

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
        author_html = (
            f'<p class="cover-author">Auteur : {pdf_author}</p>' if pdf_author else ""
        )

        # V2.9.2 - Ajouter le tag de filtre sur la page de garde s'il existe
        selected_tag = options.get("selected_tag")
        tag_html = (
            f'<p class="cover-tag">Filtré par tag : <strong>{selected_tag}</strong></p>'
            if selected_tag
            else ""
        )

        cover_page_html = f"""
        <div class="cover-page">
            {image_html}
            <h1>{options.get('title', 'Journal')}</h1>
            {author_html}
            <p class="cover-date">Période du {options['start_date'].toString('d MMMM yyyy')} au {options['end_date'].toString('d MMMM yyyy')}</p>
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
            print(f"⚠️ Fichier CSS par défaut non trouvé : {base_css_path}")
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
        <head><meta charset="UTF-8"><title>{options.get('title', 'Journal')}</title></head>
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
            self.signals.error.emit(
                "La bibliothèque 'WeasyPrint' est requise.\n"
                "Installez-la avec : pip install WeasyPrint"
            )
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

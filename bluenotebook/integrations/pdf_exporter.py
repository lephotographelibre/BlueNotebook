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


class PdfExportWorker(QRunnable):
    """Worker pour générer le PDF en arrière-plan, incluant la préparation du HTML."""

    class Signals(QObject):
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

    def __init__(self, html_string, base_url, css_string, output_path):
        super().__init__()
        # Conserver les anciens paramètres pour la compatibilité si nécessaire,
        # mais ils ne seront plus utilisés par la nouvelle logique.
        self.signals = self.Signals()
        self.html_string = html_string
        self.base_url = base_url
        self.css_string = css_string
        self.output_path = output_path

    @staticmethod
    def _build_html_and_css(options, notes_data):
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

        cover_page_html = f"""
        <div class="cover-page">
            {image_html}
            <h1>{options.get('title', 'Journal')}</h1>
            {author_html}
            <p class="cover-date">Période du {options['start_date'].toString('d MMMM yyyy')} au {options['end_date'].toString('d MMMM yyyy')}</p>
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
        escaped_pdf_title = options.get("title", "").replace('"', '\\"')
        weasyprint_css = f"""
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
            @bottom-center {{
                content: "Page " counter(page) " / " counter(pages);
                font-size: 9pt; color: #666;
            }}
            @bottom-left {{
                content: "{escaped_pdf_title}";
                font-size: 8pt; color: #999;
            }}
            @bottom-right {{
                content: string(current-date);
                font-size: 8pt; color: #999;
            }}
        }}
        body {{ font-family: 'DejaVu Sans', Arial, sans-serif; font-size: 11pt; line-height: 1.6; color: #333; }}
        .cover-page {{ text-align: center; padding-top: 30%; page-break-after: always; }}
        .cover-page h1 {{ font-size: 3em; margin-top: 40px; color: #2c3e50; }}
        .cover-date {{ font-size: 1.2em; margin-top: 20px; color: #7f8c8d; }}
        .cover-author {{ font-size: 1.1em; margin-top: 15px; color: #34495e; }}
        .journal-entry {{ page-break-before: always; }}
        .journal-entry:first-of-type {{ page-break-before: avoid; }}
        .entry-date {{ color: #3498db; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; string-set: current-date content(); }}
        h1, h2, h3, h4, h5, h6 {{ color: #2c3e50; page-break-after: avoid; }}
        pre, code {{ background-color: #f5f5f5; border: 1px solid #ddd; border-radius: 3px; font-size: 9pt; page-break-inside: avoid; }}
        code {{ padding: 2px 4px; font-family: 'DejaVu Sans Mono', monospace; }}
        pre {{ padding: 10px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #3498db; padding-left: 15px; margin-left: 0; color: #555; font-style: italic; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; page-break-inside: avoid; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; font-weight: bold; }}
        img {{ max-width: 100%; height: auto; page-break-inside: avoid; }}
        .tag {{ background-color: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 3px; font-size: 0.9em; }}
        """

        # 4. HTML final
        full_html = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head><meta charset="UTF-8"><title>{options.get('title', 'Journal')}</title></head>
        <body>{all_html_content}</body>
        </html>
        """

        return full_html, weasyprint_css

    def run(self):
        """Exécute la conversion en PDF."""
        try:
            from weasyprint import HTML, CSS

            # La nouvelle logique utilise les options et les données des notes
            # pour construire le HTML et le CSS.
            # Les anciens paramètres (self.html_string, etc.) sont ignorés.
            html_string, css_string = self._build_html_and_css(
                self.html_string, self.css_string
            )

            html_doc = HTML(string=html_string, base_url=self.base_url)
            css_doc = CSS(string=css_string)
            html_doc.write_pdf(self.output_path, stylesheets=[css_doc])
            self.signals.finished.emit(self.output_path)

        except ImportError:
            self.signals.error.emit(
                "La bibliothèque 'WeasyPrint' est requise.\n"
                "Installez-la avec : pip install WeasyPrint"
            )
        except Exception as e:
            self.signals.error.emit(str(e))


# Constructeur mis à jour pour la nouvelle logique
def create_pdf_export_worker(options, notes_data, journal_dir, output_path):
    # Le worker prend maintenant les options et les données des notes.
    # Pour la compatibilité, nous les passons via les anciens paramètres.
    return PdfExportWorker(
        html_string=options,
        css_string=notes_data,
        base_url=str(journal_dir),
        output_path=output_path,
    )

"""
# Copyright (C) 2026 Jean-Marc DIGNE
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

Gestionnaire des liens internes BlueNotebook pour ouvrir les documents
dans les visionneuses appropriées."""

import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from PyQt5.QtCore import QCoreApplication, QUrl, Qt
from PyQt5.QtWidgets import (
    QDialog, QMessageBox, QVBoxLayout, QHBoxLayout, QPushButton
)
from PyQt5.QtWebEngineWidgets import QWebEngineView


class InternalLinksContext:
    """Contexte de traduction pour les liens internes."""

    @staticmethod
    def tr(text):
        return QCoreApplication.translate("InternalLinksContext", text)


def is_internal_link(url_string):
    """
    Détecte si l'URL est un lien interne BlueNotebook.

    Les liens internes pointent vers le dossier 'notes/' du journal.
    Exemple : file:///path/to/journal/notes/document.md

    Args:
        url_string: L'URL à vérifier (str ou QUrl)

    Returns:
        bool: True si c'est un lien interne
    """
    if isinstance(url_string, QUrl):
        url_string = url_string.toString()

    # Vérifier si l'URL contient le dossier 'notes/'
    return '/notes/' in url_string and url_string.startswith('file://')


def get_document_type(file_path):
    """
    Détermine le type de document à partir de son extension.

    Args:
        file_path: Chemin du fichier (str ou Path)

    Returns:
        str: 'markdown', 'pdf', 'image', 'html' ou 'unknown'
    """
    if isinstance(file_path, str):
        file_path = Path(file_path)

    ext = file_path.suffix.lower()

    # Extensions Markdown
    if ext in ['.md', '.markdown']:
        return 'markdown'

    # Extension PDF
    if ext == '.pdf':
        return 'pdf'

    # Extensions d'images
    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
        return 'image'

    # Extensions HTML
    if ext in ['.html', '.htm']:
        return 'html'

    return 'unknown'


def url_to_file_path(url_string):
    """
    Convertit une URL file:// en chemin de fichier local.

    Args:
        url_string: L'URL à convertir (str ou QUrl)

    Returns:
        Path: Le chemin du fichier décodé
    """
    if isinstance(url_string, QUrl):
        url_string = url_string.toString()

    # Parser l'URL
    parsed = urlparse(url_string)

    # Extraire le chemin et décoder les caractères spéciaux
    file_path = unquote(parsed.path)

    # Sur Windows, supprimer le '/' initial si le chemin commence par une lettre de lecteur
    if len(file_path) > 2 and file_path[0] == '/' and file_path[2] == ':':
        file_path = file_path[1:]

    return Path(file_path)


def confirm_open_document(parent, doc_type, file_name):
    """
    Affiche une boîte de dialogue de confirmation avant d'ouvrir un document.

    Args:
        parent: Widget parent pour la boîte de dialogue
        doc_type: Type de document ('markdown', 'pdf', 'image', 'html')
        file_name: Nom du fichier à ouvrir

    Returns:
        bool: True si l'utilisateur confirme l'ouverture
    """
    type_labels = {
        'markdown': InternalLinksContext.tr("le document Markdown"),
        'pdf': InternalLinksContext.tr("le document PDF"),
        'image': InternalLinksContext.tr("l'image"),
        'html': InternalLinksContext.tr("le document HTML")
    }

    action_labels = {
        'markdown': InternalLinksContext.tr("dans l'éditeur Markdown"),
        'pdf': InternalLinksContext.tr("dans le lecteur PDF"),
        'image': InternalLinksContext.tr("dans une fenêtre séparée"),
        'html': InternalLinksContext.tr("dans une fenêtre séparée")
    }

    type_label = type_labels.get(doc_type, InternalLinksContext.tr("le document"))
    action_label = action_labels.get(doc_type, InternalLinksContext.tr("dans une application externe"))

    message_template = InternalLinksContext.tr(
        "Voulez-vous ouvrir {type_label} :\n\n{file_name}\n\n{action_label} ?"
    )
    message = message_template.format(
        type_label=type_label,
        file_name=file_name,
        action_label=action_label
    )

    reply = QMessageBox.question(
        parent,
        InternalLinksContext.tr("Ouvrir un document"),
        message,
        QMessageBox.Yes | QMessageBox.No,
        QMessageBox.Yes
    )

    return reply == QMessageBox.Yes


class DocumentViewerWindow(QDialog):
    """Fenêtre pour afficher les images et documents HTML (COPIÉ de OnlineHelpWindow)."""

    def __init__(self, file_path, doc_type, parent=None):
        """
        Initialise la fenêtre de visualisation.

        Args:
            file_path: Chemin du fichier à afficher (Path)
            doc_type: Type de document ('image' ou 'html')
            parent: Widget parent
        """
        super().__init__(parent)

        # Titre de la fenêtre selon le type
        if doc_type == 'image':
            window_title = InternalLinksContext.tr("Visualiseur d'images")
        else:
            window_title = InternalLinksContext.tr("Visualiseur de documents")

        self.setWindowTitle(window_title)
        self.resize(1200, 800)

        # Permettre de redimensionner et maximiser (COPIÉ de OnlineHelpWindow)
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)

        # Navigateur Web (EXACTEMENT comme OnlineHelpWindow)
        self.web_view = QWebEngineView()

        # Charger le contenu selon le type
        if doc_type == 'image':
            # Pour les images, créer un fichier HTML temporaire
            html_content = self._create_image_html(file_path)
            self.web_view.setHtml(html_content, QUrl.fromLocalFile(str(file_path.parent) + "/"))
        else:
            # Pour les HTML, charger directement
            file_url = QUrl.fromLocalFile(str(file_path))
            self.web_view.setUrl(file_url)

        layout.addWidget(self.web_view)

        # Bouton Fermer en bas à droite (COPIÉ de OnlineHelpWindow)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_button = QPushButton(InternalLinksContext.tr("Fermer"))
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def _create_image_html(self, image_path):
        """Crée le HTML pour afficher une image."""
        image_url = QUrl.fromLocalFile(str(image_path)).toString()
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f0f0;
        }}
        img {{
            max-width: 100%;
            height: auto;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
    </style>
</head>
<body>
    <img src="{image_url}" alt="{image_path.name}">
</body>
</html>"""


def open_markdown_in_editor(main_window, file_path):
    """
    Ouvre un document Markdown dans l'éditeur.

    Args:
        main_window: Instance de MainWindow
        file_path: Chemin du fichier Markdown (Path)
    """
    # Utiliser la méthode existante de MainWindow pour ouvrir un fichier
    main_window.open_specific_file(str(file_path))


def open_pdf_in_viewer(main_window, file_path):
    """
    Ouvre un document PDF dans le lecteur PDF.

    Args:
        main_window: Instance de MainWindow
        file_path: Chemin du fichier PDF (Path)
    """
    # Utiliser le panneau lecteur EPUB/PDF existant
    main_window.epub_reader_panel.load_document(str(file_path))

    # Afficher le panneau s'il n'est pas visible
    if not main_window.epub_reader_panel.isVisible():
        main_window.epub_reader_panel.show()
        main_window._sync_panel_controls()


def open_in_viewer_window(parent, file_path, doc_type):
    """
    Ouvre une image ou un document HTML dans une fenêtre séparée.

    Args:
        parent: Widget parent
        file_path: Chemin du fichier (Path)
        doc_type: Type de document ('image' ou 'html')
    """
    # Stocker la référence dans le parent pour éviter la destruction par le GC
    if not hasattr(parent, '_viewer_windows'):
        parent._viewer_windows = []

    viewer = DocumentViewerWindow(file_path, doc_type, parent)
    parent._viewer_windows.append(viewer)

    # Utiliser show() comme OnlineHelpWindow (PAS exec_() !)
    viewer.show()


def handle_internal_link(url_string, main_window):
    """
    Point d'entrée principal pour gérer un clic sur un lien interne BlueNotebook.

    Args:
        url_string: L'URL du lien cliqué (str ou QUrl)
        main_window: Instance de MainWindow

    Returns:
        bool: True si le lien a été géré, False sinon
    """
    # Vérifier si c'est bien un lien interne
    if not is_internal_link(url_string):
        return False

    # Convertir l'URL en chemin de fichier
    file_path = url_to_file_path(url_string)

    # Vérifier que le fichier existe
    if not file_path.exists():
        error_message = InternalLinksContext.tr(
            "Le fichier n'existe pas :\n\n{file_path}"
        ).format(file_path=str(file_path))

        QMessageBox.warning(
            main_window,
            InternalLinksContext.tr("Fichier introuvable"),
            error_message
        )
        return True

    # Déterminer le type de document
    doc_type = get_document_type(file_path)

    # Si le type est inconnu, afficher un avertissement
    if doc_type == 'unknown':
        warning_message = InternalLinksContext.tr(
            "Type de fichier non pris en charge :\n\n{file_name}"
        ).format(file_name=file_path.name)

        QMessageBox.warning(
            main_window,
            InternalLinksContext.tr("Type non pris en charge"),
            warning_message
        )
        return True

    # Demander confirmation à l'utilisateur
    if not confirm_open_document(main_window, doc_type, file_path.name):
        return True

    # Router vers la fonction appropriée selon le type
    if doc_type == 'markdown':
        open_markdown_in_editor(main_window, file_path)
    elif doc_type == 'pdf':
        open_pdf_in_viewer(main_window, file_path)
    elif doc_type in ['image', 'html']:
        open_in_viewer_window(main_window, file_path, doc_type)

    return True

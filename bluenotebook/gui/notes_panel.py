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
Panneau d'exploration des notes pour BlueNotebook.
"""
import os
import webbrowser
import shutil
import requests
from pathlib import Path

from PyQt5.QtCore import Qt, pyqtSignal, QDir
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QHBoxLayout,
    QLabel,
    QFileSystemModel,
    QMenu,
    QInputDialog,
    QMessageBox,
    QDialog,
)

from .new_note_dialog import NewFileDialog
from .import_file_dialog import ImportFileDialog


class ZoomableTreeView(QTreeView):
    """Une QTreeView qui supporte le zoom avec Ctrl + Molette."""

    def wheelEvent(self, event):
        """Gère l'événement de la molette de la souris pour le zoom."""
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            font = self.font()
            current_size = font.pointSize()

            if delta > 0:
                font.setPointSize(current_size + 1)
            elif current_size > 6:  # Empêche de rendre la police trop petite
                font.setPointSize(current_size - 1)

            self.setFont(font)
        else:
            # Comportement de défilement normal si Ctrl n'est pas pressé
            super().wheelEvent(event)


class ColorableFileSystemModel(QFileSystemModel):
    """
    Un QFileSystemModel qui permet de colorer le fond des dossiers.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_colors = {}

    def set_folder_colors(self, colors_dict):
        """Charge le dictionnaire des couleurs de dossiers."""
        self.folder_colors = colors_dict if colors_dict else {}
        # Force une mise à jour de la vue
        self.layoutChanged.emit()

    def data(self, index, role=Qt.DisplayRole):
        """Retourne les données pour un index et un rôle donnés."""
        if role == Qt.BackgroundRole:
            path = self.filePath(index)
            if path in self.folder_colors:
                return QColor(self.folder_colors[path])
        return super().data(index, role)


class NotesPanel(QWidget):
    """
    Un panneau affichant une vue arborescente du répertoire 'Notes' du journal.
    """

    # Signal émis lorsqu'un fichier doit être ouvert.
    # Le premier argument est le chemin du fichier, le second est le type ('editor', 'reader', 'external')
    file_open_request = pyqtSignal(str, str)
    directory_selected = pyqtSignal(str)
    settings_changed = pyqtSignal()  # Signal pour notifier un changement de settings

    VALID_EXTENSIONS = [
        ".md",
        ".txt",
        ".pdf",
        ".epub",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".mp4",
        ".avi",
        ".mkv",
        ".mp3",
        ".flac",
        ".html",
    ]

    # Palette de 10 couleurs pour les dossiers
    FOLDER_COLOR_PALETTE = [
        ("#ef9a9a", "Rouge clair"),
        ("#a5d6a7", "Vert clair"),
        ("#90caf9", "Bleu clair"),
        ("#fff59d", "Jaune clair"),
        ("#b39ddb", "Violet clair"),
        ("#ffab91", "Orange clair"),
        ("#80cbc4", "Cyan clair"),
        ("#f48fb1", "Rose clair"),
        ("#c5e1a5", "Citron vert"),
        ("#b0bec5", "Gris bleu"),
    ]

    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.journal_directory = None
        self.settings_manager = settings_manager
        self.source_path_for_paste = None
        self.paste_operation = None  # Peut être 'copy' ou 'cut'

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.layout.setSpacing(0)

        # En-tête de panneau (style onglet)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Notes")
        label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa; padding: 8px 12px; font-weight: bold;
                color: #24292e; border: 1px solid #d1d5da; border-bottom: none;
                border-top-left-radius: 6px; border-top-right-radius: 6px;
            }
            """
        )
        header_layout.addWidget(label)
        header_layout.addStretch()
        self.layout.addLayout(header_layout)

        self.tree_view = ZoomableTreeView()
        self.model = ColorableFileSystemModel()

        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        # Filtres pour les types de fichiers à afficher
        self.model.setNameFilters([f"*{ext}" for ext in self.VALID_EXTENSIONS])
        self.model.setNameFilterDisables(
            False
        )  # Afficher les dossiers même s'ils sont vides

        self.tree_view.setModel(self.model)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        # Cacher les colonnes inutiles (taille, type, date)
        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        # Charger les couleurs des dossiers depuis les settings
        if self.settings_manager:
            self.model.set_folder_colors(
                self.settings_manager.get("notes.folder_colors")
            )

        self.layout.addWidget(self.tree_view)

        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )

    def set_journal_directory(self, journal_dir):
        """Définit le répertoire du journal et met à jour la vue."""
        if not journal_dir:
            self.tree_view.setRootIndex(self.model.index(""))
            return

        self.journal_directory = Path(journal_dir)
        notes_dir = self.journal_directory / "notes"
        notes_dir.mkdir(exist_ok=True)

        self.model.setRootPath(str(notes_dir))
        self.tree_view.setRootIndex(self.model.index(self.model.rootPath()))

    def on_item_double_clicked(self, index):
        """Gère le double-clic sur un élément."""
        self.open_selected_item(index)

    def on_selection_changed(self, selected, deselected):
        """Gère le changement de sélection pour sauvegarder le dernier dossier."""
        indexes = selected.indexes()
        if not indexes:
            return

        file_path = self.model.filePath(indexes[0])
        if os.path.isdir(file_path):
            self.directory_selected.emit(file_path)

    def show_context_menu(self, position):
        """Affiche le menu contextuel."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            # Clic dans une zone vide : proposer de créer un dossier à la racine
            menu = QMenu()
            menu.addAction("Créer un dossier...", self.create_root_folder)
            paste_action = menu.addAction("Coller")
            paste_action.setEnabled(self.source_path_for_paste is not None)
            paste_action.triggered.connect(
                lambda: self.paste_item(self.model.rootPath())
            )

            menu.exec_(self.tree_view.viewport().mapToGlobal(position))
            return

        file_path = self.model.filePath(index)
        is_dir = self.model.isDir(index)

        # Clic sur un élément existant
        menu = QMenu()

        if is_dir:
            menu.addAction("Nouvelle note...", lambda: self.create_new_note(file_path))
            menu.addAction(
                "Créer un sous-dossier...", lambda: self.create_sub_folder(file_path)
            )
            menu.addAction(
                "Importer un fichier...", lambda: self.import_file_to_folder(file_path)
            )
            menu.addSeparator()
            # V3.2.1 - Ajout des actions Déplier/Réplier
            menu.addAction("Déplier tout", lambda: self.expand_all_from_index(index))
            menu.addAction("Réplier tout", lambda: self.collapse_all_from_index(index))
            menu.addSeparator()

            # Sous-menu pour les couleurs
            color_menu = menu.addMenu("🎨 Couleur du dossier")
            for color_hex, color_name in self.FOLDER_COLOR_PALETTE:
                action = color_menu.addAction(color_name)
                action.triggered.connect(
                    lambda checked=False, p=file_path, c=color_hex: self.set_folder_color(
                        p, c
                    )
                )

            color_menu.addSeparator()
            color_menu.addAction(
                "Aucune couleur", lambda: self.set_folder_color(file_path, None)
            )
            menu.addSeparator()

        open_action = menu.addAction("Ouvrir")
        open_action.triggered.connect(lambda: self.open_selected_item(index))

        menu.addSeparator()
        menu.addAction("Copier", lambda: self.copy_item(file_path))
        menu.addAction("Couper", lambda: self.cut_item(file_path))

        if is_dir:
            paste_action = menu.addAction("Coller")
            paste_action.setEnabled(self.source_path_for_paste is not None)
            paste_action.triggered.connect(lambda: self.paste_item(file_path))

        menu.addSeparator()
        menu.addAction("Renommer...", lambda: self.rename_item(index))
        menu.addAction("Supprimer...", lambda: self.delete_item(index))

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def open_selected_item(self, index):
        """Ouvre le fichier ou le dossier sélectionné."""
        file_path = self.model.filePath(index)
        if self.model.isDir(index):
            # On pourrait expand/collapse ici, mais le double-clic le fait déjà
            return

        ext = Path(file_path).suffix.lower()
        if ext in [".md", ".txt"]:
            self.file_open_request.emit(file_path, "editor")
        elif ext in [".pdf", ".epub"]:
            self.file_open_request.emit(file_path, "reader")
        else:  # Images, audio, video
            self.file_open_request.emit(file_path, "external")

    def create_new_note(self, directory_path):
        """Crée une nouvelle note Markdown dans le dossier spécifié."""
        dialog = NewFileDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        note_name, ok = QInputDialog.getText(
            self, "Nouvelle Note", "Nom de la note (sans extension) :"
        )
        if not ok or not note_name.strip():
            return

        file_path = Path(directory_path) / f"{note_name.strip()}.md"

        if file_path.exists():
            QMessageBox.warning(
                self, "Fichier existant", "Une note avec ce nom existe déjà."
            )
            return

        try:
            choice, template_name = dialog.get_selection()
            content = ""
            if choice == "template" and template_name:
                base_path = Path(__file__).parent.parent
                template_path = base_path / "resources" / "templates" / template_name
                if template_path.exists():
                    with open(template_path, "r", encoding="utf-8") as f:
                        content = f.read()

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Pas besoin de rafraîchir le modèle, QFileSystemModel le fait
            self.file_open_request.emit(str(file_path), "editor")

        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de créer la note :\n{e}")

    def create_sub_folder(self, parent_directory_path):
        """Crée un nouveau sous-dossier dans le dossier parent spécifié."""
        folder_name, ok = QInputDialog.getText(
            self, "Nouveau Sous-Dossier", "Nom du nouveau sous-dossier :"
        )

        if ok and folder_name.strip():
            new_folder_path = Path(parent_directory_path) / folder_name.strip()

            if new_folder_path.exists():
                QMessageBox.warning(
                    self, "Dossier existant", "Un dossier avec ce nom existe déjà."
                )
                return

            try:
                os.mkdir(new_folder_path)
                # Le QFileSystemModel se mettra à jour automatiquement
            except OSError as e:
                QMessageBox.critical(
                    self, "Erreur", f"Impossible de créer le sous-dossier :\n{e}"
                )

    def set_folder_color(self, folder_path, color_hex):
        """Définit la couleur pour un dossier et sauvegarde dans les settings."""
        if not self.settings_manager:
            return

        folder_colors = self.settings_manager.get("notes.folder_colors", {})
        if color_hex:
            folder_colors[folder_path] = color_hex
        elif folder_path in folder_colors:
            del folder_colors[folder_path]

        self.settings_manager.set("notes.folder_colors", folder_colors)
        self.settings_manager.save_settings()  # Sauvegarde immédiate
        self.model.set_folder_colors(folder_colors)

    def import_file_to_folder(self, destination_folder):
        """Ouvre une boîte de dialogue pour importer un fichier local ou distant."""
        dialog = ImportFileDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        source_path = dialog.get_path()
        if not source_path:
            return

        # Validation de l'extension
        file_extension = Path(source_path).suffix.lower()
        if file_extension not in self.VALID_EXTENSIONS:
            supported_types = ", ".join(self.VALID_EXTENSIONS)
            QMessageBox.warning(
                self,
                "Type de fichier non supporté",
                "Le fichier que vous voulez importer n'est pas supporté dans les notes.\n"
                f"Les types valides sont uniquement : {supported_types}",
            )
            return

        # Copie/Téléchargement
        try:
            is_remote = source_path.lower().startswith(("http://", "https://"))
            filename = Path(source_path).name
            destination_path = Path(destination_folder) / filename

            if destination_path.exists():
                reply = QMessageBox.question(
                    self,
                    "Fichier existant",
                    f"Le fichier '{filename}' existe déjà dans ce dossier. Voulez-vous le remplacer ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

            if is_remote:
                response = requests.get(source_path, stream=True, timeout=10)
                response.raise_for_status()  # Lève une exception pour les codes d'erreur HTTP
                with open(destination_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:  # Fichier local
                if not Path(source_path).is_file():
                    raise FileNotFoundError(
                        "Le chemin local spécifié n'est pas un fichier."
                    )
                shutil.copy2(source_path, destination_path)

            # Le QFileSystemModel se mettra à jour automatiquement.

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur d'importation", f"Impossible d'importer le fichier :\n{e}"
            )

    def copy_item(self, path):
        """Met le chemin en mémoire pour une opération de copie."""
        self.source_path_for_paste = path
        self.paste_operation = "copy"
        print(f"Prêt à copier : {path}")

    def cut_item(self, path):
        """Met le chemin en mémoire pour une opération de coupe."""
        self.source_path_for_paste = path
        self.paste_operation = "cut"
        print(f"Prêt à couper : {path}")

    def paste_item(self, destination_folder):
        """Colle le fichier/dossier en mémoire dans le dossier de destination."""
        if not self.source_path_for_paste or not self.paste_operation:
            return

        source_path = Path(self.source_path_for_paste)
        dest_path = Path(destination_folder) / source_path.name

        if str(dest_path).startswith(str(source_path)):
            QMessageBox.warning(
                self,
                "Opération impossible",
                "Vous ne pouvez pas coller un dossier dans lui-même.",
            )
            return

        if dest_path.exists():
            reply = QMessageBox.question(
                self,
                "Conflit",
                f"Un élément nommé '{source_path.name}' existe déjà. Voulez-vous le remplacer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return
            # Supprimer l'élément existant avant de coller/déplacer
            try:
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            except OSError as e:
                QMessageBox.critical(
                    self, "Erreur", f"Impossible de remplacer l'élément existant :\n{e}"
                )
                return

        try:
            if self.paste_operation == "copy":
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
            elif self.paste_operation == "cut":
                shutil.move(str(source_path), str(dest_path))
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur de collage", f"L'opération a échoué :\n{e}"
            )
        finally:
            # Réinitialiser le presse-papiers après l'opération
            self.source_path_for_paste = None
            self.paste_operation = None

    def create_root_folder(self):
        """Crée un nouveau dossier à la racine du répertoire des notes."""
        if not self.journal_directory:
            QMessageBox.warning(
                self, "Action impossible", "Le répertoire du journal n'est pas défini."
            )
            return

        folder_name, ok = QInputDialog.getText(
            self, "Nouveau Dossier", "Nom du nouveau dossier :"
        )

        if ok and folder_name.strip():
            notes_root_path = self.model.rootPath()
            new_folder_path = Path(notes_root_path) / folder_name.strip()

            if new_folder_path.exists():
                QMessageBox.warning(
                    self, "Dossier existant", "Un dossier avec ce nom existe déjà."
                )
                return

            try:
                os.mkdir(new_folder_path)
            except OSError as e:
                QMessageBox.critical(
                    self, "Erreur", f"Impossible de créer le dossier :\n{e}"
                )

    def rename_item(self, index):
        """Renomme un fichier ou un dossier."""
        old_path = self.model.filePath(index)
        old_name = self.model.fileName(index)

        new_name, ok = QInputDialog.getText(
            self, "Renommer", "Nouveau nom :", text=old_name
        )
        if not ok or not new_name.strip() or new_name == old_name:
            return

        new_path = str(Path(old_path).parent / new_name.strip())

        try:
            os.rename(old_path, new_path)
        except OSError as e:
            QMessageBox.critical(self, "Erreur", f"Impossible de renommer :\n{e}")

    def delete_item(self, index):
        """Supprime un fichier ou un dossier."""
        file_path = self.model.filePath(index)
        is_dir = self.model.isDir(index)
        item_name = Path(file_path).name

        if is_dir:
            # Logique pour les dossiers
            sub_folders, files = self._count_folder_contents(file_path)
            if sub_folders == 0 and files == 0:
                # Dossier vide
                question = (
                    f"Le dossier '{item_name}' est vide. Voulez-vous le supprimer ?"
                )
            else:
                # Dossier non vide
                question = (
                    f"Le dossier '{item_name}' n'est pas vide.\n"
                    f"Il contient {sub_folders} sous-dossier(s) et {files} fichier(s).\n\n"
                    "Voulez-vous tout supprimer ?"
                )
            reply = QMessageBox.question(
                self,
                "Confirmation de suppression",
                question,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        else:
            # Logique pour les fichiers
            reply = QMessageBox.question(
                self,
                "Confirmation de suppression",
                f"Êtes-vous sûr de vouloir supprimer le fichier '{item_name}' ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

        if reply == QMessageBox.Yes:
            try:
                if is_dir:
                    # QFileSystemModel.rmdir() ne supprime que les dossiers vides.
                    # Pour une suppression récursive, il faut utiliser shutil.rmtree().
                    # Le modèle se mettra à jour automatiquement car il surveille le système de fichiers.
                    shutil.rmtree(file_path)
                else:
                    # Pour les fichiers, model.remove() est correct.
                    self.model.remove(index)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de supprimer :\n{e}")

    def _count_folder_contents(self, folder_path):
        """Compte le nombre de sous-dossiers et de fichiers dans un dossier."""
        total_folders = 0
        total_files = 0
        # os.walk parcourt récursivement toute l'arborescence
        for dirpath, dirnames, filenames in os.walk(folder_path):
            total_folders += len(dirnames)
            total_files += len(filenames)

        return total_folders, total_files

    def select_path(self, path):
        """Sélectionne un chemin dans l'arbre."""
        if not path:
            return
        index = self.model.index(path)
        if index.isValid():
            self.tree_view.setCurrentIndex(index)
            self.tree_view.scrollTo(index, QTreeView.PositionAtCenter)

    def expand_all_from_index(self, index):
        """Déplie récursivement tous les sous-dossiers à partir d'un index."""
        if not index.isValid() or not self.model.isDir(index):
            return

        self.tree_view.expand(index)
        for i in range(self.model.rowCount(index)):
            child_index = self.model.index(i, 0, index)
            self.expand_all_from_index(child_index)

    def collapse_all_from_index(self, index):
        """Réplie récursivement tous les sous-dossiers à partir d'un index."""
        if not index.isValid() or not self.model.isDir(index):
            return

        for i in range(self.model.rowCount(index)):
            child_index = self.model.index(i, 0, index)
            self.collapse_all_from_index(child_index)
        self.tree_view.collapse(index)

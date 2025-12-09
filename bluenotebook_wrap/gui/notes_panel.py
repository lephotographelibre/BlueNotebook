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
import shutil
from pathlib import Path

import requests
from PyQt5.QtCore import Qt, pyqtSignal, QDir, QSortFilterProxyModel
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTreeView,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QFileSystemModel,
    QMenu,
    QInputDialog,
    QMessageBox,
    QDialog,
    QSplitter,
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
            elif current_size > 6:
                font.setPointSize(current_size - 1)

            self.setFont(font)
        else:
            super().wheelEvent(event)


class ColorableFileSystemModel(QFileSystemModel):
    """Un QFileSystemModel qui permet de colorer le fond des dossiers."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.folder_colors = {}

    def set_folder_colors(self, colors_dict):
        """Charge le dictionnaire des couleurs de dossiers."""
        self.folder_colors = colors_dict if colors_dict else {}
        top_left = self.index(0, 0)
        bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right, [Qt.BackgroundRole])

    def data(self, index, role=Qt.DisplayRole):
        """Retourne les données pour un index et un rôle donnés."""
        if role == Qt.BackgroundRole:
            path = self.filePath(index)
            if path in self.folder_colors:
                return QColor(self.folder_colors[path])
        return super().data(index, role)


class NotesFilterProxyModel(QSortFilterProxyModel):
    """Custom proxy model to include matching files and directories with their parents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_text = self.tr("")
        self.expanded_dirs = set()
        self.matching_paths = set()  # Cache matching paths during search
        self.valid_extensions = {ext.lower() for ext in NotesPanel.VALID_EXTENSIONS}

    def set_search_text(self, search_text):
        """Set the search text, clear previous state, update matching paths, and invalidate the filter."""
        # print(
        #    self.tr("Setting search text: '%1', clearing expanded_dirs: %2").arg(search_text).arg(self.expanded_dirs)
        # )
        self.search_text = search_text.lower()
        self.expanded_dirs.clear()  # Clear expanded directories for new search
        self.matching_paths.clear()
        if self.search_text:
            # Populate matching_paths with files and directories that match the search
            root_path = self.sourceModel().rootPath() if self.sourceModel() else self.tr("")
            for dirpath, dirnames, filenames in os.walk(root_path):
                for dirname in dirnames:
                    if self.search_text in dirname.lower():
                        self.matching_paths.add(os.path.join(dirpath, dirname))
                for filename in filenames:
                    if self.search_text in filename.lower():
                        self.matching_paths.add(os.path.join(dirpath, filename))
            # print(self.tr("Matching paths: %1").arg(self.matching_paths))
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row, source_parent):
        """Accept rows that match the search text, are parents of matches, or are valid children of matching expanded dirs."""
        source_model = self.sourceModel()
        index = source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        file_path = source_model.filePath(index)
        file_name = source_model.fileName(index).lower()
        is_dir = source_model.isDir(index)

        # Debug: Log filtering decision
        # print(self.tr("Filter checking: %1, Search: %2").arg(file_path).arg(self.search_text))

        # If no search text, show all items (initial view)
        if not self.search_text:
            # print(self.tr("Accepted: %1 (no search)").arg(file_path))
            return True

        # Accept if the file or directory name contains the search text
        if self.search_text in file_name:
            # print(self.tr("Accepted: %1 (direct match)").arg(file_path))
            return True

        # Accept directories that are parents of matching items
        if is_dir:
            for path in self.matching_paths:
                if path.startswith(file_path + os.sep):
                    # print(self.tr("Accepted: %1 (parent of match %2)").arg(file_path).arg(path))
                    return True

        # During a search, if the parent is an expanded directory that matches or is a parent of a match,
        # handle children based on whether the parent matches the search text
        if source_model.isDir(source_parent):
            parent_path = source_model.filePath(source_parent)
            if parent_path in self.expanded_dirs:
                parent_name = source_model.fileName(source_parent).lower()
                is_parent_matching = self.search_text in parent_name
                is_parent_of_match = any(
                    path.startswith(parent_path + os.sep)
                    for path in self.matching_paths
                )
                if is_parent_matching:
                    # If the parent matches (e.g., 'docs' for search 'docs'), accept all valid children
                    if (
                        is_dir
                        or Path(file_path).suffix.lower() in self.valid_extensions
                    ):
                        # print(
                        #    self.tr("Accepted: %1 (child of expanded matching %2, parent matches)").arg(file_path).arg(parent_path)
                        # )
                        return True
                    # print(
                    #    self.tr("Rejected: %1 (child of expanded matching %2, invalid extension)").arg(file_path).arg(parent_path)
                    # )
                    return False
                elif is_parent_of_match:
                    # If the parent is a parent of a match, accept children that match or are parents of matches
                    if self.search_text in file_name:
                        # print(
                        #    self.tr("Accepted: %1 (child of expanded %2, direct match)").arg(file_path).arg(parent_path)
                        # )
                        return True
                    if is_dir:
                        for path in self.matching_paths:
                            if path.startswith(file_path + os.sep):
                                # print(
                                #    self.tr("Accepted: %1 (child of expanded %2, parent of match %3)").arg(file_path).arg(parent_path).arg(path)
                                # )
                                return True
                    # print(
                    #    self.tr("Rejected: %1 (child of expanded %2, no match)").arg(file_path).arg(parent_path)
                    # )
                    return False
                else:
                    # print(
                    #    self.tr("Rejected: %1 (child of expanded %2, parent not matching)").arg(file_path).arg(parent_path)
                    # )
                    return False

        # print(self.tr("Rejected: %1").arg(file_path))
        return False

    def add_expanded_dir(self, path):
        """Add a directory to the set of expanded directories."""
        # print(self.tr("Adding expanded dir: %1").arg(path))
        self.expanded_dirs.add(path)
        self.invalidateFilter()

    def remove_expanded_dir(self, path):
        """Remove a directory from the set of expanded directories."""
        # print(self.tr("Removing expanded dir: %1").arg(path))
        self.expanded_dirs.discard(path)
        self.invalidateFilter()

    def hasChildren(self, index):
        """Indicate if a directory has children in the proxy model, considering search filter."""
        if not index.isValid():
            return super().hasChildren(index)

        source_index = self.mapToSource(index)
        source_model = self.sourceModel()
        if not source_model.isDir(source_index):
            return super().hasChildren(index)

        file_path = source_model.filePath(source_index)
        # Check if the directory has any children that would pass the filter
        for row in range(source_model.rowCount(source_index)):
            child_index = source_model.index(row, 0, source_index)
            child_path = source_model.filePath(child_index)
            if self.filterAcceptsRow(row, source_index):
                # print(self.tr("Has children: %1 (child %2 accepted)").arg(file_path).arg(child_path))
                return True
            else:
                # print(self.tr("Child rejected: %1 for parent %2").arg(child_path).arg(file_path))
                pass

        # print(self.tr("No children: %1 (no filtered children)").arg(file_path))
        return False

    def canFetchMore(self, index):
        """Allow fetching more children for directories."""
        if not index.isValid():
            return False
        source_index = self.mapToSource(index)
        return self.sourceModel().canFetchMore(source_index)

    def fetchMore(self, index):
        """Fetch more children for directories."""
        if index.isValid():
            source_index = self.mapToSource(index)
            self.sourceModel().fetchMore(source_index)


class NotesPanel(QWidget):
    """Un panneau affichant une vue arborescente du répertoire 'Notes' du journal."""

    file_open_request = pyqtSignal(str, str)
    directory_selected = pyqtSignal(str)
    settings_changed = pyqtSignal()

    VALID_EXTENSIONS = [
        ".md",
        self.tr(".txt"),
        self.tr(".pdf"),
        self.tr(".epub"),
        self.tr(".jpg"),
        self.tr(".jpeg"),
        self.tr(".png"),
        self.tr(".gif"),
        self.tr(".mp4"),
        self.tr(".avi"),
        self.tr(".mkv"),
        self.tr(".mp3"),
        self.tr(".flac"),
        ".html",
    ]

    FOLDER_COLOR_PALETTE = [
        (self.tr("#ef9a9a"), self.tr("Rouge clair")),
        (self.tr("#a5d6a7"), self.tr("Vert clair")),
        (self.tr("#90caf9"), self.tr("Bleu clair")),
        (self.tr("#fff59d"), self.tr("Jaune clair")),
        (self.tr("#b39ddb"), self.tr("Violet clair")),
        (self.tr("#ffab91"), self.tr("Orange clair")),
        (self.tr("#80cbc4"), self.tr("Cyan clair")),
        (self.tr("#f48fb1"), self.tr("Rose clair")),
        (self.tr("#c5e1a5"), self.tr("Citron vert")),
        (self.tr("#b0bec5"), self.tr("Gris bleu")),
    ]

    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.journal_directory = None
        self.settings_manager = settings_manager
        self.source_path_for_paste = None
        self.paste_operation = None

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 5, 0, 0)
        self.layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(self.tr("Notes"))
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

        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(5, 5, 5, 5)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(self.tr("Rechercher nom de fichier"))
        self.search_input.setClearButtonEnabled(True)
        search_layout.addWidget(self.search_input)

        search_button = QPushButton(self.tr("Rechercher"))
        search_layout.addWidget(search_button)
        self.layout.addLayout(search_layout)

        self.tree_view = ZoomableTreeView()
        self.model = ColorableFileSystemModel()

        self.model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        self.model.setNameFilters([self.tr("*%1").arg(ext) for ext in self.VALID_EXTENSIONS])
        self.model.setNameFilterDisables(False)

        self.proxy_model = NotesFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setRecursiveFilteringEnabled(True)
        self.tree_view.setModel(self.proxy_model)

        self.tree_view.setSortingEnabled(True)
        self.tree_view.sortByColumn(0, Qt.AscendingOrder)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

        for i in range(1, self.model.columnCount()):
            self.tree_view.hideColumn(i)

        if self.settings_manager:
            self.model.set_folder_colors(
                self.settings_manager.get(self.tr("notes.folder_colors"))
            )

        self.layout.addWidget(self.tree_view)

        self.tree_view.doubleClicked.connect(self.on_item_double_clicked)
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_selection_changed
        )
        self.tree_view.expanded.connect(self.on_directory_expanded)
        self.tree_view.collapsed.connect(self.on_directory_collapsed)

        search_button.clicked.connect(self.perform_search)
        self.search_input.textChanged.connect(self.on_search_text_changed)
        self.search_input.returnPressed.connect(self.perform_search)

    def toggle_details_columns(self):
        """Affiche ou masque les colonnes de détails (taille, type, date).
        Quand on les affiche : double la largeur du panneau et force la colonne Nom à ≥ 250px.
        Version ultra-stable – ne plante jamais."""
        currently_hidden = self.tree_view.isColumnHidden(1)  # Colonne 1 = Taille

        # ===================================================================
        # 1. Trouver le QSplitter qui contient réellement le NotesPanel
        # ===================================================================
        splitter = self.parent()
        while splitter and not isinstance(splitter, QSplitter):
            splitter = splitter.parent()
        # Si on ne trouve pas de splitter → on abandonne la partie redimensionnement (pas de crash)
        has_splitter = splitter is not None

        if currently_hidden:
            # ─── ACTIVATION du mode détails ───
            for i in range(1, self.model.columnCount()):
                self.tree_view.showColumn(i)

            # Colonne Nom bien large
            if self.tree_view.columnWidth(0) < 250:
                self.tree_view.setColumnWidth(0, 280)

            # Redimensionner les autres colonnes proprement
            self.tree_view.resizeColumnToContents(1)
            self.tree_view.resizeColumnToContents(2)
            self.tree_view.resizeColumnToContents(3)

            # Doubler la largeur du panneau (seulement si on a un splitter)
            if has_splitter:
                sizes = splitter.sizes()
                if len(sizes) > 1:
                    idx = splitter.indexOf(self)
                    if idx != -1 and sizes[idx] > 0:
                        total = sum(s for s in sizes if s > 0)
                        # On veut ~50–60 % de l’espace total quand les détails sont affichés
                        target = int(total * 0.55)
                        sizes[idx] = max(target, sizes[idx] * 2)  # au moins le double
                        # Réduire les autres panneaux proportionnellement
                        remaining = sum(s for i, s in enumerate(sizes) if i != idx)
                        if remaining > 0:
                            factor = (total - sizes[idx]) / remaining
                            for i in range(len(sizes)):
                                if i != idx and sizes[i] > 0:
                                    sizes[i] = max(
                                        50, int(sizes[i] * factor)
                                    )  # garde un minimum
                        splitter.setSizes(sizes)

        else:
            # ─── DÉSACTIVATION du mode détails → retour compact ───
            for i in range(1, self.model.columnCount()):
                self.tree_view.hideColumn(i)

            # Réduire la colonne Nom (mais garder lisible)
            current = self.tree_view.columnWidth(0)
            if current > 300:
                self.tree_view.setColumnWidth(0, 200)

            # Revenir à une largeur compacte (~20–25 % de l’écran)
            if has_splitter:
                sizes = splitter.sizes()
                if len(sizes) > 1:
                    idx = splitter.indexOf(self)
                    if idx != -1:
                        total = sum(s for s in sizes if s > 0)
                        compact = max(180, int(total * 0.22))  # jamais trop petit
                        sizes[idx] = compact
                        # Redistribuer l’espace libéré
                        remaining = total - compact
                        other_count = len(
                            [s for i, s in enumerate(sizes) if i != idx and s > 0]
                        )
                        if other_count > 0:
                            per_other = remaining // other_count
                            for i in range(len(sizes)):
                                if i != idx and sizes[i] > 0:
                                    sizes[i] = per_other
                        splitter.setSizes(sizes)

    def set_journal_directory(self, journal_dir):
        """Définit le répertoire du journal et met à jour la vue."""
        if not journal_dir:
            self.tree_view.setRootIndex(
                self.proxy_model.mapFromSource(self.model.index(self.tr("")))
            )
            return

        self.journal_directory = Path(journal_dir)
        notes_dir = self.journal_directory / self.tr("notes")
        notes_dir.mkdir(exist_ok=True)

        self.model.setRootPath(str(notes_dir))
        root_index = self.model.index(self.model.rootPath())
        self.tree_view.setRootIndex(self.proxy_model.mapFromSource(root_index))

    def perform_search(self):
        """Effectue une recherche et affiche les résultats."""
        search_text = self.search_input.text().strip()
        if not search_text:
            self.reset_search()
            return

        self.proxy_model.set_search_text(search_text)
        root_index = self.model.index(self.model.rootPath())
        proxy_root_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root_index)

        matching_files = self._find_matching_items(search_text)
        # if matching_files:
        #    print("Fichiers correspondants à la recherche :")
        #    for file_path in matching_files:
        #        print(file_path)
        # else:
        #    print("Aucun fichier correspondant trouvé.")

        self._expand_matching_directories(matching_files)

    def on_search_text_changed(self, text):
        """Réinitialise la vue si le champ de recherche est vidé."""
        if not text.strip():
            self.reset_search()

    def reset_search(self):
        """Réinitialise la vue pour afficher l'arbre complet."""
        self.proxy_model.set_search_text(self.tr(""))
        root_index = self.model.index(self.model.rootPath())
        proxy_root_index = self.proxy_model.mapFromSource(root_index)
        self.tree_view.setRootIndex(proxy_root_index)
        self.tree_view.collapseAll()
        self.tree_view.viewport().update()

    def _find_matching_items(self, search_text):
        """Trouve tous les fichiers et dossiers correspondant au critère de recherche."""
        matching_files = []
        root_path = self.model.rootPath()
        search_text = search_text.lower()

        for dirpath, dirnames, filenames in os.walk(root_path):
            for dirname in dirnames:
                if search_text in dirname.lower():
                    matching_files.append(os.path.join(dirpath, dirname))
            for filename in filenames:
                if search_text in filename.lower():
                    matching_files.append(os.path.join(dirpath, filename))

        return matching_files

    def _expand_matching_directories(self, matching_files):
        """Déplie les répertoires parents pour rendre les fichiers ou dossiers correspondants visibles."""
        for file_path in matching_files:
            current_path = Path(file_path)
            # Expand parent directories
            parent_path = current_path.parent
            while str(parent_path) != self.model.rootPath():
                index = self.model.index(str(parent_path))
                if index.isValid():
                    proxy_index = self.proxy_model.mapFromSource(index)
                    if proxy_index.isValid():
                        self.tree_view.expand(proxy_index)
                        self.proxy_model.add_expanded_dir(str(parent_path))
                        self.tree_view.scrollTo(proxy_index, QTreeView.PositionAtCenter)
                        # print(self.tr("Expanded parent directory: %1").arg(parent_path))
                    else:
                        # print(self.tr("Invalid proxy index for: %1").arg(parent_path))
                        pass
                else:
                    # print(self.tr("Invalid source index for: %1").arg(parent_path))
                    pass
                parent_path = parent_path.parent

            # Ensure the matching item is visible; no need to expand if it's a file
            index = self.model.index(str(current_path))
            if index.isValid():
                proxy_index = self.proxy_model.mapFromSource(index)
                if proxy_index.isValid():
                    self.tree_view.scrollTo(proxy_index, QTreeView.PositionAtCenter)
                    if self.model.isDir(index):
                        self.tree_view.collapse(proxy_index)
                        # print(self.tr("Ensured visible (collapsed): %1").arg(current_path))
                    else:
                        # print(self.tr("Ensured visible (file): %1").arg(current_path))
                        pass
                else:
                    # print(self.tr("Invalid proxy index for matching item: %1").arg(current_path))
                    pass
            else:
                # print(self.tr("Invalid source index for matching item: %1").arg(current_path))
                pass

    def on_item_double_clicked(self, proxy_index):
        """Gère le double-clic sur un élément."""
        if not proxy_index.isValid():
            # print("Double-clicked on invalid proxy index")
            return

        index = self.proxy_model.mapToSource(proxy_index)
        if not index.isValid():
            # print("Invalid source index for proxy index")
            return

        file_path = self.model.filePath(index)
        # print(self.tr("Double-clicked: %1, is_dir: %2").arg(file_path).arg(self.model.isDir(index)))

        if self.model.isDir(index):
            if self.tree_view.isExpanded(proxy_index):
                # print(self.tr("Collapsing directory: %1").arg(file_path))
                self.tree_view.collapse(proxy_index)
                self.proxy_model.remove_expanded_dir(file_path)
            else:
                # print(self.tr("Expanding directory: %1").arg(file_path))
                self.tree_view.expand(proxy_index)
                self.proxy_model.add_expanded_dir(file_path)
            return

        self.open_selected_item(index)

    def on_directory_expanded(self, proxy_index):
        """Handle directory expansion."""
        if not proxy_index.isValid():
            # print("Expanded invalid proxy index")
            return
        index = self.proxy_model.mapToSource(proxy_index)
        if not index.isValid():
            # print("Invalid source index for expanded proxy index")
            return
        file_path = self.model.filePath(index)
        # print(self.tr("Directory expanded: %1").arg(file_path))
        self.proxy_model.add_expanded_dir(file_path)

    def on_directory_collapsed(self, proxy_index):
        """Handle directory collapse."""
        if not proxy_index.isValid():
            # print("Collapsed invalid proxy index")
            return
        index = self.proxy_model.mapToSource(proxy_index)
        if not index.isValid():
            # print("Invalid source index for collapsed proxy index")
            return
        file_path = self.model.filePath(index)
        # print(self.tr("Directory collapsed: %1").arg(file_path))
        self.proxy_model.remove_expanded_dir(file_path)

    def on_selection_changed(self, selected, deselected):
        """Gère le changement de sélection pour sauvegarder le dernier dossier."""
        indexes = selected.indexes()
        if not indexes:
            return
        source_index = self.proxy_model.mapToSource(indexes[0])
        file_path = self.model.filePath(source_index)
        if os.path.isdir(file_path):
            self.directory_selected.emit(file_path)

    def show_context_menu(self, position):
        """Affiche le menu contextuel."""
        index = self.tree_view.indexAt(position)
        if not index.isValid():
            menu = QMenu()
            menu.addAction(self.tr("Créer un dossier..."), self.create_root_folder)
            paste_action = menu.addAction(self.tr("Coller"))
            paste_action.setEnabled(self.source_path_for_paste is not None)
            paste_action.triggered.connect(
                lambda: self.paste_item(self.model.rootPath())
            )
            menu.exec_(self.tree_view.viewport().mapToGlobal(position))
            return

        source_index = self.proxy_model.mapToSource(index)
        file_path = self.model.filePath(source_index)
        is_dir = self.model.isDir(source_index)

        menu = QMenu()

        if is_dir:
            menu.addAction(self.tr("Nouvelle note..."), lambda: self.create_new_note(file_path))
            menu.addAction(
                self.tr("Créer un sous-dossier..."), lambda: self.create_sub_folder(file_path)
            )
            menu.addAction(
                self.tr("Importer un fichier..."), lambda: self.import_file_to_folder(file_path)
            )
            menu.addSeparator()
            menu.addAction(
                self.tr("Déplier tout"), lambda: self.expand_all_from_index(source_index)
            )
            menu.addAction(
                self.tr("Réplier tout"), lambda: self.collapse_all_from_index(source_index)
            )
            menu.addSeparator()

            color_menu = menu.addMenu(self.tr("🎨 Couleur du dossier"))
            for color_hex, color_name in self.FOLDER_COLOR_PALETTE:
                action = color_menu.addAction(color_name)
                action.triggered.connect(
                    lambda checked=False, p=file_path, c=color_hex: self.set_folder_color(
                        p, c
                    )
                )
            color_menu.addSeparator()
            menu.addAction(
                self.tr("Aucune couleur"), lambda: self.set_folder_color(file_path, None)
            )
            menu.addSeparator()

        open_action = menu.addAction(self.tr("Ouvrir"))
        open_action.triggered.connect(lambda: self.open_selected_item(source_index))

        menu.addSeparator()
        menu.addAction(self.tr("Copier"), lambda: self.copy_item(file_path))
        menu.addAction(self.tr("Couper"), lambda: self.cut_item(file_path))

        if is_dir:
            paste_action = menu.addAction(self.tr("Coller"))
            paste_action.setEnabled(self.source_path_for_paste is not None)
            paste_action.triggered.connect(lambda: self.paste_item(file_path))

        menu.addSeparator()
        menu.addAction(self.tr("Renommer..."), lambda: self.rename_item(source_index))
        menu.addAction(self.tr("Supprimer..."), lambda: self.delete_item(source_index))

        menu.exec_(self.tree_view.viewport().mapToGlobal(position))

    def open_selected_item(self, index):
        """Ouvre le fichier ou le dossier sélectionné."""
        file_path = self.model.filePath(index)
        if self.model.isDir(index):
            return

        ext = Path(file_path).suffix.lower()
        if ext in [".md", ".txt", ".html"]:
            self.file_open_request.emit(file_path, self.tr("editor"))
        elif ext in [self.tr(".pdf"), self.tr(".epub")]:
            self.file_open_request.emit(file_path, self.tr("reader"))
        else:
            self.file_open_request.emit(file_path, self.tr("external"))

    def create_new_note(self, directory_path):
        """Crée une nouvelle note Markdown dans le dossier spécifié."""
        dialog = NewFileDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        note_name, ok = QInputDialog.getText(
            self, self.tr("Nouvelle Note"), self.tr("Nom de la note (sans extension) :")
        )
        if not ok or not note_name.strip():
            return

        file_path = Path(directory_path) / self.tr("%1.md").arg(note_name.strip())

        if file_path.exists():
            QMessageBox.warning(
                self, self.tr("Fichier existant"), self.tr("Une note avec ce nom existe déjà.")
            )
            return

        try:
            choice, template_name = dialog.get_selection()
            content = self.tr("")
            if choice == self.tr("template") and template_name:
                base_path = Path(__file__).parent.parent
                template_path = base_path / self.tr("resources") / self.tr("templates") / template_name
                if template_path.exists():
                    with open(template_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # --- V3.3.3 - Ajout de la substitution des placeholders ---
                    # Cette logique manquait pour la création de notes depuis le panneau.
                    try:
                        import locale
                        from datetime import datetime

                        locale.setlocale(locale.LC_TIME, self.tr("fr_FR.UTF-8"))
                    except locale.Error:
                        locale.setlocale(locale.LC_TIME, self.tr(""))

                    today_str = datetime.now().strftime("%A %d %B %Y").title()
                    timestamp_str = datetime.now().strftime("%H:%M")

                    content = content.replace(self.tr("{{date}}"), today_str)
                    content = content.replace(self.tr("{{horodatage}}"), timestamp_str)
                    # --- Fin de l'ajout ---

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            self.file_open_request.emit(str(file_path), self.tr("editor"))

        except Exception as e:
            QMessageBox.critical(self, self.tr("Erreur"), self.tr("Impossible de créer la note :\n%1").arg(e))

    def create_sub_folder(self, parent_directory_path):
        """Crée un nouveau sous-dossier dans le dossier parent spécifié."""
        folder_name, ok = QInputDialog.getText(
            self, self.tr("Nouveau Sous-Dossier"), self.tr("Nom du nouveau sous-dossier :")
        )

        if ok and folder_name.strip():
            new_folder_path = Path(parent_directory_path) / folder_name.strip()

            if new_folder_path.exists():
                QMessageBox.warning(
                    self, self.tr("Dossier existant"), self.tr("Un dossier avec ce nom existe déjà.")
                )
                return

            try:
                os.mkdir(new_folder_path)
            except OSError as e:
                QMessageBox.critical(
                    self, self.tr("Erreur"), self.tr("Impossible de créer le sous-dossier :\n%1").arg(e)
                )

    def set_folder_color(self, folder_path, color_hex):
        """Définit la couleur pour un dossier et sauvegarde dans les settings."""
        if not self.settings_manager:
            return

        folder_colors = self.settings_manager.get(self.tr("notes.folder_colors"), {})
        if color_hex:
            folder_colors[folder_path] = color_hex
        elif folder_path in folder_colors:
            del folder_colors[folder_path]

        self.settings_manager.set(self.tr("notes.folder_colors"), folder_colors)
        self.settings_manager.save_settings()
        self.model.set_folder_colors(folder_colors)

    def import_file_to_folder(self, destination_folder):
        """Ouvre une boîte de dialogue pour importer un fichier local ou distant."""
        dialog = ImportFileDialog(self)
        if dialog.exec_() != QDialog.Accepted:
            return

        source_path = dialog.get_path()
        if not source_path:
            return

        file_extension = Path(source_path).suffix.lower()
        if file_extension not in self.VALID_EXTENSIONS:
            supported_types = self.tr(", ").join(self.VALID_EXTENSIONS)
            QMessageBox.warning(
                self,
                self.tr("Type de fichier non supporté"),
                self.tr("Le fichier que vous voulez importer n'est pas supporté dans les notes."),
                self.tr("Les types valides sont uniquement : %1").arg(supported_types),
            )
            return

        try:
            is_remote = source_path.lower().startswith(("http://", "https://"))
            filename = Path(source_path).name
            destination_path = Path(destination_folder) / filename

            if destination_path.exists():
                reply = QMessageBox.question(
                    self,
                    self.tr("Fichier existant"),
                    self.tr("Le fichier '%1' existe déjà dans ce dossier. Voulez-vous le remplacer ?").arg(filename),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if reply == QMessageBox.No:
                    return

            if is_remote:
                response = requests.get(source_path, stream=True, timeout=10)
                response.raise_for_status()
                with open(destination_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            else:
                if not Path(source_path).is_file():
                    raise FileNotFoundError(
                        self.tr("Le chemin local spécifié n'est pas un fichier.")
                    )
                shutil.copy2(source_path, destination_path)

        except Exception as e:
            QMessageBox.critical(
                self, self.tr("Erreur d'importation"), self.tr("Impossible d'importer le fichier :\n%1").arg(e)
            )

    def copy_item(self, path):
        """Met le chemin en mémoire pour une opération de copie."""
        self.source_path_for_paste = path
        self.paste_operation = self.tr("copy")
        # print(self.tr("Prêt à copier : %1").arg(path))

    def cut_item(self, path):
        """Met le chemin en mémoire pour une opération de coupe."""
        self.source_path_for_paste = path
        self.paste_operation = self.tr("cut")
        # print(self.tr("Prêt à couper : %1").arg(path))

    def paste_item(self, destination_folder):
        """Colle le fichier/dossier en mémoire dans le dossier de destination."""
        if not self.source_path_for_paste or not self.paste_operation:
            return

        source_path = Path(self.source_path_for_paste)
        dest_path = Path(destination_folder) / source_path.name

        if str(dest_path).startswith(str(source_path)):
            QMessageBox.warning(
                self,
                self.tr("Opération impossible"),
                self.tr("Vous ne pouvez pas coller un dossier dans lui-même."),
            )
            return

        if dest_path.exists():
            reply = QMessageBox.question(
                self,
                self.tr("Conflit"),
                self.tr("Un élément nommé '%1' existe déjà. Voulez-vous le remplacer ?").arg(source_path.name),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.No:
                return
            try:
                if dest_path.is_dir():
                    shutil.rmtree(dest_path)
                else:
                    dest_path.unlink()
            except OSError as e:
                QMessageBox.critical(
                    self, self.tr("Erreur"), self.tr("Impossible de remplacer l'élément existant :\n%1").arg(e)
                )
                return

        try:
            if self.paste_operation == self.tr("copy"):
                if source_path.is_dir():
                    shutil.copytree(source_path, dest_path)
                else:
                    shutil.copy2(source_path, dest_path)
            elif self.paste_operation == self.tr("cut"):
                shutil.move(str(source_path), str(dest_path))
        except Exception as e:
            QMessageBox.critical(
                self, self.tr("Erreur de collage"), self.tr("L'opération a échoué :\n%1").arg(e)
            )
        finally:
            self.source_path_for_paste = None
            self.paste_operation = None

    def create_root_folder(self):
        """Crée un nouveau dossier à la racine du répertoire des notes."""
        if not self.journal_directory:
            QMessageBox.warning(
                self, self.tr("Action impossible"), self.tr("Le répertoire du journal n'est pas défini.")
            )
            return

        folder_name, ok = QInputDialog.getText(
            self, self.tr("Nouveau Dossier"), self.tr("Nom du nouveau dossier :")
        )

        if ok and folder_name.strip():
            notes_root_path = self.model.rootPath()
            new_folder_path = Path(notes_root_path) / folder_name.strip()

            if new_folder_path.exists():
                QMessageBox.warning(
                    self, self.tr("Dossier existant"), self.tr("Un dossier avec ce nom existe déjà.")
                )
                return

            try:
                os.mkdir(new_folder_path)
            except OSError as e:
                QMessageBox.critical(
                    self, self.tr("Erreur"), self.tr("Impossible de créer le dossier :\n%1").arg(e)
                )

    def rename_item(self, index):
        """Renomme un fichier ou un dossier."""
        old_path = self.model.filePath(index)
        old_name = self.model.fileName(index)

        new_name, ok = QInputDialog.getText(
            self, self.tr("Renommer"), self.tr("Nouveau nom :"), text=old_name
        )
        if not ok or not new_name.strip() or new_name == old_name:
            return

        new_path = str(Path(old_path).parent / new_name.strip())

        try:
            os.rename(old_path, new_path)
        except OSError as e:
            QMessageBox.critical(self, self.tr("Erreur"), self.tr("Impossible de renommer :\n%1").arg(e))

    def delete_item(self, index):
        """Supprime un fichier ou un dossier."""
        file_path = self.model.filePath(index)
        is_dir = self.model.isDir(index)
        item_name = Path(file_path).name

        if is_dir:
            sub_folders, files = self._count_folder_contents(file_path)
            if sub_folders == 0 and files == 0:
                question = (
                    self.tr("Le dossier '%1' est vide. Voulez-vous le supprimer ?").arg(item_name)
                )
            else:
                question = (
                    self.tr("Le dossier '%1' n'est pas vide.\n").arg(item_name)
                    self.tr("Il contient %1 sous-dossier(s) et %2 fichier(s).\n\n").arg(sub_folders).arg(files)
                    self.tr("Voulez-vous tout supprimer ?")
                )
            reply = QMessageBox.question(
                self,
                self.tr("Confirmation de suppression"),
                question,
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
        else:
            reply = QMessageBox.question(
                self,
                self.tr("Confirmation de suppression"),
                self.tr("Êtes-vous sûr de vouloir supprimer le fichier '%1' ?").arg(item_name),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

        if reply == QMessageBox.Yes:
            try:
                if is_dir:
                    shutil.rmtree(file_path)
                else:
                    self.model.remove(index)
            except Exception as e:
                QMessageBox.critical(self, self.tr("Erreur"), self.tr("Impossible de supprimer :\n%1").arg(e))

    def _count_folder_contents(self, folder_path):
        """Compte le nombre de sous-dossiers et de fichiers dans un dossier."""
        total_folders = 0
        total_files = 0
        for dirpath, dirnames, filenames in os.walk(folder_path):
            total_folders += len(dirnames)
            total_files += len(filenames)

        return total_folders, total_files

    def select_path(self, path):
        """Sélectionne un chemin dans l'arbre."""
        if not path:
            return
        source_index = self.model.index(path)
        if source_index.isValid():
            proxy_index = self.proxy_model.mapFromSource(source_index)
            self.tree_view.setCurrentIndex(proxy_index)
            self.tree_view.scrollTo(proxy_index, QTreeView.PositionAtCenter)

    def expand_all_from_index(self, index):
        """Déplie récursivement tous les sous-dossiers à partir d'un index."""
        if not index.isValid() or not self.model.isDir(index):
            return

        proxy_index = self.proxy_model.mapFromSource(index)
        self.tree_view.expand(proxy_index)
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
        proxy_index = self.proxy_model.mapFromSource(index)
        self.tree_view.collapse(proxy_index)

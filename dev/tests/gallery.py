#!/usr/bin/env python3
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

Prototype de galerie d'images pour BlueNotebook (Qt5).
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
    QScrollArea,
    QAction,
    QDialog,
    QSizePolicy,
)
from PyQt5.QtGui import QIcon, QPixmap, QImageReader, QImage
from PyQt5.QtCore import QSize, Qt


class ImageViewerDialog(QDialog):
    """Boîte de dialogue pour afficher l'image en plein format avec zoom."""

    def __init__(self, image_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle(os.path.basename(image_path))
        self.resize(1024, 768)

        # --- Attributs pour le zoom ---
        self.pixmap = None
        self.scale_factor = 1.0
        self.fit_mode = True  # L'image s'adapte à la fenêtre par défaut

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Important pour le contrôle manuel
        self.scroll_area.setAlignment(Qt.AlignCenter)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)

        # Chargement de l'image avec correction d'orientation
        reader = QImageReader(image_path)
        reader.setAutoTransform(True)
        image = reader.read()

        if not image.isNull():
            self.pixmap = QPixmap.fromImage(image)
            # Le premier affichage se fera via le premier resizeEvent
        else:
            self.image_label.setText("Impossible de charger l'image.")

        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)

    def update_image_display(self):
        """Met à jour l'affichage de l'image en fonction du mode et du facteur d'échelle."""
        if not self.pixmap:
            return

        if self.fit_mode:
            # Calculer le facteur d'échelle pour s'adapter à la fenêtre
            area_size = self.scroll_area.viewport().size()
            pixmap_size = self.pixmap.size()
            if pixmap_size.width() > 0 and pixmap_size.height() > 0:
                width_ratio = area_size.width() / pixmap_size.width()
                height_ratio = area_size.height() / pixmap_size.height()
                self.scale_factor = min(width_ratio, height_ratio)

        # Appliquer le facteur d'échelle
        new_size = self.pixmap.size() * self.scale_factor
        scaled_pixmap = self.pixmap.scaled(
            new_size, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )

        self.image_label.setPixmap(scaled_pixmap)
        self.image_label.resize(scaled_pixmap.size())

    def wheelEvent(self, event):
        """Gère le zoom avec la molette de la souris."""
        if not self.pixmap:
            return

        self.fit_mode = False  # L'utilisateur prend le contrôle du zoom

        delta = event.angleDelta().y()
        if delta > 0:
            self.scale_factor *= 1.25
        else:
            self.scale_factor /= 1.25

        self.update_image_display()

    def resizeEvent(self, event):
        """Appelé lors du redimensionnement de la fenêtre."""
        self.update_image_display()
        super().resizeEvent(event)

    def mouseDoubleClickEvent(self, event):
        """Réinitialise le zoom en mode 'fit to window' au double-clic."""
        if not self.fit_mode:
            self.fit_mode = True
            self.update_image_display()
        super().mouseDoubleClickEvent(event)


class GalleryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BlueNotebook - Galerie d'images")
        self.resize(900, 600)

        # Widget central
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Label d'info
        self.info_label = QLabel("Ouvrez un répertoire pour voir les images.")
        self.layout.addWidget(self.info_label)

        # QListWidget en mode IconMode pour la grille
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.IconMode)
        self.list_widget.setIconSize(QSize(180, 180))  # Taille des vignettes
        self.list_widget.setResizeMode(QListWidget.Adjust)
        self.list_widget.setSpacing(10)
        self.list_widget.setMovement(
            QListWidget.Static
        )  # Pas de déplacement des icones
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)

        # Connexion du double clic
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)

        self.layout.addWidget(self.list_widget)

        # Création du menu
        self.create_menu()

    def create_menu(self):
        menu_bar = self.menuBar()

        # Menu Fichier
        file_menu = menu_bar.addMenu("&Fichier")

        open_action = QAction("&Ouvrir un répertoire...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_directory)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut("Ctrl+Q")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Choisir un répertoire d'images"
        )
        if directory:
            self.load_images(directory)

    def load_images(self, directory):
        self.list_widget.clear()
        self.info_label.setText(f"Répertoire : {directory}")

        # Liste des extensions supportées par Qt + extensions courantes
        valid_extensions = {
            bytes(ext).decode().lower() for ext in QImageReader.supportedImageFormats()
        }
        valid_extensions.update(
            {"jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "tiff"}
        )

        path_obj = Path(directory)

        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            images = [
                f
                for f in path_obj.iterdir()
                if f.is_file() and f.suffix.lower().lstrip(".") in valid_extensions
            ]
            images.sort()

            for img_path in images:
                QApplication.processEvents()
                item = QListWidgetItem()
                item.setToolTip(img_path.name)

                # Utiliser QImageReader pour gérer l'orientation EXIF
                reader = QImageReader(str(img_path))
                reader.setAutoTransform(True)
                image = reader.read()

                if not image.isNull():
                    thumb = image.scaled(
                        250, 250, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                    item.setIcon(QIcon(QPixmap.fromImage(thumb)))
                else:
                    item.setIcon(QIcon(str(img_path)))

                item.setData(Qt.UserRole, str(img_path))
                self.list_widget.addItem(item)

            if not images:
                self.info_label.setText(f"Aucune image trouvée dans : {directory}")

        except Exception as e:
            self.info_label.setText(f"Erreur : {str(e)}")
        finally:
            QApplication.restoreOverrideCursor()

    def on_item_double_clicked(self, item):
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            viewer = ImageViewerDialog(file_path, self)
            viewer.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GalleryWindow()
    window.show()
    sys.exit(app.exec_())

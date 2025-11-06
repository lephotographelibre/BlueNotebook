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
Widget de lecture de documents PDF pour BlueNotebook.
Utilise PyMuPDF (fitz) pour le rendu et l'extraction de données.
"""

import fitz  # PyMuPDF

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QScrollArea,
    QMessageBox,
    QApplication,
    QMenu,
)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor
from PyQt5.QtCore import Qt, pyqtSignal, QRectF, QPoint
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QGuiApplication


class PdfViewer(QWidget):
    """Widget pour afficher les pages d'un document PDF."""

    document_loaded = pyqtSignal(
        bool, str, str, list, int
    )  # success, title, author, toc, page_count
    page_changed_by_search = pyqtSignal(int)  # page_num
    page_changed = pyqtSignal(int)  # V3.0.6 - Signal émis lors d'un changement de page

    def __init__(self, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page_num = 0
        self.search_results = []
        # V3.0.5 - Suivi de la recherche
        self.all_found_instances = []
        self.current_search_index = -1
        self.zoom_factor = 2.0  # Facteur de zoom initial
        # V3.0.5 - Pour la sélection de texte par mot
        self.is_selecting = False
        self.selection_start_point = None
        self.selection_end_point = None
        self.selected_word_rects = []

        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)  # Activer le suivi de la souris
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)

        layout.addWidget(self.scroll_area)

    def load_document(self, filepath):
        """Charge un document PDF."""
        try:
            self.doc = fitz.open(filepath)
            toc = self.doc.get_toc()
            page_count = self.doc.page_count

            title = self.doc.metadata.get("title", "Titre inconnu")
            author = self.doc.metadata.get("author", "Auteur inconnu")

            self.document_loaded.emit(True, title, author, toc, page_count)
            self.go_to_page(0)

        except Exception as e:
            QMessageBox.critical(self, "Erreur de chargement PDF", str(e))
            self.document_loaded.emit(False, "", "", [], 0)

    def render_page(self, page_num):
        """Affiche une page spécifique du PDF."""
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return

        self.current_page_num = page_num
        page = self.doc.load_page(page_num)

        # Zoom pour une meilleure qualité d'image
        zoom_matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=zoom_matrix)

        # Convertir en QImage
        qimage = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888
        )

        # Créer un QPixmap pour l'affichage
        pixmap = QPixmap.fromImage(qimage)

        # Dessiner les surlignages de recherche
        if self.search_results:
            painter = QPainter(pixmap)
            painter.setBrush(QColor(255, 255, 0, 100))  # Jaune semi-transparent
            painter.setPen(Qt.NoPen)
            for rect in self.search_results:
                # Appliquer le zoom aux coordonnées du rectangle (PyMuPDF Rect -> QRectF)
                qt_rect = QRectF(
                    rect.x0 * self.zoom_factor,
                    rect.y0 * self.zoom_factor,
                    rect.width * self.zoom_factor,
                    rect.height * self.zoom_factor,
                )
                painter.drawRect(qt_rect)
            painter.end()

        # V3.0.5 - Dessiner le surlignage de la sélection de texte
        if self.selected_word_rects:
            painter = QPainter(pixmap)
            # Couleur bleue semi-transparente pour la sélection
            painter.setBrush(QColor(0, 120, 215, 100))
            painter.setPen(Qt.NoPen)
            for rect in self.selected_word_rects:
                qt_rect = QRectF(
                    rect.x0 * self.zoom_factor,
                    rect.y0 * self.zoom_factor,
                    rect.width * self.zoom_factor,
                    rect.height * self.zoom_factor,
                )
                painter.drawRect(qt_rect)
            painter.end()

        self.image_label.setPixmap(pixmap)

    def go_to_page(self, page_num):
        """Naviguer vers une page."""
        if self.doc and 0 <= page_num < self.doc.page_count:
            # N'efface la recherche que si on change de page manuellement
            if self.current_page_num != page_num:
                self.clear_search()
            self.render_page(page_num)
            self.page_changed.emit(
                page_num
            )  # V3.0.6 - Émettre le signal de changement de page

    def find_text(self, text, new_search=False):
        """Rechercher du texte. Si new_search est True, relance une recherche complète."""
        if not self.doc or not text:
            self.clear_search()
            return

        if new_search:
            self.all_found_instances = []
            for page_num in range(self.doc.page_count):
                page = self.doc.load_page(page_num)
                instances = page.search_for(text)
                for inst in instances:
                    self.all_found_instances.append((page_num, inst))
            self.current_search_index = -1

        if not self.all_found_instances:
            QMessageBox.information(
                self, "Recherche", f"Le texte '{text}' n'a pas été trouvé."
            )
            self.clear_search()
            return

        self.navigate_search_results(1)

    def navigate_search_results(self, direction):
        """Navigue entre les résultats de recherche trouvés (1 pour suivant, -1 pour précédent)."""
        if not self.all_found_instances:
            return

        new_index = self.current_search_index + direction

        # Gérer le dépassement (boucler ou afficher un message)
        if not (0 <= new_index < len(self.all_found_instances)):
            QMessageBox.information(
                self, "Recherche", "Aucune autre occurrence trouvée."
            )
            # Optionnel: pour boucler la recherche
            # new_index = new_index % len(self.all_found_instances)
            return

        self.current_search_index = new_index
        page_num, rect = self.all_found_instances[self.current_search_index]

        # Si la nouvelle occurrence est sur une autre page, y naviguer
        if self.current_page_num != page_num:
            self.current_page_num = page_num
            self.page_changed_by_search.emit(page_num)

        # Mettre en surbrillance l'occurrence actuelle et rendre la page
        self.search_results = [rect]
        self.render_page(self.current_page_num)

    def clear_search(self):
        """Effacer les résultats de recherche."""
        self.search_results = []
        self.all_found_instances = []
        self.current_search_index = -1
        self.selected_word_rects = []
        self.is_selecting = False
        self.render_page(self.current_page_num)

    def close_document(self):
        """Ferme le document PDF."""
        if self.doc:
            self.doc.close()
            self.doc = None
        self.image_label.clear()

    def get_page_text(self, page_num):
        """Retourne le texte d'une page."""
        if self.doc and 0 <= page_num < self.doc.page_count:
            return self.doc.load_page(page_num).get_text()
        return ""

    def __del__(self):
        self.close_document()

    def wheelEvent(self, event):
        """Gère le zoom avec la molette de la souris + Ctrl."""
        if event.modifiers() == Qt.ControlModifier:
            # Récupérer le delta de la molette
            delta = event.angleDelta().y()

            if delta > 0:
                # Zoom avant
                self.zoom_factor *= 1.25
            else:
                # Zoom arrière
                self.zoom_factor /= 1.25

            # Limiter le zoom pour éviter les valeurs extrêmes
            self.zoom_factor = max(0.5, min(self.zoom_factor, 5.0))

            # Re-rendre la page avec le nouveau zoom
            self.render_page(self.current_page_num)
        else:
            # V3.0.6 - Gestion du défilement de page avec la molette
            scrollbar = self.scroll_area.verticalScrollBar()
            delta = event.angleDelta().y()

            # Défilement vers le bas
            if delta < 0:
                # Si on est en bas de la page, passer à la page suivante
                if scrollbar.value() == scrollbar.maximum():
                    if self.current_page_num < self.doc.page_count - 1:
                        self.go_to_page(self.current_page_num + 1)
                        event.accept()
                        return
            # Défilement vers le haut
            elif delta > 0:
                # Si on est en haut de la page, passer à la page précédente
                if scrollbar.value() == scrollbar.minimum():
                    if self.current_page_num > 0:
                        self.go_to_page(self.current_page_num - 1)
                        event.accept()
                        return

            # Sinon, comportement par défaut (scroll vertical dans la page)
            self.scroll_area.wheelEvent(event)

    def contextMenuEvent(self, event):
        """Affiche un menu contextuel pour copier le texte de la page."""
        if not self.doc:
            return

        menu = QMenu(self)

        # Action pour copier la sélection (activée seulement si du texte est sélectionné)
        copy_selection_action = menu.addAction("Copier la sélection")
        copy_selection_action.setEnabled(bool(self.selected_word_rects))

        # Action pour copier toute la page
        copy_page_action = menu.addAction("Copier le texte de la page")

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == copy_selection_action:
            self.copy_selected_text()
        elif action == copy_page_action:
            self.copy_page_text()

    def copy_page_text(self):
        """Copie le texte de la page actuelle dans le presse-papiers."""
        if self.doc:
            text = self.get_page_text(self.current_page_num)
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(
                self, "Copié", "Le texte de la page a été copié dans le presse-papiers."
            )

    def copy_selected_text(self):
        """Copie le texte des mots sélectionnés dans le presse-papiers."""
        if not self.doc:
            return

        # V3.0.5 - Correction de la copie de texte
        # Au lieu d'extraire le texte pour chaque rectangle, ce qui peut être imprécis,
        # nous récupérons tous les mots de la page et nous ne gardons que ceux
        # dont le rectangle est dans notre liste de sélection.
        page = self.doc.load_page(self.current_page_num)
        words = page.get_text("words")  # Liste de (x0, y0, x1, y1, "mot", ...)

        # Créer un set des rectangles sélectionnés pour une recherche rapide
        selected_rects_set = {tuple(rect) for rect in self.selected_word_rects}

        selected_words = [
            word_info[4]
            for word_info in words
            if tuple(word_info[:4]) in selected_rects_set
        ]
        selected_text = " ".join(selected_words)
        if selected_text.strip():
            QGuiApplication.clipboard().setText(selected_text.strip())
            QMessageBox.information(self, "Copié", "Le texte sélectionné a été copié.")

    def _get_pdf_point(self, widget_pos: QPoint) -> fitz.Point:
        """Convertit un point du widget en coordonnées de la page PDF."""
        pixmap_size = self.image_label.pixmap().size()
        viewport_size = self.scroll_area.viewport().size()
        offset_x = max(0, (viewport_size.width() - pixmap_size.width()) / 2)
        offset_y = max(0, (viewport_size.height() - pixmap_size.height()) / 2)

        pdf_x = (widget_pos.x() - offset_x) / self.zoom_factor
        pdf_y = (widget_pos.y() - offset_y) / self.zoom_factor

        return fitz.Point(pdf_x, pdf_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = True
            self.selected_word_rects = []  # Réinitialiser la sélection
            self.selection_start_point = self._get_pdf_point(event.pos())
            self.selection_end_point = self.selection_start_point
            self.update_selection()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_end_point = self._get_pdf_point(event.pos())
            self.update_selection()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False
            # La sélection est terminée, on ne fait rien de plus ici.
            # Les rectangles sélectionnés sont conservés pour la copie.

    def update_selection(self):
        """Met à jour la liste des mots sélectionnés en fonction des points de début et de fin."""
        if not self.doc or not self.is_selecting:
            return

        page = self.doc.load_page(self.current_page_num)
        words = page.get_text("words")  # Liste de (x0, y0, x1, y1, "mot", ...)

        # Créer le rectangle de sélection global à partir des points de début et de fin
        selection_rect = fitz.Rect(
            self.selection_start_point, self.selection_end_point
        ).normalize()

        self.selected_word_rects = []
        for word_info in words:
            x0, y0, x1, y1, word_text = word_info[:5]
            word_rect = fitz.Rect(x0, y0, x1, y1)

            # Un mot est sélectionné si son rectangle intersecte le rectangle de sélection
            if selection_rect.intersects(word_rect):
                self.selected_word_rects.append(word_rect)

        # Trier les rectangles pour s'assurer que le texte est copié dans le bon ordre
        # Tri par ligne (y0) puis par colonne (x0)
        self.selected_word_rects.sort(key=lambda r: (r.y0, r.x0))

        self.render_page(self.current_page_num)

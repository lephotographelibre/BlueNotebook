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
from PyQt5.QtGui import QGuiApplication
from pathlib import Path


class PdfViewer(QWidget):
    """Widget pour afficher les pages d'un document PDF."""

    document_loaded = pyqtSignal(
        bool, str, str, list, int
    )  # success, title, author, toc, page_count
    page_changed_by_search = pyqtSignal(int)  # page_num
    page_changed = pyqtSignal(int)  # Signal émis lors d'un changement de page

    def __init__(self, parent=None, settings_manager=None):
        super().__init__(parent)
        self.doc = None
        self.current_page_num = 0
        self.search_results = []
        self.all_found_instances = []
        self.current_search_index = -1
        self.zoom_factor = 2.0
        self.is_selecting = False
        self.selection_start_point = None
        self.selection_end_point = None
        self.selection_start_char = None
        self.selection_start_word = None
        self.selected_word_rects = []
        self.selected_text = self.tr("")
        self.settings_manager = settings_manager

        self.init_ui()

    def init_ui(self):
        """Initialiser l'interface utilisateur."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.image_label = QLabel()
        self.image_label.setMouseTracking(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidget(self.image_label)
        layout.addWidget(self.scroll_area)
        self.setMouseTracking(True)

    def load_document(self, filepath):
        try:
            self.doc = fitz.open(filepath)
            toc = self.doc.get_toc()
            page_count = self.doc.page_count
            title = self.doc.metadata.get(self.tr("title"), self.tr("Titre inconnu"))
            author = self.doc.metadata.get(self.tr("author"), self.tr("Auteur inconnu"))
            self.document_loaded.emit(True, title, author, toc, page_count)
            self.go_to_page(0)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Erreur de chargement PDF"), str(e))
            self.document_loaded.emit(False, self.tr(""), self.tr(""), [], 0)

    def render_page(self, page_num):
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return
        self.current_page_num = page_num
        page = self.doc.load_page(page_num)
        zoom_matrix = fitz.Matrix(self.zoom_factor, self.zoom_factor)
        pix = page.get_pixmap(matrix=zoom_matrix)
        qimage = QImage(
            pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888
        )
        pixmap = QPixmap.fromImage(qimage)
        if self.search_results:
            painter = QPainter(pixmap)
            painter.setBrush(QColor(255, 255, 0, 100))
            painter.setPen(Qt.NoPen)
            for rect in self.search_results:
                qt_rect = QRectF(
                    rect.x0 * self.zoom_factor,
                    rect.y0 * self.zoom_factor,
                    rect.width * self.zoom_factor,
                    rect.height * self.zoom_factor,
                )
                painter.drawRect(qt_rect)
            painter.end()
        if self.selected_word_rects:
            painter = QPainter(pixmap)
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
        if self.doc and 0 <= page_num < self.doc.page_count:
            if self.current_page_num != page_num:
                self.clear_search()
            self.render_page(page_num)
            self.page_changed.emit(page_num)

    def find_text(self, text, new_search=False):
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
            # Ajout de la boîte de message pour afficher le nombre d'occurrences
            if self.all_found_instances:
                QMessageBox.information(
                    self,
                    self.tr("Recherche"),
                    self.tr("%1 occurrence(s) trouvée(s) dans l'ensemble du document.").arg(len(self.all_found_instances)),
                )
            else:
                QMessageBox.information(
                    self, self.tr("Recherche"), self.tr("Le texte '%1' n'a pas été trouvé.").arg(text)
                )
                self.clear_search()
                return
        if self.all_found_instances:
            self.navigate_search_results(1)

    def navigate_search_results(self, direction):
        if not self.all_found_instances:
            return
        new_index = self.current_search_index + direction
        if not (0 <= new_index < len(self.all_found_instances)):
            QMessageBox.information(
                self, self.tr("Recherche"), self.tr("Aucune autre occurrence trouvée.")
            )
            return
        self.current_search_index = new_index
        page_num, rect = self.all_found_instances[self.current_search_index]
        if self.current_page_num != page_num:
            self.current_page_num = page_num
            self.page_changed_by_search.emit(page_num)
        self.search_results = [rect]
        self.render_page(self.current_page_num)

    def clear_search(self):
        self.search_results = []
        self.all_found_instances = []
        self.current_search_index = -1
        self.selected_word_rects = []
        self.selected_text = self.tr("")
        self.is_selecting = False
        self.selection_start_char = None
        self.selection_start_word = None
        self.render_page(self.current_page_num)

    def has_document(self):
        """Retourne True si un document PDF est chargé."""
        return self.doc is not None

    def close_document(self):
        if self.doc:
            self.doc.close()
            self.doc = None
        self.image_label.clear()

    def get_page_text(self, page_num):
        if self.doc and 0 <= page_num < self.doc.page_count:
            return self.doc.load_page(page_num).get_text()
        return self.tr("")

    def wheelEvent(self, event):
        if event.modifiers() == Qt.ControlModifier:
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_factor *= 1.25
            else:
                self.zoom_factor /= 1.25
            self.zoom_factor = max(0.5, min(self.zoom_factor, 5.0))
            self.render_page(self.current_page_num)
        else:
            scrollbar = self.scroll_area.verticalScrollBar()
            delta = event.angleDelta().y()
            if delta < 0:
                if scrollbar.value() == scrollbar.maximum():
                    if self.current_page_num < self.doc.page_count - 1:
                        self.go_to_page(self.current_page_num + 1)
                        event.accept()
                        return
            elif delta > 0:
                if scrollbar.value() == scrollbar.minimum():
                    if self.current_page_num > 0:
                        self.go_to_page(self.current_page_num - 1)
                        event.accept()
                        return
            self.scroll_area.wheelEvent(event)

    def contextMenuEvent(self, event):
        """Affiche un menu contextuel amélioré avec option de sauvegarde d'image."""
        if not self.doc:
            return

        menu = QMenu(self)
        copy_selection_action = menu.addAction(self.tr("Copier la sélection (Ctrl+C)"))
        copy_selection_action.setEnabled(bool(self.selected_text))
        select_all_action = menu.addAction(self.tr("Sélectionner toute la page (Ctrl+A)"))
        menu.addSeparator()
        copy_page_action = menu.addAction(self.tr("Copier le texte de la page"))

        pdf_point = self._get_pdf_point(event.pos())
        xref, img_rect = self._get_image_at_point(pdf_point)
        save_image_action = menu.addAction(self.tr("Sauvegarder cette image"))
        save_image_action.setEnabled(xref is not None)

        if self.selected_text:
            menu.addSeparator()
            clear_action = menu.addAction(self.tr("Effacer la sélection (ESC)"))
        else:
            clear_action = None

        action = menu.exec_(self.mapToGlobal(event.pos()))

        if action == copy_selection_action:
            self.copy_selected_text()
        elif action == copy_page_action:
            self.copy_page_text()
        elif action == select_all_action:
            self.select_all_page()
        elif action == save_image_action and xref is not None:
            self.save_image(xref)
        elif clear_action and action == clear_action:
            self.clear_selection()

    def save_image(self, xref):
        """Sauvegarde l'image spécifiée par xref dans un fichier .jpg choisi par l'utilisateur."""
        from PyQt5.QtWidgets import QFileDialog
        from PIL import Image
        import io

        last_dir = self.settings_manager.get(
            self.tr("pdf.last_image_save_directory"), str(Path.home())
        )

        try:
            image_data = self.doc.extract_image(xref)
            img_bytes = image_data[self.tr("image")]
            img_ext = image_data[self.tr("ext")].lower()

            img = Image.open(io.BytesIO(img_bytes))
            if img.mode != self.tr("RGB"):
                img = img.convert(self.tr("RGB"))

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                self.tr("Sauvegarder l'image"),
                str(Path(last_dir) / self.tr("image_%1.jpg").arg(xref)),
                self.tr("Images JPEG (*.jpg);;Tous les fichiers (*)"),
            )

            if file_path:
                if not file_path.lower().endswith(".jpg"):
                    file_path += self.tr(".jpg")
                img.save(file_path, self.tr("JPEG"))
                QMessageBox.information(
                    self, self.tr("Succès"), self.tr("Image sauvegardée sous %1").arg(file_path)
                )

                self.settings_manager.set(
                    self.tr("pdf.last_image_save_directory"), str(Path(file_path).parent)
                )
                self.settings_manager.save_settings()
        except Exception as e:
            QMessageBox.critical(
                self, self.tr("Erreur"), self.tr("Impossible de sauvegarder l'image : %1").arg(str(e))
            )

    def _get_image_at_point(self, pdf_point: fitz.Point) -> tuple:
        """Retourne l'identifiant de l'image et son rectangle si le point est à l'intérieur."""
        if not self.doc:
            return None, None
        page = self.doc.load_page(self.current_page_num)
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]
            rect = page.get_image_bbox(img)
            if rect.contains(pdf_point):
                return xref, rect
        return None, None

    def copy_page_text(self):
        if self.doc:
            text = self.get_page_text(self.current_page_num)
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(
                self, self.tr("Copié"), self.tr("Le texte de la page a été copié dans le presse-papiers.")
            )

    def copy_selected_text(self):
        if not self.doc:
            return
        if self.selected_text:
            QGuiApplication.clipboard().setText(self.selected_text)
            QMessageBox.information(self, self.tr("Copié"), self.tr("Le texte sélectionné a été copié."))
        else:
            QMessageBox.warning(self, self.tr("Sélection vide"), self.tr("Aucun texte sélectionné."))

    def clear_selection(self):
        self.selected_word_rects = []
        self.selected_text = self.tr("")
        self.is_selecting = False
        self.selection_start_char = None
        self.selection_start_word = None
        self.render_page(self.current_page_num)

    def select_all_page(self):
        if not self.doc:
            return
        page = self.doc.load_page(self.current_page_num)
        words = page.get_text(self.tr("words"))
        self.selected_word_rects = [fitz.Rect(w[:4]) for w in words]
        self.selected_text = page.get_text()
        self.render_page(self.current_page_num)

    def keyPressEvent(self, event):
        if event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            if self.selected_text:
                QGuiApplication.clipboard().setText(self.selected_text)
                event.accept()
                return
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_A:
            self.select_all_page()
            event.accept()
            return
        elif event.key() == Qt.Key_Escape:
            self.clear_selection()
            event.accept()
            return
        super().keyPressEvent(event)

    def _get_pdf_point(self, widget_pos: QPoint) -> fitz.Point:
        pixmap_size = self.image_label.pixmap().size()
        viewport_size = self.scroll_area.viewport().size()
        offset_x = max(0, (viewport_size.width() - pixmap_size.width()) / 2)
        offset_y = max(0, (viewport_size.height() - pixmap_size.height()) / 2)
        scroll_x = self.scroll_area.horizontalScrollBar().value()
        scroll_y = self.scroll_area.verticalScrollBar().value()
        pdf_x = (widget_pos.x() - offset_x + scroll_x) / self.zoom_factor
        pdf_y = (widget_pos.y() - offset_y + scroll_y) / self.zoom_factor
        return fitz.Point(pdf_x, pdf_y)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.doc:
            self.is_selecting = True
            self.selected_word_rects = []
            self.selected_text = self.tr("")

            pdf_point = self._get_pdf_point(event.pos())
            page = self.doc.load_page(self.current_page_num)
            text_dict = page.get_text(self.tr("dict"))
            closest_char = None
            min_distance = float(self.tr("inf"))

            for block in text_dict[self.tr("blocks")]:
                for line in block.get(self.tr("lines"), []):
                    for span in line.get(self.tr("spans"), []):
                        for char in span.get(self.tr("chars"), []):
                            char_rect = fitz.Rect(char[self.tr("bbox")])
                            char_center = fitz.Point(
                                (char_rect.x0 + char_rect.x1) / 2,
                                (char_rect.y0 + char_rect.y1) / 2,
                            )
                            distance = (
                                (char_center.x - pdf_point.x) ** 2
                                + (char_center.y - pdf_point.y) ** 2
                            ) ** 0.5
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_char = char

            if closest_char:
                self.selection_start_char = closest_char
                self.selection_start_point = fitz.Point(
                    closest_char[self.tr("bbox")][0], closest_char[self.tr("bbox")][1]
                )
                self.selection_end_point = self.selection_start_point
                self.selected_word_rects = [fitz.Rect(closest_char[self.tr("bbox")])]
                self.selected_text = closest_char[self.tr("c")]
                self.render_page(self.current_page_num)
            else:
                words = page.get_text(self.tr("words"))
                closest_word = None
                min_distance = float(self.tr("inf"))
                for word in words:
                    word_rect = fitz.Rect(word[:4])
                    word_center = fitz.Point(
                        (word_rect.x0 + word_rect.x1) / 2,
                        (word_rect.y0 + word_rect.y1) / 2,
                    )
                    distance = (
                        (word_center.x - pdf_point.x) ** 2
                        + (word_center.y - pdf_point.y) ** 2
                    ) ** 0.5
                    if distance < min_distance and distance < 50:
                        min_distance = distance
                        closest_word = word
                if closest_word:
                    self.selection_start_word = closest_word
                    self.selection_start_point = fitz.Point(
                        closest_word[0], closest_word[1]
                    )
                    self.selection_end_point = self.selection_start_point
                    self.selected_word_rects = [fitz.Rect(closest_word[:4])]
                    self.selected_text = closest_word[4]
                    self.render_page(self.current_page_num)
                else:
                    self.is_selecting = False
                    self.clear_selection()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.selection_end_point = self._get_pdf_point(event.pos())
            self.update_selection()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_selecting = False

    def update_selection(self):
        if not self.doc or not self.is_selecting:
            return
        page = self.doc.load_page(self.current_page_num)
        end_pdf_point = self.selection_end_point
        if hasattr(self, self.tr("selection_start_char")) and self.selection_start_char:
            text_dict = page.get_text(self.tr("dict"))
            closest_end_char = None
            min_distance = float(self.tr("inf"))
            for block in text_dict[self.tr("blocks")]:
                for line in block.get(self.tr("lines"), []):
                    for span in line.get(self.tr("spans"), []):
                        for char in span.get(self.tr("chars"), []):
                            char_rect = fitz.Rect(char[self.tr("bbox")])
                            char_center = fitz.Point(
                                (char_rect.x0 + char_rect.x1) / 2,
                                (char_rect.y0 + char_rect.y1) / 2,
                            )
                            distance = (
                                (char_center.x - end_pdf_point.x) ** 2
                                + (char_center.y - end_pdf_point.y) ** 2
                            ) ** 0.5
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_end_char = char
            if not closest_end_char:
                return
            self.selected_text = self.tr("")
            self.selected_word_rects = []
            selecting = False
            for block in text_dict[self.tr("blocks")]:
                for line in block.get(self.tr("lines"), []):
                    for span in line.get(self.tr("spans"), []):
                        for char in span.get(self.tr("chars"), []):
                            if char == self.selection_start_char:
                                selecting = True
                            if selecting:
                                self.selected_text += char[self.tr("c")]
                                self.selected_word_rects.append(fitz.Rect(char[self.tr("bbox")]))
                            if char == closest_end_char:
                                selecting = False
                                break
                        if not selecting:
                            break
                    if not selecting:
                        break
                if not selecting:
                    break
            if closest_end_char[self.tr("bbox")][1] < self.selection_start_char[self.tr("bbox")][1]:
                self.selected_text = self.tr("")
                self.selected_word_rects = []
                selecting = False
                for block in text_dict[self.tr("blocks")]:
                    for line in block.get(self.tr("lines"), []):
                        for span in line.get(self.tr("spans"), []):
                            for char in span.get(self.tr("chars"), []):
                                if char == closest_end_char:
                                    selecting = True
                                if selecting:
                                    self.selected_text += char[self.tr("c")]
                                    self.selected_word_rects.append(
                                        fitz.Rect(char[self.tr("bbox")])
                                    )
                                if char == self.selection_start_char:
                                    selecting = False
                                    break
                            if not selecting:
                                break
                        if not selecting:
                            break
                    if not selecting:
                        break
        elif hasattr(self, self.tr("selection_start_word")) and self.selection_start_word:
            words = page.get_text(self.tr("words"))
            closest_end_word = None
            min_distance = float(self.tr("inf"))
            for word in words:
                word_rect = fitz.Rect(word[:4])
                word_center = fitz.Point(
                    (word_rect.x0 + word_rect.x1) / 2, (word_rect.y0 + word_rect.y1) / 2
                )
                distance = (
                    (word_center.x - end_pdf_point.x) ** 2
                    + (word_center.y - end_pdf_point.y) ** 2
                ) ** 0.5
                if distance < min_distance and distance < 50:
                    min_distance = distance
                    closest_end_word = word
            if not closest_end_word:
                return
            self.selected_text = self.tr("")
            self.selected_word_rects = []
            selecting = False
            for word in words:
                if word == self.selection_start_word:
                    selecting = True
                if selecting:
                    self.selected_text += word[4] + self.tr(" ")
                    self.selected_word_rects.append(fitz.Rect(word[:4]))
                if word == closest_end_word:
                    selecting = False
                    break
            if closest_end_word[1] < self.selection_start_word[1]:
                self.selected_text = self.tr("")
                self.selected_word_rects = []
                selecting = False
                for word in words:
                    if word == closest_end_word:
                        selecting = True
                    if selecting:
                        self.selected_text += word[4] + self.tr(" ")
                        self.selected_word_rects.append(fitz.Rect(word[:4]))
                    if word == self.selection_start_word:
                        selecting = False
                        break
        self.render_page(self.current_page_num)

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
from pathlib import Path  # Ajout de cette ligne


class PdfViewer(QWidget):
    """Widget pour afficher les pages d'un document PDF."""

    document_loaded = pyqtSignal(
        bool, str, str, list, int
    )  # success, title, author, toc, page_count
    page_changed_by_search = pyqtSignal(int)  # page_num
    page_changed = pyqtSignal(int)  # V3.0.6 - Signal émis lors d'un changement de page

    def __init__(self, settings_manager=None, parent=None):
        super().__init__(parent)
        self.doc = None
        self.current_page_num = 0
        self.search_results = []
        self.all_found_instances = []
        self.current_search_index = -1
        self.zoom_factor = 2.0  # Facteur de zoom initial
        self.is_selecting = False
        self.selection_start_point = None
        self.selection_end_point = None
        self.selection_start_char = None
        self.selection_start_word = None
        self.selected_word_rects = []
        self.selected_text = ""
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
        # print(f"Loading PDF: {filepath}")
        try:
            self.doc = fitz.open(filepath)
            # print(f"PDF loaded, page count: {self.doc.page_count}")
            toc = self.doc.get_toc()
            page_count = self.doc.page_count
            title = self.doc.metadata.get("title", "Titre inconnu")
            author = self.doc.metadata.get("author", "Auteur inconnu")
            self.document_loaded.emit(True, title, author, toc, page_count)
            self.go_to_page(0)
        except Exception as e:
            # print(f"Error loading PDF: {str(e)}")
            QMessageBox.critical(self, "Erreur de chargement PDF", str(e))
            self.document_loaded.emit(False, "", "", [], 0)

    def render_page(self, page_num):
        if not self.doc or not (0 <= page_num < self.doc.page_count):
            return
        self.current_page_num = page_num
        page = self.doc.load_page(page_num)
        # print(f"Page {page_num} dimensions: {page.rect}")
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
        if not self.all_found_instances:
            QMessageBox.information(
                self, "Recherche", f"Le texte '{text}' n'a pas été trouvé."
            )
            self.clear_search()
            return
        self.navigate_search_results(1)

    def navigate_search_results(self, direction):
        if not self.all_found_instances:
            return
        new_index = self.current_search_index + direction
        if not (0 <= new_index < len(self.all_found_instances)):
            QMessageBox.information(
                self, "Recherche", "Aucune autre occurrence trouvée."
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
        self.selected_text = ""
        self.is_selecting = False
        self.selection_start_char = None
        self.selection_start_word = None
        self.render_page(self.current_page_num)

    def close_document(self):
        if self.doc:
            self.doc.close()
            self.doc = None
        self.image_label.clear()

    def get_page_text(self, page_num):
        if self.doc and 0 <= page_num < self.doc.page_count:
            return self.doc.load_page(page_num).get_text()
        return ""

    def __del__(self):
        self.close_document()

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
        copy_selection_action = menu.addAction("Copier la sélection (Ctrl+C)")
        copy_selection_action.setEnabled(bool(self.selected_text))
        select_all_action = menu.addAction("Sélectionner toute la page (Ctrl+A)")
        menu.addSeparator()
        copy_page_action = menu.addAction("Copier le texte de la page")

        # Vérifier si le clic est sur une image
        pdf_point = self._get_pdf_point(event.pos())
        xref, img_rect = self._get_image_at_point(pdf_point)
        save_image_action = menu.addAction("Sauvegarder cette image")
        save_image_action.setEnabled(xref is not None)

        if self.selected_text:
            menu.addSeparator()
            clear_action = menu.addAction("Effacer la sélection (ESC)")
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

        # Récupérer le dernier répertoire de sauvegarde depuis les préférences
        last_dir = self.settings_manager.get(
            "pdf.last_image_save_directory", str(Path.home())
        )

        try:
            # Extraire l'image du PDF
            image_data = self.doc.extract_image(xref)
            img_bytes = image_data["image"]
            img_ext = image_data["ext"].lower()

            # Convertir en image PIL pour sauvegarde en JPG
            img = Image.open(io.BytesIO(img_bytes))
            if img.mode != "RGB":
                img = img.convert("RGB")

            # Ouvrir une boîte de dialogue pour choisir le fichier
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Sauvegarder l'image",
                str(Path(last_dir) / f"image_{xref}.jpg"),
                "Images JPEG (*.jpg);;Tous les fichiers (*)",
            )

            if file_path:
                # S'assurer que l'extension est .jpg
                if not file_path.lower().endswith(".jpg"):
                    file_path += ".jpg"
                img.save(file_path, "JPEG")
                QMessageBox.information(
                    self, "Succès", f"Image sauvegardée sous {file_path}"
                )

                # Mémoriser le répertoire de destination pour la prochaine fois
                self.settings_manager.set(
                    "pdf.last_image_save_directory", str(Path(file_path).parent)
                )
                self.settings_manager.save_settings()
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de sauvegarder l'image : {str(e)}"
            )

    def _get_image_at_point(self, pdf_point: fitz.Point) -> tuple:
        """Retourne l'identifiant de l'image et son rectangle si le point est à l'intérieur."""
        if not self.doc:
            return None, None
        page = self.doc.load_page(self.current_page_num)
        images = page.get_images(full=True)
        for img in images:
            xref = img[0]  # Identifiant de l'image
            rect = page.get_image_bbox(img)
            if rect.contains(pdf_point):
                return xref, rect
        return None, None

    def copy_page_text(self):
        if self.doc:
            text = self.get_page_text(self.current_page_num)
            QGuiApplication.clipboard().setText(text)
            QMessageBox.information(
                self, "Copié", "Le texte de la page a été copié dans le presse-papiers."
            )

    def copy_selected_text(self):
        if not self.doc:
            return
        if self.selected_text:
            QGuiApplication.clipboard().setText(self.selected_text)
            QMessageBox.information(self, "Copié", "Le texte sélectionné a été copié.")
        else:
            QMessageBox.warning(self, "Sélection vide", "Aucun texte sélectionné.")

    def clear_selection(self):
        self.selected_word_rects = []
        self.selected_text = ""
        self.is_selecting = False
        self.selection_start_char = None
        self.selection_start_word = None
        self.render_page(self.current_page_num)

    def select_all_page(self):
        if not self.doc:
            return
        page = self.doc.load_page(self.current_page_num)
        words = page.get_text("words")
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
        """print(
            f"_get_pdf_point: widget_pos={widget_pos}, pixmap_size={pixmap_size}, "
            f"viewport_size={viewport_size}, offset_x={offset_x}, offset_y={offset_y}, "
            f"scroll_x={scroll_x}, scroll_y={scroll_y}, pdf_x={pdf_x}, pdf_y={pdf_y}"
        )"""
        pdf_x_simple = widget_pos.x() / self.zoom_factor
        pdf_y_simple = widget_pos.y() / self.zoom_factor
        # print(f"Simplified pdf_point: Point({pdf_x_simple}, {pdf_y_simple})")
        return fitz.Point(pdf_x, pdf_y)

    def mousePressEvent(self, event):
        """print(
            f"Mouse press event: button={event.button()}, pos={event.pos()}, zoom_factor={self.zoom_factor}"
        )"""
        if event.button() == Qt.LeftButton and self.doc:
            self.is_selecting = True
            self.selected_word_rects = []
            self.selected_text = ""

            pdf_point = self._get_pdf_point(event.pos())
            # print(f"PDF point: {pdf_point}")

            page = self.doc.load_page(self.current_page_num)
            text_dict = page.get_text("dict")
            # print(f"Text dict: {len(text_dict['blocks'])} blocks found")
            closest_char = None
            min_distance = float("inf")

            for block in text_dict["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        for char in span.get("chars", []):
                            char_rect = fitz.Rect(char["bbox"])
                            char_center = fitz.Point(
                                (char_rect.x0 + char_rect.x1) / 2,
                                (char_rect.y0 + char_rect.y1) / 2,
                            )
                            distance = (
                                (char_center.x - pdf_point.x) ** 2
                                + (char_center.y - pdf_point.y) ** 2
                            ) ** 0.5
                            """print(
                                f"Char: {char['c']}, bbox={char['bbox']}, center={char_center}, distance={distance}"
                            )"""
                            if distance < min_distance and distance < 50:
                                min_distance = distance
                                closest_char = char

            if closest_char:
                """print(
                    f"Selected caret: {closest_char['c']} at {closest_char['bbox']}, distance={min_distance}"
                )"""
                self.selection_start_char = closest_char
                self.selection_start_point = fitz.Point(
                    closest_char["bbox"][0], closest_char["bbox"][1]
                )
                self.selection_end_point = self.selection_start_point
                self.selected_word_rects = [fitz.Rect(closest_char["bbox"])]
                self.selected_text = closest_char["c"]
                self.render_page(self.current_page_num)
            else:
                # print(f"No character found near click, min_distance={min_distance}")
                words = page.get_text("words")
                # print(f"Words found: {len(words)}")
                closest_word = None
                min_distance = float("inf")
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
                    """print(
                        f"Word: {word[4]}, bbox={word[:4]}, center={word_center}, distance={distance}"
                    )"""
                    if distance < min_distance and distance < 50:
                        min_distance = distance
                        closest_word = word
                if closest_word:
                    """print(
                        f"Selected word: {closest_word[4]} at {closest_word[:4]}, distance={min_distance}"
                    )"""
                    self.selection_start_word = closest_word
                    self.selection_start_point = fitz.Point(
                        closest_word[0], closest_word[1]
                    )
                    self.selection_end_point = self.selection_start_point
                    self.selected_word_rects = [fitz.Rect(closest_word[:4])]
                    self.selected_text = closest_word[4]
                    self.render_page(self.current_page_num)
                else:
                    # print(f"No word found near click, min_distance={min_distance}")
                    self.is_selecting = False
                    self.clear_selection()

    def mouseMoveEvent(self, event):
        # print(f"Mouse move event: pos={event.pos()}, is_selecting={self.is_selecting}")
        if self.is_selecting:
            self.selection_end_point = self._get_pdf_point(event.pos())
            self.update_selection()

    def mouseReleaseEvent(self, event):
        # print(f"Mouse release event: button={event.button()}")
        if event.button() == Qt.LeftButton:
            self.is_selecting = False

    def update_selection(self):
        if not self.doc or not self.is_selecting:
            return
        page = self.doc.load_page(self.current_page_num)
        end_pdf_point = self.selection_end_point
        if hasattr(self, "selection_start_char") and self.selection_start_char:
            text_dict = page.get_text("dict")
            closest_end_char = None
            min_distance = float("inf")
            for block in text_dict["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        for char in span.get("chars", []):
                            char_rect = fitz.Rect(char["bbox"])
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
            self.selected_text = ""
            self.selected_word_rects = []
            selecting = False
            for block in text_dict["blocks"]:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        for char in span.get("chars", []):
                            if char == self.selection_start_char:
                                selecting = True
                            if selecting:
                                self.selected_text += char["c"]
                                self.selected_word_rects.append(fitz.Rect(char["bbox"]))
                            if char == closest_end_char:
                                selecting = False
                                break
                        if not selecting:
                            break
                    if not selecting:
                        break
                if not selecting:
                    break
            if closest_end_char["bbox"][1] < self.selection_start_char["bbox"][1]:
                self.selected_text = ""
                self.selected_word_rects = []
                selecting = False
                for block in text_dict["blocks"]:
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            for char in span.get("chars", []):
                                if char == closest_end_char:
                                    selecting = True
                                if selecting:
                                    self.selected_text += char["c"]
                                    self.selected_word_rects.append(
                                        fitz.Rect(char["bbox"])
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
        elif hasattr(self, "selection_start_word") and self.selection_start_word:
            words = page.get_text("words")
            closest_end_word = None
            min_distance = float("inf")
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
            self.selected_text = ""
            self.selected_word_rects = []
            selecting = False
            for word in words:
                if word == self.selection_start_word:
                    selecting = True
                if selecting:
                    self.selected_text += word[4] + " "
                    self.selected_word_rects.append(fitz.Rect(word[:4]))
                if word == closest_end_word:
                    selecting = False
                    break
            if closest_end_word[1] < self.selection_start_word[1]:
                self.selected_text = ""
                self.selected_word_rects = []
                selecting = False
                for word in words:
                    if word == closest_end_word:
                        selecting = True
                    if selecting:
                        self.selected_text += word[4] + " "
                        self.selected_word_rects.append(fitz.Rect(word[:4]))
                    if word == self.selection_start_word:
                        selecting = False
                        break
        self.render_page(self.current_page_num)

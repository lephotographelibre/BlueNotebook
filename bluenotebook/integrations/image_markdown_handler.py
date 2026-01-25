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
Module centralisé pour gérer l'insertion d'images Markdown,
incluant la copie locale, le renommage et la gestion des données EXIF.
"""

import re
import shutil
from datetime import datetime
from pathlib import Path

import requests
from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from geopy.geocoders import Nominatim
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)
from PyQt5.QtCore import QCoreApplication


class ImageMarkdownHandlerContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("ImageMarkdownHandlerContext", text)


class ImageSourceDialog(QDialog):
    """
    Boîte de dialogue pour obtenir le chemin d'une image,
    soit via une URL, soit via un sélecteur de fichier.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Source de l'image"))
        self.setModal(True)
        self.resize(500, 120)

        self.layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText(
            self.tr("http://example.com/image.png ou /chemin/local")
        )
        path_layout.addWidget(self.path_edit)

        browse_button = QPushButton(self.tr("Parcourir..."), self)
        browse_button.clicked.connect(self._browse_file)
        path_layout.addWidget(browse_button)

        form_layout.addRow(self.tr("Chemin ou URL:"), path_layout)
        self.layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def _browse_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Sélectionner une image"),
            "",
            self.tr("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)"),
        )
        if path:
            self.path_edit.setText(path)

    def get_path(self):
        return self.path_edit.text().strip()


def _get_exif_data(image_path):
    try:
        image = Image.open(image_path)
        exif_data = image._getexif()
        if not exif_data:
            return None
        return {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    except Exception:
        return None


def _get_decimal_from_dms(dms, ref):
    degrees = dms[0]
    minutes = dms[1] / 60.0
    seconds = dms[2] / 3600.0
    decimal = degrees + minutes + seconds
    if ref in ["S", "W"]:
        decimal = -decimal
    return decimal


def _get_gps_info(exif_data):
    if "GPSInfo" not in exif_data:
        return None, None
    gps_info = {
        GPSTAGS.get(tag, tag): value for tag, value in exif_data["GPSInfo"].items()
    }
    lat_dms = gps_info.get("GPSLatitude")
    lon_dms = gps_info.get("GPSLongitude")
    lat_ref = gps_info.get("GPSLatitudeRef")
    lon_ref = gps_info.get("GPSLongitudeRef")
    if lat_dms and lon_dms and lat_ref and lon_ref:
        lat = _get_decimal_from_dms(lat_dms, lat_ref)
        lon = _get_decimal_from_dms(lon_dms, lon_ref)
        return lat, lon
    return None, None


def get_location_name_from_gps(lat, lon):
    if not lat or not lon:
        return ImageMarkdownHandlerContext.tr("Lieu inconnu")
    try:
        geolocator = Nominatim(user_agent="bluenotebook_app")
        location = geolocator.reverse((lat, lon), exactly_one=True, language="fr")
        if location:
            address = location.raw.get("address", {})
            city = address.get("city", address.get("town", address.get("village", "")))
            return city if city else location.address.split(",")[0]
        return ImageMarkdownHandlerContext.tr("Lieu inconnu")
    except (GeocoderTimedOut, GeocoderUnavailable):
        return ImageMarkdownHandlerContext.tr("Service de géolocalisation indisponible")
    except Exception:
        return ImageMarkdownHandlerContext.tr("Erreur de géolocalisation")


def format_exif_as_markdown_string(image_path: str) -> str | None:
    exif_data = _get_exif_data(image_path)
    if not exif_data:
        return None
    lat, lon = _get_gps_info(exif_data)
    if not any([lat, exif_data.get("DateTimeOriginal"), exif_data.get("Model")]):
        return None
    location_part = ""
    if lat and lon:
        location_name = get_location_name_from_gps(lat, lon) or ImageMarkdownHandlerContext.tr("Lieu")
        osm_link = f"https://www.openstreetmap.org/?mlat={lat:.6f}&mlon={lon:.6f}#map=16/{lat:.6f}/{lon:.6f}"
        location_part = f"[{location_name}]({osm_link}) : "

    details_parts = []
    if dt_original := exif_data.get("DateTimeOriginal"):
        try:
            dt_obj = datetime.strptime(dt_original, "%Y:%m:%d %H:%M:%S")
            details_parts.append(dt_obj.strftime("%d/%m/%Y %H:%M"))
        except (ValueError, TypeError):
            pass
    if make := exif_data.get("Make", "").strip():
        details_parts.append(make)
    if model := exif_data.get("Model", "").strip():
        details_parts.append(model)
    if f_number := exif_data.get("FNumber"):
        details_parts.append(f"ƒ/{f_number}")

    speed_label = ImageMarkdownHandlerContext.tr("Vitesse:")
    if exposure_time := exif_data.get("ExposureTime"):
        speed = (
            f"1/{int(1/exposure_time)}s" if exposure_time > 0 else f"{exposure_time}s"
        )
        details_parts.append(f"{speed_label} {speed}")

    focal_label = ImageMarkdownHandlerContext.tr("Focale:")
    if focal_length := exif_data.get("FocalLength"):
        details_parts.append(f"{focal_label} {focal_length}mm")

    iso_label = ImageMarkdownHandlerContext.tr("ISO:")
    if iso := exif_data.get("ISOSpeedRatings"):
        details_parts.append(f"{iso_label} {iso}")

    details_text = " : ".join(filter(None, details_parts))
    return f"{location_part}**{details_text}**"


def handle_markdown_image_insertion(editor):
    """Fonction principale pour gérer l'insertion d'une image Markdown."""
    main_window = editor.main_window
    if not main_window or not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            ImageMarkdownHandlerContext.tr("Journal non défini"),
            ImageMarkdownHandlerContext.tr("Veuillez définir un répertoire de journal avant d'insérer une image."),
        )
        return

    dialog = ImageSourceDialog(main_window)
    if dialog.exec_() != QDialog.Accepted:
        return

    source_path = dialog.get_path()
    if not source_path:
        return

    is_remote = source_path.lower().startswith(("http://", "https://"))
    journal_images_dir = main_window.journal_directory / "images"
    journal_images_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if is_remote:
        try:
            response = requests.get(source_path, stream=True, timeout=10)
            response.raise_for_status()
            original_filename = Path(source_path).name.split("?")[0]
            new_filename = f"{timestamp}_{original_filename}"
            destination_file = journal_images_dir / new_filename
            with open(destination_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.RequestException as e:
            QMessageBox.critical(
                main_window,
                ImageMarkdownHandlerContext.tr("Erreur"),
                ImageMarkdownHandlerContext.tr("Erreur de téléchargement: {error}").format(error=str(e))
            )
            return
    else:
        source_file = Path(source_path)
        if not source_file.is_file():
            QMessageBox.critical(
                main_window,
                ImageMarkdownHandlerContext.tr("Erreur"),
                ImageMarkdownHandlerContext.tr("Le fichier local n'existe pas.")
            )
            return
        new_filename = f"{timestamp}_{source_file.name}"
        destination_file = journal_images_dir / new_filename
        try:
            shutil.copy2(source_file, destination_file)
        except Exception as e:
            QMessageBox.critical(
                main_window,
                ImageMarkdownHandlerContext.tr("Erreur"),
                ImageMarkdownHandlerContext.tr("Erreur de copie: {error}").format(error=str(e))
            )
            return

    relative_path = f"images/{new_filename}"
    alt_text = re.sub(r"^\d{14}_", "", Path(relative_path).stem)
    markdown_link = f"[![{alt_text}]({relative_path})]({relative_path})"

    exif_caption = format_exif_as_markdown_string(str(destination_file))

    if exif_caption:
        reply = QMessageBox.question(
            main_window,
            ImageMarkdownHandlerContext.tr("Données EXIF trouvées"),
            ImageMarkdownHandlerContext.tr("Des données EXIF ont été trouvées. Voulez-vous les insérer ?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            editor.insert_text(f"{markdown_link}\n{exif_caption}\n")
        else:
            editor.insert_text(markdown_link)
    else:
        editor.insert_text(markdown_link)

    editor.text_edit.setFocus()
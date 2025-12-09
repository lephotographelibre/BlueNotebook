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
            self.tr(""),
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
    if ref in [self.tr("S"), self.tr("W")]:
        decimal = -decimal
    return decimal


def _get_gps_info(exif_data):
    if self.tr("GPSInfo") not in exif_data:
        return None, None
    gps_info = {
        GPSTAGS.get(tag, tag): value for tag, value in exif_data[self.tr("GPSInfo")].items()
    }
    lat_dms = gps_info.get(self.tr("GPSLatitude"))
    lon_dms = gps_info.get(self.tr("GPSLongitude"))
    lat_ref = gps_info.get(self.tr("GPSLatitudeRef"))
    lon_ref = gps_info.get(self.tr("GPSLongitudeRef"))
    if lat_dms and lon_dms and lat_ref and lon_ref:
        lat = _get_decimal_from_dms(lat_dms, lat_ref)
        lon = _get_decimal_from_dms(lon_dms, lon_ref)
        return lat, lon
    return None, None


def get_location_name_from_gps(lat, lon):
    if not lat or not lon:
        return self.tr("Lieu inconnu")
    try:
        geolocator = Nominatim(user_agent=self.tr("bluenotebook_app"))
        location = geolocator.reverse((lat, lon), exactly_one=True, language=self.tr("fr"))
        if location:
            address = location.raw.get(self.tr("address"), {})
            city = address.get(self.tr("city"), address.get(self.tr("town"), address.get(self.tr("village"), self.tr(""))))
            return city if city else location.address.split(self.tr(","))[0]
        return self.tr("Lieu inconnu")
    except (GeocoderTimedOut, GeocoderUnavailable):
        return self.tr("Service de géolocalisation indisponible")
    except Exception:
        return self.tr("Erreur de géolocalisation")


def format_exif_as_markdown_string(image_path: str) -> str | None:
    exif_data = _get_exif_data(image_path)
    if not exif_data:
        return None
    lat, lon = _get_gps_info(exif_data)
    if not any([lat, exif_data.get(self.tr("DateTimeOriginal")), exif_data.get(self.tr("Model"))]):
        return None
    location_part = self.tr("")
    if lat and lon:
        location_name = get_location_name_from_gps(lat, lon) or self.tr("Lieu")
        osm_link = self.tr("https://www.openstreetmap.org/?mlat=%1&mlon=%2#map=16/%3/%4").arg(lat).arg(lon).arg(lat).arg(lon)
        location_part = self.tr("[%1](%2) : ").arg(location_name).arg(osm_link)
    details_parts = []
    if dt_original := exif_data.get(self.tr("DateTimeOriginal")):
        try:
            dt_obj = datetime.strptime(dt_original, "%Y:%m:%d %H:%M:%S")
            details_parts.append(dt_obj.strftime("%d/%m/%Y %H:%M"))
        except (ValueError, TypeError):
            pass
    if make := exif_data.get(self.tr("Make"), self.tr("")).strip():
        details_parts.append(make)
    if model := exif_data.get(self.tr("Model"), self.tr("")).strip():
        details_parts.append(model)
    if f_number := exif_data.get(self.tr("FNumber")):
        details_parts.append(self.tr("ƒ/%1").arg(f_number))
    if exposure_time := exif_data.get(self.tr("ExposureTime")):
        speed = (
            self.tr("1/%1s").arg(int(1/exposure_time)) if exposure_time > 0 else self.tr("%1s").arg(exposure_time)
        )
        details_parts.append(self.tr("Vitesse: %1").arg(speed))
    if focal_length := exif_data.get(self.tr("FocalLength")):
        details_parts.append(self.tr("Focale: %1mm").arg(focal_length))
    if iso := exif_data.get(self.tr("ISOSpeedRatings")):
        details_parts.append(self.tr("ISO: %1").arg(iso))
    details_text = self.tr(" : ").join(filter(None, details_parts))
    return self.tr("%1**%2**").arg(location_part).arg(details_text)


def handle_markdown_image_insertion(editor):
    """Fonction principale pour gérer l'insertion d'une image Markdown."""
    main_window = editor.main_window
    if not main_window or not main_window.journal_directory:
        QMessageBox.warning(
            main_window,
            self.tr("Journal non défini"),
            self.tr("Veuillez définir un répertoire de journal avant d'insérer une image."),
        )
        return

    dialog = ImageSourceDialog(main_window)
    if dialog.exec_() != QDialog.Accepted:
        return

    source_path = dialog.get_path()
    if not source_path:
        return

    is_remote = source_path.lower().startswith(("http://", "https://"))
    journal_images_dir = main_window.journal_directory / self.tr("images")
    journal_images_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    if is_remote:
        try:
            response = requests.get(source_path, stream=True, timeout=10)
            response.raise_for_status()
            original_filename = Path(source_path).name.split(self.tr("?"))[0]
            new_filename = self.tr("%1_%2").arg(timestamp).arg(original_filename)
            destination_file = journal_images_dir / new_filename
            with open(destination_file, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.RequestException as e:
            QMessageBox.critical(
                main_window, self.tr("Erreur"), self.tr("Erreur de téléchargement: %1").arg(e)
            )
            return
    else:
        source_file = Path(source_path)
        if not source_file.is_file():
            QMessageBox.critical(
                main_window, self.tr("Erreur"), self.tr("Le fichier local n'existe pas.")
            )
            return
        new_filename = self.tr("%1_%2").arg(timestamp).arg(source_file.name)
        destination_file = journal_images_dir / new_filename
        try:
            shutil.copy2(source_file, destination_file)
        except Exception as e:
            QMessageBox.critical(main_window, self.tr("Erreur"), self.tr("Erreur de copie: %1").arg(e))
            return

    relative_path = self.tr("images/%1").arg(new_filename)
    alt_text = re.sub(r"^\d{14}_", "", Path(relative_path).stem)
    markdown_link = self.tr("[![%1](%2)](%3)").arg(alt_text).arg(relative_path).arg(relative_path)

    exif_caption = format_exif_as_markdown_string(str(destination_file))

    if exif_caption:
        reply = QMessageBox.question(
            main_window,
            self.tr("Données EXIF trouvées"),
            self.tr("Des données EXIF ont été trouvées. Voulez-vous les insérer ?"),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            editor.insert_text(self.tr("%1\n%2\n").arg(markdown_link).arg(exif_caption))
        else:
            editor.insert_text(markdown_link)
    else:
        editor.insert_text(markdown_link)

    editor.text_edit.setFocus()

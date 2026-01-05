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

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt


class OnlineHelpWindow(QDialog):
    """Fenêtre d'aide en ligne affichant un fichier HTML local."""

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.setWindowTitle(self.tr("Aide en ligne"))
        self.resize(1200, 800)

        # Permettre de redimensionner et maximiser la fenêtre
        self.setWindowFlags(
            self.windowFlags() | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint
        )

        layout = QVBoxLayout(self)

        # Navigateur Web
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl(url))
        layout.addWidget(self.web_view)

        # Bouton Fermer en bas à droite
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.close_button = QPushButton(self.tr("Fermer"))
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

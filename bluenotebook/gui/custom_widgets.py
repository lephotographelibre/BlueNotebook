"""
Widgets personnalisés pour l'interface de BlueNotebook.
"""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt


class CenteredStatusBarLabel(QLabel):
    """
    Un QLabel spécialement conçu pour être centré lorsqu'il est ajouté
    à une QStatusBar avec un facteur d'étirement.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setAlignment(Qt.AlignCenter)

    def setText(self, text):
        super().setText(f" {text} ")

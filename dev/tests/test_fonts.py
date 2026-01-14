#!/usr/bin/env python3
import sys
import os
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QLabel,
    QGridLayout,
)
from PyQt5.QtGui import QFont, QFontDatabase, QFontMetrics, QRawFont
from PyQt5.QtCore import Qt


def load_local_font(filename):
    """Charge une police depuis le répertoire du script sans installation système."""
    # Chemin absolu vers le fichier de police dans le même dossier que ce script
    font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)

    if os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            loaded_families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"✅ Police locale chargée avec succès : {loaded_families}")
        else:
            print(
                f"❌ Erreur : Le fichier {filename} existe mais n'a pas pu être chargé."
            )
    else:
        print(
            f"ℹ️ Aucune police locale '{filename}' trouvée (ceci est normal si vous utilisez les polices système)."
        )


class EmojiTester(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Testeur d'Emojis (Sans Noto Color Emoji)")
        self.resize(1000, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Zone de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        self.grid = QGridLayout(content)

        # 1. Lister toutes les polices sauf Noto Color Emoji
        db = QFontDatabase()
        all_families = db.families()
        self.candidate_fonts = [f for f in all_families if "Noto Color Emoji" not in f]

        print(f"Nombre de polices candidates (hors Noto): {len(self.candidate_fonts)}")

        # Pré-chargement des QRawFont pour optimiser la recherche
        self.raw_fonts = {}
        for family in self.candidate_fonts:
            self.raw_fonts[family] = QRawFont.fromFont(QFont(family))

        # 2. Définir les plages Unicode d'emojis à tester
        # Liste couvrant les principaux blocs d'emojis
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x2600, 0x26FF),  # Misc Symbols
            (0x2700, 0x27BF),  # Dingbats
        ]

        row = 0
        col = 0
        max_cols = 6
        count_found = 0

        # 3. Itérer sur les emojis et trouver une police compatible
        for start, end in emoji_ranges:
            for code in range(start, end + 1):
                char = chr(code)

                found_font = None

                # On cherche la première police qui supporte ce caractère
                for family in self.candidate_fonts:
                    raw = self.raw_fonts.get(family)
                    if raw and raw.isValid() and raw.supportsCharacter(code):
                        found_font = family
                        break

                if found_font:
                    # Création de la cellule d'affichage
                    cell_widget = QWidget()
                    cell_layout = QVBoxLayout(cell_widget)

                    # L'emoji
                    lbl_char = QLabel(char)
                    lbl_char.setAlignment(Qt.AlignCenter)
                    font = QFont(found_font)
                    font.setPointSize(24)
                    # Empêcher le fallback vers Noto ou autre
                    font.setStyleStrategy(QFont.NoFontMerging)
                    lbl_char.setFont(font)

                    # Le nom de la police
                    lbl_name = QLabel(f"{found_font}\nU+{code:X}")
                    lbl_name.setAlignment(Qt.AlignCenter)
                    lbl_name.setStyleSheet("font-size: 10px; color: #555;")

                    cell_layout.addWidget(lbl_char)
                    cell_layout.addWidget(lbl_name)

                    self.grid.addWidget(cell_widget, row, col)

                    count_found += 1
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

        self.statusBar().showMessage(
            f"Terminé. Emojis affichables trouvés : {count_found}"
        )


class LocalEmojiViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualiseur Noto Color Emoji (Local)")
        self.resize(1000, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Zone de défilement
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        self.grid = QGridLayout(content)

        target_font = "Noto Color Emoji"
        raw_font = QRawFont.fromFont(QFont(target_font))

        # 2. Définir les plages Unicode d'emojis à tester
        emoji_ranges = [
            (0x1F600, 0x1F64F),  # Emoticons
            (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
            (0x1F680, 0x1F6FF),  # Transport and Map
            (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
            (0x2600, 0x26FF),  # Misc Symbols
            (0x2700, 0x27BF),  # Dingbats
        ]

        row = 0
        col = 0
        max_cols = 6
        count_found = 0

        for start, end in emoji_ranges:
            for code in range(start, end + 1):
                if raw_font.isValid() and raw_font.supportsCharacter(code):
                    char = chr(code)

                    cell_widget = QWidget()
                    cell_layout = QVBoxLayout(cell_widget)

                    lbl_char = QLabel(char)
                    lbl_char.setAlignment(Qt.AlignCenter)
                    font = QFont(target_font)
                    font.setPointSize(24)
                    font.setStyleStrategy(QFont.NoFontMerging)
                    lbl_char.setFont(font)

                    lbl_name = QLabel(f"U+{code:X}")
                    lbl_name.setAlignment(Qt.AlignCenter)
                    lbl_name.setStyleSheet("font-size: 10px; color: #555;")

                    cell_layout.addWidget(lbl_char)
                    cell_layout.addWidget(lbl_name)

                    self.grid.addWidget(cell_widget, row, col)

                    count_found += 1
                    col += 1
                    if col >= max_cols:
                        col = 0
                        row += 1

        self.statusBar().showMessage(f"Terminé. Emojis Noto trouvés : {count_found}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Charger la police locale une seule fois pour toute l'application
    load_local_font("NotoColorEmoji.ttf")

    window = EmojiTester()
    window2 = LocalEmojiViewer()

    window.show()
    window2.show()

    sys.exit(app.exec_())

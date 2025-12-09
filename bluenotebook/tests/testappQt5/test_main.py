import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QWidget,
    QLabel,
)
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo


class SettingsManager:
    """Classe simplifiée pour lire settings.json."""

    def __init__(self, filename="settings.json"):
        self.settings_path = os.path.join(os.path.dirname(__file__), filename)
        self.settings = self._load()

    def _load(self):
        if os.path.exists(self.settings_path):
            with open(self.settings_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def get(self, key, default=None):
        """Récupère une clé, gère les clés imbriquées comme 'app.language'."""
        try:
            keys = key.split(".")
            value = self.settings
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default


class TestWindow(QMainWindow):
    """Fenêtre de test avec un bouton pour ouvrir un QFileDialog."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test de Basculement de Langue")
        self.setGeometry(300, 300, 400, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.label = QLabel(
            "Cliquez sur le bouton pour ouvrir une boîte de dialogue 'Ouvrir un fichier'.\n"
            "Vérifiez la langue des boutons 'Open' et 'Cancel'."
        )
        self.button = QPushButton("Ouvrir QFileDialog")
        self.button.clicked.connect(self.open_file_dialog)

        layout.addWidget(self.label)
        layout.addWidget(self.button)

    def open_file_dialog(self):
        QFileDialog.getOpenFileName(self, "Ouvrir un fichier")


def main():
    # --- ÉTAPE 1 : Déterminer la langue AVANT de créer QApplication ---
    settings = SettingsManager()
    lang = settings.get("app.language", "fr_FR")  # Français par défaut

    # --- ÉTAPE 2 : Forcer la variable d'environnement ---
    # C'est la méthode la plus robuste pour que Qt s'initialise dans la bonne langue.
    os.environ["LANG"] = f"{lang}.UTF-8"
    print(f"🌍 Variable d'environnement LANG forcée à : {os.environ['LANG']}")

    # --- ÉTAPE 3 : Créer l'application ---
    # Qt va maintenant lire la variable LANG et s'initialiser correctement.
    app = QApplication(sys.argv)

    # --- ÉTAPE 4 : Charger explicitement les traductions standards de Qt ---
    # Bien que LANG soit défini, le chargement explicite est plus robuste
    # pour s'assurer que les fichiers .qm sont bien utilisés.
    locale = QLocale()
    print(f"🌍 Locale Qt effective : {locale.name()}")

    qt_translator = QTranslator()
    qt_translation_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    if qt_translator.load(locale, "qtbase", "_", qt_translation_path):
        app.installTranslator(qt_translator)
        print(
            f"✅ Traduction Qt standard '{locale.name()}' chargée et installée depuis '{qt_translation_path}'."
        )
    else:
        print(
            f"⚠️ Traduction Qt standard pour '{locale.name()}' non trouvée dans '{qt_translation_path}'."
        )

    # --- ÉTAPE 5 : Lancer la fenêtre ---
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

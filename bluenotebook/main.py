#!/usr/bin/env python3
"""
BlueNotebook - Éditeur de texte Markdown avec PyQt5
Point d'entrée principal de l'application
"""

import sys
import os
import locale as locale_module
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo, QCoreApplication
from PyQt5.QtGui import QFont, QFontDatabase
from gui.main_window import MainWindow
from core.settings import SettingsManager
from gui.first_start import FirstStartWindow
from pathlib import Path


def load_local_fonts():
    """Charge les polices locales pour assurer leur disponibilité (Flatpak/Docker)."""
    base_path = os.path.dirname(os.path.abspath(__file__))
    fonts_dir = os.path.join(base_path, "resources", "fonts")

    fonts_to_load = [
        "NotoColorEmoji.ttf",
        "NotoSans-Regular.ttf",
        "NotoSans-Bold.ttf",
        "NotoSans-Italic.ttf",
        "NotoSans-BoldItalic.ttf",
    ]

    if os.path.exists(fonts_dir):
        print(f"📂 Loading local fonts from: {fonts_dir}")
        for font_file in fonts_to_load:
            font_path = os.path.join(fonts_dir, font_file)
            if os.path.exists(font_path):
                font_id = QFontDatabase.addApplicationFont(font_path)
                if font_id != -1:
                    loaded_families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"  ✅ Font loaded: {font_file} -> {loaded_families}")
                else:
                    print(f"  ❌ Error loading font: {font_file}")
    else:
        print(f"ℹ️ Local fonts directory not found: {fonts_dir}")


def detect_environment():
    """Détecte l'environnement d'exécution (natif, Docker, Flatpak, AppImage)."""
    if "FLATPAK_ID" in os.environ or os.path.exists("/.flatpak-info"):
        return "Flatpak"
    if os.path.exists("/.dockerenv"):
        return "Docker"
    if "APPIMAGE" in os.environ and "APPDIR" in os.environ:
        return "AppImage"
    return "Native"


def main():
    """Fonction principale"""

    # --- ÉTAPE 1 : Charger les paramètres SILENCIEUSEMENT (avant QApplication) ---
    settings_manager = SettingsManager()

    # --- ÉTAPE 2 : Déterminer la langue ---
    forced_locale_str = os.getenv("BLUENOTEBOOK_LOCALE")
    settings_language = settings_manager.get("app.language")

    locale_to_set = "en_US"  # Fallback de sécurité

    if settings_language:
        locale_to_set = settings_language
    elif forced_locale_str:
        locale_to_set = forced_locale_str
    else:
        locale_to_set = "en_US"

    # --- ÉTAPE 3 : Forcer LANG AVANT QApplication ---
    os.environ["LANG"] = f"{locale_to_set}.UTF-8"

    # --- ÉTAPE 3bis : Configurer Fontconfig pour Flatpak ---
    # Configure fontconfig to see local fonts (especially Noto Color Emoji)
    # This is necessary because we cannot install fonts system-wide in Flatpak
    # without modifying the manifest.
    if sys.platform == "linux":
        base_path = os.path.dirname(os.path.abspath(__file__))
        fonts_dir = os.path.join(base_path, "resources", "fonts")

        if os.path.exists(fonts_dir):
            import tempfile

            try:
                uid = os.getuid()
            except AttributeError:
                uid = "user"

            font_conf_path = os.path.join(
                tempfile.gettempdir(), f"bluenotebook_fonts_{uid}.conf"
            )

            # Create a minimal fonts.conf that adds our directory and includes system defaults
            xml_content = f"""<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "fonts.dtd">
<fontconfig>
  <dir>{fonts_dir}</dir>
  <include ignore_missing="yes">/etc/fonts/fonts.conf</include>
  <match target="pattern">
    <test qual="any" name="family"><string>sans-serif</string></test>
    <edit name="family" mode="append" binding="weak"><string>Noto Color Emoji</string></edit>
  </match>
  <match target="pattern">
    <test qual="any" name="family"><string>serif</string></test>
    <edit name="family" mode="append" binding="weak"><string>Noto Color Emoji</string></edit>
  </match>
  <match target="pattern">
    <test qual="any" name="family"><string>monospace</string></test>
    <edit name="family" mode="append" binding="weak"><string>Noto Color Emoji</string></edit>
  </match>
</fontconfig>
"""
            try:
                with open(font_conf_path, "w") as f:
                    f.write(xml_content)
                os.environ["FONTCONFIG_FILE"] = font_conf_path
                print(f"✅ Fontconfig configured: {font_conf_path}")
            except Exception as e:
                print(f"⚠️ Failed to configure fontconfig: {e}")

    # --- ÉTAPE 4 : Créer QApplication ---
    app = QApplication(sys.argv)

    # --- ÉTAPE 4bis : Charger les polices locales ---
    load_local_fonts()

    # --- ÉTAPE 5 : Appliquer la police globale AVANT les traductions ---
    app_font_family = settings_manager.get("ui.app_font_family", app.font().family())
    app_font_size = settings_manager.get("ui.app_font_size", app.font().pointSize())
    if app_font_family and app_font_size:
        global_font = QFont(app_font_family, app_font_size)
        app.setFont(global_font)

    # --- ÉTAPE 6 : Charger les traductions Qt standard ---
    locale = QLocale(locale_to_set)

    qt_translator = QTranslator()
    qt_translation_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    if qt_translator.load(locale, "qtbase", "_", qt_translation_path):
        app.installTranslator(qt_translator)
    else:
        # Essayer le chemin système en fallback
        system_qt_path = "/usr/share/qt5/translations"
        if qt_translator.load(locale, "qtbase", "_", system_qt_path):
            app.installTranslator(qt_translator)

    # --- ÉTAPE 7 : Charger les traductions de l'application BlueNotebook ---
    app_translator = QTranslator()
    i18n_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "i18n")

    if app_translator.load(locale, "bluenotebook", "_", i18n_path):
        app.installTranslator(app_translator)

    # --- ÉTAPE 8 : MAINTENANT afficher les messages traduits ---

    print(f"🌍 Locale from settings.json: '{locale_to_set}'")
    print(f"🌍 Variable LANG forced to: {os.environ['LANG']}")
    print(f"🌍 Effective Qt local: {locale.name()}")

    # --- ÉTAPE 9 : Gestion du premier démarrage ---
    if not settings_manager.settings_path.exists():
        print("🚀 First boot - initial setup")
        first_start_window = FirstStartWindow(settings_manager)
        result = first_start_window.exec_()

        if result != QDialog.Accepted:
            print("👋 Configuration cancelled")
            sys.exit(0)

        settings_manager.load_settings()

        new_language = settings_manager.get("app.language")
        if new_language and new_language != locale_to_set:
            print(f"⚠️ Language changed to'{new_language}' - restart recommended")

    # --- ÉTAPE 10 : Configuration locale Python ---
    try:
        locale_str_with_encoding = f"{locale.name()}.UTF-8"
        locale_module.setlocale(locale_module.LC_TIME, locale_str_with_encoding)
        print(f"✅ Python locale (LC_TIME) : '{locale_str_with_encoding}'")
    except locale_module.Error:
        try:
            locale_module.setlocale(locale_module.LC_TIME, locale.name())
            print(f"✅ Python locale(LC_TIME) : '{locale.name()}' (fallback)")

        except locale_module.Error:
            print(f"⚠️ Unable to configure the Python locale for'{locale.name()}'")

    # Afficher messages de chargement des traductions
    if qt_translator.load(locale, "qtbase", "_", qt_translation_path):
        print(
            f"✅ Translation app '{locale.name()}' loaded from'{qt_translation_path}'"
        )
    else:
        print(f"⚠️ Qt translation '{locale.name()}' not found")

    if app_translator.load(locale, "bluenotebook", "_", i18n_path):
        print(f"✅ Translation app  '{locale.name()}' loaded from '{i18n_path}'")

    else:
        print(f"⚠️ Traduction app '{locale.name()}' not found in '{i18n_path}'")

    # --- ÉTAPE 11 : Arguments en ligne de commande ---
    parser = argparse.ArgumentParser(description="BlueNotebook - Journal Markdown")
    parser.add_argument(
        "-j",
        "--journal",
        dest="journal_dir",
        help="Journal directory.",
    )
    args = parser.parse_args()

    try:
        version = "4.2.0"
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion(version)
        app.setOrganizationName("BlueNotebook")

        environment = detect_environment()
        print(f"⚙️ Run-Time environment : {environment}")

        print(f"🚀 Launching BlueNotebook App V{version}...")
        window = MainWindow(journal_dir_arg=args.journal_dir, app_version=version)
        window.show()

        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print(f"👋 Closing the application...")
        sys.exit(0)
    except Exception as e:
        print("❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

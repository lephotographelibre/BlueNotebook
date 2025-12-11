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
from PyQt5.QtGui import QFont
from gui.main_window import MainWindow
from core.settings import SettingsManager
from gui.first_start import FirstStartWindow
from pathlib import Path


class MainContext:
    """Classe pour traduire les messages console de main()."""

    @staticmethod
    def tr(text):
        """Traduction dans le contexte 'MainContext'."""
        return QCoreApplication.translate("MainContext", text)


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

    # --- ÉTAPE 4 : Créer QApplication ---
    app = QApplication(sys.argv)

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
    tr = MainContext.tr

    print(tr("🌍 Locale depuis settings.json : '{0}'").format(locale_to_set))
    print(tr("🌍 Variable LANG forcée à : {0}").format(os.environ["LANG"]))
    print(tr("🌍 Locale Qt effective : {0}").format(locale.name()))

    # --- ÉTAPE 9 : Gestion du premier démarrage ---
    if not settings_manager.settings_path.exists():
        print(tr("🚀 Premier démarrage - configuration initiale"))
        first_start_window = FirstStartWindow(settings_manager)
        result = first_start_window.exec_()

        if result != QDialog.Accepted:
            print(tr("👋 Configuration annulée"))
            sys.exit(0)

        settings_manager.load_settings()

        new_language = settings_manager.get("app.language")
        if new_language and new_language != locale_to_set:
            print(
                tr("⚠️ Langue changée en '{0}' - redémarrage recommandé").format(
                    new_language
                )
            )

    # --- ÉTAPE 10 : Configuration locale Python ---
    try:
        locale_str_with_encoding = f"{locale.name()}.UTF-8"
        locale_module.setlocale(locale_module.LC_TIME, locale_str_with_encoding)
        print(tr("✅ Locale Python (LC_TIME) : '{0}'").format(locale_str_with_encoding))
    except locale_module.Error:
        try:
            locale_module.setlocale(locale_module.LC_TIME, locale.name())
            print(
                tr("✅ Locale Python (LC_TIME) : '{0}' (fallback)").format(
                    locale.name()
                )
            )
        except locale_module.Error:
            print(
                tr("⚠️ Impossible de configurer la locale Python pour '{0}'").format(
                    locale.name()
                )
            )

    # Afficher messages de chargement des traductions
    if qt_translator.load(locale, "qtbase", "_", qt_translation_path):
        print(
            tr("✅ Traduction Qt '{0}' chargée depuis '{1}'").format(
                locale.name(), qt_translation_path
            )
        )
    else:
        print(tr("⚠️ Traduction Qt '{0}' non trouvée").format(locale.name()))

    if app_translator.load(locale, "bluenotebook", "_", i18n_path):
        print(
            tr("✅ Traduction app '{0}' chargée depuis '{1}'").format(
                locale.name(), i18n_path
            )
        )
    else:
        print(
            tr("⚠️ Traduction app '{0}' non trouvée dans '{1}'").format(
                locale.name(), i18n_path
            )
        )

    # --- ÉTAPE 11 : Arguments en ligne de commande ---
    parser = argparse.ArgumentParser(description="BlueNotebook - Journal Markdown")
    parser.add_argument(
        "-j",
        "--journal",
        dest="journal_dir",
        help=tr("Spécifie le répertoire du journal."),
    )
    args = parser.parse_args()

    try:
        version = "4.0.3.1"
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion(version)
        app.setOrganizationName("BlueNotebook")

        print(tr("🚀 Lancement de BlueNotebook V{0}...").format(version))

        window = MainWindow(journal_dir_arg=args.journal_dir, app_version=version)
        window.show()

        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print(tr("👋 Fermeture de l'application..."))
        sys.exit(0)
    except Exception as e:
        print(tr("❌ Erreur: {0}").format(e))
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

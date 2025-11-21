#!/usr/bin/env python3
"""
# Copyright (C) 2025 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
#
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

BlueNotebook - Éditeur de texte Markdown avec PyQt5

Point d'entrée principal de l'application
"""

import sys
import os
import locale as locale_module
import argparse

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo, Qt
from gui.main_window import MainWindow


def main():
    """Fonction principale"""
    # Créer l'application Qt
    app = QApplication(sys.argv)

    # --- Internationalisation (i18n) des composants standards Qt ---
    # Cette section doit être après la création de l'app
    qt_translator = QTranslator()

    # Priorité : variable d'environnement, sinon locale système
    forced_locale_str = os.getenv("BLUENOTEBOOK_LOCALE")
    if forced_locale_str:
        locale = QLocale(forced_locale_str)
        print(f"🌍 Locale forcée par l'environnement : {locale.name()}")
    else:
        locale = QLocale.system()
        print(f"🌍 Locale système détectée : {locale.name()}")

    # --- Configuration de la locale Python standard (pour time, etc.) ---
    # Essayer de définir la locale pour tout le programme Python.
    # Important pour que `locale.getlocale()` fonctionne comme attendu dans les autres modules.
    try:
        locale_str_for_python = forced_locale_str if forced_locale_str else ""
        locale_module.setlocale(locale_module.LC_TIME, locale_str_for_python)
        print(
            f"✅ Locale Python (LC_TIME) configurée sur : '{locale_module.getlocale(locale_module.LC_TIME)[0]}'"
        )
    except locale_module.Error:
        print(
            f"⚠️ Impossible de configurer la locale Python pour '{locale_str_for_python}'. Utilisation de la locale système par défaut."
        )

    # Chemin vers les traductions Qt intégrées
    qt_translation_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    # Charger le fichier de traduction (ex: qtbase_fr.qm)
    if qt_translator.load(locale, "qtbase", "_", qt_translation_path):
        app.installTranslator(qt_translator)
        print(f"✅ Traduction Qt standard '{locale.name()}' chargée.")
    else:
        print(
            f"⚠️ Traduction Qt standard pour '{locale.name()}' non trouvée. Les dialogues système resteront en anglais."
        )

    # Test Grok
    print(f"Chemin des traductions : {qt_translation_path}")

    parser = argparse.ArgumentParser(description="BlueNotebook - Journal Markdown")
    parser.add_argument(
        "-j", "--journal", dest="journal_dir", help="Spécifie le répertoire du journal."
    )
    args = parser.parse_args()

    try:
        # Définir les informations de l'application
        version = "3.3.9"
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion(version)
        app.setOrganizationName("BlueNotebook")

        print(f"🚀 Lancement de l'application BlueNotebook V{version}...")

        # Créer et afficher la fenêtre principale
        window = MainWindow(journal_dir_arg=args.journal_dir, app_version=version)
        window.show()

        # Lancer la boucle d'événements
        sys.exit(app.exec_())

    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

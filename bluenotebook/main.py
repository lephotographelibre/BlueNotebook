#!/usr/bin/env python3
"""
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

BlueNotebook - Éditeur de texte Markdown avec PyQt5

Point d'entrée principal de l'application
"""

import sys
import os
import argparse

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """Fonction principale"""
    parser = argparse.ArgumentParser(description="BlueNotebook - Journal Markdown")
    parser.add_argument(
        "-j", "--journal", dest="journal_dir", help="Spécifie le répertoire du journal."
    )
    args = parser.parse_args()

    try:
        # Créer l'application Qt
        app = QApplication(sys.argv)

        # Définir les informations de l'application
        version = "1.6.9"
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion(version)
        app.setOrganizationName("BlueNotebook")

        print(f"*** Lancement de l'application BlueNotebook V{version} ***")

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

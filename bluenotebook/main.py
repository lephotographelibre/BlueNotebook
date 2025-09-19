#!/usr/bin/env python3
"""
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
    parser = argparse.ArgumentParser(description="BlueNotebook - Éditeur Markdown")
    parser.add_argument(
        "-j", "--journal", dest="journal_dir", help="Spécifie le répertoire du journal."
    )
    args = parser.parse_args()

    try:
        # Créer l'application Qt
        app = QApplication(sys.argv)

        # Définir les informations de l'application
        version = "1.1.6"
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

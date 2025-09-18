#!/usr/bin/env python3
"""
BlueNotebook - Éditeur de texte Markdown avec PyQt5
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        # Créer l'application Qt
        app = QApplication(sys.argv)
        app.setApplicationName("BlueNotebook")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("BlueNotebook")
        
        # Créer et afficher la fenêtre principale
        window = MainWindow()
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

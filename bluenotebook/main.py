#!/usr/bin/env python3
"""
Éditeur de texte Markdown BlueNotebook
Point d'entrée principal de l'application
"""

import sys
import os

# Ajouter le répertoire racine au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    """Fonction principale"""
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Fermeture de l'application...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Erreur: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

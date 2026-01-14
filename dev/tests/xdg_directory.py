# test xdg directory
# pip install xdg_base_dirs platformdirs

import os
from pathlib import Path
import platformdirs

from xdg_base_dirs import (
    xdg_cache_home,
    xdg_config_dirs,
    xdg_config_home,
    xdg_data_dirs,
    xdg_data_home,
    xdg_runtime_dir,
    xdg_state_home,
)


def main():
    print("=== Répertoire 'Home' de l'utilisateur ===")
    # La méthode moderne et recommandée avec pathlib
    print(f"Home (via pathlib) : {Path.home()}")
    # La méthode classique avec le module os
    print(f"Home (via os)      : {os.path.expanduser('~')}")
    print("-" * 40)

    print("=== Répertoires XDG Base Directory ===")

    # Répertoires utilisateur uniques (Single paths)
    print(f"XDG_DATA_HOME   (Données utilisateur) : {xdg_data_home()}")
    print(f"XDG_CONFIG_HOME (Configuration)       : {xdg_config_home()}")
    print(f"XDG_STATE_HOME  (État application)    : {xdg_state_home()}")
    print(f"XDG_CACHE_HOME  (Cache)               : {xdg_cache_home()}")

    # Runtime dir (peut ne pas être défini ou lever une erreur si non sécurisé)
    try:
        print(f"XDG_RUNTIME_DIR (Fichiers temporaires): {xdg_runtime_dir()}")
    except Exception as e:
        print(f"XDG_RUNTIME_DIR (Fichiers temporaires): Non disponible ({e})")

    # Listes de répertoires (système + utilisateur)
    print("\nXDG_DATA_DIRS (Recherche de données) :")
    for path in xdg_data_dirs():
        print(f"  - {path}")

    print("\nXDG_CONFIG_DIRS (Recherche de configuration) :")
    for path in xdg_config_dirs():
        print(f"  - {path}")

    print("\n=== Répertoires Utilisateur Standard (via platformdirs) ===")
    # Ces répertoires correspondent à la spécification XDG User Directories sur Linux
    print(f"Documents       : {platformdirs.user_documents_dir()}")
    print(f"Téléchargements : {platformdirs.user_downloads_dir()}")
    print(f"Images          : {platformdirs.user_pictures_dir()}")
    print(f"Musique         : {platformdirs.user_music_dir()}")
    print(f"Vidéos          : {platformdirs.user_videos_dir()}")
    print(f"Bureau          : {platformdirs.user_desktop_dir()}")


if __name__ == "__main__":
    main()

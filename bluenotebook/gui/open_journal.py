"""
# Copyright (C) 2026 Jean-Marc DIGNE
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

Module de gestion de l'ouverture et du changement de journal."""

import zipfile
from pathlib import Path
from datetime import datetime

from PyQt5.QtWidgets import (
    QFileDialog,
    QMessageBox,
    QDialog,
    QProgressDialog,
)
from PyQt5.QtCore import Qt, QCoreApplication

from .new_journal_dialog import NewJournalDialog


class OpenJournalContext:
    """Classe de contexte pour les traductions dans open_journal.py"""

    @staticmethod
    def tr(text):
        return QCoreApplication.translate("OpenJournalContext", text)


def validate_journal_structure(journal_path):
    """Valide si un répertoire contient une structure de journal valide.

    Args:
        journal_path (Path): Chemin du répertoire à valider

    Returns:
        dict: Informations de validation
            - 'is_valid': bool - True si journal valide
            - 'is_empty': bool - True si répertoire vide
            - 'has_subdirs': bool - True si a notes/, images/, etc.
            - 'missing_subdirs': list - Sous-répertoires manquants
    """
    # Vérifier que le chemin existe et est un répertoire
    if not journal_path.exists() or not journal_path.is_dir():
        return {
            "is_valid": False,
            "is_empty": True,
            "has_subdirs": False,
            "missing_subdirs": ["notes", "images", "attachments", "gpx"],
        }

    # Vérifier si le répertoire est vide
    try:
        is_empty = not any(journal_path.iterdir())
    except PermissionError:
        is_empty = False

    # Sous-répertoires requis
    required_subdirs = ["notes", "images", "attachments", "gpx"]
    missing_subdirs = []
    has_all_subdirs = True

    for subdir in required_subdirs:
        subdir_path = journal_path / subdir
        if not subdir_path.exists() or not subdir_path.is_dir():
            missing_subdirs.append(subdir)
            has_all_subdirs = False

    # Vérifier s'il y a des fichiers .md à la racine (optionnel)
    has_md_files = any(journal_path.glob("*.md"))

    # Un journal est considéré valide s'il a tous les sous-répertoires
    # OU s'il a au moins des fichiers .md et certains sous-répertoires
    is_valid = has_all_subdirs or (has_md_files and len(missing_subdirs) < 3)

    return {
        "is_valid": is_valid,
        "is_empty": is_empty,
        "has_subdirs": has_all_subdirs,
        "missing_subdirs": missing_subdirs,
    }


def create_empty_journal(main_window, journal_path):
    """Crée la structure de répertoires pour un nouveau journal vide.

    Args:
        main_window: Instance de MainWindow
        journal_path (Path): Chemin du répertoire du journal à créer

    Returns:
        bool: True si création réussie, False sinon
    """
    try:
        # Créer le répertoire principal
        journal_path.mkdir(parents=True, exist_ok=True)

        # Créer les sous-répertoires requis
        for sub_dir in ["notes", "images", "attachments", "gpx"]:
            (journal_path / sub_dir).mkdir(exist_ok=True)

        return True

    except Exception as e:
        message = OpenJournalContext.tr(
            "Impossible de créer le répertoire du journal :\n{error}"
        )
        message = message.format(error=str(e))
        QMessageBox.critical(main_window, OpenJournalContext.tr("Erreur"), message)
        return False


def import_journal_from_backup(main_window, journal_path, backup_zip):
    """Importe un journal depuis une archive ZIP de backup.

    Args:
        main_window: Instance de MainWindow
        journal_path (Path): Chemin du répertoire de destination
        backup_zip (Path): Chemin du fichier ZIP de backup

    Returns:
        bool: True si import réussi, False sinon
    """
    try:
        # Vérifier que le fichier ZIP existe
        if not backup_zip.exists():
            message = OpenJournalContext.tr(
                "Le fichier de sauvegarde n'existe pas :\n{path}"
            )
            message = message.format(path=str(backup_zip))
            QMessageBox.critical(main_window, OpenJournalContext.tr("Erreur"), message)
            return False

        # Vérifier que le ZIP est valide
        if not zipfile.is_zipfile(backup_zip):
            message = OpenJournalContext.tr(
                "Le fichier sélectionné n'est pas une archive ZIP valide :\n{path}"
            )
            message = message.format(path=backup_zip.name)
            QMessageBox.critical(main_window, OpenJournalContext.tr("Erreur"), message)
            return False

        # Créer le répertoire de destination s'il n'existe pas
        journal_path.mkdir(parents=True, exist_ok=True)

        # Extraire le contenu du ZIP
        with zipfile.ZipFile(backup_zip, "r") as zip_ref:
            # Afficher une boîte de dialogue de progression
            progress = QProgressDialog(
                OpenJournalContext.tr("Extraction du journal en cours..."),
                OpenJournalContext.tr("Annuler"),
                0,
                len(zip_ref.namelist()),
                main_window,
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setMinimumDuration(0)

            for i, file_info in enumerate(zip_ref.infolist()):
                if progress.wasCanceled():
                    QMessageBox.warning(
                        main_window,
                        OpenJournalContext.tr("Import annulé"),
                        OpenJournalContext.tr(
                            "L'import du journal a été annulé par l'utilisateur."
                        ),
                    )
                    return False

                zip_ref.extract(file_info, journal_path)
                progress.setValue(i + 1)

            progress.close()

        # Afficher un message de succès
        message = OpenJournalContext.tr(
            "Journal importé avec succès depuis :\n{backup_file}\n\n"
            "Destination : {journal_path}"
        )
        message = message.format(
            backup_file=backup_zip.name, journal_path=str(journal_path)
        )
        QMessageBox.information(
            main_window, OpenJournalContext.tr("Import réussi"), message
        )

        return True

    except Exception as e:
        message = OpenJournalContext.tr("Erreur lors de l'import du journal :\n{error}")
        message = message.format(error=str(e))
        QMessageBox.critical(main_window, OpenJournalContext.tr("Erreur"), message)
        return False


def prompt_for_today_note(main_window):
    """Ouvre la note du jour si elle existe, sinon propose de la créer.

    Args:
        main_window: Instance de MainWindow
    """
    today_str = datetime.now().strftime("%Y%m%d")
    today_note_path = main_window.journal_directory / f"{today_str}.md"

    if today_note_path.exists():
        # La note du jour existe : l'ouvrir automatiquement
        main_window.open_specific_file(str(today_note_path))
    else:
        # La note du jour n'existe pas : proposer de la créer
        reply = QMessageBox.question(
            main_window,
            OpenJournalContext.tr("Note du jour"),
            OpenJournalContext.tr(
                "La note du jour n'existe pas. Voulez-vous la créer ?"
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes,
        )
        if reply == QMessageBox.Yes:
            main_window.new_file()


def switch_to_journal(main_window, journal_path):
    """Bascule vers un nouveau répertoire de journal et met à jour tous les composants.

    Args:
        main_window: Instance de MainWindow
        journal_path (Path): Chemin du nouveau journal
    """
    # 1. Mettre à jour le répertoire de journal
    main_window.journal_directory = journal_path

    # 2. Mettre à jour le label dans la barre d'état
    main_window.update_journal_dir_label()

    # 3. Vider l'éditeur et la prévisualisation
    main_window.editor.set_text("")
    main_window.current_file = None
    main_window.is_modified = False
    main_window.update_title()
    main_window.update_preview()

    # 4. Mettre à jour le panneau notes avec le nouveau journal
    main_window.notes_panel.set_journal_directory(main_window.journal_directory)

    # 5. Vider les résultats de recherche de l'ancien journal
    main_window.navigation_panel.search_results_panel.update_results([], "")

    # 6. Lancer l'indexation pour le nouveau journal
    main_window.start_initial_indexing()

    # 7. Mettre à jour les highlights du calendrier
    main_window.update_calendar_highlights()

    # 8. Mettre à jour le nuage de tags
    main_window.update_tag_cloud()

    # 9. Mettre à jour les données du panneau navigation
    main_window.update_navigation_panel_data()

    # 10. Sauvegarder le chemin du journal dans les settings
    main_window.settings_manager.set(
        "journal.directory", str(main_window.journal_directory)
    )
    main_window.settings_manager.save_settings()

    # 11. Proposer de créer la note du jour
    prompt_for_today_note(main_window)

    # 12. Afficher message de confirmation
    message = OpenJournalContext.tr(
        "Journal ouvert avec succès :\n{journal_path}\n\n"
        "L'indexation des tags est en cours..."
    )
    message = message.format(journal_path=str(main_window.journal_directory))
    QMessageBox.information(main_window, OpenJournalContext.tr("Journal"), message)


def open_journal(main_window):
    """Ouvre un dialogue pour sélectionner un nouveau répertoire de journal.

    Args:
        main_window: Instance de MainWindow
    """
    # 1. Sauvegarder l'éditeur en cours
    if not main_window.check_save_changes():
        return  # Utilisateur a annulé la sauvegarde

    # 2. Dialogue de sélection de répertoire
    dir_name = QFileDialog.getExistingDirectory(
        main_window, OpenJournalContext.tr("Sélectionner le répertoire du Journal")
    )
    if not dir_name:
        return  # Utilisateur a annulé la sélection

    new_journal_path = Path(dir_name).resolve()

    # 3. Validation de la structure du journal
    validation = validate_journal_structure(new_journal_path)

    # 4. Si journal valide : ouvrir directement
    if validation["is_valid"]:
        switch_to_journal(main_window, new_journal_path)
        return

    # 5. Sinon : dialogue de création/import
    dialog = NewJournalDialog(new_journal_path, main_window)
    if dialog.exec_() != QDialog.Accepted:
        return  # Utilisateur a annulé

    choice, backup_path = dialog.get_selection()

    # 6a. Créer un journal vide
    if choice == "create_empty":
        if not create_empty_journal(main_window, new_journal_path):
            return  # Échec de la création
        switch_to_journal(main_window, new_journal_path)

    # 6b. Importer depuis un backup
    elif choice == "import_backup":
        if not import_journal_from_backup(main_window, new_journal_path, backup_path):
            return  # Échec de l'import
        switch_to_journal(main_window, new_journal_path)

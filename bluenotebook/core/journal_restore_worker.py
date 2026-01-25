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
"""

import os
import zipfile
import shutil
from pathlib import Path
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot, QCoreApplication


class JournalRestoreContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("JournalRestoreContext", text)


class JournalRestoreWorker(QRunnable):
    """
    Worker asynchrone pour la restauration du journal depuis une archive ZIP.

    Fonctionnalités :
    - Validation de l'intégrité de l'archive
    - Sauvegarde de sécurité du journal actuel
    - Extraction dans un dossier temporaire
    - Fusion intelligente ou remplacement complet
    - Rapports de progression détaillés
    """

    class Signals(QObject):
        progress = pyqtSignal(int, str)  # percentage, message
        finished = pyqtSignal(str)  # summary message
        error = pyqtSignal(str)

    def __init__(self, zip_path: Path, journal_directory: Path, merge_strategy: str):
        super().__init__()
        self.zip_path = zip_path
        self.journal_directory = journal_directory
        self.merge_strategy = merge_strategy  # "smart_merge" or "replace"
        self.signals = self.Signals()

        self.temp_extract_dir = None
        self.backup_dir = None

    @pyqtSlot()
    def run(self):
        """Exécute la restauration dans un thread séparé."""
        try:
            # Phase 1: Validation (0-10%)
            self._emit_progress(
                0, JournalRestoreContext.tr("Validation de l'archive...")
            )
            self._validate_archive()

            # Phase 2: Backup current journal (10-30%)
            self._emit_progress(
                10, JournalRestoreContext.tr("Sauvegarde du journal actuel...")
            )
            self._backup_current_journal()

            # Phase 3: Extract archive (30-70%)
            self._emit_progress(
                30, JournalRestoreContext.tr("Extraction de l'archive...")
            )
            self._extract_archive()

            # Phase 4: Merge or replace (70-95%)
            if self.merge_strategy == "smart_merge":
                self._emit_progress(
                    70, JournalRestoreContext.tr("Fusion intelligente...")
                )
                merge_report = self._smart_merge()
            else:
                self._emit_progress(
                    70, JournalRestoreContext.tr("Remplacement complet...")
                )
                merge_report = self._full_replace()

            # Phase 5: Finalize (95-100%)
            self._emit_progress(95, JournalRestoreContext.tr("Finalisation..."))
            self._cleanup()

            self._emit_progress(100, JournalRestoreContext.tr("Restauration terminée"))

            # Create summary message
            summary = self._create_summary(merge_report)
            self.signals.finished.emit(summary)

        except Exception as e:
            self._cleanup_on_error()

            error_msg = JournalRestoreContext.tr(
                "La restauration a échoué : {error}"
            ).format(error=str(e))

            self.signals.error.emit(error_msg)

    def _emit_progress(self, percentage: int, message: str):
        """Helper pour émettre les signaux de progression."""
        self.signals.progress.emit(percentage, message)

    def _validate_archive(self):
        """Valide l'intégrité du fichier ZIP et son contenu."""
        # Test ZIP integrity
        with zipfile.ZipFile(self.zip_path, "r") as zipf:
            bad_file = zipf.testzip()
            if bad_file:
                error_msg = JournalRestoreContext.tr(
                    "Archive corrompue : fichier {file} invalide"
                ).format(file=bad_file)
                raise Exception(error_msg)

            # Check for .md files
            file_list = zipf.namelist()
            md_files = [f for f in file_list if f.endswith(".md")]

            if not md_files:
                # Warn but allow (might be empty journal)
                print(f"⚠️ No .md files found in archive {self.zip_path}")

    def _backup_current_journal(self):
        """Crée une sauvegarde de sécurité du journal actuel."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_dir = Path(f"{self.journal_directory}.bak-{timestamp}")

        # Use shutil.copytree for efficient directory copy
        shutil.copytree(self.journal_directory, self.backup_dir)
        print(f"💾 Safety backup created: {self.backup_dir}")

    def _extract_archive(self):
        """Extrait l'archive dans un répertoire temporaire."""
        self.temp_extract_dir = (
            self.journal_directory.parent
            / f".restore_temp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )
        self.temp_extract_dir.mkdir(exist_ok=True)

        with zipfile.ZipFile(self.zip_path, "r") as zipf:
            total_files = len(zipf.namelist())
            for i, file in enumerate(zipf.namelist()):
                zipf.extract(file, self.temp_extract_dir)
                # Update progress within extraction phase (30-70%)
                progress = 30 + int((i / total_files) * 40)
                self._emit_progress(
                    progress,
                    JournalRestoreContext.tr("Extraction : {current}/{total}").format(
                        current=i + 1, total=total_files
                    ),
                )

        print(f"📂 Extracted {total_files} files to temp dir: {self.temp_extract_dir}")

    def _smart_merge(self) -> dict:
        """
        Stratégie de fusion intelligente :
        - Les nouveaux fichiers .md de l'archive sont ajoutés
        - Les fichiers existants sont préservés
        - Conflits : le fichier archive est renommé avec .restored
        """
        report = {"added": [], "kept": [], "renamed": []}

        # Walk through extracted files
        for root, dirs, files in os.walk(self.temp_extract_dir):
            for file in files:
                src_file = Path(root) / file
                rel_path = src_file.relative_to(self.temp_extract_dir)
                dest_file = self.journal_directory / rel_path

                if not dest_file.exists():
                    # New file: copy it
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_file, dest_file)
                    report["added"].append(str(rel_path))
                else:
                    # File exists: check if it's a .md file
                    if file.endswith(".md"):
                        # Keep current, save archive version as .restored
                        restored_name = dest_file.stem + ".restored" + dest_file.suffix
                        restored_path = dest_file.parent / restored_name
                        shutil.copy2(src_file, restored_path)
                        report["renamed"].append(str(rel_path))
                    else:
                        # Non-md files: keep current
                        report["kept"].append(str(rel_path))

        print(
            f"✅ Smart merge completed: {len(report['added'])} added, {len(report['renamed'])} conflicts, {len(report['kept'])} kept"
        )
        return report

    def _full_replace(self) -> dict:
        """
        Stratégie de remplacement complet :
        - Suppression du contenu du journal actuel
        - Copie de tous les fichiers de l'archive
        """
        report = {"replaced": []}

        # Clear current journal (except backup)
        for item in self.journal_directory.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)

        # Copy all files from temp extract
        for root, dirs, files in os.walk(self.temp_extract_dir):
            for file in files:
                src_file = Path(root) / file
                rel_path = src_file.relative_to(self.temp_extract_dir)
                dest_file = self.journal_directory / rel_path

                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
                report["replaced"].append(str(rel_path))

        print(f"✅ Full replace completed: {len(report['replaced'])} files replaced")
        return report

    def _cleanup(self):
        """Nettoyage du répertoire temporaire d'extraction."""
        if self.temp_extract_dir and self.temp_extract_dir.exists():
            shutil.rmtree(self.temp_extract_dir)
            print(f"🧹 Cleanup completed: removed {self.temp_extract_dir}")

    def _cleanup_on_error(self):
        """Nettoyage en cas d'erreur."""
        self._cleanup()

        # If backup exists and current journal is corrupted, user should manually recover
        # We don't auto-restore to avoid potential data loss
        if self.backup_dir and self.backup_dir.exists():
            print(f"❌ Restore failed. Backup preserved at: {self.backup_dir}")

    def _create_summary(self, report: dict) -> str:
        """Crée un résumé lisible de la restauration."""
        if self.merge_strategy == "smart_merge":
            message = JournalRestoreContext.tr(
                "Fusion intelligente terminée :\n"
                "- {added} fichier(s) ajouté(s)\n"
                "- {renamed} conflit(s) résolu(s) (.restored)\n"
                "- {kept} fichier(s) préservé(s)\n\n"
                "Sauvegarde de sécurité : {backup}"
            )
            return message.format(
                added=len(report["added"]),
                renamed=len(report["renamed"]),
                kept=len(report["kept"]),
                backup=str(self.backup_dir),
            )
        else:
            message = JournalRestoreContext.tr(
                "Remplacement complet terminé :\n"
                "- {replaced} fichier(s) restauré(s)\n\n"
                "Sauvegarde de sécurité : {backup}"
            )
            return message.format(
                replaced=len(report["replaced"]), backup=str(self.backup_dir)
            )

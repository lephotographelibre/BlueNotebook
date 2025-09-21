"""
Module pour l'indexation asynchrone des tags dans le journal.
"""

import os
import re
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


class IndexerSignals(QObject):
    """
    Définit les signaux disponibles pour un QRunnable.
    Hériter de QObject est nécessaire pour la définition des signaux.
    """

    finished = pyqtSignal(int)  # Signal émis à la fin, avec le nombre de tags uniques


class TagIndexer(QRunnable):
    """
    Worker QRunnable qui scanne les fichiers d'un répertoire de journal,
    extrait les tags et crée un fichier d'index.
    """

    def __init__(self, journal_directory: Path):
        super().__init__()
        self.journal_directory = journal_directory
        self.signals = IndexerSignals()
        # Regex pour trouver les tags @@tag et capturer les 40 caractères suivants
        self.tag_pattern = re.compile(r"(@@\w{2,})\b(.{0,40})")

    @pyqtSlot()
    def run(self):
        """
        Logique d'indexation exécutée dans le thread.
        """
        if not self.journal_directory or not self.journal_directory.is_dir():
            self.signals.finished.emit(0)
            return

        all_tags_data = []
        unique_tags = set()

        try:
            # Parcourir tous les fichiers .md du répertoire
            for file_path in self.journal_directory.glob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line in f:
                            for match in self.tag_pattern.finditer(line):
                                tag = match.group(1)
                                context = match.group(2).strip()
                                filename = file_path.name

                                # Stocker les données formatées
                                all_tags_data.append(f"{tag}++{context}++{filename}")
                                unique_tags.add(tag)
                except Exception:
                    # Ignorer les fichiers qui ne peuvent pas être lus
                    continue

            if not all_tags_data:
                self.signals.finished.emit(0)
                return

            # Trier la liste par ordre alphabétique des tags
            all_tags_data.sort()

            # Gérer le fichier d'index
            index_file_path = self.journal_directory / "index_tags.txt"

            # Sauvegarder l'ancien index s'il existe
            if index_file_path.exists():
                backup_path = self.journal_directory / "index_tags.txt.SAVE"
                try:
                    # Renommer est plus sûr et atomique
                    index_file_path.rename(backup_path)
                except OSError:
                    # Si le renommage échoue (ex: permissions), on ignore
                    pass

            # Écrire le nouvel index
            with open(index_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(all_tags_data))

            # Émettre le signal de fin avec le nombre de tags uniques
            self.signals.finished.emit(len(unique_tags))

        except Exception as e:
            print(f"❌ Erreur lors de l'indexation des tags : {e}")
            self.signals.finished.emit(-1)  # Émettre -1 en cas d'erreur


def start_tag_indexing(journal_directory, pool, on_finished):
    """Fonction utilitaire pour démarrer l'indexation."""
    if journal_directory:
        print(f"🚀 Lancement de l'indexation des tags pour : {journal_directory}")
        indexer = TagIndexer(journal_directory)
        indexer.signals.finished.connect(on_finished)
        pool.start(indexer)

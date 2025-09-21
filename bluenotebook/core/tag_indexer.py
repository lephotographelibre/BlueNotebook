"""
Module pour l'indexation asynchrone des tags dans le journal.
"""

import os
import csv
import json
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

        all_tags_info = []
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

                                # Stocker les données structurées
                                all_tags_info.append(
                                    {
                                        "tag": tag,
                                        "context": context,
                                        "filename": filename,
                                    }
                                )
                                unique_tags.add(tag)
                except Exception:
                    # Ignorer les fichiers qui ne peuvent pas être lus
                    continue

            if not all_tags_info:
                self.signals.finished.emit(0)
                return

            # Trier la liste par ordre alphabétique des tags
            all_tags_info.sort(key=lambda x: x["tag"])

            self._write_text_index(all_tags_info)
            self._write_csv_index(all_tags_info)
            self._write_json_index(all_tags_info)

            # Émettre le signal de fin avec le nombre de tags uniques
            self.signals.finished.emit(len(unique_tags))

        except Exception as e:
            print(f"❌ Erreur lors de l'indexation des tags : {e}")
            self.signals.finished.emit(-1)  # Émettre -1 en cas d'erreur

    def _write_text_index(self, all_tags_info):
        """Écrit l'index au format texte simple."""
        index_file_path = self.journal_directory / "index_tags.txt"
        if index_file_path.exists():
            backup_path = self.journal_directory / "index_tags.txt.SAVE"
            try:
                index_file_path.rename(backup_path)
            except OSError:
                pass

        all_tags_data = [
            f"{info['tag']}++{info['context']}++{info['filename']}"
            for info in all_tags_info
        ]
        with open(index_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_tags_data))

    def _write_csv_index(self, all_tags_info):
        """Écrit l'index au format CSV."""
        index_file_path = self.journal_directory / "index_tags.csv"
        if index_file_path.exists():
            backup_path = self.journal_directory / "index_tags.csv.SAVE"
            try:
                index_file_path.rename(backup_path)
            except OSError:
                pass

        with open(index_file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["tag", "context", "filename"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_tags_info)

    def _write_json_index(self, all_tags_info):
        """Écrit l'index au format JSON."""
        index_file_path = self.journal_directory / "index_tags.json"
        if index_file_path.exists():
            backup_path = self.journal_directory / "index_tags.json.SAVE"
            try:
                index_file_path.rename(backup_path)
            except OSError:
                pass

        json_data = {}
        for info in all_tags_info:
            tag = info["tag"]
            if tag not in json_data:
                json_data[tag] = {"occurrences": 0, "details": []}

            # Extraire et formater la date depuis le nom de fichier
            date_str = ""
            filename_base = Path(info["filename"]).stem  # ex: "20240928"
            if len(filename_base) == 8 and filename_base.isdigit():
                year = filename_base[0:4]
                month = filename_base[4:6]
                day = filename_base[6:8]
                date_str = f"{year}-{month}-{day}"  # Format ISO 8601

            json_data[tag]["details"].append(
                {
                    "context": info["context"],
                    "filename": info["filename"],
                    "date": date_str,
                }
            )
            json_data[tag]["occurrences"] += 1

        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def start_tag_indexing(journal_directory, pool, on_finished):
    """Fonction utilitaire pour démarrer l'indexation."""
    if journal_directory:
        print(f"🚀 Lancement de l'indexation des tags pour : {journal_directory}")
        indexer = TagIndexer(journal_directory)
        indexer.signals.finished.connect(on_finished)
        pool.start(indexer)

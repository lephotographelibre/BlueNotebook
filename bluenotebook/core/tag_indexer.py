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


Module pour l'indexation asynchrone des tags dans le journal.
"""

import os
import csv
import json
import re
import unicodedata
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
        # Regex pour trouver les tags @@tag et capturer le reste de la ligne comme contexte
        self.tag_pattern = re.compile(r"(@@\w{2,})\b(.*)")

    @pyqtSlot()
    def run(self):
        """
        Logique d'indexation exécutée dans le thread.
        """
        if not self.journal_directory or not self.journal_directory.is_dir():
            self.signals.finished.emit(0)
            return

        index_file_path = self.journal_directory / "index_tags.json"
        last_index_time = 0
        if index_file_path.exists():
            last_index_time = index_file_path.stat().st_mtime

        # Vérifier si des fichiers ont été modifiés depuis la dernière indexation
        files_to_process = [
            p
            for p in self.journal_directory.glob("*.md")
            if p.stat().st_mtime > last_index_time
        ]

        if not files_to_process and index_file_path.exists():
            try:
                with open(index_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                self.signals.finished.emit(len(existing_data))
                return
            except (json.JSONDecodeError, IOError):
                pass  # En cas d'erreur, on réindexe tout

        all_tags_info = []
        unique_tags = set()

        try:
            # Parcourir tous les fichiers .md du répertoire
            for file_path in self.journal_directory.glob("*.md"):
                try:
                    line_number = 0
                    with open(file_path, "r", encoding="utf-8") as f:
                        for line_number, line in enumerate(f, 1):
                            for match in self.tag_pattern.finditer(line):
                                original_tag = match.group(1)
                                context = match.group(2).strip()

                                # Normaliser le tag : suppression des accents et passage en majuscules
                                # pour regrouper @@météo, @@Météo, @@METEO sous @@METEO.
                                tag_body = original_tag[
                                    2:
                                ]  # Extrait "météo" de "@@météo"
                                nfkd_form = unicodedata.normalize("NFKD", tag_body)
                                without_accents = "".join(
                                    [
                                        c
                                        for c in nfkd_form
                                        if not unicodedata.combining(c)
                                    ]
                                )
                                normalized_tag = f"@@{without_accents.upper()}"

                                # Stocker les données structurées
                                all_tags_info.append(
                                    {
                                        "tag": normalized_tag,
                                        "context": context,
                                        "filename": file_path.name,
                                        "line": line_number,
                                    }
                                )
                                unique_tags.add(normalized_tag)
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
            print(f"❌ Error indexing tags: {e}")
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
            fieldnames = ["tag", "context", "filename", "line"]
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
                    "line": info["line"],
                }
            )
            json_data[tag]["occurrences"] += 1

        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def start_tag_indexing(journal_directory, pool, on_finished):
    """Fonction utilitaire pour démarrer l'indexation."""
    if journal_directory:
        print(f"🚀 Tag indexing has begun for: {journal_directory}")
        indexer = TagIndexer(journal_directory)
        indexer.signals.finished.connect(on_finished)
        pool.start(indexer)

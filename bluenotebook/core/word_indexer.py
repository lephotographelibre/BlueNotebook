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


Module pour l'indexation asynchrone des mots du journal.
"""

import re
import json
import csv
from pathlib import Path
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable, pyqtSlot


class WordIndexerSignals(QObject):
    """Définit les signaux pour le WordIndexer."""

    finished = pyqtSignal(int)


class WordIndexer(QRunnable):
    """
    Worker QRunnable qui scanne les fichiers, extrait les mots pertinents
    et crée des fichiers d'index (JSON, CSV).
    """

    def __init__(self, journal_directory: Path, excluded_words: set):
        super().__init__()
        self.journal_directory = journal_directory
        self.signals = WordIndexerSignals()
        self.excluded_words = excluded_words
        # Regex pour trouver les mots, en ignorant les tags @@
        self.word_pattern = re.compile(r"\b(?<!@@)\w{3,}\b")

    @pyqtSlot()
    def run(self):
        """Logique d'indexation exécutée dans le thread."""
        if not self.journal_directory or not self.journal_directory.is_dir():
            self.signals.finished.emit(0)
            return

        index_file_path = self.journal_directory / "index_words.json"
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
            # Pas de nouveaux fichiers à traiter, on peut charger le compte existant
            try:
                with open(index_file_path, "r", encoding="utf-8") as f:
                    existing_data = json.load(f)
                self.signals.finished.emit(len(existing_data))
                return
            except (json.JSONDecodeError, IOError):
                pass  # En cas d'erreur, on réindexe tout

        all_words_info = []
        unique_words = set()

        try:
            for file_path in self.journal_directory.glob("*.md"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read().lower()
                        # Utiliser finditer pour obtenir des objets match avec les positions
                        for match in self.word_pattern.finditer(content):
                            word = match.group(0)

                            # Exclure les mots qui ne contiennent aucune lettre (ex: "123", "___")
                            # ou qui sont dans la liste d'exclusion.
                            if (
                                not any(c.isalpha() for c in word)
                                or word in self.excluded_words
                            ):
                                continue

                            # Calculer le numéro de ligne
                            line_number = content.count("\n", 0, match.start()) + 1

                            # Capturer les 40 caractères qui suivent le mot
                            context_start = match.end()
                            raw_context = content[context_start : context_start + 40]
                            # Nettoyer le contexte (supprimer les sauts de ligne) et l'ajouter au mot
                            context = (
                                word + " " + raw_context.replace("\n", " ")
                            ).strip()

                            all_words_info.append(
                                {
                                    "word": word,
                                    "context": context,
                                    "filename": file_path.name,
                                    "line": line_number,
                                }
                            )
                            unique_words.add(word)
                except Exception:
                    continue

            if not all_words_info:
                self.signals.finished.emit(0)
                return

            all_words_info.sort(key=lambda x: x["word"])

            self._write_csv_index(all_words_info)
            self._write_json_index(all_words_info)

            self.signals.finished.emit(len(unique_words))

        except Exception as e:
            print(f"❌ Erreur lors de l'indexation des mots : {e}")
            self.signals.finished.emit(-1)

    def _write_csv_index(self, all_words_info):
        """Écrit l'index au format CSV."""
        index_file_path = self.journal_directory / "index_words.csv"
        with open(index_file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["word", "context", "filename", "line"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_words_info)

    def _write_json_index(self, all_words_info):
        """Écrit l'index au format JSON."""
        index_file_path = self.journal_directory / "index_words.json"
        json_data = {}
        for info in all_words_info:
            word = info["word"]
            if word not in json_data:
                json_data[word] = {"occurrences": 0, "details": []}

            date_str = ""
            filename_base = Path(info["filename"]).stem
            if len(filename_base) == 8 and filename_base.isdigit():
                date_str = (
                    f"{filename_base[0:4]}-{filename_base[4:6]}-{filename_base[6:8]}"
                )

            json_data[word]["details"].append(
                {
                    "context": info["context"],
                    "filename": info["filename"],
                    "date": date_str,
                    "line": info["line"],
                }
            )
            json_data[word]["occurrences"] += 1

        with open(index_file_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)


def start_word_indexing(journal_directory, excluded_words, pool, on_finished):
    """Fonction utilitaire pour démarrer l'indexation des mots."""
    if journal_directory:
        print(f"🚀 Lancement de l'indexation des mots pour : {journal_directory}")
        indexer = WordIndexer(journal_directory, excluded_words)
        indexer.signals.finished.connect(on_finished)
        pool.start(indexer)

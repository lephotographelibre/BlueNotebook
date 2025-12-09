#!/usr/bin/env python3
"""
# Copyright (C) 2025 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
#
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

BlueNotebook - Éditeur de texte Markdown avec PyQt5

wrap_strings.py - script Python qui parcourt votre code avec le module tokenize (standard Python) et remplace automatiquement toutes les chaînes littérales par self.tr(...)
"""
import tokenize
from io import BytesIO
import pathlib
import sys
import re


def should_skip(token, prev_tokens, current_indent):
    """Détermine si une chaîne doit être ignorée."""
    text = token.string
    line = token.line

    # 0. Ignorer les docstrings et commentaires multi-lignes
    if text.startswith('"""') or text.startswith("'''"):
        return True

    # 2. Déjà wrappé dans self.tr()
    # Recherche d'un motif comme `self.tr(` dans les tokens précédents sur la même ligne
    line_tokens = [t for t in prev_tokens if t.start[0] == token.start[0]]
    line_str = "".join(t.string for t in line_tokens)
    if "self.tr(" in line_str:
        return True

    # 3. Niveau module (indentation = 0) -> jamais de self.tr
    if current_indent == 0:
        return True

    # 4. Docstrings (juste après def/class et une nouvelle ligne)
    # Recherche `def` ou `class` suivi par NEWLINE/NL puis la chaîne
    if len(prev_tokens) >= 3:
        # class MyClass:\n """docstring"""
        if (
            prev_tokens[-3].type == tokenize.NAME
            and prev_tokens[-3].string in ("def", "class")
            and prev_tokens[-1].type in (tokenize.NEWLINE, tokenize.NL)
        ):
            return True

    # 5. Lignes ou contextes spécifiques à ignorer
    if any(
        keyword in line
        for keyword in [
            "os.path",
            "os.getenv",
            "sys.path",
            ".startswith(",
            ".endswith(",
            "__main__",
            ".json",
            ".md",
            ".html",
            ".css",
            ".zip",
            ".bak",
            "strftime",
            "strptime",
            "re.compile",
            "re.sub",
            "re.match",
            "QApplication.translate",
            "QMessageBox.question(",
            "QFileDialog.",
            "super().__init__",
            "pyqtProperty",
            "b'epub'",
            "encode('utf-8')",
            "encoding=",
            "decode('utf-8')",
            "open(",
        ]
    ):
        return True

    return False


def wrap_file(filepath: pathlib.Path, dry_run: bool = False) -> int:
    """Enveloppe les chaînes dans un fichier avec self.tr()."""
    try:
        source = filepath.read_bytes()
    except Exception as e:
        print(f"Impossible de lire {filepath}: {e}")
        return 0

    try:
        tokens = list(tokenize.tokenize(BytesIO(source).readline))
    except tokenize.TokenError as e:
        print(f"Erreur de tokenization dans {filepath}: {e}")
        return 0

    new_tokens = []
    prev_tokens = []
    indent_level = 0
    subs = 0

    for i, token in enumerate(tokens):
        if token.type == tokenize.INDENT:
            indent_level += 1
        elif token.type == tokenize.DEDENT:
            indent_level = max(0, indent_level - 1)

        if token.type == tokenize.STRING:
            # Gestion spéciale pour les f-strings
            if token.string.lower().startswith("f"):
                if not should_skip(token, tokens[:i], indent_level):
                    # Analyse de la f-string pour la convertir en self.tr().arg()
                    original_f_string = token.string
                    # Extrait le contenu de la f-string : f"..." -> ...
                    content = original_f_string[2:-1]

                    # Trouve toutes les expressions entre { }
                    variables = re.findall(r"\{([^}]+)\}", content)

                    # Remplace les expressions par des placeholders %1, %2, ...
                    translatable_string = content
                    for i, var in enumerate(variables):
                        translatable_string = translatable_string.replace(
                            f"{{{var}}}", f"%{i+1}", 1
                        )

                    # Construit les arguments .arg(var1).arg(var2)
                    arg_part = "".join([f".arg({var})" for var in variables])

                    # Construit la nouvelle chaîne complète
                    new_string = f'self.tr("{translatable_string}"){arg_part}'

                    new_tokens.append(
                        tokenize.TokenInfo(
                            tokenize.STRING,
                            new_string,
                            token.start,
                            token.end,
                            token.line,
                        )
                    )
                    subs += 1
                else:
                    new_tokens.append(token)
            # Gestion des chaînes normales
            elif not should_skip(token, tokens[:i], indent_level):
                new_string = f"self.tr({token.string})"
                new_tokens.append(
                    tokenize.TokenInfo(
                        tokenize.STRING, new_string, token.start, token.end, token.line
                    )
                )
                subs += 1
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)

    if subs > 0:
        print(f"→ {filepath.name}: {subs} chaîne(s) à envelopper.")
        if not dry_run:
            new_source = tokenize.untokenize(new_tokens)
            # filepath.with_suffix(filepath.suffix + ".bak").write_bytes(source)
            filepath.write_bytes(new_source)
    return subs


if __name__ == "__main__":
    project_root = pathlib.Path(__file__).parent / "bluenotebook"
    total_subs = 0
    dry_run = "--dry-run" in sys.argv

    print("Lancement de l'enveloppement des chaînes pour la traduction...\n")
    for py_file in project_root.rglob("*.py"):
        if (
            "tests" in py_file.parts
            or ".venv" in py_file.parts
            or py_file.name == "main.py"
            or py_file.name.endswith("_initial.py")
        ):
            continue
        total_subs += wrap_file(py_file, dry_run=dry_run)

    print("\n" + "=" * 50)
    if dry_run:
        print(f"Analyse terminée. {total_subs} chaînes seraient enveloppées.")
    else:
        print(
            f"Opération terminée. {total_subs} chaînes ont été enveloppées avec self.tr()."
        )
        # print("Des fichiers de sauvegarde .bak ont été créés.")
    print("=" * 50)

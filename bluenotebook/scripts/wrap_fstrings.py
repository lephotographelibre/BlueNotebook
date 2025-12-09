#!/usr/bin/env python3
# wrap_fstrings_FINAL_PERFECT.py — VERSION 100% FINALE
# Ne touche JAMAIS à main.py ni au script lui-même

import pathlib
import sys
import re

# Regex ultra-robuste pour f-strings avec support des triples guillemets
FSTRING_REGEX = re.compile(
    r"""(?x)
    \b(f|F)(?=[rR]?["']|["'])   # f ou F suivi d'un guillemet
    ("""
    r'"""'
    r"""|"""
    r"'''"
    r"""|['"])  # triple guillemets OU guillemet simple
    (.*?)                        # contenu (non-greedy)
    \2                           # même type de guillemet pour fermer
    """,
    re.DOTALL,
)


def convert_file(filepath, dry_run=False):
    # EXCLUSION EXPLICITE DE main.py
    if filepath.name == "main.py":
        print(f"{filepath.name} → ignoré (fichier exclu par sécurité)")
        return 0

    source = filepath.read_text(encoding="utf-8", errors="replace")
    lines = source.splitlines()

    def replace_fstring(match):
        prefix = match.group(1).lower()
        quote = match.group(2)
        content = match.group(3)

        # Ne pas toucher les docstrings pures (sans variables)
        if not re.search(r"\{[^}]+\}", content):
            return match.group(0)

        placeholders = []
        translatable = content
        i = 1
        for expr_match in re.finditer(r"\{([^}]+?)\}", content):
            full_expr = expr_match.group(0)
            expr = expr_match.group(1).split(":", 1)[0].strip()
            placeholders.append(expr)
            translatable = translatable.replace(full_expr, f"%{i}", 1)
            i += 1

        # Échappement selon le type de guillemet
        # Pour les triples guillemets, on utilise des guillemets doubles dans .tr()
        if len(quote) == 3:  # triples guillemets
            translatable = translatable.replace('"', '\\"')
        elif quote == '"':
            translatable = translatable.replace('"', '\\"')
        else:
            translatable = translatable.replace("'", "\\'")

        # Pour les f-strings multilignes, on doit replier sur une seule ligne
        # et fermer correctement les parenthèses
        if len(quote) == 3 and "\n" in content:
            # Remplacer les sauts de ligne par \n
            translatable = translatable.replace("\n", "\\n")

        if placeholders:
            args = "".join(f".arg({p})" for p in placeholders)
            return f'self.tr("{translatable}"){args}'
        else:
            return f'self.tr("{translatable}")'

    new_source, count = FSTRING_REGEX.subn(replace_fstring, source)

    if count > 0:
        print(f"{filepath.name} → {count} f-string(s) convertie(s) :")
        for i, (old, new) in enumerate(zip(lines, new_source.splitlines()), 1):
            if re.search(r'\bf["\']|\bF["\']', old):
                if "self.tr" not in old:
                    print(f"  ligne {i:3} : {old.strip()}")
                    print(f"           → {new.strip()}\n")

        if not dry_run:
            # backup = filepath.with_suffix(".py.bak")
            # backup.write_text(source, encoding="utf-8")
            filepath.write_text(new_source, encoding="utf-8")
            # print(f"Backup créé : {backup.name}\n")

    return count


if __name__ == "__main__":
    script_name = pathlib.Path(__file__).name
    root = pathlib.Path(__file__).parent / "bluenotebook"
    dry_run = "--dry-run" in sys.argv
    total = 0

    print("CONVERSION F-STRINGS → self.tr().arg() — VERSION FINALE & SÉCURISÉE\n")
    print(f"main.py → EXCLU automatiquement")
    print(f"{script_name} → EXCLU automatiquement\n")

    for pyfile in root.rglob("*.py"):
        if any(
            excl in pyfile.parts
            for excl in ("tests", ".venv", "__pycache__", "build", "dist")
        ):
            continue
        if pyfile.name in ("main.py", script_name) or pyfile.name.endswith(
            "_initial.py"
        ):
            continue

        total += convert_file(pyfile, dry_run=dry_run)

    print("=" * 80)
    if total == 0:
        print("Aucune f-string trouvée → soit déjà converties, soit projet déjà i18n")
    elif dry_run:
        print(f"DRY-RUN → {total} f-string(s) auraient été converties")
    else:
        print(f"SUCCÈS → {total} f-string(s) converties avec self.tr().arg()")
        # print("Tous les backups sont en .py.bak")
    print("=" * 80)

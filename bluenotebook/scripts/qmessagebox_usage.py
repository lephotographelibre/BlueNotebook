 
# find_qmessagebox_usage.py
import ast
import pathlib

def find_qmessagebox_questions(project_root: str):
    """
    Parcourt un projet Python pour trouver tous les appels à QMessageBox.question().

    Args:
        project_root: Le chemin vers le dossier racine du projet à analyser.
    """
    root_path = pathlib.Path(project_root)
    if not root_path.is_dir():
        print(f"Erreur : Le dossier '{project_root}' n'existe pas.")
        return

    print(f"🔍 Analyse du projet dans : {root_path.resolve()}\n")
    found_count = 0

    # Parcourir tous les fichiers .py du projet
    for py_file in sorted(root_path.rglob("*.py")):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source_code = f.read()
            
            # Analyser le code pour construire un arbre syntaxique (AST)
            tree = ast.parse(source_code, filename=str(py_file))

            # Visiter chaque nœud de l'arbre
            for node in ast.walk(tree):
                # Vérifier si le nœud est un appel de fonction (Call)
                if isinstance(node, ast.Call):
                    # Vérifier si la fonction appelée est bien `QMessageBox.question`
                    func = node.func
                    if (isinstance(func, ast.Attribute) and
                        isinstance(func.value, ast.Name) and
                        func.value.id == 'QMessageBox' and
                        func.attr == 'question'):
                        
                        found_count += 1
                        
                        # Utiliser ast.get_source_segment pour extraire le code exact
                        # (nécessite Python 3.8+)
                        try:
                            code_segment = ast.get_source_segment(source_code, node)
                        except TypeError:
                            # Fallback pour les versions de Python < 3.8
                            # Cette méthode est moins précise pour les appels multi-lignes.
                            start_line = node.lineno - 1
                            end_line = node.end_lineno -1 if hasattr(node, 'end_lineno') else start_line
                            lines = source_code.splitlines()
                            code_segment = "\n".join(lines[start_line : end_line + 1])


                        print("-" * 70)
                        print(f"Fichier : {py_file}")
                        print(f"Ligne   : {node.lineno}")
                        print("Code    :")
                        # Indenter le bloc de code pour une meilleure lisibilité
                        for line in code_segment.splitlines():
                            print(f"  {line.strip()}")
                        print("-" * 70)
                        print()


        except Exception as e:
            print(f"⚠️  Impossible d'analyser le fichier {py_file}: {e}")

    if found_count == 0:
        print("✅ Aucune occurrence de QMessageBox.question() n'a été trouvée.")
    else:
        print(f"\nAnalyse terminée. {found_count} occurrence(s) trouvée(s).")


if __name__ == "__main__":
    # Spécifiez le chemin vers le dossier contenant votre code source
    project_directory = "bluenotebook"
    find_qmessagebox_questions(project_directory)


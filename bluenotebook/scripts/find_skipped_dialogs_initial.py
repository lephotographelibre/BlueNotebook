 
# find_skipped_dialogs.py
import ast
import pathlib

def find_dialog_calls(project_root: str):
    """
    Parcourt un projet Python pour trouver tous les appels à QMessageBox.question()
    et aux méthodes statiques de QFileDialog.

    Args:
        project_root: Le chemin vers le dossier racine du projet à analyser.
    """
    root_path = pathlib.Path(project_root)
    if not root_path.is_dir():
        print(f"Erreur : Le dossier '{project_root}' n'existe pas.")
        return

    print(f"🔍 Analyse du projet dans : {root_path.resolve()}\n")
    found_count = 0

    # Dictionnaire des fonctions à rechercher
    # Clé: Nom de la classe, Valeur: liste des méthodes (None pour toutes)
    functions_to_find = {
        'QMessageBox': ['question'],
        'QFileDialog': None  # Cherche toutes les méthodes statiques
    }

    # Parcourir tous les fichiers .py du projet
    for py_file in sorted(root_path.rglob("*.py")):
        try:
            with open(py_file, "r", encoding="utf-8") as f:
                source_code = f.read()
            
            tree = ast.parse(source_code, filename=str(py_file))

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    # Vérifier si c'est un appel de méthode sur une classe (ex: Classe.methode())
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                        class_name = func.value.id
                        method_name = func.attr

                        if class_name in functions_to_find:
                            methods = functions_to_find[class_name]
                            # Si la liste des méthodes est None (pour QFileDialog), on accepte tout.
                            # Sinon, on vérifie si la méthode est dans la liste (pour QMessageBox).
                            if methods is None or method_name in methods:
                                found_count += 1
                                
                                # Utiliser ast.get_source_segment pour extraire le code exact
                                try:
                                    code_segment = ast.get_source_segment(source_code, node)
                                except TypeError:
                                    # Fallback pour les versions de Python < 3.8
                                    start_line = node.lineno - 1
                                    end_line = node.end_lineno - 1 if hasattr(node, 'end_lineno') else start_line
                                    lines = source_code.splitlines()
                                    code_segment = "\n".join(lines[start_line : end_line + 1])

                                print("-" * 70)
                                print(f"Fichier : {py_file}")
                                print(f"Ligne   : {node.lineno}")
                                print(f"Appel   : {class_name}.{method_name}()")
                                print("Code    :")
                                for line in code_segment.splitlines():
                                    print(f"  {line.strip()}")
                                print("-" * 70)
                                print()

        except Exception as e:
            print(f"⚠️  Impossible d'analyser le fichier {py_file}: {e}")

    if found_count == 0:
        print("✅ Aucune occurrence des dialogues spécifiés n'a été trouvée.")
    else:
        print(f"\nAnalyse terminée. {found_count} occurrence(s) trouvée(s).")


if __name__ == "__main__":
    project_directory = "bluenotebook"
    find_dialog_calls(project_directory)

# Stratégie pour la Traduction des f-strings avec `self.tr()`

La gestion des chaînes formatées (f-strings) pour l'internationalisation (i18n) est un défi classique. Une chaîne comme `f"Bonjour {nom}"` ne peut pas être directement enveloppée dans `self.tr()` car la variable `{nom}` est évaluée au moment de l'exécution, alors que les outils de traduction ont besoin d'une chaîne statique et prévisible.

Le script `wrap_strings.py` adopte une approche robuste pour automatiser cette conversion.

## La Démarche Expliquée

La stratégie consiste à transformer une f-string dynamique en un appel `self.tr()` avec des arguments positionnels, ce qui est le format standard attendu par le système de traduction de Qt.

### Exemple Concret

Imaginons que votre code contienne cette ligne :
```python
message = f"Le fichier '{nom_fichier}' a {nb_lignes} lignes."
```

Le script `wrap_strings.py` va automatiquement la transformer en :
```python
message = self.tr("Le fichier '%1' a %2 lignes.").arg(nom_fichier).arg(nb_lignes)
```

### Les Étapes de la Transformation

Pour y parvenir, le script suit un processus en plusieurs étapes :

1.  **Détection de la f-string** : Le script parcourt le code et identifie toutes les chaînes de caractères qui commencent par `f"..."` ou `f'...'`.

2.  **Extraction des variables** : Il utilise une expression régulière (`re.findall(r"\{([^}]+)\}"`) pour trouver et extraire toutes les expressions contenues entre accolades `{}`. Dans notre exemple, il trouvera `nom_fichier` et `nb_lignes`.

3.  **Création de la chaîne traduisible** : Il prend le contenu de la f-string et remplace chaque expression `{variable}` par un marqueur de position (`%1`, `%2`, etc.). La chaîne devient alors statique et peut être facilement gérée par les outils de traduction.
    *   `"Le fichier '{nom_fichier}' a {nb_lignes} lignes."` devient `"Le fichier '%1' a %2 lignes."`.

4.  **Construction des arguments** : Pour chaque variable extraite, il génère un appel à la méthode `.arg()`.
    *   Pour `nom_fichier` et `nb_lignes`, il construit la chaîne de code `.arg(nom_fichier).arg(nb_lignes)`.

5.  **Assemblage final** : Enfin, il combine le tout pour créer la nouvelle ligne de code, entièrement compatible avec le système de traduction de Qt.
    *   `self.tr("Le fichier '%1' a %2 lignes.")` + `.arg(nom_fichier).arg(nb_lignes)`

### Avantages de cette approche

*   **Compatibilité totale avec i18n** : Les traducteurs travaillent sur une chaîne statique (par exemple, `"The file '%1' has %2 lines."`) et peuvent même changer l'ordre des arguments (`"%2 lines in file '%1'."`), ce qui est crucial pour certaines langues.
*   **Automatisation** : Le script `wrap_strings.py` gère cette transformation complexe pour vous, ce qui vous évite des modifications manuelles fastidieuses et sujettes aux erreurs.
*   **Lisibilité du code** : Le code final reste clair et la logique de traduction est explicite.
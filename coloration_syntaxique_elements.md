### Éléments avec Style Spécifique dans BlueNotebook

Voici la liste de tous les éléments qui ont une couleur ou une police spécifique dans l'éditeur Markdown de BlueNotebook, d'après l'analyse du fichier `editor.py`.

Toutes ces couleurs (sauf mention contraire) sont personnalisables via le menu `Fichier > Préférences...` dans l'onglet "Affichage".

### Éléments avec une couleur de police spécifique

1.  **Titres (H1 à H6)**
    *   **Syntaxe** : `# Titre`, `## Titre`, etc.
    *   **Couleur par défaut** : `#208bd7` (bleu vif)
    *   **Note** : La taille de la police varie également en fonction du niveau du titre.

2.  **Listes**
    *   **Syntaxe** : Lignes commençant par `-`, `*`, `+`, `1.`, ou `- [ ]`.
    *   **Couleur par défaut** : `#208bd7` (bleu vif, la même que les titres).
    *   **Note** : La couleur s'applique à toute la ligne de la liste.

3.  **Gras**
    *   **Syntaxe** : `**texte en gras**` ou `__texte en gras__`
    *   **Couleur par défaut** : `#448C27` (vert)

4.  **Italique**
    *   **Syntaxe** : `*texte en italique*` ou `_texte en italique_`
    *   **Couleur par défaut** : `#448C27` (vert)

5.  **Texte Barré**
    *   **Syntaxe** : `~~texte barré~~`
    *   **Couleur par défaut** : `#448C27` (vert)

6.  **Liens**
    *   **Syntaxe** : `texte du lien` ou `<http://...>`
    *   **Couleur par défaut** : `#0366d6` (bleu) - *Non personnalisable actuellement*
    *   **Note** : Le texte est également souligné.

7.  **Tags**
    *   **Syntaxe** : `@@mon_tag`
    *   **Couleur par défaut** : `#d73a49` (rouge)

8.  **Horodatage**
    *   **Syntaxe** : `HH:MM` (ex: `14:30`)
    *   **Couleur par défaut** : `#005cc5` (bleu foncé)

9.  **Citations**
    *   **Syntaxe** : `> texte de la citation`
    *   **Couleur par défaut** : `#2B303B` (gris foncé) - *Non personnalisable actuellement*
    *   **Note** : Le texte est également en italique.

### Éléments avec une couleur de fond spécifique

10. **Code "inline"**
    *   **Syntaxe** : `` `code` ``
    *   **Couleur du texte** : `#d6336c` (rose/rouge)
    *   **Couleur de fond** : `#f2f07f` (jaune pâle)

11. **Blocs de code**
    *   **Syntaxe** : Blocs de texte entourés par ```.
    *   **Couleur de fond** : `#f0f0f0` (gris très clair)

12. **Surlignage**
    *   **Syntaxe** : `==texte surligné==`
    *   **Couleur de fond** : `#FFC0CB` (rose clair)

### Éléments avec une police spécifique

Certains éléments utilisent une police de caractères (fonte) spécifique pour se différencier du texte standard.

1.  **Code "inline"**
    *   **Syntaxe** : `` `code` ``
    *   **Police** : `Consolas, Monaco, monospace`. Une police à chasse fixe (monospace) est utilisée pour que tous les caractères aient la même largeur, ce qui est standard pour afficher du code.

2.  **Blocs de code**
    *   **Syntaxe** : Blocs de texte entourés par ```.
    *   **Police** : `Consolas, Monaco, monospace`. C'est la même police que pour le code "inline", pour les mêmes raisons de lisibilité du code.
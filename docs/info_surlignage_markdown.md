# Informations sur l'Extension de Surlignage Markdown

Vous avez demandé des détails sur l'extension de surlignage (`==texte==`) utilisée dans BlueNotebook et comment la supprimer. Voici une explication concrète.

### Concrètement, c'est quoi cette extension ?

L'extension en question s'appelle **`pymdownx.mark`**. Elle fait partie d'une bibliothèque très populaire nommée `pymdown-extensions`, qui ajoute de nombreuses fonctionnalités au parser `python-markdown` de base.

Son rôle est très simple et précis :
1.  Elle scanne le texte Markdown que vous écrivez.
2.  Quand elle trouve du texte entouré de doubles signes égal, comme `==ceci est surligné==`.
3.  Elle le transforme en une balise HTML standard `<mark>`, comme ceci : `<mark>ceci est surligné</mark>`.

C'est cette balise `<mark>` qui est ensuite interprétée par le panneau d'aperçu HTML. Le navigateur intégré lui applique un style (généralement un fond jaune) pour que le texte apparaisse visuellement surligné.

**En résumé :** L'extension `pymdownx.mark` est le "traducteur" qui convertit la syntaxe `==texte==` de l'éditeur en un format que l'aperçu HTML peut comprendre et afficher correctement.

---

### Comment la supprimer ?

En tant qu'**utilisateur**, vous ne pouvez pas "supprimer" ou "désactiver" cette extension via une option dans les préférences, car elle est intégrée au cœur du moteur de rendu de BlueNotebook. La manière la plus simple de ne pas l'utiliser est simplement de **ne pas écrire de texte avec la syntaxe `==...==`**.

Si vous êtes le **développeur** de l'application et que vous souhaitez la retirer complètement, l'opération est plus complexe et nécessite de modifier le code source à plusieurs endroits :

1.  **Retirer l'extension du parser Markdown** :
    Dans le fichier `bluenotebook/gui/preview.py`, il faudrait trouver la ligne qui initialise le parser et retirer `'pymdownx.mark'` de la liste des extensions.

2.  **Retirer la coloration dans l'éditeur** :
    Dans le fichier `bluenotebook/gui/editor.py`, il faudrait supprimer la règle de coloration syntaxique (`QSyntaxHighlighter`) qui détecte et colore le texte `==...==` pendant que vous tapez.

3.  **Retirer l'option du menu** :
    Dans `bluenotebook/gui/main_window.py`, il faudrait supprimer l'action (`QAction`) qui correspond à "Surligné" dans le menu "Formater", pour que l'utilisateur ne puisse plus l'insérer facilement.

4.  **Nettoyer les dépendances** :
    Enfin, il faudrait retirer la bibliothèque `pymdown-extensions` du fichier `requirements.txt` pour que les nouveaux environnements ne l'installent plus.

En bref, cette fonctionnalité est profondément intégrée. La "supprimer" reviendrait à défaire le travail qui a été fait pour l'ajouter, ce qui n'est pas une simple case à décocher.
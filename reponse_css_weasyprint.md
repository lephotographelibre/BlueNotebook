# Confirmation sur l'utilisation des CSS par WeasyPrint

Bonjour ! C'est une excellente question, et la réponse est un peu plus nuancée qu'un simple oui ou non.

En fait, **non, WeasyPrint n'utilise pas *exactement* les mêmes feuilles de style CSS que le panneau d'aperçu HTML.**

Il y a une distinction importante à faire :

1.  **L'aperçu HTML** utilise des fichiers CSS externes situés dans `bluenotebook/resources/css_preview/` (comme `github-markdown-dark_preview.css`). Ces fichiers sont conçus pour le rendu dans un navigateur web et ne contiennent pas de règles spécifiques à l'impression.

2.  **L'export PDF avec WeasyPrint** utilise une chaîne de caractères CSS qui est **définie directement dans le code Python**, à l'intérieur de la méthode `export_journal_pdf` du fichier `bluenotebook/gui/main_window.py`.

### Pourquoi cette différence ?

La raison est que l'export PDF a des besoins spécifiques que l'aperçu HTML n'a pas :

*   **Pagination** : Définir la taille de la page (`A4`), les marges, et surtout les en-têtes et pieds de page (numéros de page, titre du document, etc.). Ceci est géré par la règle `@page` en CSS, qui n'a aucun effet dans un navigateur web standard.
*   **Polices pour l'impression** : Utiliser des polices de caractères qui s'intègrent bien dans un document PDF, comme 'DejaVu Sans'.
*   **Contrôle des sauts de page** : S'assurer que chaque nouvelle note commence sur une nouvelle page (`page-break-before: always;`) et qu'un titre n'est pas laissé seul en bas d'une page (`page-break-after: avoid;`).

### Où trouver le CSS de WeasyPrint ?

Le code CSS utilisé pour le PDF est codé "en dur" dans le fichier `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/main_window.py`, dans la méthode `export_journal_pdf`.

Voici l'extrait de code pertinent :

```python
# /home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/main_window.py

# ... dans la méthode export_journal_pdf ...

        # CSS spécifique pour WeasyPrint avec pagination
        weasyprint_css = f"""
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
            
            @bottom-center {{
                content: "Page " counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #666;
            }}
            
            /* ... autres règles @page ... */
        }}
        
        body {{
            font-family: 'DejaVu Sans', Arial, sans-serif;
            font-size: 11pt;
            /* ... */
        }}

        .journal-entry {{
            page-break-before: always;
        }}
        
        /* ... beaucoup d'autres règles pour les titres, tableaux, code, etc. ... */
        """

        # ...

        worker = PdfExportWorker(
            # ...
            css_string=weasyprint_css,  # <--- Le CSS est passé ici
            # ...
        )
```

### Conclusion

Même si les styles de l'export PDF sont conçus pour **ressembler visuellement** aux thèmes de l'aperçu (par exemple, en utilisant des couleurs similaires pour les titres ou les blocs de code), il s'agit bien de **deux ensembles de règles CSS distincts et gérés séparément**.

Pour modifier l'apparence de l'export PDF, vous devez donc modifier la chaîne de caractères `weasyprint_css` dans `main_window.py`, et non les fichiers dans `resources/css_preview/`.
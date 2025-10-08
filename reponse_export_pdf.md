## V2.X.Y CSS pour WeasyPrint

`main_windows.py`

```python
# CSS spécifique pour WeasyPrint avec pagination
        weasyprint_css = f"""
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;

            @bottom-center {{
                content: "Page " counter(page) " / " counter(pages);
                /* ... */
            }}
            /* ... autres règles CSS pour l'impression ... */
        }}
        """
```
.tag --> color: #1976d2;
.entry-date -->  color: #3498db;
h1, h2, h3, h4, h5, h6  -->  color: #2c3e50;
body  --> color: #333;
blockquote --> color: #555;
blockquote --> border-left: 4px solid #3498db;
pre, code  --> background-color: #f5f5f5;
th, td --> border: 1px solid #ddd;
th --> background-color: #f5f5f5;
       


## Emplacement du Code pour l'Export PDF dans BlueNotebook

Bonjour ! Excellente question. Le code pour la fonctionnalité d'exportation PDF est principalement centralisé dans le fichier `bluenotebook/gui/main_window.py`.

Il est intelligemment divisé en deux parties : la préparation des données dans le thread principal et la génération effective du PDF dans un thread séparé pour ne pas bloquer l'interface utilisateur.

Voici une décomposition détaillée du processus et où trouver chaque partie du code :

### 1. Point d'Entrée : La Méthode `export_journal_pdf`

Tout commence dans la classe `MainWindow` avec la méthode `export_journal_pdf`. C'est la fonction qui est appelée lorsque l'utilisateur clique sur `Fichier > Exporter Journal PDF...`.

**Fichier** : `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/main_window.py`

Cette méthode orchestre tout le processus :

1.  **Vérification de WeasyPrint** : Elle s'assure que la bibliothèque `weasyprint` est installée.
2.  **Dialogue de Configuration** : Elle ouvre la boîte de dialogue `DateRangeDialog` pour permettre à l'utilisateur de choisir la plage de dates, le titre, l'auteur et une image de couverture.
3.  **Préparation du HTML** : Elle collecte toutes les notes de la période sélectionnée et les assemble en un **unique et grand document HTML** (`full_html`). Ce document inclut :
    *   Une page de garde personnalisée.
    *   Le contenu de chaque note converti de Markdown en HTML.
    *   Des sauts de page entre les notes.
4.  **Préparation du CSS** : Elle définit une chaîne de caractères CSS spécifique pour l'impression (`weasyprint_css`). **Attention**, ce n'est pas le même CSS que celui de l'aperçu. Celui-ci contient des règles `@page` pour gérer la pagination, les marges, et les en-têtes/pieds de page du PDF.
5.  **Lancement Asynchrone** : Elle instancie un `PdfExportWorker` et le lance dans un `QThreadPool`.

```python
# /home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/main_window.py

# ...

    def export_journal_pdf(self):
        """Exporte l'ensemble du journal dans un unique fichier PDF avec WeasyPrint."""
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            # ... (gestion de l'erreur si weasyprint n'est pas installé)
            return

        # ... (récupération des notes et ouverture de DateRangeDialog) ...

        # ... (construction du grand fichier HTML `full_html`) ...

        # CSS spécifique pour WeasyPrint avec pagination
        weasyprint_css = f"""
        @page {{
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
            
            @bottom-center {{
                content: "Page " counter(page) " / " counter(pages);
                /* ... */
            }}
            /* ... autres règles CSS pour l'impression ... */
        }}
        """
        # ...

        # Générer le PDF avec WeasyPrint
        try:
            self._start_pdf_flashing()

            worker = PdfExportWorker(  # <--- Instanciation du worker
                html_string=full_html,
                base_url=str(self.journal_directory),
                css_string=weasyprint_css,
                output_path=pdf_path,
            )
            # ...
            self.thread_pool.start(worker) # <--- Lancement dans un thread séparé

        # ... (gestion des erreurs) ...
```

### 2. Le Cœur de la Conversion : La Classe `PdfExportWorker`

C'est dans cette classe que la bibliothèque `weasyprint` est réellement utilisée pour convertir le HTML en PDF.

**Fichier** : `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/main_window.py` (définie au début du fichier)

La méthode `run()` de cette classe contient l'appel crucial :

```python
# /home/jm/PychymProjects/BlueNotebook/bluenotebook/gui/main_window.py

class PdfExportWorker(QRunnable):
    """Worker pour générer le PDF en arrière-plan."""

    # ... (initialisation) ...

    def run(self):
        try:
            # Conversion du HTML et du CSS en objets WeasyPrint
            html_doc = self.HTML(string=self.html_string, base_url=self.base_url)
            css_doc = self.CSS(string=self.css_string)
            
            # Écriture du fichier PDF final
            html_doc.write_pdf(self.output_path, stylesheets=[css_doc])
            
            # Envoi d'un signal pour notifier que c'est terminé
            self.signals.finished.emit(self.output_path)
        except Exception as e:
            self.signals.error.emit(str(e))
```

En résumé :

*   **Orchestration et préparation HTML/CSS** : `MainWindow.export_journal_pdf()`
*   **Conversion PDF effective (appel à WeasyPrint)** : `PdfExportWorker.run()`

Cette architecture est très bien conçue car elle garantit une interface utilisateur toujours réactive, même lors de l'exportation d'un journal très volumineux.

## Confirmation sur l'utilisation des CSS par WeasyPrint

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
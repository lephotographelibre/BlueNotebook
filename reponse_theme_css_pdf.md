# Comment est défini le thème CSS pour les exports PDF du journal ?

D'après l'analyse du code, et plus particulièrement du fichier `bluenotebook/gui/preferences_dialog.py`, il apparaît qu'il n'existe **pas encore d'option spécifique** dans la boîte de dialogue des préférences pour définir un thème CSS distinct pour les exports PDF.

### Comment le thème CSS est-il défini actuellement ?

Le thème CSS utilisé pour l'export PDF est en réalité le **même que celui configuré pour l'aperçu HTML**.

Voici comment cela fonctionne :

1.  Dans `Préférences > Affichage > Aperçu HTML`, vous pouvez sélectionner un thème CSS (par exemple, `github-markdown-dark_preview.css`).
2.  Ce choix est sauvegardé dans les paramètres sous la clé `preview.css_theme`.
3.  Lors de l'exportation en PDF (via la méthode `export_journal_pdf` dans `main_window.py`), la logique d'exportation (dans `integrations/pdf_exporter.py`) récupère le contenu HTML de chaque note.
4.  Ce contenu HTML est ensuite combiné avec le **thème CSS de l'aperçu HTML** pour générer le fichier PDF final.

En résumé, pour changer le style de vos exports PDF, vous devez actuellement changer le thème de l'aperçu HTML.

### Suggestion d'amélioration

Pour offrir plus de flexibilité, vous pourriez créer un onglet dédié dans les préférences pour l'export PDF. Cela permettrait aux utilisateurs de choisir un thème CSS pour l'aperçu et un autre, potentiellement plus adapté à l'impression, pour les exports PDF.

Nous pourrions procéder comme suit pour implémenter cette fonctionnalité :

1.  **Modifier `preferences_dialog.py`** pour ajouter une section de sélection de thème dans l'onglet "Export PDF".
2.  **Sauvegarder ce nouveau paramètre** (par exemple, `pdf.css_theme`) dans `settings.json`.
3.  **Modifier la logique d'exportation PDF** dans `main_window.py` et `integrations/pdf_exporter.py` pour utiliser ce nouveau paramètre au lieu de celui de l'aperçu HTML.
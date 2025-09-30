# Solution : Afficher une image locale dans l'aperçu HTML

Bonjour ! Je comprends tout à fait votre problème. C'est une situation classique et frustrante lorsqu'on travaille avec des vues web locales. Pour des raisons de sécurité, un composant `QWebEngineView` ne peut pas, par défaut, accéder aux fichiers de votre ordinateur (comme les images) lorsque le HTML est chargé directement comme une chaîne de texte.

La bonne nouvelle, c'est qu'il y a une solution simple ! Il suffit d'indiquer à la vue web une "URL de base" pour qu'elle sache comment interpréter les chemins de fichiers locaux.

### Explication du problème

Lorsque vous utilisez `self.web_view.setHtml(html_string)`, le contenu est traité comme s'il venait d'une page vide (`about:blank`). Les chemins de fichiers comme `/home/jm/Images/...` ou `../../../...` n'ont aucun sens dans ce contexte et sont bloqués.

### La solution

La solution consiste à utiliser le deuxième argument de la méthode `setHtml`, qui est `baseUrl`. En lui passant une URL indiquant que le contexte est le système de fichiers local, `QWebEngineView` saura comment charger vos images.

Voici la modification à apporter dans votre fichier `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/preview.py`.

```diff
--- a/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/preview.py
+++ b/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/preview.py
@@ -457,7 +457,9 @@
             full_html = self.create_html_template(html_content)
 
             # Mettre à jour la vue web
-            self.web_view.setHtml(full_html)
+            # V1.7.3 Fix: Ajout de baseUrl pour permettre l'affichage des images locales
+            # En passant "file:///", on autorise QWebEngine à charger des fichiers locaux via des chemins absolus.
+            self.web_view.setHtml(full_html, baseUrl=QUrl("file:///"))
             self.current_html = full_html
 
         except Exception as e:
```

### Comment utiliser les images maintenant ?

Avec cette modification, vous pouvez insérer des images locales en utilisant un **chemin absolu** dans votre Markdown. Les deux syntaxes suivantes fonctionneront :

1.  **Syntaxe Markdown (recommandée)** :
    ```markdown
    ![](file:///home/jm/Images/2025_07_09_Pleine_Lune/IMG_7074.jpg)
    ```
    ou simplement :
    ```markdown
    ![](/home/jm/Images/2025_07_09_Pleine_Lune/IMG_7074.jpg)
    ```

2.  **Syntaxe HTML** :
    ```html
    <img src="/home/jm/Images/2025_07_09_Pleine_Lune/IMG_7074.jpg" width="400">
    ```

**Important** : Les chemins relatifs comme `../../../` ne fonctionneront toujours pas de manière fiable, car le "document" HTML n'a pas de véritable emplacement sur le disque. Privilégiez toujours les chemins absolus.

J'ai appliqué ce petit correctif qui devrait résoudre votre problème. N'hésitez pas si vous avez d'autres questions !
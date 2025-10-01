## V1.7.X Menu Inserser Suite A FAIRE
1.
je voudrai modifier le sous menu Images (<img ..>).
si un nom de fichier est selectionné dans l'éditeur , demander la largeur max en pixels à l'utilisateur puis inserer le tag. Proposer la valeur 400 px par defaut.
Si aucun texte n'est sélectionné dans l'éditeur ouvrir une boite d dialogue qui permette à l'utilisateur de sélectionner un fichier et de demander la largeur max en pixels à l'utilisateur puis inserer le tag. Proposer la valeur 400 px par defaut.

2.
travailler le Lien Markdown
dans tous les cas ouvrir une boite de sialogue avec 2 hamps
- Texte du Lien:
- URL:  


si rien n'est selectionné ... (rien ne se passe) ouvrir la boite d edialogue avec les deux champs nom remplis

si une texte est selectionné alors ouvrir la boite de dialogue avec  le champ Teste di Mien remplis avec le texte sélectionné, et le champ URL vide

## V1.7.7 Editeur Markdown: Mini Menu Contextuel

Lorsque du texte est sélectionné je voudrais ajouter dans le menu contextuel la possibilité de mettre en gras, italique, barré, surligné, inline et bloc de code.
beta1

defilement Molette et CTRL-Défilement molette corrigés
beta2

mis à jour la version de l'application à 1.7.7 dans le point d'entrée main.py ainsi que dans le manuel utilisateur aide_en_ligne.html.
beta3


## V1.7.6 Créer un menu Intégration / Citation du jour

Creer un menu Intégration avec son emoji  dans la barre de Menu princcipale.
Il sera placé entre Insérer et Aide
Il aura comme sous menu "Citation du Jour" qui sera déplacé  avec son emoji du menu Inserer vers le Menu Intégration.
beta1

 si dans préférence "Afficher la citation du jour au demarrage" n'est pas cochée il faudra alors aller chercher la citation au moment de l'appel du menu "Citation du Jour et pas au demarrage.
 si dans préférence "Afficher la citation du jour au demarrage"  est cochée il faudra alors aller chercher la citation  au demarrage.

 ne faire l'appel réseau pour la citation que lorsque c'est nécessaire, soit au démarrage si l'option est cochée, soit au moment du clic sur le menu si elle ne l'est pas. C'est une approche bien plus optimisée.

beta2

MAJ aide en ligne avec FAQ

beta3

Je voudrais que tu généres une représentation graphique de la barre de menu du projet avec tous ses sous Menus complete avec la description de chaque sous menu et sauvegardes cette representation graphique dans le fichier docs/V1.7.6_menus.md

et la doc V1.7.6_bluenotebook_technical_doc.md
beta5



## V1.7.5 Add HTML Comment 

Je voudrais ajouter un sous menu dans Insérer qui s'appelle Commentaire HTML.
la syntaxe est <!-- texte du commentaire --> 

Si un texte est sélectionné dasn l'éditeur mettre ce texte en commentaire
Si aucun texte n'est sélectionné insérer <!-- texte du commentaire --> 
Ne pas oublier une emoli.
ce sous menu viendra directement sous "Ligne Horzontale"

Ajout aux préférences

V1.7.5beta2

MAJ Aide en lign e+ fichier Menu

V1.7.5beta3

MAJ Doc  Mets a jour le fichier doc V1.7.3_bluenotebook_technical_doc.md et crée un nouveau fichier avec les modifs V1.7.5_bluenotebook_technical_doc.md

V1.7.5beta4

Met a jour themes 

## V1.7.4 Qt Support (kde, gnome, gtk)

modification de  run_bluenotebook.sh pour la Détection de l'environnement de bureau pour le thème Qt...

```bash
echo "🎨 Détection de l'environnement de bureau pour le thème Qt..."
PLATFORM_THEME=""

# La variable XDG_CURRENT_DESKTOP est la méthode la plus standard.
# On la vérifie en premier, en ignorant la casse.
case "${XDG_CURRENT_DESKTOP,,}" in
  *kde*|*plasma*)
    PLATFORM_THEME="kde"
    ;;
  *gnome*|*cinnamon*|*mate*|*xfce*)
    PLATFORM_THEME="gtk3"
    ;;
esac

if [ -n "$PLATFORM_THEME" ]; then
    export QT_QPA_PLATFORMTHEME=$PLATFORM_THEME
    echo "✅ Thème Qt forcé à '$PLATFORM_THEME' pour une meilleure intégration."
else
    echo "ℹ️ Environnement de bureau non détecté ou non supporté pour un thème spécifique. Qt choisira par défaut."
fi
```





## V1.7.3 Affichage d'images dans l'aperçu HTML

Pour des raisons de sécurité, un composant `QWebEngineView` ne peut pas, par défaut, accéder aux fichiers de votre ordinateur (comme les images) lorsque le HTML est chargé directement comme une chaîne de texte.

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
 

V1.7.3 beta1

Ajouter un sous menu dans Inserer: Image Markdown qui insere une image avec le tag markdown c'est a dire par exemple: [](/home/jm/Images/2025_07_09_Pleine_Lune/IMG_7074.jpg)
si un nom de fichier est selectionné dans l'éditeur inserer le tag à la place directement. Sin aucun texte n'est sélectionné dans l'éditeur ouvrir une boite d dialogue qui permette à l'utilisateur de sélectionner un fichier. ce nouveau sous Menu sera positionné dans le menu inserer immediatement dessous Lien. ne pas oublier l'emoji image

V1.7.3beta2

Manque Emoji au menu Inserer Lien MAkdown

je voudrai modifier le sous Menu "Inserer -> Image Markdown"
si un nom de fichier est selectionné dans l'éditeur , inserer le tag. 
Si aucun texte n'est sélectionné dans l'éditeur ouvrir une boite d dialogue qui permette à l'utilisateur de sélectionner un fichierp uis inserer le tag.

cette fonctionnalité est déjà parfaitement implémentée dans la méthode insert_markdown_image du fichier editor.py.

Voici comment elle fonctionne actuellement :

Si du texte est sélectionné : *Le programme vérifie si ce texte correspond à un chemin de fichier valide sur votre ordinateur*.
Si c'est le cas, il utilise ce chemin pour créer le tag Markdown !.
Si ce n'est pas un chemin valide (ou si rien n'est sélectionné), il passe à l'étape 2.

Si aucun texte n'est sélectionné (ou si la sélection n'est pas un fichier) : Une boîte de dialogue s'ouvre, vous permettant de choisir un fichier image. Si vous en sélectionnez un, le tag Markdown correspondant est inséré.

V1.7.3beta3

Je voudrais réordoner les Sous menus de Inserer.. Il faut descendre Lien URL ou Email en troisieme position.

V1.7.3beta4

Il manque une emoji image au presmier sous menu de inserer c'east a dire Image (<img ..>)

V1.7.3beta5







## V1.7.2 Ajout Paramètre Affichages Couleurs +  Bug Couleurs Liste et double asterisque

Preferences : add Citations Color and Links + police code et Inline

Ajouter la Possibilité de modifier les couleurs dans l'editeur markdown  dans préférences Utilisateur pour les citations, les liens ainsi que les polices pour le code et inline et donc settings.json, mais aussi par defaut stockées comme les couleurs actuelles

V1.7.2beta1

on avait fait la modif suivante hier: "change la couleur de police des textes Listes du - ou 1. ou - [ jusqu'a la fin de la ligne c'est a dire un retour CR
meme couleur que les headers
cela devrait permettre d'identifier plus facilement les listes dans le document Markdown comme VScode  Editeur Markdown
Je souhaite annuler cette modification et pour toute les listes n'afficher dans la couleur des liste uniquement le signe en début de liste ( - , 1. ou - [ ] ). Le reste de la ligne restera comme du texte standard editeur et pourra faire l'onjet d'enrichissement (gras, italique,...)

V1.72betat2

Issue [#17](https://github.com/lephotographelibre/BlueNotebook/issues/17)
bug coloration syntaxique

dans l'editeur la lise en gras d'un mot V1.6.12beta2 produit 2 couleurs 1 pour les etoiles ** et une pour le texte V1.6.12beta2 (couleur choisie pour le gras) cela ne se produit pas avec V1.6.12beta2 ni pour V1.6.12beta2 ni pour V1.6.12beta2

**V1.6.12beta2** pas ok
*V1.6.12beta2* ok 
_V1.6.12beta2_ ok 
___V1.6.12beta2___ ok

V1.72betat3

ameliorer la syncro entre editeur et Aperçu HTM.
Je voudrais que des que je positionne le caret dans l'editeur on essaye de synchroniser l"apercu HTML et que l'on positionne l'apercu HTML à la meme position correspondante en 1 ere ligne, c'est a dire en haut de l'affichage HTML. Est ce assez clair ?
## V1.7.1 Génération d'un theme de base à partir  des paramètres actuels (couleur , Police)

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


## V1.6.12  Issue #15 Editeur Markdown : change la couleur de police des textes Listes

change la couleur de police des textes Listes du - ou 1. ou - [ jusqu'a la fin de la ligne c'est a dire un retour CR
meme couleur que les headers
cela devrait permettre d'identifier plus facilement les listes dans le document Markdown comme VScode  Editeur Markdown
V1.6.12beta1

Possibilité de modifier la couleur dans préférences Utilisateur et donc settings.json, mais aussi par defaut stockées comme couleur Header
V1.6.12beta2

Dans l'editeur les couleurs par défaut pour l'éditeur sont :

Couleur de fond (background_color) : #d6ebff (un bleu très clair)
Couleur du texte (text_color) : #2c3e50 (un gris-bleu foncé)
Couleur des titres (heading_color) : #208bd7 (un bleu vif)
Couleur des listes (list_color) : #208bd7 (la même que les titres, comme vous l'aviez demandé)
Couleur du texte sélectionné (selection_text_color) : #ff0004 (un rouge vif)

Possibilyé de modifier la couleur de  inline
Couleur du texte (police) : #d6336c (un rose/rouge).
Couleur de fond : #f2f07f (un jaune pâle).

Ajouter la Possibilité de modifier les couleur  (teste et fond)de  inline dans préférences Utilisateur et donc settings.json, mais aussi par defaut stockées comme les couleurs actuelles

V1.6.12beta3

Ajouter la Possibilité de modifier les couleurs dans l'editeur markdown  dans préférences Utilisateur pour le gras, le italique, le barré et surligné et donc settings.json, mais aussi par defaut stockées comme les couleurs actuelles



couleur de @@prompt et de l'horodatage

Ajouter la Possibilité de modifier les couleurs dans l'editeur markdown  dans préférences Utilisateur pour les @@prompt et de l'horodatage HH:MM et donc settings.json, mais aussi par defaut stockées comme les couleurs actuelles

V1.6.12beta4

Ajouter la Possibilité de modifier les couleurs dans l'editeur markdown  dans préférences Utilisateur pour les extraits de code et donc settings.json, mais aussi par defaut stockées comme les couleurs actuelles. ces préférences dans le panneau afficghage seront entre Couleur fond inline et Couleur texte en gras

V1.6.12beta4

Couleur Par default

{
    "editor": {
        "font_family": "Droid Sans Mono",
        "font_size": 12,
        "background_color": "#d6ebff",
        "text_color": "#2c3e50",
        "heading_color": "#208bd7",
        "list_color": "#208bd7",
        "selection_text_color": "#ff0004",
        "inline_code_text_color": "#d6336c",
        "inline_code_background_color": "#f2f07f",
        "bold_color": "#448C27",
        "italic_color": "#448C27",
        "strikethrough_color": "#448C27",
        "highlight_color": "#FFC0CB",
        "tag_color": "#d73a49",
        "timestamp_color": "#005cc5"
    },

## V1.6.11 Issue #5 Edition Markdon mauvaise coloration syntaxique pour les mots  contenant un "_"  

Edition Markdon mauvaise coloration syntaxique pour les mots  contenant un _ 

dans la phrase: "d'un fichier texte nommé index_tags.txt stocké dans le répertoire du journal indexé. si l'utilisateur change de journal une nouvelle indexation sera lancée dans ce nouveau journa. le format du fichier index_tags.txt sera le suivant"

coloration syntaxique inapropriée entre les deux _ c'est à dire de "_tags.txt ...à ... index_" 

Le problème est typique des expressions régulières trop "gourmandes" pour la mise en forme italique. Une regex simple comme `_(.+?)_` va capturer tout le texte entre le premier `_` de `index_tags.txt` et le `_` de `journal_indexé`, ce qui n'est pas le comportement souhaité.

La spécification Markdown (et ses variantes comme GFM) a des règles précises pour l'emphase (italique) afin d'éviter ce genre de faux positifs, notamment pour permettre les `_` à l'intérieur des mots.

Pour corriger cela, il faut affiner l'expression régulière dans votre classe `MarkdownHighlighter` (qui se trouve probablement dans `gui/editor.py`. La solution consiste à utiliser des "lookarounds" (assertions avant et arrière) pour s'assurer que les `_` sont bien des délimiteurs de formatage et non une partie d'un mot.

Une version améliorée de la règle pour l'italique avec des underscores. Dans la méthode `highlightBlock` de   `MarkdownHighlighter`.

```python
# Dans votre fichier gui/editor.py, classe MarkdownHighlighter

# Règle pour l'italique avec des underscores
# (?<!\w) : S'assure qu'il n'y a pas de caractère de mot avant le premier '_'
# _ : Le délimiteur de début
# ([^_]+) : Capture un ou plusieurs caractères qui ne sont pas des '_'
# _ : Le délimiteur de fin
# (?!\w) : S'assure qu'il n'y a pas de caractère de mot après le second '_'
italic_underscore_rule = r"(?<!\w)_([^_]+)_(?!\w)"

# Appliquer la règle
for match in re.finditer(italic_underscore_rule, text):
    self.setFormat(match.start(), match.end() - match.start(), self.italic_format)
```
Cette expression régulière garantit que l'italique ne sera appliqué que si les underscores sont entourés par des espaces, de la ponctuation, ou sont au début/fin de la ligne, mais pas s'ils sont au milieu d'un mot.



## V1.6.10 Ajuste la taille des polices pour les titres Markdown

Ajuste la logique de calcul de la taille des polices pour les titres Markdown dans la classe MarkdownHighlighter. La nouvelle formule se base sur la taille de police de l'éditeur et applique un écart plus prononcé entre chaque niveau de titre, ce qui rend la hiérarchie visuelle beaucoup plus claire.
Pour marquer encore plus clairement la hiérarchie des titres. Un écart de 2 points entre chaque niveau rendra la structure du document beaucoup plus lisible dans l'éditeur.



## V1.6.9 Issue #14 Impossible de rechercher un mot dans le champ de recherche
- on va d'abord pour le champ de recherche Supprimer le préfixe @@ automatique 
- il faudra donc utiliser la boite de recherche à la fois pour les mots ou les tags
préfixer @@ pour les tags
- pour rechercher un tags dans le fichier d'index des tags il faudra manuellement saisir @@ devant le nom du tag ou utiliser le dropdown button
- prou rechercher un mot dans le fichier d'index de mots faudra juste saisir le mot
- dans la boite de recherche vide mettre en grisé "@@tag ou mot" au lieu

- est il possible de mettre dans la boite de recherche une icone pour effacer le contenue  dans le champ  de recherche juste avant la loupe de recherche qui est déja présente. je ne sais pas comment se nomme cet indicate à cliquer a afficher dans le champ de rechcherche

- Dès que le bouton de recherche dopdown permet de sélectionner un tag dans la liste, et dès qu'il est cliqué vient remplir le champ de recherche avec le tag sélectionné.
En plus je voudrais lancer la recherche sur ce tag automatiquement des qu'il est cléqué dans la liste en plus de remplir  le champ de recherche avec le tag sélectionné

## V1.6.8 Mécanisme de Sélection du Répertoire de Sauvegarde 

- Mémoriser le dernier répertoire utilisé 
- Utiliser une variable d’environnement BACKUP__DIRECTORY. 
- Préférences utilisatur dans settings.json

```json
    "backup": {
        "last_directory": "/home/jm/T\u00e9l\u00e9chargements"
    }

```

- Changement du nom du fichier backup avec l'heure
```python
        # Générer un nom de fichier de sauvegarde par défaut
        backup_filename_default = f"BlueNotebook-Backup-{self.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"
```

## V1.6.7 Surbrillance Jaune texte recherché via boite de recherche (pas mis en oeuvre)

Pas satisfait de la mise en oeuvre compliquée de l-- Avoir plus tard

- Lorsque l'on recherche un mot ou tag via le champ de recherche du Panneau Navigation, lorsque l'on clique dans 


## V1.6.6 Fix Bug redimentionement Zone de Recherche

- Quand j'agrandi la fenetre principale pour passer en plein ecran , les élements du panneau Navigation reste de taille fixe ce qui est attendu, sauf la zone sous le calendrier qui se déforme.C'est a dire qu ele champ recherche rest de taille fixe ok , mais le bouton drop down a coté se déforme est devient tres grand en hauteur ce qui deforme toute cette sone. il ne faut pas que ce bouton change de taillle lors d'un redimentionnement

## V1.6.5 Recherche Tags et Mots - Panneau Résultat de Recherche

- Lors de la recherche d'un tags dans à partir du champ de recherche du panneau Navigation on va  aller chercher les information dans le fichier index_tags.json qui est dans le répertoire du Journal.
On va alors afficher une liste dans le Panneau Résultats de Recherche. Chaque ligne de la liste est composé de deux champ:
- Le champ Date: La date de la note de l'occurrence du tag recherché format YYYY-MM-JJ
- Le champ Texte: qui le le context du fichier JSP de l'occurrence du tag recherché

les lignes de la liste affichée dans le Panneau Résultats de Recherche comportera donc deux colonnes (Date et Texte) et seront triées suvant la date (les plus recentes en premier
Le header de la colonne date permettra d'in verser le tri des dates

- idem pour les mots + correction Index

Beta3

- enrichir l'indexation des tags et des mots en ajoutant un nouveau champ pour chaque entrée en plus de context, filename, et date qui est le numero de ligne ou se trouve ce tag ou ce mot dans le fichier note.

Beta4

- les fichiers index tags et mots contiennent mainteant le numero de lign eou se trouve le tag ou le mot recherché. Idans la liste "Résultat de recherche lorsqu'un tag ou un mot est sélectionné il faut que la note consernée s'ouvre en positionnat la note dans l'editeur avec la ligne concernée à la premoière ligne de l'editeur. Est ce clair


## V1.6.4 Click Nuage/Mots et Création panneau Résultat de Recherche

- dans le nuage de tag Quand on clique sur un tag , il est inséré dans le champ de recherche de du panneau navigation et il est préfixé par @@
- lorsque je clique sur le tag il est bien inséré dans le champ de recherche mais le panneau Nuage de tags est effacé. Ce n'est pas ce que je veux. Le paneau  du nuage de tags doir rester rempli comme avant le clic
 - mplémenter exactement le meme modele pour le click de Mots dans nuage de mots. la seule differences est que le mot dans le champ de recherche ne doit pas apparaitre précédé de @@. Sinon idem pour les couleur, le theme 
- definition d'un nouveau panneau qui sera affiché dans le panneau Navigation ce nouveu panneau sera appelé dès que l'on lance une recherche à partir du champ recherche dès qu'il y a un mot ou un tag dans le champ rechercher. Ce panneau Résultats de Recherche s'affichera alors à la place de Nuage de Tags et de Nuage de Mots donc en dessous du champ recherche.. Après une recherche on concerve affiché le tag ou le mot affiché dans le champ Recherche. Lorsque l'utilisateur vide le champ recherche (efface TOUS les caractères) on viendra alors afficher Nuage des Tags et Nuage de Mots à la place du Panneau Résultats de Recherche



## V1.6.3 Nuage de mots et tags du journal

- dans la liste des mots à exclure du nuage de tags donné par l'utilisateur i faut appliquer cette exclusion a toutes les formes du mot , quel que sout les majuscules ou minuscules dans le mots ou bien que certains caractères soit accentués ou pas

dans tag_cloud.py
```

   def _normalize_tag(self, tag_text: str) -> str:
        """Convertit un tag en minuscules et sans accents pour la comparaison."""
        # Convertit en minuscules et décompose les caractères accentués
        nfkd_form = unicodedata.normalize("NFKD", tag_text.lower())
        # Conserve uniquement les caractères non-combinants (supprime les accents)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

```

- Afficher un nuage de mots en dessous de nuage de tags sur le meme modèle que que nuage de tags.
- il faut s'appuyer sur le fichier index_words.json qui est dans le repertoire du journal
- les nuages de tags et mots ne seront reinitialisé qu'au demarrage de l'application 
- il faut ajouter une préférences utilisateur qui est Mots à exclure du nuage et stocker cette preference dans le fichier settings.json
- la taille et les contraintes d'affichage seront identiques pour le nuage de mots que celle du nuage de tags
- le nuage de Mots sera affiché en dessous du nuage de tags
- Il faut n'afficher dans le nuage de mots que les 40 premiers mots triés par occurence. les tailles de la polices sera calculés uniquement sur les occurences de ces 40 Premiers


BlueNotebookV1.6.3beta2

- Il faut maintenat afficher un champ d Recherche qui permette à  l'utilsateur de saisir un tag pour une recherche ultérieure.
- Ce champ de saisie sera possitionné entre le widget calendrier et le nuage de tags.
- en grise sera écrit tag dans de champ mais des que l'utilisateur saisi un texte c'est le texte qui s'affiche dans le champ à saisir
- cette zone de saisie prendra toute la largeur du panneau Navigation

BlueNotebookV1.6.3beta3

- dès que l'utilisateur comment à taper on vien ajouter @@ devant les caracteres qu'il saisi
- ajourter dans ce champ de saisie sur la droite une icone que l'utilisateur peut cliquer pour lancer la recherche


BlueNotebookV1.6.3beta4

- a droite du champ de recherche je veux un bouton ayant pour label "v" pour faire faire apparaitre  une liste déroulante qui contien tous les tags importé du fichier index_tags.json classé par ordre alphabétique. Si un éléments est selectionné (clické)  dans la liste il s'affichera dans le champ de Rechrche de tag

- la hauteur du bouton qui lance la liste déroulante ne prend pas toute la hauteur du panneau de recherche de tag et apparait donc plus petiti que le champ de recher en hauteur

## V1.6.2 Nuage de tags

- Dans l'oglet navifgation ajourter un panneau de la meme taille que le calendrier (meme largeur et meme hauteur) dans lequel on va afficher une représentation e mode "nuage" des tags indexés.
- Les informations sur lesquelles est contruit le nuage de tags est le fichier index_tags.json du répertoire du journal courant.
- l'affichage est textuel et le nombre d'occurences des tags est représenté par la taille de la police de caractère.
- on définira au max 5 tailles de polices (occurences de 0 à 2)
- la police utilisée est la meme que Calendier
- A terme ces tags seront clickables

- filtrer les tags affiché dans le nuage de tag. ajouter dasn préférence général "Tags a exclure du nuage" une liste des tags choisi par l'urilisateur qu'il ne faut pas afficher dans le nuage. et sauvegardé dans le préferences utilisateur

- les differents élements du panneau Naavigation sont de taille fixe 400px en largeur et ils ne doivent pas se deformer si l'on étire le pannean vers le bas . ils sont tous collés les un aux autres meme s'il reste de la place en bas du panneau. La taille du panneau Naviagtion doit faire égalemnt 400 px de largeur et ne pas se déformer
 
- Set taille widget Navigation (largeur fixe de 400)
        self.calendar.setFixedSize(400, 250)
        self.tag_cloud.setFixedSize(400, 300)


## V1.6.1  Spécifications Indexation des mots du journal

- de la meme manière que le fichier index_tag.json indexe les tags dans le document je voudrais que soient indexés  les mots dans les notes du journal. Au démarrage lancer indexation des tags et des mots de manière asynchrone
- A exclure de l'indexation les signes de ponctuation, les pre positions, les caractères spéciaux, les tags précédés de @@
- Dans Préférence onglet Général permettre à l'utilisateur d'ajourter des mots à exclue
- Le fichier d'index de mots "index_words.json" sera sauvegardédans le répertoire Journal
- On ne lancera l'indexation qu s'il existe des notes d'une date supérieure à celle du dernier  fichier index_words.json
- un fichier index_word.csv sera crée également
- le fichier index_words.json  et index_words.cvs auront une strucuture similaire à index_tags.json et index_tags.csv Pour chaque mot indexé (Mot, occurences details (contexte, fichier, date))
- pour chaque mot indexé on stockera le nombre d'occurence
- A la fin du processus  asyncrone d'indexation indiquer comme aujourd'hui dans la barre d'état les tatistiques  concernant tags et mots
- ajouter exclure de l'indexarion les mots ne contenant que des chiffres, les mots ne contenant pas des lettres, les adverbes. dasn la liste des mots à exclure de Préférences n'afficher que la liste des mots à exclure rajoutés par l'utilisateur en plus de ceux choisi par le programme

- réorganiser la barre d'état en bas de la fenètre principale
- A gauche on ne touche pas au nom du fichier mais on vien coller les statistique du document en cours d'édition
- A droite on affiche les information sur le journal + Les information d'indexation (tags et mots) dans la meme couleur que le nom du journal
- on rajoute une boite a cocher dans l'onglet Général de Préférences demandant si l'on veut afficher les statistiques de mots et tags

## V1.5.4 Reorganisation Préférences
preferences_dialog.py  

- Transfert de la police : J'ai déplacé le code de création du bouton de sélection de la police de l'onglet "Général" vers l'onglet "Affichage" et je l'ai placé en première position.
- Renommage du label : Dans l'onglet "Affichage", le label "Couleur des titres:" a été mis à jour en "Couleur des titres Markdown:".
- Déplacement et renommage du bouton de réinitialisation :Le bouton "Remise à 0" a été renommé en "Valeurs d'affichage par défaut". Son code a été déplacé de l'onglet "Général" vers la fin de l'onglet "Affichage".
 
L'onglet "Général" est maintenant vide, mais je l'ai conservé pour de futures options de configuration qui ne seraient pas liées à l'affichage.

## V1.5.3 Fix Issue #11 Barre de défilement Editeur et Outline pas visible

La barre de defilement à droite de l'editeur et Plan du document l'Indicateur de progression du defilement n'es pas visible (noir sur noir) --> changer sa couleur en gris clair

Pour corriger cela, j'ai ajouté des règles de style spécifiques pour la barre de défilement du panneau "Plan du document". L'indicateur (la poignée) sera maintenant gris clair, ce qui le rendra bien visible sur le fond sombre.

dans editor.py et outline.py

```python

            /* Style pour la barre de défilement verticale */
            QScrollBar:vertical {{
                border: none;
                background: #e0e0e0; /* Fond de la barre de défilement */
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #b0b0b0; /* Couleur de l'indicateur (gris clair) */
                min-height: 25px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background: #a0a0a0; /* Un peu plus foncé au survol */
            }}

```

## V1.5.2 Fix Issue #10 Claude - Sync btw Outline and Editor

### Problème identifié 
La méthode ensureCursorVisible() centre le curseur dans la vue au lieu de le placer en haut, et elle peut ne rien faire si le curseur est déjà visible.
Solutions apportées :

### Positionnement précis du curseur 
Le curseur est d'abord positionné correctement sur le bloc correspondant au heading.

### Défilement contrôlé
Au lieu de se fier à ensureCursorVisible(), la méthode :

Utilise d'abord ensureCursorVisible() pour s'assurer que le curseur est dans la zone visible
Puis ajuste manuellement la position de scroll pour placer le heading en haut

###  Approche itérative

La méthode fait jusqu'à 3 tentatives d'ajustement pour être sûre que le positioning est correct, avec un processEvents() entre chaque tentative pour laisser le temps au widget de se mettre à jour.

###  Gestion des cas limites :

- Vérifie si le curseur est déjà proche du haut (moins de 20 pixels) avant d'ajuster
- Respecte les limites de la scrollbar (minimum 0, maximum scrollbar.maximum())
- Ajoute une marge de 10 pixels depuis le haut pour un meilleur rendu visuel

Cette solution devrait résoudre les deux problèmes que vous avez mentionnés :

- Les headings seront toujours positionnés en première ligne, même s'ils sont déjà visibles
- Les headings en fin de document seront aussi correctement positionnés en haut quand c'est possible

## V1.5.1 Panneau "Plan du document" et Préférences d'Affichage des Panneaux

Cette version introduit deux fonctionnalités majeures pour améliorer la navigation dans les documents et la personnalisation de l'espace de travail.

### 1. Nouveau Panneau : "Plan du document" (Outline)

Un nouveau panneau a été ajouté à l'interface principale, se positionnant entre le panneau "Navigation" et l'éditeur.

*   **Fonctionnalité** : Il affiche en temps réel une vue hiérarchique de tous les titres (headings : `#`, `##`, etc.) présents dans le document que vous éditez. Les titres sont indentés pour refléter leur niveau.
*   **Navigation Rapide** : Chaque titre dans le plan est cliquable. Un clic déplace le curseur dans l'éditeur à la ligne correspondante et fait défiler la vue pour la rendre visible.
*   **Cohérence Visuelle** : Le panneau hérite des styles de l'éditeur (police, couleur de fond, couleur des titres) pour une expérience unifiée.
*   **Contrôle de l'Affichage** : Le panneau peut être masqué/affiché via le menu `Affichage > 📜 Basculer Plan du document` (raccourci `F7`).

### 2. Nouvel Onglet "Panneaux" dans les Préférences

Un nouvel onglet a été ajouté à la fenêtre `Préférences` pour vous permettre de configurer votre espace de travail par défaut.

*   **Personnalisation au Démarrage** : Vous pouvez désormais choisir quels panneaux sont visibles au lancement de l'application.
*   **Interface** : Des cases à cocher permettent d'activer ou de désactiver les panneaux suivants :
    *   Panneau de Navigation
    *   Panneau 'Plan du document'
    *   Panneau 'Aperçu HTML'
*   **Persistance** : Vos choix sont sauvegardés dans `settings.json` et restaurés à chaque démarrage.
*   **Configuration par défaut** :
    *   Navigation : Fermé
    *   Plan du document : Ouvert
    *   Aperçu HTML : Fermé

### 3. Autres modifications

*   Le texte du menu "Basculer l'Aperçu" a été clarifié en "Basculer Aperçu HTML".
*   L'onglet "Intégrations" dans les préférences a été restauré.
*   Correction de bugs liés à la création du panneau "Plan du document" et à la navigation.

## V1.4.5 Préférences couleurs des headings et sélections de texte  

## V1.4.4 Editeur Coloration syntaxique Sélection et Tag Headings Markdown

dans editor.py Nouvelle couleur texte sélectionné

```python

        # Style amélioré couleur rouge
        # V1.4.4 Editeur Surlignage en Jaune lors de sélection
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                background-color: #d6ebff;
                selection-background-color: #ffffff; 
                color: #2c3e50;
                selection-color: #ff0004;
            }
            
            QTextEdit:focus {
                border: 2px solid #3498db;
            }
        """
        )
```


dans editor.py Nouvelle couleur heading format.setForeground(QColor("#208bd7"))

```python
    def setup_formats(self):
        """Configuration des formats de coloration"""
        # Format pour les titres
        self.title_formats = []
        for i in range(1, 7):
            format = QTextCharFormat()
            format.setForeground(QColor("#208bd7"))
            format.setFontWeight(QFont.Bold)
            format.setFontPointSize(16 - i)
            self.title_formats.append(format)

```
## V1.4.3 Document fonctionnalités Settings 

--> docs/V1.4.3_settings.md

documenter les fichiers settings.json dans ~/.config/settings.json
```json
{
    "editor": {
        "font_family": "Droid Sans Mono",
        "font_size": 12,
        "background_color": "#d6ebff",
        "text_color": "#2c3e50"
    },
    "integrations": {
        "show_quote_of_the_day": true
    }
}
```
ainsi que le fichier core/settings.py avec la Classes SettingManager()

preferences_dialog.py

Correction de la boite de dialogue Raz (supprime Yes et No --> Valider et Annuler)
```python
    def _reset_settings(self):
        """Affiche une confirmation et réinitialise les paramètres."""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            "Êtes-vous sûr de vouloir réinitialiser toutes les préférences aux valeurs par défaut ?\n"
            "L'application devra être redémarrée pour appliquer tous les changements.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
```


## V1.4.2 Fix bug Crash if show_quote_of_the_day is false - set a default value

preferences_dialog.py
```python
class PreferencesDialog(QDialog):
  .....
        # V1.4.2 Fix bug Crash if show_quote_of_the_day is false - set a default value
        # is_checked = self.settings_manager.get("integrations.show_quote_of_the_day")
        is_checked = self.settings_manager.get(
            "integrations.show_quote_of_the_day", False
        )
```
## V1.4.1 Ajouts d'un panneau Préferences dans BlueNotebook (Priority 2)

Ce panneau est le centre de contrôle pour personnaliser l'apparence et le comportement de l'application BlueNotebook.

### Accès et Structure Générale du panneau Préferences

*   **Accès** : On ouvre ce panneau via le menu `Fichier > ⚙️ Préférences...`.
*   **Structure** : C'est une fenêtre de dialogue (`QDialog`) qui contient un système d'onglets (`QTabWidget`) pour organiser les différents paramètres. En bas, deux boutons permettent de `Valider` les changements ou de les `Annuler`.

### Onglet "Général"

Cet onglet se concentre sur les paramètres fondamentaux de l'éditeur.

*   **Police de l'éditeur** :
    *   **Fonctionnalité** : Permet de choisir la famille de police (ex: "Droid Sans Mono", "Consolas") et sa taille.
    *   **Interface** : Un bouton affiche la police actuelle (ex: `Droid Sans Mono, 12pt`). Un clic sur ce bouton ouvre la boîte de dialogue standard de sélection de police de votre système.

*   **Remise à 0** :
    *   **Fonctionnalité** : C'est le bouton de "Remise à Zéro" (RaZ). Il réinitialise **toutes** les préférences de l'application (police, couleurs, etc.) à leurs valeurs par défaut.
    *   **Interface** : Un bouton `Remise à 0`.
    *   **Fonctionnement détaillé** :
        1.  Affiche une boîte de dialogue pour **confirmer** l'action, prévenant l'utilisateur qu'un redémarrage est nécessaire.
        2.  Si l'utilisateur confirme, il appelle la méthode `settings_manager.reset_to_defaults()` qui supprime le fichier de configuration `settings.json` et le recrée avec les valeurs d'usine.
        3.  Affiche un message d'information confirmant la réinitialisation.
        4.  Ferme la fenêtre des préférences **sans sauvegarder** les choix qui étaient affichés à l'écran, pour s'assurer que ce sont bien les valeurs par défaut qui seront utilisées au prochain démarrage.

### Onglet "Affichage"

Cet onglet est dédié à la personnalisation visuelle de la zone d'écriture.

*   **Couleur de fond de l'éditeur** :
    *   **Fonctionnalité** : Permet de choisir une couleur de fond pour la zone où vous tapez le texte.
    *   **Interface** : Un bouton dont la couleur de fond reflète la couleur actuellement sélectionnée. Un clic ouvre le sélecteur de couleurs.

*   **Couleur de la police de l'éditeur** :
    *   **Fonctionnalité** : Permet de choisir la couleur du texte dans l'éditeur.
    *   **Interface** : Similaire au choix de la couleur de fond, un bouton affiche la couleur du texte choisie.

### Onglet "Intégrations"

Cet onglet gère les fonctionnalités qui interagissent avec des services externes ou des modules optionnels.

*   **Afficher la citation du jour au démarrage** :
    *   **Fonctionnalité** : Permet d'activer ou de désactiver l'affichage de la fenêtre "Citation du Jour" qui apparaît au lancement de l'application.
    *   **Interface** : Une simple case à cocher (`QCheckBox`).

En résumé, le panneau des préférences offre un moyen simple et organisé de personnaliser les aspects les plus importants de l'expérience utilisateur, avec une fonction de réinitialisation sécurisée pour revenir facilement à la configuration initiale.

## V1.3.3 Correctif sur la boite de Dialogue de Restautation

Label "Valider" et "Annuler" et texte affiché formatté correctement
Mise à jour du menu dans Aide en ligne et footer

## V1.3.2 Menu "Fichier" regroupement des actions relatives au "Journal"

la nouvelle structure du menu "Fichier" après les derniers changements.

J'ai mis en évidence le nouveau groupement des actions relatives au "Journal" pour que vous puissiez bien voir la différence.

```
📁 Fichier
├── 📄 Nouveau
├── 📂 Ouvrir
├── ---
├── 💾 Sauvegarder
├── 💾 Sauvegarder sous...
├── ---
│
├── 📓 Ouvrir Journal           ┐
├── 💾 Sauvegarde Journal...    ├─  (Actions groupées pour le Journal)
├── 🔄 Restauration Journal...  ┘
├── ---
│
├── 🌐 Exporter HTML...
├── ---
└── 🚪 Quitter (Ctrl+Q)

```


## V1.3.1 Mise en place Sauvegarde/Restauration Journal

####  Résumé des fonctionnalités de Sauvegarde et Restauration

Voici un résumé des fonctionnalités de sauvegarde et de restauration que j'ai implémentées dans BlueNotebook.

##### 1. Sauvegarde du Journal (`Fichier > Sauvegarde Journal...`)

Cette fonctionnalité vous permet de créer une archive complète de votre journal en quelques clics.

*   **Simplicité** : Une seule action dans le menu lance le processus.
*   **Nommage intelligent** : Un nom de fichier par défaut est proposé, incluant le nom de votre journal et la date du jour (ex: `BlueNotebook-Backup-MonJournal-2025-09-26.zip`), mais vous restez libre de le modifier.
*   **Exhaustivité** : L'intégralité du répertoire de votre journal est compressée dans une seule archive `.zip`.
*   **Confirmation** : Une fois la sauvegarde terminée, un message vous confirme le succès de l'opération et l'emplacement du fichier.

##### 2. Restauration du Journal (`Fichier > Restauration Journal...`)

La restauration a été conçue avec la sécurité de vos données actuelles comme priorité absolue.

*   **Sélection facile** : Vous choisissez simplement l'archive `.zip` que vous souhaitez restaurer.
*   **Sécurité avant tout (pas de destruction)** : Votre journal actuel est **sauvegardé** en étant renommé (ex: `MonJournal.bak-20250926-103000`). **Vos données actuelles ne sont jamais supprimées.**
*   **Confirmation éclairée** : Une fenêtre de dialogue vous demande de confirmer l'opération en vous indiquant précisément le nom du fichier de sauvegarde qui vient d'être créé pour votre journal actuel.
*   **Redémarrage nécessaire** : Pour garantir que l'application charge correctement le nouveau journal restauré, un message vous informe que l'application va se fermer. Il vous suffira de la relancer.

En résumé, vous disposez maintenant d'un outil de sauvegarde simple et d'un outil de restauration qui protège vos données existantes avant toute modification.


## V1.2.3 Déplace le menu Inserer dans la barre de Menu

Rendre le menu "Insérer" plus accessible en le plaçant au premier niveau de la barre de menus améliorera certainement l'expérience utilisateur. MaJour de la doc technique V1.2.3 et de l'aide en ligne

```
👁️ Affichage
..
🎨 Formater
...
➕ Insérer
├── 🔗 Lien (URL ou email) (<url>)
├── 🖼️ Image (<img ...>)
├── 🔗 Lien Markdown (texte)
├── 🔗 Fichier
├── ---
├── ➖ Ligne Horizontale
├── ▦ Tableau
├── 💬 Citation
├── ✨ Citation du jour
├── ---
├── 🏷️ Tag (@@)
├── 🕒 Heure
├── ---
├── 😊 Emoji
...
❓ Aide
..
```

## V1.2.2 Changement format de date dans la template par defaut de l'editeur

Le changement a été effectué dans le fichier `bluenotebook/gui/main_window.py`.

```diff
--- a/bluenotebook/gui/main_window.py
+++ b/bluenotebook/gui/main_window.py
@@ -647,7 +647,7 @@
             except locale.Error:
                 locale.setlocale(locale.LC_TIME, "")  # Utiliser la locale système
 
-            today_str = datetime.now().strftime("%A %d %B %Y").capitalize()
+            today_str = datetime.now().strftime("%A %d %B %Y").title()
             template = f"""______________________________________________________________
 
 # {today_str}
 ```

## V1.2.1 Panneau a gauche Nommé Navigation qui affiche un Qt Calendar Widget et bouton de Navigation
panneau a gauche de l'editeur nommé Navigation qui affiche en haut un Qt Widget Calendar . ce panneau dispose d'un choix de menu dans le Menu Affichage ce sous menu est appeler Basculer Naviagtion avec une icone comme pour basculer apercu.

```
👁️ Affichage
├── 🧭 Basculer Navigation (F6)
└── 👁️ Basculer l'aperçu (F5)

```
 Le comportement sera le meme que pour basculer apercu c'es ta dire q'un clic fera se fermer le panneau Navigation puis sun autre click fera reapparaitre le panneau Navigation
## 

## V1.2 --- Focus Navigation  (Calendar, Fleches, Nuage de Mots, Tags, Nuages  de Tags)

## V1.1.19 Ajout Menu Inserer Emoj 

Dans le menu Formater je souhaite rajouter un sous menu appelé Emoji qui permette d'insérer les emoli suivant: 
 Livre, Musique, A  Lire, Casque Audio, Voyage, Santé, Soleil, Nuage , Pluie, Nuage, Vent, Content, Mécontent, Triste.
Chaque Label Textuel de sous menu  sera accompagné de son Emoji 📖 🎵

├── 😊 Emoji
│   ├── 📖 Livre
│   ├── 🎵 Musique
│   ├── 📚 À Lire
│   ├── 🎬 À Regarder
│   ├── 🎧 A Ecouter
│   ├── ✈️ Voyage
│   ├── ❤️ Santé
│   ├── ☀️ Soleil
│   ├── ☁️ Nuage
│   ├── 🌧️ Pluie
│   ├── 🌬️ Vent
│   ├── 😊 Content
│   ├── 😠 Mécontent
│   └── 😢 Triste



## V1.1.18 Mise en place Licence GNU GPLv3

https://www.gnu.org/licenses/gpl-3.0.html

Entete des fichiers Python, A Propos Aide en Ligne

## V1.1.17 Fix Issue #6 Message transient on save file

file main_windows.py  -> Passe timeou 2000 -> 2

self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2)
self.statusbar.showMessage(f"Contenu ajouté à : {filename}", 2)

## V1.1.16 Barre status - Couleur affichage nom du fichier - Etat de sauvegarde du fichier courant

Gestion des couleurs pour l'état de sauvegarde du fichier dans la barre de statut. C'est une excellente idée pour améliorer la visibilité de l'état du document.

A l'ouverture la police de caractère utilise la couleur blanche.
Des que le fichier est modifié et pas sauvegardé le fichier passe au rouge et dès qu'il vient d'etre sauverardé il passe au vert

main_window.py --> Classe MainWindow(QMainWindow) --> fonction setup_statusbar(self):

 

## V1.1.15 Creation asynchrone d'un index de tags au démarrage txt, csv et JSON

Ajout d'une fonctionnalité de recherche puissante. L'indexation asynchrone des tags permettra de ne pas ralentir le démarrage de l'application tout en préparant les données pour une future utilisation.

fichier tag_indexer.py --> class TagIndexer(QRunnable)

Le fichier `index_tags.txt` est un simple fichier texte créé **dans le répertoire du Journal courant** où chaque ligne représente une occurrence d'un tag trouvé dans vos fichiers de journal (.md).
Le format est le suivant:
*@@tag++contexte du tag++nom_du_fichier.md*
```
Description des parties :
@@tag

C'est le tag lui-même, tel qu'il a été trouvé dans le fichier. Par exemple, @@projet ou @@idee.
++

C'est un séparateur fixe utilisé pour délimiter les différentes parties de l'information.
contexte du tag

Il s'agit des 40 caractères qui suivent immédiatement le tag sur la même ligne dans le fichier source. Cela permet de donner un aperçu rapide de l'endroit où le tag a été utilisé. Les espaces au début et à la fin de ce contexte sont supprimés.
++

Le même séparateur.
nom_du_fichier.md

C'est le nom du fichier (par exemple, 20240927.md) dans lequel le tag a été trouvé.
```

Affichage du résultat d'indexation dans la console et dans la barre de status de la fenètre blueNotebook

✅ Index Tags Terminé: 7 tags uniques trouvés.

Etendre la fonctionnalité d'indexation pour générer également des fichiers CSV et JSON en plus du fichier texte existant. Cela offrira plus de flexibilité pour exploiter les données des tags à l'avenir.

fichier JSON ìndex_tags.json

```json
{
  "@@projet": {
    "occurrences": 2,
    "details": [
      {
        "context": "avancement sur le projet BlueNotebook",
        "filename": "20240927.md",
        "date": "2024-09-27"
      },
      {
        "context": "réunion de suivi pour le projet Alpha",
        "filename": "20240928.md",
        "date": "2024-09-28"
      }
    ]
  },
  "@@idee": {
    "occurrences": 1,
    "details": [
      {
        "context": "une nouvelle fonctionnalité pour l'app",
        "filename": "20240927.md",
        "date": "2024-09-27"
      }
    ]
  }
}
```


## V1.1.14 Syncronisation panneau Editeur et panneau Apercu HTML

 La synchronisation du défilement (scroll sync) est une fonctionnalité clé pour les éditeurs Markdown.

Faire défiler le panneau de l'éditeur, le panneau de l'aperçu HTML se déplacera en tandem pour afficher la section correspondante du document.

## V1.1.13 Changement de la page par defaut de l'editeur et colorations des tags en HTML

1
main_windows.py --> fonction new_file(self)
Lorsque l'on crée un nouveau document, on applique par defaut une page au format Markdown qui est une template de page de Journal.

2
Changement entête
previews.py --> class MarkdownPreview(QWidget):
label = QLabel("👀 Aperçu HTML")

3
Changement entête
editor.py --> class MarkdownEditor(QWidget) --> fonction setup_ui(self)
label = QLabel("📝 Éditeur Markdown")

4
Pour que les tags apparaissent en rouge également dans l'aperçu HTML, il faut modifier le moteur de rendu Markdown pour qu'il reconnaisse et stylise spécifiquement les tags @@....
Pour l'appliquer à l'aperçu, nous devons utiliser une extension Markdown qui va transformer @@tag en une balise HTML spécifique (par exemple <span class="tag">tag</span>), puis ajouter le style CSS correspondant.

une balise HTML spécifique (par exemple, <span class="tag">tag</span>) et ajouter le style CSS correspondant
ajouter une extension Markdown personnalisée qui s'occupe de cette transformation et ajout le style CSS nécessaire.

## V1.1.12 Zoom Editeur avec la Molette

Pour améliorer l'ergonomie de l'éditeur. Pour implémenter le zoom avec CTRL + Molette, il faut intercepter l'événement de la molette de la souris dans le widget de l'éditeur.


## V1.1.11 Insertion d'un "Internal Link" vers  un fichier

Ajouter dasn le mene Formater -> Insérer -> Fichier
qui permette à l'utilisateur de choisir un fichier dans le répertoire de fichier puis qui insere un lien Markdown vers ce fichier sous la forme
[An Internal Link](/guides/content/editing-an-existing-page)
en mettant entre crocher [] le nom+extension fichier sans le path

exemple:
 [Twitter-Logо.png](file:///home/jm/Images/pixmaps/Twitter-Log%D0%BE.png)

```
├── ➕ Insérer
│   ├── 🔗 Lien (URL ou email) (<url>)
│   ├── 🖼️ Image (<img ...>)
│   ├── 🔗 Lien Markdown (texte)
│   ├── 🔗 Fichier
│   ├── ▦ Tableau (|...|)
│   ├── ➖ Ligne Horizontale (---)
│   ├── 💬 Citation (> texte)
│   ├── ✨ Citation du jour
│   ├── 🏷️ Tag (@@)
│   └── 🕒 Heure (HH:MM)
```



## V1.1.10 Modifier la couleur de fond de l'editeur + Tag formating

HTMLColors `#d6ebff`

editor.py --> background-color: #d6ebff;
```python

        # Style amélioré
        self.text_edit.setStyleSheet(
            """
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 10px;
                background-color: #d6ebff;
                selection-background-color: #3498db;
                color: #2c3e50;
                selection-color: white;
            }

```

**10:54**
Ajout Tag formating
 
```
🎨 Formater
  └── ➕ Insérer

      ├── 🏷️ Tag  (@@)
      └── 🕒 Heure
```



## V1.1.9 Insertion  de l'heure par menue Formater + Emojs Menus

Je veux pouvoir inserer l'heure directement dans l'éditeur Markdown
Ajout d'un choix de menu Formater - > Insérer -> Heure. Insérer la chaine de caractère HH:MM correspondanst à l'heure locale . Ne pas ouvlier d'accmpagner le laber Heure d'une petite icone.

Modifier le fichier de documentation docs/V1.1.8 bluenotebook_technical_doc.md en modifiant le representaion graphique de la barre de menu pour y ajouter le sous menu heure

Dans le menu inserer les differents items sont des labels texte uniquement. Ajouter une emoj pour chacun deux avant le label (Lien, Image, ....Heure)

── ➕ Insérer
│   ├── 🔗 Lien (URL ou email) (<url>)
│   ├── 🖼️ Image (<img ...>)
│   ├── 🔗 Lien Markdown (texte)
│   ├── ▦ Tableau (|...|)
│   ├── ➖ Ligne Horizontale (---)
│   ├── 💬 Citation (> texte)
│   ├── ✨ Citation du jour
│   └── 🕒 Heure (HH:MM) 
├── ---
└── 🧹 RaZ (Effacer le formatage)

❓ Aide
├── 🌐 Documentation en ligne
└── ℹ️ À propos

## V1.1.8 Changement de la police de caractères de l'editeur

Dans `editor.py ` remplace la police "*Courier New*" par "*Droid Sans Mono*" qui est la police utilisée dans VSCode

## V1.1.7 Fix Issue #2 Markdown editor - coloration syntaxique nefonctionne pas

Re écriture de la classe MarkdownHighlighter.
Redéfinition du parser pour éviter un chevauchement des filtres

[#2](https://github.com/lephotographelibre/BlueNotebook/issues/2) 


## V1.1.6 Citation du jour

Pour récupérer une citation du jour en français + Menu Inserer Citation du jour comme quote Markdown

https://citations.ouest-france.fr/ + WebScrapping


## V1.1.5 Aide en ligne

Création d'une page d'aide de documentation en ligne menu Aide -> Documentation en ligne. le fichier html de la page d'aide est stocké dans le repertoire bluenotebook/resources/html/ et se nomme  bluenotebook_aide_en_ligne.html

## V1.1.4 Ajout Menu Formater 

Le menu est organisé en sous-menus logiques pour un accès facile aux différentes options de formatage.

```text
Formater
├── 📜 Titre
│   ├── Niv 1 (#)
│   ├── Niv 2 (##)
│   ├── Niv 3 (###)
│   ├── Niv 4 (####)
│   └── Niv 5 (#####)
│
├── 🎨 Style de texte
│   ├── Gras (**texte**)
│   ├── Italique (*texte*)
│   ├── Barré (~~texte~~)
│   └── Surligné (==texte==)
│
├── 💻 Code
│   ├── Monospace (inline) (`code`)
│   └── Bloc de code (```...```)
│
├── 📋 Listes
│   ├── Liste non ordonnée (- item)
│   ├── Liste ordonnée (1. item)
│   └── Liste de tâches (- [ ] item)
│
├── ➕ Insérer
│   ├── Lien (URL ou email) (<url>)
│   ├── Image (<img ...>)
│   ├── Lien Markdown (texte)
│   ├── Tableau (|...|)
│   ├── Ligne Horizontale (---)
│   └── Citation (> texte)
│
├── --- (Séparateur)
│
└── 🧹 RaZ (Effacer le formatage)
```


## V1.1.3 Fix Bug #1 Cannot see HTML fragment pasted into the editor

       padding: 10px;
                background-color: #ffffff;
                selection-background-color: #3498db;
                color: #2c3e50;   ---> Ajouté
                selection-color: white;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
            }

## V1.1.2   Création d'en script de lancement

Je voudrais un script bash pour linix et un script pour windows pour lancer le programme bluenotebook. sur Linux bien vérifier que l'in est dasn un terminal bash ce script doit positionner l'environnement virtuel pyenv nommé .venv_bluenotebook avec Python 3.13.5, verifier le bon chargements des packages qui sont dans requirements.txt, puis lancer le programme main.py

1
bluenotebook$ ./run_bluenotebook.sh   --> Par defaut Journal dossier bluenotebook dans répertoire utilisateur
2
bluenotebook$ ./run_bluenotebook.sh --journal "/ssd/Dropbox/bluenotebook"
3
bluenotebook$ export JOURNAL_DIRECTORY="/home/jm/Work/BlueNotebook/"
bluenotebook$ ./run_bluenotebook.sh

et mettre a jour le dossier technique docs/V1.0 bluenotebook_technical_doc.md avec les nouvelles fonctionnalités décrites dans versions.md. 
Remettre à jour l'aborecence des fichiers

## V1.1.1   Fix gestion variable d'environnement JOURNAL_DIRECTORY

## V1.1.0   Gestion du répertoire Journal


## V1.0    Première release avec Qt (editeur Markdown + Preview)
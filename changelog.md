## V3.2.4 Refresh tag index Fix Issue [#63]

I would like to be able to refresh the tag index on demand by clicking on the index display in the bottom right corner of the main window.
Fix Issue [#63](https://github.com/lephotographelibre/BlueNotebook/issues/63) V3.2.3 main_windows: reload tag index #63


## V3.2.3 Fix Issue [#62] Notes Search

Fix Issue [#62](https://github.com/lephotographelibre/BlueNotebook/issues/62)  V3.2.2 Notes: Search keyworks is not working correctly #62

branch search_notes

1 supprimer tout le code   qui concerne la recherche notes dans notes_panel.py excepté le champ de recherche et le bouton rechercher peux tu me montrer sans toucher au code les impacts sur le code 
beta1


2 demander a grok de 
dans le panneau Notes 
- mettre en oeuvre une recherche simple sur tous les fichiers et repétoires  dont le nom contient cette chaine de caractère recherchée quelle que soit la casse
- quand l'utilisateur efface le critère de recherche reafficher l'arbre initial a partir de la racine notes
- quand l'utilisateur appuie sur le bouton rechercher Si des fichiers correspondent au critère de recherche, afficher les et déplier les répertoires où ils se trouvent upour afficher tous les fichiers résultats de la recherche
- afficher également dans la console la liste des fichiers correspondants au critère de recherche (path complet)
beta2

 


3 inclure les dossiers dans la recherche. 
Si un ou plusieurs dossier correspond au critère de recherche afficher le ou les dossier pour qu'il soit clickable et que l'on puisse l'ouvrir en cliquant dessus pour voir les fichiers qu'il contient
beta4

- Probleme de reset
beta5
 

si l'utilisateur saisi une chaine de recherche dans le champ de recherche et qu'il fair return cela doit avoir le meme effet que s'in appuie sur le bouton rechercher
beta6

## V3.2.2 Notes - Fix Issue [#58] Fix Issue [#57] Fix Issue [#59]


Fix Issue [#58](https://github.com/lephotographelibre/BlueNotebook/issues/55) V3.2.1 Notes: Cannot Resize Notes Panel #58

Le panneau "Notes" n'est actuellement pas redimensionnable en largeur, ce qui peut être contraignant. la cause est bien une largeur fixe qui lui est appliquée lors de la configuration de l'interface dans `main_window.py`
```python
 # self.notes_panel.setFixedWidth(400)
```

Fix Issue [#57](https://github.com/lephotographelibre/BlueNotebook/issues/57) V3.2.1 Notes: add size, Modify column to the file browser #57

je voudrais dans le panneau Notes pouvoir afficher en plus de la liste arborescente des fichiers les colonnes de taille,  type et date de derniere modification. Ces colonnes additionnelles sont affichées si l'utilisateur utilise CRTL-M et sont cachées si l'utilisateur utilise `CRTL-M`  a nouveau
beta1

Le panneau "Notes" je voudrais en haut du panneau faire apparaitre un champ de saisie et un bouton à sa droite qui à pour label "Rechercher".
le champ de recherche et le pouton prendront toute la largeur du panneu largueur qui sera redimmentionnée si le panneau Note est redommentionné
si rien n' été sais dans le champ de recherche era affiché en grisé "Tapez la chaine à rechercher".
Lorsque l'utilisateur appuie sur le bouton "Rechercher" on va rechercher dans toute l'arborescence tous les fichiers/dossiers qui contienne la chaine de cararctère saisie dans le champ de recherche, queque soient les majuscules, Minuscules, accents dans le nom des fichiers/dossiers. Les fichiers correspondants au critère de recherche seront affichés dans le TreeView.
L'utilisateur pourra réinitialiser la recherche par un icone effacer à droite dans le champ de recher et le TreeView sera réinitilisé.
Si au cun fichier ne correspond a cette recherche on ne modifira pas le TreeView et un message via une boite de dialogie sera affiché pour l'utilisateur
beta2

Tri sur les header de colonnes
je voudais que les colonnes du treeview puisse etre triée en cliquant sur le header des colonnes (Nom, Taille, Dernière Modification). Au click suivant sur le meme header le tri sera inversé
beta3

Fix Issue [#59](https://github.com/lephotographelibre/BlueNotebook/issues/59) V3.2.1 Notes: Open HTML Files in Notes with the Editor #59

Panneau Notes: je voudrais que lorsque l'on clique sur un fichier HTML qui est dans un dossier de Notes alors ce fichier soit ouvert dans l'editeur Markdown. Si un fichier est déja ouvert dans l'éditeur alors on demandera a l'utilisateur de Sauvegarder ou pas son document en cours avant d'ouvrir le fichier HTML dans l'éditeur et d'afficher l'aperçu HTML
beta4

aide en ligne a main.py

beta5

dans le Panneau Notes si je recherche la chaine "Spec" je trouve bien le dossier "Specs" qui apparait bien dans l'aborescence masi je ne peux cliquer dessus alors q'il contien des fichiers.  la premiere fois le repertoires Specs Trouvé est affiché avec un petite fleche a coté indiquant qu'il s agit d'un répertoire avec du contenu mais quand on clique de ssus le dossier ne s'ouvre pas et la flèche disparait.
Et quand je clique sur le dossier Specs dans la console s'affiche une suite de message
 


## V3.2.1 Directory Navigation Panel

Fix Issue [#53](https://github.com/lephotographelibre/BlueNotebook/issues/53) V3.1.4 Main Window: Add new panel: directory #53

 
git checkout -b notes_directory

 

Je voudrais crrér un nouveau panneau appelé Notes. Ce panneau apparaitra toujours a l'extreme gauche. 
Il faudra créer un bouton poussoir dans la  barre des bouton à gauche de "Navigation". 
ce panneau aura un label "Notes" sous la forme d'un onglet comme les autres panneaux (ex: Navigation"). et la vue arborescente prendra toute la place en hauteur.en dessous de l'onglet jusqu'au bas de la page. en largeur la taille initiale de ce panneau sera de 400px mais pourra etre agrandi.
Il fera apparaitre   une vue arborescente (QTreeView) affichant les fichiers du répertoire 'Notes' du journal et ses sous-répertoires avec des nœuds cliquables. les fichiers affichés seront uniquement du type Markdown, PDF, Images, Vidéos ou musique mp3 ou flac ou HTML ou epub. Le dossier séléctionné apparitra en surbillance.
Un menu contextuel de ce panneau 'Notes' permettra :
- soit de créer un fichier .md dans ce dossier puis de l'ouvrir dans l'éduteur après avoir demandé à l'utilisateur le nom de ce fichier (la séquence est l'utilsateur clique sur un dossier, puis ouvre le menu contextuel créer une note, une boite de dialogue est ouverte  ou l'utilisateur donne le nom du fichier et peut choisir un modèle  de document du dossier `bluenotebook/resources/templates/`, le fichier est créé dans le dossier,  affiché dans le dossier de la vue arbirescente et ouver dans l'éditeur.)
- soit d'ouvrir un fichier existant (dans l'editeur s'il s'agit d'un fichier .md ou .txt, dans le lecteur s'il s'agit d'un document pdf ou epub). Les fichiers images, video ou audio seront visualisé dans le navigateur externe par défault.
- soit de copir/deplacer, renommer, effacer un fichier

le dernier dossier sélectionné dans l'arbre sera persisté dans les préférences utilisateur (settings.json) afin qu'à l'ouverture de l'application ou ou l'ouverture du panneau 'Notes' le dernier dossier sélectionné apparaisse dans l'arbre, sélectionné et en surbrillance

beta2
new_file_dialog.py --> new_note_dialog.py ?

le nom du fichier gui/new_file_dialog.py n'est pas tres heureux. Peuc tu renommer ce fichier gui/
beta3
Panneau Note
- si rien n'est affiché ou sélectionné dans l'arbre, me menu contextuel doit poivoir 
    - créer un dossier à la racine des notes du journal (dossier `Journal/notes). un boite de dialogue doit pouvoir lui demander le nom du dossier à créer
- si un dossier est sélectionné 
    on doit poivoir à l'aide su menu contextuel créer un sous dossier  un boite de dialogue doit pouvoir lui demander le nom du dossier à créer
    on doit pouvoir supprimer un dossier s'il est vide apres affichage d'une boite de dialue " Le dossier xxxx est vide voulez-vous le supprimer ?"
    on doit pouvoir supprimer un dossier et ses sous dossiers mem s'il n'est pas vide .  apres affichage d'une boite de dialue " Le dossier xxxx n'est pas vide . Il contient X sous dossiers et Y fichiers Voulez-vous lTout supprimer   ?
beat4

Importer dans Notes 
- si un dossier est sélectionné 
    on doit poivoir à l'aide du menu contextuel "Importer un fichier" dans ce dosiier. Une noite de dialogue s'ouvre permettant de selectionner soit un fichier local soit un fichier distant via une URL. Le fichier sera importé/copié dans le dossier sélectionné s'il est d'un type valide c'est a dire:

            [
                "*.md",
                "*.txt",
                "*.pdf",
                "*.epub",
                "*.jpg",
                "*.jpeg",
                "*.png",
                "*.gif",
                "*.mp4",
                "*.avi",
                "*.mkv",
                "*.mp3",
                "*.flac",
                "*.html",
            ]
Si le fichier n'est pas d'un type valide alors afficher une boite de dialogue mentionant " Le fichier que vous voulez importer n'est pas supporté dans les notes. Les types valides sont uniquement: ... la liste des types supportés...
beta5



Avec la souris il sera possible de zommer/dezommer l'arbre.
icones systemes par default
beta6

peux tu implementer les fonctions de Presse-papiers (Couper/Copier/Coller) dans le panneau Notes

En complément du glisser-déposer, ajouter des options "Couper", "Copier" et "Coller" au menu contextuel. Cela permettrait une gestion plus flexible des fichiers et dossiers, notamment pour les déplacer entre des dossiers non visibles simultanément à l'écran.
beta7

si un dossier est sélectionné via le menu contextue on va pouvoir déplier tous les sous répertoires ou au contraire réplier tous les sous répertoires.
beta8

lorsque je suis sur un dossier je voudrai pourvoir choisir une couleur parmi 10 pour colorer ce dossier

A FAIE Redimmentionnement du panneau Notes





## V3.2.0 Add new English README.md + Images 

## V3.1.9 Refactoring Export PDF / Epub 
dans une demarche de refactoring je voudrais alléger le fichier `bluenotebook/gui/main_window.py`.
Dan sun premier temps je voudrais que les methodes 
- def export_pdf(self):
- def export_journal_pdf(self):
soient exportées dans le fichier `bluenotebook/integrations/pdf_exporter.py`. Verifie bien les exports
beta1

dans une demarche de refactoring je voudrais alléger le fichier `bluenotebook/gui/main_window.py`.
Dan sun premier temps je voudrais que la methode 
- def export_journal_epub(self):
soit exportée dans le fichier `bluenotebook/integrations/epub_exporter.py`. Verifie bien les exports
beta2

dans une demarche de refactoring je voudrais alléger le fichier `bluenotebook/gui/main_window.py`.

peux tu egalement déplacer la methode 
-  def restore_journal(self):
dans le fichier `bluenotebook/gui/backup_handler.py  
beta4

Peux tu afficher un message dans la console a la fin du backup et a la fin du restaure précédé de cet emoji 🔁
 
## V3.1.8 Export PDF
Voici une explication détaillée des étapes  pour ajouter une fonctionnalité d'exportation PDF pour un fichier Markdown ouvert, 

L'approche consiste à reproduire la logique de la fonction `export_html` existante et à l'adapter pour le format PDF en utilisant la bibliothèque `weasyprint`, qui est déjà utilisée ailleurs dans l' application.

Toutes les modifications se feront dans un seul fichier : `bluenotebook/gui/main_window.py`.


### Étapes à réaliser

#### 1. Créer une nouvelle action de menu

Dans la méthode `_create_actions`, il faudrait ajouter une nouvelle `QAction` pour le menu "Exporter en PDF...". Elle serait placée juste après l'action existante pour l'export HTML.

**Code à ajouter :**
```python
# Juste après self.export_action
self.export_pdf_action = QAction(
    "Exporter en PDF...",
    self,
    statusTip="Exporter le fichier actuel en PDF",
    triggered=self.export_pdf,  # On la connecte à une nouvelle méthode
)
```

#### 2. Ajouter l'action au menu "Fichier"

Dans la méthode `setup_menu`, il faudrait insérer cette nouvelle action dans le menu `file_menu`.

**Code à ajouter :**
```python
# Dans file_menu, juste après self.export_action
file_menu.addAction(self.export_pdf_action)
```

#### 3. Implémenter la méthode `export_pdf`

C'est le cœur de la fonctionnalité. Il faudrait créer une nouvelle méthode `export_pdf` dans la classe `MainWindow`.

Attention à la résolution du chemin des images (tag liens Markdown de type [![2024_11_11_img_5812_01](images/20251110141452_2024_11_11_img_5812_01.jpg)](images/20251110141452_2024_11_11_img_5812_01.jpg)
- Les images sont toujours dans le sous-répertoire images du journal Journal/images.
- les fichiers Markdown a exporter en PDF peuvent etre:
    - soit des notes journalières (dans le répertoire "Journal")
    - Soit des notes (dans le répertoire "Journal/notes" et sous repertoires)
    mais dans les deux cas les liens sont toujours du meme type par exemple ([![2024_11_11_img_5812_01](images/20251110141452_2024_11_11_img_5812_01.jpg)](images/20251110141452_2024_11_11_img_5812_01.jpg)

beta1

dans le cas ou j'exporte en PDF une note journaliere c'est ok c'est a dire une note qui est dans le répertoire journal
mais dans le cas ou j'exporte en pdf une note qui est dans le répertoire (Journal/notes) ou un des sous répertoires cela ne marche pas par exemple il chercher a afficher une images comme [Le fichier ou le dossier /home/jm/Dropbox/BlueNotebookJournal/notes/Bluenotebook/images/20251110141452_2024_11_11_img_5812_01.jpg n'existe pas.](.) dans ce cas la notes est dans /home/jm/Dropbox/BlueNotebookJournal/notes/Bluenotebook/ et les images sont bien dans /home/jm/Dropbox/BlueNotebookJournal/images, alors que cette note dans l'apercu HTML affiche bien les images
- 
le Journal est dans /ssd/Dropbox/BlueNotebookJournal/ 
cela fonctionne si j'exporte en PDF une note qui est dans /ssd/Dropbox/BlueNotebookJournal/notes/Bluenotebook/ (les images sont bien affichées)
cela ne fonctionne pas si j'exporte en PDF une note qui est dans /ssd/Dropbox/BlueNotebookJournal/notes/Bluenotebook/ (les images ne sont pas bien affichées)
le lien dans le PDF est: file:///home/jm/Dropbox/BlueNotebookJournal/notes/Bluenotebook/images/20251110141452_2024_11_11_img_5812_01.jpg 
donc les images sont recherché en relatif par rapport la la localisation de la not et pas en absolu par rapport au répertoire images dans le Journal qui est /ssd/Dropbox/BlueNotebookJournal/images

beta2
mettre a jour aide ne ligne

## V3.1.7 Cleaning up the documentation


## V3.1.6 Fix Search Epub Full Text

lorsque je recherche un mot dans un fichier epub en utilisant la barre de recherche en haut de la page affichée,la recherche est aléatoire.
Parfois cela fonctionne, parfois cela ne fonctionne pas.
- Si je recherche un mot qui est sur la page affichée cela fonctionne, le mot et toutes ses occurences sont trouvés
- Si je recherche ce meme mot à partir d'une autre page affichée cela ne fonctionne pas
Est-ce volontaire, je voudrais que peu importe ll'endroit ou l'on se trouve dasn le document on puisse touver toutes les occurence du mot dans TOUT le document et se déplacer d'une occurrence à l'autre avec les boutons Suivant et Précédent

**Comportement actuel :**
- La recherche utilise QWebEnginePage.findText(), une méthode intégrée à Qt WebEngine. Celle-ci ne recherche que dans le contenu HTML chargé dans la vue web actuelle (c'est-à-dire le chapitre courant).
- Si le mot est dans le chapitre affiché, il est trouvé et surligné, et vous pouvez naviguer entre ses occurrences locales avec "Suivant" (findText() sans flag) et "Précédent" (findText() avec QWebEnginePage.FindBackward).
- Si le mot n'est pas dans le chapitre courant (ou si vous commencez la recherche depuis un autre chapitre), rien n'est trouvé, car la recherche ne s'étend pas aux autres chapitres. Ce n'est pas "aléatoire" : c'est limité par conception au chapitre chargé.
- c'est une limitation de l'implémentation actuelle. Le code charge les chapitres un par un pour des raisons de performance (les EPUB peuvent être volumineux), donc la recherche est locale par défaut.

**Ce que vous voulez :**
-Une recherche globale sur tout l'EPUB : trouver toutes les occurrences du mot dans tous les chapitres.
-Navigation fluide avec "Suivant" et "Précédent" : changer automatiquement de chapitre si l'occurrence suivante/précédente est ailleurs, et scroller/surligner le mot.

Ce n'est pas implémenté nativement, mais c'est tout à fait réalisable en modifiant le code. Je vais vous proposer une solution complète ci-dessous, sous forme de patch à appliquer à votre fichier epub_reader_panel.py. Cela impliquera :

- Une indexation des occurrences lors de la recherche initiale.
- Une gestion des résultats (liste de tuples : (chapitre_index, position_dans_texte)).
- Une navigation qui charge le chapitre cible et utilise findText() pour surligner et scroller.

MAJ Horodatage et A  Propos



## V3.1.5 Fix issue [#33] Add export pdf pour fichiers hors journal #33

Fix issue [#33](https://github.com/lephotographelibre/BlueNotebook/issues/33) 
Rendre le menu export html plus générique

V1.3.8


## V3.1.4 Fix issue [#50] V3.1.3 Lecteur: crash lors de l'ouverture de l'onglet lecteur
#50

Fix issue [#50](https://github.com/lephotographelibre/BlueNotebook/issues/50) 

D'après la trace d'erreur que vous avez fournie, le problème est très clair :

- Vous cliquez sur le bouton pour ouvrir le panneau "Lecteur".

- Le code vérifie si un document est déjà chargé en appelant epub_reader_panel.has_document().
Cette méthode, dans [epub_reader_panel.py](code-assist-path:/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/epub_reader_panel.py), vérifie à son tour si le pdf_viewer a un document chargé en appelant self.pdf_viewer.has_document().

- Le crash se produit ici : la classe PdfViewer dans [pdf_viewer.py](code-assist-path:/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/pdf_viewer.py) n'a pas de méthode has_document().

La solution est simple : il suffit d'ajouter cette méthode manquante à la classe PdfViewer.

Add pdf_viewer.py


```python
    def has_document(self):
        """Retourne True si un document PDF est chargé."""
        return self.doc is not None
```


## V3.1.3 Lecteur Fix Issue [#41] Fix Issue [#34] Fix Issue [#37]

Fix issue [#34](https://github.com/lephotographelibre/BlueNotebook/issues/34) Définir Menu contextuel en Français pour Lecteur
Fix Issue [#41](https://github.com/lephotographelibre/BlueNotebook/issues/41) V3.0.2 Main Windown: Modifier les menus ouvrir pour améliorer la comprehension
Fix Issue [#37](https://github.com/lephotographelibre/BlueNotebook/issues/37) V3.0.1 Lecteur EPUB: Affichage et copie des images du livre epub #37
 

## V3.1.2 Fix Issue [#47] +EPUB TOC et synchro navigation EPUB/PDF

Fix Issus [#47](https://github.com/lephotographelibre/BlueNotebook/issues/47)

TOC EPUB OK
beta1

TOC/NAV Sync + Wheel PDF OK
beta3

TOC/NAV Sync + Wheel Epub
beta4

 


## V3.1.1 Remove all the search words code

create new branch `remove_word_indexer`


Je veux supprimer tout le code qui était utilisé pour l'indexation de mots, la recherche de mots cela inclus
- word_indexer.py et tout le code associé
- default_excluded_words.py et tout le code associé
- les fichiers index_words.json index_words.cvv et tout le code associé
- dans Préférences -> Général --> Mots personnalisés à exclure de l'indexation
- dans Préférences -> Général --> Mots à exclure du nuage de mots
- dans le panneau Navigation le Nuage de Mots, le code lié à la recherche de mots e


This version removes all functionality related to word indexing and searching.

**Removed Files:**
- `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/core/word_indexer.py`
- `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/core/default_excluded_words.py`
- `/home/jm/PycharmProjects/BlueNotebook/bluenotebook/gui/word_cloud.py`

**Removed Functionality:**
- Word indexing and generation of `index_words.json` and `index_words.csv`.
- "Mots personnalisés à exclure de l'indexation" and "Mots à exclure du nuage de mots" settings in Preferences.
- The "Nuage de Mots" panel in Navigation.
- Display of word count in the status bar (tag count remains).
- All associated code for word searching in `main_window.py` and `navigation.py`.


 
Suppression des fichiers Python liés à l'indexation de mots. 

Les fichiers bluenotebook/core/word_indexer.py, 
bluenotebook/core/default_excluded_words.py et 
bluenotebook/gui/word_cloud.py 
beta1
 
modify aide_en_ligne.html

Maintenant qu'il n'y a plus d'indexation de mots, je voudrais dans le panneau navigation toujours afficher le panneau de resultat de recherche search_results_panel.py meme s'il n'y a pas eu encore de recher. ce panneau d'affichage de resultats de rechercher sera toujours présent et dessous le nuage de tag jusqu'en bas du panneau navigation. il prendra donc toute la place restant sous le nuage de tag.
beta2

Si aucune recherche n'a été éffectuée je veux que soient affiché par default, le panneau de résultat de recherche  pour le tag @@TODO et que soit affiché dans le  header du panneau de recherche "✔ Liste des Tâches @@TODO". dès qu'une recherche est effectué on reprend l'affichage normal "🔍 Résultats de la Recherche". mais si l'utilisateur relance une recherche sur @@TODO alors on rebascule sur "✔ Liste des Tâches @@TODO"



## V3.0.8 Onglet Lecteur (PDF) Fix [#46] Text Selection with mousewheel + Images

fix [#46](https://github.com/lephotographelibre/BlueNotebook/issues/46) `pdf_viewer.py`

@@Grok
 J'ecris une application Python, j'ai un onglet lecteur qui permet d'afficher des fichiers PDF. Je ne suis pas satisfait de la solution mise en oeuvre de sélection de texte avec la souris pour copy/paste d'un mot ou quelques mots . La solution de "Copier le texte de la page" via le menu contextuel fonctionne correctement.
Le principal probleme vient de la position de l'origine de la sélection avec la souris. si je clicke sur un mot puis je glisse avecla souris pour selectionner le paragraphe souhaité, souvent le texte sélection est surligné plusieur lignes plus haut !!
il faudrair pouvoir définir un caret et sélectionner à partir de ce caret
 que me propose tu ?
beta1

Je voudrais pouvoir pointer sur une image dans un page pdf et pouvoir avec le menu contextuel "Sauvegarder cette image" copier cette image et la sauvegarder au format .jpg dans un dossier choisi par l'utilsateur via une boite de dialogue 
beta2

 
+ persistance du dossier de sauvegarde  dans settings.json




## V3.0.7 Onglet Lecteur (epub) Fix [#46] Cannot scroll with mousewheel

dans le panneau "Lecteur" avec un fichier epub ouvert, j'essaye de faire defiler les pages avec la molette de la souris.
Cela ne fonctionne pas.

Fix [#47](https://github.com/lephotographelibre/BlueNotebook/issues/47)

Amelioration de la vitesse de demarrage

modifier le script run_bluenotebook.sh afin qu'il ne fasse les vérifications lourdes (comme l'installation des dépendances avec pip install) que si c'est vraiment nécessaire.

La lenteur provient principalement de deux commandes qui sont exécutées à chaque fois :

- eval "$(pyenv init --path)" et eval "$(pyenv virtualenv-init -)" : Ces commandes sont coûteuses en temps. Elles ne sont utiles que si votre shell n'est pas déjà configuré pour pyenv.
- pip install -r requirements.txt : C'est le point le plus lent. Le script vérifie et installe les dépendances à chaque lancement, même si elles n'ont pas changé.
le script sera nettement plus rapide au quotidien. Les vérifications complètes et l'installation des dépendances ne se feront que la toute première fois ou lorsque vous modifierez le fichier requirements.txt.


## V3.0.6 Onglet Lecteur (PDF) Fix [#45] Cannot scroll with mousewheel


Fix [#45](https://github.com/lephotographelibre/BlueNotebook/issues/45)

dans le panneau "Lecteur" avec un fichier pdf ouvert, j'essaye de faire defiler les pages avec la molette de la souris.
Cela ne fonctionne pas.

Cela défile bien dans la page affichée mais je voudrais que le défilement m'affiche la page suivante ou précédente

Cela fonctionne maintenant mais 
- mais l'affichage dans la table des matières a gauche du document n'est pas mise à jour des changements de page, de chapitre
-
- mais pas l'affichage dans la liste déroulante (entre les flèches) de la barre de navigation n'est pas mise à jour des changements de page, de chapitre

## V3.0.5 Onglet Lecteur (EPUB/PDF) MaJ PDFReader

--> Branch ---> pdf_reader   git checkout -b pdf_reader

Prérequis
```bash
pip install PyMuPDF
```

Actuellement l'onglet "Lecteur" permet d'affichier un fichier epub avec sa table des matieres, barre de recherche et barre de navigation. Je vdrais également pouvoir afficher un document pdf avec les meme fonctionnalités si possible (avec sa table des matieres, barre de recherche et barre de navigation). L'interface utilisateur devra etre si possible similaire à celle du lecteur epub


- Les fonctionnalités de lecture d'un fichier pdf sont les suivantes:
	- Affichage des pages et de la table des matières
	- navigation dans le pages et les chapitres via la table des matières ou via une barre de naviagtion au dessus du texte
	 
	- Recherche de mots dans le document (avec barre de recherche intégrée (Rechercher - Suivant - Précédent - Effacer))
	- possiblités de couper coller du texte  pour le coller dans l'éditeur
	- plus tard possibilité d'exporter un chapitre complet en Markdown dans l'editeur **(a venir)**
	- lorsque un document s'ouvre il est possitionné à la première page  la table des matières est affichée
	- possiblité de cacher la table des matières 
	- CSS du rendu externalisé dans un dossier bluenotebook/resources/css_epub/ **(a venir)**

- Le code spécifique à la gestion du pdf sera aussi externalisé dans ce répertoire  `bluenotebook/gui/`  
beta1

dans le panneau "Lecteur" avec un fichier pdf ouvert, j'essaye de lancer la recherche sur un mot;
- Le mot est trouvé, et le terme est mis en surbrillance PK
- si j'appuie sur "Suivant" pour recherche l'occurence suivante de ce mot rien ne se passe.

dans le panneau "Lecteur" avec un fichier pdf ouvert, j'essaye de naviguer dans le document avec la barre de navigation qui est située dessous le document. 
- Lorsque j'utilise les fleches l'affichage du document est bien remis à jour 
- mais pas l'affichage dans la table des matières a gauche du document
- mais pas l'affichage dans la liste déroulante (entre les flèches) de la barre de navigation


dans le panneau "Lecteur" avec un fichier pdf ouvert, j'essaye de lancer la recherche sur un mot;
- Le mot est trouvé, afficher dans la bonne page, et le terme est mis en surbrillance 
- mais l'affichage dans la table des matières a gauche du document n'est pas mise à jour

beta2
dans le panneau "Lecteur" avec un fichier pdf ouvert,
- Pas de redimentionnement dynamique avec la molette de la souris

dans le panneau "Lecteur" avec un fichier pdf ouvert,
- pas d'affichage d'un menu contextuel pour faire du copier coller de texte affichier dans la page pdf

dans le panneau "Lecteur" avec un fichier pdf ouvert,
- je veux pouvoir sélectionner du texte dans la page pdf avec la souris
- Je veu pouvoir copier ce texte selectionné pas toute la page dans le presse papier

Cela ne fonctionne pas bien, le texte récupéré (paste) ne correspond pas au texte sélectionné (copy). je n'aime pas ce mode de sélectionn y a un autre mode que le rubber_band




## V3.0.4 Fix [#44] Navigation Search table header results color

Fix [#44](https://github.com/lephotographelibre/BlueNotebook/issues/44)
comment the following line into `gui/search_results_panel.py`

        # self.results_tree.setStyleSheet("border: none; background: transparent;")


```python
    def setup_ui(self):
        """Configuration de l'interface utilisateur du panneau."""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 0)
        layout.setSpacing(5)

        self.label = QLabel("🔍 Résultats de la Recherche")
        font = self.label.font()
        font.setBold(True)
        self.label.setFont(font)

        self.label.setMaximumHeight(35)
        layout.addWidget(self.label)

        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(2)
        self.results_tree.setHeaderLabels(["Date", "Texte"])
        # self.results_tree.setHeaderLabels(["🗓️", ""])
        self.results_tree.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.results_tree.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.results_tree.setSortingEnabled(True)
        self.results_tree.sortByColumn(0, Qt.DescendingOrder)  # Trier par date
        # self.results_tree.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.results_tree)

        self.setLayout(layout)
```

## V3.0.3 Integration: Add YT transcription Fix [#42]

Add comment1

Fix [#42](https://github.com/lephotographelibre/BlueNotebook/issues/42)
 
Tester youtube-transcript-api <https://github.com/jdepoix/youtube-transcript-api>

- create git branch youtube-transcript-api
- ajouter package `pip install youtube-transcript-api`
- Créer un fichier read_transcript.py dans `bluenotebook/tests/`
- Tester sur video <https://www.youtube.com/watch?v=S2TUommS3O0>  --> ID = S2TUommS3O0


```python
from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()
ytt_api.fetch(video_id)
```

Note: By default, this will try to access the English transcript of the video. If your video has a different language, or you are interested in fetching a transcript in a different language, please read the section below.

Note: Pass in the video ID, NOT the video URL. For a video with the URL https://www.youtube.com/watch?v=12345 the ID is 12345

1st release

```python
# From doc: https://github.com/jdepoix/youtube-transcript-api
# Test Video: https://www.youtube.com/watch?v=S2TUommS3O0 --> ID = "S2TUommS3O0"
# 2nd Yann Le Cun https://www.youtube.com/watch?v=Z208NMP7_-0 --> ID = "Z208NMP7_-0"
#
# Pre-requisite:
#   pip install youtube-transcript-api


from youtube_transcript_api import YouTubeTranscriptApi

ytt_api = YouTubeTranscriptApi()
# fetched_transcript = ytt_api.fetch("S2TUommS3O0")
# fetched_transcript = ytt_api.fetch("S2TUommS3O0", languages=["fr", "en"])
fetched_transcript = ytt_api.fetch(
    "Z208NMP7_-0", languages=["fr", "en"], preserve_formatting=True
)

# provides a length
snippet_count = len(fetched_transcript)
print(f"snippet_count = {snippet_count}")

# is iterable
for snippet in fetched_transcript:
    print(snippet.text)

# indexable
last_snippet = fetched_transcript[-1]


```


----

Cela va me permettre de spécifier un ajout à l'integration de video Youtube.
- Lorsque l'utilisateur veut integrer une video Youtube en fournissant une URL (code déja existant on ne le modifie pas)
- on va aller verifier qu'il existe un transcript pour cette video e utilisant le package Python youtube_transcript_api (voir code `bluenotebook/tests/read_transcript_grok.py`
- si un transcript existe alors on va proposer à l'utilisateur d'ajouter ce transcript en dessous de la video dans le fragment Markdown. généré par l'intégration Youtube , code déja existant) via une boite de dialogue:
"Pour cette vidéo Youtube une transcription en {langage du transcript} existe, Voulez vous l'ajouter ?"
- Le transcript sera préfixé par "** Transcript de la video Youtube**" puis le texte du transcript.
- Le code pour récuperer le transcript sera basé sur le code `bluenotebook/tests/read_transcript_grok.py`
- Affichage éventuel d'une fenetre avec le Message d'erreur mais le reste de l'intégration Youtube (code déja présent devra continuer à fonctionner) Erreur non Bloquante
- Dans les préférences -> Intéfrations l'utilisateur pourra choisir s'il souhaite ou non l'affichage des transcripts Youtube via une boite à cocher: "Autoriser l'affichage des transcripts de vidéo Youtube dans l'éditeur Markdown" . Cette boite a cocher sera en dessous celle qui existe déjà "Autoriser l'intégration de vidéo Youtube dans l'éditeur Markdown".
- Si la boite a cocher "Autoriser l'intégration de vidéo Youtube dans l'éditeur Markdown" n'est pas validée alors "Autoriser l'affichage des transcripts de vidéo Youtube dans l'éditeur Markdown" ne sera pas validée. 
- Ces choix de préférences utilisateur seront persistés dans settings.json de l'utilisateur.

beta1

La géneration de Transcription est parfois longue. je voudrais 
- que cette tache puisse etre asynchrone pour ne pas bloquer l'utilisateur
- qu'un message "Récupération de la transcription en cours..." puisse etre affiché en rouge dans la barre de statut de l'editeur

Création une nouvelle classe TranscriptWorker dans `youtube_video.py`. Cette classe, qui hérite de `QRunnable`, s'exécutera en arrière-plan pour ne pas bloquer l'interface.

Elle encapsule la logique de `get_youtube_transcript`.
Elle utilise des signaux (finished, error, no_transcript) pour communiquer le résultat à la fenêtre principale.

Modification de `main_window.py` pour utiliser ce nouveau worker et gérer l'affichage dans la barre de statut.

- Barre de statut : Ajout d'un label et d'un timer pour le message clignotant "Récupération de la transcription en cours...".
- Logique asynchrone : La méthode insert_youtube_video lance maintenant le TranscriptWorker et connecte ses signaux à des méthodes de rappel (on_transcript_finished, on_transcript_error, etc.).
- Insertion du contenu : Le bloc Markdown de la vidéo est inséré immédiatement. Si une transcription est trouvée plus tard, elle est ajoutée à la suite


Ajouter table de correspondance fr --> Français de --> Allemand
git branch





## V3.0.2 Fix [#38]Buttons & Fix [#34] Table des Matières

Fix [#28](https://github.com/lephotographelibre/BlueNotebook/issues/28)
Fix [#34](https://github.com/lephotographelibre/BlueNotebook/issues/34)


## V3.0.1 Panneau Lecteur & EPUB Reader

Je voudrais inclure un nouveau panneau appelé "Lecteur". Ce panneau apparaitra toujours a droite de l'editeur. Si l'aperçu HTML est ouvert également l'ordre sera "Editeur Markdow -> Aperçu HTM --> Lecteur". Ce panneau sera dédié à l'affichage et la navigation dans des documents EPUB ou PDF.
- Ce panneau respectera les memes caractéristiques que les autres panneaux
	- Entete sous forme d'onglet
	- Bouton poussoir dans la barre des boutons sous la barre de menu principale
	- Par defaut ce panneau sera fermé et son bouton poussoir en mode fermé/Grisé
	- Si on active le bouton poussoir "Lecteur" et qu'aucun document n'a été sélectionné alors on affichera une boite de dialogue demandant à l'utilisateur de sélectionner un fichier (EPUB ou PDF) à ouvrir dans le menu "Fichier > Ouvrir Document..."
- On va donc créer le menu  "Fichier > Ouvrir Document..." qui permettra d'ouvrir des fichiers .pdf ou .epub locaux ou distants via URL
    - Si un document est trouvé on va alors ouvrir le panneau "Lecteur" à la droite de l'éditeur avec le document à afficher.
	- on pourra fermer ce panneau via le bouton poussoir "Lecteur" qui deviendra alors grisé lorsque le panneau est fermé.
	- on conservera toujours la memoire du dernier document ouvert dans le "Lecteur" et cela sera persisté dans settings.json de l'utilisateur.

Dans un premier temps on va developper le code nécessaire à la fonctionnalité de lecture des fichiers epub dans cet onglet. ne pas oublier que plus tard on pourra ouvrir également des fichiers PDF dans ce panneau **(a venir)**.

- Les fonctionnalités de lecture d'un epub sont les suivantes:
	- Affichage des pages et de la table des matières
	- navigation dans le pages et les chapitres via la table des matières ou via une barre de naviagtion au dessus du texte
	- affichage des images  diu livre **(a venir)**
	- Recherche de mots dans le document (avec barre de recherche intégrée (Rechercher - Suivant - Précédent - Effacer))
	- possiblités de couper coller du texte  pour le coller dans l'éditeur
	- plus tard possibilité d'exporter un chapitre complet en Markdown dans l'editeur **(a venir)**
	- lorsque un doument s'ouvre il est possitionné à la première pa eg la table des matières est affichée
	- possiblité de cacher la table des matières **(a venir)**
	- CSS du rendu externalisé dans un dossier bluenotebook/resources/css_epub/ **(a venir)**
	- utilisation si possible des polices "embedded dans l'ouvrage **(a venir)**


J'ai developpé le code `bluenotebook/tests/epub_readerV6.py` comme exemple et je souhaite que l'on puisse s'appuyer sur celui-ci.
les prerequis sont les pacakges Python

pip install PyQt5 PyQtWebEngine ebooklib

En particulier (Table des matières et les barres de recherche et de navigation (avec boutons Permier, Dernier chapitre précédent, chapitre suivant et affichage central du chapitre courant avec boite déroulante pour changer de chapitre) . Il faudra trouver une place pour mettre la position courante dans le livre  Chapitre/Page (Exemple --> "Chapitre: 6 / 173") C'est dire Multi-méthodes de navigation : L'utilisateur peut naviguer via liste, combo box, ou boutons selon sa préférence
beta1

la taille du panneau  "Lecteur" en hauteur n'est pas correcte e donc la taille de l'onglet n'est pas correcte. Le panneau sans l'onglet est trop ramassé vers le bas et ne s'étend pas sur toute la taille du panneau. 
beta2

je voudrais juste a gauche du champ recherche dasn le panneau Lecteur une petit bouton avec une icone "fleche"  qui permette de cacher ou pas la table des matières
- < pour fermer la table
- > pour ouvrir la table des matières
 

 
## V2.9.4 Bug Fix Issue [#26] & Fix issue [#25] & Fix issue [#24] & Fix issue [#27]

Fix Issue [#26] Résultats de recherche header de colonne illisible
dans search_results_panel.py 

a la place de
self.results_tree.setHeaderLabels(["🗓️", ""])
revenir à 
self.results_tree.setHeaderLabels(["Date", "Texte"])
beta1

Fix issue [#25](https://github.com/lephotographelibre/BlueNotebook/issues/25)
Augmenter la taille du résumé des livres
b
La taille du résumé pour l'intégration Amazon ISBN est définie directement dans le code du fichier `bluenotebook/integrations/amazon_books.py`. 

Plus précisément, dans la fonction `get_book_info_from_amazon`, la taille maximale du résumé est codée en dur à 200 caractères.
--> Augmenter à 500 caractères

```python
            if len(raw_summary) > 500:
                # Tronquer à la fin de la dernière phrase avant 500 caractères
                trunc_limit = 500
```
beta2

Fix issue [#24](https://github.com/lephotographelibre/BlueNotebook/issues/24)
Add Markdown Link without selected text

Quand je suis dans l'editeur Markdown et que j'active le menu  Insérer > Lien Markdown (texte) si aucun texte n'est sélectionné rien ne se passe. Idem avec le sous menu contextuel.
Ce n'est pas le comportement que j'attendais. 
- Je veux que dans ce cas apparaisse la boite de dialogue Insérer un lien Markdown avec les deux champs vide que l'utilisteur doit remplir (Texte du  Lien et URL du lien).
- Sinon conserver le comportement actuel si un texte est sélectionné dans l'éditeur

Modifier le label de ce menu "Lien Markdown (texte)" en "Lien Markdown"

Comportement de l'insertion de lien :

- Sans sélection : Si vous activez "Insérer > Lien Markdown" sans avoir sélectionné de texte, la boîte de dialogue s'ouvrira désormais avec les deux champs ("Texte du lien" et "URL") vides, prête à être remplie.
- Avec sélection : Le comportement que vous appréciez est conservé. Si du texte est sélectionné, il pré-remplira automatiquement le champ "Texte du lien".

Changement du libellé :

Le menu Insérer > Lien Markdown (texte) a été renommé en Insérer > Lien Markdown.


modification a été appliquée au fichier `bluenotebook/gui/editor.py`

 
-Sans sélection de texte : Lorsque vous utilisez Insérer > Lien Markdown, la boîte de dialogue s'ouvrira désormais avec les deux champs ("Texte du lien" et "URL") vides, prête à être remplie.
-Avec sélection de texte : Le comportement actuel est conservé. Le texte que vous avez sélectionné pré-remplira automatiquement le champ "Texte du lien".


```python
        # V2.9.4 - Gérer le cas du lien Markdown en premier, car il doit
        # fonctionner avec ou sans sélection.
        if format_type == "markdown_link":
            selected_text = cursor.selectedText().strip()
            self._handle_markdown_link(selected_text)
            return
```
beta3

Quand la boite de dialogue de Lien Markdown est "Validée" il faut vérifier que les deux champs sont bien remplis. Sinon en informer l'utilisateur pour qu'il puisse completer la saisie ou bien annuler la saisie de ce lien Markdown

modification a été appliquée au fichier `bluenotebook/gui/editor.py`

```python
        # V2.9.4 - Remplacer self.accept par une méthode de validation personnalisée
        self.button_box.accepted.connect(self.validate_and_accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addWidget(self.button_box)

    def validate_and_accept(self):
        """Vérifie que les champs ne sont pas vides avant d'accepter."""
        link_text = self.text_edit.text().strip()
        url_text = self.url_edit.text().strip()

        if not link_text or not url_text:
            QMessageBox.warning(
                self,
                "Champs requis",
                "Le texte du lien et l'URL sont tous les deux obligatoires.",
            )
        else:
            self.accept()
```
Fix issue [#27](https://github.com/lephotographelibre/BlueNotebook/issues/27)
Ajouter menu inserer URLs and Email Addresses

conformément à la syntaxe Markdown https://www.markdownguide.org/basic-syntax/#links
URLs and Email Addresses
To quickly turn a URL or email address into a link, enclose it in angle brackets.

<https://www.markdownguide.org>
<fake@example.com>
The rendered output looks like this:

https://www.markdownguide.org
fake@example.com

Je voudrais ajouter une nouveau menu Insérer > Lien URL/Email en dessous de Lien Markdown. à la fois dans le menu principal et le menu contextuel.
- L'utilisateur sélectionne dans l'éditeur une URL ou une adresse email 
- On insere le lien avec les "<" ">"


modifications:
- Nouveau menu Insérer > Lien URL/Email : Un nouvel élément de menu a été ajouté dans le menu principal, juste en dessous de "Lien Markdown".
- Mise à jour du menu contextuel : Ce même choix "Lien URL/Email" a été ajouté au menu contextuel qui apparaît lors d'un clic droit sur du texte sélectionné.

Fonctionnalité : Lorsque vous sélectionnez une URL ou une adresse e-mail dans l'éditeur et que vous activez cette nouvelle action, le texte sélectionné sera automatiquement encadré par des chevrons (< et >), le transformant en un lien cliquable dans l'aperçu.
beta4

petite correction dans le cas ou l'utilisateur sélection une url ou adresse email avec des espaces devant ou derriere les supprimer lors de l'insertion du lien.
C'est a dire si l'utilisateur sélectionne dans l'éditeur " https://www.markdownguide.org/basic-syntax/#links " le lien sera <https://www.markdownguide.org/basic-syntax/#links>


Fix issue [#32](https://github.com/lephotographelibre/BlueNotebook/issues/32)
Ajouter emoji memo 📝 question mark ❓ and exclamation mark emoji ❗à laliste des emojis du Menue Insérer > Emojis

 ## V2.9.3 Bug Fix Issue [#31]  Mise en forme paragraphe & Fix Issue [#30]

Issue [#31](https://github.com/lephotographelibre/BlueNotebook/issues/31)
Mise en forme paragraphe

- Ajout d'un sous-menu contextuel "Mise en forme" avec une option "Nettoyer le paragraphe" pour supprimer les sauts de ligne et espaces superflus dans une sélection.
- Amélioration de la gestion des espaces lors de l'application des styles (gras, italique, etc.) pour préserver l'espacement original.

Issue [#30](https://github.com/lephotographelibre/BlueNotebook/issues/30)
Formatage correct élements de dtyle sélectionnés dans l'éditeur


## V2.9.2 Export PDF basé sur un tag

Pour l'"export Journal PDF" je voudrais ajouter un critère:
- En Complément d'une fenetre de dates (qui est prioritaire) je voudrais ajouter comme critère la présence d'un tag dans les notes du jour exportées en PDF. c'est a dire n'inclure dans l'export PDF unquement les notes du jour entre "date de debut et date de fin" qui contienne obligatoirement un tage donné.
- Le tag sera sélectionné dans une liste déroulante basée sur les données `index_tags.json` du journalc ce qui contraindra l'utilisateur à ne choisir qu'un tag qui existe déja et qui a été indexé.
- il n'est pas nécessaire de reparser les fichiers notes car celles ci ont été indexées au demarrage de l'appli et le résultat est `index_tags.json` qui contient pour chaque tag la liste des notes qui contiennent ce tag.
- ce choix apparaitra dans la boite de dialogue lancée lors de l"export pdf après les choix "date de debut et date de fin" 
- Si aucune note comportant ce tag n'existe dans la fenetre "date de debut et date de fin" un message sera affiché pour l'utilisateur et aucun fichier ne sera créé.
- Il faudra ajouter le nom du tag sélectionné sur la première page du Journal PDF.
beta1



## V2.9.1 Thèmes CSS pour PDF  

- Création d'un dossier `bluenotebook/resources/css_pdf/`
- Création d'in onglet `Préférences .. Affichage .. Export PDF`

- Comment est defini le theme css pour les exports PDF du journal ?

- Peut_on externaliser tout le code CSS de la méthode `weasyprint_css` du   fichier `integrations/pdf_exporter.py` dans un fichier `default_pdf.css` dans le répertoire `resources/css_pdf/` ce qui rendra plus facile ensuite sa modification a ISO fonctionnalités. le fichier `default_pdf.css` sera au standard CSS.
beta1

- Je voudrais 
1.  **Modifier `preferences_dialog.py`** pour ajouter une section de sélection de thème dans l'onglet "Export PDF" de la même manière que cela es fait pour Aperçu HTML afin de concerver une homogénéité entre onglets.
2.  **Sauvegarder ce nouveau paramètre** (par exemple, `pdf.css_theme`) dans `settings.json`.
3.  **Modifier la logique d'exportation PDF** dans `main_window.py` et `integrations/pdf_exporter.py` pour utiliser ce nouveau paramètre
beta2


Dans le répertoire resources/css_preview/ j'ai un theme css utilisé pour l'apercu HTML qui s'appelle theme-minimaliste.css.
Je voudrais que tu convertises ce theme au meme format que resources/css_pdf/default_pdf.css et que sauvegarde ce fichier sous le meme nom resources/css_pdf/theme-minimaliste.css 
beta3

## V2.8.2 Theme CSS pour Aperçu HTML + Clean Menu + Attachements

Ajout de 3 thèmes CSS pour Aperçu HTML.
beta1

Je voudrais alleger un peu les menus je voudrais supprimer le Menu "Insérer -- Fichier" et le code associé.
peux tu supprimer aussi a logique associée dans le fichier de l'éditeur (editor.py) pour gérer "internal_link" si elle devient ainsi inutilisée editor.py
beta2

Je voudrais alleger un peu les menus je voudrais supprimer le Menu "Insérer -- Lien (URL ou email)" du menu principal mais aussi du mmenu contextuel de l'éditeur
beta3

Je voudrai ajouter au menu contextuel de l'editeur le menu (et ses sous-menus) de formattage de titres et de formattage de liste (et ses sous-menus) comme dans le menu principal
beta4

Attachement
Lien mono directionnel
 
- Ajout d'un menu `Insérer --> Attachement` en dessous Lien Markdown (texte)
- demander à l'utilisateur ou se trouve le fichier à attacher en local (sélécteur de fichier ou à distance (URL) comme pour insérer Image (<img.. >) (boite de dialogue: Chemin ou URL  et parcourir pour le sélecteur de fichier)  
- copier le fichier sélectionné dans le répertoire `attachments` du journal en le renommemant `YYYYMMJJ_nom_du_fichier.extension` (YYYYMMJJ est la date du jour de la note dans laquelle on insère cet attachement). Si le fichier est déja dans le bon répertoire ne pas le renommer !
- générer un fragment Markdown de type: (incluant l'emoji 📎)
📎 [Attachement | 20251024_nom_du_fichier.extension](attachments/20251024_nom_du_fichier.extension)
par exemple
📎 [Attachement | 20251024_Vax_paper.md](attachments/20251024_Vax_paper.md)

## V2.8.1 Re-définition d'un menu contextuel en Français dans l'aperçu HTML

Redéfinir un menu contextuel personnalisé dans une fenêtre PyQt  PyQt5 ou PyQt6, ce qui est courant pour les interfaces graphiques Python). L'objectif est de faciliter la traduction des menus en différentes langues, en utilisant le système d'internationalisation (i18n) de Qt. Cela évite de dépendre du menu contextuel standard des widgets (comme QTextEdit ou QLabel), qui peut être capricieux pour les traductions, et vous permet de contrôler pleinement les chaînes de texte.

Redéfinir le menu contextuel

- Au lieu d'utiliser widget.createStandardContextMenu(), créez un QMenu personnalisé avec des QAction.
- Associez-le à l'événement clic droit via contextMenuEvent ou en définissant setContextMenuPolicy(Qt.CustomContextMenu) et en connectant le signal customContextMenuRequested.

## V2.7.11 Aide en ligne HTML redesign

aide_en_ligne.html dans le fichier d'aide en ligne la table des matieres apparait en premier puis le texte. je voudrais que la table des matieres apparaisse a gauche du texte et reste toujours affichée meme si l'utilisateur scrolle le texte

To achieve this, I'll restructure the HTML slightly and update the CSS to use a Flexbox layout, which will allow the table of contents to remain "sticky" on the left while you scroll through the main content on the right.

Here are the required changes for bluenotebook/resources/html/aide_en_ligne.html:



## V2.7.10 Intégration Conversion PDf to MD

Pour cette nouvelle integration on va aller recuperer chercher un fichier PDF en local ou à distance via une URL puis on va le convertir en Markdown en utilisant le toolkit de Microsoft dispobile `https://github.com/microsoft/markitdown`

- Le menu pour lancer l'intégration "Intégrations --> Conversion PDF-Markdown"
- Le code nécessaire à l'integration sera stocké dans le dossier `bluenotebook/integrations`
- L'utilisateur devra sélectionner via une boite de dialogue la localisation du fichier local ou remote
- Le toolkit `markitdown` de microsoft sera utilisé.
- SLe fichier résultat sera affiché dans l'editeur Markdown. Si un fichier était déjà en cours d'édition il sera sauvegradé après demande à l'utilisateur.
- La conversion peut prendre du temps alors celle ci sera faite dans un worrker spécifique et l'utilisateur sera informé de la conversion en cours par un message en police rouge dans la barre de statut de la fenètre principale.

**Exemple de code Python pour convertir un PDF en Markdown avec MarkItDown**

`MarkItDown` est un excellent outil de Microsoft pour convertir des documents (comme les PDF) en Markdown structuré, idéal pour les LLMs ou l'analyse de texte. Comme indiqué dans la documentation du repo GitHub, l'installation se fait via `pip install 'markitdown[all]'` pour inclure toutes les dépendances optionnelles (y compris pour les PDF).
Voici un exemple complet et simple d'utilisation en Python. Je suppose que vous avez un fichier PDF local (remplacez "mon_fichier.pdf" par votre chemin). Ce code :

- Charge l'outil.
- Convertit le PDF en Markdown.
- Affiche le résultat et l'enregistre dans un fichier .md.



```python
from markitdown import MarkItDown
import os

# Initialisation de MarkItDown
# - enable_plugins=False : Désactive les plugins tiers (par défaut)
# - Vous pouvez ajouter llm_client pour des descriptions d'images si besoin
md_converter = MarkItDown(enable_plugins=False)

# Chemin vers votre fichier PDF
pdf_path = "mon_fichier.pdf"  # Remplacez par votre fichier

# Vérification si le fichier existe
if not os.path.exists(pdf_path):
    print(f"Erreur : Le fichier '{pdf_path}' n'existe pas.")
    exit(1)

try:
    # Conversion du PDF en Markdown
    result = md_converter.convert(pdf_path)
    
    # Affichage du Markdown généré
    print("Contenu Markdown généré :\n")
    print(result.text_content)
    print("\n" + "="*50 + "\n")
    
    # Enregistrement dans un fichier Markdown
    output_md = pdf_path.replace(".pdf", ".md")
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(result.text_content)
    
    print(f"Fichier Markdown sauvegardé : {output_md}")
    
except Exception as e:
    print(f"Erreur lors de la conversion : {e}")
    print("Assurez-vous d'avoir installé 'markitdown[pdf]' pour les PDF.")
```


## V2.7.9 Filtre Liste déroulante des tags + suppress doublons, + @@ Majuscules 

La liste déroulante des tags est définie et gérée dans le fichier `bluenotebook/gui/navigation.py`.

Voici comment cela fonctionne, en se basant sur la documentation technique :

1.  **Création de l'interface** : Dans le fichier `gui/navigation.py`, la classe `NavigationPanel` (ou une classe similaire) est responsable de la création des widgets du panneau de navigation. C'est là que le champ de recherche (`QLineEdit`) et le bouton pour la liste déroulante (`QToolButton` ou `QPushButton` avec un "▼") sont créés et agencés.

2.  **Population de la liste** :
    *   Au démarrage, `MainWindow` lance l'indexation des tags, qui crée le fichier `index_tags.json`.
    *   Une fois l'indexation terminée, `MainWindow` lit ce fichier JSON pour obtenir la liste de tous les tags uniques.
    *   Cette liste de tags est ensuite transmise au `NavigationPanel`.
    *   Le `NavigationPanel` utilise cette liste pour construire dynamiquement un menu (`QMenu`) qui s'affichera lorsque l'utilisateur cliquera sur le bouton "▼". Chaque tag de la liste devient une action (`QAction`) dans ce menu.

3.  **Interaction** :
    *   Le `changelog.md` (version 1.6.9) précise bien le comportement attendu : "dès qu'il est cliqué [le tag dans la liste] vient remplir le champ de recherche avec le tag sélectionné."
    *   Cela signifie que le signal `triggered` de chaque `QAction` (chaque tag dans le menu) est connecté à une méthode (un "slot") qui insère le texte du tag dans le champ de recherche et, comme le précise la documentation, lance immédiatement la recherche.

En résumé, la **définition visuelle** du bouton se trouve dans `gui/navigation.py`, mais la **logique de remplissage** avec les données des tags est orchestrée par `MainWindow` après l'indexation.

Si vous cherchiez à modifier l'apparence ou le comportement de cette liste, c'est le fichier `bluenotebook/gui/navigation.py` qu'il faudrait examiner en premier.

### beta 1 Indexation des tags
@bluenotebook @tag_indexer.py 
Les tags sont indexés par tag_indexer.py  qui fabrique une liste index_tags.json et index_tags.cvs.
La saisie des tags par l'utilisateur est variable le meme tag teut etre saisi sous differentes formes (casse & accentuation)
Quellleque soit la saisie je voudrais que soient aggrégées toutes les formes d'un meme tag (avec differentes casse et accentuation sous in tag unique EN MAJUSCULE.
On retrouvera dans la liste des tags par exemple @@METEO qui aggerera toutes les occurences de @@Météo @@MéTEO @@météo.
donc dans la liste de tags index_tags.json et index_tags.cvs n'existeront que des tags en majuscules

### beta2 Sauvegarde Journal asynch
 Sauvegarde du journal peut-etre assz longue. je voudrais que celle ci soit réaliséé en asyncrhone avec message d'attente en police de couleur rouge dans la barre de status. je voudrais que le code n"cessaire à la sauvegarde du journal soir externalisé dans un fichier python du répertoire `bluenotebook/core/`

### beta3 index_tags augementer le contexte

dans le fichier index_tag.json ou .csv a chaque occurence du tag j'ajoute une élément de contexte (le champ context)

```json
  "@@AECOUTER": {
    "occurrences": 2,
    "details": [
      {
        "context": "[Comment l'IA bouleverse-t-elle notre",
        "filename": "20251028.md",
        "date": "2025-10-28",
        "line": 10
      },
      {
        "context": "[Comment l'IA bouleverse-t-elle notre",
        "filename": "20251023.md",
        "date": "2025-10-23",
        "line": 36
      }
    ]
  }
```
Le "contexte" d'un tag est constitué des 40 premiers caractères qui suivent immédiatement le tag sur la même ligne, après avoir supprimé les éventuels espaces de début et de fin de cette chaîne de 40 caractères.
Je voudrais augmenter la taille du contexte en pranant tous les caractères qui suivent immédiatement le tag sur la même ligne jusqu'à la fin de la ligne.

Modification du code Regex du le fichier `bluenotebook/core/tag_indexer.py ` pour que le contexte capturé s'étende jusqu'à la fin de la ligne, au lieu d'être limité aux 40 premiers caractères.

```python
        # Regex pour trouver les tags @@tag et capturer les 40 caractères suivants
        # self.tag_pattern = re.compile(r"(@@\w{2,})\b(.{0,40})")
        # Regex pour trouver les tags @@tag et capturer le reste de la ligne comme contexte
        self.tag_pattern = re.compile(r"(@@\w{2,})\b(.*)")
```


## V2.7.8 Migration Markdown Météo, Astro, carte GPS, trace GPX, Amazon ISBN, Vidéo Youtube

Je voudrais modifier le code généré par l'intégration Météo whether.py. En fait je voudrais ne plus générer de HTML mais que du Markdown 

par exemple je génère le HTML suivant:

```html
<div class="weather-container">
    <img src="https://cdn.weatherapi.com/weather/64x64/night/296.png" alt="Pluie légère" class="weather-icon">
    <div class="weather-details">
        <span class="weather-location">Poitiers:</span> Pluie légère, <strong class="weather-temp">11.3°C</strong> à 08:09<br>
        <span class="weather-extra">Vent: 13.3 km/h, Humidité: 100%</span>
    </div>
</div>
```
Je voudrais générer le code Markdown à la place

![Pluie légère](https://cdn.weatherapi.com/weather/64x64/night/296.png) 

**Poitiers :** Pluie légère, **11.3°C** à 08:09  Vent : 13.3 km/h, Humidité : 100%

modifie le fichier bluenotebook/integrations/sun_moon.py pour qu'il génère un fragment Markdown au lieu du HTML, en suivant la même logique que pour l'intégration météo.
beta1

Je voudrais modifier le code généré par l'intégration carte GPS. 
- En fait je voudrais ne plus générer de HTML mais que du Markdown (à fonctionnalités équivalentes) à la place  de par exemple
```html
<figure style="text-align: center;">
    <a href="https://www.openstreetmap.org/#map=16/46.58325004582807/0.3438650843823104">
         <img src="images/20251025093445_carte_Poitiers.png" alt="Carte de Poitiers, coordonnées 46.58325004582807, 0.3438650843823104" width="800">
    </a>
    <figcaption style="font-weight: bold;">GPS: [46.58325004582807, 0.3438650843823104]  Poitiers</figcaption>
</figure>
```
- je voudrais aussi que tout le code nécessaire à cette intégration soit externalisé dans un fichier python dans le répertoire integrations

Il faudrait modifier l'url générée pour inclure le marker c'est a dire rajouter "?mlat=46.561517&mlon=0.323711" par exemple ce qui conne une url de type

https://www.openstreetmap.org/?mlat=46.561517&mlon=0.323711#map=16/46.56152/0.32371

beta2

je voudrais faire la meme chose avec l'intégration de trace GPX
- En fait je voudrais ne plus générer de HTML mais que du Markdown (à fonctionnalités équivalentes) à la place  de par exemple
```html
<figure style="text-align: center;">
    <a href="https://www.openstreetmap.org/#map=16/46.569191/0.344628" target="_blank">
         <img src="images/20250502_Poitiers_gpx.png" alt="Trace GPX - Poitiers" width="800">
    </a>
    <figcaption style="font-weight: bold;">Trace GPX: <a href="https://www.openstreetmap.org/?mlat=46.569191&mlon=0.344628#map=16/46.569191/0.344628" target="_blank">Poitiers</a> - 02/05/2025 à 09:46 - Durée: 1:23:45</figcaption>
</figure>
```
- En plus je voudrais que l'image clickable genere un lien avec un marker de type https://www.openstreetmap.org/?mlat=46.569191&mlon=0.344628#map=16/46.569191/0.344628
- Si nécessaire je voudrais aussi que tout le code nécessaire à cette intégration soit externalisé dans un fichier python dans le répertoire integrations

correction pour les traces GPX je voudrais que le lien clickable de l'image soit l'image elle meme


[![Trace GPX - Poitiers](images/20250502_Poitiers_gpx.png)](https://www.openstreetmap.org/?mlat=46.569191&mlon=0.344628#map=16/46.569191/0.344628)

**Trace GPX :** [Poitiers](https://www.openstreetmap.org/?mlat=46.569191&mlon=0.344628#map=16/46.569191/0.344628) - 02/05/2025 à 09:46 - Durée: 1:23:45

[![Trace GPX - Poitiers](images/20250502_Poitiers_gpx.png)](images/20250502_Poitiers_gpx.png)

**Trace GPX :** [Poitiers](https://www.openstreetmap.org/?mlat=46.569191&mlon=0.344628#map=16/46.569191/0.344628) - 02/05/2025 à 09:46 - Durée: 1:23:45

beta3

Je vais continuer pour l'intégration Amazon ISBN.
- En fait je voudrais ne plus générer de HTML mais que du Markdown (à fonctionnalités équivalentes) à la place  de par exemple

```html
<div class="book-container">
    <h2>Les cent jours qui ont changé les États-Unis</h2>
    <div class="book-content">
        <div class="book-image">
            <img src="https://m.media-amazon.com/images/I/31Umm4kJo5L._SY445_SX342_QL70_ML2_.jpg" alt="Couverture">
        </div>
        <div class="book-details">
            <p><strong>Auteur :</strong> Gilles PARIS</p>
            <p><strong>Éditeur :</strong> Editions de l'Aube</p>
            <p><strong>Date de publication :</strong> 17 octobre 2025</p>
            <p><strong>ISBN :</strong> 9782815968645</p>
            <p><strong>Pages :</strong> 189 pages</p>
            <p><strong>Note :</strong> Inconnu</p>
            <p><strong>Résumé :</strong> Le retour de Trump signe une nouvelle ère pour les États-Unis. Endurci, entouré d'hommes à sa solde et disposant maintenant des pleins pouvoirs, il n'a plus face à lui de véritables limites.<br>En lire plus...</p>
            <p><a href="https://www.amazon.fr/dp/B0FV3GBYVW" target="_blank">Voir sur Amazon.fr</a></p>
        </div>
    </div>
</div>
```
A la place je voudrais générer quelque chose comme!
```markdown
![Couverture](https://m.media-amazon.com/images/I/31Umm4kJo5L._SY445_SX342_QL70_ML2_.jpg)

**Auteur :** Gilles PARIS  
**Éditeur :** Editions de l'Aube  
**Date de publication :** 17 octobre 2025  
**ISBN :** 9782815968645  
**Pages :** 189 pages  
**Note :** Inconnu  

**Résumé :** Le retour de Trump signe une nouvelle ère pour les États-Unis. Endurci, entouré d'hommes à sa solde et disposant maintenant des pleins pouvoirs, il n'a plus face à lui de véritables limites.  
[En lire plus...](https://www.amazon.fr/dp/B0FV3GBYVW)

[Voir sur Amazon.fr](https://www.amazon.fr/dp/B0FV3GBYVW)
```
- Si nécessaire je voudrais aussi que tout le code nécessaire à cette intégration soit externalisé dans un fichier python dans le répertoire integrations
- Je voudrais avant la couverture générer un fragment Markdown de type:
@@Book **Titre :** Titre du livre

beta4

Toujours dans la meme logique pour l'intégration de videos youtube 
- En fait je voudrais ne plus générer de HTML mais que du Markdown (à fonctionnalités équivalentes) à la place  de par exemple

```html
@@Video @@Youtube Etta James Inspired Blues Unforgettable Melodies of Heart and Soul
<https://www.youtube.com/watch?v=zucjShnTi4g>
<figure class="youtube-video-figure">
    <a href="https://www.youtube.com/watch?v=zucjShnTi4g" target="_blank" title="Lancer dans le navigateur">
        <img src="https://img.youtube.com/vi/zucjShnTi4g/hqdefault.jpg" alt="Etta James Inspired Blues Unforgettable Melodies of Heart and Soul" style="max-width: 480px; border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    </a>
    <figcaption style="font-size: 0.9em; margin-top: 0.5em;">
        <a href="https://www.youtube.com/watch?v=zucjShnTi4g" target="_blank" style="text-decoration: none; color: #ff0000;">
            <span>Voir sur YouTube : https://www.youtube.com/watch?v=zucjShnTi4g</span>
        </a>
    </figcaption>
</figure>
```
A la place je voudrais générer quelque chose comme!
```markdown

@@Video @@Youtube Etta James Inspired Blues Unforgettable Melodies of Heart and Soul [Voir sur YouTube : https://www.youtube.com/watch?v=zucjShnTi4g](https://www.youtube.com/watch?v=zucjShnTi4g)

[![Etta James Inspired Blues Unforgettable Melodies of Heart and Soul](https://img.youtube.com/vi/zucjShnTi4g/hqdefault.jpg)](https://www.youtube.com/watch?v=zucjShnTi4g)
```
beta5

- je voudrais modifier le code Markdown renvoyé par l'intégration météo
- Basé sur la table de correspondance suivante:


| Icône | Terme météo en français | Terme météo en anglais | Emoji le plus proche |
|-------|-------------------------|-----------------------|----------------------|
| 113   | Ensoleillé             | Sunny                 | ☀️                   |
| 116   | Partiellement nuageux  | Partly Cloudy         | ⛅                   |
| 119   | Nuageux                | Cloudy                | ☁️                   |
| 122   | Couvert                | Overcast              | 🌥️                  |
| 143   | Brume                  | Mist                  | 🌫️                  |
| 176   | Pluie éparse à proximité | Patchy rain nearby  | 🌦️                  |
| 179   | Neige éparse à proximité | Patchy snow nearby  | ❄️🌨️               |
| 182   | Grésil épars à proximité | Patchy sleet nearby | 🌨️💧               |
| 185   | Bruine verglaçante éparse à proximité | Patchy freezing drizzle nearby | 🌧️❄️       |
| 374   | Légères averses de cristaux de glace | Light showers of ice pellets | 🌨️       |
| 377   | Averses de cristaux de glace modérées à fortes | Moderate or heavy showers of ice pellets | 🌨️💨 |
| 386   | Légère pluie éparse avec tonnerre par endroit | Patchy light rain in area with thunder | 🌦️⚡️ |
| 389   | Pluie forte à modérée avec tonnerre par endroit | Moderate or heavy rain in area with thunder | 🌧️⚡️ |
| 392   | Légère neige éparse avec tonnerre par endroit | Patchy light snow in area with thunder | ❄️⚡️ |
| 395   | Neige éparse modérée à forte avec tonnerre par endroit | Moderate or heavy snow in area with thunder | ❄️⚡️💨 |
- je voudrais supprimer l'affichage actuel de l'icone tel que cidessous:
```markdown
 ![Pluie légère](https://cdn.weatherapi.com/weather/64x64/day/296.png)

**Météo pour Poitiers :** Pluie légère, **12.2°C** à 08:49  Vent : 29.5 km/h, Humidité : 88%
```
et le remplacer par l'insertion de la bonne emoji coformément au tableau ci-dessus fourni tel que:
```markdown
**🌨️ Météo pour Poitiers :** Pluie légère, **12.2°C** à 08:49  Vent : 29.5 km/h, Humidité : 88%
```

## V2.7.7 Bug Fix Insert Image Markdown

Modification de l'insertion d'images via le menu "Inserer -> Image Markdown" pour un comportement plus robuste et cohérent.

- **Copie systématique dans le journal** : Que l'image soit sélectionnée depuis un fichier local ou une URL distante, elle est désormais systématiquement copiée dans le répertoire `images/` du journal.

- **Renommage avec horodatage** : L'image copiée est renommée en suivant le format `YYYYMMJJHHMMSS-nom_original.extension`. Par exemple, `photo.jpg` devient `20251026103000_photo.jpg`.

- **Génération de Markdown cliquable** : Le tag Markdown généré est maintenant une image cliquable. Il prend la forme `[!alt_text](chemin/image.jpg)`. Le texte alternatif (`alt_text`) est dérivé du nom de fichier original.

- **Ouverture dans le navigateur** : Dans l'aperçu HTML, un clic sur l'image insérée l'ouvrira en grand dans le navigateur externe par défaut.

- **Gestion des données EXIF** :
  - Lors de l'insertion d'une image, l'application détecte la présence de données EXIF.
  - Si des données sont trouvées, une boîte de dialogue vous demande si vous souhaitez les insérer.
  - Si vous acceptez, une ligne de métadonnées formatée en Markdown est ajoutée sous l'image. Elle inclut le lieu (cliquable vers OpenStreetMap), la date, l'appareil photo et les principaux paramètres de prise de vue.
  - Exemple de format :
[Poitiers](https://www.openstreetmap.org/?mlat=46.565814&mlon=0.359097#map=16/46.565814/0.359097) : **06/11/2024 10:30 : Google : Pixel 6a : ƒ/1.73 : Vitesse: 1/99s : Focale: 4.38mm : ISO: 79**

Cette modification garantit que toutes les images insérées font partie intégrante du journal, le rendant ainsi plus portable et autonome.
beta2

***Refactoring***

Je veux que la totalité du code n'écessaire à l'insertion d'image Markdown sera externalié dans un fichier Python qui sera dans le répertoire integration du projet afin d'alléger editor.py, main_window.py etc. Y integrer également le code integrations/image_exif.py
--> Création du nouveau fichier `bluenotebook/integrations/image_markdown_handler.py`

je voudrais que toutes les images "Markdown" insérées s'affichent avec une largeur/hauteur maximales de 600 px dans l'aperçu HTML en concervant le bon ration longueur largeur

Ajouté une règle de style CSS directement dans le composant d'aperçu (preview.py). Cette règle s'appliquera à toutes les images qui ne sont pas déjà contrôlées par une balise <figure> (comme celles insérées via le menu "Image ()").

```python
        # V2.7.7 - Ajout d'un style pour limiter la taille des images Markdown
        # Cette règle s'applique aux images qui ne sont pas dans une <figure>
        # pour ne pas affecter les images HTML dont la taille est déjà définie.
        image_style = """
        body > p > img, body > p > a > img {
            max-width: 600px;
            max-height: 600px;
            height: auto; /* Conserve le ratio */
            display: block; /* Permet le centrage avec margin */
            margin: 1em auto; /* Centre l'image horizontalement */
        }
        """
```
beta4

***Refactoring***

Je veux que la totalité du code n'écessaire à l'insertion d'image HTML (le code associé au menu Inserer --> Image (<img...>)) sera externalié dans un fichier Python qui sera dans le répertoire integrations du projet afin d'alléger editor.py,

## V2.7.6 Travail préparatoire Images Markdown

voir docs/[text](../../../../ssd/Dropbox/BlueNotebookJournal/attachments/V2.7.6_Images_Markdown.md)



## 2.7.5 bug Images Markdown clickable (images seuleument)

Ceci est important car je veux changer le code inclus lors dune integration Carte GPS et de HTML (facilement clickable) à Markdown

[![Carte de Poitiers, coordonnées 46.58325004582807, 0.3438650843823104](images/20251025093445_carte_Poitiers.png)](https://www.openstreetmap.org/#map=16/46.58325004582807/0.3438650843823104)

 @@TODO ⚠️ ⚠️ ⚠️ Pb d'image clickable dans le cas de carte GPS --> on ouvre l'image pas le lien associé 

### Analyse du problème
Le problème vient de la manière dont les liens sont gérés dans le panneau d'aperçu (bluenotebook/gui/preview.py). Pour permettre d'ouvrir les images en grand, une règle a été mise en place qui intercepte tous les clics sur des liens. Si le lien pointe vers une image (se terminant par .jpg, .png, etc.), il l'ouvre localement. Sinon, il tente d'ouvrir le lien dans un navigateur externe.

Dans votre cas, un lien Markdown comme Voir la carte... est converti en une balise HTML <a>. Le code actuel ne fait pas la distinction entre un lien contenant une image et un lien contenant uniquement du texte. Il traite tous les liens de la même manière, ce qui cause ce comportement inattendu.





## V2.7.4  Integration Youtube add Playlist

Je voudrais modifier l'integration youtube deja existante. telle qu'elle est elle permet d'ajouter des vidéo youtube avec des URL de type https://www.youtube.com/watch?v=bo_efYhYU2A.
Je voudrais pourvoir rajouter des playlists Youtube avec des url de type https://www.youtube.com/playlist?list=OLAK5uy_n2B_NIITvMyLSO6eiiFe5mAiOKW30EvD0 et dans ce cas la récuperer l'image de la playlist, l'auteur ou les auteurs, le titre de la playlist, le nombre de morceaux et afficher l'image de la playlist clickable.
ce qui change seront les tags @@Musique @@Youtube @@Playlist au lieu @@Video @@Youtube sinon utiliser le meme type d'affichage et de CSS que pour une vidéo youtube classique.
Appelable toujours par le meme menu ou bien url selectionnée dans l'editeur Markdown



## V2.7.3 Integration Soleil-Lune

Pour cette nouvelle integration on va aller recuperer les donnes astronominiques de la journée concernant le soleil et la lune de la ville choisie par l'utilisateur

- Dans les Préferences --> Intégrations on va ajouter une ligne:
Astro Soleil et Lune Ville: <champs de sasie> Bouton Rechercher <champ Latitude> <champ Longitude>

Lorsque l'utilisateur saisie une ville puis appuie sur rechercher on va  aller rechercher les coordonnées géographiques latitude et longitude de la ville qui seront utilisées pour le calcul des données adtronomiques de la nouvelle integration.
- Si on a trouvé les coordonnées on va les afficher dasn les champs <champ Latitude> <champ Longitude>
- Sinon Message d'erreur en demandant à l'utilisateur de saisir à nouveau la ville
Lorsque l'utilisateur valide les préférences, les donnes ville + <champ Latitude> et <champ Longitude> seront persistées dans le fichier des préférences utilisateurs settings.json.  Ces données seront recharchées à partir de settings.json lors des redemarrages ultérieurs
```json
    "integrations": {
        "show_quote_of_the_day": false,
        "youtube_enabled": true,
        "weather": {
            "city": "Poitiers",
            "api_key": "9d0c712506214035838132544251410"
        },
        "sun_moon": {
            "city": "Poitiers",
            "latitude": "46.580260",
            "longitude": "0.340196"
        }
```
beta1

on va continuer l amise en place de cette extension. Je vais rajouter une Integration pour les données astronomiques du jour
- Le menu pour lancer l'intégration "Intégrations --> Astro du jour"
- Le code nécessaire à l'integration sera stocké dans le dossier `bluenotebook/integrations`
- L'utilisateur devra au préalable saisir les donnees de paramètres Préferences --> Intégrations
- Si ces données n'existent pas afficher une boite de dialogue demandant à l'utilisateurs de saisir la ville concernée
- Si ces données existe on va aller chercher les données (pour aujourd'hui) qui nous interessent en utilisant un code similaire a celui qui suit:

```python
import requests
import json
from datetime import date
from typing import List, Dict, Any, Optional


# Dictionnaire de traduction pour les phases de la lune
MOON_PHASES_TRANSLATION = {
    "New Moon": ("Nouvelle Lune", "🌑"),
    "Waxing Crescent": ("Croissant Ascendant", "🌒"),
    "First Quarter": ("Premier Quartier", "🌓"),
    "Waxing Gibbous": ("Gibbeuse Ascendante", "🌔"),
    "Full Moon": ("Pleine Lune", "🌕"),
    "Waning Gibbous": ("Gibbeuse Descendante", "🌖"),
    "Last Quarter": ("Dernier Quartier", "🌗"),
    "Waning Crescent": ("Croissant Descendant", "🌘"),
}


def find_phenomenon_time(
    data_list: List[Dict[str, Any]], phenomenon: str
) -> Optional[str]:
    """
    Trouve l'heure d'un phénomène ('R' pour lever, 'S' pour coucher) dans une liste de données.
    Gère les anciennes ('R', 'S') et nouvelles ('Rise', 'Set') notations de l'API.
    """
    for item in data_list:
        phen_value = item.get("phen", "")
        # Comparaison insensible à la casse et gestion des abréviations
        if phen_value.lower() == phenomenon.lower() or (
            phenomenon in ("R", "S") and phen_value.startswith(phenomenon)
        ):
            # Nettoie l'heure pour ne garder que HH:MM
            return item.get("time", "").split()[0]
    return None


def generate_sun_html(
    sun_rise: Optional[str],
    sun_set: Optional[str],
    moon_phase: str,
    moon_emoji: str,
    illumination: str,
) -> str:
    """Génère un fragment HTML à partir des données du soleil et de la lune."""
    sun_rise_str = sun_rise or "N/A"
    sun_set_str = sun_set or "N/A"

    html = f"""
<div class="sun-moon-container">
    <div class="sun-moon-row sun-moon-row-split">
        <span class="sun-moon-item"><span class="sun-moon-emoji">🌅</span><span class="sun-moon-text">Lever: <strong>{sun_rise_str}</strong></span></span>
        <span class="sun-moon-item"><span class="sun-moon-emoji">🌇</span><span class="sun-moon-text">Coucher: <strong>{sun_set_str}</strong></span></span>
    </div>
    <div class="sun-moon-row">
        <span class="sun-moon-item"><span class="sun-moon-emoji">{moon_emoji}</span><span class="sun-moon-text">Phase lune: {moon_phase} ({illumination} illuminée)</span></span>
    </div>
</div>
"""
    return html


# Utiliser la date du jour pour éviter les erreurs de date future
today = date.today().strftime("%Y-%m-%d")
url = f"https://aa.usno.navy.mil/api/rstt/oneday?date=2025-10-22&coords=46.56890409839087,0.34354146083074305&tz=1&dst=true"

try:
    response = requests.get(url, timeout=10)
    # Lève une exception pour les codes d'erreur HTTP (4xx ou 5xx)
    response.raise_for_status()

    data = response.json()

    # Vérifier la présence d'une erreur applicative dans le JSON
    if data.get("error"):
        print(f"☀️ Erreur de l'API: {data.get('message', 'Erreur inconnue.')}")
    elif "properties" not in data or "data" not in data["properties"]:
        print("☀️ Erreur: La structure de la réponse JSON est inattendue.")
        print(json.dumps(data, indent=2))
    else:
        api_data = data["properties"]["data"]

        # Extraire les données en utilisant la nouvelle structure
        sun_rise_time = find_phenomenon_time(api_data.get("sundata", []), "Rise")
        sun_set_time = find_phenomenon_time(api_data.get("sundata", []), "Set")
        moon_phase_en = api_data.get("curphase", "Inconnue")
        frac_illum = api_data.get("fracillum", "N/A")

        # Traduire la phase de la lune et obtenir l'emoji
        moon_phase_fr, moon_emoji = MOON_PHASES_TRANSLATION.get(
            moon_phase_en, (moon_phase_en, "❔")
        )

        print(f"☀️ Lever soleil 🌅: {sun_rise_time or 'Non disponible'}")
        print(f"☀️ Coucher soleil 🌇: {sun_set_time or 'Non disponible'}")
        print(f"☀️ Phase lune: {moon_phase_fr} {moon_emoji} ({frac_illum} illuminée)")

        # Générer et afficher le fragment HTML
        html_fragment = generate_sun_html(
            sun_rise_time,
            sun_set_time,
            moon_phase_fr,
            moon_emoji,
            frac_illum,
        )
        print("\n--- Fragment HTML généré ---")
        print(html_fragment)

except requests.exceptions.RequestException as e:
    print(f"Erreur de requête HTTP: {e}")
```
- le fragment de HTML sera inséré à la position du curseur dans l'editeur Makdown avec les données
- le code CSS a été ajouté au fichier CSS de l'aperçu HTML par defaut: 
default_bluenotebook.css


Comment ça fonctionne ?
- Menu "Astro du jour" : Un nouveau sous-menu a été ajouté dans "Intégrations".
- Vérification de la configuration : Lorsque vous cliquez dessus, l'application vérifie si une ville avec sa latitude et sa longitude est configurée dans les préférences.
- Message d'erreur : Si ce n'est pas le cas, une boîte de dialogue vous invite à aller dans les préférences pour effectuer la configuration.
- Appel à l'API : Si tout est configuré, un worker est lancé en arrière-plan pour appeler l'API de l'USNO avec les coordonnées de votre ville.
- Insertion du HTML : Une fois les données récupérées, le fragment HTML est généré et inséré à l'emplacement de votre curseur dans l'éditeur. Le style CSS que vous aviez déjà ajouté dans default_bluenotebook.css sera automatiquement appliqué.

beta2

Ajouter les information de localisation : la ville  au fragment HTML généré par l'integration "Astro du Jour"
beta3

Pour l'integration Météo dans le fragment HTML généré sont melangées les données HTML et le CSS. Je voudrais externaliser le CSS de cette integration

## V2.7.2 Integration Book by ISBN

Je vais rajouter une Integration pour les livres en donnat l'ISBn comme critere de recherche
- Le menu pour lancer l'intégration livres "Intégrations --> Amazon ISBN"
- Le code nécessaire à l'integration sera stocké dans le dossiers `bluenotebook/integrations`
- L'utilisateur pourra soit séléctionner l'ISBN dans l'éditeur Markdown soit on demandera à l'utilisateur de fournir le code isbn via une boite de dialogue
- une fois l'ISBN récupéré on ira faire une recherche sur Amazon et on fabriquera un fragment HTML que l'in inserera à la place du code ISBN dans l'editeur ou bien à la position du curseur si aucun code ISBN n'etait sélectionné dans l'editeur Markdown
- Les éléments CSS suivants on déja étit intégré dans la feuille de style default_bluenotebook.css

```css
/* Style for book integration */

.book-container {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
}

.book-container h2 {
    color: #333;
    margin-top: 0;
}

.book-content {
    display: flex;
    align-items: flex-start;
}

.book-image {
    flex: 0 0 150px;
    margin-right: 20px;
}

.book-image img {
    max-width: 150px;
    height: auto;
    border: 1px solid #ddd;
}

.book-details {
    flex: 1;
}

.book-details p {
    margin: 5px 0;
}

.book-details a {
    color: #007185;
    text-decoration: none;
}

.book-details a:hover {
    text-decoration: underline;
}

.book-error {
    border: 1px solid #ccc;
    padding: 20px;
    max-width: 600px;
    margin: 20px auto;
    font-family: Arial, sans-serif;
    color: #d32f2f;
}

```
- Le code à utiliser pour l'intégration sera similaire à ce qui suit

```python
import requests
from bs4 import BeautifulSoup
import json
import time
import re

def get_book_info_from_amazon(isbn, region='fr'):
    """
    Récupère les métadonnées d'un livre Amazon via ISBN.
    :param isbn: ISBN-13 sans tirets (ex: '9782743664060')
    :param region: 'fr' pour amazon.fr, 'com' pour amazon.com, etc.
    :return: JSON avec métadonnées
    """
    # Nettoie l'ISBN
    isbn = re.sub(r'[^0-9]', '', isbn)
    if len(isbn) not in (10, 13):
        return json.dumps({"error": "ISBN invalide"}, ensure_ascii=False, indent=4)

    # URL de recherche Amazon
    domain = f"amazon.{region}"
    search_url = f"https://www.{domain}/s?k={isbn}&i=stripbooks"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
        'Referer': f'https://www.{domain}/'
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        # Étape 1: Recherche
        print(f"Recherche sur {search_url}")
        time.sleep(1)  # Délai politeness
        response = session.get(search_url, timeout=10)
        response.raise_for_status()
        print("Requête réussie, statut :", response.status_code)
        print("Contenu brut (premiers 500 caractères) :", response.text[:500])

        # Parse le HTML
        soup = BeautifulSoup(response.content, 'lxml')

        # Vérifie si la page contient un CAPTCHA
        captcha = soup.select_one('form[action="/errors/validateCaptcha"]')
        if captcha:
            return json.dumps({"error": "CAPTCHA détecté, requête bloquée par Amazon"}, ensure_ascii=False, indent=4)

        # Trouve les liens de produits
        product_links = soup.select('a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style, a.a-link-normal[href*="/dp/"]')
        if not product_links:
            print("Aucun lien produit trouvé dans les résultats.")
            # Fallback sur ASIN connu pour cet ISBN
            if isbn == "9782743664060":
                product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                print(f"Fallback sur ASIN connu: {product_url}")
            else:
                return json.dumps({"error": "Aucun produit trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)
        else:
            # Log des 3 premiers résultats
            print("3 premiers résultats trouvés :")
            for link in product_links[:3]:
                title = link.get_text(strip=True)
                href = link.get('href', '')
                print(f"- {title[:100]}... (href: {href})")

            # Sélectionne le lien pertinent
            product_url = None
            for link in product_links:
                href = link.get('href', '')
                title = link.get_text(strip=True).lower()
                if isbn in href or 'jaguar' in title or 'bonnefoy' in title:
                    asin_match = re.search(r'/dp/([A-Z0-9]{10})', href)
                    if asin_match:
                        asin = asin_match.group(1)
                        product_url = f"https://www.{domain}/dp/{asin}"
                        print(f"Lien produit sélectionné: {product_url}")
                        break

            if not product_url:
                # Fallback sur ASIN connu
                if isbn == "9782743664060":
                    product_url = f"https://www.{domain}/dp/B0DK6KTBMH"
                    print(f"Fallback sur ASIN connu: {product_url}")
                else:
                    return json.dumps({"error": "Aucun produit pertinent trouvé pour cet ISBN"}, ensure_ascii=False, indent=4)

        # Étape 2: Page produit
        print(f"Page produit: {product_url}")
        time.sleep(1)
        response = session.get(product_url, timeout=10)
        response.raise_for_status()
        print("Contenu page produit (premiers 500 caractères) :", response.text[:500])
        soup = BeautifulSoup(response.content, 'lxml')

        # Extraction des métadonnées
        book_data = {}

        # Titre
        title_elem = soup.select_one('#productTitle')
        book_data['titre'] = title_elem.get_text(strip=True) if title_elem else "Inconnu"

        # Auteur(s)
        authors = soup.select('a.a-link-normal.contributorName, .author a.a-link-normal, span.author a')
        book_data['auteur'] = '; '.join([a.get_text(strip=True) for a in authors]) if authors else "Inconnu"

        # Éditeur
        pub_elem = soup.select_one('div#rpi-attribute-book_details-publisher .rpi-attribute-value, span:contains("Éditeur") + span, td:contains("Éditeur") + td')
        book_data['editeur'] = pub_elem.get_text(strip=True) if pub_elem else "Inconnu"

        # Date publication
        date_elem = soup.select_one('div#rpi-attribute-book_details-publication_date .rpi-attribute-value, span:contains("Date") + span, td:contains("Date") + td')
        book_data['date_publication'] = date_elem.get_text(strip=True) if date_elem else "Inconnu"

        # Description
        desc_elem = soup.select_one('#productDescription, #bookDescription_feature_div')
        book_data['resume'] = desc_elem.get_text(strip=True) if desc_elem else "Non disponible"

        # ISBN (confirmation)
        book_data['isbn'] = isbn

        # Pages
        pages_elem = soup.select_one('div#rpi-attribute-book_details-fiona_pages .rpi-attribute-value, span:contains("pages") + span, td:contains("pages") + td')
        book_data['pages'] = pages_elem.get_text(strip=True) if pages_elem else "Inconnu"

        # Note (étoiles)
        rating_elem = soup.select_one('#acrPopover + span .a-icon-alt')
        book_data['note'] = rating_elem.get_text(strip=True) if rating_elem else "Inconnu"

        # Couverture URL
        cover_elem = soup.select_one('#imgBlkFront, #main-image-container img')
        book_data['couverture_url'] = cover_elem['src'] if cover_elem and 'src' in cover_elem.attrs else "Non disponible"

        # URL produit pour le lien cliquable
        book_data['product_url'] = product_url

        return json.dumps(book_data, ensure_ascii=False, indent=4)

    except requests.RequestException as e:
        return json.dumps({"error": f"Erreur requête: {str(e)}"}, ensure_ascii=False, indent=4)
    except Exception as e:
        return json.dumps({"error": f"Erreur inattendue: {str(e)}"}, ensure_ascii=False, indent=4)

def generate_html_fragment(book_data_json):
    """
    Génère un fragment HTML pour afficher les métadonnées du livre.
    :param book_data_json: JSON string contenant les métadonnées
    :return: Fragment HTML
    """
    try:
        book_data = json.loads(book_data_json)
        if "error" in book_data:
            return """
            <div class="book-error">
                <h2>Erreur</h2>
                <p>{}</p>
            </div>
            """.format(book_data['error'])

        # Construction du fragment HTML
        html = """
        <div class="book-container">
            <h2>{}</h2>
            <div class="book-content">
                <div class="book-image">
                    <img src="{}" alt="Couverture">
                </div>
                <div class="book-details">
                    <p><strong>Auteur :</strong> {}</p>
                    <p><strong>Éditeur :</strong> {}</p>
                    <p><strong>Date de publication :</strong> {}</p>
                    <p><strong>ISBN :</strong> {}</p>
                    <p><strong>Pages :</strong> {}</p>
                    <p><strong>Note :</strong> {}</p>
                    <p><strong>Résumé :</strong> {}</p>
                    <p><strong>Source :</strong> Données extraites d'<a href="https://www.amazon.fr" target="_blank">Amazon.fr</a></p>
                    <p><a href="{}" target="_blank">Voir sur Amazon.fr</a></p>
                </div>
            </div>
        </div>
        """.format(
            book_data.get('titre', 'Inconnu'),
            book_data.get('couverture_url', 'https://via.placeholder.com/150'),
            book_data.get('auteur', 'Inconnu'),
            book_data.get('editeur', 'Inconnu'),
            book_data.get('date_publication', 'Inconnu'),
            book_data.get('isbn', 'Inconnu'),
            book_data.get('pages', 'Inconnu'),
            book_data.get('note', 'Inconnu'),
            book_data.get('resume', 'Non disponible'),
            book_data.get('product_url', '#')
        )
        return html

    except json.JSONDecodeError:
        return """
        <div class="book-error">
            <h2>Erreur</h2>
            <p>Erreur lors du traitement des données JSON.</p>
        </div>
        """

# Exemple d'utilisation
isbn_exemple = "9782743664060"  # Le rêve du jaguar
book_data_json = get_book_info_from_amazon(isbn_exemple, region='fr')
print("JSON des métadonnées :")
print(book_data_json)
print("\nFragment HTML :")
print(generate_html_fragment(book_data_json))
```
beta1
## V2.7.1 Integration Trace GPX

Je vais rajouter une Integration pour les fichiers GPX. Aufinal j'insere une carte statique sous la forme d'une image HTML avec le tracé GPX et en légende la date et le lieu du tracé , heure de debut et heure de fin. Cette image sera clickable et ouvrira OpenStreetMap avec comme marqueur le pont de départ du tracé GPX. Le tracé GPX sera recuperer soit en local dans un dossier soit à distrace via un lien Web. Dans tous les cas ce travé GPX sera sauvegardé dans le dossier gpx du journal sous le nom YYYYMMJJ_Lieu.gpx (ou  YYYYMMJJ correspond au jour ou le tracé a commencé et le Lieu du tracé). 

Installer les packages `gpxpy` `py-staticmaps`
```bash
pip install gpxpy py-staticmaps
```
- Le menu pour lancer l'intégration GPX Menu "Intégrations --> Trace GPX"
- Le code nécessaire à l'integration sera stocké dans le dossiers `bluenotebook/integrations`
- Le tracé GPX sera recuperer soit en local dans un dossier soit à distrace via un lien Web
- Ce tracé GPX sera sauvegardé dans le dossier gpx du journal sous le nom YYYYMMJJ_Lieu.gpx (ou  YYYYMMJJ correspond au jour ou le tracé a commencé et le Lieu du tracé). 
- Carte fabriquée au format PNG sera stockée dans le dossier images du Journal. On demandra a l'utilisateur la taille de la largueur de l'affichage en Pixels
- Cette carte sera archivée dans le dossier `images` du journal sous le nom  YYYYMMJJ_lieu_gpx.png (ou  YYYYMMJJ correspond au jour ou le tracé a commencé et le Lieu du tracé). 
- pour créer la carte on va utiliser le package `staticmaps` <https://www.npmjs.com/package/staticmaps> et GitHub <https://github.com/StephanGeorg/staticmaps> et   le code pour fabriquer la carte sera inspiré de 

```
import sys

import gpxpy
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

with open(sys.argv[1], "r") as file:
    gpx = gpxpy.parse(file)

for track in gpx.tracks:
    for segment in track.segments:
        line = [
            staticmaps.create_latlng(p.latitude, p.longitude) for p in segment.points
        ]
        context.add_object(staticmaps.Line(line))

for p in gpx.walk(only_points=True):
    pos = staticmaps.create_latlng(p.latitude, p.longitude)
    marker = staticmaps.ImageMarker(pos, "start.png", origin_x=27, origin_y=35)
    context.add_object(marker)
    break

 # render anti-aliased png (this only works if pycairo is installed)
image = context.render_cairo(800, 500)
image.write_to_png("draw_gpx.cairo.png")

```
- Pour marquer le début du trajet il faut mettre une icone de marqueur start.png qui est dans le repértoire  `bluenotebook/resources/icons/`
- cette carte générée permettra de générer un fragment HTML du type suivant (ici lieu = Poitiers et coordonnées GPX sont les coordonnées du 1er Point GPX ou il i a le marqueur start.png)


```html
<figure style="text-align: center;">
    <a href="https://www.openstreetmap.org/#map=16/46.569111995162096/0.34343837205047145">
         <img src="images/YYYYMMJJ_lieu_gpx.png" alt="Trace GPX - Poitiers" width="800">
    </a>
    <figcaption style="font-weight: bold;">Trace GPX - Poitiers - OpenStreetMap</figcaption>
</figure>
```
- Cette carte est doc clickable et le lien renvoie vers une carte openstreetmap avec un marqueur cetré sur le prmier point de la traceGPX

beta1

Il faudrait modifier le code HTML généré pour les traces GPX pour rendre le Lieu dans figcaption (ici poitiers) clickable et ouvrir https://www.openstreetmap.org/?mlat=46.561517&mlon=0.323711#map=16/46.561517/0.323711. Les coordonées GPS utilisées étant celle du premier point de la trace GPX.
Cela donnerait quelque chose comme:
```html
<figure style="text-align: center;">
    <a href="https://www.openstreetmap.org/#map=16/46.569194/0.344577" target="_blank">
         <img src="images/20250506_Poitiers_gpx.png" alt="Trace GPX - Poitiers" width="1000">
    </a>
    <figcaption style="font-weight: bold;">Trace GPX: <a href="https://www.openstreetmap.org/?mlat=46.561517&mlon=0.323711#map=16/46.561517/0.323711">Poitiers</a> - 06/05/2025 à 09:45 - Durée: 1:48:24</figcaption>
</figure>
```
beta2

le marqueur de départ start.png n'est pas localisé exactement au point de départ de la trace GPX peux tu corriger cela

## V2.6.4 Imagces clickables + Integration Youtube MaJ

Lorsque j'insère une image (Menu Insérer --> Image(<img ..>))dans le journal, l'image est copiée dans le dossier images du journal et un fragment HTML est généré du type par exemple

```html
<img src="images/20251020112436_20251018_092855.jpg" width="600">
```

je voudrais que le fragment html soit modifier pour rendre l'image cliclable et donc qu'elle puisse s'ouvrir en grand dans l'apercu HTML.
beta1

 Exemple:



<figure style="text-align: center;">
    <a href="images/20251020160600_IMG_6938-4k.jpg" target="_blank"><img src="images/20251020160600_IMG_6938-4k.jpg" width="400" alt="Image"></a>
    <figcaption style="font-weight: bold;">08/06/2025 15:45 : Chauvigny : Canon EOS 700D : ƒ/10.0 : Vitesse: 1/125s : Focale: 24.0mm : ISO: 100</figcaption>
</figure>



2 -
dans mon application Bluenotebook je génère des fragments HTML dans l'éditeur Markdownd pour affichier des images dans la fenetre d'aperçu HTML (preview.py). Ces images sont clickables

<figure style="text-align: center;">
    <a href="images/20251020160600_IMG_6938-4k.jpg" target="_blank"><img src="images/20251020160600_IMG_6938-4k.jpg" width="400" alt="Image"></a>
    <figcaption style="font-weight: bold;">08/06/2025 15:45 : Canon : Canon EOS 700D : ƒ/10.0 : Vitesse: 1/125s : Focale: 24.0mm : ISO: 100</figcaption>
</figure>
 

Quand je clique sur une image dans l'aperçu, j'ai bien une flèche qui se dessine mais après click rien ne se passe

je voudrais qu'un clic sur une image dans l'aperçu l'ouvre bien en grand dans de la visionneuse d'images ou du navigateur par défaut et que Cela fonctionne  également pour tous les autres liens (par exemple, les liens vers des sites web) que je pourrais avoir dans mes  notes.

beta2

3 image Markdown
Dans cette meme application j'insere des images au format Markdown.

 ![](images/20251020164812_2025_06_25_img_7028_01.jpg)

Comment faire pour que ces images soient également ckliqiable dans l'Apercu HTML et s'ouvre  dans la visionneuse par defaut
beta3

4- Embelissement css images
 
@CSS /* Styles pour les images cliquables */ ajouté --> Theme CSS -->  defaul_preview2;css

```css
/* Styles pour les images cliquables */
a img {
    transition: border 0.2s ease, opacity 0.2s ease;
}

a img:hover {
    border: 2px solid #3498db;
    opacity: 0.9;
}
```
beta4

dans mon application Bluenotebook je génère des fragments Markdown dans l'éditeur   pour affichier des images qui doivent permettre de lancer des vidéo Youtube. voici par exemple le code Markdown généré  par le menu de la fenètre principale "Integrations --> Vidéo Youtube" 

```
@@Video @@Youtube Perfect Morrning 🎶✨ Comfortable music that makes you feel positive | Best Indie/Pop/Folk/Acoustic <https://www.youtube.com/watch?v=796pqzI9T_w>

[![Perfect Morrning 🎶✨ Comfortable music that makes you feel positive | Best Indie/Pop/Folk/Acoustic](https://img.youtube.com/vi/796pqzI9T_w/hqdefault.jpg)](https://www.youtube.com/watch?v=796pqzI9T_w)

⬆️**Cliquez sur l'image pour lancer la vidéo**⬆️

```

depuis que l'on a modifié le code pour rendre les images clickable Markdown, ce n'est plus la video youtube que je lance mais 
il faudrait corriger le code généré par le menu de la fenètre principale "Integrations --> Vidéo Youtube" pour générer un fragment HTML (et pas MArkdown) à la place qui lorsque l'on demande à integrer la video youtube https://www.youtube.com/watch?v=796pqzI9T_w  :

1 - Affiche le titre de la video comme ici: @@Video @@Youtube Perfect Morrning 🎶✨ Comfortable music that makes you feel positive | Best Indie/Pop/Folk/Acoustic + URL de la video

2- Affiche la vignette de la video youtube choisie ici: https://img.youtube.com/vi/796pqzI9T_w/hqdefault.jpg et qui soit clickable . Si on clique dessus on lance la video youtube ici: https://www.youtube.com/watch?v=796pqzI9T_w dans un navigateur externe

3- en figcaption de l'image "Voir sur Youtube"
beta5

Je voudrais que tout le code relatif à l'insertion de video youtube soit dans le fichier bluenotebook/integrations/youtube_video.py

cela comprend le code HTML dans la metheode insert_youtube_video de editor.py pour eviter d'avoir du code et du parametrage dispersé dans plusieurs fichiers y compris le style CSS pour les videos Youtubes Integrées

```css
/* Style pour les vidéos YouTube intégrées */
figure.youtube-video-figure {
    border: 2px solid #e50914; /* Une bordure rouge rappelant YouTube */
    border-radius: 12px;       /* Des coins plus arrondis pour le conteneur */
    padding: 10px;             /* Un peu d'espace entre la bordure et l'image */
    background-color: #f0f0f0; /* Un fond légèrement gris pour faire ressortir la figure */
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    /* Corrections pour l'alignement */
    display: inline-block; /* S'adapte à la largeur du contenu */
    margin: 1em auto;      /* Centre le bloc horizontalement */
    text-align: center;    /* Centre la légende (figcaption) */
}

figure.youtube-video-figure:hover {
    transform: scale(1.02); /* Un léger effet de zoom au survol */
    box-shadow: 0 6px 12px rgba(0,0,0,0.3); /* Ombre plus prononcée au survol */
}
```


## V2.6.3 Dark Theme Support

1- Afin de supprimer le maximun de surstyle je voudrais pour le panneau navigation et ses different widgets supprimer toutes élements de surstylage par rappport au theme systme. ne concerver que les jours en bleu (ceux qui ont une note dans le calendrier) et le jour d'aujour'hui en jaune. tous les widget sont concerne barre de bouttons, calendrier, barre de recher, bouton et liest de recher, panneau de resultat de rechcher, nuage de mots, nuage de tags. main_window.py navigation.py word_cloud.py tag_cloud.py custom_widgets.py search_results_panel.py

2 - la couleur de fond du panneau navigation reste claire alors qu'elle devrait etre combre avec un theme sombre. coment corriger cela
beta1

3- Corrections des boutons de Navigation du panneau NAvigation 

4- Je voudrait que le header du panneau navigation soit comme les autres headers de panneaux "Editeur Markdown" par exemple. c'est a dire qu'il ressemble à un onglet dont la taille couvre juste le texte du header "Navigation" et de la meme couleur que les autres onglets/headers


## V2.6.2.2 doc install Windows Linux run_bluenotebook.bat

## V2.6.2.1 README.md MaJ + copie d'écran

Basé sur document architecture technique générée par Gemini CLI

## V2.6.2 Export EPUB bug Fix + Refactoring PDF

Modifier table des matières pour inclure tous les headers de niveau 1 # et de niveau 2 ##
- Structure de la table des matières (toc) : Pour créer une table des matières avec des sous-niveaux (un chapitre de jour contenant des liens vers les titres de la note), EbookLib attend une structure comme (Section, (chapitre_principal, lien_1, lien_2, ...)). Le code précédent mélangeait des objets EpubHtml et des Link de manière incorrecte. La correction s'assure que chaque entrée de la table des matières respecte ce format.
- Ajout de l'index à la table des matières : La page d'index des tags doit être ajoutée à la table des matières en tant que epub.Link, et non en tant qu'objet EpubHtml brut.

corrections
- Gestion des chapitres sans sous-titres : Le code vérifie maintenant si une note contient des sous-titres (if sub_links:).

Si c'est le cas, il crée une section hiérarchique dans la table des matières, comme prévu.
Si la note n'a pas de sous-titres, il ajoute simplement le chapitre principal à la table des matières, sans créer de section vide, ce qui évitait l'erreur.
- Ajout de la page d'index : J'ai également corrigé la manière dont la page d'index des tags est ajoutée à la table des matières. Elle doit être ajoutée en tant qu'objet de chapitre (EpubHtml) et non en tant que simple lien (Link), ce qui était une autre source potentielle d'erreur

Fixed with Claude !!
beta1

main_window.py je voudrais externaliser tout le code qui sert à l'export PDF dans un fichier python dans le répertoire integrations comme cela a été fait pour l'export EPUB

beta 2

add aide en ligne principaux packages python

beta3

## V2.6.1 Export EPUB

Je voudrais pouvoir exporter mon journal a format epub. le livre de vra contenir une table des matières, une couverture, un titre , un auteur.
Menu Fichier->" Export Journal EPUB..." ce choix de menu viendra juste avant "Exporter Journal PDF ..."
Une boite de dialogue Option d'exportation du Journal EPUB (à l'identique de celle utilise pour l'export PDV
Puis une deuxieme boite de dialogue permettant de choisir l'emplacement du fichier epub. Cet emplacement sera persisté dans les préferences utilisateur settings.json. et sera reproposé lors des exports ultérieurs.
Le fichier EPUB sera a la norme EPUB 3.
L'image de couverture sélectionnée par l'utilisateur servira à fabrique la couverture du livre. Cette couverture du livre sera une image jpg composé d'une moitier haute (l'image sélectionnée par l'utilisateur) et une moitier basse sur fond blanc et police de caractère noire avec le titre, l'auteur (si disponible, la plage de dates couvertes par le journal.
Tout le code produit pour la logique de cet export sera externalisé dans un fichier python spécifique
Y a t il d'autres questions a se poser ?

```bash
pip install EbookLib Pillow
```
beta1

bien sur les images sont manquantes dans le epub. Il est nécessaire de les inclure dasn le epub.
Ils faut les rapatrier en local dasn le epub et donc
- soit aller les chercher en utilisant l'URL
- Soit aller les chercher dans le dosser images du Journal.
toutes les images seront stockées dasn le dossier Images de l'epub dans un format jpg compressé à80% taille maxi (800 px x 800 px) pour diminuer la taille du fichier.

L'intégration des images dans le fichier EPUB est une étape cruciale pour rendre l'export complet et autonome.

Pour ce faire, je vais modifier le EpubExportWorker afin qu'il analyse le contenu HTML de chaque note, trouve toutes les images, les télécharge ou les copie, les redimensionne, les compresse, puis les intègre directement dans le fichier .epub.

J'utiliserai la bibliothèque BeautifulSoup pour analyser le HTML de manière fiable et requests pour télécharger les images depuis des URLs.

beta 2
 

Il faudrait changer la position du Menu Fichier->" Export Journal EPUB..." le positionner entre export HTML et export Journal PDF

pour traiter les images svg --> Sinon Erreur car non supportées par Pillow

Pour que cette modification fonctionne, vous devez installer la bibliothèque cairosvg et ses dépendances système.

1. Installation de la bibliothèque Python :

```bash
pip install cairosvg
```
2. Installation des dépendances système (sur Linux/Debian/Ubuntu) :

cairosvg a besoin de la bibliothèque libcairo2. Si elle n'est pas déjà sur votre système, vous pouvez l'installer avec :

```bash
sudo apt-get update
sudo apt-get install libcairo2-dev
```
beta3


Je voudrais créer un index a la fin du livre qui liste toute les tags (du type @@Python) dans le epub et qu me permette d'acceder rapidement aux pages. A chaque tag classé suivant ordre alphanumerique une liste de page cliquable pour acceder à l'emplacement du tag. Pages d'index ayant pour titre Index de Tags et bien listé dans spine et toc.ncx.





externaliser toute la logique de l'export PDF

## V2.5.3  Barre d'outils des panneaux

Je voudrais afficher sous la barre de menu une barre de boutons switch ayant comme label le nom des panneaux (Navigation, Plan, EditeurAperçu )
Sur une ligne
Navigation (switch) Plan (switch) Editeur (Switch) Aperçu (switch)

- Quand un switch est on le panneau est visible
- Quand un switch est off le panneau est masqué
- Editeur est toujours on et grisé (pas desactivable)
- D'autres panneaux viendront par la suite
- Au demarrage les switchs tienne comtpe des préférences (fichier settings.json). Sinon par defaut editeur+Aperçu HTML seulement

beta1

comme j'ai ajouté cette barre de menu, je peux supprimer le menu affichage et ses 3 sous menu de la barre de menu principale
beta2

Barre d'outils des panneaux: je voudrais remplacer les boutons simples par des QtQuick.Controls
Pour un arrangement de type
Navigation (QtQuick.Controls) Plan (QtQuick.Controls) Editeur (QtQuick.Controls) Aperçu (QtQuick.Controls)

## V2.5.2 add emoji + About

je voudrais ajouter ces trois emoji à la liste des emoji du Menu Inserer --> Emoji

✅ ❌ ⚠️

## V2.5.1 Integration Meteo + Preferences  

<https://www.weatherapi.com/> and <https://github.com/weatherapicom/>

**Test Request:**

http://api.weatherapi.com/v1/current.json?key=XXXXXXXX&q=Poitiers&aqi=no

Execute with Rest Client : press `F1` and then select/type `Rest Client: Send Request`, the response will be previewed in a separate webview panel of Visual Studio Code
----------------------

## Integration:   Météo Weatherapi.com
.

Dans préférences... -> Intégrations
On va ajouter une ligne :
Météo Weatherapi.com  `Ville :` (Champ de Saisie de 20 Charactères) +  `Clé API :` : (Champ de Saisie de 30 Charactères)

Ces ajouts préparent  le terrain pour l'implémentation de la logique de récupération des données météo. N'hésitez pas si vous avez d'autres questions !
beta1

Les champs comme la ville et la clé API pour la météo ne doivent pas avoir de valeur par défaut dans le code source. Ils doivent être créés dans le fichier settings.json de l'utilisateur uniquement lorsqu'il les saisit.
```json
    "integrations": {
        "show_quote_of_the_day": false,
        "youtube_enabled": true,
        "weather": {
            "city": "Poitiers",
            "api_key": "d0c71250621403xxx8132544251410"
        }
```
beta2

Je voudrait ajouter un sous menu au Menu" Intégrations" appelé "Méteo  Weatherapi.com" 

le code associé à ce traitements sera externalisé dans un fichier python dans le répertoire bluenotbook/integrations 

Quand ce menu est appelé :
- On va chercher les paramètres de la météo `Ville` et  `Clé API`  qui sont dans le fichier settings.json de l'utilisateur
```json
        "weather": {
            "city": "Poitiers",
            "api_key": "d0c71250621403xxx8132544251410"
```
Météo Weatherapi.com  `Ville` et  `Clé API` 

- Si les paramètres sont vides ou pas renseignés tous les deux on va afficher une fenetre d'erreur demandant à l'utilisateur de renseigner ces paramètres
- Sinon on va sur la base de ces paramètres générere une requète API de la forme

http://api.weatherapi.com/v1/current.json?key=d0c71250621403xxx8132544251410&q=Poitiers&aqi=no
q=Nom de la ville
key=d0c71250621403xxx8132544251410

- Si erreur lors de cette requete afficher un boite de dialogue avec le libellé de l'erreur
-Sinon

le retour de cette API est un flux JSON qu'il va falloir parser pour retrouver les informations
```json
    "name": "Poitiers",
    "region": "Poitou-Charentes",
    "country": "France",
    "localtime": "2025-10-15 16:16"
    "temp_c": 18.1,
    "condition": {
      "text": "Sunny",
      "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
      "code": 1000
    },
    "wind_kph": 26.3,
    "humidity": 64,
```
A partir de ces données on va construire un fragment  HTML incluant les données textuelles avec libellés en Français mais qui pourront etre traduit dans une phase ultérieure ainsi l'icone renvoyée dans le flux pour présenter les conditions. Essaye quelque chose de pas trop gros (2 lignes max + icones)

Ce fragment HTML sera inclus à la position du caret dans l'éditeur au moment de l'appel
beta3

Il faudrait ajouter l'heure dans le fragment météo après la température dans le format HH:MM

```html
 <div style="display: flex; align-items: center; border: 1px solid #ccc; border-radius: 5px; padding: 5px; background-color: #f9f9f9; max-width: 450px;">
    <img src="https://cdn.weatherapi.com/weather/64x64/day/113.png" alt="Ensoleillé" style="margin-right: 10px; width: 48px; height: 48px;">
    <div style="font-family: sans-serif; font-size: 0.9em;">
        <strong style="color: #333;">Poitiers:</strong> Ensoleillé, <strong>18.4°C</strong> à 16:48<br>
        <span style="color: #666;">Vent: 26.3 km/h, Humidité: 60%</span>
    </div>
</div>
```



## V2.4.6 Improve Exif Display + Onglet Navigation Journal

Je veux modifier le HTML généré lors d'une insertion d'image Menu Insérer -> Image (<img..>) dans le cas ou il y a des information exif a afficher 
objectif: Réduire la taille de l'affichage, plus compact et ajourter un marker à OpenSteetMaps
toute la logique reste la meme c'est juste le HTML généré qui change
voici les deux versions avant/ APrès pour illuster le changement

Avant:

<img src="images/20251013092158_PXL_20231027_083617007.jpg" width="800">

| Propriété | Valeur |
|---|---|
| Lieu | Chauvigny |
| Coordonnées GPS | [46.569323, 0.644341] |
| OpenStreetMap | <https://www.openstreetmap.org/#map=16/46.569323/0.644341> |
| Date et Heure de la prise de vue | 27/10/2023 10:36 |
| Appareil | Google Pixel 6a |
| Ouverture | ƒ/1.7 |
| Vitesse | 1/687 |
| Focale | 4.38mm |
| ISO | 56 |


Après:

<figure style="text-align: center;">
   <img src="images/20251013092158_PXL_20231027_083617007.jpg" width="800">
    <figcaption style="font-weight: bold;">   
       <a href="https://www.openstreetmap.org/?mlat=46.569323&mlon=0.644341#map=16/46.569323/0.644341">
       Poitiers</a> : 19/11/2023 16:36  : Google Pixel 6a : ƒ/1.7  : Vitesse: 1/1063 : Focale: 4.38mm : ISO:56    
   </figcaption>
</figure>

Beta1

dans la fenetre principale, L'affichage de l'onglet "Navigation Journal" n'est pas correct:
- Il faut enlever l'emoj
- L'onglet est trop long (toute la largeur du panneau. Il ne boit couvrir que la longueur du texte "Navigation Journal")
beta2 OK


## V2.4.5 Bug Editor: Coloration Menu Contextuel
1
@bluenotebook @editor.py a chaque remedemarrage la couleur de fond de l'editeur reprends la couleur par defaut et perd celle choisie par l'utilisateur avec son theme. Lorsque l'utilisateur selectionne son theme les couleurs et la couleur de fond sont bien persister dans settings.json.
Mais au redemarrage l'application utilise la couleur de fond par defaut. le probleme es uniquement sur la couleur de fond (SettingsManager ?)
beta1

2
Lorsque je passe la souris sur un élément du Menu contextuel de l'éditeur, l'élément change de couleur.
La couleur actuelle est une couleur tres claire qui n'es pas tres visible avec des themes clairs.
Je voudrais que l'element choisi ne change pas de couleur mais soit mis en surbrillance. a la fois pour le menu et ses sous menus

## 2.4.4 Integration Insert Image with Exif

Je voudrait modifier l'action du menu Insérer --> Image (<img ...>)
A la fin de du processus après avoir demandé "La taille maximale en pixels", il faudrait analyser si l'image contient des données Exif et dans le cas positif demander à l'utilisateur s'il souhaite afficher ces données Exif en dessous de l'image.

Si ces données  existent dans l'image et que l'utilisateur souhaite les afficher. Il faudra afficher le résultat sous la forme

```markdown
<img src="images/20251012085153_PXL_20240121_083252469.NIGHT.jpg" width="400">

| Lieu | Poitiers |
|---|---|
|Coordonnées GPS| [46.569317, 0.346048] |
| OpenStreetMap | <https://www.openstreetmap.org/#map=16/46.569317/0.346048> |
|Date et Heure de la prise de vue|25/10/2025 12:10|
| Appareil|Google Pixel 6a|
| Ouverture|ƒ/1,73|
| Vitesse|1/487|
| Focale|84 ISO|
| ISO |84 ISO |

```

Cela veut dire qu'il faut retourver la Ville (Lieur) à partir des coordonnées GPS si elles existent.
 


## V2.4.3 New Look

1. Modernisation des Panneaux (editor.py, preview.py, outline.py)
Les en-têtes des panneaux "Éditeur", "Aperçu" et "Plan" étaient lourds. Je les ai remplacés par de simples labels en gras, sans fond ni bordure, pour un look beaucoup plus épuré.

2. Affinement des Séparateurs et de l'Interface (main_window.py)
J'ai rendu les séparateurs (QSplitter) plus fins et discrets. Ils ne s'affichent en couleur qu'au survol de la souris. Les boutons pour réduire les panneaux ont également été redessinés pour être plus modernes et moins intrusifs.

Résultat
Ces changements combinés donnent à BlueNotebook une apparence plus professionnelle et minimaliste. L'interface est moins chargée, les séparations sont plus subtiles et l'ensemble est plus agréable à l'œil, vous permettant de mieux vous concentrer sur votre écriture.
beta1

Supprimer les Emoticones de tous les menus e dans les Préférences
Beta2

Affiner encore les séparateurs entre panneaux
diminuer la taille de la police de caractères dans le panneau Plan du documen
beta3

 Permettre à l'utilisateur d'ajuster la taille de la police du plan du document indépendamment de celle de l'éditeur améliorera grandement le confort de lecture.

J'ai implémenté cette fonctionnalité en ajoutant un nouveau champ dans les préférences et en mettant à jour la logique pour l'appliquer.
beta4


Transformer les en-têtes de panneaux pour qu'ils ressemblent à des onglets donnera à l'application une apparence plus intégrée et professionnelle, très similaire à celle des éditeurs de code modernes.



Refaire la doc en ligne avec le menu
Beta3

## V2.4.2 Bugs Fixing Coloration syntaxique Bloc de code

Bug dans l'editeur Markdown. Quand dans un bloc de code il y a un caractère # comme premier caractère d'une ligne, ce # est pris comme un caractère de header markdown. s'il est en deuxieme colonne ou plus c'est ok. bien sur c'est vrai pour ## ou ###. Comment eviter qu'il soit interprété comme Header

Pou illuster mon propos si j'ai le bloc de code suivant
 
```txt
qsqs# # sdsd
## dsds
# sdsd
 ### sdqsd
```
 
les ligne 2 et 3 sont interprétées comme header, pour les ligne 1 et 4 c'est bon

J'ai ajusté la logique dans la méthode `highlightBlock` du fichier `bluenotebook/gui/editor.py`. Le code va maintenant :

- Détecter correctement le début et la fin d'un bloc de code.
- Appliquer le formatage du bloc de code.
- Réinitialiser l'état (setCurrentBlockState(0)) lorsque la balise de fin ``` est trouvée, pour que le surligneur puisse recommencer à analyser normalement les lignes suivantes.
- Continuer à ignorer les autres règles de formatage (comme les titres #) à l'intérieur des blocs de code.

beta1

Cela a resolu le problème de coloration syntaxique dans l'editeur mais pas dans le panneau plan du document. Dans ce panneau qui presente une vue arborescente du document les les ligne 2 et 3 sont interprétées comme header, pour les ligne 1 et 4 c'est bon l'exemple est:

```txt
qsqs# # sdsd
## dsds
# sdsd
 ### sdqsd
```

## V2.4.1 Refactoring Extension

Déplacer la logique des intégrations dans des fichiers dédiés rend le projet beaucoup plus propre, maintenable et facile à faire évoluer.

J'ai effectué le refactoring que vous avez demandé. Voici le détail des modifications :

1. Création d'un nouveau fichier pour l'intégration YouTube
J'ai créé un nouveau fichier bluenotebook/integrations/youtube_video.py qui contient maintenant toute la logique de traitement d'une URL YouTube (extraction de l'ID, récupération du titre, etc.).

2. Mise à jour de main_window.py
La fenêtre principale utilise maintenant la nouvelle fonction get_youtube_video_details. La logique de l'interface (boîtes de dialogue) reste ici, mais le traitement de l'URL est délégué au nouveau module.

Avantages de ce refactoring

- Séparation des préoccupations : La logique de l'interface (main_window.py) est maintenant distincte de la logique métier de l'intégration (youtube_video.py).
- Réutilisabilité : La fonction get_youtube_video_details pourrait être utilisée ailleurs dans l'application si nécessaire, sans dépendre de l'interface graphique.
- Testabilité : Il est beaucoup plus facile d'écrire des tests unitaires pour la fonction get_youtube_video_details maintenant qu'elle ne dépend plus de QMessageBox.
- Clarté : Le code de main_window.py est allégé et plus facile à lire.

beta1

Je voudrais renommer le menu "Maps GPS" en" Carte GPS"

beta2

Lorsque du texte est sélectionné je voudrais ajouter dans le menu contextuel la possibilité de mettre en lien URL ou Markadown comme je l'ai fait dans le menu insérer

Dans la méthode show_context_menu du fichier bluenotebook/gui/editor.py, j'ai ajouté un nouveau sous-menu "🔗 Liens". Ce menu n'apparaît que si vous avez sélectionné du texte et contient deux actions :

- Lien (URL ou email) : Encadre le texte sélectionné avec des chevrons (< >), le transformant en un lien cliquable.
- Lien Markdown : Ouvre la boîte de dialogue pour créer un lien Markdown complet (texte), en pré-remplissant le champ "Texte du lien" avec votre sélection.
 
## V2.3.6 Integration GPS -> Maps

    # pip install py-staticmaps[cairo]
    # sudo apt install libcairo2-dev

je voudrais créer une nouvelle integration qui à partir de coordonées GPS affichue une carte statique sous la forme d'une image HTML.

 
- ajouter un sous menu au Menu" Intégrations" appelé "Maps GPS" avec un emoji. Quand ce menu est appelé : - Soit une chaine de caractère (les coordonées GPS de la carte à créer) est  déja sélectionnée dans l'éditeur Markdown - Soit on demande à l'utilisateur de saisir  les coordonées GPS de la carte à créer Latitude: Longitude:
- On va verfier que ces coordonées existent Sinon message d'erreur

- Le code nécessaire à l'integration sera stocké dans le dossiers bluenotebook/integrations
- Les coordonnées GPS seront dans l'éditeur Markdown sous la forme [46.569317, 0.346048]
- Il faudra récherche la ville la plus proche des ces coordonées GPS
- Carte fabriquée au format PNG sera stockée dans le dossier images du Journal. On demandra a l'utilisateur la taille de la largueur de l'affichage en Pixels
- si les coordonnées GPS sont [46.569317, 0.346048] le code généré par l'intégration sera du type::


<img src="images/YYYYMMJJHHSS_carte+lieu.jpg" width="800">

|   | [46.569317, 0.346048]  |
|---|---|
| Lieu | Poitiers |
| OpenSteetMap | <https://www.openstreetmap.org/#map=16/46.569317/0.346048>|

le code pour fabriquer la carte sera inspiré de 
```python
import staticmaps

context = staticmaps.Context()
context.set_tile_provider(staticmaps.tile_provider_OSM)

place = staticmaps.create_latlng(float("46.569317"), float("0.346048"))
context.add_object(staticmaps.Marker(place, size=5))

# render png via cairo
if staticmaps.cairo_is_supported():
    cairo_image = context.render_cairo(800, 500)
    cairo_image.write_to_png("imagesYYYYMMJJHHSS_carte+lieu.png")
```

beta1


modifier pour un code HTML du type

```html
<figure style="text-align: center;">
    <a href="https://www.openstreetmap.org/#map=16/46.569317/0.346048">
         <img src="images/20251010181131_carte_Poitiers.png" alt="Carte de Poitiers, coordonnées 46.569317, 0.346048" width="800">
    </a>
    <figcaption style="font-weight: bold;">GPS: [46.569317, 0.346048]  Poitiers</figcaption>
</figure>
```
Beta2


## VX.Y Image --> Coord GPS -- Map - Side bt Side Image and Ma

## Integration: Image OpenSteetMap
Je voudrait ajouter un sous menu au Menu" Intégrations" appelé "Maps" avec un emoji.
Quand ce menu est appelé :
- Soit une chaine de caractère (URL de la vidéo YouTube ) est déja sélectionnée dans l'éditeur Markdown
- Soit on demande à l'utilisateur de saisir   l'URL de la vidéo YouTube  

On va ensuite
- 1 Verifier que cette vidéo YouTube existe bien à testant son URL et si la viéo n'existe pas un message   "Attention: La vidéo YouTube demandée n'existe pas !"
- 2 générer un tag du type

## V2.3.5 QSplitter

sur les bordures verticales de la fenetre editeur je voudrais un petit composants un handle au milier qui permette d'ouvre ou fermer un panneau latéral. je ne connais pas le nom de ce type de widget graphique qui existe par exemple dans Libreoffice Calc. nous pouvons ajouter de petits boutons (flèches) directement sur la poignée du `QSplitter`. Un clic sur ces boutons permettra de masquer ou de réafficher le panneau adjacent.

Une poignée entre editeur et Aperçu et une poignée entre Editeur et Plandu Document

beta1



## V2.3.4 Fix image path for preview


## Gestion des l'URL relative pour les images locales

@@Prompt
Pour que les images avec des chemins relatifs comme images/qr-code-svg.jpg s'affichent à la fois dans l'aperçu HTML et dans l'export PDF, il faut indiquer à l'aperçu (QWebEngineView) quel est le dossier de base pour résoudre ces chemins.

La solution consiste à passer l'URL du répertoire de votre journal comme baseUrl lors de la mise à jour du contenu HTML.

Actuellement, votre fichier preview.py utilise baseUrl=QUrl("file:///"). Cela autorise le chargement de fichiers locaux, mais uniquement avec des chemins absolus (ex: /home/user/Journal/images/photo.jpg). Un chemin relatif comme images/photo.jpg est interprété comme /images/photo.jpg, ce qui est incorrect.

Solution
Nous allons modifier la méthode update_content dans bluenotebook/gui/preview.py pour qu'elle accepte le chemin du répertoire du journal et l'utilise comme base pour les chemins relatifs.

nous allons maintenant intégrer la modification dans main_window.py pour qu'il transmette le chemin du répertoire du journal à l'aperçu.

Cela permettra à l'aperçu HTML de résoudre correctement les chemins relatifs des images (comme images/mon-image.jpg) et de les afficher.

Modification du fichier main_window.py
L'objectif est de passer self.journal_directory lors de l'appel à self.preview.update_content(). Cette méthode est appelée à plusieurs endroits, mais principalement via la méthode update_preview(). C'est donc cette dernière que nous allons modifier.


Avec cette modification, chaque fois que l'aperçu HTML est rafraîchi, il reçoit le chemin du répertoire de votre journal. Il peut alors l'utiliser comme base pour résoudre les chemins relatifs des images, comme src="images/qr-code-svg.jpg".

beta1

### Récuperer les images locales dans le dossier images du Journal

@@Prompt
quand je veux inserer une image locale que se soit :
- Avec le Menu Image (<img ...>)
- Avec le menu Image Markdown

Si je sélectionne un chemin local,  par exemple  /home/jm/Images/2025_06_26_img_8128.jpg il faudra
- Copier cette image dans le dossier images du Journal
- Renommer cette image YYYYMMJJHHSS+ancien_nom.extention
par exemple 

si je selection  /home/jm/Images/2025_06_26_img_8128.jpg
l'imege sera copiée comme 202510090805_2025_06_26_img_8128.jpg dans le dossier images du journal
- on génerera le tag HTML ou markdown  en utilisant ce chemin relatif: "images/202510090805_2025_06_26_img_8128.jpg"

- dans le cas du tag HTML 
<img src="images/202510090805_2025_06_26_img_8128.jpg" width="100"> on demandera comme actuellement La largeur en pixels de l'image
- dans le cas d'une image Markdown 
 ![image](images/202510090805_2025_06_26_img_8128.jpg)


beta2

Gérer les images locales de cette manière rendra votre journal beaucoup plus portable et robuste. En copiant les images dans un répertoire local au journal, vous vous assurez de ne jamais perdre les liens, même si vous déplacez le dossier de votre journal.

1. Création d'une méthode centralisée (`_copy_image_to_journal`) dans MarkdownEditor pour gérer la copie et le renommage des images locales.
2. Cette méthode vérifie si un chemin est local, crée le répertoire images dans le journal s'il n'existe pas, génère un nouveau nom de fichier avec un horodatage, copie l'image, et retourne le nouveau chemin relatif.
3. Si le chemin est une URL (commençant par http), il est retourné sans modification.
4. Les méthodes insert_html_image et insert_markdown_image sont mises à jour pour utiliser cette nouvelle logique avant de générer les balises <img> ou Markdown.

## V2.3.3 Fix Issue [#19](https://github.com/lephotographelibre/BlueNotebook/issues/19)

Lors du lancement la première fois de l'application (c'est a dire qu'il n'existe pas encore de note journalière à la date d'Aujourd'hui) a journée un boite de dialogue s'ouvre "Créer un nouveau document".

2 choix sont:

Créer un fichier Vierge (coché par défaut)
Utiliser un modèle

Je voudrais que par defaut soit sélectionné "Utiliser un modèle" avec  le template [Fr]Page_Journal_Standard.md si la locale de l'utilisatuer est "fr_FR"

Pour toutes les autres locales Je voudrais que par defaut soit sélectionné "Utiliser un modèle" avec  le template [en-US]default.md

les templates sont stockées dans le répertoire bluenotebook/resources/templates/

Pour les autres utilisattions (c'est a dire qu'il  existe une note journalière à la date d'Aujourd'hui) il faudra continuer a faire comme fit actuellement:
-Créer un fichier Vierge (coché par défaut) sans sélection de modèle


## V2.3.2 Fix Issue [#7](https://github.com/lephotographelibre/BlueNotebook/issues/7)

Dans le widget calendrier dans le panneau Navigation Journal mettre le chiffre de la journée d'aujourd'hui   dans une police jaune vif si une note journalière existe dans le journal pour aujourd'hui bluenotebook navigation.py

Pour améliorer la visibilité de la note du jour directement dans le calendrier. Pour ce faire, nous allons modifier la méthode highlight_dates dans le fichier bluenotebook/gui/navigation.py afin qu'elle applique un style différent pour la date d'aujourd'hui si une note existe.

Explication des modifications

Récupération de la date du jour : J'ai ajouté today = QDate.currentDate() pour obtenir la date actuelle.
Création d'un format pour "aujourd'hui" : Un nouvel objet QTextCharFormat (today_format) est créé spécifiquement pour la date du jour.
setForeground(QBrush(QColor("#FFFF00"))) applique la couleur jaune vif que vous souhaitiez.
Ajout  d'uune couleur de fond bleue (setBackground QBrush(QColor("#3498db")) pour que le jaune soit bien lisible, quel que soit le thème de votre système.

Logique conditionnelle : Dans la boucle qui parcourt les dates ayant une note, je vérifie si la date correspond à celle d'aujourd'hui.
Si c'est le cas, j'applique le nouveau today_format (jaune sur fond bleu).
Sinon, je conserve l'ancien date_format (bleu).

Avec cette modification, la date du jour sera bien mise en évidence en jaune vif dans le calendrier si une note a été créée pour aujourd'hui, tout en conservant la mise en forme bleue pour les autres jours.

Dès que le fichier de la note du jour est créé ou modifié, la fonction update_calendar_highlights est immédiatement exécutée. Elle va alors scanner le répertoire, voir que la note pour aujourd'hui existe, et demander au panneau de navigation de mettre à jour l'affichage du calendrier, faisant ainsi passer le chiffre du jour en jaune vif, et ce, sans avoir besoin de redémarrer l'application.

## V2.3.1 Integration Video Youtube
Je voudrait ajouter un sous menu au Menu" Intégrations" appelé "Vidéo YouTube" avec un emoji.
Quand ce menu est appelé :
- Soit une chaine de caractère (URL de la vidéo YouTube ) est déja sélectionnée dans l'éditeur Markdown
- Soit on demande à l'utilisateur de saisir   l'URL de la vidéo YouTube  

On va ensuite
- 1 Verifier que cette vidéo YouTube existe bien à testant son URL et si la viéo n'existe pas un message   "Attention: La vidéo YouTube demandée n'existe pas !"
- 2 générer un tag du type
"@@Video
Clickez sur l'image pour lancer la vidéo @@Youtube  <https://www.youtube.com/watch?v=ZD6F_zOpuSg>

[![alt text](https://img.youtube.com/vi/ZD6F_zOpuSg/0.jpg)](https://www.youtube.com/watch?v=ZD6F_zOpuSg)
"

Par exemple:

- L'URL de la vidéo Youtube est : https://www.youtube.com/watch?v=ZD6F_zOpuSg
- Le video ID extrait de l'URL est ZD6F_zOpuSg
- L'adresse de l'image YouTube Thumbnail est https://img.youtube.com/vi/ZD6F_zOpuSg/0.jpg construit à partir du Video ID extrait de l'URL

@@Video @@Youtube <https://www.youtube.com/watch?v=pRESLH7YHBg>

[![alt text](https://img.youtube.com/vi/pRESLH7YHBg/0.jpg)](https://www.youtube.com/watch?v=pRESLH7YHBg)

⬆️**Cliquez sur l'image pour lancer la vidéo**⬆️

beta1



Ajouter une boite à cocher dans le panneau "Intégrations" des Préférences
"Autoriser l'intégration de vidéo Youtube dans l'editeur Markdown"

Dans le cas ou ce choix est décoché alors le sous Menu "Vidéo YouTube" du Menu "Integrations" sera grisé et non activable
 
beta2 

Peux-tu mettre à jour la documentation en ligne pour refléter ce nouveau format d'intégration vidéo ?

## V2.2.1 Qt internationalization i18n (Phase 1)

Certaines boîtes de dialogue standards de l'application (par exemple, le sélecteur de fichiers `QFileDialog` ou les messages de confirmation `QMessageBox`) affichent des boutons en anglais ("Open", "Save", "Cancel", "Yes", "No") alors que le système d'exploitation est configuré en français.
que faire

Le framework Qt est livré avec des fichiers de traduction pour ses composants standard (boutons "Open", "Save", "Cancel", etc.). Votre application doit simplement charger le fichier de traduction correspondant à la langue du système de l'utilisateur.

La procédure consiste à :

1. Créer un objet `QTranslator`.
2. Déterminer la langue du système (`QLocale.system()`).
3. Trouver le chemin où sont stockées les traductions de Qt (`QLibraryInfo`).
4. Charger le bon fichier de traduction (par exemple, `qt_fr.qm` pour le français).
5. Installer ce traducteur dans l'application.

Cette opération doit être effectuée juste après la création de QApplication et avant l'affichage de la fenêtre principale.

Modification de `main.py` :

**Ne pas oublier les imports**: from PyQt5.QtCore import QTranslator, QLocale, QLibraryInfo
beta1

**L'utilsation de cette variable d'envirionnemnt sera réservée au developpement et de debugging**

Forcer la locale par une variable d'envirionnement BLUENOTEBOOK_LOCALE. qui sera passé en parametre du script de lancement de l'application. Par defaut cette variable d'environnement sera "fr_FR". peux tu ecrire un tel script de lancement du programme python main.py et modifier le code pour extraire et forcer cette variable d'environement BLUENOTEBOOK_LOCALE
beta2
 



## V2.1.4 Bug fix Améliorer visibilité du message de sauvegarde + export HTML

Améliorer la visibilité du message de sauvegarde. C'est une excellente idée pour l'ergonomie de l'application. Pour le centrer et le colorer en vert, nous allons créer un QLabel personnalisé qui s'affichera temporairement au milieu de la barre d'état.
beta1

Lorsque l'on demande "Export HTML" aucun nom de fichier n'est porposer dans la boite de dialogue.
Il faudrait proposer BlueNotebook+nomdufichier+datedujour.html
- Nomdufichier --> enminuscules, sans blanc, sans extension
- Datedujour -> sous le format YYYY_MM__DD


beta2

Il faudrait memoriser la destination (répertoire) choisi par l'utilisateur lors de l'export HTML et le reproposer lors d'un appel ulterieur. Persistance dans settings.json

## V2.1.3 2-Thèmes Classic from ghostwriter (light and dark)

From: https://ghostwriter.kde.org/fr/

<img src="/home/jm/Dropbox/BlueNotebookJournal/images/light_mode.jpg" width="400">
<img src="/home/jm/Dropbox/BlueNotebookJournal/images/dark_mode.jpg" width="400">


## V2.1.2 Bug Export PDF: pied de page

l'export PDF permet Pied de page personnalisé ce que je veux c'est 
  - Gauche : Titre du rapport choisi poar l'utilisateur lors du lancement de l'export par l'utilisateur
  or ce que j'obtiens est toujours le meme titre de rapport "BlueNotebook - Journal"

## V2.1.1 Templates Management

@@prompt
BlueNotebook peux tu extraires le texte qui sert de template à la note du jour et le stocker sour le nom bluenotebook/resources/templates/default.md

1- La note du jour est crée avec le template par nommé bluenotebook/resources/templates/default.md

- Extraction du modèle : J'ai extrait le contenu de votre modèle de note journalière.
- Création du fichier : J'ai créé un nouveau fichier default.md dans un nouveau répertoire bluenotebook/resources/templates/. Le nouveau fichier de template est nommé bluenotebook/resources/templates/default.md e tutilise {{date}} comme espace réservé pour la date, qui sera remplacé dynamiquement par le programme.
- Mise à jour du code : Modification de la méthode new_file dans main_window.py pour qu'elle lise ce nouveau fichier, remplace la date, puis l'affiche dans l'éditeur
beta1

Lorsque l'utilisateur Active le Menu Fichier -> Nouveau ... il faut proposer à l'utilisateur de creer un fichier vierge, une sélection de modèles via une liste dérourante qui présente à l'utilisateur la liste des fichiers templates du répertoire bluenotebook/resources/templates/.

Si la template contient {{date}} il faudra faire la substitution et inserer dans le document afficher dans l'éditeur la date du jour. 
Si la template contient {{horodatage}} il faudra faire la substitution et inserer dans le document afficher dans l'éditeur la heure actuelle sous le format HH:MM
beta2

AjouT d'un sous-menu dans Fichier.. "Sauvegarder comme Modèle" entre "Sauvegarder" et "Sauvegarder comme..". Il permet de sauvegarder le document en cours d'édition dans le répertoire bluenotebook/resources/templates/ en demandant à l'utilisatuer de donner un nom de fichier avec md.comme extension.

renommer le menu "Fichiers -> "Sauvegarder" en "Sauvegarder dans Journal"

beta3

Ajouter Nouveau sous menu "Insérer un modèle" à l'empalcement du curseur dans l'éditeur dans le document en cours d'edition. ce sous menu sera le premier de la liste du menu "Edition".
Lorsque l'utilisateur Active le Menu "Edition -> "Insérer un modèle"  il faut proposer à l'utilisateur d'inserer un  modèle dans le document en cours d'édition via une liste dérourante qui présente à l'utilisateur la liste des fichiers templates du répertoire bluenotebook/resources/templates/.

beta4

doc en ligne + mise a jour de la doc technique







## V2.0.2 Export PDF du Journal par plage de dates

Lorsque l'utilisateur lance "Exporter Journal PDF", une nouvelle boîte de dialogue lui permet de sélectionner une plage de dates.

- **Date de début** : Par défaut, la date de la plus ancienne note du journal.
- **Date de fin** : Par défaut, la date du jour.

L'export PDF ne contiendra que les notes comprises dans l'intervalle de dates sélectionné (inclus). Si l'utilisateur valide sans rien changer, toutes les notes du journal sont exportées.
beta1

1. Toujours mémoriser la dernière destination de L'export pdf dans settings.json par exemple: "destination_dir": "/home/jm/Work/BlueNotebook/pdf"

2.Proposer une nom de fichier composé de Journal+datedebbut+datefin.pdf

3. En plus des date l'utilisateur doit pouvoir choisir :
- Un Titre par defaut "BlueNotebook Journal" comme titre du Journal en Page 0
- Un nom d'auteur: "" pas de défaut
beta2

le nom d'auteur s'il est saisi une fois par l'utilisateur doit etre rendu persistant dans setting.json et utilisé comme valeur par defaut dans le editions pdf ultérieur

la taille de la photo affichée peu etre au max 400px x 400 px
beta3

Persistance du titre et du nom de l'auteur

Beta4  -------- TDOD cela ne marche pas -- meme après suppression manuelle


Supprimer infos redondantes settings.json (SettingManager dans core/settings.py)

    "pdf_export": {
        "title": "Mon Journal1",
        "full_journal": false,
        "destination_dir": "/home/jm/Work/BlueNotebook/pdf"
    }

##  V2.0.1 Export PDF - Make PDF Journal

Je voudrais fabrique une document PDF, paginé, à partir de toutes les notes journalière du journal
- Premiere page Titre "Journal BlueNoteBook", u "Date de la dernière note" + logo bluenotebook/resources/images/bluenotebook_256-x256_fond_blanc.png
- Puis pages du journal avec saut de page à chaque nouveau Jour

Creation d'un nouveau sous menu dans Fichier appelé "Exporter Journal PDF" sous "Exporter HTML" qui demande à l'utilisateur de choisr la répertoire de destination du fichier
- Nom du fichier PDF  du type "Journal-1002204-03102025" pour un journal du 10 Fev 2024 au 03 Oct 2025
- une mise en page assez proche des  vues HTML de l'aperçu HTML

1. Nouvelle Action de Menu : Une action Exporter Journal PDF... a été ajoutée au menu "Fichier", juste en dessous de "Exporter HTML...".
2. Logique d'Exportation (export_journal_pdf) :
- 	La méthode récupère et trie chronologiquement tous les fichiers de notes (YYYYMMDD.md).
- 	Elle génère un nom de fichier par défaut intelligent, basé sur la date de la première et de la dernière note (ex: Journal-10022024-03102025.pdf).
- 	Elle construit un grand document HTML en concaténant une page de garde et le contenu de chaque note. Un saut de page (page-break-before: always) est inséré avant chaque nouvelle note pour une pagination correcte.
- 	Pour assurer une mise en page cohérente, le même parser et le même template CSS que l'aperçu HTML sont utilisés.

- Ajouter en bas des pages du fichier pdf une pagination


@@Claude
Si cette solution ne fonctionne pas non plus (car QWebEngine peut avoir des limitations avec JavaScript lors de l'export PDF), vous pourriez envisager d'utiliser une bibliothèque externe comme `ReportLab` ou `WeasyPrint` qui supportent mieux la pagination CSS. Voulez-vous que je vous montre comment intégrer l'une de ces solutions ?

### Solution 1 : WeasyPrint (Recommandée) ✅
J'ai créé une nouvelle méthode export_journal_pdf_weasyprint() qui utilise WeasyPrint. Cette bibliothèque supporte parfaitement la directive CSS @page et offre :
Avantages :

- ✅ Pagination automatique avec counter(page) et counter(pages)
- ✅ Pieds de page personnalisables (gauche, centre, droite)
- ✅ Meilleur contrôle des sauts de page
- ✅ Rendu CSS plus fidèle
- ✅ Gestion native des images locales

Installation :
```bash
pip install weasyprint
```

Fichiers générés
1. `main_window.py `(version complète et propre)

1. ✅ Intégration de WeasyPrint pour l'export PDF avec pagination
2. ✅ Suppression de tout le code obsolète lié à QWebEngine pour le PDF
3. ✅ Code nettoyé et bien organisé
4. ✅ Gestion d'erreur si WeasyPrint n'est pas installé

2. `preview.py (`version épurée)

1. ✅ Suppression de toute la logique de pagination PDF (maintenant inutile)
2. ✅ Code simplifié pour l'aperçu HTML uniquement
3. ✅ Conservation de la gestion des thèmes CSS
beta2

- Du fait de la fabrication asynchrone du pdf, afficher en rouge au milieu de la barre d'état "Veillez Patienter ...." en clignotant @preview.py @main_window.py 
beta3

Memoriser le répertoire de destination d'exportation PDF. Cela évitera à l'utilisateur de naviguer à chaque fois vers le même dossier.

# V2   ----------------------------------------------------------------------------------------------------------------------


## V1.9.3 Editor: Line Numbering

Claude: dans l'editeur markdown peux t on rajouter un numero de ligne devant chaque ligne de l'éditeur
beta1

Peut-on rajouter dans Préférences -> Affichage -> Editeur Markdown une boite à cocher sous les deux boutons du theme: Label de la boite a cocher "Affichage des numéro de lignes ?"
- Si l'utilisateur coche alors on affiche les numeros de lignes dans l'éditeur
- Sinon on n'affiche pas les numeros de lignes dans l'éditeur
Cette préférences est sauvegardée dans settings.json

## V1.9.2 CSS Colors

Je voudrais que lorque un utilisateur séléctionne une feuille de style CSS dans Préférences -> Affichage -> Aperçu HTML il puisse visualiser le formattage HTML correspondant à cette feuille de style par un mini previever HTML qui s'afficherait un document HTML de test qui est composé de la pluspart des tag HTML majeurs. comme cela l'utilisateur pourra juger cette feuille de style. des que l'utilsateur selection un autre feuille de style on vient remettre a jour le mini previewer HTML
beta 1

Suprimmer le bouton  "Sauvegarder comme thème CSS" dans Préférences -> Affichage -> Aperçu HTML
beta 2
d




## V1.9.1 Aperçu HTML CSS

Le répertoire bluenotebook/resources/css_preview est destiner a stocker des feuilles de dtyle CSS pour le previewer HTML

1. Extraire les éléments CSS utilisé actuellement par l'aperçu HTML  pou run faire un fichier CSS nommé default_preview.css et stocké dans le répertoire bluenotebook/resources/css_preview
beta1

2. @github-markdown-dark.css  En respectectant scrictement le meme format que celui de @default_preview.css peut tu convertir github-markdown-dark.css et nommer ce fichier github-markdown-dark_preview.css dans le répertoire bluenotebook/resources/css_preview

3. idem pour github-markdown_preview.css et github-markdown-light_preview.css
beta2

4. si il y des styles CSS présent dans default_preview.css et pas dans les autres fichiers CSS du répertoire bluenotebook/resources/css_preview ajouter ceux-ci dans les trois autres fichiers css En respectectant scrictement le meme format que celui de default_preview.css
bet4

4. Dans Préférences -> Affichage -> Editeur Markdown il y a un bouton "Valeurs Par défaut".Je voudrais que se bouton ne soit plus sur Préférences -> Affichage -> Editeur Markdown mais sur Préférences -> Affichage c'est a dire visble sous les 3 onglets (Editeur Markdown, Aperçu HTML, Export PDF ). Il concerve les memes foctionnalités

Beta5

5. Le label sur ce bouton "Valeurs Par défaut" va devenir "Valeurs d'affichage par défaut"
et modifier le comportement en reinitialisant uniquement les valeurs d'affichage mais plus la visibilité des panneaux et les paramètres d'untégration. La boite de confirmation devra tenir compte de ces modifications.

6. dans Préférences -> Affichage -> Aperçu HTML je voudrais 
- Un bouton "Sauvegarder comme thème CSS" sans action acteuellement
- Un bouton "Sélectionner un thème CSS" qui ouvre une liste déroulante qui me permette de sélectionner une feuille de style présente dans le répertoire répertoire bluenotebook/resources/css_preview.  

Ces deux boutons seront placés exactement comme "Sauvegarder comme thème" et "Sélectionner un thème" dans l'onglet Préférences -> Affichage -> Editeur Markdown

Une fois que l'itilisateur aura sélectionné un nouveau thème CSS et validé son utilisation.
- Stocker le nom du theme choisi dans settings.json
- Reinitialiser le previewer HTML avec cette feuille de style.

A demarrage de l'application on veillera a bien charger le theme stocké dans settings.json.

Lorsque l'utilisateur cliquera sur le bouton "Valeurs d'affichage par défaut" dans l'onglet Préférences -> Affichage lors de la reinitialisation des valeurs d'affichage, il conviendra de charger le theme css default_preview.css qui est dans le repertoire bluenotebook/resources/css_preview
beta7

lorsque l'utilisateur appuie sur le bouton "Sélectionner un thème" de Préférences -> Affichage -> Editeur Markdown s'ouvre une boite de dialoque. Multiplier par 2 la largeur de cette boite de dialoque

Beta8

TODO Mettre a jour doc, aide en ligne
couplet sur la personnalisation de theme d'affichage (Editeur et aperçu HTML)


6.
## V1.8.2 Reglages préférences

Préference Général. Redimentionnement des champs de saisie max 3 lignes de hauteurs les trois champs de saisie sont alignés vers le haut de l'onglet. ce n'est pas grave s'il reste de la place en tre les champs de saisie et le bas de l'onglet
beta1

à l'ouverture, la fenètre Préférences n'est pas assez large et assez haute pour contenir tous les éléments de Préférences -> Affichage. Il faut agrandir cette fenètre

- self.setMinimumWidth(1050) : J'ai augmenté la largeur minimale de 800 à 1050 pixels. Cela représente une augmentation substantielle (proche de ce que vous suggériez avec "x1.5" par rapport à la taille d'origine) qui devrait donner amplement d'espace aux trois colonnes de l'onglet "Affichage" pour s'étendre, rendant les libellés et les widgets de sélection de police et de couleur parfaitement lisibles.
- self.setMinimumHeight(850) : J'ai mis à jour la hauteur minimale de 750 à 850 pixels. Cela ajoute l'espace vertical nécessaire pour que tous les éléments, en particulier dans l'onglet "Affichage", soient bien visibles sans avoir besoin de faire défiler la fenêtre.
beta2


quand l'utilisateur clique sur le bouton Valeurs par defaut --> Il faut :
- recharge les couleurs de valeur par defaut dans le palette de Préférences -> Affichage
- Puis afficher la fenetre de confirmation

Maintenant, la séquence d'événements est la suivante :

1. L'utilisateur clique sur le bouton "Valeurs par défaut".
2. L'interface de l'onglet "Affichage" est immédiatement mise à jour avec les polices et les couleurs par défaut. L'utilisateur peut voir exactement ce qu'il s'apprête à valider.
3. La boîte de dialogue de confirmation s'affiche.
    - Si l'utilisateur clique sur "Valider", les paramètres sont réinitialisés en arrière-plan et l'application se prépare à fermer.
    - S'il clique sur "Annuler", la boîte de dialogue se ferme, mais les couleurs par défaut restent affichées dans la fenêtre des préférences. L'utilisateur peut alors soit "Valider" ces nouveaux réglages, soit "Annuler" pour fermer les préférences sans rien changer.

Beta3

MAJ version V1.8.2

En fait je voudrais restructurer l'onglet Affichage dans **Préferences**
Dans cet onglet Affichage je voudrais 3 nouveaux sous-onglets	
   - Editeur Markdown,
   - Aperçu HTML
   - Export PDF

Le Sous-panneau ouvert par défaut sera  "Editeur Markdown"

Tous les champs actuels de Affichage seront maintenant dans l"onglet "Editeur Markdown" en gardat le meme arrangement
Pour l'instant les onlets 
    - Aperçu HTML
   - Export PDF  - 
   seront vides

Beta4

Lorsque l'on fait Quitter s'affiche une boite de dialogue "Modifications non sauvegardées".
Changer les labels des 3 boutons
- Save --> Sauvegarder
- Discard --> Ne pas sauvegarder
- Cancel --> Annuler

## V1.8.1  Redesign du panneau Préférences-> Affichage + Theme Management

En fait je voudrais restructurer l'onglet Affichage dans **Préferences**
Dans cet onglet Affichage je voudrais 3 nouveaux sous-onglets	
   - Editeur Markdown,
   - Aperçu HTML
   - Plan du document
   - Export PDF

Le Sous-panneau ouvert par défaut sera  "Editeur Markdown"

Tous les champs actuels de Affichage seront maintenant dans le sous panneau Affichage mais affiché sur 3 colonnes:
- 1 colonne pour les polices
- 2 colonnes pour les Couleurs



Pour l'instant il n'y a rien dans les 3 autres sous onglets
   - Aperçu HTML
   - Plan du document
   - Export PDF


Le bouton " Valeurs par defaut" reste attaché au panneau Affichage et doit rester visible quel que soit les sous onglet ouvert. Il continue à Réinitialiser toutes les valeurs d'affichage la visibilité des panneaux et les paramètres d'intégration.
Par défaut aucune Intégration est cochée.
beta1

Préference Général. Redimentionnement des champs de saisie max 3 lignes de hauteurs les trois champs de saisie sont alignés vers le haut de l'onglet. ce n'est pas grave s'il reste de la place en tre les champs de saisie et le bas de l'onglet

Préference Général. Modifier le texte "Tags à exclure du nuage" en "Tags à exclure du nuage de tags"
beta2

mettre à jour le numéro de version de l'application à 1.8.1.

modifications dans les deux fichiers que vous avez mentionnés : main.py pour la logique de l'application et aide_en_ligne.html pour la documentation utilisateur.

beta3

En bas de la première colonne dans Préférence -> Affichage -> Editeur Markdown   creer un bouton nommé  "Sauvedarder comme thème"
Lorsque se bouton sera pressé on viendra sauvegarder les valeurs actuelles dans Préférence -> Affichage -> Editeur Markdown dans un fichier JSON thème répertoire bluenotebook/resources/themes/.
Le format du thème sera identique à celui nommé base_theme.json déja présent.
Une fenètre de dialogue permettra de renseigner les champs 
- "name" label Nom du theme:
- "type" label Type:  boite deroulante avec 2 choix light ou dark
les 2 autres camps seront optionnels
- "author" label Auteur:
- "description" label Description:  
le nom du fichier theme sauvegardé sera la valeur saisie pour le champ name (en minuscule e sans blanc ou caracteres speciaux) + _theme.json 

Si name à pour valeur "Thème Bleu" le nom du fichier sera "themebleu_theme.json" sans accent et sans blanc
les autres champs du fichier thème seront remplis avec les valeurs actuelles affichées dans Préférence -> Affichage -> Editeur Markdown

Confirmer la sauvegarde  du theme


Beta 4

Agrandir en largeur la boite de dialogue SaveThemeDialog (multiply par 1,5)

En bas de la première colonne dans Préférences -> Affichage -> Editeur Markdown creer un bouton nommé "Sélectionner un thème"  
en dessous du bouton "Sauvegarder comme thème"
Dès que cliqué on fera apparaitre une boite de dialogue qui contient une liste déroulante permettant de sélectionner un theme présent dans le répertoire bluenotebook/resources/themes/.
Pour chaque theme la liste déroulante affiche une ligne qui contient les 4 champs
 - "name" label Nom du thème:
- "type" label Type:   
- "author" label Auteur:
- "description" label Description:  
Lorsque l'utilisatuer clique sur une ligne, il selectionne le theme correspondant qui est chargé dans les differents champs d'affichage de Préférences -> Affichage -> Editeur Markdown pour que l'utilisateur voit ce que contenait le theme selectionné.

Au final lorsque l'utilisateur clique sur le bouton "Valider" de Préferences on sauvegardera les différentes valeurs dans settings.json et on configurara l'editeur avec les valeurs du thème selectionné.


Il manque le champ  "type" label Type:   dans la boite de dialogue. et dans cette voite de dialogue il faut remplace OK par Valider et Cancel par Annuler

beta5

Attention pb avec les fontes (affichge incorect)
le theme sélectionné par un utilisateur doit etre mémorisé dans settings.json et a la prochaine ouvertire de la boite de dialogue de selection de theme, il ser aproposé en premier. Lu'utilsateur pourra en choisir un autre en le selectionnat dans la liste déroulante de la boite de dialogue.S


beta6

dans le tab Préférences -> Affichage -> Editeur Markdown je veux replacer les deux boutons
- Sauvegarder comme theme
- Sélectionner un theme

je veux qu'ils soient de la meme taille et prendre toute la largeur de la première colonne de ce tab
je veux que "Sauvegarder comme theme" soit en bas aligné a gache
je veux que "Sélectionner un theme" soit au dessus collé au bouton "Sauvegarder comme theme"

beta7

------------------------------------------
Problème de fonte
dans Préférences -> Affichage -> Editeur Markdown modification de la police  de 12pt a 20pt -> Valider
le changement 20pt est bien ecrit dans settings.json
l'editeur ne change pas de police et reste   en 12py
apres redemarrage settings.json reprend l'ancienne valeur 12pt (lié au theme ?)
l'editeur ne change pas de police et reste   en 12py
-----
beta8 

quand on agrandit la fenetres Préférences les 2 colonnes ne se répartissent pas sur l'espace 1/3,1/3,1/3 la taille des colonnes à l'ai statique ( 1  colonne pour les police, 2 coleonnes pour les couleur) Pas de redimensionnement dynamique
Elargir préférences (multiply*1,25)  pour  Préférences -> Affichage -> Editeur Markdown car l'affichage du nom des polices est illisible

Claude :
Voici la version complète et améliorée du fichier preferences_dialog.py.
Principales améliorations :
✅ Largeur augmentée : 700px au lieu de 500px (+40%)
✅ Hauteur minimale : 600px pour éviter le débordement
✅ Layout en grille : QGridLayout au lieu de QFormLayout pour l'onglet Affichage
✅ 2 colonnes de couleurs : Répartition équilibrée et redimensionnement dynamique
✅ Largeur minimale des boutons de police : 250px pour une meilleure lisibilité
✅ Zone scrollable : Pour gérer tous les paramètres sans débordement
✅ Code simplifié : Méthode _make_color_selector() qui remplace 17 méthodes redondantes
Structure de l'onglet Affichage :

Polices (haut, 1 colonne) :

Police de l'éditeur
Police des extraits de code


Couleurs (2 colonnes équilibrées) :

Colonne gauche : Fond, texte, titres, listes, sélection, code...
Colonne droite : Gras, italique, barré, surlignage, citations, liens...


Bouton Valeurs par défaut (bas, pleine largeur)

Les colonnes s'ajusteront automatiquement quand vous redimensionnez la fenêtre grâce à setColumnStretch().


Beta9
-----------------

Dés que le bouton "Valeurs par défaut" est activé, on charge  les valeurs du theme base_theme.json
beta 6 
dans Préférence -> Affichage -> Editeur Markdown ajouter un bouton Choisr un theme

## V1.7.8 Menu Inserser Images (<img ..>) et Image Markdown

### fonctionnement du sous menu Images (<img ..>).
- si un nom de fichier est selectionné dans l'éditeur , demander la largeur max en pixels à l'utilisateur puis inserer le tag. Proposer la valeur 400 px par defaut.
- Si aucun texte n'est sélectionné dans l'éditeur ouvrir une fenetre de dialogue  dialogue qui permette à l'utilisateur de sélectionner soit un fichier, soit taper une URL puis demander la largeur max en pixels à l'utilisateur puis inserer le tag. Proposer la valeur 400 px par defaut.

les deux scénarios  

-Si un nom de fichier est sélectionné, insère la balise.
-Si rien n'est sélectionné, la boîte de dialogue s'ouvre.

Puis bug sur les panneaux
Beta3

###  fonctionnement du sous menu Inserer Image Markdown
les deux scénarios  

-Si un nom de fichier est sélectionné, insère la balise. OK celui la fonctionne
-Si rien n'est sélectionné, la une fenetre de dialogue s'ouvre  qui permette à l'utilisateur de sélectionner soit un fichier, soit taper une URL puis inserer le tag.


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

# V1   ----------------------------------------------------------------------------------------------------------------------

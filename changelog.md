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
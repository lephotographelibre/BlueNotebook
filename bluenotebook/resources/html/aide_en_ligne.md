## 1. Introduction

Bienvenue dans BlueNotebook ! Ce guide vous explique comment utiliser l'application pour tenir votre journal personnel en Markdown et gérer vos notes et documents associés.

BlueNotebook est un éditeur de texte simple qui vous permet de vous concentrer sur l'écriture. Il utilise la syntaxe Markdown et affiche un aperçu en temps réel de votre document.

Des fonctionnalités avancées de recherche et navigation permettent aux utilisateurs de retrouver rapidement des informations dans les différentes notes journalières avec le support de tags et une indexation automatique.

De nouvelles fonctionnalités de gestion de documents vous permettent de gérér, conjointement aux notes chronologiques du journal, des documents Markdown, PDF, ebooks Epub, cartes et images qui constituront peu à peu votre base de connaissance personnelle intégrée au journal à travers des objets liens, bookmarks et pièces jointes

### Premier démarrage

Lors du tout premier lancement de BlueNotebook (lorsqu'aucun fichier de configuration n'existe), un écran de bienvenue s'affiche automatiquement pour vous guider dans la configuration initiale. Cet écran vous permet de définir les paramètres essentiels avant de commencer à utiliser l'application.

#### Configuration initiale

L'écran de premier démarrage présente une interface claire avec le logo BlueNotebook et vous propose de configurer trois paramètres principaux :

#### 1. Langue de l'application

Choisissez la langue d'interface de l'application :

- **Anglais** (English)
- **Français**


Ce choix détermine la langue de tous les menus, dialogues et messages de l'application. Vous pourrez modifier ce paramètre ultérieurement dans `Fichier > Préférences > Général`.

**Note :** Si vous changez la langue par rapport à celle de votre système, l'application devra être redémarrée pour que le changement soit pris en compte.

#### 2. Répertoire du Journal

Définissez l'emplacement où toutes vos notes, images et pièces jointes seront sauvegardées :

- **Emplacement par défaut :** `~/BlueNotebookJournal` (dans votre répertoire personnel)
- **Personnalisation :** Cliquez sur le bouton **"Choisir..."** pour sélectionner un autre emplacement parent. Le dossier `BlueNotebookJournal` sera automatiquement créé à l'emplacement choisi.


Les sous-dossiers nécessaires (`notes`, `images`, `attachments`, `gpx`) seront créés automatiquement lors de la validation.

**Important :** Si le dossier choisi existe déjà et n'est pas vide, l'application vous demandera confirmation avant de l'utiliser comme journal.

#### 3. Répertoire de Sauvegarde

Choisissez où seront stockées les archives de sauvegarde de votre journal (créées via `Fichier > Sauvegarde Journal...`) :

- **Emplacement par défaut :** `~/BlueNotebookBackup` (dans votre répertoire personnel)
- **Personnalisation :** Cliquez sur le bouton **"Choisir..."** pour sélectionner un autre emplacement parent. Le dossier `BlueNotebookBackup` sera automatiquement créé à l'emplacement choisi.


Ce répertoire sera proposé par défaut lors de vos futures sauvegardes manuelles du journal.

#### Validation et démarrage

Une fois vos choix effectués, cliquez sur le bouton **"Terminé"** en bas à droite de la fenêtre. BlueNotebook va alors :

1. Créer les répertoires nécessaires
2. Sauvegarder vos paramètres dans le fichier de configuration
3. Afficher un message de confirmation
4. Démarrer l'application (ou vous inviter à la redémarrer si vous avez changé de langue)


Vous êtes maintenant prêt à utiliser BlueNotebook ! L'application se lancera et vous pourrez commencer à écrire votre première note.

## 2. L'interface Principale

L'interface est divisée en plusieurs panneaux pour s'adapter à votre façon de travailler :

- **Panneau "Notes" (`F9`) :** Situé à l'extrême gauche, est un gestionnaire de fichiers puissant et intégré, conçu pour organiser tous les documents associés aux notes de votre journal.
- **Panneau de Navigation (`F6`) :** Contient le calendrier, les outils de recherche et le nuage de tags.
- **Panneau "Plan du document" (`F7`) :** Affiche la structure des titres (`#`, `##`, etc.) de votre note actuelle. Cliquez sur un titre pour naviguer instantanément.
- **L'Éditeur :** La zone centrale où vous écrivez votre texte en Markdown. Ce panneau est toujours visible.
- **L'Aperçu HTML (`F5`) :** Affiche le rendu final de votre texte, mis en forme en temps réel.
- **Le Lecteur (`F8`) :** Un panneau dédié à la lecture de documents (EPUB, PDF).


Juste sous la barre de menu principale, une **barre d'outils des panneaux** vous permet d'afficher ou de masquer rapidement ces panneaux à l'aide de boutons interrupteurs. L'état de ces boutons (activé/désactivé) est synchronisé avec les préférences que vous définissez dans `Préférences > Panneaux`. Les raccourcis clavier (`F5`, `F6`, `F7`, `F8`) sont également fonctionnels.

La **barre de statut**, située tout en bas de la fenêtre, est une source d'information précieuse. De gauche à droite, vous y trouverez :

- Le nom du **fichier actuel** (ex: `20250920.md`).
- Un indicateur de modification (`●`) qui apparaît si votre travail n'est pas enregistré.
- Des statistiques sur votre document (lignes, mots, caractères).
- À l'extrémité droite, le chemin vers votre **dossier de journal** et les **statistiques d'indexation**.
 Ce dernier est cliquable : un clic dessus relance manuellement l'indexation des tags, ce qui est utile si vous avez modifié des fichiers en dehors de l'application.


## 3. Le Concept de "Note du Jour"

BlueNotebook est organisé autour d'un concept simple mais puissant : votre journal est un dossier sur votre ordinateur, et chaque journée est un fichier texte.

### La Note du Jour

À chaque lancement, BlueNotebook vérifie votre dossier de journal. Il cherche un fichier correspondant à la date du jour, nommé selon le format `AAAAMMJJ.md` (par exemple, `20250920.md`). Si ce fichier existe, il l'ouvre automatiquement. Sinon, il vous présente une nouvelle page vierge, prête à devenir l'entrée de la journée.

### La Sauvegarde

L'action de sauvegarde (`Fichier > Sauvegarder` ou `Ctrl+S`) le contenu original de la note du jour sera entièrement écrasé et remplacé par ce qui se trouve actuellement dans l'éditeur. Soyez prudent avec cette option !



## 4. Gérer et Utiliser les Modèles (Templates)

Les modèles sont des structures de notes pré-remplies qui vous permettent de démarrer rapidement votre travail. BlueNotebook vous offre une gestion complète des modèles pour créer, utiliser et insérer des structures récurrentes.

### Utiliser un modèle pour une nouvelle note

Lorsque vous créez un nouveau document via `Fichier > Nouveau...` (`Ctrl+N`), une boîte de dialogue s'ouvre et vous propose :

- **Créer un fichier vierge :** Pour commencer avec une page blanche.
- **Utiliser un modèle :** Une liste déroulante vous présente tous les modèles disponibles (fichiers `.md`) dans le dossier `resources/templates/`. En choisissant un modèle, votre nouvelle note sera pré-remplie avec son contenu.


### Créer vos propres modèles

Vous avez une structure de note que vous utilisez souvent ? Transformez-la en modèle !

1. Rédigez ou ouvrez la note que vous souhaitez utiliser comme modèle.
2. Allez dans le menu `Fichier > Sauvegarder comme Modèle...`.
3. Une boîte de dialogue s'ouvrira, vous invitant à donner un nom à votre modèle (par exemple, `rapport_hebdomadaire.md`).
4. Validez. Votre modèle est maintenant sauvegardé et sera disponible dans la liste lors de la création d'une nouvelle note.


### Insérer un modèle dans une note existante

Besoin d'ajouter une section structurée (comme un compte-rendu de réunion) au milieu de votre note du jour ?

- Placez votre curseur à l'endroit où vous souhaitez insérer le contenu.
- Allez dans le menu `Édition > Insérer un modèle...`.
- Choisissez le modèle souhaité dans la boîte de dialogue. Son contenu sera inséré à la position du curseur.


### Placeholders dynamiques

Pour rendre vos modèles encore plus puissants, vous pouvez utiliser des "placeholders" qui seront automatiquement remplacés lors de l'utilisation du modèle :

- `{{date}}` : Sera remplacé par la date complète du jour (ex: "Lundi 28 Octobre 2025").
- `{{horodatage}}` : Sera remplacé par l'heure actuelle (ex: "14:32").


N'hésitez pas à modifier les modèles existants (`default.md`, `reunion.md`, etc.) ou à créer les vôtres pour adapter BlueNotebook à vos besoins !

## 5. Navigation dans le Journal

Le panneau de Navigation (`F6`) vous offre plusieurs outils pour voyager dans le temps à travers vos notes.

- **Le Calendrier :** Les jours pour lesquels une note existe sont mis en évidence. Cliquez sur une date pour ouvrir la note correspondante.
- **Boutons de Navigation :** Juste au-dessus du calendrier, les boutons `Précédent` et `Suivant` vous permettent de sauter à la note existante la plus proche, tandis que `Aujourd'hui` vous ramène à la note du jour.


### 5.1 Raccourcis

BlueNotebook offre des raccourcis clavier pour une navigation rapide dans votre journal :

- **Bouton "📅 Aujourd'hui" (`Ctrl+H`) :** Ce bouton vous ramène instantanément à la note du jour en cours. Très pratique pour revenir rapidement au présent après avoir consulté d'anciennes notes.
- **Bouton "📅 Demain" (`Ctrl+T`) :** Permet de naviguer vers le jour suivant. Utile pour planifier vos notes du lendemain ou parcourir votre journal de manière chronologique.


*Note :* Ces raccourcis sont également accessibles via les boutons correspondants dans le panneau de navigation.

## 6. Gestion des Images et Pièces Jointes

### 6.1 Insérer un Bookmark (Signet)

La fonctionnalité "Bookmark" vous permet de créer des liens enrichis vers des pages web. BlueNotebook va vérifier l'URL, récupérer le titre de la page et générer un lien Markdown formaté.

#### Comment ça marche ?

1. **Lancer l'action :** Allez dans `Insérer > 🔖 Bookmark` ou faites un clic droit dans l'éditeur et choisissez `Liens > 🔖 Bookmark`.
2. **Sélection d'URL :**
  - Si vous avez déjà sélectionné une URL dans l'éditeur, elle sera utilisée automatiquement.
  - Sinon, une boîte de dialogue s'ouvrira pour que vous puissiez saisir l'URL.
3. **Vérification et formatage :** L'application vérifie l'URL en arrière-plan. Si elle est valide, un lien formaté est inséré.   - Si un titre de page est trouvé : `🔖 [Bookmark | Titre de la page - URL](URL)`
  - Si aucun titre n'est trouvé : `🔖 [Bookmark | URL](URL)`


### 6.2 Insertion d'Images (Markdown et HTML)

Pour garantir que votre journal reste complet et portable, BlueNotebook adopte une gestion robuste et intelligente des images que vous insérez, qu'elles proviennent de votre ordinateur ou d'une URL distante.

#### Le Processus Automatique

Que vous utilisiez `Insérer > Image Markdown` ou `Insérer > Image (<img...>)`, l'application effectue systématiquement les actions suivantes en arrière-plan :

1. **Copie systématique dans le journal :** Que l'image soit sélectionnée depuis un fichier local ou une URL distante, elle est désormais toujours copiée dans le répertoire `images/` de votre journal.
2. **Renommage avec horodatage :** Pour éviter les conflits et garder une trace chronologique, l'image copiée est renommée en suivant le format `AAAAMMJJHHMMSS_nom_original.extension`. Par exemple, `photo.jpg` devient `20251026103000_photo.jpg`.
3. **Génération de Markdown cliquable :** Le tag Markdown généré est maintenant une image cliquable. Il prend la forme `[![alt_text](chemin/image.jpg)](chemin/image.jpg)`. Dans l'aperçu HTML, un clic sur l'image l'ouvrira en grand dans votre navigateur.
4. **Affichage optimisé :** Les images insérées en Markdown sont automatiquement redimensionnées pour ne pas dépasser 600px de large ou de haut dans l'aperçu, tout en conservant leurs proportions.


### Les Avantages

- **Portabilité :** Votre journal devient entièrement autonome. Vous pouvez déplacer ou copier le dossier de votre journal sur un autre ordinateur, et toutes vos images continueront de s'afficher, car elles sont incluses.
- **Sécurité :** L'image originale sur votre ordinateur n'est pas modifiée.
- **Pérennité :** Les liens vers des images sur internet ne risquent plus de se "casser" si le site distant disparaît.
- **Organisation :** Toutes les ressources visuelles de votre journal sont centralisées dans un seul et même dossier.


### 6.3 Gestion des Pièces Jointes (Attachements)

En plus des images, BlueNotebook vous permet d'attacher n'importe quel type de fichier à vos notes (PDF, documents, archives, etc.). Cette fonctionnalité est conçue pour centraliser toutes les ressources liées à votre journal en un seul endroit.

#### Comment insérer une pièce jointe ?

1. Placez votre curseur à l'endroit où vous souhaitez insérer le lien vers la pièce jointe.
2. Allez dans le menu `Insérer > 📎 Attachement`.
3. Une boîte de dialogue s'ouvrira, vous permettant de :
  - Coller une **URL** vers un fichier distant (ex: un PDF en ligne).
  - Cliquer sur **"Parcourir..."** pour sélectionner un fichier sur votre ordinateur.


#### Que se passe-t-il en arrière-plan ?

Lorsque vous validez, BlueNotebook effectue plusieurs actions pour garantir la portabilité de votre journal :

- **Création d'un dossier dédié :** Un dossier nommé `attachments` est créé à la racine de votre répertoire de journal (s'il n'existe pas déjà).
- **Copie et renommage :** Le fichier que vous avez sélectionné (qu'il soit local ou distant) est copié dans ce dossier `attachments`. Pour une meilleure organisation, il est automatiquement renommé en suivant le format `AAAAMMJJ_nom_original.extension`, où `AAAAMMJJ` correspond à la date de la note dans laquelle vous insérez la pièce jointe.
- **Insertion d'un lien Markdown :** Un lien formaté est inséré dans votre éditeur, par exemple :  
`📎 [Attachement | 20251026_rapport.pdf](attachments/20251026_rapport.pdf)`


Grâce à ce système, même si vous déplacez votre dossier de journal sur un autre ordinateur, tous les liens vers vos pièces jointes continueront de fonctionner car les fichiers sont stockés localement dans le journal.

### 6.4 Insertion d'images avec données EXIF

Pour enrichir vos notes, notamment pour un journal de voyage, BlueNotebook peut extraire et afficher les données EXIF (Exchangeable image file format) contenues dans vos photos.

#### Comment ça marche ?

1. Utilisez le menu `Insérer > Image Markdown` pour choisir une image locale.
2. Après avoir choisi la taille de l'image, l'application analyse le fichier.
3. Si des données EXIF pertinentes (coordonnées GPS, date, modèle d'appareil photo, etc.) sont trouvées, une boîte de dialogue vous demandera : **"Voulez-vous les insérer sous l'image ?"**
4. Si vous acceptez, une ligne de métadonnées formatée en Markdown sera ajoutée sous l'image, présentant les informations de manière compacte et lisible.


#### Quelles informations sont affichées ?

Si elles sont disponibles dans l'image, vous pourrez voir :

- **Lieu :** La ville ou le village est automatiquement retrouvé à partir des coordonnées GPS.
- **Coordonnées GPS :** Avec un lien direct vers OpenStreetMap.
- **Date et heure** de la prise de vue.
- **Informations techniques :** Modèle de l'appareil, ouverture, vitesse, focale et sensibilité ISO.


Cette fonctionnalité transforme une simple image en une fiche d'information complète, parfaite pour se souvenir des détails de chaque moment capturé.

### 6.5 Gestion intelligente des fichiers locaux

#### Insertion de liens locaux et distants

Le menu `Insérer > Lien` a été amélioré pour vous permettre de créer des liens non seulement vers des sites web, mais aussi vers n'importe quel fichier local de votre ordinateur, tout en garantissant la portabilité de votre journal.

##### Comment créer un lien ?

1. Allez dans le menu `Insérer > Lien`. Une boîte de dialogue s'ouvre.
2. **Pour un lien web :** Remplissez le "Texte du lien" et collez l'URL (`http://...`) dans le champ "URL ou chemin".
3. **Pour un fichier local :**
  - Cliquez sur le bouton **"Parcourir..."**. Un sélecteur de fichiers s'ouvrira, positionné par défaut à la racine de votre journal.
  - Sélectionnez n'importe quel fichier (document, image, note, etc.). Le champ "Texte du lien" sera automatiquement rempli avec le nom du fichier.


##### Gestion de la portabilité

- **Si le fichier est déjà dans votre journal :** Un lien relatif est créé. Votre journal reste portable.
- **Si le fichier est en dehors de votre journal :** Une boîte de dialogue vous demandera si vous souhaitez copier le fichier dans votre journal. Si vous acceptez, vous pourrez choisir un dossier de destination (par défaut `notes/` ou `attachments/`). Le fichier y sera copié, et un lien relatif sera créé. Cela garantit que vous ne perdrez jamais un lien si vous déplacez votre journal.


Le lien généré pour un fichier local aura le format suivant : `🔗 [[[Texte du lien]]](chemin/relatif/vers/le/fichier)`. L'emoji 🔗 vous permet d'identifier visuellement les liens vers des fichiers locaux, et la syntaxe `[[[...]]]` est reconnue par l'éditeur pour la coloration syntaxique, tout en restant un lien parfaitement fonctionnel dans l'aperçu.

Cette fonctionnalité vous permet de lier entre elles vos notes, vos documents de référence et vos images de manière simple et robuste.

#### Comportement intelligent lors de l'ouverture des liens locaux

Lorsque vous cliquez sur un lien local dans l'aperçu HTML, BlueNotebook ouvre intelligemment le fichier selon son type. Une confirmation vous est toujours demandée avant d'ouvrir le fichier pour des raisons de sécurité.

| Type | Extension | Action | Confirmation | Fenêtre |
| --- | --- | --- | --- | --- |
| **Markdown** | `.md`, `.markdown` | Ouvre dans l'éditeur | ✓ | Éditeur principal |
| **PDF** | `.pdf` | Ouvre dans le lecteur PDF/EPUB | ✓ | Panneau lecteur |
| **Image** | `.jpg`, `.png`, `.gif`, `.bmp`, `.svg`, `.webp` | Ouvre dans DocumentViewerWindow | ✓ | Fenêtre séparée |
| **HTML** | `.html`, `.htm` | Ouvre dans DocumentViewerWindow | ✓ | Fenêtre séparée |


Ce comportement garantit une expérience utilisateur optimale tout en maintenant une navigation fluide entre les différents types de documents de votre journal. Que vous travailliez sur des notes Markdown, consultiez des PDF de référence, visualisiez des images ou exploriez des pages HTML, BlueNotebook sélectionne automatiquement la meilleure interface pour chaque type de contenu.

## 7. Le Panneau Lecteur (EPUB et PDF)

BlueNotebook intègre désormais un puissant lecteur de documents, vous permettant de consulter des livres au format **EPUB** et des documents **PDF** directement à côté de vos notes. C'est l'outil idéal pour la recherche, la prise de notes à partir de sources ou simplement pour la lecture.

### Activation et Ouverture

- **Activation :** Cliquez sur le bouton **"Lecteur"** dans la barre d'outils des panneaux ou utilisez le raccourci `F8`.
- **Ouvrir un document :** Allez dans le menu `Fichier > Ouvrir Document...` pour sélectionner un fichier `.epub` ou `.pdf` sur votre ordinateur.
- **Comportement intelligent :** Si vous activez le panneau "Lecteur" sans qu'un document ne soit chargé, l'application vous invitera automatiquement à en choisir un. L'application mémorise également le dernier document ouvert pour le recharger au prochain démarrage.


### Fonctionnalités du Lecteur

Le panneau Lecteur est divisé en deux parties : la table des matières à gauche et la zone de lecture à droite.

- **Navigation multiple :** Naviguez dans le document en cliquant sur un chapitre dans la **table des matières**, en utilisant la **liste déroulante** sous le texte, ou avec les boutons **Précédent/Suivant**.
- **Recherche intégrée :** Utilisez la barre de recherche en haut pour trouver du texte dans tout le document. Les boutons "Suivant" et "Précédent" vous permettent de naviguer entre les occurrences, qui sont mises en surbrillance.
- **Sélection de texte et Copier-coller :** Vous pouvez sélectionner du texte avec la souris dans les documents EPUB et PDF. Un clic droit ouvrira un menu contextuel offrant des options pour copier le texte sélectionné ou tout sélectionner.
- **Gestion des images :** Si vous faites un clic droit sur une image (dans un EPUB ou un PDF), le menu contextuel vous proposera de la sauvegarder (convertie au format JPEG par défaut) ou de la copier dans le presse-papiers. L'application mémorise le dernier dossier de sauvegarde utilisé.
- **Optimisation de l'espace :** Cliquez sur le bouton `<` ou `>` à gauche de la barre de recherche pour masquer ou afficher la table des matières et maximiser votre espace de lecture.
- **Informations contextuelles :** Sous la barre de navigation, le titre du document, son auteur et votre position actuelle (Chapitre X / Y) sont affichés en permanence.
- **Zoom dynamique :** Maintenez la touche `Ctrl` enfoncée et utilisez la **molette de la souris** pour zoomer ou dézoomer sur la page.
- **Sélection de texte avancée et Copier-coller :** Le système de sélection de texte a été amélioré pour être particulièrement précis et intuitif dans les PDF. Le menu contextuel offre des options pour copier le texte sélectionné, tout sélectionner, ou copier le texte de la page entière.


## 8. La Gestion des Notes (Explorateur de Fichiers)

Le panneau "Notes" (`F9`), situé à l'extrême gauche, est bien plus qu'un simple ajout : c'est un véritable explorateur de fichiers intégré à BlueNotebook, conçu pour organiser tous les documents, idées et ressources qui ne sont pas directement liés à une date précise. Il transforme votre journal en un véritable "second cerveau".

#### Fonctionnalités Clés du Panneau "Notes"

- **Exploration de Fichiers :** Affiche une vue arborescente du dossier spécial `notes/` de votre journal. Vous pouvez y créer une hiérarchie de sous-dossiers pour organiser vos projets, recherches, ou collections de documents. Le panneau est maintenant redimensionnable en largeur pour s'adapter à vos besoins.
- **Filtrage Intelligent :** La vue est épurée pour n'afficher que les types de fichiers pertinents :
  - **Texte :** `.md`, `.txt`
  - **Documents :** `.pdf`, `.epub`, `.html` (ouvrable dans l'éditeur)
  - **Médias :** Images (`.jpg`, `.png`), vidéos (`.mp4`) et audio (`.mp3`).
- **Personnalisation Visuelle :**
  - **Coloration des dossiers :** Faites un clic droit sur un dossier et choisissez une couleur parmi 10 pour le marquer visuellement. Ce choix est sauvegardé.
  - **Zoom :** Maintenez `Ctrl` et utilisez la molette de la souris pour agrandir ou réduire la taille du texte dans l'arborescence pour un meilleur confort de lecture.
- **Persistance :** L'application mémorise le dernier dossier que vous avez sélectionné et le ré-ouvre automatiquement au prochain démarrage.


### 8.1 Recherche et Tri

Pour naviguer plus efficacement dans vos notes, le panneau intègre désormais des outils de recherche et de tri.

- **Barre de recherche :** Située en haut du panneau, elle vous permet de filtrer instantanément l'arborescence. La recherche est insensible à la casse et aux accents. Appuyez sur `Entrée` ou sur le bouton "Rechercher" pour lancer le filtre. Un bouton d'effacement vous permet de réinitialiser la vue.
- **Tri par colonne :** Cliquez sur les en-têtes des colonnes ("Nom", "Taille", "Dernière modification") pour trier les fichiers et dossiers. Un second clic sur le même en-tête inverse l'ordre de tri.


### 8.2 Affichage des colonnes de détails

Par défaut, seul le nom des fichiers est affiché. Vous pouvez afficher des informations supplémentaires :

- Utilisez le raccourci clavier `Ctrl+M` pour afficher ou masquer les colonnes "Taille", "Type" et "Dernière modification".


### 8.3 Opérations sur les Fichiers et Dossiers (Menu Contextuel)

Un clic droit dans le panneau "Notes" ouvre un menu contextuel riche qui s'adapte à ce que vous sélectionnez.

**Sur un dossier :**

- **`Nouvelle note...` :** Crée un fichier `.md`, vous demande un nom, et l'ouvre dans l'éditeur.
- **`Créer un sous-dossier...` :** Crée un nouveau répertoire à l'intérieur du dossier sélectionné.
- **`Importer un fichier...` :** Copie un fichier depuis votre ordinateur ou télécharge depuis une URL dans le dossier sélectionné.
- **`Déplier tout` / `Réplier tout` :** Déploie ou réduit récursivement toute l'arborescence d'un dossier.
- **`Couper` / `Copier` / `Coller` :** Gérez vos fichiers avec les opérations de presse-papiers classiques.
- **`Renommer...` / `Supprimer...` :** La suppression affiche une confirmation intelligente, vous prévenant si le dossier n'est pas vide et combien d'éléments il contient.


**Sur un fichier :**

- **`Ouvrir` :** Ouvre le fichier dans le panneau approprié (Éditeur, Lecteur) ou avec l'application par défaut de votre système pour les médias.
- Les fichiers `.html` sont maintenant ouverts directement dans l'éditeur Markdown.
- Ainsi que les options `Couper`, `Copier`, `Renommer`, `Supprimer`.


**Dans une zone vide :**

- **`Créer un dossier...` :** Crée un nouveau dossier à la racine du répertoire `notes/`.
- **`Coller` :** Colle un fichier ou dossier précédemment copié/coupé.


## 9. Intégrations (Météo, YouTube, etc.)

BlueNotebook peut interagir avec des services externes pour enrichir vos notes. Ces fonctionnalités se trouvent dans le menu `Intégrations`.

### 9.1 Insérer la Météo du Jour

Ajoutez les conditions météorologiques actuelles à vos notes journalières, ce qui est parfait pour un journal de bord ou pour contextualiser vos écrits.

1. **Configuration initiale :** Avant de pouvoir utiliser cette fonctionnalité, vous devez la configurer.   - Rendez-vous dans `Préférences > Intégrations`.
  - Dans la section "Météo Weatherapi.com", renseignez votre **Ville** et votre **Clé API**. Vous pouvez obtenir une clé API gratuite sur le site [weatherapi.com](https://www.weatherapi.com).
  - Validez les préférences. Ces informations sont sauvegardées localement et en toute sécurité.
2. **Insertion :**
  - Placez votre curseur à l'endroit souhaité dans l'éditeur.
  - Allez dans le menu `Intégrations > Météo Weatherapi.com`.
  - Une ligne de texte au format Markdown, contenant un emoji météo et les informations (température, conditions, vent, humidité), sera insérée dans votre note.


### 9.2 Intégrer une Trace GPX

Pour les amateurs de randonnée, de vélo ou de voyage, BlueNotebook permet d'intégrer une carte de votre parcours directement depuis un fichier de trace GPX.

1. Allez dans le menu `Intégrations > Trace GPX`.
2. Une boîte de dialogue s'ouvre, vous permettant de :
  - Coller une **URL** vers un fichier GPX en ligne.
  - Cliquer sur **"Parcourir..."** pour sélectionner un fichier GPX sur votre ordinateur.
3. Choisissez ensuite la **largeur** de l'image de la carte en pixels.
4. L'application va alors automatiquement :
  - Analyser le fichier GPX pour en extraire le tracé, la date et l'heure de début/fin.
  - Sauvegarder une copie du fichier GPX dans le dossier `gpx/` de votre journal.
  - Générer une image de carte statique (`.png`) avec le tracé et un marqueur de départ, puis la sauvegarder dans le dossier `images/`.
  - Insérer un bloc de texte au format Markdown dans votre note.


Le résultat est une image de votre parcours, cliquable pour ouvrir la carte sur OpenStreetMap avec un marqueur sur le point de départ. La légende est riche et interactive : elle contient le nom du lieu (cliquable), la date et l'heure de départ, ainsi que la durée totale du parcours.

### 9.3 Intégrer une Carte Statique (GPS)

Vous pouvez générer et insérer une carte statique directement dans vos notes à partir de coordonnées GPS. Cette fonctionnalité est idéale pour documenter des lieux de voyage, des randonnées ou des points d'intérêt.

1. Allez dans le menu `Intégrations > Carte GPS`.
2. Une boîte de dialogue vous demandera de saisir la **Latitude** et la **Longitude**. Vous pouvez aussi sélectionner du texte au format `[46.514, 0.338]` dans l'éditeur avant de lancer l'action pour pré-remplir les champs.
3. Choisissez ensuite la **largeur** de l'image de la carte en pixels.
4. L'application va alors :
  - Contacter un service de géolocalisation pour trouver le nom du lieu le plus proche (ex: "Ligugé").
  - Générer une image de carte statique (un fichier `.png`) et la sauvegarder dans le dossier `images/` de votre journal.
  - Insérer un bloc de texte au format Markdown dans votre note.


Le résultat est une image cliquable qui renvoie vers OpenStreetMap (avec un marqueur sur le lieu), accompagnée d'une légende claire indiquant les coordonnées et le nom du lieu, également cliquable.

    [![Carte de Poitiers...](images/20251026_carte_Poitiers.png)](https://www.openstreetmap.org/...)

    **GPS :** [46.58, 0.34] - [Poitiers](https://www.openstreetmap.org/...)

### 9.4 Intégrer une Vidéo YouTube

Vous pouvez facilement intégrer une vidéo ou une playlist YouTube dans vos notes, avec une miniature cliquable qui renvoie vers le site de YouTube.

1. Allez dans le menu `Intégrations > Vidéo YouTube`.
2. Si vous avez déjà sélectionné une URL YouTube (vidéo ou playlist) dans l'éditeur, elle sera utilisée automatiquement.
3. Sinon, une boîte de dialogue s'ouvrira avec le message "Entrez l'URL de la vidéo ou playlist Youtube:". Collez-y votre lien.
4. L'application détecte automatiquement s'il s'agit d'une vidéo ou d'une playlist et insère un bloc de texte au format Markdown avec :
  - Pour une **vidéo** : le titre et la miniature.
  - Pour une **playlist** : le titre, l'auteur, le nombre de pistes et la miniature.


**Astuce :** Vous pouvez activer ou désactiver cette fonctionnalité dans `Préférences > Intégrations`.

#### 9.4.1 Récupération de la Transcription

Pour enrichir davantage vos notes, BlueNotebook peut automatiquement récupérer la transcription textuelle d'une vidéo YouTube, si elle est disponible.

1. **Processus automatique :** Lorsque vous intégrez une vidéo, l'application vérifie en arrière-plan si une transcription existe (en français ou en anglais). Cette recherche ne bloque pas l'interface, et un message `Récupération de la transcription en cours...` s'affiche dans la barre de statut.
2. **Proposition à l'utilisateur :** Si une transcription est trouvée, une boîte de dialogue apparaît : `"Pour cette vidéo Youtube une transcription en {langue} existe, Voulez vous l'ajouter ?"`.
3. **Insertion formatée :** Si vous acceptez, le texte de la transcription, intelligemment formaté en paragraphes, est ajouté sous le bloc de la vidéo, précédé du titre `**Transcript de la video Youtube**`.


Cette fonctionnalité est extrêmement utile pour la prise de notes, la recherche de mots-clés dans une vidéo ou pour conserver une trace écrite d'un contenu oral.

**Configuration :** Vous pouvez contrôler cette fonctionnalité dans `Préférences > Intégrations` via la case à cocher `"Autoriser l'affichage des transcripts de vidéo Youtube dans l'éditeur Markdown"`. Notez que cette option n'est active que si l'intégration YouTube principale est elle-même autorisée.

### 9.7 Insérer les Données Astronomiques du Jour

Ajoutez les heures de lever/coucher du soleil et la phase de la lune pour la ville de votre choix, idéal pour un journal de bord ou pour noter les conditions du jour.

1. **Configuration initiale :** Avant de pouvoir utiliser cette fonctionnalité, vous devez la configurer.   - Rendez-vous dans `Préférences > Intégrations`.
  - Dans la section "Astro Soleil et Lune", saisissez le nom de votre **Ville** et cliquez sur **"Rechercher"**. L'application trouvera automatiquement la latitude et la longitude.
  - Validez les préférences. Ces informations sont sauvegardées localement.
2. **Insertion :**
  - Placez votre curseur à l'endroit souhaité dans l'éditeur.
  - Allez dans le menu `Intégrations > Astro du jour`.
  - Un bloc de texte au format Markdown contenant les informations (lever/coucher du soleil, phase de la lune) pour votre ville sera inséré dans votre note.


### 9.8 Convertir un PDF en Markdown

Cette intégration puissante vous permet de transformer le contenu textuel d'un fichier PDF (local ou distant) en un document Markdown propre et éditable. C'est l'outil parfait pour extraire le contenu d'articles, de rapports ou de documents que vous souhaitez archiver et rendre consultables dans votre journal.

1. Allez dans le menu `Intégrations > Conversion PDF-Markdown` ou faites un clic-droit sur un dossier dans le panneau "Notes".
2. Une boîte de dialogue s'ouvre, vous invitant à fournir le chemin vers un fichier PDF local (via le bouton "Parcourir...") ou à coller l'URL d'un PDF en ligne.
3. Après validation, l'application télécharge et analyse le PDF en arrière-plan.
4. Une fois la conversion terminée, le contenu Markdown est soit chargé dans l'éditeur, soit sauvegardé comme un nouveau fichier dans le dossier que vous avez choisi, prêt à être modifié et annoté.


**Note :** Cette fonctionnalité s'appuie sur la bibliothèque `pymupdf4llm`. La qualité de la conversion dépend de la structure du PDF source (les PDF basés sur du texte fonctionnent mieux que ceux basés sur des images).

### 9.9 Convertir une URL/HTML en Markdown

Transformez n'importe quelle page web ou fichier HTML local en une note Markdown propre et lisible. Cette fonctionnalité est idéale pour archiver des articles de blog, des documentations techniques ou toute autre page web que vous souhaitez conserver et annoter.

1. Allez dans le menu `Intégrations > Conversion URL(HTML)-Markdown`.
2. Une boîte de dialogue s'ouvre. Si vous aviez sélectionné une URL dans l'éditeur, elle sera déjà pré-remplie. Vous pouvez aussi coller une URL ou parcourir votre disque pour choisir un fichier `.html`.
3. Vous pouvez affiner la conversion avec plusieurs options :
  - **Ajouter le titre en # :** Ajoute automatiquement le titre de la page comme un titre de niveau 1 en haut du document.
  - **Conserver les liens Markdown :** Garde tous les hyperliens de la page originale.
  - **Utiliser Readability pour nettoyer :** C'est l'option la plus puissante. Elle utilise un algorithme pour extraire uniquement le contenu principal de l'article, en supprimant les publicités, les menus et autres éléments superflus.
4. Après validation, une fenêtre vous demande où sauvegarder le nouveau fichier `.md` (par défaut dans le dossier `notes/` de votre journal).
5. Le fichier est créé et immédiatement ouvert dans l'éditeur, prêt à être utilisé.


### 9.6 Insérer la Citation du Jour

Commencez votre journée avec une pensée inspirante. BlueNotebook peut récupérer une citation célèbre et l'insérer dans votre note.

- **Au démarrage :** Si l'option est activée dans `Préférences > Intégrations`, une fenêtre affichant la citation du jour apparaîtra au lancement de l'application.
- **Manuellement :** À tout moment, vous pouvez aller dans le menu `Intégrations > Citation du jour` pour insérer la citation actuelle (formatée comme une citation Markdown) à l'endroit où se trouve votre curseur.


## 10. Recherche et Navigation Avancée par Tags

Le panneau de Navigation intègre de puissants outils pour retrouver vos informations : le nuage de tags et un champ de recherche.

### Le Nuage de Tags

Sous le calendrier, vous trouverez le "nuage de tags" :

- **Nuage de Tags :** Affiche les tags (`@@mot`) que vous utilisez le plus souvent. Plus un tag est fréquent, plus il apparaît en grand.


**Interaction :** Cliquez sur un tag dans le nuage pour l'insérer automatiquement dans le champ de recherche et **lancer immédiatement la recherche**.

**Attention:** Les tags n’apparaissent pas tous dans le nuage, uniquement les plus fréquents. Néanmoins vous pouvez lancer une recherche sur n'importe quel tag par une saisie directe dans le champ Recherche.

### Le Champ de Recherche

Situé sous le calendrier, ce champ vous permet de lancer une recherche précise. Il est conçu pour être rapide et efficace.

- **Rechercher un tag :** Vous devez préfixer votre recherche avec `@@` (ex: `@@projet`).
- **Liste des tags :** Cliquez sur le bouton `▼` à droite du champ pour afficher la liste de tous vos tags. Cliquer sur un tag dans cette liste le sélectionne et **lance automatiquement la recherche**.
- **Effacer la recherche :** Cliquez sur l'icône qui apparaît à droite dans le champ pour effacer son contenu et revenir à l'affichage des nuages.


### Le Panneau de Résultats de Recherche

Le panneau de résultats de recherche est toujours visible dans le panneau de navigation, juste en dessous du nuage de tags, et occupe tout l'espace restant. Chaque ligne correspond à une occurrence trouvée et contient deux colonnes : "Date" et "Texte". Le contexte affiché correspond à **toute la fin de la ligne** où le tag a été trouvé, vous donnant un aperçu beaucoup plus complet. Les résultats sont triés par défaut du plus récent au plus ancien (vous pouvez inverser le tri en cliquant sur l'en-tête "Date").

**Comportement par défaut et recherche :**

- **Par défaut**, si aucune recherche n'a été effectuée, ce panneau affiche la liste des tâches `@@TODO` avec le titre "✔ Liste des Tâches @@TODO".
- Dès qu'une **recherche est lancée**, le titre devient "🔍 Résultats de la Recherche" et le panneau affiche les résultats correspondants.
- Si vous recherchez à nouveau le tag `@@TODO`, le titre rebascule sur "✔ Liste des Tâches @@TODO".


**Interaction :** Cliquez sur une ligne de résultat pour ouvrir la note correspondante **directement à la bonne ligne** dans l'éditeur !

**Rafraîchissement de l'index :** Pour plus de commodité, vous pouvez relancer manuellement l'indexation des tags en cliquant directement sur :

- Le titre principal du panneau : **"Navigation Journal"**.
- Le titre du panneau de résultats : **"✔ Liste des Tâches @@TODO"** ou **"🔍 Résultats de la Recherche"**.


## 11. Exploration des Menus

Voici un guide visuel de toutes les fonctionnalités accessibles depuis la barre de menus.

    Fichier
    ├── Nouveau... (Ctrl+N) : Crée un nouveau fichier, en proposant un document vierge ou un modèle.
    ├── Ouvrir... (Ctrl+O) : Ouvre un fichier (Markdown, EPUB, PDF) et l'affiche dans le panneau approprié (éditeur ou lecteur).
    ├── ---
    ├── Sauvegarder dans Journal (Ctrl+S) : Sauvegarde la note dans le répertoire du journal.
    ├── Sauvegarder comme Modèle... : Sauvegarde le document actuel comme un nouveau modèle réutilisable.
    ├── Sauvegarder sous... (Ctrl+Shift+S) : Enregistre la note actuelle dans un nouveau fichier de votre choix.
    ├── ---
    ├── Ouvrir Journal : Permet de sélectionner un nouveau dossier qui servira de journal.
    ├── Sauvegarde Journal... : Crée une archive ZIP complète de votre journal actuel.
    ├── Restauration Journal... : Restaure un journal depuis une archive ZIP.
    ├── ---
    ├── Exporter HTML... : Exporte la note en fichier HTML.
    ├── Exporter en PDF... : Exporte la note actuelle en fichier PDF.
    ├── Exporter Journal PDF... : Crée un document PDF de votre journal, avec sélection de dates, titre et auteur.
    ├── Exporter Journal EPUB... : Crée un livre numérique au format EPUB de votre journal.
    ├── ---
    ├── Préférences... : Ouvre la fenêtre de personnalisation de l'application.
    ├── ---
    └── Quitter (Ctrl+Q) : Ferme BlueNotebook.

    Édition
    ├── Insérer un modèle... : Insère le contenu d'un modèle à la position du curseur.
    ├── ---
    ├── Annuler (Ctrl+Z) : Annule la dernière action.
    ├── Rétablir (Ctrl+Y) : Rétablit la dernière action annulée.
    ├── ---
    └── Rechercher (Ctrl+F) : Recherche du texte dans l'éditeur.

    Formater
    ├── Titres
    │   ├── Niv 1 (#)
    │   ├── Niv 2 (##)
    │   ├── Niv 3 (###)
    │   ├── Niv 4 (####)
    │   └── Niv 5 (#####)
    ├── Style de texte
    │   ├── Gras (**texte**)
    │   ├── Italique (*texte*)
    │   ├── Barré (~~texte~~)
    │   └── Surligné (==texte==)
    ├── Code
    │   ├── Monospace (inline)
    │   └── Bloc de code
    ├── Listes
    │   ├── Liste non ordonnée
    │   ├── Liste ordonnée
    │   └── Liste de tâches
    ├── ---
    └── RaZ (Effacer le formatage) : Supprime tout le formatage Markdown de la sélection.

    Insérer
    ├── Image (Ctrl+Shift+I) : Insère une image avec la syntaxe Markdown `!`. Copie les images locales dans le journal.
    ├── 🔗 Lien : Ouvre une boîte de dialogue pour créer un lien `texte`. Gère les liens distants et les fichiers locaux (avec copie dans le journal si nécessaire).
    ├── Lien URL/Email : Encadre une URL ou un email sélectionné avec des chevrons `< >` pour le rendre cliquable.
    ├── 📎 Attachement : Insère un lien vers un fichier attaché (local ou distant), copié dans le répertoire `attachments` du journal.
    ├── 🔖 Bookmark : Crée un lien enrichi vers une page web, avec récupération automatique du titre.
    ├── ---
    ├── Ligne Horizontale : Insère une ligne de séparation `---`.
    ├── Commentaire HTML
    ├── Tableau
    ├── Citation
    ├── ---
    ├── Tag (@@) : Insère un tag `@@` ou transforme la sélection en tag.
    ├── Heure : Insère l'heure actuelle (HH:MM).
    ├── ---
    └── Emoji : Ouvre un sous-menu pour insérer des emojis.

    Intégrations
    ├── Météo Weatherapi.com : Insère les conditions météorologiques actuelles (température, conditions, vent, humidité).
    ├── Trace GPX : Génère une carte interactive à partir d'un fichier de trace GPX.
    ├── Carte GPS : Génère et insère une carte statique à partir de coordonnées GPS.
    ├── Vidéo YouTube : Insère une vidéo ou une playlist YouTube avec sa miniature à partir d'une URL.
    ├── Livre Amazon ISBN : Insère les informations d'un livre (titre, auteur, éditeur, résumé) à partir d'un ISBN.
    ├── Citation du jour : Insère la citation du jour (récupérée depuis Internet) dans votre note.
    ├── Données Astronomiques : Insère les informations astronomiques du jour (lever/coucher soleil/lune, phase lunaire).
    ├── Convertir PDF en Markdown : Convertit un fichier PDF en texte Markdown.
    └── Convertir URL/HTML en Markdown : Convertit une page web en texte Markdown.

    Aide
    ├── Documentation en ligne : Ouvre ce manuel.
    └── À propos : Affiche les informations sur l'application, sa version et sa licence.
  

## 12. Exportation

### 12.1 Exporter en HTML (fichier individuel)

Cette fonction vous permet d'exporter le contenu de la note Markdown actuellement ouverte en un fichier HTML statique. C'est idéal pour partager rapidement une note ou la consulter dans un navigateur web.

- **Accès :** Via le menu `Fichier > Exporter HTML...`.
- **Nom de fichier :** Un nom de fichier par défaut est suggéré, basé sur le nom de votre note et la date du jour.
- **Mémorisation :** L'application se souvient du dernier répertoire d'exportation utilisé pour faciliter les exports futurs.
- **Apparence :** Le fichier HTML généré utilise le même thème visuel que votre aperçu dans l'application.


### 12.2 Exporter en PDF (fichier individuel)

Exportez la note Markdown actuellement ouverte en un document PDF. Cette option est utile pour archiver une note spécifique ou la partager dans un format universel.

- **Accès :** Via le menu `Fichier > Exporter en PDF...`.
- **Technologie :** L'exportation est réalisée à l'aide de la bibliothèque `WeasyPrint`, garantissant un rendu fidèle du contenu.
- **Gestion des images :** Les chemins des images (y compris celles situées dans le dossier `Journal/images/` ou ses sous-répertoires) sont correctement résolus, assurant leur affichage dans le PDF.
- **Nom de fichier :** Un nom de fichier par défaut est suggéré, basé sur le nom de votre note.
- **Mémorisation :** L'application se souvient du dernier répertoire d'exportation utilisé.


### 12.3 Exporter le Journal en PDF

BlueNotebook vous permet de créer un document PDF professionnel et paginé de votre journal, idéal pour l'archivage, l'impression ou le partage. Cette fonctionnalité est accessible via `Fichier > Exporter Journal PDF...`.

Lorsque vous lancez cette action, une boîte de dialogue apparaît, vous donnant un contrôle total sur le contenu de l'export :

- **Plage de dates :** Vous pouvez choisir une date de début et une date de fin pour n'exporter qu'une période spécifique de votre journal. Par défaut, l'application propose d'exporter l'intégralité de vos notes.
- **Titre du document :** Personnalisez le titre qui apparaîtra sur la page de garde de votre PDF. Par défaut, "BlueNotebook Journal" est utilisé.
- **Nom de l'auteur :** Vous pouvez ajouter votre nom sur la page de garde.
- **Photo de couverture :** Ajoutez une touche personnelle en sélectionnant une image (PNG, JPG) qui s'affichera sur la page de garde (taille max 400x400px).
- **Filtrage par tag :** Une liste déroulante vous permet de sélectionner un tag parmi ceux qui ont été indexés dans votre journal. Si vous choisissez un tag, seules les notes contenant ce tag (et comprises dans la plage de dates) seront incluses dans l'export. Laissez sur "(Aucun tag)" pour exporter toutes les notes de la période.


**Mémorisation intelligente :** Pour vous faire gagner du temps, BlueNotebook mémorise le dernier dossier de destination utilisé, ainsi que le titre et le nom d'auteur que vous avez saisis pour les exports futurs.

#### Structure du PDF généré :

1. **Page de garde :** Affiche le titre, le nom de l'auteur, votre photo (si choisie)ou le logo de BlueNotebook et la plage de dates concernée. Si un tag a été sélectionné pour le filtre, il sera également mentionné sur cette page.
2. **Notes du journal :** Chaque note journalière est ajoutée sur une nouvelle page, en respectant le formatage de l'aperçu HTML.
3. **Pagination :** Toutes les pages sont numérotées en bas de page pour une lecture facile.


Une fois les options choisies, l'application génère le fichier PDF en arrière-plan. Une notification clignotante "Veuillez patienter..." apparaît dans la barre de statut pendant le processus.

### 12.4 Exportation du Journal en EPUB

En plus du PDF, BlueNotebook vous permet de transformer votre journal en un véritable livre numérique au format EPUB, compatible avec toutes les liseuses (Kobo, Kindle, etc.) et applications de lecture. Cette fonctionnalité est accessible via `Fichier > Exporter Journal EPUB...`.

L'export EPUB est conçu pour offrir une expérience de lecture optimale et inclut de nombreuses fonctionnalités avancées :

- **Configuration similaire au PDF :** Vous pouvez choisir la plage de dates, le titre du livre, le nom de l'auteur et une image de base pour la couverture.
- **Couverture personnalisée :** L'application génère une couverture de livre professionnelle en combinant l'image que vous avez choisie avec le titre, l'auteur et la plage de dates sur un fond élégant.
- **Table des matières :** Un sommaire cliquable est automatiquement créé, avec une entrée pour chaque note journalière, vous permettant de naviguer facilement dans votre livre.
- **Intégration des images :** Toutes les images de vos notes (locales ou web) sont automatiquement téléchargées, redimensionnées, compressées et intégrées dans le fichier EPUB. Votre livre est ainsi 100% autonome.
- **Index des tags :** Pour une navigation thématique, un index de tous vos tags (`@@tag`) est généré à la fin du livre. Chaque tag est suivi d'une liste de liens cliquables qui vous amènent directement à chaque occurrence du tag dans le journal.


Le résultat est un fichier `.epub` de haute qualité, prêt à être transféré sur votre liseuse pour une relecture confortable de vos souvenirs.

**Note :** Pour utiliser cette fonctionnalité, les bibliothèques Python `EbookLib`, `Pillow`, `BeautifulSoup4`, `requests` et `cairosvg` doivent être installées.

## 13. Sauvegarde et Restauration du Journal

BlueNotebook V4.2.5+ dispose d'un système complet de sauvegarde et restauration de votre journal, avec des fonctionnalités avancées de fusion intelligente et de sécurité.

### Sauvegarde du journal

#### Comment créer une sauvegarde

1. **Ouvrir le menu :** `Fichier > Sauvegarde Journal...`
2. **Choisir l'emplacement :** Par défaut, BlueNotebook propose le dernier répertoire utilisé. Le nom de fichier est automatiquement généré : `BlueNotebook-Backup-2026-01-24-15-30.zip`. Vous pouvez modifier le nom et l'emplacement selon vos besoins.
3. **Lancer la sauvegarde :** Cliquez sur **Sauvegarder**. Un message clignotant apparaît dans la barre de statut : *"Sauvegarde en cours..."*. L'interface reste responsive pendant la sauvegarde. Un message de confirmation s'affiche à la fin avec le chemin complet.


#### Contenu de l'archive

L'archive ZIP contient :

- Tous vos fichiers `.md` (notes quotidiennes)
- Le dossier `notes/` (notes supplémentaires)
- Le dossier `images/` (images insérées)
- Le dossier `attachments/` (pièces jointes)
- Le dossier `gpx/` (traces GPS)
- Les fichiers d'index (tags, etc.)


**Exclusions automatiques :** Répertoires `__pycache__` (cache Python)

### Restauration du journal

#### Comment restaurer un journal

1. **Ouvrir le menu :** `Fichier > Restauration Journal...`

2. **Sélectionner l'archive :** Choisissez le fichier `.zip` à restaurer. Par défaut, le dialogue s'ouvre dans le dernier répertoire de sauvegarde utilisé.

3. **Choisir la stratégie de restauration :** Un dialogue s'affiche avec deux options :
  - **Option 1 : Fusion intelligente (recommandé)**         **Comportement :**

    - Les **nouveaux fichiers** de l'archive sont **ajoutés** au journal actuel
    - Les **fichiers existants** sont **préservés**
    - En cas de **conflit** (même nom de fichier) : votre fichier actuel est **conservé**, le fichier de l'archive est **renommé** avec l'extension `.restored`

        **Avantages :** Aucune perte de données, vous pouvez comparer les versions en conflit, fusion manuelle possible.

  - **Option 2 : Remplacement complet**         **Comportement :** Le contenu **actuel** du journal est **complètement supprimé** et le contenu de l'**archive** le **remplace intégralement**.

        **Attention :** Toutes vos données actuelles seront supprimées (une sauvegarde de sécurité sera créée automatiquement).

        **Utilisez cette option :** Pour restaurer un backup complet, pour migrer vers un nouveau journal, quand vous êtes sûr de vouloir remplacer tout le contenu.

4. **Suivre la progression :** Un dialogue de progression s'affiche avec 5 phases :
  1. Validation de l'archive (0-10%) : Vérification de l'intégrité du ZIP
  2. Sauvegarde du journal actuel (10-30%) : Création du backup de sécurité
  3. Extraction de l'archive (30-70%) : Décompression des fichiers
  4. Fusion intelligente (70-95%) : Merge ou remplacement
  5. Finalisation (95-100%) : Nettoyage et vérification

    Un label clignotant dans la barre de statut : *"Restauration en cours..."*. L'interface reste responsive.

5. **Résultat :** À la fin de la restauration, un message de résumé s'affiche indiquant le nombre de fichiers ajoutés, de conflits résolus et de fichiers préservés, ainsi que le chemin vers la sauvegarde de sécurité.

6. **Redémarrage nécessaire :** L'application se ferme automatiquement après la restauration. **Relancez BlueNotebook** pour utiliser le journal restauré.

### Sauvegarde de sécurité automatique

Avant **toute** restauration (fusion ou remplacement), BlueNotebook crée automatiquement une copie de sécurité de votre journal actuel.

**Format du nom :** `{journal_directory}.bak-YYYYMMDD-HHMMSS`

**Exemple :** `/home/user/BlueNotebookJournal.bak-20260124-153045`

**Où se trouve la sauvegarde ?** Même répertoire parent que votre journal actuel, nom basé sur le nom du journal + timestamp.

**Pourquoi c'est important ?** En cas d'erreur ou si vous restaurez la mauvaise archive, votre journal actuel est intact dans le backup. Pour récupérer, copiez simplement le contenu du `.bak-*` vers votre journal.

**Note :** Ces backups ne sont **pas supprimés automatiquement**. Pensez à les nettoyer manuellement de temps en temps.

### Validation de l'archive

Avant toute restauration, BlueNotebook valide l'archive ZIP :

- **Intégrité du ZIP :** Test de corruption du fichier, vérification de tous les fichiers de l'archive
- **Structure du journal :** Présence de fichiers `.md` (notes), détection de répertoires standards
- **Sécurité :** Pas de chemins dangereux (symlinks, `..`, chemins absolus)


**Résultats possibles :**

- **Archive valide :** La restauration peut continuer
- **Archive suspecte :** Un avertissement s'affiche, mais vous pouvez continuer
- **Archive corrompue :** La restauration est bloquée avec un message d'erreur


## 14. Personnalisation (Préférences)

La fenêtre des Préférences, accessible via `Fichier > Préférences...`, est le centre de contrôle pour adapter BlueNotebook à vos goûts. Les modifications sont appliquées immédiatement après avoir cliqué sur "Valider".

### Onglet "Général"

- **Police de l'application :** Permet de choisir une police de caractères et une taille qui seront appliquées à l'ensemble de l'interface de l'application (menus, boutons, panneaux, etc.). Ce réglage est idéal pour améliorer la lisibilité ou adapter l'application à vos préférences visuelles. Un redémarrage de l'application est nécessaire pour que ce changement soit pris en compte partout.
- **Statistiques d'indexation :** Cochez pour afficher en permanence le nombre de mots et tags dans la barre de statut.
- **Tags à exclure des nuages :** Permet de masquer certains tags des nuages sans les retirer de l'index de recherche.


### Onglet "Affichage"

Cet onglet est le cœur de la personnalisation visuelle. Il est lui-même divisé en sous-onglets pour l'Éditeur, l'Aperçu, etc.

#### 14.1 Thèmes de l'Éditeur

Dans le sous-onglet **"Éditeur Markdown"**, vous pouvez changer chaque aspect de l'apparence de la zone d'écriture. BlueNotebook vous offre une flexibilité totale, que vous souhaitiez utiliser un thème prêt à l'emploi ou créer le vôtre.

 **Affichage des numéros de lignes ? :**

Cochez cette case pour afficher une marge avec les numéros de ligne à gauche de l'éditeur. C'est pratique pour se repérer dans de longs documents.

**Thèmes de l'éditeur (Clair & Sombre)**

Pour une mise en place rapide, BlueNotebook inclut des thèmes développé par BlueNotebook ainsi que des thèmes inspirés de l'excellent éditeur Markdown [Ghostwriter](https://ghostwriter.kde.org/fr/).

- **Sélectionner un thème :** Cliquez sur ce bouton pour choisir un thème prêt à l'emploi (comme "Classic Light" ou "Classic Dark"). La sélection met instantanément à jour les couleurs dans la fenêtre des préférences pour que vous puissiez prévisualiser le résultat.


**Personnalisation avancée et création de thèmes**

Si vous souhaitez aller plus loin, vous pouvez ajuster chaque couleur individuellement (fond, texte, titres, code, etc.) et même la police de caractères.

- **Sauvegarder comme thème :** Une fois que vous avez créé une palette de couleurs qui vous plaît, cliquez sur ce bouton pour la sauvegarder comme un nouveau thème. Il sera alors disponible dans la liste de sélection.
- **Affichage des numéros de lignes :** Cochez cette case pour afficher une marge avec les numéros de ligne, pratique pour se repérer dans de longs documents.


#### 14.2 Thèmes de l'Aperçu HTML

Dans le sous-onglet **"Aperçu HTML"**, vous pouvez changer radicalement l'apparence du panneau de prévisualisation, ce qui affectera également l'apparence de vos **exports HTML**.

L'apparence est contrôlée par des feuilles de style CSS. Pour vous aider à choisir, une prévisualisation du rendu est intégrée directement dans la fenêtre des préférences.

- **Sélectionner un thème CSS :** Cliquez sur ce bouton pour choisir un style parmi ceux proposés. Vous trouverez des thèmes clairs et sombres inspirés de l'apparence de GitHub.
- **Prévisualisation instantanée :** Dès que vous sélectionnez un thème dans la liste, une mini-fenêtre d'aperçu située en dessous se met à jour pour vous montrer le rendu des titres, paragraphes, liens et blocs de code. Cela vous permet de juger de l'apparence avant de valider votre choix.


Le thème que vous validez est sauvegardé et sera automatiquement appliqué à chaque démarrage de BlueNotebook.

#### 14.3 Thèmes de l'Export PDF

De la même manière que pour l'aperçu HTML, vous pouvez désormais choisir un thème CSS **spécifique pour vos exports PDF**. Cette fonctionnalité est très utile pour utiliser un thème sombre pour l'édition à l'écran, et un thème clair, optimisé pour l'impression, pour vos documents PDF.

- **Accès :** Rendez-vous dans `Préférences > Affichage > Export PDF`.
- **Sélectionner un thème CSS pour le PDF :** Cliquez sur ce bouton pour choisir un style dans le dossier dédié `resources/css_pdf/`. Ces thèmes sont spécialement conçus pour la mise en page des documents PDF.
- **Prévisualisation instantanée :** Comme pour l'aperçu HTML, une mini-fenêtre vous montre le rendu du thème sélectionné avant que vous ne validiez votre choix.


Cette séparation vous offre une flexibilité maximale pour que vos documents finaux aient exactement l'apparence que vous souhaitez, indépendamment de votre thème de travail quotidien.

Le bouton **"Valeurs d'affichage par défaut"**, présent dans l'onglet "Affichage", réinitialise toutes les options de cet onglet (couleurs de l'éditeur, thème de l'aperçu, etc.) à leurs valeurs d'usine.

### Onglet "Panneaux"

Contrôlez quels panneaux sont visibles par défaut au démarrage de l'application pour un espace de travail sur mesure :

- **Panneau "Notes" (`F9`)**
- **Panneau de Navigation (`F6`)**
- **Panneau 'Plan du document' (`F7`)**
- **Panneau 'Aperçu HTML' (`F5`)**
- **Panneau 'Lecteur' (`F8`)**


### Onglet "Intégrations"

Gérez les fonctionnalités additionnelles.

### Le fichier `settings.json`

Toutes les modifications que vous effectuez dans la fenêtre des Préférences sont sauvegardées dans un fichier texte nommé `settings.json`. Ce fichier est le gardien de votre configuration personnelle.

#### À quoi sert-il ?

Il conserve tous vos choix de personnalisation :

- Les polices et les couleurs de l'éditeur.
- La visibilité par défaut des panneaux.
- Les mots et tags que vous souhaitez exclure des index ou des nuages.
- Les options d'intégrations, comme l'affichage de la citation du jour.


Grâce à ce fichier, BlueNotebook se souvient de vos préférences à chaque fois que vous le lancez. Vous pouvez même le sauvegarder pour transférer votre configuration sur un autre ordinateur.

#### Où se trouve-t-il ?

L'emplacement dépend de votre système d'exploitation :

- **Sur Linux :** `~/.config/BlueNotebook/settings.json` (où `~` est votre dossier personnel).
- **Sur Windows :** `C:\Users\VotreNom\.config\BlueNotebook\settings.json`


**Attention :** Il est déconseillé de modifier ce fichier manuellement, sauf si vous savez ce que vous faites. Une erreur de syntaxe pourrait entraîner la réinitialisation de vos préférences. Utilisez toujours la fenêtre des Préférences pour modifier les paramètres en toute sécurité.

## 15. Raccourcis Clavier

| Action | Raccourci |
| --- | --- |
| Nouveau fichier | `Ctrl+N` |
| Ouvrir un fichier | `Ctrl+O` |
| Sauvegarder | `Ctrl+S` |
| Sauvegarder sous... | `Ctrl+Shift+S` |
| Quitter l'application | `Ctrl+Q` |
| Annuler | `Ctrl+Z` |
| Rétablir | `Ctrl+Y` |
| Rechercher | `Ctrl+F` |
| Mettre en gras | `Ctrl+B` |
| Afficher/Masquer les détails (Panneau Notes) | `Ctrl+M` |
| Insérer une image | `Ctrl+I` |
| Basculer l'aperçu | `F5` |
| Basculer la navigation | `F6` |
| Basculer le plan du document | `F7` |
| Basculer le lecteur de documents | `F8` |
| Basculer l'explorateur de notes | `F9` |


## 16. Foire Aux Questions (FAQ)

Vous trouverez ici les réponses aux questions les plus fréquentes sur l'utilisation de l'application.

### Gestion du Journal et des Notes

Q : Comment créer une nouvelle note pour la journée ?
**R :** C'est automatique ! Au lancement, BlueNotebook ouvre ou crée pour vous un fichier pour la date du jour (ex: `20250927.md`). Vous n'avez qu'à commencer à écrire.

Q : Comment ajouter des informations à une note existante de la journée ?
**R :** Lorsque vous sauvegardez (`Ctrl+S`) une note pour un jour qui existe déjà, BlueNotebook vous demande si vous voulez **"Ajouter à la fin"** ou **"Remplacer"**. Choisissez "Ajouter à la fin" pour conserver vos écrits précédents et ajouter les nouveaux.

Q : Comment puis-je consulter ou modifier une note d'un autre jour ?
**R :** Vous avez deux options principales :

1. **Utilisez le calendrier** dans le panneau de Navigation à gauche. Les jours avec une note sont en bleu. Cliquez sur une date pour ouvrir la note correspondante.
2. Utilisez le menu `Fichier > Ouvrir` (`Ctrl+O`) pour parcourir manuellement votre dossier de journal.

### L'Éditeur Markdown

Q : Qu'est-ce que le Markdown ?
**R :** Le Markdown est une syntaxe très simple pour mettre en forme du texte. Au lieu de cliquer sur des boutons, vous utilisez des symboles pour indiquer le formatage, ce qui vous permet de ne pas quitter votre clavier. L'aperçu à droite vous montre le résultat en temps réel.

Q : Comment mettre du texte en gras ou en italique ?
**R :** Pour le **gras**, entourez votre texte de deux astérisques : `**texte en gras**`. Pour l'*italique*, entourez-le d'un seul astérisque : `*texte en italique*`. Vous pouvez aussi utiliser le menu `Formater > Style de texte`.

Q : Y a-t-il un moyen rapide de formater du texte sans utiliser les menus ?
**R :** Oui ! En plus des raccourcis clavier, vous pouvez maintenant faire un **clic droit** sur du texte que vous avez sélectionné. Un menu contextuel apparaîtra, vous donnant un accès direct aux options de formatage, y compris les sous-menus pour les **Titres**, les **Listes**, le **Style de texte** et le **Code**.

Q : Quelle est la différence entre "Lien Markdown" et "Lien URL/Email" ?
**R :**

- **Lien Markdown** : Ouvre une boîte de dialogue pour créer un lien avec un texte personnalisé (ex: `Visitez notre site`). Si vous n'avez rien sélectionné, les champs sont vides. Si vous avez sélectionné du texte, il est utilisé comme texte du lien.
- **Lien URL/Email** : Est une action rapide. Sélectionnez une URL ou une adresse e-mail dans votre texte, et cette action l'encadrera de chevrons (`<https://example.com>`) pour la rendre automatiquement cliquable dans l'aperçu.

Q : Comment nettoyer un paragraphe mal formaté (par exemple, après une conversion PDF) ?
**R :** Sélectionnez le paragraphe contenant des sauts de ligne ou des espaces superflus, faites un clic droit, puis choisissez `Mise en forme > Nettoyer le paragraphe`. L'application fusionnera les lignes en un seul paragraphe fluide et supprimera les espaces en trop.

### Recherche et Navigation

Q : Comment retrouver rapidement une information dans mon journal ?
**R :** Utilisez le champ de recherche situé dans le panneau de Navigation, sous le calendrier. Vous pouvez y rechercher des tags.

Q : Comment rechercher un tag spécifique (ex: `@@projet`) ?
**R :** Tapez simplement `@@projet` dans le champ de recherche et appuyez sur `Entrée`. La recherche est insensible à la casse et aux accents : chercher `@@météo` trouvera le tag `@@METEO`. Vous pouvez aussi cliquer sur le bouton `▼` pour voir la liste de tous vos tags (qui sont affichés sous leur forme normalisée, en majuscules).

Q : À quoi servent les "Nuages de Tags/Mots" ?
**R :** Ils vous montrent les tags et les mots que vous utilisez le plus fréquemment. C'est un moyen de voir les thèmes principaux de votre journal. **Cliquez sur un mot ou un tag dans un nuage pour lancer immédiatement une recherche sur ce terme !**

Q : Que se passe-t-il quand je clique sur un résultat de recherche ?
**R :** L'application ouvre la note correspondante et positionne le curseur **directement à la ligne** où l'occurrence a été trouvée. C'est un moyen ultra-rapide de retrouver le contexte exact d'une information.

### Sauvegarde et Sécurité

Q : Comment faire une sauvegarde complète de tout mon journal ?
**R :** Allez dans `Fichier > Sauvegarde Journal...`. Cela créera une archive `.zip` contenant toutes vos notes et les fichiers d'index. C'est une bonne pratique à faire régulièrement.

Q : Comment restaurer mon journal depuis une sauvegarde ?
**R :** Utilisez `Fichier > Restauration Journal...`. La procédure est très sécurisée : avant de restaurer, BlueNotebook renomme votre journal actuel pour en faire une sauvegarde (ex: `MonJournal.bak-20250927-103000`). **Vos données actuelles ne sont jamais supprimées.** Vous devrez simplement redémarrer l'application après la restauration.

### Export et Partage

Q : Comment puis-je partager une de mes notes ?
**R :** La meilleure façon de partager une note est de l'exporter en HTML. Allez dans `Fichier > Exporter HTML...`. Une boîte de dialogue s'ouvrira en vous proposant un nom de fichier intelligent (`BlueNotebook-nom-date.html`) et se souviendra du dernier dossier que vous avez utilisé. Le fichier HTML généré utilisera le même thème visuel que votre aperçu dans l'application.

Q : Comment puis-je créer un PDF de tout ou partie de mon journal ?
**R :** Utilisez la fonction `Fichier > Exporter Journal PDF...`. C'est un outil puissant qui vous permet de créer un document PDF professionnel. Une boîte de dialogue vous permettra de :

- Sélectionner une **plage de dates** pour n'inclure que certaines notes.
- Définir un **titre**, un **nom d'auteur** et même une **image de couverture** pour la page de garde.
L'application mémorise vos choix (dossier, titre, auteur) pour vous faire gagner du temps lors des prochains exports. Le résultat est un document paginé, parfait pour l'archivage ou l'impression.

Q : Comment transformer mon journal en livre numérique (EPUB) ?
**R :** BlueNotebook propose une fonction d'export EPUB très complète via `Fichier > Exporter Journal EPUB...`. Elle transforme votre journal en un véritable livre numérique pour liseuses. En plus des options de dates, titre et auteur, l'export EPUB inclut :

- Une **couverture personnalisée** générée automatiquement.
- Une **table des matières** cliquable.
- L'**intégration de toutes vos images**, redimensionnées et compressées.
- Un **index des tags** à la fin du livre pour une navigation par thème.
C'est la solution idéale pour une relecture confortable de vos souvenirs sur n'importe quelle liseuse.

### Personnalisation et Thèmes

Q : Comment puis-je créer mon propre thème de couleurs pour l'éditeur Markdown de BlueNotebook ?
**R :** C'est très simple !

1. Allez dans `Préférences > Affichage > Éditeur Markdown`.
2. Allez dans `Préférences > Affichage > Éditeur Markdown`.
3. Ajustez les différentes couleurs (fond, texte, titres, etc.) et la police jusqu'à obtenir un résultat qui vous plaît.
4. Cliquez sur le bouton `Sauvegarder comme thème`.
5. Donnez un nom à votre thème (ex: "Mon Thème Sombre") et validez.
Votre thème est maintenant sauvegardé et vous pouvez le sélectionner à tout moment depuis le bouton `Sélectionner un thème`.

Q : Comment modifier un thème existant ?
**R :**

1. Ouvrez les `Préférences > Affichage > Éditeur Markdown`.
2. Ouvrez les `Préférences > Affichage > Éditeur Markdown`.
3. Cliquez sur `Sélectionner un thème` et choisissez le thème que vous souhaitez modifier. Ses couleurs sont alors chargées dans l'interface.
4. Changez les couleurs ou la police que vous voulez ajuster.
5. Cliquez sur `Sauvegarder comme thème`. Vous pouvez soit lui donner un nouveau nom pour créer une variation, soit utiliser le même nom pour écraser et mettre à jour le thème existant.

## 17. Principaux Packages Python

Voici une liste des principales bibliothèques Python qui animent le projet BlueNotebook, avec une explication de leur rôle.

### Interface Graphique et Composants de Base

- **PyQt5** : C'est le cœur de l'application. Ce framework est utilisé pour créer toute l'interface utilisateur, des fenêtres aux boutons, en passant par les menus et les panneaux. La partie `QWebEngineWidgets` est spécifiquement utilisée pour l'aperçu HTML en temps réel.   - **Auteur :** Riverbank Computing
  - **Site Officiel :** [www.riverbankcomputing.com](https://www.riverbankcomputing.com)


### Traitement du Markdown et du HTML

- **python-markdown** : Cette bibliothèque est essentielle pour convertir le texte que vous écrivez en Markdown vers le format HTML qui est affiché dans le panneau d'aperçu.   - **Auteur :** Waylan Limberg et contributeurs
  - **Dépôt GitHub :** [github.com/Python-Markdown/markdown](https://github.com/Python-Markdown/markdown)
- **Pygments** : Utilisée par `python-markdown` pour réaliser la coloration syntaxique des blocs de code dans l'aperçu HTML, ce qui rend le code beaucoup plus lisible.   - **Auteur :** Georg Brandl et contributeurs
  - **Dépôt GitHub :** [github.com/pygments/pygments](https://github.com/pygments/pygments)
- **pymdown-extensions** : Fournit des fonctionnalités Markdown supplémentaires qui ne sont pas dans la version de base, comme le surlignage (`==texte==`) ou le texte barré (`~~texte~~`).   - **Auteur :** Isaac Muse
  - **Dépôt GitHub :** [github.com/facelessuser/pymdown-extensions](https://github.com/facelessuser/pymdown-extensions)
- **BeautifulSoup4 (`bs4`)** : Un outil très puissant utilisé à plusieurs endroits pour analyser (parser) du code HTML. Il sert notamment à extraire la citation du jour, mais aussi à trouver et traiter les images et les tags lors de l'export EPUB.   - **Auteur :** Leonard Richardson
  - **Site Officiel :** [www.crummy.com/software/BeautifulSoup/](https://www.crummy.com/software/BeautifulSoup/)


### Export de Documents

- **WeasyPrint** : C'est la bibliothèque qui permet de générer les exports PDF de haute qualité. Elle prend le contenu HTML du journal et le transforme en un document PDF paginé.   - **Auteur :** Kozea
  - **Dépôt GitHub :** [github.com/Kozea/WeasyPrint](https://github.com/Kozea/WeasyPrint)
- **EbookLib** : La bibliothèque centrale pour la création des fichiers au format EPUB. Elle gère l'assemblage des chapitres, la création de la table des matières, l'intégration de la couverture et des images.   - **Auteur :** Aleksandar Erkalovic
  - **Dépôt GitHub :** [github.com/aerkalov/ebooklib](https://github.com/aerkalov/ebooklib)


### Gestion des PDF

- **PyMuPDF (`fitz`)** : Une bibliothèque extrêmement rapide et polyvalente pour lire, rendre et extraire des données de fichiers PDF. Elle est au cœur du lecteur PDF, gérant l'affichage des pages, l'extraction de la table des matières et la sélection de texte.   - **Dépôt GitHub :** [github.com/pymupdf/PyMuPDF](https://github.com/pymupdf/PyMuPDF)


### Conversion de Documents

- **pymupdf4llm** : Une bibliothèque de l'écosystème PyMuPDF utilisée pour la conversion de PDF en Markdown. Elle est optimisée pour extraire un contenu propre et structuré, adapté à une utilisation avec les grands modèles de langage (LLM).   - **Dépôt GitHub :** [github.com/pymupdf/pymupdf-llm](https://github.com/pymupdf/pymupdf-llm)


### Manipulation d'Images

- **Pillow** (un fork de PIL) : Utilisée pour tout ce qui touche à la manipulation d'images. Elle sert principalement à créer l'image de couverture composite pour l'export EPUB (en combinant une image et du texte) et à redimensionner/compresser les images avant de les inclure dans le livre numérique.   - **Auteur :** Alex Clark et contributeurs
  - **Dépôt GitHub :** [github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow)
- **cairosvg** : Une bibliothèque spécialisée qui permet de convertir les images au format vectoriel SVG en format PNG, car Pillow ne peut pas lire les SVG nativement. C'est crucial pour l'export EPUB.   - **Auteur :** Kozea
  - **Dépôt GitHub :** [github.com/Kozea/cairosvg](https://github.com/Kozea/cairosvg)


### Intégrations et Réseau

- **requests** : C'est la bibliothèque de référence pour effectuer des requêtes sur internet. Elle est utilisée pour récupérer la citation du jour, les informations sur les vidéos YouTube, les données météo, et pour télécharger les images depuis des URLs lors de l'export EPUB.   - **Auteur :** Python Software Foundation (mainteneur actuel)
  - **Dépôt GitHub :** [github.com/psf/requests](https://github.com/psf/requests)
- **geopy** : Utilisée pour la géolocalisation, notamment pour convertir les noms de villes en coordonnées géographiques (latitude et longitude) pour l'intégration "Astro du Jour".   - **Auteur :** Geopy Contributors
  - **Dépôt GitHub :** [github.com/geopy/geopy](https://github.com/geopy/geopy)

---


*Ce manuel a été rédigé pour la version V4.2.10 de BlueNotebook.*

Si vous rencontrez des erreurs ou dysfonctionnements, vous pouvez notifier ceux-ci sur le [site du développeur](https://github.com/lephotographelibre/BlueNotebook/issues).

BlueNotebook est un logiciel libre distribué sous les termes de la [Licence Publique Générale GNU v3](https://www.gnu.org/licenses/gpl-3.0.html).

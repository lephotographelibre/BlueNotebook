# Document d'Architecture Technique - BlueNotebook V1.1.11

## 1. Introduction

Ce document décrit l'architecture technique de l'application BlueNotebook, un journal personnel et éditeur Markdown. L'objectif est de fournir une vue d'ensemble de la structure du projet, de ses composants principaux, de ses dépendances et de son fonctionnement interne.

## 2. Structure du Projet

### 2.1. Arborescence Complète

L'arborescence complète des fichiers du projet (hors fichiers de cache `__pycache__`) est la suivante :

```
.
├── architecture.md
├── core
│   ├── file_handler.py
│   ├── __init__.py
│   ├── markdown_parser.py
│   └── quote_fetcher.py
├── gui
│   ├── citation_fetcher.py
│   ├── editor.py
│   ├── __init__.py
│   ├── main_window119.py
│   ├── main_window.py
│   ├── preview.py
│   ├── Pychar
│   └── test_editor.py
├── main.py
├── manuel_utilisateur.md
├── README.md
├── requirements.txt
├── resources
│   ├── html
│   │   └── bluenotebook_aide_en_ligne.html
│   ├── icons
│   │   ├── bluenotebook_64-x64_fond_blanc.ico
│   │   ├── bluenotebook.ico
│   │   ├── ... (et autres icônes .png, .svg)
│   ├── images
│   │   └── bluenotebook_256-x256_fond_blanc.png
│   └── templates
│       └── PageJournal.md
├── run_bluenotebook.bat
├── run_bluenotebook.sh
├── scripts
└── tests
    ├── __init__.py
    ├── test_file_handler.py
    └── test_markdown_parser.py
```

### 2.2. Description des Répertoires

- **`core/`**: Contient la logique métier principale (non-GUI), comme la gestion des fichiers et l'analyse du Markdown.
- **`gui/`**: Regroupe tous les composants de l'interface graphique (fenêtres, widgets) construits avec PyQt5.
- **`resources/`**: Stocke les ressources statiques : icônes, images, modèles de page, et la documentation HTML.
- **`tests/`**: Contient les tests unitaires pour assurer la fiabilité des composants du `core`.
- **`scripts/`**: Prévu pour des scripts utilitaires (build, déploiement, etc.).

## 3. Composants Principaux

(Cette section reste globalement inchangée, voir la version précédente du document)

## 4. Structure des Menus de l'Interface

La structure hiérarchique des menus définit les fonctionnalités accessibles à l'utilisateur. Elle est représentée ci-dessous pour plus de clarté :

```
📁 Fichier
├── 📄 Nouveau (Ctrl+N): Crée une nouvelle note vierge.
├── 📂 Ouvrir (Ctrl+O): Ouvre un fichier Markdown existant.
├── 📓 Ouvrir Journal: Sélectionne le dossier qui sert de journal.
├── 💾 Sauvegarder (Ctrl+S): Enregistre la note dans le fichier du jour.
├── 💾 Sauvegarder sous... (Ctrl+Shift+S): Enregistre dans un nouveau fichier.
├── 🌐 Exporter HTML...: Exporte la note actuelle au format HTML.
└── 🚪 Quitter (Ctrl+Q): Ferme l'application.

✏️ Edition
├── ↩️ Annuler (Ctrl+Z): Annule la dernière action.
├── ↪️ Rétablir (Ctrl+Y): Rétablit la dernière action annulée.
└── 🔍 Rechercher (Ctrl+F): Ouvre un dialogue de recherche.

👁️ Affichage
└── 👁️ Basculer l'aperçu (F5): Affiche ou masque le panneau de prévisualisation.

🎨 Formater
├── 📜 Titres
│   ├── 1️⃣ Niv 1 (#)
│   ├── 2️⃣ Niv 2 (##)
│   ├── 3️⃣ Niv 3 (###)
│   ├── 4️⃣ Niv 4 (####)
│   └── 5️⃣ Niv 5 (#####)
├── 🎨 Style de texte
│   ├── 🅱️ Gras (**texte**)
│   ├── *️⃣ Italique (*texte*)
│   ├── ~ Barré (~~texte~~)
│   └── 🖍️ Surligné (==texte==)
├── 💻 Code
│   ├── ` Monospace (inline)
│   └── ``` Bloc de code
├── 📋 Listes
│   ├── • Liste non ordonnée
│   ├── 1. Liste ordonnée
│   └── ☑️ Liste de tâches
├── ➕ Insérer
│   ├── 🔗 Lien (URL ou email)
│   ├── 🖼️ Image
│   ├── 🔗 Lien Markdown
│   ├── 🔗 Fichier (Lien interne)
│   ├── ➖ Ligne Horizontale
│   ├── ▦ Tableau
│   ├── 💬 Citation
│   ├── ✨ Citation du jour
│   ├── 🏷️ Tag (@@)
│   └── 🕒 Heure
└── 🧹 RaZ (Effacer le formatage)

❓ Aide
├── 🌐 Documentation en ligne
└── ℹ️ À propos
```


## 5. Justification de l'Architecture

L'architecture actuelle, qui sépare distinctement le **Noyau Métier (`core`)** de l'**Interface Graphique (`gui`)**, a été choisie pour plusieurs raisons stratégiques :

1.  **Séparation des préoccupations (SoC)**: C'est le principe fondamental appliqué ici. La logique de manipulation des données (lecture/écriture de fichiers, parsing Markdown) est complètement indépendante de la manière dont elle est présentée à l'utilisateur. Cela rend le code plus propre et plus facile à comprendre.

2.  **Maintenabilité**: Si l'interface utilisateur doit être modifiée (par exemple, changer un bouton de place, ou même migrer de PyQt5 à une autre technologie), la logique métier dans `core` reste intacte. Inversement, une modification dans l'algorithme de parsing Markdown n'impactera pas l'interface.

3.  **Testabilité**: La logique métier dans `core` peut être testée unitairement de manière fiable et rapide, sans avoir besoin de simuler des interactions complexes avec l'interface graphique. Les tests existants dans `tests/` en sont la preuve.

4.  **Réutilisabilité**: Les composants du `core` pourraient être réutilisés dans un autre contexte, par exemple pour un utilitaire en ligne de commande qui convertirait des fichiers Markdown, ou une version web de l'application.

## 6. Recommandations pour l'Évolution

### 6.1. Stack Technique

- **Migration de PyQt5 vers PySide6**: PyQt5 est sous licence GPL, ce qui impose des contraintes fortes si l'application devait être distribuée commercialement. PySide6, maintenu officiellement par le projet Qt, est sous licence LGPL, beaucoup plus permissive. La migration est généralement simple car les API sont très similaires.

- **Base de données pour la gestion des notes**: Actuellement, les notes sont des fichiers `.md` indépendants. Pour des fonctionnalités avancées comme la recherche plein texte rapide, la gestion de métadonnées (tags, dates) et les relations entre les notes, l'utilisation d'une base de données légère comme **SQLite** (intégrée à Python) serait une évolution majeure et bénéfique. Chaque note serait un enregistrement dans la base, tout en pouvant être exportée en `.md`.

- **Gestion asynchrone des tâches**: Pour des opérations comme la récupération de la citation du jour ou de futures synchronisations cloud, l'utilisation de `asyncio` pourrait améliorer la réactivité de l'application en évitant de bloquer l'interface, de manière plus moderne que les timers ou les threads dédiés.

### 6.2. Fonctionnalités Utilisateur

- **Recherche Avancée**: En lien avec la suggestion d'une base de données, implémenter une recherche plein texte sur l'ensemble du journal, avec la possibilité de filtrer par tags, par date, etc.

- **Synchronisation Cloud**: Permettre aux utilisateurs de synchroniser leur journal avec des services comme Dropbox, Google Drive ou un dépôt Git privé. C'est une fonctionnalité très demandée pour les applications de prise de notes.

- **Thématisation**: Offrir un mode sombre (`dark mode`) et la possibilité pour les utilisateurs de personnaliser les couleurs de l'éditeur et de la prévisualisation via des fichiers de style (CSS).

- **Support des Modèles (Templates)**: Améliorer la fonctionnalité de modèle de page (`PageJournal.md`) pour permettre à l'utilisateur de créer et gérer plusieurs modèles pour différents types d'entrées (ex: note de réunion, entrée de journal intime, etc.).

- **Export PDF**: En plus de l'export HTML, permettre d'exporter une note, une sélection de notes ou le journal entier au format PDF, une fonctionnalité déjà envisagée (marquée "soon" dans la boîte "À propos").

---
*Ce document a été mis à jour pour la version 1.1.11.*


# Manuel Utilisateur - BlueNotebook v1.1.11

## 1. Introduction

Bienvenue dans BlueNotebook ! Ce guide vous explique comment utiliser l'application pour tenir votre journal personnel en Markdown.

BlueNotebook est un éditeur de texte simple qui vous permet de vous concentrer sur l'écriture. Il utilise la syntaxe Markdown et affiche un aperçu en temps réel de votre document.

## 2. Lancement et Configuration

### Comment Lancer BlueNotebook

- **Sur Windows** : Double-cliquez sur le fichier `run_bluenotebook.bat`. Une fenêtre de terminal s'ouvrira pour configurer l'environnement, puis l'application se lancera.
- **Sur Linux** : Ouvrez un terminal, rendez le script exécutable une seule fois avec la commande `chmod +x run_bluenotebook.sh`, puis lancez-le avec `./run_bluenotebook.sh`.

### Configurer votre Répertoire de Journal

BlueNotebook a besoin de savoir où sauvegarder vos notes. Il existe trois manières de lui indiquer, par ordre de priorité :

1.  **Argument de Ligne de Commande `--journal` (Priorité la plus haute)**
    Vous pouvez spécifier un dossier de journal directement au lancement. C'est la méthode la plus flexible.
    - Sur Linux : `./run_bluenotebook.sh --journal /chemin/vers/mon/journal`
    - Sur Windows : `run_bluenotebook.bat --journal C:\Users\VotreNom\Documents\Journal`

2.  **Variable d'Environnement `JOURNAL_DIRECTORY`**
    Vous pouvez définir cette variable pour que BlueNotebook l'utilise par défaut à chaque lancement.
    - Sur Linux (temporaire) : `export JOURNAL_DIRECTORY="/chemin/vers/mon/journal" && ./run_bluenotebook.sh`
    - Sur Windows (temporaire) : `set JOURNAL_DIRECTORY=C:\chemin\vers\journal && run_bluenotebook.bat`

3.  **Répertoire par Défaut (Priorité la plus basse)**
    Si aucune des méthodes ci-dessus n'est utilisée, BlueNotebook créera et utilisera un dossier nommé `bluenotebook` dans votre répertoire personnel.

## 3. L'interface Principale

L'interface est divisée en deux panneaux principaux :

1.  **L'Éditeur (à gauche) :** C'est ici que vous écrivez votre texte en utilisant la syntaxe Markdown.
2.  **La Prévisualisation (à droite) :** Affiche le rendu final de votre texte, mis en forme.

Vous pouvez redimensionner ces panneaux en faisant glisser le séparateur central. Vous pouvez également masquer/afficher la prévisualisation avec la touche `F5`.

La **barre de statut**, située tout en bas de la fenêtre, est une source d'information précieuse. De gauche à droite, vous y trouverez :
- Le nom du **fichier actuel** (ex: `20250920.md`).
- Un indicateur de modification (`●`) qui apparaît si votre travail n'est pas enregistré.
- Le chemin vers votre **dossier de journal**, affiché en bleu pour le repérer facilement.
- À l'extrémité droite, des **statistiques** sur votre document, mises à jour en temps réel : le nombre de lignes, de mots et de caractères.

## 4. Le concept de "Journal" et son fonctionnement

BlueNotebook est organisé autour d'un concept simple mais puissant : votre journal est un dossier sur votre ordinateur, et chaque journée est un fichier texte.

### La Note du Jour

À chaque lancement, BlueNotebook vérifie votre dossier de journal. Il cherche un fichier correspondant à la date du jour, nommé selon le format `AAAAMMJJ.md` (par exemple, `20250920.md`). Si ce fichier existe, il l'ouvre automatiquement. Sinon, il vous présente une nouvelle page vierge, prête à devenir l'entrée de la journée.

### La Sauvegarde Intelligente

L'action de sauvegarde (`Fichier > Sauvegarder` ou `Ctrl+S`) est au cœur de ce système :

- **Si la note du jour n'existe pas encore**, elle sera simplement créée avec le contenu de l'éditeur.
- **Si la note du jour existe déjà**, une boîte de dialogue vous proposera deux choix cruciaux :
    - **Ajouter à la fin**: Votre nouveau texte sera ajouté à la suite du contenu existant, séparé par une ligne. C'est l'option idéale pour ajouter des pensées ou des notes tout au long de la journée sans perdre les informations précédentes.
    - **Remplacer**: Le contenu original de la note du jour sera entièrement écrasé et remplacé par ce qui se trouve actuellement dans l'éditeur. Soyez prudent avec cette option !

### Accéder aux Anciennes Notes

Pour consulter ou modifier une entrée d'un jour précédent, utilisez simplement le menu `Fichier > Ouvrir` (`Ctrl+O`). Une fenêtre s'ouvrira, vous permettant de naviguer jusqu'à votre répertoire de journal et de sélectionner le fichier correspondant à la date souhaitée (par exemple, `20250919.md` pour relire la note de la veille).

## 5. Exploration Détaillée des Menus

Voici un guide visuel de toutes les fonctionnalités accessibles depuis la barre de menus.

```
📁 Fichier
├── 📄 Nouveau (Ctrl+N): Crée une nouvelle note vierge.
├── 📂 Ouvrir (Ctrl+O): Ouvre un fichier Markdown existant.
├── 📓 Ouvrir Journal: Sélectionne le dossier qui sert de journal.
├── 💾 Sauvegarder (Ctrl+S): Enregistre la note dans le fichier du jour.
├── 💾 Sauvegarder sous... (Ctrl+Shift+S): Enregistre dans un nouveau fichier.
├── 🌐 Exporter HTML...: Exporte la note actuelle au format HTML.
└── 🚪 Quitter (Ctrl+Q): Ferme l'application.

✏️ Edition
├── ↩️ Annuler (Ctrl+Z): Annule la dernière action.
├── ↪️ Rétablir (Ctrl+Y): Rétablit la dernière action annulée.
└── 🔍 Rechercher (Ctrl+F): Ouvre un dialogue de recherche.

👁️ Affichage
└── 👁️ Basculer l'aperçu (F5): Affiche ou masque le panneau de prévisualisation.

🎨 Formater
├── 📜 Titres
│   ├── 1️⃣ Niv 1 (#)
│   ├── 2️⃣ Niv 2 (##)
│   ├── 3️⃣ Niv 3 (###)
│   ├── 4️⃣ Niv 4 (####)
│   └── 5️⃣ Niv 5 (#####)
├── 🎨 Style de texte
│   ├── 🅱️ Gras (**texte**)
│   ├── *️⃣ Italique (*texte*)
│   ├── ~ Barré (~~texte~~)
│   └── 🖍️ Surligné (==texte==)
├── 💻 Code
│   ├── ` Monospace (inline)
│   └── ``` Bloc de code
├── 📋 Listes
│   ├── • Liste non ordonnée
│   ├── 1. Liste ordonnée
│   └── ☑️ Liste de tâches
├── ➕ Insérer
│   ├── 🔗 Lien (URL ou email)
│   ├── 🖼️ Image
│   ├── 🔗 Lien Markdown
│   ├── 🔗 Fichier (Lien interne)
│   ├── ➖ Ligne Horizontale
│   ├── ▦ Tableau
│   ├── 💬 Citation
│   ├── ✨ Citation du jour
│   ├── 🏷️ Tag (@@)
│   └── 🕒 Heure
└── 🧹 RaZ (Effacer le formatage)

❓ Aide
├── 🌐 Documentation en ligne
└── ℹ️ À propos
```


## 6. Récapitulatif des Raccourcis Clavier

Pour une productivité accrue, utilisez les raccourcis clavier suivants :

| Action | Raccourci |
| :--- | :--- |
| Nouveau fichier | `Ctrl+N` |
| Ouvrir un fichier | `Ctrl+O` |
| Sauvegarder | `Ctrl+S` |
| Sauvegarder sous... | `Ctrl+Shift+S` |
| Quitter l'application | `Ctrl+Q` |
| Annuler | `Ctrl+Z` |
| Rétablir | `Ctrl+Y` |
| Rechercher | `Ctrl+F` |
| Mettre en gras | `Ctrl+B` |
| Insérer une image | `Ctrl+I` |
| Basculer l'aperçu | `F5` |

## 7. Exemples d'Utilisation

Comment utiliser BlueNotebook au quotidien ? Voici quelques idées.

### Cas 1 : Le Journal de Bord Professionnel

Utilisez BlueNotebook pour suivre votre journée de travail. Chaque matin, lancez l'application. L'entrée du jour est prête.

- Utilisez les **Titres** (`#`) pour séparer les projets ou les réunions.
- Créez des **listes de tâches** (`- [ ]`) pour vos objectifs de la journée et cochez-les (`- [x]`) au fur et à mesure.
- Insérez l'**heure** (`Formater > Insérer > Heure`) avant de noter les minutes d'un appel.
- Collez des extraits de code dans des **blocs de code** pour les garder sous la main.
- Utilisez les **tags** (`@@projet-alpha`) pour retrouver facilement toutes les notes liées à un projet.

### Cas 2 : Le Journal Intime

C'est l'usage classique. BlueNotebook offre un environnement sans distraction pour vos pensées.

- Écrivez librement. La date est gérée automatiquement.
- Insérez la **citation du jour** pour commencer votre session d'écriture avec une inspiration.
- Utilisez les **citations** (`>`) pour retranscrire des dialogues ou des pensées marquantes.
- Ajoutez des **images** pour illustrer un souvenir.

### Cas 3 : La Base de Connaissances Personnelle

Transformez votre journal en un wiki personnel.

- Créez une note pour un sujet spécifique en utilisant `Fichier > Sauvegarder sous...` (ex: `recette-lasagnes.md`).
- Documentez une procédure technique avec des **blocs de code** et des **listes numérotées**.
- Enregistrez des liens importants avec une description pour vous en souvenir.
- Utilisez la fonction `Rechercher` (`Ctrl+F`) pour retrouver rapidement une information.

## 8. Personnalisation des Scripts de Lancement

Les scripts `run_bluenotebook.sh` (Linux) et `run_bluenotebook.bat` (Windows) ne font pas que lancer l'application, ils gèrent aussi l'environnement Python pour s'assurer que tout fonctionne correctement. Voici comment ils sont structurés :

### Script Linux (`run_bluenotebook.sh`)

```bash
#!/bin/bash

# ... (Partie de vérification de pyenv et des dépendances)

# Lancement de l'application
python main.py "$@"
```

- **`python main.py`**: C'est la commande qui exécute le programme.
- **`"$@"`**: Cette variable spéciale est très importante. Elle transmet tous les arguments que vous ajoutez à la ligne de commande (comme `--journal ...`) directement au script Python. C'est ce qui permet à la configuration par argument de fonctionner.

### Script Windows (`run_bluenotebook.bat`)

```batch
@echo off
REM ... (Partie de vérification de pyenv et des dépendances)

REM Lancement de l'application
python main.py %*
```

- **`python main.py`**: Lance le programme.
- **`%*`**: C'est l'équivalent sous Windows de `"$@"`. Il récupère tous les arguments passés au `.bat` et les transmet au script `main.py`.

Vous pouvez modifier ces scripts pour, par exemple, définir de manière permanente la variable `JOURNAL_DIRECTORY` si vous ne souhaitez pas utiliser les autres méthodes.

---
*Ce manuel a été rédigé pour la version 1.1.11 de BlueNotebook.*

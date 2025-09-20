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

# **BlueNotebook - Documentation Technique**

**Version du Document :** V2.6.2
**Date :** 17 octobre 2025
**Auteur :** Jean-Marc Digne



## 1. Introduction et Vision du Produit

BlueNotebook est une application de bureau multiplateforme (Windows, Linux) conçue pour la prise de notes et la tenue d'un journal personnel. Son principe fondamental est de fournir un environnement d'écriture centré sur le texte, basé sur la syntaxe **Markdown**, tout en offrant des fonctionnalités riches de navigation, de recherche et de personnalisation.

L'application s'adresse aux utilisateurs qui apprécient la simplicité et la portabilité du format texte brut, mais qui souhaitent bénéficier d'une interface graphique moderne et d'outils avancés pour organiser et retrouver leurs informations.

La vision du produit est de combiner le meilleur des deux mondes :

*   **La pérennité des données :** Le journal est un simple dossier de fichiers `.md`, lisibles par n'importe quel éditeur de texte.
*   **L'efficacité d'une application dédiée :** Navigation par calendrier, recherche plein texte, indexation de tags, aperçu en temps réel, exports professionnels (PDF, EPUB), et intégrations de services web.

Copyright (C) 2025 Jean-Marc DIGNE

Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le modifier conformément aux termes de la Licence Publique Générale GNU telle que publiée par la Free Software Foundation ; soit la version 3 de la licence, soit (à votre choix) toute version ultérieure.


[![License GNU](https://img.shields.io/github/license/lephotographelibre/BlueNotebook)](https://www.gnu.org/licenses/>)

## **Table des Matières**
1.  [Introduction et Vision du Produit](#1-introduction-et-vision-du-produit)
2.  [Architecture Logicielle](#2-architecture-logicielle)
    *   [2.1. Vue d'ensemble](#21-vue-densemble)
    *   [2.2. Description des Composants](#22-description-des-composants)
3.  [Technologies et Dépendances](#3-technologies-et-dépendances)
4.  [Description Détaillée des Fonctionnalités](#4-description-détaillée-des-fonctionnalités)
    *   [4.1. Cœur de l'Application (Core)](#41-cœur-de-lapplication-core)
    *   [4.2. Interface Utilisateur (GUI)](#42-interface-utilisateur-gui)
    *   [4.3. Intégrations Externes](#43-intégrations-externes)
5.  [Gestion des Données](#5-gestion-des-données)
    *   [5.1. Le Répertoire du Journal](#51-le-répertoire-du-journal)
    *   [5.2. Fichiers d'Indexation](#52-fichiers-dindexation)
    *   [5.3. Fichiers de Configuration](#53-fichiers-de-configuration)
6.  [Recommandations d'Évolution](#6-recommandations-dévolution)
    *   [6.1. Évolutions Techniques](#61-évolutions-techniques)
    *   [6.2. Évolutions Fonctionnelles](#62-évolutions-fonctionnelles)
7.  [Conclusion](#7-conclusion)

---

## 2. Architecture Logicielle

### 2.1. Vue d'ensemble

L'application est développée en Python 3 et suit une architecture modulaire qui sépare clairement les responsabilités. La structure du projet est organisée comme suit :

```
bluenotebook/
├── core/         # Logique métier, indépendante de l'interface
├── gui/          # Tous les composants de l'interface graphique (PyQt5)
├── integrations/ # Modules pour interagir avec des services externes
├── resources/    # Fichiers statiques (icônes, templates, CSS, thèmes)
├── tests/        # Tests unitaires
└── main.py       # Point d'entrée de l'application
```

Cette séparation permet une bonne maintenabilité et facilite l'évolution indépendante des différentes parties de l'application. Par exemple, la logique d'indexation dans `core` pourrait être réutilisée avec une autre interface (web, mobile), et l'interface `gui` pourrait être modifiée sans impacter la manière dont les fichiers sont gérés.

### 2.2. Description des Composants

#### `main.py`

Le point d'entrée de l'application. Il est responsable de :

*   L'initialisation de `QApplication`.
*   La gestion de l'internationalisation (i18n) pour les composants Qt.
*   Le parsing des arguments de ligne de commande (ex: `--journal`).
*   L'instanciation et l'affichage de la fenêtre principale (`MainWindow`).

#### `core/` (Logique Métier)

Ce paquet contient la logique fondamentale de l'application, sans aucune dépendance à l'interface graphique.

*   **`settings.py` (`SettingsManager`)**: Gère le chargement et la sauvegarde des préférences de l'utilisateur depuis un fichier `settings.json` situé dans le répertoire de configuration du système (`~/.config/BlueNotebook`).
*   **`file_handler.py` (`FileHandler`)**: Fournit des méthodes statiques pour lire et écrire des fichiers, garantissant un encodage UTF-8.
*   **`markdown_parser.py` (`MarkdownParser`)**: Encapsule la bibliothèque `markdown` pour convertir le texte Markdown en HTML.
*   **`tag_indexer.py` (`TagIndexer`)** et **`word_indexer.py` (`WordIndexer`)**: Composants cruciaux pour la fonctionnalité de recherche. Ils opèrent de manière asynchrone (via `QRunnable`) pour scanner le répertoire du journal, extraire les tags (`@@tag`) et les mots, et générer des fichiers d'index (`index_tags.json`, `index_words.json`).
*   **`quote_fetcher.py` (`QuoteFetcher`)**: Récupère la "citation du jour" en scrappant le site `citations.ouest-france.fr`. Inclut un mécanisme de cache pour éviter les requêtes répétées.

#### `gui/` (Interface Graphique)

Ce paquet contient tous les widgets et fenêtres qui composent l'interface utilisateur, construits avec PyQt5.

*   **`main_window.py` (`MainWindow`)**: La classe centrale de l'application. Elle assemble tous les autres composants de l'interface, gère les menus, les actions, la barre d'état, et orchestre la communication entre les différents panneaux.
*   **`editor.py` (`MarkdownEditor`)**: Le cœur de l'expérience utilisateur. C'est un widget composite qui inclut :
    *   `QTextEditWithLineNumbers`: Un `QTextEdit` personnalisé avec affichage des numéros de ligne.
    *   `MarkdownHighlighter`: Un `QSyntaxHighlighter` qui applique une coloration syntaxique en temps réel au texte Markdown.
*   **`preview.py` (`MarkdownPreview`)**: Affiche le rendu HTML du texte Markdown en utilisant `QWebEngineView`. Il gère l'application de thèmes CSS.
*   **`navigation.py` (`NavigationPanel`)**: Le panneau latéral gauche, qui contient le calendrier pour la navigation temporelle, le champ de recherche, et les nuages de tags et de mots.
*   **`outline.py` (`OutlinePanel`)**: Affiche une arborescence cliquable des titres (H1, H2, etc.) du document en cours.
*   **`preferences_dialog.py` (`PreferencesDialog`)**: Une fenêtre complexe permettant à l'utilisateur de personnaliser en détail l'apparence (thèmes, polices, couleurs) et le comportement de l'application.
*   Autres widgets : `date_range_dialog.py` (pour les exports), `search_results_panel.py`, `tag_cloud.py`, `word_cloud.py`.

#### `integrations/` (Services Externes)

Ce paquet gère la communication avec des API ou des processus externes.

*   **`pdf_exporter.py`** et **`epub_exporter.py`**: Contiennent la logique pour convertir l'ensemble du journal en fichiers PDF ou EPUB, en utilisant respectivement `WeasyPrint` et `EbookLib`. Ils sont exécutés en arrière-plan (`QRunnable`) pour ne pas bloquer l'interface.
*   **`weather.py`**: Interroge l'API de `WeatherAPI.com` pour récupérer les données météorologiques.
*   **`youtube_video.py`**: Extrait l'ID et le titre d'une vidéo YouTube à partir de son URL.
*   **`gps_map_generator.py`**: Utilise `staticmaps` pour générer une image de carte statique et `geopy` pour obtenir le nom d'un lieu à partir de coordonnées GPS.
*   **`image_exif.py`**: Extrait les métadonnées EXIF des images (GPS, date, appareil) en utilisant `Pillow`.

## 3. Technologies et Dépendances

L'application est construite sur un ensemble de bibliothèques Python robustes et éprouvées.

*   **Langage** : Python (la version 3.13.5 est ciblée dans les scripts de lancement).
*   **Framework d'Interface Graphique** :
    *   **PyQt5** : Utilisé pour construire l'ensemble de l'interface de bureau.
    *   **PyQtWebEngine** : Utilisé pour le panneau d'aperçu HTML en temps réel.

*   **Dépendances Principales** (issues de `requirements.txt`) :
    *   `markdown` & `pymdown-extensions`: Pour la conversion du texte Markdown en HTML.
    *   `Pygments`: Pour la coloration syntaxique des blocs de code dans l'aperçu HTML.
    *   `requests`: Pour toutes les requêtes HTTP (météo, citation, vidéos YouTube).
    *   `beautifulsoup4` & `lxml`: Pour le parsing HTML (scraping de la citation du jour, traitement des exports).
    *   `appdirs`: Pour localiser de manière multiplateforme le répertoire de cache de l'application.

*   **Dépendances Optionnelles** (requises pour certaines fonctionnalités) :
    *   `WeasyPrint`: Nécessaire pour l'exportation du journal au format PDF.
    *   `EbookLib`, `Pillow`, `cairosvg`: Nécessaires pour l'exportation au format EPUB.
    *   `staticmaps`, `geopy`: Nécessaires pour la génération de cartes GPS.

## 4. Description Détaillée des Fonctionnalités

### 4.1. Cœur de l'Application (Core)

*   **Gestion de Journal Basée sur les Fichiers** : L'application est centrée sur un "répertoire de journal". Chaque entrée correspond à un fichier `AAAAMMJJ.md`. Cette approche garantit que les données de l'utilisateur sont transparentes, portables et pérennes.
*   **Indexation Asynchrone** : Au démarrage et lors de la sélection d'un journal, l'application lance des tâches de fond pour indexer tous les mots et les tags (`@@...`). Cela permet une recherche quasi-instantanée sans jamais bloquer l'interface utilisateur. Les index sont stockés dans des fichiers JSON pour des rechargements rapides.
*   **Gestion Centralisée des Paramètres** : Toutes les préférences de l'utilisateur (thèmes de couleurs, polices, visibilité des panneaux, clés API) sont gérées par la classe `SettingsManager` et stockées dans un unique fichier `settings.json`, ce qui facilite la sauvegarde et la portabilité de la configuration.

### 4.2. Interface Utilisateur (GUI)

*   **Éditeur Markdown Avancé** :
    *   **Coloration Syntaxique en Temps Réel** : Le `MarkdownHighlighter` analyse le texte au fur et à mesure de la frappe pour colorer les titres, le gras, l'italique, les listes, le code, les liens, les tags, etc.
    *   **Personnalisation Extrême** : L'utilisateur peut changer la police et la couleur de chaque élément syntaxique via la fenêtre de préférences.
    *   **Numéros de Ligne** : Une marge optionnelle affiche les numéros de ligne.
*   **Aperçu HTML en Temps Réel** :
    *   Le panneau d'aperçu se met à jour automatiquement quelques millisecondes après la modification du texte.
    *   Il utilise le même moteur de rendu qu'un navigateur moderne (`QWebEngine`), garantissant un affichage fidèle.
    *   Les thèmes CSS (inspirés de GitHub, etc.) permettent de personnaliser entièrement l'apparence de l'aperçu.
*   **Navigation Intelligente** :
    *   **Calendrier** : Met en évidence les jours où une note a été écrite, permettant un accès direct.
    *   **Nuages de Mots et de Tags** : Générés à partir des index, ils offrent une vue d'ensemble des thèmes récurrents du journal. Un clic sur un terme lance une recherche.
    *   **Recherche Plein Texte** : Le champ de recherche permet de trouver des mots ou des tags dans tout le journal. Les résultats s'affichent avec leur contexte et un clic sur un résultat ouvre le fichier correspondant directement à la bonne ligne.
*   **Panneaux Modulables** : Les panneaux de Navigation, Plan et Aperçu peuvent être affichés ou masqués (via des boutons ou les touches `F5`-`F7`) pour créer un espace de travail personnalisé.

### 4.3. Intégrations Externes

*   **Export PDF et EPUB** :
    *   Génération de documents de haute qualité incluant une page de garde, une table des matières, une pagination et une gestion correcte des images.
    *   L'export EPUB va plus loin en intégrant un index des tags cliquable et en embarquant toutes les images pour une portabilité totale.
*   **Sauvegarde et Restauration** : L'utilisateur peut créer une archive `.zip` complète de son journal et la restaurer, avec un mécanisme de sécurité qui sauvegarde le journal existant avant de l'écraser.
*   **Enrichissement de Contenu** :
    *   **Météo** : Insertion d'un bloc HTML avec les conditions météo actuelles.
    *   **Vidéo YouTube** : Insertion d'une miniature cliquable et d'un tag `@@Video` à partir d'une simple URL.
    *   **Cartes GPS** : Génération d'une carte statique à partir de coordonnées, avec recherche inversée du nom du lieu.
    *   **Données EXIF** : Extraction et formatage des métadonnées d'une photo (lieu, date, appareil) pour les insérer sous l'image.

## 5. Gestion des Données

### 5.1. Le Répertoire du Journal
C'est le dossier principal choisi par l'utilisateur. Il contient :
*   Les notes journalières au format `AAAAMMJJ.md`.
*   Un sous-dossier `images/` où sont copiées toutes les images locales insérées.
*   Les fichiers d'index générés par l'application.

### 5.2. Fichiers d'Indexation
Générés et mis à jour automatiquement dans le répertoire du journal :
*   `index_tags.json`: Un dictionnaire où chaque clé est un tag et la valeur contient le nombre d'occurrences et une liste détaillée de chaque occurrence (fichier, ligne, contexte, date).
*   `index_words.json`: Structure identique à `index_tags.json` mais pour les mots du journal.
*   `index_tags.csv` et `index_words.csv`: Des versions alternatives des index au format CSV pour une éventuelle utilisation externe.

### 5.3. Fichiers de Configuration
*   `~/.config/BlueNotebook/settings.json`: Fichier unique contenant toutes les préférences de l'utilisateur (polices, couleurs, thèmes, clés API, etc.).
*   `resources/templates/`: Contient les modèles de notes (`.md`) que l'utilisateur peut créer et utiliser.
*   `resources/themes/`: Contient les thèmes de couleurs de l'éditeur au format JSON.
*   `resources/css_preview/`: Contient les thèmes CSS pour le panneau d'aperçu.

## 6. Recommandations d'Évolution

### 6.1. Évolutions Techniques

1.  **Modernisation de la Gestion des Dépendances** : Migrer de `requirements.txt` vers un outil moderne comme [Poetry](https://python-poetry.org/) ou [PDM](https://pdm-project.org/) avec un fichier `pyproject.toml`. Cela améliorerait la gestion des dépendances, la reproductibilité des builds et la séparation des dépendances de développement.

2.  **Amélioration de la Couverture de Tests** : Le projet contient une base de tests pour les composants `core`. Il serait bénéfique de :
    *   Étendre les tests unitaires pour couvrir toute la logique métier.
    *   Introduire des tests d'intégration.
    *   Mettre en place des tests pour l'interface graphique en utilisant `pytest-qt` pour simuler des interactions utilisateur et vérifier le comportement de l'UI.

3.  **Refactoring et Typage** :
    *   Renforcer le typage statique avec `mypy` sur l'ensemble de la base de code pour réduire les erreurs à l'exécution et améliorer la lisibilité.
    *   Certaines parties de `main_window.py` sont très longues. Envisager de déléguer certaines logiques (ex: la gestion des exports, des sauvegardes) à des classes dédiées pour alléger `MainWindow` et mieux respecter le principe de responsabilité unique.

4.  **Mise en Place d'une CI/CD** : Intégrer une pipeline d'intégration continue (ex: GitHub Actions) pour automatiser l'exécution des tests, le linting (`ruff`, `black`) et le typage (`mypy`) à chaque commit.

5.  **Optimisation de l'Indexation** : L'indexation est déjà asynchrone, ce qui est excellent. Pour les journaux très volumineux, on pourrait envisager une approche de base de données (ex: SQLite avec une extension FTS5) au lieu de fichiers JSON, ce qui pourrait offrir de meilleures performances en lecture et en écriture pour les mises à jour incrémentielles.

### 6.2. Évolutions Fonctionnelles

1.  **Synchronisation Cloud** : C'est la fonctionnalité la plus demandée pour ce type d'application. Permettre aux utilisateurs de synchroniser leur répertoire de journal avec des services comme Dropbox, Google Drive ou Nextcloud augmenterait considérablement la valeur de l'application.

2.  **Application Compagnon (Mobile/Web)** : Développer une application mobile légère (ou une PWA) qui pourrait lire et éditer les fichiers `.md` du journal synchronisé via le cloud.

3.  **Améliorations de l'Éditeur** :
    *   Intégrer un correcteur orthographique.
    *   Ajouter des modes d'édition (ex: mode "Focus" qui estompe le texte non actif, mode "Machine à écrire" où la ligne active reste au centre).
    *   Support des raccourcis de type Vim/Emacs.

4.  **Système de Plugins/Extensions** : Créer une architecture de plugins pour permettre à la communauté (ou à l'utilisateur) de développer ses propres intégrations (ex: nouveaux services météo, export vers d'autres formats, etc.) sans modifier le cœur de l'application.

5.  **Chiffrement des Notes** : Proposer une option pour chiffrer les notes (soit par fichier, soit tout le journal) avec un mot de passe pour garantir la confidentialité des données.

6.  **Recherche Avancée** : Améliorer le moteur de recherche avec des opérateurs booléens (`mot1 AND mot2`, `tag:projet NOT tag:archive`), la recherche par plage de dates, etc.

## 7. Conclusion

BlueNotebook est une application de journalisation remarquablement complète et bien conçue. Son architecture modulaire, sa gestion transparente des données et la richesse de ses fonctionnalités (notamment les exports PDF/EPUB et les intégrations) en font un outil puissant.

Les recommandations techniques visent à moderniser ses fondations pour assurer sa pérennité et sa maintenabilité, tandis que les recommandations fonctionnelles proposent des pistes pour l'aligner avec les attentes des utilisateurs d'applications de prise de notes modernes. Le projet dispose d'une base solide sur laquelle capitaliser pour de futures versions.

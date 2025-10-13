# BlueNotebook



**BlueNotebook** est un éditeur de texte Markdown moderne développé en Python, conçu pour offrir une expérience d'édition fluide avec un aperçu en temps réel. L'application combine la simplicité de la syntaxe Markdown avec la puissance d'un rendu HTML professionnel.

Copyright (C) 2025 Jean-Marc DIGNE

Ce programme est un logiciel libre ; vous pouvez le redistribuer ou le modifier conformément aux termes de la Licence Publique Générale GNU telle que publiée par la Free Software Foundation ; soit la version 3 de la licence, soit (à votre choix) toute version ultérieure.

[![License GNU](https://img.shields.io/github/license/lephotographelibre/BlueNotebook)](https://www.gnu.org/licenses/>)


### Spécifications techniques

- **Langage** : Python 3.7+
- **Framework GUI** : PyQt5
- **Moteur de rendu** : QWebEngine (Chromium)
- **Parser Markdown** : python-markdown avec extensions
- **Coloration syntaxique** : Pygments
- **Architecture** : MVC (Model-View-Controller)
- **Plateforme** : Cross-platform (Windows, macOS, Linux)

---

## Architecture et choix techniques

### Paradigme architectural

L'application suit une architecture **MVC modifiée** adaptée aux applications desktop :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Model      │    │      View       │    │   Controller    │
│                 │    │                 │    │                 │
│  • FileHandler  │◄──►│  • MainWindow   │◄──►│  • MainWindow   │
│  • MarkdownParser│    │  • Editor       │    │  • Event Logic  │
│                 │    │  • Preview      │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Choix de PyQt5 vs alternatives

| Critère | PyQt5 | Tkinter | Electron | PySide6 |
|---------|-------|---------|----------|---------|
| **Performance** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Rendu HTML** | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Natif** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ |
| **Distribution** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| **Écosystème** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

**Justification** : PyQt5 a été choisi pour :
- **QWebEngine** : Moteur Chromium intégré pour rendu HTML parfait
- **Maturité** : Écosystème stable et documentation complète
- **Performance** : Applications natives, pas de VM JavaScript
- **Fonctionnalités** : Widgets avancés, système de signaux/slots

### Architecture des données

```python
# Flux de données unidirectionnel
Markdown Text (Editor) → Parser → HTML → QWebEngine (Preview)
     ↑                                            ↓
File I/O ←─────────── User Actions ──────── DOM Events
```

---

## Arborescence des fichiers

```
bluenotebook/
├── main.py                     # Point d'entrée de l'application
├── requirements.txt            # Dépendances Python
├── README.md                   # Documentation utilisateur
├── .gitignore                  # Exclusions Git
│
├── gui/                        # Interface utilisateur (Vue)
│   ├── __init__.py
│   ├── main_window.py          # Fenêtre principale et orchestration
│   ├── editor.py               # Composant éditeur de texte
│   └── preview.py              # Composant aperçu HTML
│
├── core/                       # Logique métier (Modèle)
│   ├── __init__.py
│   ├── markdown_parser.py      # Traitement Markdown → HTML
│   └── file_handler.py         # Gestion des fichiers I/O
│
├── resources/                  # Ressources statiques
│   ├── icons/                  # Icônes de l'application
│   │   ├── bluenotebook.ico    # Icône Windows
│   │   ├── bluenotebook.png    # Icône universelle
│   │   ├── bluenotebook.svg    # Icône vectorielle
│   │   └── create_icons.py     # Générateur d'icônes
│   └── styles.css              # Styles CSS (non utilisé actuellement)
│
└── tests/                      # Tests unitaires
    ├── __init__.py
    ├── test_markdown_parser.py # Tests du parser
    └── test_file_handler.py    # Tests I/O fichiers
```

### Justification de l'organisation

- **Séparation des responsabilités** : GUI, logique métier, et ressources séparées
- **Modularité** : Chaque composant peut être testé et modifié indépendamment  
- **Extensibilité** : Ajout facile de nouveaux composants GUI ou parsers
- **Maintenabilité** : Structure claire pour nouveaux développeurs

---

## Description des composants

### 1. Main Window (`gui/main_window.py`)

**Rôle** : Orchestrateur principal, gestion des événements et coordination des composants.

```python
class MainWindow(QMainWindow):
    # Responsabilités :
    # - Gestion du cycle de vie de l'application
    # - Coordination Editor ↔ Preview
    # - Menus et raccourcis clavier
    # - Gestion des fichiers (ouverture, sauvegarde)
    # - Interface avec l'OS (barre de statut, titre)
```

**Fonctionnalités clés** :
- **Timer de mise à jour** : Évite les rafraîchissements trop fréquents (300ms)
- **Gestion d'état** : Suivi des modifications, fichier actuel
- **Signaux PyQt5** : Communication asynchrone entre composants
- **Validation de fermeture** : Protection contre la perte de données

### 2. Editor (`gui/editor.py`)

**Rôle** : Éditeur de texte avec coloration syntaxique Markdown.

```python
class MarkdownEditor(QWidget):
    # Composants intégrés :
    # - QTextEdit : Zone de saisie
    # - MarkdownHighlighter : Coloration syntaxique
    # - FindDialog : Recherche et remplacement
```

**Architecture de la coloration syntaxique** :

```python
class MarkdownHighlighter(QSyntaxHighlighter):
    def highlightBlock(self, text):
        # Regex patterns pour :
        # - Titres (# ## ###)
        # - Emphases (**gras**, *italique*)  
        # - Code (`inline`, ```blocks```)
        # - Liens [text](url)
        # - Citations (> text)
        # - Listes (-, *, 1.)
```

**Optimisations** :
- **Highlighting en temps réel** : QSyntaxHighlighter intégré à QTextDocument
- **Police monospace** : Consolas/Monaco pour lisibilité du code
- **Sélection intelligente** : Préservation du contexte lors des recherches

### 3. Preview (`gui/preview.py`)

**Rôle** : Rendu HTML en temps réel avec QWebEngine.

```python
class MarkdownPreview(QWidget):
    # Pipeline de rendu :
    # Markdown → python-markdown → HTML + CSS → QWebEngine
```

**Architecture du rendu** :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Markdown      │    │   Extensions    │    │   HTML + CSS    │
│   Raw Text      │───►│   Processing    │───►│   Final Render  │
│                 │    │                 │    │                 │
│  - Headers      │    │  - Tables       │    │  - GitHub Style │
│  - Emphasis     │    │  - Code blocks  │    │  - Syntax HL    │
│  - Lists        │    │  - TOC          │    │  - Responsive   │
│  - Links        │    │  - Footnotes    │    │  - Print ready  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

**Extensions Markdown utilisées** :
- `tables` : Support des tableaux GitHub
- `fenced_code` : Blocs de code avec ```
- `codehilite` : Coloration syntaxique via Pygments
- `toc` : Table des matières automatique
- `attr_list` : Attributs HTML personnalisés
- `footnotes` : Notes de bas de page
- `sane_lists` : Parsing amélioré des listes

**CSS intégré** :
- **Reset CSS** moderne pour cohérence
- **Typography** optimisée (line-height, spacing)
- **Responsive design** pour différentes tailles
- **Print styles** pour export PDF futur
- **GitHub-like** styling pour familiarité

## Arborescence Complète des Menus

Voici une vue d'ensemble de tous les menus de l'application.

```text
📁 Fichier
├── 📄 Nouveau (Ctrl+N)
├── 📂 Ouvrir (Ctrl+O)
├── 📓 Ouvrir Journal
├── ---
├── 💾 Sauvegarder (Ctrl+S)
├── 💾 Sauvegarder sous... (Ctrl+Shift+S)
├── ---
├── 🌐 Exporter HTML...
├── ---
└── 🚪 Quitter (Ctrl+Q)

✏️ Edition
├── ↩️ Annuler (Ctrl+Z)
├── ↪️ Rétablir (Ctrl+Y)
├── ---
└── 🔍 Rechercher (Ctrl+F)

👁️ Affichage
└── 👁️ Basculer l'aperçu (F5)

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
│   ├── ---
│   ├── ➖ Ligne Horizontale
│   ├── ▦ Tableau
│   ├── 💬 Citation
│   ├── ✨ Citation du jour
│   ├── ---
│   ├── 🏷️ Tag (@@)
│   └── 🕒 Heure
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
├── ---
└── 🧹 RaZ (Effacer le formatage)

❓ Aide
├── 🌐 Documentation en ligne
└── ℹ️ À propos

```

## Gestion des Tags dans BlueNotebook

Le système de tags est une fonctionnalité centrale de BlueNotebook, conçue pour organiser et retrouver facilement l'information à travers l'ensemble de votre journal. Il repose sur trois piliers : une syntaxe simple, une coloration syntaxique pour une identification visuelle immédiate, et un puissant système d'indexation asynchrone.

#### Création et Syntaxe des Tags

La création d'un tag est volontairement simple et intuitive pour ne pas interrompre le flux d'écriture.

*   **Syntaxe** : Pour créer un tag, il suffit de préfixer un mot avec un double arobase `@@`, sans espace. Le mot peut contenir des lettres, des chiffres et le tiret bas (`_`).
*   **Exemples** :
    *   `@@projet-alpha`
    *   `@@idee`
    *   `@@reunion_importante`
    *   `@@a_lire`

Cette syntaxe a été choisie pour éviter les conflits avec le Markdown standard et les usages courants du simple arobase (`@`) ou du dièse (`#`).


#### 2. Coloration Syntaxique

Pour qu'un tag soit immédiatement identifiable, il est mis en évidence à la fois dans l'éditeur et dans l'aperçu HTML.

*   **Dans l'Éditeur** : La classe `MarkdownHighlighter` (dans `gui/editor.py`) utilise une expression régulière (`r"@@(\w{2,})\b"`) pour détecter les tags en temps réel. Chaque tag identifié est instantanément coloré en rouge, le rendant visible au milieu du texte.
*   **Dans l'Aperçu HTML** : Pour une expérience cohérente, les tags sont également stylisés dans l'aperçu. Cela est réalisé via une extension Markdown personnalisée qui transforme la syntaxe `@@tag` en une balise HTML, par exemple `<span class="tag">tag</span>`. Une règle CSS est ensuite appliquée à cette classe pour la colorer en rouge, assurant une correspondance visuelle parfaite avec l'éditeur.

#### 3. Le Processus d'Indexation Asynchrone

C'est le cœur du système. Pour permettre une recherche rapide sur l'ensemble du journal, une indexation de tous les tags est réalisée en arrière-plan au démarrage de l'application.

*   **Déclenchement** : L'indexation est lancée automatiquement au démarrage de BlueNotebook et chaque fois que le répertoire du journal est modifié.
*   **Asynchronisme** : Le processus s'exécute dans un thread séparé (`QThreadPool`), grâce à la classe `TagIndexer` qui hérite de `QRunnable`. Cela garantit que l'interface utilisateur reste fluide et réactive, même si l'indexation d'un grand nombre de notes prend du temps.
*   **Processus d'Indexation** :
    1.  Le `TagIndexer` scanne tous les fichiers `.md` présents dans le répertoire du journal.
    2.  Pour chaque fichier, il lit le contenu ligne par ligne.
    3.  Il utilise une expression régulière pour trouver toutes les occurrences de tags (`@@...`).
    4.  Pour chaque tag trouvé, il extrait le tag lui-même, le nom du fichier, et un "contexte" (les 40 caractères qui suivent le tag) pour donner un aperçu de son utilisation.
    5.  Toutes ces informations sont collectées et agrégées.

*   **Notification** : Une fois l'indexation terminée, un signal est émis. L'interface principale le reçoit et met à jour la barre de statut avec un message de confirmation, comme : `✅ Index Tags Terminé: 7 tags uniques trouvés.`.

#### 4. Formats des Fichiers d'Index

À la fin du processus, le `TagIndexer` génère trois fichiers d'index dans le répertoire du journal. Ces fichiers servent de cache pour les futures fonctionnalités de recherche et d'analyse.

1.  **`index_tags.txt` (Format Texte brut)**
    Ce fichier est une liste simple de toutes les occurrences de tags, facile à lire ou à parser avec des scripts simples.
    *   **Format** : `@@tag++contexte du tag++nom_du_fichier.md`
    *   **Exemple** :
        ```
        @@projet++avancement sur le projet BlueNotebook++20240927.md
        @@idee++une nouvelle fonctionnalité pour l'app++20240927.md
        @@projet++réunion de suivi pour le projet Alpha++20240928.md
        ```

2.  **`index_tags.csv` (Format CSV)**
    Ce format est idéal pour une importation dans des tableurs ou des bases de données.
    *   **Structure** : `tag,context,filename,date`
    *   **Exemple** :
        ```csv
        tag,context,filename,date
        @@projet,"avancement sur le projet BlueNotebook",20240927.md,2024-09-27
        @@idee,"une nouvelle fonctionnalité pour l'app",20240927.md,2024-09-27
        @@projet,"réunion de suivi pour le projet Alpha",20240928.md,2024-09-28
        ```

3.  **`index_tags.json` (Format JSON)**
    Ce format structuré est le plus puissant. Il regroupe les informations par tag, ce qui est parfait pour alimenter une interface de recherche avancée.
    *   **Structure** : Un dictionnaire où chaque clé est un tag. La valeur associée contient le nombre d'occurrences et une liste de détails pour chaque occurrence.
    *   **Exemple** :
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

## Aide en ligne

L'application inclut une documentation en ligne accessible via le menu `Aide -> Documentation en ligne`.
-   Le contenu de l'aide est un fichier HTML (`bluenotebook_aide_en_ligne.html`) situé dans `resources/html/`.
-   Un clic sur l'option de menu ouvre ce fichier dans le navigateur web par défaut de l'utilisateur.
-   Cette approche permet de mettre à jour facilement la documentation sans recompiler l'application.


## Citation du jour

Au lancement, l'application récupère une "citation du jour" depuis le site `citations.ouest-france.fr` en utilisant des techniques de web scraping (avec les bibliothèques `requests` et `BeautifulSoup`).

-   **Affichage** : La citation et son auteur sont présentés dans une boîte de dialogue modale au démarrage.
-   **Insertion** : L'utilisateur peut insérer cette citation dans l'éditeur via le menu `Formater -> Insérer -> Citation du jour`. Elle sera formatée en tant que citation Markdown (`>`).
-   **Dépendances** : Cette fonctionnalité ajoute les dépendances `requests` et `beautifulsoup4` au projet.

### Scripts de lancement

-   **`run_bluenotebook.sh` (Linux/macOS)** :
    -   Active l'environnement virtuel.
    -   Vérifie et installe les dépendances de `requirements.txt`.
    -   Lance l'application `main.py` en transmettant les arguments.



---

## Conclusion

BlueNotebook représente une architecture moderne et extensible pour un éditeur Markdown. Les choix techniques (PyQt5, QWebEngine, python-markdown) offrent un équilibre optimal entre performance, fonctionnalités et maintenabilité.

L'architecture modulaire permet une évolution progressive vers un écosystème complet d'édition technique, tout en conservant la simplicité d'usage qui fait le succès des éditeurs Markdown.

Les évolutions proposées transformeraient BlueNotebook d'un éditeur simple vers une plateforme complète de documentation et collaboration technique, positionnée entre des outils comme Typora (simplicité) et Obsidian (fonctionnalités avancées).
 
---
 
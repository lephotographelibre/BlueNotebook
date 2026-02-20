# BlueNotebook — Architecture

> **Version** : 4.2.12 | **Python** 3.11 | **Licence** GPL v3
> Coller ce fichier en début de conversation pour donner le contexte à l'assistant.

---

## 1. Stack technique

| Catégorie | Lib / Version |
|---|---|
| GUI | PyQt5 == 5.15.11, PyQtWebEngine == 5.15.7 |
| Markdown | `markdown`, `Pygments`, `pymdown-extensions` |
| HTML/Web | `beautifulsoup4`, `readability-lxml`, `markdownify` |
| Export PDF | `WeasyPrint`, `PyMuPDF`, `pycairo`, `cairosvg` |
| Export EPUB | `EbookLib`, `Pillow == 9.5.0` |
| Réseau/API | `requests`, `validators` |
| Géolocalisation | `geopy`, `gpxpy`, `py-staticmaps` |
| YouTube | `youtube-transcript-api` |
| i18n | Qt Linguist (`pylupdate5` → `.ts` → `lrelease` → `.qm`) |

---

## 2. Structure des dossiers

```
bluenotebook/
├── main.py                         # Point d'entrée : locale, fonts, QApplication, MainWindow
│
├── core/                           # Logique métier pure (sans GUI)
│   ├── settings.py                 # SettingsManager : config JSON (~/.config/BlueNotebook/settings.json)
│   ├── file_handler.py             # Lecture/écriture .md (UTF-8, fallback latin-1)
│   ├── markdown_parser.py          # Markdown → HTML (tables, fenced code, TOC, codehilite)
│   ├── tag_indexer.py              # TagIndexer (QRunnable) : extraction @@TAGS → index_tags.json
│   ├── quote_fetcher.py            # Citation du jour via ZenQuotes API
│   ├── journal_backup_worker.py    # Sauvegarde ZIP asynchrone du journal
│   └── journal_restore_worker.py   # Restauration ZIP asynchrone
│
├── gui/                            # Composants Qt
│   ├── main_window.py              # ★ MainWindow : orchestrateur central (~4 166 lignes)
│   ├── editor.py                   # MarkdownEditor : éditeur texte + numéros de lignes + coloration
│   ├── preview.py                  # MarkdownPreview : rendu HTML (QWebEngineView)
│   ├── notes_panel.py              # NotesPanel : arbre fichiers + couleurs de dossiers
│   ├── outline.py                  # OutlinePanel : hiérarchie des titres (cliquable)
│   ├── navigation.py               # NavigationPanel : calendrier + recherche tags
│   ├── tag_cloud.py                # TagCloudPanel : nuage de tags visuel
│   ├── search_results_panel.py     # Résultats de recherche par tag
│   ├── epub_reader_panel.py        # Lecteur EPUB intégré (QWebEngineView + epub://)
│   ├── pdf_viewer.py               # Lecteur PDF intégré (PyMuPDF)
│   ├── preferences_dialog.py       # Préférences : couleurs, polices, thèmes, intégrations
│   ├── first_start.py              # Assistant de premier démarrage
│   ├── new_note_dialog.py          # Création note : choix template
│   ├── new_journal_dialog.py       # Création / ouverture journal
│   ├── open_journal.py             # Sélecteur de journal existant
│   ├── import_file_dialog.py       # Import fichiers externes dans le journal
│   ├── date_range_dialog.py        # Sélection plage de dates (export)
│   ├── on_line_help.py             # Fenêtre d'aide HTML/MD
│   ├── internal_links_handler.py   # Gestion liens internes (.md, .pdf, images, .html)
│   ├── bookmark_handler.py         # Insertion de marque-pages dans le texte
│   ├── backup_handler.py           # UI backup/restore (barre de progression)
│   └── custom_widgets.py           # Widgets spéciaux (CenteredStatusBarLabel…)
│
├── integrations/                   # Services externes (tous asynchrones via QRunnable)
│   ├── weather.py                  # WeatherAPI.com → insert météo + emojis
│   ├── sun_moon.py                 # Lever/coucher soleil, phases de lune
│   ├── youtube_video.py            # Détails + transcription YouTube
│   ├── google_books.py             # Recherche ISBN : Google Books + fallback Open Library
│   ├── url_converter.py            # URL → snippet Markdown (titre, description, image)
│   ├── url_to_markdown_handler.py  # UI pour coller une URL
│   ├── image_markdown_handler.py   # Insertion image + extraction EXIF/GPS
│   ├── image_exif.py               # Parsing données EXIF
│   ├── gps_map_generator.py        # Carte statique PNG depuis lat/lon (py-staticmaps)
│   ├── gps_map_handler.py          # Gestion coordonnées GPS
│   ├── gpx_trace_generator.py      # Génération fichiers GPX
│   ├── pdf_exporter.py             # Export journal → PDF (WeasyPrint, plage de dates)
│   ├── pdf_converter.py            # Utilitaires conversion PDF
│   └── epub_exporter.py            # Export journal → EPUB (couverture, métadonnées)
│
├── i18n/
│   ├── bluenotebook_en.ts/.qm      # Traductions anglaises
│   └── bluenotebook_fr.ts/.qm      # Traductions françaises
│
└── resources/
    ├── fonts/                      # NotoSans + NotoColorEmoji (TTF embarqués)
    ├── icons/                      # Icônes PNG/ICO
    ├── images/                     # Logos UI
    ├── themes/                     # 14 thèmes JSON (Brique, Turquoise, Dark…)
    ├── templates/                  # Templates Markdown nouvelles notes ([Fr]…, [en-US]…)
    ├── css_preview/                # CSS rendu prévisualisation (default_preview.css)
    ├── css_pdf/                    # CSS export PDF (default_pdf.css, theme-minimaliste.css)
    └── html/                       # Documentation aide (online_help.html/md, aide_en_ligne.html/md)

dev/
├── scripts/                        # Scripts de build, traduction, déploiement
└── tests/                          # Tests manuels (non automatisés)

docs/changelog.md
flatpak/          windows_installer/          appimage/
```

---

## 3. Format du journal (données)

```
mon_journal/
├── 20260219.md          # Notes quotidiennes (YYYYMMDD.md)
├── sous-dossier/
│   └── note-libre.md    # Notes avec nom libre
├── images/              # Images insérées
├── attachments/         # Fichiers joints
├── gpx/                 # Traces GPS
└── index_tags.json      # Index des @@TAGS (généré automatiquement)
```

**Format index_tags.json** :
```json
[{"tag": "@@TODO", "context": "Finir la feature", "filename": "20260219.md", "line": 12}]
```

**Tags** : syntaxe `@@NOM` dans le texte. Normalisés : `@@météo` → `@@METEO`.
**Pas de frontmatter YAML** — Markdown pur + @@tags.

---

## 4. Flux de données principaux

### 4.1 Création / sauvegarde d'une note
```
Action utilisateur
  → main_window.py : new_file() / save_file()
  → new_note_dialog.py : choix template
  → core/file_handler.py : write_file(path, content)   ← écriture .md
  → core/tag_indexer.py : TagIndexer.run()              ← reindex (thread pool)
  → gui/tag_cloud.py + search_results_panel.py          ← mise à jour UI
```

### 4.2 Indexation des tags
```
TagIndexer (QRunnable, exécuté en arrière-plan)
  → Parcourt tous les .md du journal
  → Regex @@\w{2,} sur chaque ligne
  → Normalise (suppr. accents, uppercase)
  → Écrit index_tags.json
  → Signal finished() → StatusBar + TagCloud
```

### 4.3 Prévisualisation Markdown
```
editor.py : textChanged → QTimer (debounce ~300ms)
  → core/markdown_parser.py : parse(content) → HTML
  → gui/preview.py : setHtml(html, baseUrl)
  → CSS de css_preview/ appliqué
  → Liens internes détectés → internal_links_handler.py
```

### 4.4 Démarrage de l'application
```
main.py : main()
  1. SettingsManager → charge settings.json
  2. Détection locale (env var → settings → "en_US")
  3. Fontconfig (Flatpak/Linux)
  4. QApplication + polices NotoSans
  5. QTranslator → charge .qm correspondant
  6. Premier démarrage ? → FirstStartWindow
  7. Args CLI : --journal /chemin/
  8. MainWindow() → show() → app.exec_()
```

---

## 5. Conventions de code

### Traduction i18n (règles strictes)

```python
# 1. Chaîne simple
self.tr("Texte simple")

# 2. Avec arguments (une ligne)
self.tr("Fichier {name} ouvert").format(name=filename)

# 3. Multi-lignes SANS arguments
self.tr(
    "Long texte "
    "sur plusieurs lignes."
)

# 4. Multi-lignes AVEC arguments → variable intermédiaire
msg = self.tr(
    "Le dossier « {dir} » existe déjà.\n"
    "Continuer quand même ?"
)
msg = msg.format(dir=path.name)

# 5. Hors QWidget → classe de contexte
class MonModuleContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("MonModuleContext", text)

MonModuleContext.tr("Message").format(var=val)
```

### En-tête obligatoire pour tout nouveau fichier Python
```python
"""
# Copyright (C) 2026 Jean-Marc DIGNE
# [licence GPL v3 — voir CLAUDE.md pour le texte complet]

Description concise du rôle du fichier."""
```

### Patterns récurrents
- **Workers asynchrones** : `QRunnable` + `QThreadPool` pour toute opération longue
- **Signaux** : classes `*Signals(QObject)` avec `pyqtSignal` pour communiquer hors thread
- **Contexte i18n** : classe `*Context` avec méthode statique `tr()` dans les modules sans GUI
- **Accès settings** : `SettingsManager` partagé, accès par `settings.get("section.key")`
- **Pas de tests automatisés** (cf. CLAUDE.md : "Pas de générations de tests")

---

## 6. Configuration (settings.json)

**Chemin** : `~/.config/BlueNotebook/settings.json`
**Classe** : `core/settings.py::SettingsManager`

Sections principales :
```
app.language            → "en_US" | "fr_FR"
editor.*                → police, taille, couleurs syntaxe
preview.css_theme       → fichier CSS prévisualisation
ui.*                    → visibilité des panneaux
integrations.*          → WeatherAPI key, villes, YouTube…
notes.folder_colors     → dict {chemin → couleur hex}
pdf.*                   → dernier auteur, titre, répertoire
backup.last_directory   → dernier répertoire de sauvegarde
```

---

## 7. Points d'entrée fréquemment modifiés

| Fichier | Quand le toucher |
|---|---|
| `gui/main_window.py` | Ajouter menu, action, raccourci, intégration |
| `gui/editor.py` | Modifier l'éditeur, la coloration syntaxique |
| `gui/preferences_dialog.py` | Ajouter une option de configuration |
| `core/settings.py` | Ajouter un nouveau paramètre |
| `core/tag_indexer.py` | Modifier le comportement des @@tags |
| `integrations/` | Ajouter / modifier une intégration externe |
| `i18n/bluenotebook_*.ts` | Mettre à jour les traductions |
| `resources/templates/` | Ajouter / modifier un template de note |
| `resources/themes/*.json` | Ajouter un thème de couleurs |
| `resources/css_preview/` | Modifier le rendu de prévisualisation |

---

## 8. Commandes de développement utiles

```bash
# Lancer l'application
python bluenotebook/main.py

# Lancer avec un journal spécifique
python bluenotebook/main.py --journal /chemin/vers/journal

# Mettre à jour les fichiers de traduction
cd bluenotebook
pylupdate5 $(find . -name "*.py") -ts i18n/bluenotebook_fr.ts
pylupdate5 $(find . -name "*.py") -ts i18n/bluenotebook_en.ts

# Compiler les traductions
lrelease i18n/bluenotebook_fr.ts
lrelease i18n/bluenotebook_en.ts

# Scripts de build (depuis dev/scripts/)
./dev/scripts/update_translations.sh
./dev/scripts/update_version.sh
```

---

*Généré le 2026-02-19 — BlueNotebook v4.2.12*

# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown moderne et professionnel développé en Python avec PyQt5 et QWebEngine.

## ✨ Fonctionnalités

- ✏️ **Édition avancée** avec coloration syntaxique Markdown
- 👀 **Aperçu HTML en temps réel** avec rendu parfait (QWebEngine)
- 💾 **Gestion de fichiers** complète (nouveau, ouvrir, sauvegarder)
- 🔍 **Recherche et remplacement** intégrés
- 📊 **Statistiques du document** (lignes, mots, caractères)
- 📤 **Export HTML** avec CSS professionnel
- 🌐 **Support complet Markdown** (tables, code, citations, etc.)
- 🎨 **Interface moderne** avec PyQt5
- 📋 **Table des matières** automatique
- ⌨️ **Raccourcis clavier** intuitifs

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- PyQt5 et PyQtWebEngine

### Installation rapide

1. **Créer le projet** :
```bash
# Exécuter le script de génération
./setup_bluenotebook.sh
cd bluenotebook
```

2. **Installer les dépendances** :
```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt
```

3. **Lancer l'application** :
```bash
python main.py
```

### Installation manuelle des dépendances

```bash
pip install PyQt5 PyQtWebEngine markdown pymdown-extensions Pygments
```

## 🎯 Utilisation

### Interface principale
- **Zone d'édition** (gauche) : Éditeur avec coloration syntaxique
- **Zone d'aperçu** (droite) : Rendu HTML en temps réel
- **Barre de statut** : Informations sur le fichier et statistiques

### Raccourcis clavier

| Raccourci | Action |
|-----------|--------|
| `Ctrl+N` | Nouveau fichier |
| `Ctrl+O` | Ouvrir un fichier |
| `Ctrl+S` | Sauvegarder |
| `Ctrl+Shift+S` | Sauvegarder sous... |
| `Ctrl+Q` | Quitter |
| `Ctrl+Z` | Annuler |
| `Ctrl+Y` | Rétablir |
| `Ctrl+F` | Rechercher |
| `F5` | Basculer l'aperçu |

### Syntaxe Markdown supportée

```markdown
# Titres
## Sous-titres
### Titres de niveau 3

**Gras** et *italique*

`Code inline` et blocs de code :
```python
def hello():
    print("Hello BlueNotebook!")
```

> Citations
> sur plusieurs lignes

- Listes à puces
- Avec sous-éléments
  - Comme ça

1. Listes numérotées
2. Deuxième élément

| Tables | Colonnes |
|--------|----------|
| Data   | Values   |

[Liens](https://example.com) et ![Images](image.png)

---

Règles horizontales et plus !
```

## 🏗️ Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur PyQt5
│   ├── __init__.py
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur avec coloration syntaxique
│   └── preview.py       # Aperçu HTML avec QWebEngine
├── core/                # Logique métier
│   ├── __init__.py
│   ├── markdown_parser.py  # Gestionnaire Markdown
│   └── file_handler.py     # Gestionnaire de fichiers
├── resources/           # Ressources
│   └── styles.css

# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown moderne et professionnel développé en Python avec PyQt5 et QWebEngine. *aaa*

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

```bash
# Créer un environnement virtuel (recommandé)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\\Scripts\\activate   # Windows

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
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

## 🛠️ Développement

### Tests

```bash
# Lancer tous les tests
pytest tests/

# Tests avec couverture
pytest tests/ --cov=.
```

### Personnalisation

- **CSS de l'aperçu** : Modifier `gui/preview.py`
- **Extensions Markdown** : Modifier `setup_markdown()` dans `gui/preview.py`
- **Interface** : Modifier les fichiers dans `gui/`

## 🐛 Dépannage

### Problèmes courants

**PyQt5 ne s'installe pas** :
```bash
# Ubuntu/Debian
sudo apt-get install python3-pyqt5 python3-pyqt5.qtwebengine

# macOS avec Homebrew
brew install pyqt5

# Windows : utiliser pip normalement
pip install PyQt5 PyQtWebEngine
```

## 📄 Licence

MIT License

---

**BlueNotebook** - Un éditeur Markdown moderne pour tous vos besoins d'écriture ! 🔵📓

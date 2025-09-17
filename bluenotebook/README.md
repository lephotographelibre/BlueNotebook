# BlueNotebook - Éditeur Markdown Python

Un éditeur de texte Markdown simple et efficace développé en Python avec Tkinter.

## Fonctionnalités

- ✏️ Édition de fichiers Markdown
- 👀 Aperçu en temps réel
- 💾 Sauvegarde et ouverture de fichiers
- ⌨️ Raccourcis clavier
- 🎨 Interface utilisateur intuitive

## Installation

1. Cloner le projet :
```bash
git clone <votre-repo>
cd bluenotebook
```

2. Installer les dépendances :
```bash
pip install -r requirements.txt
```

3. Lancer l'application :
```bash
python main.py
```

## Utilisation

### Raccourcis clavier

- `Ctrl+N` : Nouveau fichier
- `Ctrl+O` : Ouvrir un fichier
- `Ctrl+S` : Sauvegarder
- `Ctrl+Q` : Quitter

### Structure du projet

```
bluenotebook/
├── main.py              # Point d'entrée
├── gui/                 # Interface utilisateur
│   ├── main_window.py   # Fenêtre principale
│   ├── editor.py        # Éditeur de texte
│   └── preview.py       # Aperçu HTML
├── core/                # Logique métier
│   ├── markdown_parser.py
│   └── file_handler.py
├── resources/           # Ressources
│   └── styles.css
└── tests/              # Tests unitaires
```

## Développement

### Ajouter des fonctionnalités

1. **Nouvelles extensions Markdown** : Modifier `core/markdown_parser.py`
2. **Améliorer l'UI** : Modifier les fichiers dans `gui/`
3. **Export** : Ajouter de nouvelles fonctions dans `core/`

### Tests

```bash
pytest tests/
```

## Roadmap

- [ ] Coloration syntaxique avancée
- [ ] Thèmes personnalisables
- [ ] Export PDF
- [ ] Plugin system
- [ ] Mode sombre
- [ ] Recherche et remplacement

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir des issues ou soumettre des pull requests.

## Licence

MIT License

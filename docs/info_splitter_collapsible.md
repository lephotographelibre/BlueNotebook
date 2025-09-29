# Amélioration de l'Interface : Le QSplitter Rétractable

Ce que vous décrivez est une excellente idée pour améliorer l'ergonomie de l'interface. Le composant graphique que vous cherchez s'appelle un **`QSplitter`** en PyQt.

Bonne nouvelle : votre application **BlueNotebook l'utilise déjà** pour séparer les différents panneaux !

1.  Un premier `QSplitter` sépare le panneau de **Navigation** (gauche), le panneau **Plan du document** (milieu), et la zone principale (éditeur + aperçu).
2.  Un second `QSplitter` sépare l'**Éditeur** de l'**Aperçu HTML**.

Les "poignées" (handles) que vous voyez entre ces panneaux sont les contrôles de ce `QSplitter`.

### Ce que vous pouvez faire

Vous pouvez déjà utiliser ces poignées pour redimensionner les panneaux. De plus, il est possible de les "fermer" (réduire à une taille nulle) en double-cliquant dessus ou en les faisant glisser complètement sur le côté.

### Amélioration : Ajouter des boutons de fermeture sur les poignées

Pour rendre cette fonctionnalité plus évidente, comme dans des logiciels comme LibreOffice ou de nombreux IDE, nous pouvons ajouter de petits boutons (flèches) directement sur la poignée du `QSplitter`. Un clic sur ces boutons permettra de masquer ou de réafficher le panneau adjacent.

Voici comment nous pouvons modifier le code pour obtenir ce comportement.

#### 1. Modification du `QSplitter` dans `main_window.py`

Nous allons créer une classe personnalisée `CollapsibleSplitter` qui hérite de `QSplitter` et qui ajoute ces boutons.

```python
class CollapsibleSplitterHandle(QSplitterHandle):
    """Poignée de splitter avec des boutons pour réduire/restaurer les panneaux."""

    def __init__(self, orientation, parent):
        super().__init__(orientation, parent)
        self.setChildrenCollapsible(False)

        layout = QHBoxLayout(self) if orientation == Qt.Horizontal else QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.button_left = QPushButton(self)
        self.button_right = QPushButton(self)

        if orientation == Qt.Horizontal:
            self.button_left.setArrowType(Qt.LeftArrow)
            self.button_right.setArrowType(Qt.RightArrow)
            layout.addWidget(self.button_left)
            layout.addStretch()
            layout.addWidget(self.button_right)
        else:  # Vertical
            self.button_left.setArrowType(Qt.UpArrow)
            self.button_right.setArrowType(Qt.DownArrow)
            layout.addWidget(self.button_left)
            layout.addStretch()
            layout.addWidget(self.button_right)

        self.button_left.setFixedSize(12, 24)
        self.button_right.setFixedSize(12, 24)

        self.button_left.clicked.connect(self.collapse_left)
        self.button_right.clicked.connect(self.collapse_right)

    def collapse_left(self):
        # ... (logique pour réduire/restaurer le panneau de gauche)

    def collapse_right(self):
        # ... (logique pour réduire/restaurer le panneau de droite)

class CollapsibleSplitter(QSplitter):
    def createHandle(self):
        return CollapsibleSplitterHandle(self.orientation(), self)
```

### Explication des changements

1.  **`CollapsibleSplitterHandle`** : C'est une nouvelle classe qui représente la "poignée" entre deux panneaux. Elle contient deux `QPushButton` qui, au clic, redimensionnent les panneaux pour en masquer un.
2.  **`CollapsibleSplitter`** : C'est notre nouveau `QSplitter` amélioré. Il surcharge la méthode `createHandle()` pour dire à Qt d'utiliser notre poignée personnalisée au lieu de celle par défaut.
3.  **Mise à jour dans `setup_ui`** : Il suffit de remplacer `QSplitter` par `CollapsibleSplitter` lors de la création des splitters.
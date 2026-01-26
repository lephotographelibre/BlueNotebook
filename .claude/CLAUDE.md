# Bluenotebook information

Bluenotebook est une application Python (3.11) PyQt5==5.15.11 PyQtWebEngine==5.15.7. Cette application est traduite en Français et en anglais

## Règles de codage générales

- Pas de générations de tests

## Règles de codage Python pour la traduction i18n

Pour PyQt5 et `pylupdate5`, voici les recommandations :

### Format recommandé : `.format()` avec marqueurs nommés

**Pourquoi ?**
- `pylupdate5` gère mieux `.format()` que `.arg()`
- Les marqueurs nommés (`{variable}`) sont plus lisibles et maintenables
- Évite les erreurs d'ordre des arguments
- Compatible avec les outils de traduction modernes

### Règles d'encapsulation
Je suis entrain de traduire mon application python qt5 avec pylupdate5. j'ai défini les regles d'encapsulation des chainnes de caractères avec les quatres regles. peux tu les appliquer au fichier gui/search_results_panel.py tu le sauvegarde avant avec l'extension ;save. tu me listeras toutes les encapsulations réalisées dans ce fichier

### 1. **Chaînes simples**
```python
self.tr("Texte simple")
```

### 2. **Chaînes avec arguments (une ligne)**
```python
self.tr("Le fichier {filename} est dans {path}").format(filename=filename, path=path)
```

### 3. **Chaînes multi-lignes SANS arguments**
```python
self.tr(
    "Ceci est un long texte "
    "qui continue sur plusieurs lignes "
    "mais sans variables."
)
```

### 4. **Chaînes multi-lignes AVEC arguments**
**Méthode recommandée :** Utilisez une variable intermédiaire
```python
message = self.tr(
    "Le répertoire « {dirname} » existe déjà et n'est pas vide.\n"
    "Voulez-vous quand même l'utiliser ?"
)
message = message.format(dirname=journal_path.name)
```


### 5. création d'une classe de contexte dans le cas ou il n'y a pas  de classe QWidget,
 
 par exemple pour un fichier `amazonbook.py` --> classe de contexte `AmazonBooksContext`
```python
class AmazonBooksContext:
    @staticmethod
    def tr(text):
        return QCoreApplication.translate("AmazonBooksContext", text)
```

et ensuite utliser cette classe de contexte pour encapsuler les messages en utilisant le nom de la classe de contexte au lieu de self.

```python
publisher_label=AmazonBooksContext.tr("Éditeur :"),
```

Les regles pour les f*strings s'appliquent également. Exemple:

```python
   resume_more_link_markdown = AmazonBooksContext.tr("[{plus}]({url})").format( plus=en_lire_plus, url=product_url)

```

## En-tête de fichiers Python

**IMPORTANT** : Tous les nouveaux fichiers Python créés doivent obligatoirement commencer par l'en-tête suivant :

```python
"""
# Copyright (C) 2026 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

DESCRIPTIF DES FONCTIONS DE CE SCRIPT."""
```

**Note** : Remplacer "DESCRIPTIF DES FONCTIONS DE CE SCRIPT" par une description concise du rôle du fichier.

**Exemple** :
```python
"""
# Copyright (C) 2026 Jean-Marc DIGNE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

Module de gestion de l'ouverture et du changement de journal."""

import zipfile
from pathlib import Path
# ... reste du code
```

##
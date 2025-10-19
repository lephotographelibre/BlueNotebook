# Issue #22 Application d'un thème sombre pour les boîtes de dialogue dans BlueNotebook

## Problème
Lors de l'utilisation d'un thème sombre, certaines boîtes de dialogue (`QDialog`, `QFileDialog`, `QInputDialog`) deviennent illisibles car elles ne respectent pas le thème sombre du système. Cela affecte les boîtes de dialogue pour :
- Insérer une image HTML ou Markdown (sélection d'une image).
- Insérer un lien Markdown.
- Sélectionner un fichier via un sélecteur de fichiers.

## Solution
Pour garantir que les boîtes de dialogue respectent le thème sombre du système, nous utilisons la bibliothèque `darkdetect` pour détecter si le système est en mode sombre et appliquons une palette sombre personnalisée (`QDarkPalette`) aux boîtes de dialogue et sélecteurs de fichiers. Voici les modifications apportées aux fichiers concernés (`date_range_dialog.py`, `main_window.py`, et `editor.py`).

### Étapes générales
1. **Installer `darkdetect`** :
   - Exécutez `pip install darkdetect` pour permettre la détection du thème système.
2. **Définir une palette sombre** :
   - Créer une classe `QDarkPalette` dérivée de `QPalette` pour définir les couleurs adaptées au mode sombre.
3. **Appliquer la palette aux boîtes de dialogue** :
   - Dans chaque constructeur de `QDialog` (par exemple, `DateRangeDialog`, `NewFileDialog`, `GpsInputDialog`, `ImageSourceDialog`), vérifier si le mode sombre est actif avec `darkdetect.isDark()` et appliquer la palette sombre si nécessaire.
4. **Appliquer la palette aux sélecteurs de fichiers** :
   - Modifier les appels à `QFileDialog.getOpenFileName` ou `getSaveFileName` pour utiliser une instance de `QFileDialog`, permettant d'appliquer la palette sombre et, si nécessaire, désactiver les dialogues natifs avec `DontUseNativeDialog` pour garantir l'application de la palette.
5. **Appliquer la palette aux dialogues d'entrée** :
   - Modifier les appels à `QInputDialog.getText` ou `getInt` pour utiliser une instance de `QInputDialog`, permettant d'appliquer la palette sombre.

### Code modifié pour `date_range_dialog.py`
Le fichier `date_range_dialog.py` a été mis à jour pour inclure la détection du thème sombre et appliquer une palette sombre à la boîte de dialogue `DateRangeDialog` ainsi qu'au sélecteur de fichiers utilisé dans `_browse_for_image`.

```python
# Copyright (C) 2025 Jean-Marc DIGNE
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

from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QDialogButtonBox,
    QFormLayout,
    QDateEdit,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QFileDialog,
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QPalette, QColor

try:
    import darkdetect
except ImportError:
    darkdetect = None

WHITE =     QColor(255, 255, 255)
BLACK =     QColor(0, 0, 0)
RED =       QColor(255, 0, 0)
PRIMARY =   QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY =  QColor(42, 130, 218)

def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())

class QDarkPalette(QPalette):
    """Dark palette for a Qt application meant to be used with the Fusion theme."""
    def __init__(self, *__args):
        super().__init__(*__args)

        # Set all the colors based on the constants in globals
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        """Static method to set the tooltip stylesheet to a `QtWidgets.QApplication`."""
        app.setStyleSheet("QToolTip {"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        """Set the Fusion theme and this palette to a `QtWidgets.QApplication`."""
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)

class DateRangeDialog(QDialog):
    """
    Boîte de dialogue pour sélectionner une plage de dates.
    """

    def __init__(
        self,
        start_date_default: QDate,
        end_date_default: QDate,
        min_date: QDate,
        max_date: QDate,
        default_title: str,
        default_cover_image: str,
        default_author: str,
        parent=None,
    ):
        super().__init__(parent)
        if darkdetect and darkdetect.isDark():
            self.setPalette(QDarkPalette())
        self.setWindowTitle("Options d'exportation du journal PDF")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateRange(min_date, max_date)
        self.start_date_edit.setDate(start_date_default)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDateRange(min_date, max_date)
        self.end_date_edit.setDate(end_date_default)

        self.title_edit = QLineEdit(self)
        self.title_edit.setText(default_title)

        self.author_edit = QLineEdit(self)
        self.author_edit.setText(default_author)

        # Champ pour l'image de couverture
        self.cover_image_path = default_cover_image
        self.cover_image_edit = QLineEdit(self)
        self.cover_image_edit.setText(self.cover_image_path)
        self.cover_image_edit.setReadOnly(True)
        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_for_image)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.cover_image_edit)
        image_layout.addWidget(browse_button)

        form_layout.addRow(QLabel("Première note à inclure :"), self.start_date_edit)
        form_layout.addRow(QLabel("Dernière note à inclure :"), self.end_date_edit)
        form_layout.addRow(QLabel("Titre du journal :"), self.title_edit)
        form_layout.addRow(QLabel("Nom de l'auteur (optionnel) :"), self.author_edit)
        form_layout.addRow(QLabel("Image de couverture :"), image_layout)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _browse_for_image(self):
        """Ouvre une boîte de dialogue pour sélectionner un fichier image."""
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Sélectionner une image de couverture")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)")
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # Utiliser le dialog Qt pour appliquer la palette
        if dialog.exec_() == QDialog.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.cover_image_path = selected_files[0]
                self.cover_image_edit.setText(self.cover_image_path)

    def get_export_options(self) -> dict:
        """Retourne les options d'exportation sélectionnées."""
        return {
            "start_date": self.start_date_edit.date(),
            "end_date": self.end_date_edit.date(),
            "title": self.title_edit.text(),
            "author": self.author_edit.text(),
            "cover_image": self.cover_image_path,
        }
```

### Modifications pour `main_window.py`
Pour `main_window.py`, appliquez les mêmes principes aux boîtes de dialogue `NewFileDialog`, `GpsInputDialog`, et à tous les appels à `QFileDialog` ou `QInputDialog`. Voici un exemple pour `NewFileDialog` et un appel à `QFileDialog` :

1. **Ajouter les imports et la classe `QDarkPalette`** :
   - Ajoutez les imports et la définition de `QDarkPalette` comme dans `date_range_dialog.py` au début de `main_window.py`.

2. **Modifier `NewFileDialog`** :
   Dans la classe `NewFileDialog`, ajoutez la détection du thème sombre dans `__init__` :
   ```python
   class NewFileDialog(QDialog):
       def __init__(
           self, parent=None, use_template_by_default=False, default_template_name=None
       ):
           super().__init__(parent)
           if darkdetect and darkdetect.isDark():
               self.setPalette(QDarkPalette())
           self.setWindowTitle("Créer un nouveau document")
           self.setMinimumWidth(400)
           # ... reste du code inchangé ...
   ```

3. **Modifier `GpsInputDialog`** :
   Dans la classe `GpsInputDialog`, ajoutez la détection du thème sombre :
   ```python
   class GpsInputDialog(QDialog):
       def __init__(self, parent=None):
           super().__init__(parent)
           if darkdetect and darkdetect.isDark():
               self.setPalette(QDarkPalette())
           self.setWindowTitle("Coordonnées GPS")
           self.setMinimumWidth(300)
           # ... reste du code inchangé ...
   ```

4. **Modifier les appels à `QFileDialog`** :
   Remplacez les appels statiques comme `QFileDialog.getOpenFileName` par des instances de `QFileDialog`. Par exemple, dans une méthode comme `open_file` (si elle existe), modifiez comme suit :
   ```python
   def open_file(self):
       dialog = QFileDialog(self)
       dialog.setWindowTitle("Ouvrir un fichier")
       dialog.setFileMode(QFileDialog.ExistingFile)
       dialog.setNameFilter("Fichiers Markdown (*.md);;Tous les fichiers (*.*)")
       if darkdetect and darkdetect.isDark():
           dialog.setPalette(QDarkPalette())
       dialog.setOption(QFileDialog.DontUseNativeDialog, True)
       if dialog.exec_() == QDialog.Accepted:
           file_path = dialog.selectedFiles()[0]
           # ... traitement du fichier ...
   ```

### Modifications pour `editor.py`
Pour `editor.py`, modifiez la classe `ImageSourceDialog` (si elle existe, sinon créez-la si nécessaire) et les appels à `QFileDialog` et `QInputDialog`. Voici un exemple pour `insert_html_image` et `insert_markdown_image` :

1. **Ajouter les imports et la classe `QDarkPalette`** :
   - Ajoutez les imports et la définition de `QDarkPalette` comme dans `date_range_dialog.py` au début de `editor.py`.

2. **Modifier `ImageSourceDialog` (si elle existe)** :
   Si `ImageSourceDialog` est utilisée dans `insert_html_image` ou `insert_markdown_image`, ajoutez la détection du thème sombre :
   ```python
   class ImageSourceDialog(QDialog):
       def __init__(self, parent=None):
           super().__init__(parent)
           if darkdetect and darkdetect.isDark():
               self.setPalette(QDarkPalette())
           # ... reste du code inchangé ...
   ```

3. **Modifier les appels à `QFileDialog` dans `insert_html_image` et `insert_markdown_image`** :
   Remplacez l'appel statique `QFileDialog.getOpenFileName` par une instance :
   ```python
   def insert_html_image(self):
       cursor = self.text_edit.textCursor()
       selected_text = cursor.selectedText().strip()
       file_path = ""
       if selected_text and Path(selected_text).is_file():
           file_path = selected_text
       elif not selected_text:
           dialog = QFileDialog(self)
           dialog.setWindowTitle("Sélectionner une image")
           dialog.setFileMode(QFileDialog.ExistingFile)
           dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)")
           if darkdetect and darkdetect.isDark():
               dialog.setPalette(QDarkPalette())
           dialog.setOption(QFileDialog.DontUseNativeDialog, True)
           if dialog.exec_() == QDialog.Accepted:
               file_path = dialog.selectedFiles()[0]
       else:
           file_path = selected_text

       if file_path:
           relative_path = self._copy_image_to_journal(file_path)
           width, ok = QInputDialog.getInt(
               self,
               "Largeur de l'image",
               "Largeur maximale en pixels :",
               400,
               1,
               10000,
               1,
           )
           if ok:
               cursor.insertText(f'<img src="{relative_path}" width="{width}">')

   def insert_markdown_image(self):
       cursor = self.text_edit.textCursor()
       selected_text = cursor.selectedText().strip()
       image_path = ""
       if selected_text and Path(selected_text).is_file():
           image_path = selected_text
       elif not selected_text:
           dialog = QFileDialog(self)
           dialog.setWindowTitle("Sélectionner une image")
           dialog.setFileMode(QFileDialog.ExistingFile)
           dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)")
           if darkdetect and darkdetect.isDark():
               dialog.setPalette(QDarkPalette())
           dialog.setOption(QFileDialog.DontUseNativeDialog, True)
           if dialog.exec_() == QDialog.Accepted:
               image_path = dialog.selectedFiles()[0]
       else:
           image_path = selected_text

       if image_path:
           relative_path = self._copy_image_to_journal(image_path)
           image_path_md = relative_path.replace("\\", "/")
           self.insert_text(f"![]({image_path_md})")

       self.text_edit.setFocus()
   ```

4. **Modifier les appels à `QInputDialog`** :
   Dans `insert_html_image` et `insert_link`, remplacez `QInputDialog.getInt` ou `getText` par des instances :
   ```python
   def insert_link(self):
       cursor = self.text_edit.textCursor()
       selected_text = cursor.selectedText().strip()
       url = ""
       if selected_text:
           url = selected_text

       dialog = QInputDialog(self)
       dialog.setWindowTitle("Insérer un lien")
       dialog.setLabelText("URL du lien :")
       if darkdetect and darkdetect.isDark():
           dialog.setPalette(QDarkPalette())
       if dialog.exec_() == QDialog.Accepted:
           url = dialog.textValue()
           if url:
               self.insert_text(f"[{selected_text or 'Lien'}]({url})")
       self.text_edit.setFocus()
   ```

### Notes importantes
- **Installation de `darkdetect`** : Assurez-vous d'installer `darkdetect` avec `pip install darkdetect`. Si la bibliothèque n'est pas disponible, le code vérifie `darkdetect is None` pour éviter les erreurs.
- **Option `DontUseNativeDialog`** : L'option `QFileDialog.DontUseNativeDialog` est utilisée pour garantir que la palette sombre s'applique. Cependant, cela désactive les dialogues natifs du système, ce qui peut changer l'apparence des sélecteurs de fichiers. Si vous préférez les dialogues natifs, supprimez cette ligne, mais sachez que la palette sombre pourrait ne pas s'appliquer correctement sur certaines plateformes.
- **Compatibilité multi-plateforme** : Testez les modifications sur votre plateforme (Windows, macOS, Linux), car le rendu des dialogues Qt peut varier. La palette sombre définie ici est optimisée pour le style `Fusion` de Qt.
- **Palette personnalisable** : La classe `QDarkPalette` utilise des couleurs prédéfinies (`PRIMARY`, `SECONDARY`, `TERTIARY`, etc.). Vous pouvez ajuster ces couleurs en modifiant les constantes globales (`WHITE`, `BLACK`, etc.) pour mieux correspondre à vos préférences.
- **Application globale** : Si vous souhaitez appliquer la palette sombre à l'ensemble de l'application (et pas seulement aux dialogues), vous pouvez appeler `QDarkPalette().set_app(QApplication.instance())` au démarrage de l'application, par exemple dans le constructeur de `MainWindow` dans `main_window.py`.

### Instructions pour appliquer les modifications
1. Remplacez le contenu de `date_range_dialog.py` par le code fourni.
2. Ajoutez les imports et la classe `QDarkPalette` au début de `main_window.py` et `editor.py`.
3. Appliquez la détection du thème sombre (`if darkdetect and darkdetect.isDark(): self.setPalette(QDarkPalette())`) dans les constructeurs des classes `NewFileDialog`, `GpsInputDialog`, et `ImageSourceDialog` (si applicable).
4. Modifiez les appels à `QFileDialog.getOpenFileName` et `QInputDialog.getText`/`getInt` dans `main_window.py` et `editor.py` pour utiliser des instances avec la palette sombre, comme montré dans les exemples.
5. Installez `darkdetect` avec `pip install darkdetect`.
6. Testez l'application en mode sombre et clair pour vérifier que les boîtes de dialogue et sélecteurs de fichiers sont lisibles.

Si vous rencontrez des problèmes spécifiques (par exemple, une boîte de dialogue particulière qui reste illisible), fournissez plus de détails sur le contexte (plateforme, version de PyQt5, thème système), et je pourrai affiner la solution.
------------------

#2nd Part
Le problème que vous décrivez, où certaines boîtes de dialogue ou sélecteurs de fichiers adoptent correctement le thème sombre tandis que d'autres ne le font pas, est probablement dû à des différences dans la manière dont ces dialogues sont implémentés dans votre application. Voici une analyse détaillée des raisons possibles et des solutions pour uniformiser le comportement :

---

### Raisons possibles pour lesquelles certaines boîtes de dialogue ou sélecteurs de fichiers ne fonctionnent pas

1. **Utilisation de dialogues natifs vs dialogues Qt personnalisés** :
   - Les appels à `QFileDialog.getOpenFileName` ou `QFileDialog.getSaveFileName` utilisent par défaut les dialogues natifs du système (par exemple, les dialogues de fichiers de Windows, macOS, ou Linux). Ces dialogues natifs ne respectent pas toujours la palette Qt personnalisée (`QDarkPalette`) car ils sont rendus par le système d'exploitation, qui applique son propre thème.
   - Les dialogues personnalisés (`QDialog`, comme `DateRangeDialog`, `NewFileDialog`, etc.) sont entièrement rendus par Qt, ce qui permet d'appliquer la palette sombre via `setPalette(QDarkPalette())`. Si vous avez utilisé l'option `DontUseNativeDialog` pour certains `QFileDialog` (comme dans l'exemple modifié de `date_range_dialog.py`), ces dialogues adoptent la palette sombre, tandis que d'autres appels sans cette option utilisent les dialogues natifs et ignorent la palette.

2. **Application incohérente de la palette sombre** :
   - Si vous avez appliqué `setPalette(QDarkPalette())` uniquement dans certaines classes de dialogues (par exemple, `DateRangeDialog` mais pas `NewFileDialog` ou `GpsInputDialog`), cela explique pourquoi certaines boîtes de dialogue adoptent le thème sombre et d'autres non.
   - De plus, si une boîte de dialogue est créée sans vérifier `darkdetect.isDark()`, elle utilisera la palette par défaut de l'application ou du système, qui peut être illisible en mode sombre.

3. **Héritage des styles de l'application principale** :
   - Si l'application principale (via `QApplication` dans `main_window.py`) définit une feuille de style globale ou une palette qui n'est pas cohérente avec le thème sombre, certaines boîtes de dialogue peuvent hériter de ces styles, entraînant des incohérences visuelles.
   - Par exemple, si `main_window.py` définit un style global via `QApplication.setStyleSheet` ou une palette différente, cela peut interférer avec les dialogues qui ne redéfinissent pas explicitement leur palette.

4. **Différences dans les appels statiques vs instanciés** :
   - Les appels statiques comme `QFileDialog.getOpenFileName` ou `QInputDialog.getText` ne permettent pas de personnaliser facilement la palette ou les options du dialogue avant affichage. En revanche, les instances créées (par exemple, `dialog = QFileDialog(self)`) permettent d'appliquer des modifications comme `setPalette` ou `setOption(QFileDialog.DontUseNativeDialog)`. Si certaines parties de votre code utilisent des appels statiques, elles ne bénéficieront pas de la palette sombre.

5. **Comportement spécifique à la plateforme** :
   - Sur certaines plateformes (par exemple, macOS ou certaines distributions Linux), les dialogues natifs peuvent ignorer les modifications de palette Qt, même avec `DontUseNativeDialog`. Cela peut entraîner des différences de rendu entre les plateformes.
   - De plus, `darkdetect.isDark()` peut ne pas détecter correctement le mode sombre sur certains systèmes si la configuration du thème n'est pas standard.

6. **Problèmes avec les sous-composants** :
   - Certaines boîtes de dialogue, comme celles contenant des `QDateEdit` avec des calendriers déroulants, peuvent avoir des sous-composants (par exemple, `QCalendarWidget`) qui nécessitent des styles QSS spécifiques pour respecter le thème sombre. Si ces styles ne sont pas définis, des parties du dialogue peuvent rester illisibles.

---

### Étapes pour uniformiser le comportement

Pour garantir que **toutes** les boîtes de dialogue et sélecteurs de fichiers respectent le thème sombre de manière cohérente, voici les étapes à suivre :

1. **Appliquer la palette sombre globalement à l'application** :
   - Plutôt que d'appliquer `QDarkPalette` à chaque dialogue individuellement, configurez la palette sombre au niveau de l'application dans `main_window.py` au démarrage. Cela garantit que toutes les boîtes de dialogue héritent de la palette sombre, sauf si elles sont explicitement surchargées.

2. **Utiliser des dialogues Qt non natifs pour les sélecteurs de fichiers** :
   - Remplacez tous les appels statiques à `QFileDialog.getOpenFileName` ou `getSaveFileName` par des instances de `QFileDialog` avec `DontUseNativeDialog` pour garantir que la palette sombre s'applique.

3. **Vérifier et mettre à jour toutes les boîtes de dialogue** :
   - Assurez-vous que toutes les classes dérivées de `QDialog` (`DateRangeDialog`, `NewFileDialog`, `GpsInputDialog`, `ImageSourceDialog`) incluent la vérification du thème sombre et l'application de `QDarkPalette`.

4. **Appliquer des styles QSS spécifiques pour les sous-composants** :
   - Pour les dialogues contenant des widgets comme `QDateEdit` (utilisé dans `DateRangeDialog`), définissez des styles QSS pour garantir que le calendrier déroulant respecte le thème sombre.

5. **Vérifier les appels à `QInputDialog`** :
   - Remplacez les appels statiques à `QInputDialog.getText` ou `getInt` par des instances pour appliquer la palette sombre.

---

### Modifications spécifiques pour résoudre les incohérences

Voici les modifications à apporter aux fichiers fournis (`date_range_dialog.py`, `main_window.py`, `editor.py`) pour uniformiser l'application du thème sombre.

#### 1. Appliquer la palette sombre globalement dans `main_window.py`
Modifiez le fichier `main_window.py` pour appliquer la palette sombre à l'ensemble de l'application au démarrage. Ajoutez les imports et la classe `QDarkPalette` (comme dans `date_range_dialog.py`) et configurez la palette dans le constructeur de `MainWindow`.

```python
# Au début de main_window.py, ajoutez les imports et la classe QDarkPalette
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMenuBar, QMenu,
    QAction, QFileDialog, QMessageBox, QStatusBar, QLabel, QDialog,
    QDialogButtonBox, QProgressDialog, QInputDialog, QToolBar,
    QApplication, QPushButton, QRadioButton, QComboBox, QFormLayout, QLineEdit,
    QSplitterHandle, QToolButton
)
from PyQt5.QtCore import Qt, QTimer, QDate, QUrl, QThreadPool, QPropertyAnimation, QRect, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QKeySequence, QIcon, QFont, QPainter, QPalette, QColor
from pathlib import Path
# ... autres imports ...
try:
    import darkdetect
except ImportError:
    darkdetect = None

WHITE =     QColor(255, 255, 255)
BLACK =     QColor(0, 0, 0)
RED =       QColor(255, 0, 0)
PRIMARY =   QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY =  QColor(42, 130, 218)

def css_rgb(color, a=False):
    """Get a CSS `rgb` or `rgba` string from a `QtGui.QColor`."""
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())

class QDarkPalette(QPalette):
    """Dark palette for a Qt application meant to be used with the Fusion theme."""
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        app.setStyleSheet("QToolTip {"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)

# Modifiez la classe MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Appliquer la palette sombre globalement si le mode sombre est détecté
        if darkdetect and darkdetect.isDark():
            QDarkPalette().set_app(QApplication.instance())
        # ... reste du code inchangé ...
```

#### 2. Mettre à jour `date_range_dialog.py`
Votre code pour `DateRangeDialog` applique déjà `QDarkPalette` au dialogue et au sélecteur de fichiers dans `_browse_for_image`. Cependant, pour garantir que le calendrier déroulant de `QDateEdit` soit lisible en mode sombre, ajoutez des styles QSS spécifiques.

```python
class DateRangeDialog(QDialog):
    def __init__(
        self,
        start_date_default: QDate,
        end_date_default: QDate,
        min_date: QDate,
        max_date: QDate,
        default_title: str,
        default_cover_image: str,
        default_author: str,
        parent=None,
    ):
        super().__init__(parent)
        if darkdetect and darkdetect.isDark():
            self.setPalette(QDarkPalette())
        self.setWindowTitle("Options d'exportation du journal PDF")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)

        self.start_date_edit = QDateEdit(self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDateRange(min_date, max_date)
        self.start_date_edit.setDate(start_date_default)
        if darkdetect and darkdetect.isDark():
            self.start_date_edit.setStyleSheet("""
                QDateEdit {
                    background-color: rgb(35, 35, 35);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(53, 53, 53);
                }
                QDateEdit QCalendarWidget {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                }
                QDateEdit QCalendarWidget QAbstractItemView {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                    selection-background-color: rgb(42, 130, 218);
                }
                QDateEdit QCalendarWidget QWidget#qt_calendar_calendarview > QWidget {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                }
                QDateEdit QCalendarWidget QToolButton {
                    color: rgb(255, 255, 255);
                    background-color: rgb(53, 53, 53);
                }
                QDateEdit QCalendarWidget QSpinBox {
                    color: rgb(255, 255, 255);
                    background-color: rgb(53, 53, 53);
                    border: none;
                }
            """)

        self.end_date_edit = QDateEdit(self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDateRange(min_date, max_date)
        self.end_date_edit.setDate(end_date_default)
        if darkdetect and darkdetect.isDark():
            self.end_date_edit.setStyleSheet("""
                QDateEdit {
                    background-color: rgb(35, 35, 35);
                    color: rgb(255, 255, 255);
                    border: 1px solid rgb(53, 53, 53);
                }
                QDateEdit QCalendarWidget {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                }
                QDateEdit QCalendarWidget QAbstractItemView {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                    selection-background-color: rgb(42, 130, 218);
                }
                QDateEdit QCalendarWidget QWidget#qt_calendar_calendarview > QWidget {
                    background-color: rgb(53, 53, 53);
                    color: rgb(255, 255, 255);
                }
                QDateEdit QCalendarWidget QToolButton {
                    color: rgb(255, 255, 255);
                    background-color: rgb(53, 53, 53);
                }
                QDateEdit QCalendarWidget QSpinBox {
                    color: rgb(255, 255, 255);
                    background-color: rgb(53, 53, 53);
                    border: none;
                }
            """)

        self.title_edit = QLineEdit(self)
        self.title_edit.setText(default_title)

        self.author_edit = QLineEdit(self)
        self.author_edit.setText(default_author)

        self.cover_image_path = default_cover_image
        self.cover_image_edit = QLineEdit(self)
        self.cover_image_edit.setText(self.cover_image_path)
        self.cover_image_edit.setReadOnly(True)
        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_for_image)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.cover_image_edit)
        image_layout.addWidget(browse_button)

        form_layout.addRow(QLabel("Première note à inclure :"), self.start_date_edit)
        form_layout.addRow(QLabel("Dernière note à inclure :"), self.end_date_edit)
        form_layout.addRow(QLabel("Titre du journal :"), self.title_edit)
        form_layout.addRow(QLabel("Nom de l'auteur (optionnel) :"), self.author_edit)
        form_layout.addRow(QLabel("Image de couverture :"), image_layout)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)

    def _browse_for_image(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Sélectionner une image de couverture")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)")
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_() == QDialog.Accepted:
            selected_files = dialog.selectedFiles()
            if selected_files:
                self.cover_image_path = selected_files[0]
                self.cover_image_edit.setText(self.cover_image_path)
```

#### 3. Mettre à jour `main_window.py` pour `NewFileDialog` et `GpsInputDialog`
Ajoutez la palette sombre dans les constructeurs des dialogues et modifiez les appels à `QFileDialog`.

```python
class NewFileDialog(QDialog):
    def __init__(
        self, parent=None, use_template_by_default=False, default_template_name=None
    ):
        super().__init__(parent)
        if darkdetect and darkdetect.isDark():
            self.setPalette(QDarkPalette())
        self.setWindowTitle("Créer un nouveau document")
        self.setMinimumWidth(400)
        # ... reste du code inchangé ...

class GpsInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if darkdetect and darkdetect.isDark():
            self.setPalette(QDarkPalette())
        self.setWindowTitle("Coordonnées GPS")
        self.setMinimumWidth(300)
        # ... reste du code inchangé ...
```

#### 4. Mettre à jour `editor.py` pour `ImageSourceDialog`, `insert_html_image`, `insert_markdown_image`, et `insert_link`
- Ajoutez la classe `ImageSourceDialog` si elle n'existe pas (elle est référencée dans le code mais absente dans l'extrait fourni).
- Modifiez les méthodes pour utiliser des instances de `QFileDialog` et `QInputDialog`.

```python
# Au début de editor.py, ajoutez les imports et QDarkPalette
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFileDialog, QTextEdit, QLabel, QDialog, QHBoxLayout,
    QLineEdit, QMenu, QPushButton, QDialogButtonBox, QFormLayout, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter, QTextDocument, QKeySequence, QTextCursor, QPalette
# ... autres imports ...
try:
    import darkdetect
except ImportError:
    darkdetect = None

# Définir QDarkPalette comme dans date_range_dialog.py
WHITE =     QColor(255, 255, 255)
BLACK =     QColor(0, 0, 0)
RED =       QColor(255, 0, 0)
PRIMARY =   QColor(53, 53, 53)
SECONDARY = QColor(35, 35, 35)
TERTIARY =  QColor(42, 130, 218)

def css_rgb(color, a=False):
    return ("rgba({}, {}, {}, {})" if a else "rgb({}, {}, {})").format(*color.getRgb())

class QDarkPalette(QPalette):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.setColor(QPalette.Window,          PRIMARY)
        self.setColor(QPalette.WindowText,      WHITE)
        self.setColor(QPalette.Base,            SECONDARY)
        self.setColor(QPalette.AlternateBase,   PRIMARY)
        self.setColor(QPalette.ToolTipBase,     WHITE)
        self.setColor(QPalette.ToolTipText,     WHITE)
        self.setColor(QPalette.Text,            WHITE)
        self.setColor(QPalette.Button,          PRIMARY)
        self.setColor(QPalette.ButtonText,      WHITE)
        self.setColor(QPalette.BrightText,      RED)
        self.setColor(QPalette.Link,            TERTIARY)
        self.setColor(QPalette.Highlight,       TERTIARY)
        self.setColor(QPalette.HighlightedText, BLACK)

    @staticmethod
    def set_stylesheet(app):
        app.setStyleSheet("QToolTip {"
                          "color: {white};"
                          "background-color: {tertiary};"
                          "border: 1px solid {white};"
                          "}}".format(white=css_rgb(WHITE), tertiary=css_rgb(TERTIARY)))

    def set_app(self, app):
        app.setStyle("Fusion")
        app.setPalette(self)
        self.set_stylesheet(app)

# Ajouter ImageSourceDialog si elle n'existe pas
class ImageSourceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        if darkdetect and darkdetect.isDark():
            self.setPalette(QDarkPalette())
        self.setWindowTitle("Source de l'image")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.path_edit = QLineEdit(self)
        self.path_edit.setPlaceholderText("Entrez une URL ou sélectionnez un fichier")
        browse_button = QPushButton("Parcourir...", self)
        browse_button.clicked.connect(self._browse_for_image)
        form_layout.addRow("Chemin ou URL :", self.path_edit)
        form_layout.addRow("", browse_button)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _browse_for_image(self):
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Sélectionner une image")
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.gif *.bmp *.svg)")
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        if dialog.exec_() == QDialog.Accepted:
            self.path_edit.setText(dialog.selectedFiles()[0])

    def get_path(self):
        return self.path_edit.text()

# Modifier insert_html_image
def insert_html_image(self):
    cursor = self.text_edit.textCursor()
    selected_text = cursor.selectedText().strip()
    file_path = ""
    if selected_text and Path(selected_text).is_file():
        file_path = selected_text
    elif not selected_text:
        dialog = ImageSourceDialog(self)
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        if dialog.exec_() == QDialog.Accepted:
            file_path = dialog.get_path()
    else:
        file_path = selected_text

    if file_path:
        relative_path = self._copy_image_to_journal(file_path)
        dialog = QInputDialog(self)
        dialog.setWindowTitle("Largeur de l'image")
        dialog.setLabelText("Largeur maximale en pixels :")
        dialog.setIntValue(400)
        dialog.setIntRange(1, 10000)
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        if dialog.exec_() == QDialog.Accepted:
            width = dialog.intValue()
            cursor.insertText(f'<img src="{relative_path}" width="{width}">')

# Modifier insert_markdown_image
def insert_markdown_image(self):
    cursor = self.text_edit.textCursor()
    selected_text = cursor.selectedText().strip()
    image_path = ""
    if selected_text and Path(selected_text).is_file():
        image_path = selected_text
    elif not selected_text:
        dialog = ImageSourceDialog(self)
        if darkdetect and darkdetect.isDark():
            dialog.setPalette(QDarkPalette())
        if dialog.exec_() == QDialog.Accepted:
            image_path = dialog.get_path()
    else:
        image_path = selected_text

    if image_path:
        relative_path = self._copy_image_to_journal(image_path)
        image_path_md = relative_path.replace("\\", "/")
        self.insert_text(f"![]({image_path_md})")
    self.text_edit.setFocus()

# Modifier insert_link
def insert_link(self):
    cursor = self.text_edit.textCursor()
    selected_text = cursor.selectedText().strip()
    url = ""
    if selected_text:
        url = selected_text

    dialog = QInputDialog(self)
    dialog.setWindowTitle("Insérer un lien")
    dialog.setLabelText("URL du lien :")
    if darkdetect and darkdetect.isDark():
        dialog.setPalette(QDarkPalette())
    if dialog.exec_() == QDialog.Accepted:
        url = dialog.textValue()
        if url:
            self.insert_text(f"[{selected_text or 'Lien'}]({url})")
    self.text_edit.setFocus()
```

---

### Explications des changements

1. **Palette sombre globale** :
   - En appliquant `QDarkPalette().set_app(QApplication.instance())` dans `MainWindow`, toutes les boîtes de dialogue et widgets héritent automatiquement de la palette sombre en mode sombre, réduisant le besoin d'appliquer `setPalette` à chaque dialogue. Cela garantit une cohérence de base.

2. **Styles QSS pour `QDateEdit`** :
   - Dans `DateRangeDialog`, les styles QSS spécifiques pour `QDateEdit` et son `QCalendarWidget` garantissent que le calendrier déroulant est lisible en mode sombre, en utilisant les couleurs de `QDarkPalette` (`rgb(53, 53, 53)` pour le fond, `rgb(255, 255, 255)` pour le texte, etc.).

3. **Dialogues non natifs** :
   - L'option `QFileDialog.DontUseNativeDialog` force l'utilisation des dialogues Qt, qui respectent la palette sombre. Sans cette option, les dialogues natifs du système peuvent ignorer la palette Qt, ce qui explique pourquoi certains sélecteurs de fichiers ne fonctionnent pas correctement.

4. **Uniformisation des dialogues** :
   - En ajoutant `setPalette(QDarkPalette())` à chaque `QDialog` (`NewFileDialog`, `GpsInputDialog`, `ImageSourceDialog`) et en utilisant des instances pour `QFileDialog` et `QInputDialog`, vous garantissez que tous les dialogues adoptent le thème sombre.

---

### Instructions pour appliquer les changements

1. **Installer `darkdetect`** :
   - Exécutez `pip install darkdetect` dans votre environnement Python.

2. **Mettre à jour les fichiers** :
   - Remplacez le contenu de `date_range_dialog.py` par le code fourni.
   - Ajoutez la classe `QDarkPalette` et les imports nécessaires dans `main_window.py` et `editor.py`.
   - Appliquez la palette sombre globale dans le constructeur de `MainWindow` dans `main_window.py`.
   - Mettez à jour `NewFileDialog`, `GpsInputDialog`, et les méthodes `insert_html_image`, `insert_markdown_image`, et `insert_link` dans `editor.py` comme indiqué.

3. **Vérifier les autres dialogues** :
   - Parcourez votre code pour identifier d'autres appels à `QFileDialog.getOpenFileName`, `QFileDialog.getSaveFileName`, `QInputDialog.getText`, ou `QInputDialog.getInt`. Remplacez-les par des instances avec `setPalette(QDarkPalette())` et `DontUseNativeDialog` si nécessaire.
   - Si d'autres dialogues personnalisés existent (par exemple, dans `preferences_dialog.py` ou d'autres fichiers non fournis), ajoutez `if darkdetect and darkdetect.isDark(): self.setPalette(QDarkPalette())` dans leurs constructeurs.

4. **Tester sur votre plateforme** :
   - Testez l'application en mode sombre et clair sur votre système (Windows, macOS, Linux) pour vérifier que toutes les boîtes de dialogue et sélecteurs de fichiers sont lisibles.
   - Si vous préférez utiliser les dialogues natifs, supprimez `setOption(QFileDialog.DontUseNativeDialog, True)`, mais testez pour confirmer que la palette sombre s'applique correctement (cela peut ne pas fonctionner sur toutes les plateformes).

---

### Résolution des incohérences restantes

Si certaines boîtes de dialogue ou sélecteurs de fichiers restent illisibles après ces changements, voici comment enquêter :

1. **Identifier les dialogues problématiques** :
   - Notez exactement quelles boîtes de dialogue ou sélecteurs de fichiers posent problème (par exemple, le sélecteur de fichiers dans une méthode spécifique ou un dialogue particulier).
   - Vérifiez si ces dialogues utilisent des appels statiques (`QFileDialog.getOpenFileName`, `QInputDialog.getText`) ou des dialogues natifs.

2. **Vérifier les styles globaux** :
   - Recherchez dans `main_window.py` ou d'autres fichiers si une feuille de style globale (`QApplication.setStyleSheet`) ou une palette par défaut est appliquée, ce qui pourrait interférer avec `QDarkPalette`.

3. **Déboguer avec `darkdetect`** :
   - Ajoutez un log pour vérifier si `darkdetect.isDark()` retourne `True` correctement :
     ```python
     if darkdetect:
         print(f"Mode sombre détecté : {darkdetect.isDark()}")
     else:
         print("darkdetect non disponible")
     ```
   - Si `darkdetect` ne détecte pas correctement le mode sombre, vérifiez la configuration du thème système.

4. **Inspecter les sous-composants** :
   - Pour les dialogues avec des widgets comme `QComboBox`, `QDateEdit`, ou `QCalendarWidget`, assurez-vous que des styles QSS spécifiques sont appliqués (comme dans `DateRangeDialog` pour `QDateEdit`).

5. **Fournir plus de détails** :
   - Si le problème persiste, fournissez :
     - Les noms des dialogues ou sélecteurs de fichiers problématiques.
     - Votre plateforme (Windows, macOS, Linux) et la version de PyQt5.
     - Une capture d'écran ou une description de l'apparence des dialogues problématiques.
     - Tout message d'erreur ou log pertinent.

Cela permettra d'identifier précisément pourquoi certains dialogues ne respectent pas le thème sombre et de proposer une solution ciblée.

---

### Conclusion

En appliquant la palette sombre globalement dans `MainWindow`, en utilisant des dialogues Qt non natifs pour `QFileDialog`, et en ajoutant des styles QSS pour les sous-composants comme `QDateEdit`, vous devriez éliminer les incohérences. Les modifications proposées garantissent que toutes les boîtes de dialogue et sélecteurs de fichiers adoptent le thème sombre de manière cohérente lorsque le système est en mode sombre. Testez thoroughly et signalez tout problème persistant pour une assistance supplémentaire.
 
Pour répondre à votre demande, je vais vous expliquer comment redéfinir un menu contextuel personnalisé dans une fenêtre PyQt (je suppose que `preview.py` utilise PyQt5 ou PyQt6, ce qui est courant pour les interfaces graphiques Python). L'objectif est de faciliter la traduction des menus en différentes langues, en utilisant le système d'internationalisation (i18n) de Qt. Cela évite de dépendre du menu contextuel standard des widgets (comme `QTextEdit` ou `QLabel`), qui peut être capricieux pour les traductions, et vous permet de contrôler pleinement les chaînes de texte.

Je vais structurer la réponse comme suit :
- **Étapes pour redéfinir le menu contextuel** : Créer un `QMenu` personnalisé et l'associer à un événement clic droit.
- **Intégration de l'i18n** : Marquer les chaînes pour traduction, générer les fichiers de traduction, et charger dynamiquement les langues.
- **Exemple de code** : Un extrait modifiable pour `preview.py` (à adapter à votre classe de fenêtre existante).
- **Conseils pour tester et étendre**.

### 1. Redéfinir le menu contextuel
- Au lieu d'utiliser `widget.createStandardContextMenu()`, créez un `QMenu` personnalisé avec des `QAction`.
- Associez-le à l'événement clic droit via `contextMenuEvent` ou en définissant `setContextMenuPolicy(Qt.CustomContextMenu)` et en connectant le signal `customContextMenuRequested`.

### 2. Système d'internationalisation (i18n)
- Utilisez `self.tr("texte")` pour marquer les chaînes traduisibles (contexte : nom de la classe).
- Générez des fichiers `.ts` (XML pour traductions) avec `pylupdate5` (fourni avec PyQt5).
- Compilez en `.qm` (binaire) avec `pyrcc5` ou `lrelease`.
- Chargez un `QTranslator` à l'application ou à la fenêtre, et appelez `retranslateUi()` pour rafraîchir les textes lors du changement de langue.
- Pour Qt lui-même (ex. : menus standards), chargez aussi les traductions Qt (`qt_fr.qm` pour le français).

**Outils requis** : Installez PyQt5/PyQt6 si ce n'est pas fait (`pip install pyqt5` ou `pyqt6`). Les outils `pylupdate5` et `lrelease` sont inclus.

### 3. Exemple de code pour `preview.py`
Voici un exemple complet pour une fenêtre de prévisualisation (`PreviewWindow`). Intégrez-le dans votre fichier existant. J'assume une fenêtre simple avec un `QTextEdit` pour l'aperçu ; adaptez à votre cas (ex. : image, PDF).

```python
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QMenu, QAction, 
                             QMessageBox, QFileDialog)
from PyQt5.QtCore import QTranslator, QLibraryInfo, QLocale, Qt
from PyQt5.QtGui import QIcon  # Optionnel pour icônes

class PreviewWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.tr("Fenêtre de Prévisualisation"))  # Texte traduisible
        self.setGeometry(100, 100, 800, 600)

        # Widget central : un QTextEdit pour l'exemple (remplacez par votre contenu)
        self.preview_text = QTextEdit(self)
        self.preview_text.setPlainText(self.tr("Contenu de prévisualisation ici..."))
        self.setCentralWidget(self.preview_text)

        # Traducteur pour l'app (membre de classe pour persistance)
        self.translator = QTranslator(self)

        # Menu contextuel personnalisé
        self.context_menu = None
        self._create_context_menu()

        # Politique de menu contextuel
        self.preview_text.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview_text.customContextMenuRequested.connect(self._show_context_menu)

        # Exemple : Menu principal pour changer de langue (ajoutez un menu "Langue")
        self._setup_language_menu()

    def _create_context_menu(self):
        """Crée le menu contextuel personnalisé avec actions traduisibles."""
        self.context_menu = QMenu(self)

        # Action Copier (exemple)
        copy_action = QAction(self.tr("Copier"), self)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self._copy_text)
        self.context_menu.addAction(copy_action)

        # Action Coller
        paste_action = QAction(self.tr("Coller"), self)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self._paste_text)
        self.context_menu.addAction(paste_action)

        # Séparateur
        self.context_menu.addSeparator()

        # Action Traduire (exemple d'action personnalisée)
        translate_action = QAction(self.tr("Traduire le texte"), self)
        translate_action.triggered.connect(self._translate_text)
        self.context_menu.addAction(translate_action)

        # Action Ouvrir fichier (personnalisé)
        open_action = QAction(self.tr("Ouvrir un fichier"), self)
        open_action.triggered.connect(self._open_file)
        self.context_menu.addAction(open_action)

    def _show_context_menu(self, position):
        """Affiche le menu au clic droit."""
        self.context_menu.exec_(self.preview_text.mapToGlobal(position))

    # Actions exemple (implémentez selon vos besoins)
    def _copy_text(self):
        self.preview_text.copy()
        QMessageBox.information(self, self.tr("Info"), self.tr("Texte copié !"))

    def _paste_text(self):
        self.preview_text.paste()
        QMessageBox.information(self, self.tr("Info"), self.tr("Texte collé !"))

    def _translate_text(self):
        # Exemple : Ouvrir un dialogue pour traduction (à implémenter)
        QMessageBox.information(self, self.tr("Traduction"), self.tr("Fonction de traduction à implémenter."))

    def _open_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.tr("Ouvrir Fichier"))
        if file_path:
            with open(file_path, 'r') as f:
                self.preview_text.setPlainText(f.read())

    def _setup_language_menu(self):
        """Menu pour changer de langue (exemple : Français, Anglais)."""
        lang_menu = self.menuBar().addMenu(self.tr("Langue"))

        # Action Français
        fr_action = QAction(self.tr("Français"), self)
        fr_action.triggered.connect(lambda: self._load_language("fr"))
        lang_menu.addAction(fr_action)

        # Action Anglais
        en_action = QAction(self.tr("Anglais"), self)
        en_action.triggered.connect(lambda: self._load_language("en"))
        lang_menu.addAction(en_action)

    def _load_language(self, lang_code):
        """Charge la traduction pour la langue spécifiée et rafraîchit l'UI."""
        # Retire l'ancien traducteur
        QApplication.removeTranslator(self.translator)

        # Charge le fichier .qm de votre app (ex. : preview_fr.qm)
        if self.translator.load(f"preview_{lang_code}", ":/translations"):  # Si embarqué dans ressources
            QApplication.installTranslator(self.translator)
        else:
            # Fallback : charge depuis le chemin système
            qt_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
            self.translator.load(f"qt_{lang_code}", qt_path)
            QApplication.installTranslator(self.translator)

        # Change la locale
        locale = QLocale(lang_code)
        QApplication.instance().setDefaultLocale(locale)

        # Rafraîchit les textes (retranslateUi si vous avez un Ui_ généré ; sinon, recreez les menus)
        self.retranslate_ui()  # À implémenter si besoin

    def retranslate_ui(self):
        """Rafraîchit tous les textes traduisibles. Appelez-la après changement de langue."""
        self.setWindowTitle(self.tr("Fenêtre de Prévisualisation"))
        self.preview_text.setPlainText(self.tr("Contenu de prévisualisation ici..."))
        # Recréez le menu contextuel pour les nouveaux textes
        self._create_context_menu()
        # Mettez à jour les titres/actions d'autres menus si besoin

    def changeEvent(self, event):
        """Gère le changement de langue (QEvent.LanguageChange)."""
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)

# Point d'entrée
if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Charge traductions Qt par défaut (pour menus standards si besoin)
    default_translator = QTranslator()
    qt_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    locale = QLocale.system().name()  # Ex. : "fr_FR"
    if default_translator.load(f"qt_{locale}", qt_path):
        app.installTranslator(default_translator)

    window = PreviewWindow()
    window.show()
    sys.exit(app.exec_())
```

### 4. Génération des fichiers de traduction
1. **Créez un fichier `.pro` pour lister vos fichiers Python** (ex. : `preview.pro`) :
   ```
   SOURCES = preview.py
   TRANSLATIONS = preview_fr.ts preview_en.ts
   ```

2. **Générez les `.ts`** (fichiers XML à traduire) :
   ```
   pylupdate5 -from-list sources.txt preview.pro  # Ou directement : pylupdate5 preview.py -ts preview_fr.ts
   ```
   (Créez `sources.txt` avec `preview.py` dedans.)

3. **Traduisez avec Qt Linguist** (GUI fournie avec PyQt) :
   ```
   linguist preview_fr.ts
   ```
   Ajoutez les traductions pour chaque chaîne (ex. : "Copier" → "Copy").

4. **Compilez en `.qm`** (binaire à charger) :
   ```
   lrelease preview_fr.ts
   ```
   Copiez `preview_fr.qm` dans un dossier `translations/` ou embarquez-le dans les ressources Qt (fichier `.qrc` + `pyrcc5`).

5. **Pour embarquer les ressources** (optionnel, pour distribution) :
   - Créez `resources.qrc` :
     ```
     <RCC>
         <qresource prefix="/translations">
             <file>preview_fr.qm</file>
             <file>preview_en.qm</file>
         </qresource>
     </RCC>
     ```
   - Compilez : `pyrcc5 resources.qrc -o resources.py`
   - Importez `import resources` en haut de `preview.py`, et chargez avec `translator.load("preview_fr", ":/translations")`.

### 5. Conseils pour tester et étendre
- **Test** : Lancez l'app, changez de langue via le menu, et vérifiez le menu contextuel (clic droit sur le texte). Les textes doivent se mettre à jour.
- **Problèmes courants** :
  - Si les traductions Qt (ex. : "Cut/Copy") ne s'appliquent pas, vérifiez le chemin `QLibraryInfo.TranslationsPath` et assurez-vous que `qt_fr.qm` existe.
  - Pour PyQt6, remplacez `PyQt5` par `PyQt6` et ajustez les imports (ex. : `from PyQt6.QtCore import ...`).
  - Si votre `preview.py` utilise des fichiers `.ui` (Qt Designer), utilisez `uic.loadUi` et appelez `ui.retranslateUi(self)` dans `retranslate_ui()`.
- **Extension** : Ajoutez plus d'actions au menu (ex. : zoom, exporter). Pour une traduction dynamique sans redémarrage, surchargez `changeEvent` comme montré.
- **Ressources** : Consultez la doc PyQt sur l'i18n (recherchez "PyQt Internationalization") pour plus de détails.

Si vous partagez le code actuel de `preview.py` (ou des extraits), je peux l'adapter plus précisément ! Si c'est pour Tkinter ou une autre lib, précisez. 😊


--------------------------------------------------------------------------------------------------------------------------

Parfait ! Merci pour le fichier complet `preview.py`.  
Je vais **modifier directement votre classe `MarkdownPreview`** pour :

1. **Remplacer le menu contextuel par défaut** de `QWebEngineView` (qui affiche "Copier", "Recharger", etc.)  
2. **Créer un menu contextuel personnalisé et traduisible** avec `self.tr()`  
3. **Préparer le terrain pour la traduction multilingue** (français → anglais, etc.)  
4. **Conserver toutes les fonctionnalités existantes** (clics sur images, liens, etc.)

---

### Modifications apportées

- Ajout de `contextMenuEvent` dans `MarkdownPreview`
- Création d’un `QMenu` personnalisé avec actions traduisibles
- Utilisation de `self.tr()` pour toutes les chaînes du menu
- Ajout d’une méthode `retranslate_ui()` pour mise à jour dynamique
- Gestion propre des sélecteurs (copier/coller/se tout sélectionner)

---

### Code modifié (à remplacer dans `preview.py`)

```python
# === AJOUTEZ CES IMPORTS EN HAUT DU FICHIER ===
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtGui import QClipboard
# (les autres imports restent inchangés)

class MarkdownPreview(QWidget):
    """Aperçu HTML avec QWebEngine"""

    def __init__(self):
        super().__init__()
        self.current_html = ""
        self.current_markdown = ""
        self.setup_ui()
        self.default_css = self._load_default_css()
        self.pygments_css = HtmlFormatter(style="default").get_style_defs(".highlight")
        self.custom_css = ""
        self.setup_markdown()

        # === NOUVEAU : Désactiver le menu contextuel par défaut ===
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

    # ... vos méthodes setup_ui(), eventFilter(), etc. restent INCHANGÉES ...

    # === NOUVELLE MÉTHODE : MENU CONTEXTUEL PERSONNALISÉ ===
    def show_context_menu(self, pos):
        """Affiche un menu contextuel personnalisé et traduisible"""
        menu = QMenu(self)

        # --- Sélection de texte ---
        has_selection = self.web_view.selectedText().strip() != ""

        # Action : Copier
        copy_action = QAction(self.tr("Copier"), self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(self.copy_selection)
        menu.addAction(copy_action)

        # Action : Tout sélectionner
        select_all_action = QAction(self.tr("Tout sélectionner"), self)
        select_all_action.triggered.connect(self.select_all)
        menu.addAction(select_all_action)

        menu.addSeparator()

        # Action : Recharger
        reload_action = QAction(self.tr("Recharger"), self)
        reload_action.triggered.connect(self.web_view.reload)
        menu.addAction(reload_action)

        # Action : Ouvrir dans le navigateur
        open_in_browser_action = QAction(self.tr("Ouvrir dans le navigateur"), self)
        open_in_browser_action.triggered.connect(self.open_in_browser)
        menu.addAction(open_in_browser_action)

        menu.addSeparator()

        # Action : Imprimer (optionnel)
        print_action = QAction(self.tr("Imprimer..."), self)
        print_action.triggered.connect(self.web_view.page().printRequested)
        menu.addAction(print_action)

        # Exécuter le menu
        menu.exec_(self.web_view.mapToGlobal(pos))

    # === ACTIONS ASSOCIÉES ===
    def copy_selection(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.web_view.selectedText())

    def select_all(self):
        self.web_view.triggerPageAction(QWebEnginePage.SelectAll)

    def open_in_browser(self):
        url = self.web_view.page().url()
        if url.isValid():
            QDesktopServices.openUrl(url)

    # === POUR LA TRADUCTION : mise à jour dynamique ===
    def retranslate_ui(self):
        """À appeler quand on change de langue"""
        # Rien à faire ici pour l'instant, mais utile si vous ajoutez d'autres widgets
        pass

    # === Surcharge pour capter le changement de langue ===
    def changeEvent(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslate_ui()
        super().changeEvent(event)
```

---

### Étapes pour activer la traduction (i18n)

#### 1. Créez un fichier `.pro` (ex: `preview.pro`)

```pro
SOURCES = preview.py
TRANSLATIONS = translations/preview_fr.ts \
               translations/preview_en.ts
```

#### 2. Générez les fichiers `.ts`

```bash
mkdir translations
pylupdate5 preview.pro
```

#### 3. Traduisez avec **Qt Linguist**

```bash
linguist translations/preview_fr.ts
```

→ Traduisez :
- "Copier" → "Copy"
- "Tout sélectionner" → "Select All"
- etc.

#### 4. Compilez en `.qm`

```bash
lrelease translations/preview_fr.ts -qm translations/preview_fr.qm
lrelease translations/preview_en.ts -qm translations/preview_en.qm
```

#### 5. Chargez la langue dans votre application principale

```python
from PyQt5.QtCore import QTranslator, QLocale

def load_language(app, lang="fr"):
    translator = QTranslator(app)
    if translator.load(f"translations/preview_{lang}.qm"):
        app.installTranslator(translator)
    # Recharge les traductions Qt
    qt_translator = QTranslator(app)
    qt_path = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
    qt_translator.load(f"qt_{lang}", qt_path)
    app.installTranslator(qt_translator)

    # Change la locale
    QLocale.setDefault(QLocale(lang))
    app.instance().removeTranslator(app.translator)  # si déjà chargé
    # Réapplique
    for widget in app.allWidgets():
        if hasattr(widget, 'retranslate_ui'):
            widget.retranslate_ui()
```

---

### Résultat

| Action | Français | Anglais |
|-------|----------|--------|
| Copier | "Copier" | "Copy" |
| Tout sélectionner | "Tout sélectionner" | "Select All" |
| Recharger | "Recharger" | "Reload" |
| Ouvrir dans le navigateur | "Ouvrir dans le navigateur" | "Open in Browser" |

**Menu contextuel 100% personnalisé et traduisible**  
**Aucune dépendance au menu natif de Qt WebEngine**

---

### Bonus : Icônes (optionnel)

```python
copy_action.setIcon(QIcon.fromTheme("edit-copy"))
```

---

### Prochaines étapes

1. **Intégrez ce code dans `preview.py`**
2. **Créez le dossier `translations/`**
3. **Testez avec `pylupdate5` + `linguist`**
4. **Ajoutez un menu "Langue" dans votre app principale**

---

Si vous voulez, je peux vous générer :
- Le `.pro` complet
- Un exemple de `main.py` avec changement de langue
- Un système de thèmes + traduction automatique

Dites-moi !
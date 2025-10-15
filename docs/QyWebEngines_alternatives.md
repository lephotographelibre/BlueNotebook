Alternatives

Le problème que vous cherchez à résoudre concerne la traduction du menu contextuel de `QWebEngineView` dans BlueNotebook, qui reste en anglais car le fichier de traduction `qtwebengine_fr.qm` est introuvable sur votre système Ubuntu, même après l'installation des paquets `libqt5webengine-data`, `qtwebengine5-dev`, `libqt5webengine5`, et `qttranslations5-l10n`. De plus, le téléchargement du fichier source `qtwebengine_fr.ts` depuis le dépôt Qt a échoué, probablement en raison d'une mauvaise URL ou d'une structure différente du dépôt. Vous demandez maintenant s'il existe des alternatives à l'utilisation de Qt WebEngine (`QWebEngineView`) pour afficher l'aperçu HTML dans BlueNotebook, afin d'éviter les problèmes de traduction.

### Analyse
- **Contexte** : Le composant `QWebEngineView` (basé sur Chromium) est utilisé dans `preview.py` pour afficher l'aperçu HTML du Markdown. Son menu contextuel (clic droit) repose sur les traductions Qt WebEngine (`qtwebengine_fr.qm`), qui sont absentes de votre système et de votre environnement virtuel (`/home/jm/.pyenv/versions/3.13.5/envs/.venv_bluenotebook/...`).
- **Problème** : L'absence de `qtwebengine_fr.qm` et les difficultés à obtenir `qtwebengine_fr.ts` compliquent la localisation du menu contextuel.
- **Objectif** : Trouver une alternative à `QWebEngineView` pour afficher l'aperçu HTML, de préférence avec une gestion des traductions plus simple ou intégrée aux traductions Qt standards (`qtbase_fr.qm`), qui fonctionnent déjà dans votre application (comme configuré dans `main.py` avec `BLUENOTEBOOK_LOCALE=fr_FR`).

Voici des solutions alternatives à l'utilisation de `QWebEngineView`, ainsi que des options pour contourner le problème de traduction sans changer de composant, en tenant compte de votre environnement (Ubuntu, PyQt5 5.15.11 via pip, Python 3.13.5).

---

### Solution 1 : Remplacer `QWebEngineView` par `QTextBrowser`
`QTextBrowser` est un widget Qt natif qui peut afficher du contenu HTML simple et prend en charge les traductions Qt standards (`qtbase_fr.qm`), déjà fonctionnelles dans votre application. Contrairement à `QWebEngineView`, il ne dépend pas de traductions spécifiques à WebEngine et son menu contextuel sera automatiquement en français si `qtbase_fr.qm` est chargé.

#### Modifications dans `preview.py`
Remplacez la classe `MarkdownPreview` pour utiliser `QTextBrowser` au lieu de `QWebEngineView`. Voici un exemple de code modifié :

```python
"""
# Copyright (C) 2025 Jean-Marc DIGNE
# ... (licence inchangée)
Composant d'aperçu HTML du Markdown avec QTextBrowser
"""

import os
from xml.etree import ElementTree
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextBrowser
from PyQt5.QtCore import Qt
from pygments.formatters import HtmlFormatter
from markdown.inlinepatterns import InlineProcessor
import markdown


class TagInlineProcessor(InlineProcessor):
    """Traite les tags @@tag en les entourant d'une balise span."""
    def handleMatch(self, m, data):
        el = ElementTree.Element("span")
        el.set("class", "tag")
        el.text = m.group(0)
        return el, m.start(0), m.end(0)


class MarkdownPreview(QWidget):
    """Aperçu HTML avec QTextBrowser"""
    def __init__(self):
        super().__init__()
        self.current_html = ""
        self.current_markdown = ""
        self.setup_ui()
        self.default_css = self._load_default_css()
        self.pygments_css = HtmlFormatter(style="default").get_style_defs(".highlight")
        self.custom_css = ""
        self.setup_markdown()

    def setup_ui(self):
        """Configuration de l'interface de prévisualisation"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel("Aperçu HTML")
        label.setStyleSheet(
            """
            QLabel {
                background-color: #f6f8fa;
                padding: 8px 12px;
                font-weight: bold;
                color: #24292e;
                border: 1px solid #d1d5da;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            """
        )
        header_layout.addWidget(label)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.web_view = QTextBrowser()
        self.web_view.setOpenExternalLinks(True)
        self.web_view.setStyleSheet(
            """
            QTextBrowser {
                border: 1px solid #d1d5da;
                border-radius: 4px;
                background-color: white;
            }
            """
        )
        layout.addWidget(self.web_view, 1)
        self.setLayout(layout)
        self.show_welcome_content()

    def setup_markdown(self):
        """Configuration du processeur Markdown"""
        self.md = markdown.Markdown(
            extensions=[
                "tables",
                "fenced_code",
                "codehilite",
                "toc",
                "attr_list",
                "def_list",
                "footnotes",
                "md_in_html",
                "sane_lists",
                "smarty",
                "pymdownx.tilde",
                "pymdownx.mark",
            ],
            extension_configs={
                "codehilite": {"css_class": "highlight", "use_pygments": True},
                "toc": {"permalink": True},
            },
        )
        markdown.etree = ElementTree
        self.md.inlinePatterns.register(
            TagInlineProcessor(r"@@(\w{2,})\b", self.md), "tag", 175
        )

    def _load_css_from_file(self, filename):
        """Charge le contenu d'un fichier CSS depuis le répertoire des thèmes."""
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            css_path = os.path.join(
                base_path, "..", "resources", "css_preview", filename
            )
            with open(css_path, "r", encoding="utf-8") as f:
                return f.read()
        except (FileNotFoundError, IOError) as e:
            print(f"⚠️ Erreur: Impossible de charger le fichier CSS '{filename}': {e}")
            return f"/* CSS '{filename}' non trouvé */"

    def _load_default_css(self):
        """Charge le contenu du fichier CSS par défaut."""
        return self._load_css_from_file("default_preview.css")

    def set_css_theme(self, theme_filename):
        """Définit et applique un nouveau thème CSS pour l'aperçu."""
        if not theme_filename:
            theme_filename = "default_preview.css"
        self.default_css = self._load_css_from_file(theme_filename)
        if self.current_markdown:
            self.update_content(self.current_markdown)

    def create_html_template(self, content):
        """Créer le template HTML complet"""
        toc_html = ""
        if hasattr(self.md, "toc") and self.md.toc:
            toc_html = (
                f'<div class="toc"><h2>📋 Table des matières</h2>{self.md.toc}</div>'
            )
        final_css = self.default_css + self.pygments_css + self.custom_css
        return f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <title>BlueNotebook Preview</title>
            <style>
                {final_css}
            </style>
        </head>
        <body>
            {toc_html}
            {content}
        </body>
        </html>
        """

    def show_welcome_content(self):
        """Afficher le contenu de bienvenue"""
        welcome_content = """
        <div style="text-align: center; padding: 40px;">
            <h1>🔵 Bienvenue dans BlueNotebook</h1>
            <p><em>Commencez à taper du Markdown dans l'éditeur pour voir l'aperçu ici.</em></p>
            <!-- ... (contenu inchangé) ... -->
        </div>
        """
        self.web_view.setHtml(welcome_content)

    def update_content(self, markdown_content: str, journal_dir: str = None):
        """Mettre à jour le contenu de l'aperçu"""
        try:
            self.current_markdown = markdown_content
            if not markdown_content.strip():
                self.show_welcome_content()
                return
            self.md.reset()
            html_content = self.md.convert(markdown_content)
            full_html = self.create_html_template(html_content)
            self.web_view.setHtml(full_html)
            self.current_html = full_html
        except Exception as e:
            error_html = self.create_html_template(
                f"""
                <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 16px; border-radius: 4px;">
                    <h3>❌ Erreur de rendu</h3>
                    <p><strong>Erreur :</strong> {str(e)}</p>
                    <p><em>Vérifiez la syntaxe Markdown dans l'éditeur.</em></p>
                </div>
                """
            )
            self.web_view.setHtml(error_html)

    def get_html(self):
        """Récupérer le HTML complet pour l'export"""
        return self.current_html

    def scroll_to_percentage(self, percentage: float):
        """Fait défiler la vue à un pourcentage donné de la hauteur totale."""
        if not (0.0 <= percentage <= 1.0):
            return
        scrollbar = self.web_view.verticalScrollBar()
        scroll_height = scrollbar.maximum()
        target_pos = int(scroll_height * percentage)
        scrollbar.setValue(target_pos)
```

#### Changements clés
- **Remplacement de `QWebEngineView` par `QTextBrowser`** :
  - Importez `QTextBrowser` à la place de `QWebEngineView`.
  - Remplacez `self.web_view = QWebEngineView()` par `self.web_view = QTextBrowser()`.
  - Ajoutez `self.web_view.setOpenExternalLinks(True)` pour permettre l'ouverture des liens externes dans le navigateur par défaut.
- **Simplification de `scroll_to_percentage`** :
  - Remplacez le code JavaScript par une gestion directe du scrollbar de `QTextBrowser`, qui est plus simple et ne nécessite pas de JavaScript.
- **Suppression de `QUrl`** :
  - La méthode `setHtml` de `QTextBrowser` ne prend pas de `baseUrl`, donc l'argument `journal_dir` est ignoré (les liens relatifs peuvent nécessiter un ajustement si utilisés).

#### Avantages
- **Traductions** : Le menu contextuel de `QTextBrowser` (ex. : "Copier", "Coller") est géré par `qtbase_fr.qm`, déjà chargé dans `main.py` avec `BLUENOTEBOOK_LOCALE=fr_FR`. Aucun fichier de traduction supplémentaire n'est requis.
- **Simplicité** : Moins de dépendances (pas besoin de `PyQtWebEngine`).
- **Léger** : `QTextBrowser` est moins lourd que `QWebEngineView` (pas de moteur Chromium).

#### Inconvénients
- **Rendu HTML limité** : `QTextBrowser` supporte un sous-ensemble d'HTML/CSS (pas de JavaScript, rendu CSS limité). Certains styles avancés ou fonctionnalités interactives peuvent ne pas fonctionner correctement.
- **Images locales** : Les images référencées par des chemins locaux (ex. : `![](file://...)`) peuvent ne pas s'afficher sans configuration supplémentaire.
- **Performance** : Moins optimisé pour les documents HTML complexes par rapport à `QWebEngineView`.

#### Étapes supplémentaires
1. **Mettez à jour `requirements.txt`** :
   - Supprimez `PyQtWebEngine` et `PyQtWebEngine-Qt5` :
     ```
     PyQt5==5.15.11
     PyQt5-Qt5==5.15.17
     PyQt5_sip==12.17.0
     # PyQtWebEngine==5.15.7  # Supprimé
     # PyQtWebEngine-Qt5==5.15.17  # Supprimé
     ```
   - Réinstallez les dépendances :
     ```bash
     source ~/.pyenv/versions/.venv_bluenotebook/bin/activate
     pip install -r requirements.txt
     ```

2. **Testez** :
   - Relancez BlueNotebook :
     ```bash
     ./start_bluenotebook.sh
     ```
   - Vérifiez que l'aperçu HTML fonctionne et que le menu contextuel (clic droit) est en français.
   - Testez le rendu des documents Markdown complexes (tables, code, images, etc.) pour détecter d'éventuelles limitations.

3. **Ajustements si nécessaire** :
   - Si les images locales ne s'affichent pas, convertissez les chemins relatifs en absolus dans le Markdown ou ajoutez une base URL dans `update_content` :
     ```python
     def update_content(self, markdown_content: str, journal_dir: str = None):
         # ...
         if journal_dir:
             self.web_view.setSearchPaths([journal_dir])
         self.web_view.setHtml(full_html)
         # ...
     ```

---

### Solution 2 : Personnaliser le menu contextuel de `QWebEngineView`
Plutôt que de remplacer `QWebEngineView`, vous pouvez créer un menu contextuel personnalisé pour contourner la dépendance à `qtwebengine_fr.qm`. Cela permet de définir des actions en français directement dans votre code.

#### Modifications dans `preview.py`
Ajoutez un menu contextuel personnalisé à la classe `MarkdownPreview` :

```python
from PyQt5.QtWidgets import QMenu, QAction
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class MarkdownPreview(QWidget):
    def __init__(self):
        # ... (code existant)
        self.setup_ui()
        self.default_css = self._load_default_css()
        self.pygments_css = HtmlFormatter(style="default").get_style_defs(".highlight")
        self.custom_css = ""
        self.setup_markdown()
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        """Affiche un menu contextuel personnalisé."""
        menu = QMenu(self)
        
        # Actions en français
        copy_action = QAction("Copier", self)
        copy_action.triggered.connect(self.web_view.copy)
        menu.addAction(copy_action)

        paste_action = QAction("Coller", self)
        paste_action.triggered.connect(self.web_view.paste)
        menu.addAction(paste_action)

        select_all_action = QAction("Tout sélectionner", self)
        select_all_action.triggered.connect(self.web_view.selectAll)
        menu.addAction(select_all_action)

        # Afficher le menu au point cliqué
        menu.exec_(self.web_view.mapToGlobal(position))

    # ... (reste du code inchangé)
```

#### Changements clés
- **Désactiver le menu par défaut** : `setContextMenuPolicy(Qt.CustomContextMenu)` désactive le menu contextuel natif de `QWebEngineView`.
- **Menu personnalisé** : Crée un `QMenu` avec des actions en français ("Copier", "Coller", "Tout sélectionner") connectées aux méthodes correspondantes de `QWebEngineView`.
- **Langue** : Les libellés sont codés en dur en français, donc aucune dépendance à `qtwebengine_fr.qm`.

#### Avantages
- **Traductions garanties** : Le menu est en français sans besoin de fichiers de traduction externes.
- **Contrôle total** : Vous pouvez ajouter ou personnaliser les actions selon vos besoins.
- **Compatibilité** : Conserve toutes les fonctionnalités de `QWebEngineView` (rendu HTML/CSS avancé, JavaScript).

#### Inconvénients
- **Fonctionnalités limitées** : Le menu personnalisé ne reproduit pas toutes les actions du menu natif (ex. : "Inspecter", "Ouvrir le lien dans un nouvel onglet").
- **Maintenance** : Vous devez gérer manuellement les actions et leurs traductions.

#### Étapes
1. Appliquez la modification ci-dessus dans `preview.py`.
2. Testez :
   ```bash
   ./start_bluenotebook.sh
   ```
   - Faites un clic droit dans l'aperçu HTML et vérifiez que le menu affiche "Copier", "Coller", etc.
3. Ajoutez d'autres actions si nécessaire (ex. : "Recharger" avec `self.web_view.reload()`).

---

### Solution 3 : Utiliser un moteur Markdown externe (wkhtmltopdf ou WeasyPrint)
Au lieu d'utiliser `QWebEngineView` ou `QTextBrowser`, vous pouvez générer l'aperçu HTML en utilisant un moteur externe comme `wkhtmltopdf` ou `WeasyPrint` pour convertir le Markdown en HTML, puis l'afficher dans un widget simple comme `QLabel` ou `QTextBrowser`. Cela évite complètement Qt WebEngine.

#### Exemple avec `WeasyPrint`
1. **Installez WeasyPrint** :
   ```bash
   source ~/.pyenv/versions/.venv_bluenotebook/bin/activate
   pip install weasyprint
   ```
   Ajoutez à `requirements.txt` :
   ```
   weasyprint==62.3
   ```

2. **Modifiez `preview.py`** :
   ```python
   from weasyprint import HTML
   from PyQt5.QtWidgets import QTextBrowser

   class MarkdownPreview(QWidget):
       def __init__(self):
           # ... (code similaire à Solution 1, avec QTextBrowser)
           self.web_view = QTextBrowser()
           self.web_view.setOpenExternalLinks(True)
           # ...

       def update_content(self, markdown_content: str, journal_dir: str = None):
           try:
               self.current_markdown = markdown_content
               if not markdown_content.strip():
                   self.show_welcome_content()
                   return
               self.md.reset()
               html_content = self.md.convert(markdown_content)
               full_html = self.create_html_template(html_content)
               # Convertir en HTML statique avec WeasyPrint
               weasy_html = HTML(string=full_html)
               rendered_html = weasy_html.write_html()  # Génère HTML statique
               self.web_view.setHtml(rendered_html)
               self.current_html = rendered_html
           except Exception as e:
               error_html = self.create_html_template(
                   f"""
                   <div style="background-color: #ffebee; border-left: 4px solid #f44336; padding: 16px; border-radius: 4px;">
                       <h3>❌ Erreur de rendu</h3>
                       <p><strong>Erreur :</strong> {str(e)}</p>
                       <p><em>Vérifiez la syntaxe Markdown dans l'éditeur.</em></p>
                   </div>
                   """
               )
               self.web_view.setHtml(error_html)
   ```

3. **Testez** :
   - Relancez l'application et vérifiez le rendu de l'aperçu.

#### Avantages
- **Pas de dépendance WebEngine** : Élimine le besoin de `qtwebengine_fr.qm` et de `PyQtWebEngine`.
- **Traductions** : Utilise `QTextBrowser`, donc le menu contextuel est traduit via `qtbase_fr.qm`.

#### Inconvénients
- **Dépendances externes** : Nécessite l'installation de `weasyprint` et de ses dépendances système (ex. : `libpango`).
- **Rendu limité** : WeasyPrint est orienté vers le rendu statique (pas de JavaScript ni d'interactivité).

#### Installation des dépendances système
```bash
sudo apt install libpango-1.0-0 libpangocairo-1.0-0
```

---

### Solution 4 : Continuer avec Qt WebEngine et ignorer les traductions
Si remplacer `QWebEngineView` n'est pas souhaitable (car il offre un rendu HTML avancé), vous pouvez accepter que le menu contextuel reste en anglais et documenter cela comme une limitation connue. Cela évite tout changement de code ou installation supplémentaire.

- **Action** : Mettez à jour la documentation de BlueNotebook pour indiquer que le menu contextuel de l'aperçu HTML est en anglais en raison de l'absence de traductions Qt WebEngine.
- **Avantage** : Aucun changement requis, l'application reste fonctionnelle.
- **Inconvénient** : Moins convivial pour les utilisateurs francophones.

---

### Recommandation
- **Solution préférée** : **Solution 2 (Menu contextuel personnalisé)** est la plus rapide et conserve les fonctionnalités de `QWebEngineView` tout en garantissant un menu en français sans dépendre de `qtwebengine_fr.qm`. Elle est simple à implémenter et robuste.
- **Si rendu HTML simple suffisant** : Optez pour **Solution 1 (QTextBrowser)** pour éliminer la dépendance à Qt WebEngine et utiliser les traductions Qt standards déjà fonctionnelles.
- **Si rendu avancé requis** : Essayez **Solution 3 (WeasyPrint)** pour un compromis entre rendu de qualité et simplicité des traductions, mais cela ajoute une dépendance externe.
- **Dernier recours** : **Solution 4** si aucune autre option n'est viable.

### Vérifications supplémentaires
Si vous souhaitez persister avec Qt WebEngine et résoudre le problème de `qtwebengine_fr.qm` :
1. Vérifiez les fichiers `.pak` :
   ```bash
   find / -name "fr.pak" 2>/dev/null
   ```
   - Si trouvé, essayez la modification de `main.py` avec `QWebEngineSettings` (voir réponse précédente).
2. Vérifiez les paquets installés :
   ```bash
   apt list --installed | grep -E 'qtwebengine|qt5|qttranslations'
   ```
3. Clonez le dépôt `qttranslations` pour explorer les fichiers disponibles :
   ```bash
   git clone https://code.qt.io/qt/qttranslations.git
   cd qttranslations
   git checkout 5.15.2
   find translations -name "*fr*.ts"
   ```

### Conclusion
Remplacer `QWebEngineView` par `QTextBrowser` (Solution 1) ou créer un menu contextuel personnalisé (Solution 2) sont les approches les plus pratiques pour contourner l'absence de `qtwebengine_fr.qm`. La Solution 2 est particulièrement adaptée si vous souhaitez conserver le rendu HTML avancé de `QWebEngineView`. Si vous choisissez de poursuivre avec Qt WebEngine, fournissez la sortie des commandes ci-dessus pour explorer d'autres chemins de traduction ou confirmer la structure du dépôt Qt.

Quelle solution préférez-vous ? Si vous avez besoin d'aide pour implémenter l'une d'elles ou pour déboguer davantage, partagez les résultats des vérifications demandées.
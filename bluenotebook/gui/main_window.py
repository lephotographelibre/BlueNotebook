"""
Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import os
from datetime import datetime
from pathlib import Path
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QMenuBar,
    QMenu,
    QAction,
    QFileDialog,
    QMessageBox,
    QStatusBar,
    QLabel,
    QDialog,
    QDialogButtonBox,
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence, QIcon, QFont

from .editor import MarkdownEditor
from .preview import MarkdownPreview


class MainWindow(QMainWindow):
    def __init__(self, journal_dir_arg=None, app_version="1.0.0"):
        super().__init__()
        self.journal_dir_arg = journal_dir_arg
        self.app_version = app_version
        self.journal_directory = None
        self.current_file = None
        self.is_modified = False

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        self.setup_journal_directory()

        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)

        self.load_initial_file()

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        self.setWindowTitle(f"BlueNotebook V{self.app_version} - Éditeur Markdown")
        self.setGeometry(100, 100, 1400, 900)

        # Définir l'icône de l'application
        self.set_application_icon()

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        # Splitter pour séparer éditeur et aperçu
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(8)
        splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #dee2e6;
                border: 1px solid #adb5bd;
                border-radius: 3px;
            }
            
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """
        )

        # Zone d'édition (gauche)
        self.editor = MarkdownEditor()
        splitter.addWidget(self.editor)

        # Zone d'aperçu (droite)
        self.preview = MarkdownPreview()
        splitter.addWidget(self.preview)

        # Configuration du splitter
        # Répartition 50/50 par défaut
        splitter.setSizes([700, 700])

        # Empêcher la fermeture complète des panneaux
        splitter.setCollapsible(0, False)  # Éditeur
        splitter.setCollapsible(1, False)  # Aperçu

        # Tailles minimales pour éviter les problèmes d'affichage
        self.editor.setMinimumWidth(300)
        self.preview.setMinimumWidth(300)

        # Ajouter le splitter au layout principal
        main_layout.addWidget(splitter)

    def set_application_icon(self):
        """Définir l'icône de l'application"""
        import os

        # Chemins possibles pour l'icône
        icon_paths = [
            "resources/icons/bluenotebook.ico",
            "resources/icons/bluenotebook.png",
            "resources/icons/bluenotebook_64.png",
            "bluenotebook.ico",
            "bluenotebook.png",
        ]

        for icon_path in icon_paths:
            if os.path.exists(icon_path):
                try:
                    icon = QIcon(icon_path)
                    if not icon.isNull():
                        self.setWindowIcon(icon)
                        # Définir aussi l'icône de l'application
                        from PyQt5.QtWidgets import QApplication

                        QApplication.instance().setWindowIcon(icon)
                        print(f"✅ Icône chargée : {icon_path}")
                        return
                except Exception as e:
                    print(f"⚠️ Erreur lors du chargement de {icon_path}: {e}")
                    continue

        print("ℹ️ Aucune icône trouvée, utilisation de l'icône par défaut")

    def setup_menu(self):
        """Configuration du menu"""
        menubar = self.menuBar()

        # Menu Fichier
        file_menu = menubar.addMenu("&Fichier")

        new_action = QAction("&Nouveau", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.setStatusTip("Créer un nouveau fichier")
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("&Ouvrir", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.setStatusTip("Ouvrir un fichier existant")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        open_journal_action = QAction("Ouvrir &Journal", self)
        open_journal_action.setStatusTip("Ouvrir un répertoire de journal")
        open_journal_action.triggered.connect(self.open_journal)
        file_menu.addAction(open_journal_action)

        file_menu.addSeparator()

        save_action = QAction("&Sauvegarder", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip("Sauvegarder le fichier")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Sauvegarder &sous...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.setStatusTip("Sauvegarder sous un nouveau nom")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("&Exporter HTML...", self)
        export_action.setStatusTip("Exporter en HTML")
        export_action.triggered.connect(self.export_html)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        quit_action = QAction("&Quitter", self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip("Quitter l'application")
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

        # Menu Edition
        edit_menu = menubar.addMenu("&Edition")

        undo_action = QAction("&Annuler", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.editor.undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("&Rétablir", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.editor.redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("&Rechercher", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.editor.show_find_dialog)
        edit_menu.addAction(find_action)

        # Menu Affichage
        view_menu = menubar.addMenu("&Affichage")

        toggle_preview = QAction("&Basculer l'aperçu", self)
        toggle_preview.setShortcut("F5")
        toggle_preview.triggered.connect(self.toggle_preview)
        view_menu.addAction(toggle_preview)

        # Menu Aide
        help_menu = menubar.addMenu("&Aide")

        about_action = QAction("À &propos", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self.statusbar.addWidget(self.file_label)

        # Label pour le répertoire du journal
        self.journal_dir_label = QLabel("")
        self.statusbar.addWidget(self.journal_dir_label)

        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)

        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)

    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)

    def setup_journal_directory(self):
        """Initialise le répertoire du journal au lancement."""
        journal_path = None

        # 1. Argument de la ligne de commande
        if self.journal_dir_arg and Path(self.journal_dir_arg).is_dir():
            journal_path = Path(self.journal_dir_arg).resolve()

        # 2. Variable d'environnement
        elif (
            "JOURNAL_DIRECTORY" in os.environ
            and Path(os.environ["JOURNAL_DIRECTORY"]).is_dir()
        ):
            journal_path = Path(os.environ["JOURNAL_DIRECTORY"]).resolve()

        # 3. Répertoire par défaut dans le dossier utilisateur
        else:
            default_dir = Path.home() / "bluenotebook"
            if default_dir.is_dir():
                journal_path = default_dir.resolve()
            else:
                # 4. Créer le répertoire par défaut s'il n'existe pas
                try:
                    default_dir.mkdir(parents=True, exist_ok=True)
                    journal_path = default_dir.resolve()
                except OSError as e:
                    QMessageBox.warning(
                        self,
                        "Erreur de Journal",
                        f"Impossible de créer le répertoire de journal par défaut:\n{e}",
                    )
                    journal_path = None

        self.journal_directory = journal_path
        self.update_journal_dir_label()

    def update_journal_dir_label(self):
        """Met à jour le label du répertoire de journal dans la barre de statut."""
        if self.journal_directory:
            self.journal_dir_label.setText(f"Journal: {self.journal_directory}")
        else:
            self.journal_dir_label.setText("Journal: Non défini")

    def load_initial_file(self):
        """Charge le fichier journal du jour s'il existe, sinon un nouveau fichier."""
        if self.journal_directory:
            today_str = datetime.now().strftime("%Y%m%d")
            journal_file_path = self.journal_directory / f"{today_str}.md"

            if journal_file_path.exists():
                self.open_specific_file(str(journal_file_path))
                return

        # Si le fichier du jour n'existe pas ou si le répertoire n'est pas défini
        self.new_file()

    def on_text_changed(self):
        """Appelé quand le texte change"""
        self.is_modified = True
        self.update_title()
        self.update_stats()

        # Démarrer le timer pour la mise à jour de l'aperçu
        self.update_timer.start(300)  # 300ms de délai

    def update_preview(self):
        """Mettre à jour l'aperçu"""
        content = self.editor.get_text()
        self.preview.update_content(content)

    def update_title(self):
        """Mettre à jour le titre de la fenêtre"""
        if self.current_file:
            filename = os.path.basename(self.current_file)
            self.file_label.setText(filename)
        else:
            filename = "Nouveau fichier"
            self.file_label.setText(filename)

        if self.is_modified:
            self.setWindowTitle(
                f"BlueNotebook V{self.app_version} - {filename} *"
            )  # Déjà correct, mais je vérifie
            self.modified_label.setText("●")
        else:
            self.setWindowTitle(
                f"BlueNotebook V{self.app_version} - {filename}"
            )  # Déjà correct, mais je vérifie
            self.modified_label.setText("")

    def update_stats(self):
        """Mettre à jour les statistiques du document"""
        content = self.editor.get_text()
        lines = len(content.splitlines())
        words = len(content.split())
        chars = len(content)

        self.stats_label.setText(f"{lines} lignes | {words} mots | {chars} caractères")

    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            self.editor.set_text(
                """# Bienvenue dans BlueNotebook

## Éditeur Markdown moderne

**BlueNotebook** est un éditeur de texte Markdown avec aperçu en temps réel.

### Fonctionnalités

- ✏️ **Édition** avec coloration syntaxique
- 👀 **Aperçu HTML** en temps réel
- 💾 **Sauvegarde** automatique
- 🚀 **Interface moderne** avec PyQt5

### Syntaxe Markdown

Voici quelques exemples de syntaxe Markdown :

#### Mise en forme du texte
- **Gras** : `**texte**` ou `__texte__`
- *Italique* : `*texte*` ou `_texte_`
- `Code inline` : `code`

#### Listes
1. Premier élément
2. Deuxième élément
   - Sous-élément
   - Autre sous-élément

#### Code
```python
def hello_world():
    print("Hello, BlueNotebook!")
```

#### Citations
> Ceci est une citation
> sur plusieurs lignes

#### Liens et images
[Lien vers un site](https://example.com)

---

Commencez à taper pour voir la magie opérer ! ✨
"""
            )
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()

    def open_journal(self):
        """Ouvre un dialogue pour sélectionner un nouveau répertoire de journal."""
        dir_name = QFileDialog.getExistingDirectory(
            self, "Sélectionner le répertoire du Journal"
        )
        if dir_name:
            new_journal_path = Path(dir_name).resolve()
            if new_journal_path.is_dir():
                self.journal_directory = new_journal_path
                self.update_journal_dir_label()
                QMessageBox.information(
                    self,
                    "Journal",
                    f"Le répertoire du journal est maintenant :\n{self.journal_directory}",
                )

    def open_file(self):
        """Ouvrir un fichier"""
        if self.check_save_changes():
            filename, _ = QFileDialog.getOpenFileName(
                self,
                "Ouvrir un fichier Markdown",
                "",
                "Fichiers Markdown (*.md *.markdown *.txt);;Tous les fichiers (*)",
            )

            self.open_specific_file(filename)

    def open_specific_file(self, filename):
        """Ouvre un fichier spécifique depuis son chemin."""
        if not filename:
            return

        try:
            with open(filename, "r", encoding="utf-8") as f:
                content = f.read()

            self.editor.set_text(content)
            self.current_file = filename
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self.update_preview()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ouvrir le fichier :\n{str(e)}"
            )

    def save_file(self):
        """Sauvegarder le fichier"""
        # Logique de sauvegarde dans le journal
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Sauvegarde impossible",
                "Le répertoire du journal n'est pas défini.",
            )
            return

        today_str = datetime.now().strftime("%Y%m%d")
        journal_file_path = self.journal_directory / f"{today_str}.md"

        if journal_file_path.exists():
            # Le fichier journal du jour existe déjà, demander à l'utilisateur
            dialog = QDialog(self)
            dialog.setWindowTitle("Fichier Journal déjà existant")
            layout = QVBoxLayout()
            layout.addWidget(
                QLabel(f"Le fichier journal '{journal_file_path.name}' existe déjà.")
            )

            buttons = QDialogButtonBox()
            replace_button = buttons.addButton(
                "Remplacer", QDialogButtonBox.DestructiveRole
            )
            append_button = buttons.addButton(
                "Ajouter à la fin", QDialogButtonBox.AcceptRole
            )
            cancel_button = buttons.addButton("Annuler", QDialogButtonBox.RejectRole)
            layout.addWidget(buttons)
            dialog.setLayout(layout)

            # Connecter les boutons aux actions
            replace_button.clicked.connect(lambda: dialog.done(1))  # 1 pour Remplacer
            append_button.clicked.connect(lambda: dialog.done(2))  # 2 pour Ajouter
            cancel_button.clicked.connect(dialog.reject)

            result = dialog.exec_()

            if result == 1:  # Remplacer
                self._save_to_file(str(journal_file_path))
            elif result == 2:  # Ajouter
                self._append_to_file(str(journal_file_path))
            else:  # Annuler
                return
        else:
            # Nouveau fichier journal pour aujourd'hui
            self._save_to_file(str(journal_file_path))

        # Mettre à jour l'état de l'application
        self.current_file = str(journal_file_path)
        self.update_title()

    def save_file_as(self):
        """Sauvegarder sous"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le fichier",
            "",
            "Fichiers Markdown (*.md);;Fichiers texte (*.txt);;Tous les fichiers (*)",
        )

        if filename:
            if not filename.endswith((".md", ".markdown", ".txt")):
                filename += ".md"

            self._save_to_file(filename)
            self.current_file = filename
            self.update_title()

    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            content = self.editor.get_text()
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)

            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2000)

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible de sauvegarder le fichier :\n{str(e)}"
            )

    def _append_to_file(self, filename):
        """Ajoute le contenu de l'éditeur à la fin d'un fichier."""
        try:
            content = self.editor.get_text()
            with open(filename, "a", encoding="utf-8") as f:
                f.write(
                    "\n\n---\n\n" + content
                )  # Ajoute un séparateur pour la lisibilité

            self.is_modified = False
            self.update_title()
            self.statusbar.showMessage(f"Contenu ajouté à : {filename}", 2000)
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ajouter au fichier :\n{str(e)}"
            )

    def export_html(self):
        """Exporter en HTML"""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter en HTML",
            "",
            "Fichiers HTML (*.html);;Tous les fichiers (*)",
        )

        if filename:
            if not filename.endswith(".html"):
                filename += ".html"

            try:
                html_content = self.preview.get_html()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html_content)

                self.statusbar.showMessage(f"Exporté en HTML : {filename}", 3000)

            except Exception as e:
                QMessageBox.critical(
                    self, "Erreur", f"Impossible d'exporter en HTML :\n{str(e)}"
                )

    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()

    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            f"""<h2>BlueNotebook V{self.app_version}</h2>
            <p><b>Éditeur de journal Markdown moderne</b></p> 
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Édition avec coloration syntaxique</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML</li>
            <li>Interface moderne</li>
            </ul>
            <p>Dépôt GitHub : <a href="https://github.com/lephotographelibre/BlueNotebook">BlueNotebook</a></p>
            <p>© 2024 BlueNotebook</p>""",
        )

    def check_save_changes(self):
        """Vérifier si il faut sauvegarder les modifications"""
        if self.is_modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
                QMessageBox.Save,
            )

            if reply == QMessageBox.Save:
                self.save_file()
                return not self.is_modified  # Retourner False si la sauvegarde a échoué
            elif reply == QMessageBox.Cancel:
                return False

        return True

    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            event.accept()
        else:
            event.ignore()

"""
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

Fenêtre principale de BlueNotebook - Éditeur Markdown avec PyQt5
"""

import webbrowser
import locale
import functools
import os
import shutil
import zipfile
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
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtCore import QThreadPool
from PyQt5.QtGui import QKeySequence, QIcon, QFont
from PyQt5.QtGui import QColor

from .editor import MarkdownEditor
from .preview import MarkdownPreview
from .navigation import NavigationPanel
from .outline import OutlinePanel
from .preferences_dialog import PreferencesDialog
from core.quote_fetcher import QuoteFetcher  # noqa


class MainWindow(QMainWindow):
    def __init__(self, journal_dir_arg=None, app_version="1.0.0"):
        super().__init__()
        self.journal_dir_arg = journal_dir_arg
        self.app_version = app_version
        self.journal_directory = None
        self.current_file = None
        self.is_modified = False
        self.daily_quote = None
        self.daily_author = None
        # Importer ici pour éviter les dépendances circulaires si nécessaire
        from core.settings import SettingsManager

        self.settings_manager = SettingsManager()

        # Initialiser le pool de threads pour les tâches de fond
        self.thread_pool = QThreadPool()

        self.setup_ui()
        self.apply_settings()  # Appliquer les paramètres au démarrage
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()
        self.setup_journal_directory()

        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)

        self.load_initial_file()
        self.show_quote_of_the_day()
        self.start_initial_indexing()
        self.update_calendar_highlights()

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

        # Splitter principal pour séparer la navigation du reste
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(8)
        main_splitter.setStyleSheet(
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

        # Panneau de navigation (gauche)
        self.navigation_panel = NavigationPanel()
        main_splitter.addWidget(self.navigation_panel)

        # Panneau du plan (milieu)
        self.outline_panel = OutlinePanel()
        main_splitter.addWidget(self.outline_panel)

        # Splitter secondaire pour séparer éditeur et aperçu
        editor_preview_splitter = QSplitter(Qt.Horizontal)
        editor_preview_splitter.setHandleWidth(8)
        editor_preview_splitter.setStyleSheet(
            """
            QSplitter::handle {
                background-color: #dee2e6;
            }
            QSplitter::handle:hover {
                background-color: #3498db;
            }
        """
        )

        # Zone d'édition (gauche)
        self.editor = MarkdownEditor(main_window=self)
        editor_preview_splitter.addWidget(self.editor)

        # Zone d'aperçu (droite)
        self.preview = MarkdownPreview()
        editor_preview_splitter.addWidget(self.preview)

        # Configuration du splitter
        # Répartition 50/50 par défaut
        editor_preview_splitter.setSizes([700, 700])

        # Empêcher la fermeture complète des panneaux
        editor_preview_splitter.setCollapsible(0, False)  # Éditeur
        editor_preview_splitter.setCollapsible(1, False)  # Aperçu

        # Tailles minimales pour éviter les problèmes d'affichage
        self.editor.setMinimumWidth(300)
        self.preview.setMinimumWidth(300)

        # Ajouter le splitter secondaire au splitter principal
        main_splitter.addWidget(editor_preview_splitter)

        # Configuration du splitter principal
        # Fixer la largeur du panneau de navigation
        self.navigation_panel.setFixedWidth(350)
        self.outline_panel.setFixedWidth(350)
        main_splitter.setSizes([350, 350, 1000])  # Ajuster les tailles initiales
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(2, False)

        # Ajouter le splitter au layout principal
        main_layout.addWidget(main_splitter)

    def set_application_icon(self):
        """Définir l'icône de l'application"""
        # Utiliser le chemin du fichier actuel pour construire des chemins absolus
        base_path = os.path.dirname(os.path.abspath(__file__))

        # Chemins possibles pour l'icône
        icon_paths = [
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook.ico"),
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook.png"),
            os.path.join(base_path, "..", "resources", "icons", "bluenotebook_64.png"),
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

        self._create_actions()

        # Menu Fichier
        file_menu = menubar.addMenu("📁 &Fichier")
        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addSeparator()
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(self.open_journal_action)
        file_menu.addAction(self.backup_journal_action)
        file_menu.addAction(self.restore_journal_action)
        file_menu.addSeparator()
        file_menu.addAction(self.export_action)
        file_menu.addSeparator()
        file_menu.addAction(self.preferences_action)
        file_menu.addSeparator()
        file_menu.addAction(self.quit_action)

        # Menu Edition
        edit_menu = menubar.addMenu("✏️ &Edition")
        edit_menu.addAction(self.undo_action)
        edit_menu.addAction(self.redo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.find_action)

        # Menu Affichage
        view_menu = menubar.addMenu("👁️ &Affichage")
        view_menu.addAction(self.toggle_navigation_action)
        view_menu.addAction(self.toggle_outline_action)
        view_menu.addAction(self.toggle_preview_action)

        # Menu Formatter
        format_menu = menubar.addMenu("🎨 F&ormater")
        self._setup_format_menu(format_menu)

        # Menu Insérer (maintenant au premier niveau)
        insert_menu = menubar.addMenu("➕ &Insérer")
        self._setup_insert_menu(insert_menu)

        # Menu Aide
        help_menu = menubar.addMenu("❓ &Aide")
        help_menu.addAction(self.online_help_action)
        help_menu.addAction(self.about_action)

    def _create_actions(self):
        """Crée toutes les actions de l'application."""
        self.new_action = QAction(  # noqa
            "📄 Nouveau",
            self,
            shortcut=QKeySequence.New,
            statusTip="Créer un nouveau fichier",
            triggered=self.new_file,
        )
        self.open_action = QAction(
            "📂 Ouvrir",
            self,
            shortcut=QKeySequence.Open,
            statusTip="Ouvrir un fichier existant",
            triggered=self.open_file,
        )
        self.open_journal_action = QAction(
            "📓 Ouvrir Journal",
            self,
            statusTip="Ouvrir un répertoire de journal",
            triggered=self.open_journal,
        )
        self.save_action = QAction(
            "💾 Sauvegarder",
            self,
            shortcut=QKeySequence.Save,
            statusTip="Sauvegarder le fichier",
            triggered=self.save_file,
        )
        self.save_as_action = QAction(
            "💾 Sauvegarder sous...",
            self,
            shortcut=QKeySequence.SaveAs,
            statusTip="Sauvegarder sous un nouveau nom",
            triggered=self.save_file_as,
        )
        self.backup_journal_action = QAction(
            "💾 Sauvegarde Journal...",
            self,
            statusTip="Sauvegarder le journal complet dans une archive ZIP",
            triggered=self.backup_journal,
        )
        self.restore_journal_action = QAction(
            "🔄 Restauration Journal...",
            self,
            statusTip="Restaurer le journal depuis une archive ZIP",
            triggered=self.restore_journal,
        )
        self.export_action = QAction(
            "🌐 Exporter HTML...",
            self,
            statusTip="Exporter en HTML",
            triggered=self.export_html,
        )
        self.preferences_action = QAction(
            "⚙️ Préférences...",
            self,
            statusTip="Ouvrir les préférences de l'application",
            triggered=self.open_preferences,
        )
        self.quit_action = QAction(
            "🚪 Quitter",
            self,
            shortcut=QKeySequence.Quit,
            statusTip="Quitter l'application",
            triggered=self.close,
        )

        self.undo_action = QAction(
            "↩️ Annuler", self, shortcut=QKeySequence.Undo, triggered=self.editor.undo
        )
        self.redo_action = QAction(
            "↪️ Rétablir", self, shortcut=QKeySequence.Redo, triggered=self.editor.redo
        )
        self.find_action = QAction(
            "🔍 Rechercher",
            self,
            shortcut=QKeySequence.Find,
            triggered=self.editor.show_find_dialog,
        )

        self.toggle_navigation_action = QAction(
            "🧭 Basculer Navigation",
            self,
            shortcut="F6",
            triggered=self.toggle_navigation,
        )

        self.toggle_outline_action = QAction(
            "📜 Basculer Plan du document",
            self,
            shortcut="F7",
            triggered=self.toggle_outline,
        )

        self.toggle_preview_action = QAction(
            "👁️ Basculer Aperçu HTML", self, shortcut="F5", triggered=self.toggle_preview
        )

        self.about_action = QAction(
            "ℹ️ À propos",
            self,
            triggered=self.show_about,
        )

        self.online_help_action = QAction(
            "🌐 Documentation en ligne",
            self,
            triggered=self.show_online_help,
        )

    def _setup_format_menu(self, format_menu):
        """Configure le menu de formatage de manière dynamique."""
        # --- Sous-menu Titre ---
        title_menu = QMenu("📜 Titres", self)
        title_actions_data = [
            ("1️⃣ Niv 1 (#)", "h1"),
            ("2️⃣ Niv 2 (##)", "h2"),
            ("3️⃣ Niv 3 (###)", "h3"),
            ("4️⃣ Niv 4 (####)", "h4"),
            ("5️⃣ Niv 5 (#####)", "h5"),
        ]
        for name, data in title_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            title_menu.addAction(action)
        format_menu.addMenu(title_menu)

        # --- Sous-menu Style de texte ---
        style_menu = QMenu("🎨 Style de texte", self)
        style_actions_data = [
            ("🅱️ Gras (**texte**)", "bold", QKeySequence.Bold),
            ("*️⃣ Italique (*texte*)", "italic"),  # Raccourci Ctrl+I retiré
            ("~ Barré (~~texte~~)", "strikethrough"),
            ("🖍️ Surligné (==texte==)", "highlight"),
        ]
        for name, data, *shortcut in style_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            if shortcut:
                action.setShortcut(shortcut[0])
            style_menu.addAction(action)
        format_menu.addMenu(style_menu)

        # --- Sous-menu Code ---
        code_menu = QMenu("💻 Code", self)
        code_actions_data = [
            ("` Monospace (inline)", "inline_code"),
            ("``` Bloc de code", "code_block"),
        ]
        for name, data in code_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            code_menu.addAction(action)
        format_menu.addMenu(code_menu)

        # --- Sous-menu Listes ---
        list_menu = QMenu("📋 Listes", self)
        list_actions_data = [
            ("• Liste non ordonnée", "ul"),
            ("1. Liste ordonnée", "ol"),
            ("☑️ Liste de tâches", "task_list"),
        ]
        for name, data in list_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            list_menu.addAction(action)
        format_menu.addMenu(list_menu)

        format_menu.addSeparator()

        # --- Action RaZ ---
        clear_action = QAction("🧹 RaZ (Effacer le formatage)", self)
        clear_action.triggered.connect(self.editor.clear_formatting)
        format_menu.addAction(clear_action)

    def _setup_insert_menu(self, insert_menu):
        """Configure le menu d'insertion de manière dynamique."""
        insert_actions_data = [
            ("🔗 Lien (URL ou email) (<url>)", "url"),
            (
                "🖼️ Image (<img ...>)",
                "image",
                QKeySequence.Italic,
            ),  # Raccourci Ctrl+I
            ("🔗 Lien Markdown (texte)", "markdown_link"),
        ]

        for name, data, *shortcut in insert_actions_data:
            action = QAction(name, self)
            action.triggered.connect(
                lambda checked=False, d=data: self.editor.format_text(d)
            )
            if shortcut:
                action.setShortcut(shortcut[0])
            insert_menu.addAction(action)

        insert_internal_link_action = QAction("🔗 Fichier", self)
        insert_internal_link_action.triggered.connect(
            lambda: self.editor.format_text("internal_link")
        )
        insert_menu.addAction(insert_internal_link_action)
        insert_menu.addSeparator()

        # Actions statiques
        insert_hr_action = QAction("➖ Ligne Horizontale", self)
        insert_hr_action.triggered.connect(lambda: self.editor.format_text("hr"))
        insert_table_action = QAction("▦ Tableau", self)
        insert_table_action.triggered.connect(lambda: self.editor.format_text("table"))
        insert_quote_action = QAction("💬 Citation", self)
        insert_quote_action.triggered.connect(lambda: self.editor.format_text("quote"))
        insert_quote_day_action = QAction("✨ Citation du jour", self)
        insert_quote_day_action.triggered.connect(
            lambda: self.editor.format_text("quote_of_the_day")
        )

        insert_menu.addAction(insert_hr_action)
        insert_menu.addAction(insert_table_action)
        insert_menu.addAction(insert_quote_action)
        insert_menu.addAction(insert_quote_day_action)
        insert_menu.addSeparator()

        insert_tag_action = QAction("🏷️ Tag (@@)", self)
        insert_tag_action.triggered.connect(lambda: self.editor.format_text("tag"))
        insert_menu.addAction(insert_tag_action)

        insert_time_action = QAction("🕒 Heure", self)
        insert_time_action.triggered.connect(lambda: self.editor.format_text("time"))
        insert_menu.addAction(insert_time_action)
        insert_menu.addSeparator()

        # --- Sous-menu Insérer ---
        # V1.1.9 Le menu est maintenant créé dans _setup_format_menu
        # insert_menu = QMenu("➕ Insérer", self)
        insert_menu = QMenu("➕ Insérer", self)  # noqa
        insert_actions_data = [
            ("🔗 Lien (URL ou email) (<url>)", "url"),
            (
                "🖼️ Image (<img ...>)",
                "image",
                QKeySequence.Italic,
            ),  # Raccourci Ctrl+I ajouté ici
            ("🔗 Lien Markdown (texte)", "markdown_link"),
        ]

        # --- Sous-menu Emoji ---
        emoji_menu = QMenu("😊 Emoji", self)
        emoji_actions_data = [
            ("📖 Livre", "📖"),
            ("🎵 Musique", "🎵"),
            ("📚 À Lire", "📚"),
            ("🎬 À Regarder", "🎬"),
            ("🎧 A Ecouter", "🎧"),
            ("✈️ Voyage", "✈️"),
            ("❤️ Santé", "❤️"),
            ("☀️ Soleil", "☀️"),
            ("☁️ Nuage", "☁️"),
            ("🌧️ Pluie", "🌧️"),
            ("🌬️ Vent", "🌬️"),
            ("😊 Content", "😊"),
            ("😠 Mécontent", "😠"),
            ("😢 Triste", "😢"),
        ]
        for name, emoji in emoji_actions_data:
            action = QAction(
                name, self, triggered=functools.partial(self.editor.insert_text, emoji)
            )
            emoji_menu.addAction(action)
        insert_menu.addMenu(emoji_menu)

    def setup_statusbar(self):
        """Configuration de la barre de statut"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Indicateur du fichier actuel
        self.file_label = QLabel("Nouveau fichier")
        self._set_file_label_color("white")  # Couleur par défaut à l'ouverture
        self.statusbar.addWidget(self.file_label)

        # Label pour le répertoire du journal
        self.journal_dir_label = QLabel("")
        self.journal_dir_label.setStyleSheet("color: #3498db;")  # Bleu clair
        self.statusbar.addWidget(self.journal_dir_label)

        # Indicateur de modification
        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)

        # Statistiques du document
        self.stats_label = QLabel("")
        self.statusbar.addPermanentWidget(self.stats_label)

        # Label pour le statut de l'indexation des tags
        self.tag_index_status_label = QLabel("")
        self.tag_index_status_label.setStyleSheet("color: green;")
        self.statusbar.addPermanentWidget(self.tag_index_status_label)

    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.text_edit.verticalScrollBar().valueChanged.connect(
            self.sync_preview_scroll
        )
        self.navigation_panel.prev_day_button_clicked.connect(
            self.on_prev_day_button_clicked
        )
        self.navigation_panel.next_day_button_clicked.connect(
            self.on_next_day_button_clicked
        )
        self.navigation_panel.today_button_clicked.connect(self.on_today_button_clicked)
        self.navigation_panel.date_clicked.connect(self.on_calendar_date_clicked)
        self.outline_panel.item_clicked.connect(self.on_outline_item_clicked)

    def setup_journal_directory(self):
        """Initialise le répertoire du journal au lancement."""
        journal_path = None

        # 1. Argument de la ligne de commande
        if self.journal_dir_arg and Path(self.journal_dir_arg).is_dir():
            journal_path = Path(self.journal_dir_arg).resolve()

        # 2. Variable d'environnement
        elif "JOURNAL_DIRECTORY" in os.environ:
            env_path = Path(os.environ["JOURNAL_DIRECTORY"])
            if env_path.is_dir():
                journal_path = env_path.resolve()

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
        if self.journal_directory:
            print(f"📓 Répertoire du journal: {self.journal_directory}")
        else:
            print("⚠️ Répertoire du journal non défini.")

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
        self.outline_panel.update_outline(self.editor.text_edit.document())

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
            self._set_file_label_color("red")
            self.setWindowTitle(
                f"BlueNotebook V{self.app_version} - {filename} *"
            )  # Déjà correct, mais je vérifie
            self.modified_label.setText("●")
        else:
            # Ne pas changer la couleur ici, elle sera gérée par les actions (save, open)
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

    # V1.1.13 Changement de la page par defaut de l'editeur
    def new_file(self):
        """Créer un nouveau fichier"""
        if self.check_save_changes():
            # Configurer la locale en français pour avoir les noms des jours/mois
            try:
                locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
            except locale.Error:
                locale.setlocale(locale.LC_TIME, "")  # Utiliser la locale système

            today_str = datetime.now().strftime("%A %d %B %Y").title()
            template = f"""______________________________________________________________

# {today_str}

______________________________________________________________

# TODO

- [ ] tache 1
- [ ] tache 2
- [ ] tache 3
- [ ] tache 4

______________________________________________________________
# Activités & Notes




# Pour Demain



# Liens




"""
            self.editor.set_text(template)
            self.current_file = None
            self.is_modified = False
            self.update_title()
            self.update_stats()
            self._set_file_label_color("white")
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
                self.start_initial_indexing()  # Relancer l'indexation
                self.update_calendar_highlights()  # Mettre à jour le calendrier

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
            self._set_file_label_color("white")
            self.update_preview()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur", f"Impossible d'ouvrir le fichier :\n{str(e)}"
            )

    def save_file(self):
        """Sauvegarder le fichier"""
        # Si aucun répertoire de journal n'est défini, on fait un "Sauvegarder sous"
        if not self.journal_directory:
            self.save_file_as()
            return

        # Déterminer le chemin du fichier à sauvegarder
        file_to_save_path = None
        if self.current_file:
            # Si un fichier est déjà ouvert, on le sauvegarde
            file_to_save_path = Path(self.current_file)
        else:
            # Si c'est un nouveau fichier, il devient la note du jour
            today_str = datetime.now().strftime("%Y%m%d")
            file_to_save_path = self.journal_directory / f"{today_str}.md"

        # Si le fichier à sauvegarder n'est pas dans le répertoire du journal,
        # on fait une sauvegarde simple.
        if not str(file_to_save_path).startswith(str(self.journal_directory)):
            self._save_to_file(str(file_to_save_path))
            return

        journal_file_path = file_to_save_path

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
            self._set_file_label_color("green")
            # V1.1.18 Issue #6 2000 -> 2
            self.statusbar.showMessage(f"Fichier sauvegardé : {filename}", 2)

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
            self._set_file_label_color("green")
            self.statusbar.showMessage(f"Contenu ajouté à : {filename}", 2)
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

    def backup_journal(self):
        """Sauvegarde le répertoire du journal dans une archive ZIP."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Sauvegarde impossible",
                "Aucun répertoire de journal n'est actuellement défini.",
            )
            return

        # Générer un nom de fichier de sauvegarde par défaut
        backup_filename_default = f"BlueNotebook-Backup-{self.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d')}.zip"

        # Ouvrir une boîte de dialogue pour choisir l'emplacement de la sauvegarde
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le journal",
            backup_filename_default,
            "Archives ZIP (*.zip)",
            options=QFileDialog.DontConfirmOverwrite,
        )

        if not backup_path:
            return  # L'utilisateur a annulé

        # Vérifier si le fichier existe et demander confirmation si nécessaire
        if os.path.exists(backup_path):
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Fichier existant")
            msg_box.setText(
                f"Le fichier '{os.path.basename(backup_path)}' existe déjà.\n\n"
                "Voulez-vous le remplacer ?"
            )
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.button(QMessageBox.Yes).setText("Valider")
            msg_box.button(QMessageBox.No).setText("Annuler")
            msg_box.setDefaultButton(QMessageBox.No)
            reply = msg_box.exec_()

            if reply == QMessageBox.No:
                self.statusbar.showMessage("Sauvegarde annulée.", 3000)
                return

        try:
            # Créer l'archive ZIP
            shutil.make_archive(
                base_name=os.path.splitext(backup_path)[0],
                format="zip",
                root_dir=self.journal_directory,
            )
            self.statusbar.showMessage(f"Journal sauvegardé dans {backup_path}", 5000)
            QMessageBox.information(
                self,
                "Sauvegarde terminée",
                f"Le journal a été sauvegardé avec succès dans :\n{backup_path}",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erreur de sauvegarde", f"La sauvegarde a échoué : {e}"
            )

    def restore_journal(self):
        """Restaure un journal depuis une archive ZIP."""
        if not self.journal_directory:
            QMessageBox.warning(
                self,
                "Restauration impossible",
                "Aucun répertoire de journal de destination n'est défini.",
            )
            return

        # Sélectionner l'archive à restaurer
        zip_path, _ = QFileDialog.getOpenFileName(
            self, "Restaurer le journal", "", "Archives ZIP (*.zip)"
        )

        if not zip_path:
            return

        # Nom du backup pour le journal existant
        current_journal_backup_path = (
            f"{self.journal_directory}.bak-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        )

        # Fenêtre de confirmation personnalisée
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Confirmation de la restauration")
        msg_box.setTextFormat(Qt.RichText)  # Interpréter le texte comme du HTML
        msg_box.setText(
            f"<p>Vous êtes sur le point de restaurer le journal depuis '{os.path.basename(zip_path)}'.</p>"
            f"<p>Le journal actuel sera d'abord sauvegardé ici :<br><b>{current_journal_backup_path}</b></p>"
            f"<p>L'application va devoir être redémarrée après la restauration. Continuer ?</p>"
        )
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.button(QMessageBox.Yes).setText("Valider")
        msg_box.button(QMessageBox.No).setText("Annuler")
        msg_box.setDefaultButton(QMessageBox.No)
        reply = msg_box.exec_()

        if reply == QMessageBox.No:
            return

        try:
            # 1. Sauvegarder (renommer) le journal actuel
            os.rename(self.journal_directory, current_journal_backup_path)

            # 2. Créer le répertoire de destination vide
            os.makedirs(self.journal_directory)

            # 3. Extraire l'archive
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.journal_directory)

            QMessageBox.information(
                self,
                "Restauration terminée",
                "La restauration est terminée. L'application va maintenant se fermer.\n"
                "Veuillez la relancer pour utiliser le journal restauré.",
            )
            # Fermer l'application pour forcer un rechargement propre
            self.close()

        except Exception as e:
            QMessageBox.critical(
                self, "Erreur de restauration", f"La restauration a échoué : {e}"
            )

    def toggle_preview(self):
        """Basculer la visibilité de l'aperçu"""
        if self.preview.isVisible():
            self.preview.hide()
        else:
            self.preview.show()

    def toggle_navigation(self):
        """Basculer la visibilité du panneau de navigation."""
        if self.navigation_panel.isVisible():
            self.navigation_panel.hide()
        else:
            self.navigation_panel.show()

    def toggle_outline(self):
        """Basculer la visibilité du panneau de plan."""
        if self.outline_panel.isVisible():
            self.outline_panel.hide()
        else:
            self.outline_panel.show()

    def show_online_help(self):
        """Affiche la page d'aide HTML dans le navigateur par défaut."""
        # Construire le chemin vers le fichier d'aide
        base_path = os.path.dirname(os.path.abspath(__file__))
        help_file_path = os.path.join(
            base_path, "..", "resources", "html", "aide_en_ligne.html"
        )

        if os.path.exists(help_file_path):
            # Convertir le chemin en URL de fichier
            url = f"file:///{os.path.abspath(help_file_path)}"
            webbrowser.open(url)
        else:
            QMessageBox.warning(
                self,
                "Aide non trouvée",
                f"Le fichier d'aide n'a pas été trouvé:\n{help_file_path}",
            )

    def show_about(self):
        """Afficher la boîte À propos"""
        QMessageBox.about(
            self,
            "À propos de BlueNotebook",
            f"""<h2>BlueNotebook V{self.app_version}</h2>
            <p><b>Éditeur de journal Markdown </b></p> 
            <p>Un éditeur de texte Markdown avec aperçu en temps réel, 
            développé avec PyQt5 et QWebEngine.</p>
            <p>Très inspiré du logiciel <a href="https://github.com/jendrikseipp/rednotebook">RedNotebook</a>  développé par Jendrik Seipp</p>
            <p><b>Fonctionnalités :</b></p>
            <ul>
            <li>Gestion d'un journal<li>
            <li>Sauvegarde Automatique (soon)</li>
            <li>Édition avec coloration syntaxique</li>
            <li>Extensions Markdown surligné, barré</li>
            <li>Aperçu HTML en temps réel</li>
            <li>Export HTML des pages du journal</li>
            <li>Export PDF du journal complet ou partiel (soon)</li>
            <li>Gestion de Templates (soon)</li>
            <li>Gestion de tags / Recherche par tags (soon)</li>
            </ul>
            <p>Dépôt GitHub : <a href="https://github.com/lephotographelibre/BlueNotebook">BlueNotebook</a></p>
            <p>Licence : <a href="https://www.gnu.org/licenses/gpl-3.0.html">GNU GPLv3</a></p>
            <p>© 2025 BlueNotebook by Jean-Marc DIGNE</p>""",
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

    def show_quote_of_the_day(self):
        """Affiche la citation du jour dans une boîte de dialogue."""
        # Vérifier si l'affichage est activé dans les paramètres
        if self.settings_manager.get("integrations.show_quote_of_the_day"):
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()
            if self.daily_quote and self.daily_author:
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Citation du Jour")
                msg_box.setText(
                    f"<blockquote><i>« {self.daily_quote} »</i></blockquote>"
                )
                msg_box.setInformativeText(f"<b>{self.daily_author}</b>")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setStandardButtons(QMessageBox.Ok)
                msg_box.exec_()

    def sync_preview_scroll(self, value):
        """Synchronise le défilement de l'aperçu avec celui de l'éditeur."""
        editor_scrollbar = self.editor.text_edit.verticalScrollBar()
        preview_page = self.preview.web_view.page()

        # Calculer la position relative (0.0 à 1.0)
        scroll_max = editor_scrollbar.maximum()
        if scroll_max == 0:
            relative_pos = 0.0
        else:
            relative_pos = value / scroll_max

        # Exécuter un script JavaScript pour faire défiler la page web
        js_code = f"window.scrollTo(0, document.body.scrollHeight * {relative_pos});"
        preview_page.runJavaScript(js_code)

    def start_initial_indexing(self):
        """Lance l'indexation des tags pour le répertoire de journal actuel."""
        # Importer ici pour éviter les dépendances circulaires si nécessaire
        from core.tag_indexer import start_tag_indexing

        start_tag_indexing(
            self.journal_directory, self.thread_pool, self.on_indexing_finished
        )

    def on_indexing_finished(self, unique_tag_count):
        """Callback exécuté à la fin de l'indexation."""
        if unique_tag_count >= 0:
            message = f"Index Tags Terminé: {unique_tag_count} tags uniques trouvés."
            print(f"✅ {message}")
            self.tag_index_status_label.setText(message)
            # Optionnel: faire disparaître le message après quelques secondes
            QTimer.singleShot(10000, lambda: self.tag_index_status_label.clear())
        else:
            message = "Erreur d'indexation des tags."
            print(f"⚠️ {message}")
            self.tag_index_status_label.setText(message)

    def on_prev_day_button_clicked(self):
        """
        Appelé lors du clic sur 'Jour Précédent'.
        Trouve la note existante la plus proche avant la date actuelle et l'ouvre.
        """
        if not self.journal_directory:
            return

        # Déterminer la date de départ pour la recherche
        start_date = QDate.currentDate()
        if self.current_file:
            try:
                filename = Path(self.current_file).stem
                current_date_obj = datetime.strptime(filename, "%Y%m%d").date()
                start_date = QDate(
                    current_date_obj.year,
                    current_date_obj.month,
                    current_date_obj.day,
                )
            except ValueError:
                # Le fichier actuel n'est pas une note de journal, on part d'aujourd'hui
                pass

        # Chercher la note précédente en remontant dans le temps
        current_check_date = start_date.addDays(-1)
        # Limiter la recherche pour éviter une boucle infinie (ex: 5 ans)
        for _ in range(365 * 5):
            filename = current_check_date.toString("yyyyMMdd") + ".md"
            file_path = self.journal_directory / filename

            if file_path.exists():
                # Note trouvée ! On met à jour le calendrier et on l'ouvre.
                self.navigation_panel.calendar.setSelectedDate(current_check_date)
                self.on_calendar_date_clicked(current_check_date)
                return  # Sortir de la fonction

            # Passer au jour précédent
            current_check_date = current_check_date.addDays(-1)

        # Si on arrive ici, aucune note précédente n'a été trouvée
        self.statusbar.showMessage(
            "Aucune note précédente trouvée dans le journal.", 3000
        )

    def on_next_day_button_clicked(self):
        """
        Appelé lors du clic sur 'Jour Suivant'.
        Trouve la note existante la plus proche après la date actuelle et l'ouvre.
        """
        if not self.journal_directory:
            return

        # Déterminer la date de départ pour la recherche
        start_date = QDate.currentDate()
        if self.current_file:
            try:
                filename = Path(self.current_file).stem
                current_date_obj = datetime.strptime(filename, "%Y%m%d").date()
                start_date = QDate(
                    current_date_obj.year,
                    current_date_obj.month,
                    current_date_obj.day,
                )
            except ValueError:
                # Le fichier actuel n'est pas une note de journal, on part d'aujourd'hui
                pass

        # Chercher la note suivante en avançant dans le temps
        current_check_date = start_date.addDays(1)
        # Limiter la recherche pour éviter une boucle infinie (ex: 5 ans)
        for _ in range(365 * 5):
            filename = current_check_date.toString("yyyyMMdd") + ".md"
            file_path = self.journal_directory / filename

            if file_path.exists():
                # Note trouvée ! On met à jour le calendrier et on l'ouvre.
                self.navigation_panel.calendar.setSelectedDate(current_check_date)
                self.on_calendar_date_clicked(current_check_date)
                return  # Sortir de la fonction

            # Passer au jour suivant
            current_check_date = current_check_date.addDays(1)

        # Si on arrive ici, aucune note suivante n'a été trouvée
        self.statusbar.showMessage(
            "Aucune note suivante trouvée dans le journal.", 3000
        )

    def on_today_button_clicked(self):
        """
        Appelé lorsque le bouton 'Aujourd'hui' est cliqué.
        Sélectionne la date du jour et ouvre la note correspondante.
        """
        today = QDate.currentDate()
        self.navigation_panel.calendar.setSelectedDate(today)
        self.on_calendar_date_clicked(today)

    def on_calendar_date_clicked(self, date):
        """
        Appelé lorsqu'une date est cliquée dans le calendrier.
        Ouvre le fichier journal correspondant.
        """
        if not self.journal_directory:
            return

        # Formater la date en nom de fichier (YYYYMMDD.md)
        filename = date.toString("yyyyMMdd") + ".md"
        file_path = self.journal_directory / filename

        # Vérifier si le fichier existe
        if file_path.exists():
            # Vérifier si le fichier en cours a des modifications non sauvegardées
            if self.check_save_changes():
                self.open_specific_file(str(file_path))
        else:
            self.statusbar.showMessage(
                f"Aucune note pour le {date.toString('dd/MM/yyyy')}", 3000
            )

    # V1.5.2 Fix Issue #10 Claude - Sync btw Outline and Editor
    def on_outline_item_clicked(self, position):
        """
        Déplace le curseur vers la position cliquée dans le plan et fait défiler
        la vue pour que la ligne du titre soit exactement à la première ligne de l'éditeur.
        """
        # Importer QTextCursor si nécessaire
        from PyQt5.QtGui import QTextCursor

        # Déplacer le curseur à la position du titre
        block = self.editor.text_edit.document().findBlock(position)
        cursor = self.editor.text_edit.textCursor()
        cursor.setPosition(block.position())
        self.editor.text_edit.setTextCursor(cursor)

        # Solution robuste : utiliser QTextEdit.scrollToAnchor
        # Créer un nom d'ancre temporaire basé sur la position
        anchor_name = f"heading_{block.blockNumber()}"

        # Méthode alternative plus directe :
        # Forcer le scroll en utilisant la scrollbar directement
        scrollbar = self.editor.text_edit.verticalScrollBar()

        # Obtenir le rectangle du curseur après l'avoir positionné
        text_edit = self.editor.text_edit

        # S'assurer que le curseur est visible d'abord
        text_edit.ensureCursorVisible()

        # Maintenant, ajuster pour que ce soit en haut
        # On va utiliser une approche itérative pour être sûr
        for attempt in range(3):  # Maximum 3 tentatives
            cursor_rect = text_edit.cursorRect()

            # Si le curseur est déjà proche du haut (moins de 20 pixels), c'est bon
            if cursor_rect.top() <= 20:
                break

            # Calculer combien on doit scroller vers le haut
            scroll_adjustment = cursor_rect.top() - 10  # 10 pixels de marge en haut

            # Appliquer l'ajustement
            current_scroll = scrollbar.value()
            new_scroll = current_scroll + scroll_adjustment
            new_scroll = max(0, min(new_scroll, scrollbar.maximum()))

            scrollbar.setValue(new_scroll)

            # Laisser le temps au widget de se mettre à jour
            from PyQt5.QtWidgets import QApplication

            QApplication.processEvents()

        # Donner le focus à l'éditeur
        text_edit.setFocus()

    def update_calendar_highlights(self):
        """Scanne le répertoire du journal et met en évidence les dates dans le calendrier."""
        if not self.journal_directory:
            return

        dates_with_notes = set()
        try:
            for filename in os.listdir(self.journal_directory):
                if filename.endswith(".md"):
                    # Essayer de parser le nom du fichier en date
                    try:
                        date_str = os.path.splitext(filename)[0]
                        date = datetime.strptime(date_str, "%Y%m%d").date()
                        dates_with_notes.add(QDate(date.year, date.month, date.day))
                    except ValueError:
                        # Ignorer les fichiers qui ne correspondent pas au format YYYYMMDD.md
                        continue
            self.navigation_panel.highlight_dates(dates_with_notes)
        except FileNotFoundError:
            print(
                f"⚠️ Répertoire du journal non trouvé pour la mise à jour du calendrier: {self.journal_directory}"
            )

    def _set_file_label_color(self, color):
        """Définit la couleur du texte pour le label du nom de fichier."""
        self.file_label.setStyleSheet(f"color: {color};")

    def open_preferences(self):
        """Ouvre la boîte de dialogue des préférences."""
        dialog = PreferencesDialog(self.settings_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            # Sauvegarder les nouveaux paramètres
            self.settings_manager.set(
                "editor.font_family", dialog.current_font.family()
            )
            self.settings_manager.set(
                "editor.font_size", dialog.current_font.pointSize()
            )
            self.settings_manager.set(
                "editor.background_color", dialog.current_color.name()
            )
            self.settings_manager.set(
                "editor.text_color", dialog.current_text_color.name()
            )
            self.settings_manager.set(
                "editor.heading_color", dialog.current_heading_color.name()
            )
            self.settings_manager.set(
                "editor.selection_text_color",
                dialog.current_selection_text_color.name(),
            )
            self.settings_manager.set(
                "integrations.show_quote_of_the_day",
                dialog.show_quote_checkbox.isChecked(),
            )
            self.settings_manager.set(
                "ui.show_navigation_panel", dialog.show_nav_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_outline_panel", dialog.show_outline_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_preview_panel", dialog.show_preview_checkbox.isChecked()
            )

            self.settings_manager.save_settings()
            self.apply_settings()

    def apply_settings(self):
        """Applique les paramètres chargés à l'interface utilisateur."""
        # --- Visibilité des panneaux ---
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        self.navigation_panel.setVisible(show_nav)

        show_outline = self.settings_manager.get("ui.show_outline_panel", True)
        self.outline_panel.setVisible(show_outline)

        show_preview = self.settings_manager.get("ui.show_preview_panel", False)
        self.preview.setVisible(show_preview)

        # Appliquer la police
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        font = QFont(font_family, font_size)
        self.editor.set_font(font)

        # Appliquer la couleur de fond
        bg_color = self.settings_manager.get("editor.background_color")
        self.editor.set_background_color(bg_color)

        # Appliquer la couleur du texte
        text_color = self.settings_manager.get("editor.text_color")
        self.editor.set_text_color(text_color)

        # Appliquer la couleur des titres
        heading_color = self.settings_manager.get("editor.heading_color")
        self.editor.set_heading_color(heading_color)

        # Appliquer la couleur du texte de sélection
        selection_text_color = self.settings_manager.get("editor.selection_text_color")
        self.editor.set_selection_text_color(selection_text_color)

        # Appliquer les styles au panneau de plan
        self.outline_panel.apply_styles(font, QColor(heading_color), QColor(bg_color))

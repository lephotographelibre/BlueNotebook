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
import json
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
from .word_cloud import WordCloudPanel
from core.default_excluded_words import DEFAULT_EXCLUDED_WORDS
from core.word_indexer import start_word_indexing


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
        self.tag_index_count = -1
        self.word_index_count = -1
        # Importer ici pour éviter les dépendances circulaires si nécessaire
        from core.settings import SettingsManager

        self.settings_manager = SettingsManager()

        # Initialiser le pool de threads pour les tâches de fond
        self.thread_pool = QThreadPool()

        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.apply_settings()  # Appliquer les paramètres au démarrage
        self.setup_connections()
        self.setup_journal_directory()

        # Timer pour mettre à jour l'aperçu (évite les mises à jour trop fréquentes)
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.update_preview)

        # V1.7.2beta3 - Timer pour la synchronisation du curseur
        self.cursor_sync_timer = QTimer()
        self.cursor_sync_timer.setSingleShot(True)
        self.cursor_sync_timer.timeout.connect(self.sync_preview_to_cursor)

        # V1.7.6 - Lancer les tâches de fond après que la fenêtre principale soit prête
        # Utiliser un QTimer.singleShot(0, ...) garantit que ces opérations
        # ne bloquent pas l'affichage initial de l'interface.
        QTimer.singleShot(0, self.run_startup_tasks)

    def run_startup_tasks(self):
        """Exécute les tâches qui peuvent être lancées après l'affichage de l'UI."""
        self.load_initial_file()
        self.show_quote_of_the_day()  # Affiche la citation si l'option est activée
        self.start_initial_indexing()  # Lance l'indexation en arrière-plan
        self.update_calendar_highlights()  # Met à jour le calendrier

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
        self.navigation_panel.setFixedWidth(400)
        self.outline_panel.setFixedWidth(400)
        main_splitter.setSizes([400, 400, 1000])  # Ajuster les tailles initiales
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

        # Menu Intégrations
        integrations_menu = menubar.addMenu("🔌 &Intégrations")
        integrations_menu.addAction(self.insert_quote_day_action)

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
            "🧭 Basculer Navigation Journal",
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
            "💡 À propos",
            self,
            triggered=self.show_about,
        )

        self.online_help_action = QAction(
            "🌐 Documentation en ligne",
            self,
            triggered=self.show_online_help,
        )

        self.insert_quote_day_action = QAction(
            "✨ Citation du jour",
            self,
            triggered=self.insert_quote_of_the_day,
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
            ("🖼️ Image (<img ...>)", "image", QKeySequence.Italic),
            (
                "🖼️ Image Markdown",
                "markdown_image",
                QKeySequence("Ctrl+Shift+I"),
            ),
            ("🔗 Lien (URL ou email) (<url>)", "url"),
            ("🔗 Lien Markdown (texte)", "markdown_link"),
        ]

        for name, data, *shortcut in insert_actions_data:
            action = QAction(name, self)
            # Utilisation de functools.partial pour éviter le problème de closure de lambda dans une boucle
            action.triggered.connect(functools.partial(self.editor.format_text, data))
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

        insert_comment_action = QAction("💬 Commentaire HTML", self)
        insert_comment_action.triggered.connect(
            lambda: self.editor.format_text("html_comment")
        )

        insert_table_action = QAction("▦ Tableau", self)
        insert_table_action.triggered.connect(lambda: self.editor.format_text("table"))
        insert_quote_action = QAction("💬 Citation", self)
        insert_quote_action.triggered.connect(lambda: self.editor.format_text("quote"))

        insert_menu.addAction(insert_hr_action)
        insert_menu.addAction(insert_comment_action)
        insert_menu.addAction(insert_table_action)
        insert_menu.addAction(insert_quote_action)
        # L'action "Citation du jour" est maintenant dans le menu "Intégrations"
        # insert_menu.addAction(self.insert_quote_day_action)
        insert_menu.addSeparator()

        insert_tag_action = QAction("🏷️ Tag (@@)", self)
        insert_tag_action.triggered.connect(lambda: self.editor.format_text("tag"))
        insert_menu.addAction(insert_tag_action)

        insert_time_action = QAction("🕒 Heure", self)
        insert_time_action.triggered.connect(lambda: self.editor.format_text("time"))
        insert_menu.addAction(insert_time_action)  # noqa
        insert_menu.addSeparator()  # noqa

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

        # --- Widgets de gauche ---
        self.file_label = QLabel("Nouveau fichier")
        self._set_file_label_color("gray")  # Couleur par défaut à l'ouverture
        self.statusbar.addWidget(self.file_label)

        self.modified_label = QLabel("")
        self.statusbar.addWidget(self.modified_label)

        self.stats_label = QLabel("")
        self.statusbar.addWidget(self.stats_label)

        # --- Widgets de droite ---
        self.journal_dir_label = QLabel("")
        self.journal_dir_label.setStyleSheet("color: #3498db;")  # Bleu clair
        self.statusbar.addPermanentWidget(self.journal_dir_label)

        # Label pour le statut de l'indexation des tags
        self.tag_index_status_label = QLabel("")
        self.tag_index_status_label.setStyleSheet(
            "color: #3498db;"
        )  # Même couleur que le journal
        self.statusbar.addPermanentWidget(self.tag_index_status_label)

    def setup_connections(self):
        """Configuration des connexions de signaux"""
        self.editor.textChanged.connect(self.on_text_changed)
        self.editor.text_edit.verticalScrollBar().valueChanged.connect(
            self.sync_preview_scroll
        )
        self.editor.cursorPositionChanged.connect(
            lambda: self.cursor_sync_timer.start(100)
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
        self.navigation_panel.tag_search_triggered.connect(self.perform_search)
        self.navigation_panel.file_open_requested.connect(self.open_file_from_search)

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
            self._set_file_label_color("gray")
            self.update_preview()
            self.expand_outline()

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
                self.update_word_cloud()
                self.update_tag_cloud()

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
            self._set_file_label_color("gray")
            self.update_preview()
            self.expand_outline()

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

        # --- Déterminer le répertoire de départ pour la sauvegarde ---
        # Priorité 1: Variable d'environnement
        initial_dir = os.getenv("BACKUP__DIRECTORY")
        if not initial_dir or not os.path.isdir(initial_dir):
            # Priorité 2: Dernier répertoire utilisé dans les paramètres
            initial_dir = self.settings_manager.get("backup.last_directory")
            if not initial_dir or not os.path.isdir(initial_dir):
                # Par défaut: le dossier parent du journal
                initial_dir = str(self.journal_directory.parent)

        # Générer un nom de fichier de sauvegarde par défaut
        backup_filename_default = f"BlueNotebook-Backup-{self.journal_directory.name}-{datetime.now().strftime('%Y-%m-%d-%H-%M')}.zip"

        # Construire le chemin complet par défaut
        default_path = os.path.join(initial_dir, backup_filename_default)

        # Ouvrir une boîte de dialogue pour choisir l'emplacement de la sauvegarde
        backup_path, _ = QFileDialog.getSaveFileName(
            self,
            "Sauvegarder le journal",
            default_path,  # Utiliser le chemin complet avec le répertoire initial
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

            # Mémoriser le répertoire de la sauvegarde réussie
            new_backup_dir = os.path.dirname(backup_path)
            self.settings_manager.set("backup.last_directory", new_backup_dir)
            self.settings_manager.save_settings()

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
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setWindowTitle("Modifications non sauvegardées")
            msg_box.setText(
                "Le fichier a été modifié. Voulez-vous sauvegarder les modifications ?"
            )
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            msg_box.button(QMessageBox.Save).setText("Sauvegarder")
            msg_box.button(QMessageBox.Discard).setText("Ne pas sauvegarder")
            msg_box.button(QMessageBox.Cancel).setText("Annuler")
            msg_box.setDefaultButton(QMessageBox.Save)

            reply = msg_box.exec_()
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
            # Sauvegarder les paramètres de visibilité des panneaux
            self.save_panel_visibility_settings()
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

    def insert_quote_of_the_day(self):
        """Insère la citation du jour dans l'éditeur, en la récupérant si nécessaire."""
        # Si la citation n'a pas encore été récupérée (car l'option au démarrage est désactivée),
        # on la récupère maintenant.
        if not self.daily_quote:
            self.daily_quote, self.daily_author = QuoteFetcher.get_quote_of_the_day()

        if self.daily_quote and self.daily_author:
            self.editor.format_text("quote_of_the_day")
        else:
            QMessageBox.warning(
                self, "Erreur", "Impossible de récupérer la citation du jour."
            )

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

    def sync_preview_to_cursor(self):
        """
        Synchronise la vue de l'aperçu sur la position actuelle du curseur
        dans l'éditeur.
        """
        cursor = self.editor.text_edit.textCursor()
        block = cursor.block()
        if not block.isValid():
            return

        total_blocks = self.editor.text_edit.document().blockCount()
        if total_blocks == 0:
            return

        # Calculer la position relative du bloc actuel
        relative_pos = block.blockNumber() / total_blocks

        # Demander à l'aperçu de défiler
        self.preview.scroll_to_percentage(relative_pos)

    def start_initial_indexing(self):
        """Lance l'indexation des tags pour le répertoire de journal actuel."""
        # Importer ici pour éviter les dépendances circulaires si nécessaire
        from core.tag_indexer import start_tag_indexing

        # Lancer l'indexation des tags
        start_tag_indexing(
            self.journal_directory, self.thread_pool, self.on_indexing_finished
        )

        # Lancer l'indexation des mots
        user_excluded = self.settings_manager.get("indexing.user_excluded_words", [])

        # Combiner les deux listes pour l'indexeur
        excluded_words_set = set(DEFAULT_EXCLUDED_WORDS) | set(user_excluded)
        start_word_indexing(
            self.journal_directory,
            excluded_words_set,
            self.thread_pool,
            self.on_word_indexing_finished,
        )

    def on_indexing_finished(self, unique_tag_count):
        """Callback exécuté à la fin de l'indexation."""
        self.tag_index_count = unique_tag_count
        self.update_indexing_status_label()

    def on_word_indexing_finished(self, unique_word_count):
        """Callback exécuté à la fin de l'indexation des mots."""
        self.word_index_count = unique_word_count
        self.update_indexing_status_label()

    def update_indexing_status_label(self):
        """Met à jour la barre de statut avec les résultats des deux indexations."""
        # Ne rien faire tant que les deux résultats ne sont pas arrivés
        if self.tag_index_count == -1 or self.word_index_count == -1:
            return

        tag_msg = "Erreur tags"
        if self.tag_index_count >= 0:
            tag_msg = f"{self.tag_index_count} tags"

        word_msg = "Erreur mots"
        if self.word_index_count >= 0:
            word_msg = f"{self.word_index_count} mots"

        full_message = f"Index: {tag_msg} | {word_msg}"
        print(f"✅ {full_message}")
        self.tag_index_status_label.setText(full_message)

        # Si l'option est décochée, le message est transitoire. Sinon, il est permanent.
        if not self.settings_manager.get("ui.show_indexing_stats", True):
            QTimer.singleShot(15000, lambda: self.tag_index_status_label.clear())
        self.update_tag_cloud()  # Mettre à jour le nuage après l'indexation
        self.update_word_cloud()
        self.update_navigation_panel_data()

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
        self.update_tag_cloud()
        self.update_word_cloud()

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
                "editor.list_color", dialog.current_list_color.name()
            )
            self.settings_manager.set(
                "editor.selection_text_color",
                dialog.current_selection_text_color.name(),
            )
            self.settings_manager.set(
                "editor.inline_code_text_color",
                dialog.current_inline_code_text_color.name(),
            )
            self.settings_manager.set(
                "editor.inline_code_background_color",
                dialog.current_inline_code_bg_color.name(),
            )
            self.settings_manager.set(
                "editor.code_block_background_color",
                dialog.current_code_block_bg_color.name(),
            )
            self.settings_manager.set(
                "editor.bold_color", dialog.current_bold_color.name()
            )
            self.settings_manager.set(
                "editor.italic_color", dialog.current_italic_color.name()
            )
            self.settings_manager.set(
                "editor.strikethrough_color",
                dialog.current_strikethrough_color.name(),
            )
            self.settings_manager.set(
                "editor.highlight_color",
                dialog.current_highlight_color.name(),
            )
            self.settings_manager.set(
                "editor.tag_color", dialog.current_tag_color.name()
            )
            self.settings_manager.set(
                "editor.timestamp_color", dialog.current_timestamp_color.name()
            )
            # V1.7.2 Ajout Paramètre Affichages Couleurs
            self.settings_manager.set(
                "editor.quote_color", dialog.current_quote_color.name()
            )
            self.settings_manager.set(
                "editor.link_color", dialog.current_link_color.name()
            )
            self.settings_manager.set(
                "editor.code_font_family", dialog.current_code_font.family()
            )
            self.settings_manager.set(
                "editor.html_comment_color",
                dialog.current_html_comment_color.name(),
            )
            # Fin V1.7.2

            self.settings_manager.set(
                "editor.show_line_numbers",
                dialog.show_line_numbers_checkbox.isChecked(),
            )

            self.settings_manager.set(
                "integrations.show_quote_of_the_day",
                dialog.show_quote_checkbox.isChecked(),
            )
            self.settings_manager.set(
                "ui.show_indexing_stats",
                dialog.show_indexing_stats_checkbox.isChecked(),
            )
            # V1.6.1 Mots à exclure
            user_words_text = dialog.excluded_words_edit.toPlainText()
            user_words_list = [
                word.strip().lower()
                for word in user_words_text.split(",")
                if word.strip()
            ]
            self.settings_manager.set("indexing.user_excluded_words", user_words_list)
            # V1.6.2 Tags à exclure du nuage
            excluded_tags_text = dialog.excluded_tags_edit.toPlainText()
            excluded_tags_list = [
                tag.strip().lower()
                for tag in excluded_tags_text.split(",")
                if tag.strip()
            ]
            self.settings_manager.set(
                "indexing.excluded_tags_from_cloud", excluded_tags_list
            )

            # Mots à exclure du nuage de mots
            excluded_words_cloud_text = dialog.excluded_words_cloud_edit.toPlainText()
            excluded_words_cloud_list = [
                word.strip().lower()
                for word in excluded_words_cloud_text.split(",")
                if word.strip()
            ]
            self.settings_manager.set(
                "indexing.excluded_words_from_cloud", excluded_words_cloud_list
            )

            # V1.7.8 - Correction régression: Sauvegarder l'état des cases à cocher des panneaux
            # et non l'état de visibilité actuel des panneaux.
            self.settings_manager.set(
                "ui.show_navigation_panel", dialog.show_nav_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_outline_panel", dialog.show_outline_checkbox.isChecked()
            )
            self.settings_manager.set(
                "ui.show_preview_panel", dialog.show_preview_checkbox.isChecked()
            )

            # *** CORRECTION PRINCIPALE : Sauvegarder IMMÉDIATEMENT les paramètres ***
            self.settings_manager.save_settings()

            # Appliquer les paramètres à l'interface
            self.apply_settings()

    def save_panel_visibility_settings(self):
        """Sauvegarde l'état de visibilité actuel des panneaux."""
        self.settings_manager.set(
            "ui.show_navigation_panel", self.navigation_panel.isVisible()
        )
        self.settings_manager.set(
            "ui.show_outline_panel", self.outline_panel.isVisible()
        )
        self.settings_manager.set("ui.show_preview_panel", self.preview.isVisible())
        self.settings_manager.save_settings()

    def closeEvent(self, event):
        """Événement de fermeture de la fenêtre"""
        if self.check_save_changes():
            # Sauvegarder UNIQUEMENT l'état de visibilité actuel des panneaux
            # (pas les autres paramètres qui sont déjà sauvegardés)
            self.save_panel_visibility_settings()
            event.accept()
        else:
            event.ignore()

    def apply_settings(self):
        """Applique les paramètres chargés à l'interface utilisateur."""
        # --- Visibilité des panneaux ---
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        self.navigation_panel.setVisible(show_nav)

        show_outline = self.settings_manager.get("ui.show_outline_panel", True)
        self.outline_panel.setVisible(show_outline)

        show_preview = self.settings_manager.get("ui.show_preview_panel", False)
        self.preview.setVisible(show_preview)

        # --- Visibilité des statistiques d'indexation ---
        show_stats = self.settings_manager.get("ui.show_indexing_stats", True)
        if not show_stats:
            self.tag_index_status_label.clear()

        # --- Appliquer la police de l'éditeur ---
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        font = QFont(font_family, font_size)
        self.editor.set_font(font)

        # --- Appliquer la couleur de fond ---
        bg_color = self.settings_manager.get("editor.background_color")
        self.editor.set_background_color(bg_color)

        # --- Appliquer la couleur du texte ---
        text_color = self.settings_manager.get("editor.text_color")
        self.editor.set_text_color(text_color)

        # --- Appliquer la couleur des titres ---
        heading_color = self.settings_manager.get("editor.heading_color")
        self.editor.set_heading_color(heading_color)

        # --- Appliquer la couleur des listes ---
        list_color = self.settings_manager.get("editor.list_color")
        self.editor.set_list_color(list_color)

        # --- Appliquer la couleur du texte de sélection ---
        selection_text_color = self.settings_manager.get("editor.selection_text_color")
        self.editor.set_selection_text_color(selection_text_color)

        # --- Appliquer les couleurs du code inline ---
        inline_text_color = self.settings_manager.get("editor.inline_code_text_color")
        inline_bg_color = self.settings_manager.get(
            "editor.inline_code_background_color"
        )
        self.editor.set_inline_code_colors(inline_text_color, inline_bg_color)

        # --- Appliquer la couleur de fond des blocs de code ---
        code_block_bg_color = self.settings_manager.get(
            "editor.code_block_background_color"
        )
        self.editor.set_code_block_background_color(code_block_bg_color)

        # --- Appliquer les couleurs des styles de texte ---
        bold_color = self.settings_manager.get("editor.bold_color")
        italic_color = self.settings_manager.get("editor.italic_color")
        strikethrough_color = self.settings_manager.get("editor.strikethrough_color")
        highlight_color = self.settings_manager.get("editor.highlight_color")
        self.editor.set_text_style_colors(
            bold_color, italic_color, strikethrough_color, highlight_color
        )

        # --- Appliquer les couleurs des tags et horodatage ---
        tag_color = self.settings_manager.get("editor.tag_color")
        timestamp_color = self.settings_manager.get("editor.timestamp_color")
        self.editor.set_misc_colors(tag_color, timestamp_color)

        # --- Appliquer les couleurs des citations et liens ---
        quote_color = self.settings_manager.get("editor.quote_color")
        link_color = self.settings_manager.get("editor.link_color")
        self.editor.set_quote_link_colors(quote_color, link_color)

        # --- Appliquer la police du code ---
        code_font = self.settings_manager.get("editor.code_font_family")
        self.editor.set_code_font(code_font)

        # --- Appliquer la couleur des commentaires HTML ---
        html_comment_color = self.settings_manager.get(
            "editor.html_comment_color", "#a4b5cf"
        )
        self.editor.set_html_comment_color(html_comment_color)

        # --- Appliquer les styles au panneau de plan ---
        self.outline_panel.apply_styles(font, QColor(heading_color), QColor(bg_color))

        """Applique les paramètres chargés à l'interface utilisateur."""
        # --- Visibilité des panneaux ---
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        self.navigation_panel.setVisible(show_nav)

        show_outline = self.settings_manager.get("ui.show_outline_panel", True)
        self.outline_panel.setVisible(show_outline)

        show_preview = self.settings_manager.get("ui.show_preview_panel", False)
        self.preview.setVisible(show_preview)

        # --- Visibilité des statistiques d'indexation ---
        show_stats = self.settings_manager.get("ui.show_indexing_stats", True)
        if not show_stats:
            self.tag_index_status_label.clear()

        # --- Appliquer la police de l'éditeur ---
        font_family = self.settings_manager.get("editor.font_family")
        font_size = self.settings_manager.get("editor.font_size")
        font = QFont(font_family, font_size)
        self.editor.set_font(font)

        # --- Appliquer la couleur de fond ---
        bg_color = self.settings_manager.get("editor.background_color")
        self.editor.set_background_color(bg_color)

        # --- Appliquer la couleur du texte ---
        text_color = self.settings_manager.get("editor.text_color")
        self.editor.set_text_color(text_color)

        # --- Appliquer la couleur des titres ---
        heading_color = self.settings_manager.get("editor.heading_color")
        self.editor.set_heading_color(heading_color)

        # --- Appliquer la couleur des listes ---
        list_color = self.settings_manager.get("editor.list_color")
        self.editor.set_list_color(list_color)

        # --- Appliquer la couleur du texte de sélection ---
        selection_text_color = self.settings_manager.get("editor.selection_text_color")
        self.editor.set_selection_text_color(selection_text_color)

        # --- Appliquer les couleurs du code inline ---
        inline_text_color = self.settings_manager.get("editor.inline_code_text_color")
        inline_bg_color = self.settings_manager.get(
            "editor.inline_code_background_color"
        )
        self.editor.set_inline_code_colors(inline_text_color, inline_bg_color)

        # --- Appliquer la couleur de fond des blocs de code ---
        code_block_bg_color = self.settings_manager.get(
            "editor.code_block_background_color"
        )
        self.editor.set_code_block_background_color(code_block_bg_color)

        # --- Appliquer les couleurs des styles de texte ---
        bold_color = self.settings_manager.get("editor.bold_color")
        italic_color = self.settings_manager.get("editor.italic_color")
        strikethrough_color = self.settings_manager.get("editor.strikethrough_color")
        highlight_color = self.settings_manager.get("editor.highlight_color")
        self.editor.set_text_style_colors(
            bold_color, italic_color, strikethrough_color, highlight_color
        )

        # --- Appliquer les couleurs des tags et horodatage ---
        tag_color = self.settings_manager.get("editor.tag_color")
        timestamp_color = self.settings_manager.get("editor.timestamp_color")
        self.editor.set_misc_colors(tag_color, timestamp_color)

        # --- Appliquer les couleurs des citations et liens ---
        quote_color = self.settings_manager.get("editor.quote_color")
        link_color = self.settings_manager.get("editor.link_color")
        self.editor.set_quote_link_colors(quote_color, link_color)

        # --- Appliquer la police du code ---
        code_font = self.settings_manager.get("editor.code_font_family")
        self.editor.set_code_font(code_font)

        # --- Appliquer la couleur des commentaires HTML ---
        html_comment_color = self.settings_manager.get(
            "editor.html_comment_color", "#a4b5cf"
        )
        self.editor.set_html_comment_color(html_comment_color)

        # --- Appliquer l'affichage des numéros de ligne ---
        show_line_numbers = self.settings_manager.get("editor.show_line_numbers", False)
        # La méthode set_line_numbers_visible doit être implémentée dans editor.py
        if hasattr(self.editor, "set_line_numbers_visible"):
            self.editor.set_line_numbers_visible(show_line_numbers)

        # --- Appliquer le thème CSS à l'aperçu HTML ---
        css_theme = self.settings_manager.get(
            "preview.css_theme", "default_preview.css"
        )
        self.preview.set_css_theme(css_theme)

        # --- Appliquer les styles au panneau de plan ---
        self.outline_panel.apply_styles(font, QColor(heading_color), QColor(bg_color))

    def _apply_theme_to_settings(self, theme_key):
        """Charge un thème et met à jour les paramètres en mémoire."""
        if theme_key:
            base_path = Path(__file__).parent.parent
            theme_path = base_path / "resources" / "themes" / f"{theme_key}.json"
            if theme_path.exists():
                try:
                    with open(theme_path, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)

                    # Écraser les paramètres d'affichage avec ceux du thème
                    font_info = theme_data.get("font", {})
                    self.settings_manager.set(
                        "editor.font_family", font_info.get("family")
                    )
                    self.settings_manager.set("editor.font_size", font_info.get("size"))
                    self.settings_manager.set(
                        "editor.code_font_family", font_info.get("code_family")
                    )

                    color_info = theme_data.get("colors", {})
                    for key, value in color_info.items():
                        self.settings_manager.set(f"editor.{key}", value)

                except (json.JSONDecodeError, IOError) as e:
                    print(f"⚠️ Erreur lors du chargement du thème au démarrage : {e}")

        # --- Visibilité des panneaux ---
        show_nav = self.settings_manager.get("ui.show_navigation_panel", False)
        self.navigation_panel.setVisible(show_nav)

        show_outline = self.settings_manager.get("ui.show_outline_panel", True)
        self.outline_panel.setVisible(show_outline)

        show_preview = self.settings_manager.get("ui.show_preview_panel", False)
        self.preview.setVisible(show_preview)

        # --- Visibilité des statistiques d'indexation ---
        show_stats = self.settings_manager.get("ui.show_indexing_stats", True)
        # Si l'option est désactivée, on s'assure que le label est vide au démarrage.
        if not show_stats:
            self.tag_index_status_label.clear()

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

        # Appliquer la couleur des listes
        list_color = self.settings_manager.get("editor.list_color")
        self.editor.set_list_color(list_color)

        # Appliquer la couleur du texte de sélection
        selection_text_color = self.settings_manager.get("editor.selection_text_color")
        self.editor.set_selection_text_color(selection_text_color)

        # Appliquer les couleurs du code inline
        inline_text_color = self.settings_manager.get("editor.inline_code_text_color")
        inline_bg_color = self.settings_manager.get(
            "editor.inline_code_background_color"
        )
        self.editor.set_inline_code_colors(inline_text_color, inline_bg_color)

        # Appliquer la couleur de fond des blocs de code
        code_block_bg_color = self.settings_manager.get(
            "editor.code_block_background_color"
        )
        self.editor.set_code_block_background_color(code_block_bg_color)

        # Appliquer les couleurs des styles de texte
        bold_color = self.settings_manager.get("editor.bold_color")
        italic_color = self.settings_manager.get("editor.italic_color")
        strikethrough_color = self.settings_manager.get("editor.strikethrough_color")
        highlight_color = self.settings_manager.get("editor.highlight_color")
        self.editor.set_text_style_colors(
            bold_color, italic_color, strikethrough_color, highlight_color
        )

        # Appliquer les couleurs des tags et horodatage
        tag_color = self.settings_manager.get("editor.tag_color")
        timestamp_color = self.settings_manager.get("editor.timestamp_color")
        self.editor.set_misc_colors(tag_color, timestamp_color)

        # V1.7.2 Ajout Paramètre Affichages Couleurs
        quote_color = self.settings_manager.get("editor.quote_color")
        link_color = self.settings_manager.get("editor.link_color")
        self.editor.set_quote_link_colors(quote_color, link_color)

        code_font = self.settings_manager.get("editor.code_font_family")
        self.editor.set_code_font(code_font)

        html_comment_color = self.settings_manager.get(
            "editor.html_comment_color", "#a4b5cf"
        )
        self.editor.set_html_comment_color(html_comment_color)

        # --- Appliquer l'affichage des numéros de ligne ---
        show_line_numbers = self.settings_manager.get("editor.show_line_numbers", False)
        # La méthode set_line_numbers_visible doit être implémentée dans editor.py
        if hasattr(self.editor, "set_line_numbers_visible"):
            self.editor.set_line_numbers_visible(show_line_numbers)

        # --- Appliquer le thème CSS à l'aperçu HTML ---
        css_theme = self.settings_manager.get(
            "preview.css_theme", "default_preview.css"
        )
        if hasattr(self.preview, "set_css_theme"):
            self.preview.set_css_theme(css_theme)

        # Appliquer les styles au panneau de plan
        self.outline_panel.apply_styles(font, QColor(heading_color), QColor(bg_color))

    def update_tag_cloud(self):
        """Met à jour le contenu du nuage de tags."""
        excluded_tags_list = self.settings_manager.get(
            "indexing.excluded_tags_from_cloud", []
        )
        excluded_tags_set = set(excluded_tags_list)
        self.navigation_panel.tag_cloud.update_cloud(
            self.journal_directory, excluded_tags_set
        )

    def update_word_cloud(self):
        """Met à jour le contenu du nuage de mots."""
        excluded_words_list = self.settings_manager.get(
            "indexing.excluded_words_from_cloud", []
        )
        excluded_words_set = set(excluded_words_list)
        self.navigation_panel.word_cloud.update_cloud(
            self.journal_directory, excluded_words_set
        )

    def perform_search(self, query: str):
        """Effectue une recherche dans les index et affiche les résultats."""
        if not query or not self.journal_directory:
            self.navigation_panel.show_clouds()
            return

        results = []
        query_lower = query.lower()

        # Recherche de tag
        if query_lower.startswith("@@"):
            index_file = self.journal_directory / "index_tags.json"
            if index_file.exists() and len(query_lower) > 2:
                with open(index_file, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                # Recherche insensible à la casse
                for tag_key, tag_value in tags_data.items():
                    if tag_key.lower() == query_lower:
                        for detail in tag_value["details"]:
                            # On passe maintenant le numéro de ligne
                            results.append(
                                (
                                    detail["date"],
                                    detail["context"],
                                    detail["filename"],
                                    detail.get("line", 1),
                                )  # .get pour la compatibilité
                            )
                        break  # Tag trouvé, on peut arrêter de chercher
        # Recherche de mot
        else:
            index_file = self.journal_directory / "index_words.json"  # noqa
            if index_file.exists():
                with open(index_file, "r", encoding="utf-8") as f:
                    words_data = json.load(f)
                if query_lower in words_data:
                    for detail in words_data[query_lower]["details"]:
                        # On passe maintenant le numéro de ligne
                        results.append(
                            (
                                detail["date"],
                                detail["context"],
                                detail["filename"],
                                detail.get("line", 1),
                            )  # .get pour la compatibilité
                        )

        self.navigation_panel.show_search_results(results)

    def open_file_from_search(self, filename: str, line_number: int):
        """
        Ouvre un fichier sélectionné depuis les résultats de recherche et se positionne
        à la ligne spécifiée.
        """
        if not self.journal_directory or not filename:
            return

        file_path = self.journal_directory / filename
        if file_path.exists():
            if self.check_save_changes():
                # Ouvrir le fichier sans se soucier du scroll pour l'instant
                self.open_specific_file(str(file_path))
                # Maintenant, se positionner à la bonne ligne
                self.go_to_line(line_number)
        else:
            QMessageBox.warning(
                self, "Fichier non trouvé", f"Le fichier '{filename}' n'existe plus."
            )

    def go_to_line(self, line_number: int):
        """
        Déplace le curseur à la ligne spécifiée et la positionne en haut de l'éditeur.
        """
        if line_number <= 0:
            return

        from PyQt5.QtGui import QTextCursor

        text_edit = self.editor.text_edit
        doc = text_edit.document()

        # Le numéro de bloc correspond au numéro de ligne - 1
        block = doc.findBlockByNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            text_edit.setTextCursor(cursor)

            # Forcer le défilement pour que la ligne soit en haut
            scrollbar = text_edit.verticalScrollBar()
            cursor_rect = text_edit.cursorRect()
            scrollbar.setValue(scrollbar.value() + cursor_rect.top())

            text_edit.setFocus()

    def update_navigation_panel_data(self):
        """Met à jour les données nécessaires au panneau de navigation, comme la liste des tags."""
        if not self.journal_directory:
            return

        tags_list = []
        index_file = self.journal_directory / "index_tags.json"
        if index_file.exists():
            try:
                with open(index_file, "r", encoding="utf-8") as f:
                    tags_data = json.load(f)
                # Trier les clés (les tags) par ordre alphabétique
                tags_list = sorted(tags_data.keys())
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️ Erreur de lecture de l'index des tags pour le menu: {e}")

        self.navigation_panel.set_available_tags(tags_list)

    def expand_outline(self):
        """Déplie entièrement l'arborescence du plan du document."""
        self.outline_panel.tree_widget.expandAll()

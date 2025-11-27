import os
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QFileDialog,
    QDialogButtonBox,
    QMessageBox,
)
from PyQt5.QtCore import QRunnable, pyqtSignal, QObject, pyqtSlot
from validators import url as valid_url

from integrations.url_converter import UrlToMarkdown


class UrlToMarkdownDialog(QDialog):
    """Boîte de dialogue pour la conversion URL/HTML vers Markdown."""

    def __init__(self, initial_url="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conversion URL/HTML vers Markdown")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)

        # Champ URL/Chemin
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Chemin ou URL:"))
        self.url_input = QLineEdit(initial_url)
        url_layout.addWidget(self.url_input)
        browse_button = QPushButton("Parcourir...")
        browse_button.clicked.connect(self.browse_file)
        url_layout.addWidget(browse_button)
        layout.addLayout(url_layout)

        # Options
        self.title_checkbox = QCheckBox("Ajouter le titre en #")
        self.title_checkbox.setChecked(True)
        layout.addWidget(self.title_checkbox)

        self.links_checkbox = QCheckBox("Conserver les liens Markdown")
        self.links_checkbox.setChecked(True)
        layout.addWidget(self.links_checkbox)

        self.clean_checkbox = QCheckBox("Utiliser Readability pour nettoyer")
        self.clean_checkbox.setChecked(True)
        layout.addWidget(self.clean_checkbox)

        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def browse_file(self):
        """Ouvre un sélecteur de fichier pour les fichiers HTML."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Sélectionner un fichier HTML", "", "Fichiers HTML (*.html *.htm)"
        )
        if path:
            self.url_input.setText(path)

    def get_options(self):
        """Retourne les options sélectionnées."""
        return {
            "url_or_path": self.url_input.text().strip(),
            "add_title": self.title_checkbox.isChecked(),
            "keep_links": self.links_checkbox.isChecked(),
            "clean_content": self.clean_checkbox.isChecked(),
        }


class UrlToMarkdownSignals(QObject):
    """Signaux pour le worker de conversion."""

    finished = pyqtSignal(str, str)  # content, destination_path
    error = pyqtSignal(str)


class UrlToMarkdownWorker(QRunnable):
    """Worker pour exécuter la conversion en arrière-plan."""

    def __init__(self, options, destination_path):
        super().__init__()
        self.options = options
        self.destination_path = destination_path
        self.signals = UrlToMarkdownSignals()

    @pyqtSlot()
    def run(self):
        """Exécute la conversion."""
        url_or_path = self.options["url_or_path"]
        is_url = valid_url(url_or_path)
        is_local_file = os.path.exists(url_or_path) and os.path.isfile(url_or_path)

        if not is_url and not is_local_file:
            self.signals.error.emit(
                f"Le chemin ou l'URL '{url_or_path}' n'est pas valide."
            )
            return

        try:
            converter = UrlToMarkdown()
            html_content = None
            url_for_base = url_or_path

            if is_local_file:
                with open(url_or_path, "r", encoding="utf-8", errors="ignore") as f:
                    html_content = f.read()
                url_for_base = f"file://{os.path.abspath(url_or_path)}"

            markdown_content = converter.convert(
                url=url_for_base,
                title=self.options["add_title"],
                links=self.options["keep_links"],
                clean=self.options["clean_content"],
                html_content=html_content,
            )

            # Sauvegarder le fichier Markdown
            with open(self.destination_path, "w", encoding="utf-8") as f:
                f.write(markdown_content)

            self.signals.finished.emit(markdown_content, self.destination_path)

        except Exception as e:
            self.signals.error.emit(f"Erreur lors de la conversion : {e}")


def run_url_to_markdown_conversion(main_window, initial_url=""):
    """Fonction principale pour lancer le processus de conversion."""
    dialog = UrlToMarkdownDialog(initial_url, main_window)
    if dialog.exec_() == QDialog.Accepted:
        options = dialog.get_options()

        # Demander où sauvegarder le fichier .md
        default_dir = os.path.join(main_window.journal_directory, "notes")
        os.makedirs(default_dir, exist_ok=True)

        destination_path, _ = QFileDialog.getSaveFileName(
            main_window,
            "Sauvegarder le fichier Markdown",
            default_dir,
            "Fichiers Markdown (*.md)",
        )

        if not destination_path:
            return

        # Sauvegarder le fichier en cours d'édition avant de continuer
        main_window.save_file()

        # Lancer le worker
        main_window.start_task("Conversion en Markdown en cours...")
        worker = UrlToMarkdownWorker(options, destination_path)
        worker.signals.finished.connect(main_window.on_url_to_markdown_finished)
        worker.signals.error.connect(main_window.on_task_error)
        main_window.thread_pool.start(worker)

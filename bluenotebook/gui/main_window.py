"""
Fenêtre principale de BlueNotebook - Éditeur Markdown
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from .editor import MarkdownEditor
from .preview import MarkdownPreview

class MainWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BlueNotebook - Éditeur Markdown")
        self.root.geometry("1200x800")
        
        self.current_file = None
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        # Frame principal avec séparateur
        main_frame = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone d'édition
        self.editor = MarkdownEditor(main_frame)
        main_frame.add(self.editor.frame, weight=1)
        
        # Zone d'aperçu
        self.preview = MarkdownPreview(main_frame)
        main_frame.add(self.preview.frame, weight=1)
        
        # Connecter l'éditeur au preview
        self.editor.on_text_change = self.preview.update_preview
        
    def setup_menu(self):
        """Configuration du menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Sauvegarder", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit_app, accelerator="Ctrl+Q")
        
        # Raccourcis clavier
        self.root.bind('<Control-n>', lambda e: self.new_file())
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-q>', lambda e: self.quit_app())
        
    def new_file(self):
        """Créer un nouveau fichier"""
        self.editor.clear()
        self.current_file = None
        self.root.title("BlueNotebook - Nouveau fichier")
        
    def open_file(self):
        """Ouvrir un fichier"""
        filename = filedialog.askopenfilename(
            title="Ouvrir un fichier Markdown",
            filetypes=[("Fichiers Markdown", "*.md"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.set_content(content)
                self.current_file = filename
                self.root.title(f"BlueNotebook - {filename}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")
                
    def save_file(self):
        """Sauvegarder le fichier"""
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
            
    def save_file_as(self):
        """Sauvegarder sous"""
        filename = filedialog.asksaveasfilename(
            title="Sauvegarder le fichier",
            defaultextension=".md",
            filetypes=[("Fichiers Markdown", "*.md"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self._save_to_file(filename)
            self.current_file = filename
            self.root.title(f"BlueNotebook - {filename}")
            
    def _save_to_file(self, filename):
        """Sauvegarder dans un fichier spécifique"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.editor.get_content())
            messagebox.showinfo("Succès", "Fichier sauvegardé avec succès!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible de sauvegarder:\n{e}")
            
    def quit_app(self):
        """Quitter l'application"""
        self.root.quit()
        
    def run(self):
        """Lancer l'application"""
        self.root.mainloop()

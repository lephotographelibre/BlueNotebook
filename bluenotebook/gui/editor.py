"""
Composant éditeur de texte BlueNotebook avec coloration Markdown
"""

import tkinter as tk
from tkinter import ttk

class MarkdownEditor:
    def __init__(self, parent):
        self.parent = parent
        self.on_text_change = None
        self.setup_ui()
        
    def setup_ui(self):
        """Configuration de l'interface d'édition"""
        self.frame = ttk.Frame(self.parent)
        
        # Label
        label = ttk.Label(self.frame, text="Éditeur")
        label.pack(pady=(0, 5))
        
        # Zone de texte avec scrollbar
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            undo=True,
            font=("Consolas", 12),
            bg="#f8f9fa",
            fg="#343a40",
            insertbackground="#007bff",
            selectbackground="#007bff",
            selectforeground="white"
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Événements
        self.text_widget.bind('<KeyRelease>', self._on_text_change)
        self.text_widget.bind('<Button-1>', self._on_text_change)
        
    def _on_text_change(self, event=None):
        """Callback pour changement de texte"""
        if self.on_text_change:
            content = self.get_content()
            self.on_text_change(content)
            
    def get_content(self):
        """Récupérer le contenu"""
        return self.text_widget.get("1.0", tk.END + "-1c")
        
    def set_content(self, content):
        """Définir le contenu"""
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.insert("1.0", content)
        
    def clear(self):
        """Vider l'éditeur"""
        self.text_widget.delete("1.0", tk.END)

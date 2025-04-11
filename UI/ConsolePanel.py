import tkinter as tk
from tkinter import scrolledtext

class ConsolePanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_console()
        
    def _setup_console(self):
        self.console = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            width=80,
            height=10,
            font=('Consolas', 10),
            state='disabled'
        )
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def mostrar_en_consola(self, mensaje):
        """Muestra un mensaje en la consola"""
        self.console.config(state='normal')
        self.console.insert(tk.END, str(mensaje) + "\n")
        self.console.config(state='disabled')
        self.console.see(tk.END)
        
    def clear(self):
        """Limpia la consola"""
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.config(state='disabled')
        
    def grid(self, **kwargs):
        super().grid(**kwargs)
        return self
import tkinter as tk
from tkinter import ttk

class ErrorPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()
        
    def _setup_ui(self):
        # Configurar Treeview para mostrar errores
        self.tree = ttk.Treeview(
            self,
            columns=("Error",),
            show="headings",
            height=10,
            selectmode="extended"
        )
        self.tree.heading("Error", text="Errores")
        self.tree.column("Error", width=350, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Botón para copiar errores
        self.copy_btn = ttk.Button(
            self,
            text="Copiar Errores",
            command=self._copy_errors
        )
        self.copy_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Configurar menú contextual
        self._setup_context_menu()
        
    def _setup_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Copiar", command=self._copy_selected)
        self.tree.bind("<Button-3>", self._show_context_menu)
        
    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
            
    def _copy_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        text = "\n".join(
            self.tree.item(item, "values")[0]
            for item in selected
        )
        self.clipboard_clear()
        self.clipboard_append(text)
        
    def _copy_errors(self):
        text = "\n".join(
            self.tree.item(item, "values")[0]
            for item in self.tree.get_children()
        )
        self.clipboard_clear()
        self.clipboard_append(text)
        
    def clear(self):
        """Limpia todos los errores"""
        self.tree.delete(*self.tree.get_children())
        
    def add_error(self, error_type, message, line=None):
        """Agrega un error a la lista"""
        line_info = f"Línea {line}: " if line else ""
        self.tree.insert("", tk.END, values=(f"{error_type}: {line_info}{message}",))
        
    def add_error_section(self, title):
        """Agrega un encabezado de sección"""
        self.tree.insert("", tk.END, values=(f"==== {title} ====",))
        
    def grid(self, **kwargs):
        super().grid(**kwargs)
        return self
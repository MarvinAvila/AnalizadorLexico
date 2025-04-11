import tkinter as tk
from tkinter import ttk
from SyntaxAnalyzer.Parser import TIPOS_DE_DATOS
from LexicalAnalyzer.Lexer import reserved

class CodeEditor(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_editor()
        self._setup_line_numbers()
        self._bind_events()
        
    def _setup_editor(self):
        # Frame principal
        self.text_frame = tk.Frame(self)
        self.text_frame.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        self.scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Área de texto
        self.text_area = tk.Text(
            self.text_frame,
            wrap=tk.NONE,
            yscrollcommand=self._sync_scroll,
            font=('Consolas', 12),
            undo=True
        )
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.text_area.yview)
        
        # Configurar tags para resaltado de sintaxis
        self._setup_syntax_highlighting()
        
    def _setup_line_numbers(self):
        # Numeración de líneas
        self.line_numbers = tk.Text(
            self.text_frame,
            width=4,
            padx=5,
            pady=5,
            state=tk.DISABLED,
            bg='#f0f0f0',
            fg='#666',
            font=('Consolas', 12),
            yscrollcommand=self._sync_scroll
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self._update_line_numbers()
        
    def _setup_syntax_highlighting(self):
        # Configurar colores para resaltado
        self.text_area.tag_configure("keyword", foreground="#0000FF")
        self.text_area.tag_configure("datatype", foreground="#800080")
        self.text_area.tag_configure("comment", foreground="#808080", font=('Consolas', 12, 'italic'))
        self.text_area.tag_configure("string", foreground="#008000")
        self.text_area.tag_configure("operator", foreground="black", font=('Consolas', 12, 'bold'))
        self.text_area.tag_configure("boolean", foreground="#B22222")
        self.text_area.tag_configure("error", background="red", foreground="white")
        
    def _bind_events(self):
        self.text_area.bind("<KeyRelease>", self._on_key_release)
        self.text_area.bind("<Return>", self._auto_indent)
        self.text_area.bind("<Configure>", self._update_line_numbers)
        
    def _on_key_release(self, event=None):
        self._update_line_numbers()
        self._highlight_syntax()
        
    def _auto_indent(self, event=None):
        """Agrega tabulación automática al presionar Enter"""
        cursor_index = self.text_area.index(tk.INSERT)
        line_start = f"{cursor_index.split('.')[0]}.0"
        current_line = self.text_area.get(line_start, cursor_index)

        indentation = ""
        for char in current_line:
            if char == " ":
                indentation += " "
            else:
                break

        self.text_area.insert(tk.INSERT, "\n" + indentation)
        return "break"  # Evita que Tkinter agregue un salto de línea por defecto

    def _update_line_numbers(self, event=None):
        """Actualiza la numeración de líneas en el área de texto."""
        lines = self.text_area.get("1.0", tk.END).count("\n") + 1
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        for line in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{line}\n")
        self.line_numbers.config(state=tk.DISABLED)

    def _highlight_syntax(self, event=None):
        """Resalta palabras clave, tipos de datos, cadenas, comentarios, operadores y comparadores."""
        self._update_line_numbers()

        # 🔹 Categorías basadas en Lexer y Parser
        keywords = list(reserved.keys())  # Palabras clave en el Lexer
        datatypes = list(TIPOS_DE_DATOS.values())  # Tipos de datos en el Parser
        operators = ["\\+", "-", "\\*", "/", "=", "AND", "OR", "NOT"]
        comparators = [">", "<", ">=", "<=", "==", "!="]
        boolean_values = ["verdadero", "falso"]

        # 🔹 Configurar colores (PSeInt Style)
        self.text_area.tag_configure("keyword", foreground="#0000FF")  # Azul fuerte
        self.text_area.tag_configure("datatype", foreground="#800080")  # Púrpura
        self.text_area.tag_configure(
            "comment", foreground="#808080", font=("Consolas", 10, "italic")
        )
        self.text_area.tag_configure("string", foreground="#008000")  # Verde oscuro
        self.text_area.tag_configure(
            "operator", foreground="black", font=("TkDefaultFont", 10, "bold")
        )
        self.text_area.tag_configure("boolean", foreground="#B22222")  # Rojo oscuro

        # 🔹 Limpiar resaltado previo
        for tag in [
            "keyword",
            "datatype",
            "comment",
            "string",
            "operator",
            "comparator",
            "boolean",
        ]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        # 🔹 Aplicar resaltado en el orden correcto

        # 1. Resaltar comentarios primero
        self._apply_regex_highlight("comment", r"//.*")

        # 2. Resaltar cadenas de texto
        self._apply_regex_highlight("string", r'"[^"]*"')

        # 3. Resaltar palabras clave, tipos de datos, operadores, etc.
        for word in keywords:
            self._apply_highlight("keyword", word)
        for word in datatypes:
            self._apply_highlight("datatype", word)
        for word in boolean_values:
            self._apply_highlight("boolean", word)
        for op in operators:
            self._apply_regex_highlight("operator", op)

        # 🔹 Asegurar que palabras clave no se mezclen con paréntesis o símbolos
        self._apply_regex_highlight(
            "keyword", r"\b(?:" + "|".join(keywords) + r")\b(?!\s*\))"
        )

        # 🔹 Volver a resaltar operadores para evitar interferencias con el "="
        self.text_area.tag_remove("operator", "1.0", tk.END)
        self._apply_regex_highlight("operator", r"\b(?:" + "|".join(operators) + r")\b")
        
    def _sync_scroll(self, *args):
        """Sincroniza el scroll del editor con los números de línea"""
        self.line_numbers.yview_moveto(args[0])
        self.text_area.yview_moveto(args[0])
        
    def get_code(self):
        """Obtiene el código del editor"""
        return self.text_area.get("1.0", tk.END).strip()
        
    def highlight_error_line(self, line_number):
        """Resalta una línea con error"""
        self.text_area.tag_remove("error", "1.0", tk.END)
        if isinstance(line_number, int):
            start = f"{line_number}.0"
            end = f"{line_number}.end"
            self.text_area.tag_add("error", start, end)
            
    def grid(self, **kwargs):
        super().grid(**kwargs)
        return self
    
    def _apply_regex_highlight(self, tag, pattern):
        """Aplica resaltado basado en expresiones regulares"""
        start = "1.0"
        while True:
            start = self.text_area.search(pattern, start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start} lineend"
            self.text_area.tag_add(tag, start, end)
            start = end

    def _apply_highlight(self, tag, word):
        """Aplica resaltado a palabras clave"""
        start = "1.0"
        while True:
            start = self.text_area.search(r"\m" + word + r"\M", start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(word)}c"
            self.text_area.tag_add(tag, start, end)
            start = end
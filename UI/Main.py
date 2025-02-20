import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LexicalAnalyzer.Lexer import lexer  
from SyntaxAnalyzer.Parser import parser 

class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador en Español")

        # Contenedor principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Área de texto para ingresar el código
        self.text_area = scrolledtext.ScrolledText(main_frame, width=50, height=15, padx=5, pady=5)
        self.text_area.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Contenedor para las tablas
        table_frame = tk.Frame(main_frame)
        table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Tabla para mostrar los tokens
        self.token_list = ttk.Treeview(table_frame, columns=("Tipo", "Valor"), show="headings", height=10)
        self.token_list.heading("Tipo", text="Tipo de Token")
        self.token_list.heading("Valor", text="Valor")
        self.token_list.column("Tipo", width=150, anchor="center")
        self.token_list.column("Valor", width=200, anchor="w")
        self.token_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tabla para mostrar errores
        self.error_list = ttk.Treeview(table_frame, columns=("Error",), show="headings", height=10)
        self.error_list.heading("Error", text="Errores")
        self.error_list.column("Error", width=350, anchor="w")
        self.error_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Botón para analizar el código
        self.analyze_button = tk.Button(main_frame, text="Analizar", command=self.analyze_code)
        self.analyze_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Configurar la distribución del grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

    def analyze_code(self):
        code = self.text_area.get("1.0", tk.END).strip()

        lexer.input(code)
        tokens = []
        lex_errors = []

        for tok in lexer:
            tokens.append((tok.type, tok.value))

        syntax_errors = []
        try:
            parser.parse(code)
        except Exception as e:
            syntax_errors.append(str(e))  # Capturar errores de PLY

        # Mostrar tokens
        self.token_list.delete(*self.token_list.get_children())
        for token in tokens:
            self.token_list.insert("", tk.END, values=token)

        # Mostrar errores
        self.error_list.delete(*self.error_list.get_children())
        for error in lex_errors + syntax_errors:
            self.error_list.insert("", tk.END, values=(f"  {error}  ",))  # Agregar espacios en blanco

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CompilerApp()
    app.run()

import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LexicalAnalyzer.Lexer import Lexer
from SyntaxAnalyzer.Parser import Parser

class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador en Español")

        # Área de texto para ingresar el código
        self.text_area = scrolledtext.ScrolledText(self.root, width=50, height=10)
        self.text_area.pack()

        # Botón para analizar el código
        self.analyze_button = tk.Button(self.root, text="Analizar", command=self.analyze_code)
        self.analyze_button.pack()

        # Tabla para mostrar los tokens
        self.token_list = ttk.Treeview(self.root, columns=("Tipo", "Valor"), show="headings")
        self.token_list.heading("Tipo", text="Tipo de Token")
        self.token_list.heading("Valor", text="Valor")
        self.token_list.pack()

        # Tabla para mostrar errores
        self.error_list = ttk.Treeview(self.root, columns=("Error",), show="headings")
        self.error_list.heading("Error", text="Errores")
        self.error_list.pack()

    def analyze_code(self):
        code = self.text_area.get("1.0", tk.END).strip()
        
        # Análisis léxico
        lexer = Lexer()
        tokens, lex_errors = lexer.tokenize(code)

        # Mostrar tokens
        self.token_list.delete(*self.token_list.get_children())
        for token in tokens:
            self.token_list.insert("", tk.END, values=token)

        # Análisis sintáctico
        parser = Parser(tokens)
        syntax_errors = parser.parse()

        # Mostrar errores
        self.error_list.delete(*self.error_list.get_children())
        for error in lex_errors + syntax_errors:
            self.error_list.insert("", tk.END, values=(error,))

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CompilerApp()
    app.run()

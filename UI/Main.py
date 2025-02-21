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

        # Configurar resaltado de sintaxis
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)  # Resaltar en tiempo real

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

        # Consola de salida
        self.console = scrolledtext.ScrolledText(main_frame, width=50, height=5, padx=5, pady=5)
        self.console.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.console.config(state=tk.DISABLED)  # Hacerla de solo lectura

        # Botón para analizar el código
        self.analyze_button = tk.Button(main_frame, text="Analizar", command=self.analyze_code)
        self.analyze_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Configurar la distribución del grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Pasar la función mostrar_en_consola al parser
        parser.mostrar_en_consola = self.mostrar_en_consola

    def highlight_syntax(self, event=None):
        """Resalta las palabras clave, cadenas y comentarios en el área de texto."""
        keywords = ["inicio", "fin", "si", "entonces", "sino", "mientras", "hacer", "para", "mostrar"]
        strings = r'"[^"]*"'  # Expresión regular para cadenas
        comments = r'//.*'    # Expresión regular para comentarios

        # Limpiar resaltado anterior
        for tag in ["keyword", "string", "comment"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        # Resaltar palabras clave
        for word in keywords:
            start = "1.0"
            while True:
                start = self.text_area.search(word, start, stopindex=tk.END)
                if not start:
                    break
                end = f"{start}+{len(word)}c"
                self.text_area.tag_add("keyword", start, end)
                start = end

        # Resaltar cadenas
        start = "1.0"
        while True:
            start = self.text_area.search(strings, start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start} lineend"
            self.text_area.tag_add("string", start, end)
            start = end

        # Resaltar comentarios
        start = "1.0"
        while True:
            start = self.text_area.search(comments, start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start} lineend"
            self.text_area.tag_add("comment", start, end)
            start = end

    def mostrar_en_consola(self, mensaje):
        """Muestra un mensaje en la consola de salida."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, mensaje + "\n")
        self.console.config(state=tk.DISABLED)

    def analyze_code(self):
        print("\n🚀 Iniciando análisis de código...")
        
        # Obtener el código fuente del área de texto
        code = self.text_area.get("1.0", tk.END).strip()
        print(f"📌 Código ingresado:\n{code}\n")

        # Pasar el código al lexer para generar tokens
        lexer.input(code)
        tokens = []
        lex_errors = []

        # Recorrer los tokens generados por el lexer
        for tok in lexer:
            print(f"🔹 Token detectado: {tok.type} -> {tok.value}")
            tokens.append((tok.type, tok.value))

        syntax_errors = []
        try:
            # Enviar el código al parser para análisis sintáctico
            print("📌 Enviando código al parser...")
            print(f"📄 Código enviado al parser:\n{code}\n")  # 🔥 Imprimir el código que llega al parser
            parser.parse(code)  # 🔥 Aquí se envía el código al parser
            print("✔️ Análisis sintáctico completado.")
        except Exception as e:
            # Capturar errores de sintaxis
            syntax_errors.append(str(e))
            print(f"❌ Error en el parser: {e}")

        # Mostrar tokens y errores en la interfaz
        self.token_list.delete(*self.token_list.get_children())
        for token in tokens:
            self.token_list.insert("", tk.END, values=token)

        self.error_list.delete(*self.error_list.get_children())
        for error in lex_errors + syntax_errors:
            self.error_list.insert("", tk.END, values=(f"  {error}  ",))

        print("🚀 Análisis finalizado.\n")

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CompilerApp()
    app.run()
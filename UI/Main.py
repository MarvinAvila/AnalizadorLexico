import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from LexicalAnalyzer.Lexer import lexer  
from SyntaxAnalyzer.Parser import parser, SemanticError, TIPOS_DE_DATOS,variables, constantes
from LexicalAnalyzer.Lexer import reserved 
from Executor.Runner import run_code  

class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador en Español")

        # Contenedor principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Área de texto para ingresar el código con numeración de líneas
        self.text_frame = tk.Frame(main_frame)
        self.text_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Scrollbar compartido
        self.text_scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Numeración de líneas
        self.line_numbers = tk.Text(self.text_frame, width=4, padx=5, pady=5, state=tk.DISABLED, yscrollcommand=self.text_scrollbar.set)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Área de texto para el código
        self.text_area = tk.Text(self.text_frame, width=50, height=15, padx=5, pady=5, yscrollcommand=self.sync_scroll)
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text_scrollbar.config(command=self.sync_scroll)

        # Configurar resaltado de sintaxis y numeración de líneas
        self.text_area.tag_configure("keyword", foreground="blue")
        self.text_area.tag_configure("string", foreground="green")
        self.text_area.tag_configure("comment", foreground="gray")
        self.text_area.tag_configure("datatype", foreground="purple")
        self.text_area.bind("<KeyRelease>", self.highlight_syntax)
        self.text_area.bind("<Return>", self.auto_indent)

        # Contenedor para las tablas
        table_frame = tk.Frame(main_frame)
        table_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Tabla para mostrar errores
        self.error_list = ttk.Treeview(table_frame, columns=("Error",), show="headings", height=10)
        self.error_list.heading("Error", text="Errores")
        self.error_list.column("Error", width=350, anchor="w")
        self.error_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Consola de salida
        self.console = scrolledtext.ScrolledText(main_frame, width=50, height=15, padx=5, pady=5)
        self.console.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        self.console.config(state=tk.DISABLED)

        # Botón para analizar el código
        self.analyze_button = tk.Button(main_frame, text="Analizar", command=self.analyze_code)
        self.analyze_button.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Configurar la distribución del grid
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Pasar la función mostrar_en_consola al parser
        parser.mostrar_en_consola = self.mostrar_en_consola

        # Inicializar la numeración de líneas
        self.update_line_numbers()

    def sync_scroll(self, *args):
        """ Sincroniza el desplazamiento del área de texto y la numeración de líneas. """
        if args[0] == "scroll":
            self.line_numbers.yview_scroll(int(args[1]), args[2])
            self.text_area.yview_scroll(int(args[1]), args[2])
        else:
            self.line_numbers.yview_moveto(args[0])
            self.text_area.yview_moveto(args[0])

    def update_line_numbers(self, event=None):
        """Actualiza la numeración de líneas en el área de texto."""
        lines = self.text_area.get("1.0", tk.END).count("\n") + 1
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        for line in range(1, lines + 1):
            self.line_numbers.insert(tk.END, f"{line}\n")
        self.line_numbers.config(state=tk.DISABLED)

    def highlight_syntax(self, event=None):
        """Resalta palabras clave, tipos de datos, cadenas, comentarios, operadores y comparadores."""
        self.update_line_numbers()

        # 🔹 Categorías basadas en Lexer y Parser
        keywords = list(reserved.keys())  # Palabras clave en el Lexer
        datatypes = list(TIPOS_DE_DATOS.values())  # Tipos de datos en el Parser
        operators = ["\\+", "-", "\\*", "/", "=", "AND", "OR", "NOT"]
        comparators = [">", "<", ">=", "<=", "==", "!="]
        boolean_values = ["verdadero", "falso"]

        # 🔹 Configurar colores (PSeInt Style)
        self.text_area.tag_configure("keyword", foreground="#0000FF")  # Azul fuerte
        self.text_area.tag_configure("datatype", foreground="#800080")  # Púrpura
        self.text_area.tag_configure("comment", foreground="#808080", font=("Consolas", 10, "italic"))
        self.text_area.tag_configure("string", foreground="#008000")  # Verde oscuro
        self.text_area.tag_configure("operator", foreground="black", font=("TkDefaultFont", 10, "bold"))
        self.text_area.tag_configure("boolean", foreground="#B22222")   # Rojo oscuro

        # 🔹 Limpiar resaltado previo
        for tag in ["keyword", "datatype", "comment", "string", "operator", "comparator", "boolean"]:
            self.text_area.tag_remove(tag, "1.0", tk.END)

        # 🔹 Aplicar resaltado
        for word in keywords:
            self._apply_highlight("keyword", word)
        for word in datatypes:
            self._apply_highlight("datatype", word)
        for word in boolean_values:
            self._apply_highlight("boolean", word)
        for op in operators:
            self._apply_regex_highlight("operator", op)


        # 🔹 Asegurar que palabras clave no se mezclen con paréntesis o símbolos
        self._apply_regex_highlight("keyword", r'\b(?:' + '|'.join(keywords) + r')\b(?!\s*\))')
        
        # 🔹 Resaltar comentarios correctamente
        self._apply_regex_highlight("comment", r"//.*")

        # 🔹 Resaltar cadenas correctamente sin Tcl errors
        self._apply_regex_highlight("string", r'"[^"]*"')

        # 🔹 Volver a resaltar operadores para evitar interferencias con el "="
        self.text_area.tag_remove("operator", "1.0", tk.END)
        self._apply_regex_highlight("operator", r'\b(?:' + '|'.join(operators) + r')\b')



    def _apply_highlight(self, tag, word):
        """Aplica resaltado a palabras clave, tipos de datos y booleanos."""
        start = "1.0"
        while True:
            start = self.text_area.search(r'\m' + word + r'\M', start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start}+{len(word)}c"
            self.text_area.tag_add(tag, start, end)
            start = end

    def _apply_regex_highlight(self, tag, pattern):
        """Aplica resaltado basado en expresiones regulares."""
        start = "1.0"
        while True:
            start = self.text_area.search(pattern, start, stopindex=tk.END, regexp=True)
            if not start:
                break
            end = f"{start} lineend"
            self.text_area.tag_add(tag, start, end)
            start = end


    def mostrar_en_consola(self, mensaje):
        """Muestra un mensaje en la consola de salida."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, mensaje + "\n")
        self.console.config(state=tk.DISABLED)

    def analyze_code(self):
        print("\n🚀 Iniciando análisis de código...")
        
        # 🔹 Limpiar la consola antes de cada análisis
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

        # 🔹 Limpiar la tabla de errores antes de cada análisis
        self.error_list.delete(*self.error_list.get_children())

        # 🔹 Reiniciar listas de errores globales
        from SyntaxAnalyzer.Parser import syntax_errors, semantic_errors
        syntax_errors.clear()
        semantic_errors.clear()
        
        # 🔹 LIMPIAR LAS VARIABLES Y CONSTANTES PREVIAS
        variables.clear()
        constantes.clear()

        # Obtener el código fuente del área de texto
        code = self.text_area.get("1.0", tk.END).strip()
        print(f"📌 Código ingresado:\n{code}\n")

        # Pasar el código al lexer para generar tokens
        lexer.input(code)
        tokens = []
        lex_errors = []

        # Recorrer los tokens generados por el lexer
        for tok in lexer:
            #print(f"🔹 Token detectado: {tok.type} -> {tok.value}")
            tokens.append((tok.type, tok.value))

        execution_errors = []

        try:
            # Enviar el código al parser para análisis sintáctico
            print("📌 Enviando código al parser...")
            parser.parse(code, tracking=True)  # 🔥 Aquí se envía el código al parser
            print("✔️ Análisis sintáctico completado.")
        except SyntaxError as e:
            syntax_errors.append(str(e))
            print(f"❌ Error en el parser: {e}")
        except SemanticError as e:
            semantic_errors.append(str(e))
            print(f"❌ Error semántico: {e}")

        # Ejecutar el código si no hay errores sintácticos o semánticos
        if not syntax_errors and not semantic_errors:
            try:
                # Aquí deberías generar el código Python a partir del código fuente
                python_code = self.generate_python_code(code)  # Implementa esta función si no está
                execution_result = run_code(python_code)
                if "Error de ejecución" in execution_result:
                    execution_errors.append(execution_result)
            except Exception as e:
                execution_errors.append(f"Error de ejecución: {str(e)}")

        # Mostrar tokens y errores en la interfaz
        # self.token_list.delete(*self.token_list.get_children())
        # for token in tokens:
        #     self.token_list.insert("", tk.END, values=token)

        self.error_list.delete(*self.error_list.get_children())
        for error in lex_errors + syntax_errors + semantic_errors + execution_errors:
            self.error_list.insert("", tk.END, values=(error,))

        print("🚀 Análisis finalizado.\n")
    def auto_indent(self, event=None):
        """ Agrega tabulación automática al presionar Enter """
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


    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = CompilerApp()
    app.run()
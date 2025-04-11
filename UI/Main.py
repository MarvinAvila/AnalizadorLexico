import sys
import os
import tkinter as tk
from tkinter import ttk, scrolledtext

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from GlobalErrors.ErrorsManager import global_errors
from LexicalAnalyzer.Lexer import lexer
from SyntaxAnalyzer.Parser import parser, TIPOS_DE_DATOS, variables, constantes
from LexicalAnalyzer.Lexer import reserved
from Executor.Runner import run_code
from SemanticAnalyzer.SemanticAnalyzer import SemanticAnalyzer
from SyntaxAnalyzer.AST import NodoPrograma, NodoIf, NodoMientras, NodoPara, NodoRepetir, NodoMostrar, NodoBinario, NodoUnario, NodoIdentificador, NodoLiteral
from CodeGenerator.TACGenerator import TACGenerator
from CodeGenerator.Translator import Translator
from CodeGenerator.Optimizer import Optimizer


class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador en Español")

        # Contenedor principal
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Área de texto para ingresar el código con numeración de líneas
        self.text_frame = tk.Frame(main_frame)
        self.text_frame.grid(
            row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew"
        )

        # Scrollbar compartido
        self.text_scrollbar = tk.Scrollbar(self.text_frame, orient=tk.VERTICAL)
        self.text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Numeración de líneas
        self.line_numbers = tk.Text(
            self.text_frame,
            width=4,
            padx=5,
            pady=5,
            state=tk.DISABLED,
            yscrollcommand=self.text_scrollbar.set,
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        # Área de texto para el código
        self.text_area = tk.Text(
            self.text_frame,
            width=50,
            height=15,
            padx=5,
            pady=5,
            yscrollcommand=self.sync_scroll,
        )
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
        self.error_list = ttk.Treeview(
            table_frame, columns=("Error",), show="headings", height=10
        )
        self.error_list.heading("Error", text="Errores")
        self.error_list.column("Error", width=350, anchor="w")
        self.error_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.add_copy_functionality()

        # Consola de salida
        self.console = scrolledtext.ScrolledText(
            main_frame, width=50, height=15, padx=5, pady=5
        )
        self.console.grid(
            row=2, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.console.config(state=tk.DISABLED)

        # Botón para analizar el código
        self.analyze_button = tk.Button(
            main_frame, text="Analizar", command=self.analyze_code
        )
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
        """Sincroniza el desplazamiento del área de texto y la numeración de líneas."""
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

    def _apply_highlight(self, tag, word):
        """Aplica resaltado a palabras clave, tipos de datos y booleanos."""
        start = "1.0"
        while True:
            start = self.text_area.search(
                r"\m" + word + r"\M", start, stopindex=tk.END, regexp=True
            )
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

    def highlight_error_line(self, line_number):
        """Resalta en rojo la línea donde ocurrió un error."""
        self.text_area.tag_remove("error", "1.0", tk.END) 

        if isinstance(line_number, int):
            start = f"{line_number}.0"
            end = f"{line_number}.end"
            self.text_area.tag_add("error", start, end)
            self.text_area.tag_config("error", background="red", foreground="white")


    def mostrar_en_consola(self, mensaje):
        """Muestra un mensaje en la consola de salida."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, str(mensaje))  # Convertir a string por seguridad
        self.console.insert(tk.END, "\n")  # Añadir salto de línea
        self.console.see(tk.END)  # Auto-desplazamiento al final
        self.console.config(state=tk.DISABLED)
        self.console.update_idletasks()  # Forzar actualización de la GUI

    def analyze_code(self):
        print("\n🚀 Iniciando análisis de código...")

        # 🔹 Limpiar la consola antes de cada análisis
        self.console.config(state=tk.NORMAL)
        self.console.delete("1.0", tk.END)
        self.console.config(state=tk.DISABLED)

        # 🔹 Limpiar la tabla de errores antes de cada análisis
        self.error_list.delete(*self.error_list.get_children())

        self.text_area.tag_remove("error", "1.0", tk.END)


        # Limpiar estados globales
        from GlobalErrors.ErrorsManager import global_errors
        global_errors.clear()
        
        from LexicalAnalyzer.Lexer import lexer
        lexer.lineno = 1  

        # 🔹 LIMPIAR LAS VARIABLES Y CONSTANTES PREVIAS
        variables.clear()
        constantes.clear()

        # Obtener el código fuente del área de texto
        code = self.text_area.get("1.0", tk.END).strip()
        print(f"📌 Código ingresado:\n{code}\n")
        
        # --------------------------------------------
        # 1. Análisis Léxico
        # --------------------------------------------

        lexer.input(code)
        try:
            # Solo para verificar que el lexer funciona
            for tok in lexer:
                pass  # Simplemente consumir todos los tokens
            print("✔️ Análisis léxico completado.")
        except Exception as e:
            global_errors.append({
                "tipo": "léxico",
                "linea": 0,
                "mensaje": f"Error léxico: {str(e)}"
            })

        # Si hay errores léxicos, detenerse aquí
        if global_errors:
            self._mostrar_errores()
            return

        # --------------------------------------------
        # 2. Análisis Sintáctico
        # --------------------------------------------
        try:
            print("📌 Enviando código al parser...")
            lexer.lineno = 1
            ast = parser.parse(code, lexer=lexer, tracking=True)
            
            # Depuración: imprimir estructura cruda del AST
            # print("\n🔥 Estructura cruda del AST:")
            # from pprint import pprint
            # pprint(vars(ast))
            # for decl in ast.declaraciones:
            #     pprint(vars(decl))
            #     if hasattr(decl, 'cuerpo'):
            #         print("Contenido del cuerpo:", decl.cuerpo)
            
            # Después de parser.parse()
            if isinstance(ast, NodoPrograma):
                print("AST construido correctamente")
                # for decl in ast.declaraciones:
                #     print(f"Declaración en línea {decl.linea}")
            else:
                print("Error: No se generó un NodoPrograma válido")
            
            print("✔️ Análisis sintáctico completado.")
                    # Verificar que se obtuvo un AST válido
            if not isinstance(ast, NodoPrograma):
                global_errors.append({
                    "tipo": "sintáctico",
                    "linea": 0,
                    "mensaje": "El programa no pudo ser analizado correctamente"
                })
        except Exception as e:
            global_errors.append({
                "tipo": "sintáctico",
                "linea": 0,
                "mensaje": f"Error de sintaxis: {str(e)}"
            }) 
        
        # Si hay errores sintácticos, detenerse aquí
        if global_errors:
            self._mostrar_errores()
            return
        
        # --------------------------------------------
        # 3. Análisis Semántico
        # --------------------------------------------
        
        try:
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)
            print("✔️ Análisis semántico completado.")
        except Exception as e:
            global_errors.append({
                "tipo": "semántico",
                "linea": 0,
                "mensaje": f"Error semántico: {str(e)}" 
            })

        # Si hay errores semánticos, detenerse aquí
        if global_errors:
            self._mostrar_errores()
            return
            
        # --------------------------------------------
        # 4. Generación de Código Intermedio (TAC)
        # --------------------------------------------
        try:
            tac_gen = TACGenerator()
            tac_code = tac_gen.generate(ast)
            
            # Mostrar TAC original
            self.mostrar_en_consola("\n🔷 Código Intermedio (TAC) - Antes de optimizar:")
            for line in tac_code:
                self.mostrar_en_consola(line)
            
            print("✔️ Generación de código intermedio completada.")
        except Exception as e:
            global_errors.append({
                "tipo": "generación",
                "linea": 0,
                "mensaje": f"Error generando TAC: {str(e)}"
            })
            self._mostrar_errores()
            return

        # --------------------------------------------
        # 5. Optimización del TAC
        # --------------------------------------------
        try:
            optimizer = Optimizer()
            optimized_tac = optimizer.optimize(tac_code)
            
            # Mostrar TAC optimizado
            self.mostrar_en_consola("\n🔷 Código Intermedio (TAC) - Después de optimizar:")
            for line in optimized_tac:
                self.mostrar_en_consola(line)
                
            # Mostrar variables esenciales detectadas (para depuración)
            self.mostrar_en_consola(f"\n🔍 Variables esenciales identificadas: {', '.join(optimizer.essential_vars)}")
            
            print("✔️ Optimización de código intermedio completada.")
        except Exception as e:
            self.mostrar_en_consola(f"⚠️ Advertencia: {str(e)}")
            optimized_tac = tac_code  # Usar TAC no optimizado como fallback

        # --------------------------------------------
        # 6. Traducción a Python
        # --------------------------------------------
        try:
            translator = Translator(optimized_tac)
            python_code = translator.translate()
            
            # Validación de identación
            self.validate_python_code(python_code)
            
            self.mostrar_en_consola("\n🐍 Código Python Generado:")
            self.mostrar_en_consola(python_code)
            
            print("✔️ Traducción a Python completada.")
        except Exception as e:
            global_errors.append({
                "tipo": "traducción",
                "linea": 0,
                "mensaje": f"Error traduciendo a Python: {str(e)}"
            })
            self._mostrar_errores()
            return

        # --------------------------------------------
        # 7. Ejecución del Código
        # --------------------------------------------
        self.execute_python_code(python_code)
        
    def validate_python_code(self, code):
        """Valida que el código Python generado sea correcto"""
        lines = code.split('\n')
        stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())
            
            # Para bloques que deben aumentar identación
            if stripped.endswith(':'):
                if i+1 < len(lines) and not lines[i+1].startswith(' ' * (current_indent + 4)):
                    raise IndentationError(f"Falta identación después de ':' en línea {i}")
                stack.append(current_indent)
            
            # Para bloques que deben reducir identación
            elif stripped and current_indent < (stack[-1] if stack else 0):
                if not any(stripped.startswith(kw) for kw in ['else', 'elif']):
                    stack.pop()
        
        if stack:
            raise IndentationError("Bloques sin cerrar correctamente")    
    
    def validate_python_indentation(self, code):
        """Valida que el código Python tenga identación correcta"""
        lines = code.split('\n')
        indent_stack = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())
            
            # Para bloques que deben aumentar identación
            if stripped.endswith(':'):
                if i+1 < len(lines) and not lines[i+1].startswith(' ' * (current_indent + 4)):
                    raise IndentationError(f"Falta identación después de ':' en línea {i}")
                indent_stack.append(current_indent)
            
            # Para bloques que deben reducir identación
            elif stripped and current_indent < (indent_stack[-1] if indent_stack else 0):
                if not any(stripped.startswith(kw) for kw in ['else', 'elif', 'except', 'finally']):
                    indent_stack.pop()
        
        if indent_stack:
            raise IndentationError("Bloques sin cerrar correctamente")

    def execute_python_code(self, python_code):
        """Ejecuta el código Python generado con manejo seguro"""
        execution_errors = []
        old_stdout = sys.stdout
        
        try:
            # Validar sintaxis primero
            import ast
            ast.parse(python_code)
            
            # Configurar entorno seguro
            safe_env = {
                '__builtins__': {
                    'print': print,
                    'range': range,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool
                },
                'True': True,
                'False': False
            }
            
            # Redirigir salida
            from io import StringIO
            sys.stdout = mystdout = StringIO()
            
            # Ejecutar con timeout
            from threading import Thread
            from queue import Queue
            
            result_queue = Queue()
            
            def execute():
                try:
                    exec(python_code, safe_env)
                    result_queue.put(("success", mystdout.getvalue()))
                except Exception as e:
                    result_queue.put(("error", str(e)))
            
            thread = Thread(target=execute)
            thread.start()
            thread.join(timeout=5)  # 5 segundos máximo
            
            if thread.is_alive():
                thread.join(timeout=0)
                execution_errors.append({
                    "tipo": "ejecución",
                    "linea": "desconocida",
                    "mensaje": "Error: Tiempo de ejecución excedido (posible bucle infinito)"
                })
            else:
                status, result = result_queue.get()
                if status == "success":
                    self.mostrar_en_consola("\n🚀 Resultados de la ejecución:")
                    self.mostrar_en_consola(result)
                else:
                    execution_errors.append({
                        "tipo": "ejecución",
                        "linea": "desconocida",
                        "mensaje": f"Error de ejecución: {result}"
                    })
                    
        except SyntaxError as syn_err:
            error_msg = f"Error de sintaxis en línea {syn_err.lineno}: {syn_err.msg}"
            self.highlight_error_line(syn_err.lineno)
            execution_errors.append({
                "tipo": "ejecución",
                "linea": syn_err.lineno,
                "mensaje": error_msg
            })
        except Exception as e:
            execution_errors.append({
                "tipo": "ejecución",
                "linea": "desconocida",
                "mensaje": f"Error inesperado: {str(e)}"
            })
        finally:
            sys.stdout = old_stdout
            if execution_errors:
                self._mostrar_errores(execution_errors)

    def _mostrar_errores(self, execution_errors=None):
        """Muestra los errores clasificados por tipo"""
        # Crear secciones para cada tipo de error
        error_types = {
            "léxico": "Errores Léxicos",
            "sintáctico": "Errores Sintácticos",
            "semántico": "Errores Semánticos",
            "ejecución": "Errores de Ejecución"
        }
        
        # Agrupar errores por tipo
        grouped_errors = {k: [] for k in error_types}
        for error in global_errors + (execution_errors if execution_errors else []):
            if isinstance(error, dict) and "tipo" in error and error["tipo"] in error_types:
                grouped_errors[error["tipo"]].append(error)
        
        # Mostrar en la tabla
        for error_type, title in error_types.items():
            if grouped_errors[error_type]:
                # Agregar encabezado
                self.error_list.insert("", tk.END, values=(f"===== {title} =====",))
                
                # Agregar errores
                for error in grouped_errors[error_type]:
                    line_info = f"Línea {error['linea']}: " if "linea" in error and isinstance(error["linea"], int) else ""
                    self.error_list.insert("", tk.END, values=(f"  {line_info}{error['mensaje']}",))
        
        self.error_list.update_idletasks()
        print("🚀 Análisis finalizado.\n")
        
    def print_ast(self, node, level=0):
        """Muestra el AST en la consola para depuración"""
        indent = "  " * level
        node_info = f"{indent}{type(node).__name__}"
        
        if hasattr(node, 'linea'):
            node_info += f" (línea {node.linea})"
        
        self.mostrar_en_consola(node_info)
        
        # Recorrer hijos del nodo
        if isinstance(node, NodoPrograma):
            for decl in node.declaraciones:
                self.print_ast(decl, level + 1)
        elif isinstance(node, NodoIf):
            self.mostrar_en_consola(f"{indent}  Condición:")
            self.print_ast(node.condicion, level + 2)
            self.mostrar_en_consola(f"{indent}  Cuerpo IF:")
            for stmt in node.cuerpo_if:
                self.print_ast(stmt, level + 2)
            if node.cuerpo_else:
                self.mostrar_en_consola(f"{indent}  Cuerpo ELSE:")
                for stmt in node.cuerpo_else:
                    self.print_ast(stmt, level + 2)
        elif isinstance(node, NodoMientras):
            self.mostrar_en_consola(f"{indent}  Condición:")
            self.print_ast(node.condicion, level + 2)
            self.mostrar_en_consola(f"{indent}  Cuerpo:")
            for stmt in node.cuerpo:
                self.print_ast(stmt, level + 2)
        elif isinstance(node, NodoPara):
            self.mostrar_en_consola(f"{indent}  Variable: {node.variable}")
            self.mostrar_en_consola(f"{indent}  Desde:")
            self.print_ast(node.inicio, level + 2)
            self.mostrar_en_consola(f"{indent}  Hasta:")
            self.print_ast(node.fin, level + 2)
            if node.paso:
                self.mostrar_en_consola(f"{indent}  Paso:")
                self.print_ast(node.paso, level + 2)
            self.mostrar_en_consola(f"{indent}  Cuerpo:")
            for stmt in node.cuerpo:
                self.print_ast(stmt, level + 2)
        elif isinstance(node, NodoRepetir):
            self.mostrar_en_consola(f"{indent}  Cuerpo:")
            for stmt in node.cuerpo:
                self.print_ast(stmt, level + 2)
            self.mostrar_en_consola(f"{indent}  Condición:")
            self.print_ast(node.condicion, level + 2)
        elif isinstance(node, NodoMostrar):
            self.mostrar_en_consola(f"{indent}  Expresiones:")
            for expr in node.expresiones:
                self.print_ast(expr, level + 2)
        elif isinstance(node, (NodoBinario, NodoUnario)):
            # No es necesario recorrer hijos aquí, ya se muestran en el nodo principal
            pass
        elif isinstance(node, (NodoIdentificador, NodoLiteral)):
            # Nodos hoja, no requieren recorrido adicional
            pass
        
    def auto_indent(self, event=None):
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

    def run(self):
        self.root.mainloop()

    def add_copy_functionality(self):
        # Crear menú contextual para copiar
        self.error_list.bind("<Button-3>", self.show_error_context_menu)
        
        # Crear menú contextual
        self.error_context_menu = tk.Menu(self.root, tearoff=0)
        self.error_context_menu.add_command(label="Copiar", command=self.copy_selected_errors)
        
        # Botón para copiar todos los errores
        self.copy_all_button = tk.Button(
            self.error_list.master, 
            text="Copiar Todos los Errores", 
            command=self.copy_all_errors
        )
        self.copy_all_button.pack(side=tk.BOTTOM, fill=tk.X)

    def show_error_context_menu(self, event):
        """Muestra el menú contextual para copiar errores"""
        try:
            self.error_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.error_context_menu.grab_release()

    def copy_selected_errors(self):
        """Copia los errores seleccionados al portapapeles"""
        selected_items = self.error_list.selection()
        if not selected_items:
            return
            
        error_text = ""
        for item in selected_items:
            error_values = self.error_list.item(item, "values")
            if error_values:
                error_text += error_values[0] + "\n"
        
        if error_text:
            self.root.clipboard_clear()
            self.root.clipboard_append(error_text.strip())

    def copy_all_errors(self):
        """Copia todos los errores al portapapeles"""
        all_errors = ""
        for item in self.error_list.get_children():
            error_values = self.error_list.item(item, "values")
            if error_values:
                all_errors += error_values[0] + "\n"
        
        if all_errors:
            self.root.clipboard_clear()
            self.root.clipboard_append(all_errors.strip())


    def validate_optimized_tac(self, tac_code, original_tac):
        """Valida que el TAC optimizado conserve todas las variables necesarias"""
        # Obtener todas las variables declaradas en el original
        original_vars = set()
        for line in original_tac:
            if '=' in line and not line.strip().startswith('print('):
                var = line.split('=')[0].strip()
                original_vars.add(var)
        
        # Verificar que no falten variables esenciales
        optimized_vars = set()
        for line in tac_code:
            if '=' in line and not line.strip().startswith('print('):
                var = line.split('=')[0].strip()
                optimized_vars.add(var)
        
        missing_vars = original_vars - optimized_vars
        if missing_vars:
            raise ValueError(f"Variables faltantes después de optimizar: {', '.join(missing_vars)}")

if __name__ == "__main__":
    app = CompilerApp()
    app.run()

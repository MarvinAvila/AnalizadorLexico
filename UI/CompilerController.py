import sys
import ast
from io import StringIO
from threading import Thread
from queue import Queue
from SyntaxAnalyzer.AST import NodoPrograma
from GlobalErrors.ErrorsManager import global_errors
from LexicalAnalyzer.Lexer import lexer
from SyntaxAnalyzer.Parser import parser, variables, constantes
from SemanticAnalyzer.SemanticAnalyzer import SemanticAnalyzer
from CodeGenerator.TACGenerator import TACGenerator
from CodeGenerator.Translator import Translator
from CodeGenerator.Optimizer import Optimizer

class CompilerController:
    def __init__(self, code_editor, error_panel, console_panel):
        self.code_editor = code_editor
        self.error_panel = error_panel
        self.console_panel = console_panel
        
        self._execution_thread = None
        self._should_stop = False
        
        self._setup_parser_callbacks()


    def _setup_parser_callbacks(self):
        """Configura los callbacks para el parser"""
        parser.mostrar_en_consola = self.console_panel.mostrar_en_consola

    def analyze_code(self):
        """Orquesta todo el proceso de compilación"""
        try:
            # 1. Preparación inicial
            self._prepare_compilation_environment()
            code = self.code_editor.get_code()

            # 2. Pipeline de compilación
            ast_node = self._perform_lexical_syntactic_analysis(code)
            if not ast_node or self._has_errors():
                return

            self._perform_semantic_analysis(ast_node)
            if self._has_errors():
                return

            tac_code = self._generate_intermediate_code(ast_node)
            optimized_tac = self._optimize_code(tac_code)
            python_code = self._translate_to_python(optimized_tac)

            # 3. Ejecución
            self._execute_python_code(python_code)

        except Exception as e:
            self._handle_unexpected_error(e)
        finally:
            self._display_errors()

    def _prepare_compilation_environment(self):
        """Reinicia todos los estados para una nueva compilación"""
        global_errors.clear()
        variables.clear()
        constantes.clear()
        lexer.lineno = 1
        self.error_panel.clear()
        self.console_panel.clear()
        print("🚀 Iniciando análisis de código...\n")

    def _perform_lexical_syntactic_analysis(self, code):
        """Realiza análisis léxico y sintáctico"""
        print("🔍 Realizando análisis léxico...")
        try:
            lexer.input(code)
            # Solo para verificar que el lexer funciona
            for _ in lexer:
                pass
        except Exception as e:
            self._add_error("léxico", f"Error léxico: {str(e)}", 0)
            return None

        print("🔍 Realizando análisis sintáctico...")
        try:
            # Reiniciar el lexer para el análisis sintáctico
            lexer.lineno = 1
            ast_node = parser.parse(code, lexer=lexer, tracking=True)
            if not isinstance(ast_node, NodoPrograma):
                self._add_error("sintáctico", "No se generó un AST válido", 0)
                return None
            return ast_node
        except Exception as e:
            self._add_error("sintáctico", f"Error de sintaxis: {str(e)}", 0)
            return None

    def _perform_semantic_analysis(self, ast_node):
        """Realiza análisis semántico"""
        print("🔍 Realizando análisis semántico...")
        try:
            #reiniciar el lexer para el análisis semántico
            lexer.lineno = 1
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast_node)
        except Exception as e:
            self._add_error("semántico", f"Error semántico: {str(e)}", 0)

    def _generate_intermediate_code(self, ast_node):
        """Genera código de tres direcciones (TAC)"""
        print("🔧 Generando código intermedio...")
        try:
            tac_gen = TACGenerator()
            tac_code = tac_gen.generate(ast_node)
            return tac_code
        except Exception as e:
            self._add_error("generación", f"Error generando TAC: {str(e)}", 0)
            raise

    def _optimize_code(self, tac_code):
        """Optimiza el código intermedio"""
        print("⚡ Optimizando código...")
        try:
            optimizer = Optimizer()
            optimized_tac = optimizer.optimize(tac_code)
            return optimized_tac
        except Exception as e:
            print(f"⚠️ Advertencia de optimización: {str(e)}")
            return tac_code  # Fallback al código no optimizado

    def _translate_to_python(self, tac_code):
        """Traduce TAC a Python"""
        print("🔄 Traduciendo a Python...")
        try:
            translator = Translator(tac_code)
            python_code = translator.translate()

            print("🐍 Código Python formateado:\n", python_code)

            return python_code


        except IndentationError as e:
            import re
            match = re.search(r"línea (\d+)", str(e))
            if match:
                linea = int(match.group(1))
                self.code_editor.highlight_error_line(linea)
            else:
                linea = 0
            self._add_error("traducción", f"Error traduciendo a Python: {str(e)}", linea)
            raise

        except Exception as e:
            self._add_error("traducción", f"Error traduciendo a Python: {str(e)}", 0)
            raise


    def _execute_python_code(self, python_code):
        """Ejecuta el código Python generado de forma segura"""
        self.console_panel.mostrar_en_consola("\n⚡ Ejecutando código...")
        # Redirección de salida
        old_stdout = sys.stdout
        try:
            # Validación de sintaxis
            ast.parse(python_code)

            # Entorno seguro
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

            sys.stdout = output_capture = StringIO()

            # Ejecución con timeout
            result_queue = Queue()

            def execute():
                try:
                    safe_env["_should_stop"] = lambda: self._should_stop  # función para consultar estado
                    exec(python_code, safe_env)
                    result_queue.put(("success", output_capture.getvalue()))
                except Exception as e:
                    result_queue.put(("error", str(e)))


            self._execution_thread = Thread(target=execute)
            self._execution_thread.start()
            self._execution_thread.join(timeout=5)

            if self._execution_thread.is_alive():
                self._execution_thread.join(timeout=0)
                self._add_error("ejecución", "Tiempo excedido (posible bucle infinito)", 0)
            else:
                status, result = result_queue.get()
                if status == "success":
                    self.console_panel.mostrar_en_consola("\n✅ Resultado de ejecución:")
                    self.console_panel.mostrar_en_consola(result)
                else:
                    self._add_error("ejecución", result, 0)

        except SyntaxError as e:
            self.code_editor.highlight_error_line(e.lineno)
            self._add_error("ejecución", f"Error de sintaxis en línea {e.lineno}: {e.msg}", e.lineno)
        except Exception as e:
            self._add_error("ejecución", f"Error inesperado: {str(e)}", 0)
        finally:
            sys.stdout = old_stdout
            
    def stop_execution(self):
        """Detiene la ejecución en curso del código"""
        if self._execution_thread and self._execution_thread.is_alive():
            self._should_stop = True
            self.console_panel.mostrar_en_consola("\n⛔ Ejecución detenida por el usuario.")

    def _add_error(self, error_type, message, line):
        """Agrega un error a la lista global"""
        global_errors.append({
            "tipo": error_type,
            "linea": line,
            "mensaje": message
        })

    def _has_errors(self):
        """Verifica si hay errores en la lista global"""
        return bool(global_errors)

    def _display_errors(self):
        """Muestra todos los errores acumulados"""
        if not global_errors:
            self.console_panel.mostrar_en_consola("\n✅ Análisis completado sin errores")
            return

        # Agrupar errores por tipo
        error_groups = {}
        for error in global_errors:
            if error["tipo"] not in error_groups:
                error_groups[error["tipo"]] = []
            error_groups[error["tipo"]].append(error)

        # Mostrar en el panel de errores
        for error_type, errors in error_groups.items():
            self.error_panel.add_error_section(f"Errores {error_type}")
            for error in errors:
                line_info = f"Línea {error['linea']}: " if error["linea"] else ""
                self.error_panel.add_error(error_type, f"{line_info}{error['mensaje']}")

    def _handle_unexpected_error(self, error):
        """Maneja errores inesperados en el proceso de compilación"""
        error_msg = str(error)
        self.error_panel.add_error("sistema", error_msg, 0)
        self._add_error("sistema", error_msg, 0)
        self._display_errors()


    def _validate_python_code(self, code):
        """Valida que el código Python generado tenga identación correcta"""
        lines = code.split('\n')
        indent_stack = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            current_indent = len(line) - len(line.lstrip())

            if stripped.endswith(':'):
                if i + 1 < len(lines) and not lines[i + 1].startswith(' ' * (current_indent + 4)):
                    raise IndentationError(f"Falta identación después de ':' en línea {i}")
                indent_stack.append(current_indent)
            elif stripped and current_indent < (indent_stack[-1] if indent_stack else 0):
                if not any(stripped.startswith(kw) for kw in ['else', 'elif', 'except', 'finally']):
                    indent_stack.pop()

        if indent_stack:
            raise IndentationError("Bloques sin cerrar correctamente")

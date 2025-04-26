# SemanticAnalyzer/SemanticAnalyzer.py
from GlobalErrors.ErrorsManager import global_errors
from SyntaxAnalyzer.AST import NodoPrograma,NodoError
from SyntaxAnalyzer import AST

class SemanticAnalyzer:
    def __init__(self):
        self.variables = {}  # {nombre: (tipo, valor, línea_declaración)}
        self.constantes = {}  # {nombre: (tipo, valor, línea_declaración)}
        self.current_scope = "global"
        self.errors = global_errors

    def analyze(self, ast):
        """Método principal para iniciar el análisis semántico"""
        self.variables.clear()   # ✅ limpiar estado anterior
        self.constantes.clear()  # ✅ limpiar constantes también
        if isinstance(ast, NodoPrograma):
            self.visit_program(ast)
        else:
            self._add_error("El AST no comienza con un NodoPrograma", 0)

    def visit_program(self, node):
        """Visita un nodo programa"""
        for declaration in node.declaraciones:
            if isinstance(declaration, NodoError):
                self._add_error(declaration.mensaje, declaration.linea)
                return
            self.visit(declaration)

    def visit(self, node):
        # Ignorar nodos de error para no contaminar el análisis
        if node is None or isinstance(node, AST.NodoError):
            return None  # No hacemos nada con NodoError

        if isinstance(node, str):
            self._add_error(f"Se esperaba un nodo AST pero se recibió un string: '{node}'", 0)
            return None

        method_name = f'visit_{type(node).__name__.lower()}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)


    def generic_visit(self, node):
        """Método genérico para nodos no implementados"""
        self._add_error(f"Tipo de nodo no implementado: {type(node).__name__}", node.linea)

    # ---------------------------------------------------------------
    # Métodos para visitar nodos específicos
    # ---------------------------------------------------------------

    def visit_nododeclaracion(self, node):
        """Verifica declaraciones de variables"""
        # Verificar si la variable ya fue declarada
        var_name = node.identificador.nombre  # Obtener el nombre del identificador
        if var_name in self.variables or var_name in self.constantes:
            self._add_error(f"Variable '{var_name}' ya declarada", node.linea)
            return

        # Verificar tipo en asignación si existe
        # Si es constante, inferir su tipo real y sobrescribir
        if getattr(node, "es_constante", False):
            tipo_real = self.visit(node.expresion)
            node.tipo = tipo_real
            self.constantes[var_name] = (tipo_real, None, node.linea)
            return  # No continúa como variable normal

        # Verificar tipo en asignación si existe
        if node.expresion:
            expr_type = self.visit(node.expresion)
            if expr_type and not self._check_type_compatibility(node.tipo, expr_type, "declaración"):
                self._add_error(
                    f"Tipo incompatible en declaración: esperaba '{node.tipo}', obtuvo '{expr_type}'", 
                    node.linea
                )
        if var_name in self.constantes:
            self._add_error(f"No se puede modificar la constante '{var_name}'", node.linea)
            return



        # Registrar la variable
        self.variables[var_name] = (node.tipo, None, node.linea)

    def visit_nodoasignacion(self, node):
        """Verifica asignaciones de variables"""
        # Verificar que el identificador sea un nodo válido
        if not isinstance(node.identificador, AST.NodoIdentificador):
            self._add_error("Identificador inválido en asignación", node.linea)
            return

        # Extraer el nombre del identificador
        var_name = node.identificador.nombre
        
        # Verificar si la variable existe
        if var_name not in self.variables:
            self._add_error(f"Variable '{var_name}' no declarada", node.linea)
            return

        # Obtener tipo de la variable (usando var_name en lugar del nodo)
        var_type = self.variables[var_name][0]
        
        # Verificar la expresión
        expr_type = self.visit(node.expresion)
        
        # Verificar compatibilidad de tipos
        if expr_type and not self._check_type_compatibility(var_type, expr_type, "asignación"):
            self._add_error(
                f"Tipo incompatible en asignación: esperaba '{var_type}', obtuvo '{expr_type}'", 
                node.linea
            )

    def visit_nodoif(self, node):
        # Validación de estructura general
        self._verificar_estructura('si', node, [
            ('condicion', "una condición válida"),
            ('cuerpo_if', "instrucciones después de 'ENTONCES'")
        ])

        # Verifica tipo de condición
        cond_type = self.visit(node.condicion)
        if cond_type != "booleano":
            self._add_error("La condición del 'si' debe ser booleana", node.linea)

        # Verifica cuerpo del if
        for stmt in node.cuerpo_if:
            self.visit(stmt)
            if isinstance(stmt, AST.NodoError):
                self._add_error("La sentencia 'si' contiene instrucciones inválidas (posible error de estructura)", node.linea)

        if getattr(node, "tiene_sino", False):  # solo entra si el usuario realmente escribió un "sino"
            if any(isinstance(stmt, AST.NodoError) for stmt in node.cuerpo_else):
                self._add_error("La sentencia 'sino' contiene instrucciones inválidas", node.linea)
            elif len(node.cuerpo_else) == 0:
                self._add_error("La sentencia 'sino' está vacía o mal definida", node.linea)
            else:
                for stmt in node.cuerpo_else:
                    self.visit(stmt)

    def visit_nodomientras(self, node):
        """Verifica sentencias while"""
        # Verificar que la condición sea booleana
        
        self._verificar_estructura('mientras', node, [
            ('condicion', "una condición booleana"),
            ('cuerpo', "un bloque de instrucciones después de 'HACER'")
        ])
        
        cond_type = self.visit(node.condicion)
        if cond_type != "booleano":
            self._add_error("La condición del 'mientras' debe ser booleana", node.linea)

        # Verificar cuerpo del while
        for stmt in node.cuerpo:
            self.visit(stmt)

    def visit_nodopara(self, node):
        """Verifica sentencias for"""
        
        self._verificar_estructura('para', node, [
            ('inicio', "un valor inicial (DESDE)"),
            ('fin', "un valor final (HASTA)"),
            ('cuerpo', "un bloque de instrucciones después de 'HACER'")
        ])
        # paso puede ser opcional, así que podrías omitirlo
        
        # Validar tipos de inicio, fin y paso
        inicio_type = self.visit(node.inicio)
        fin_type = self.visit(node.fin)

        if inicio_type != "entero" or fin_type != "entero":
            self._add_error("Los límites del 'para' deben ser enteros", node.linea)

        if node.paso:
            paso_type = self.visit(node.paso)
            if paso_type != "entero":
                self._add_error("El paso del 'para' debe ser entero", node.linea)
                paso_valor = self._evaluate_literal(node.paso)
            if isinstance(node.paso, AST.NodoLiteral) and isinstance(node.paso.valor, (int, float)) and node.paso.valor == 0:
                self._add_error("El paso del 'para' no puede ser cero (causaría bucle infinito)", node.linea)

        # Si es de tipo literal y se puede evaluar:
        if isinstance(node.inicio, AST.NodoLiteral) and isinstance(node.fin, AST.NodoLiteral):
            if node.inicio.valor > node.fin.valor and not node.paso:
                self._add_error("El valor inicial del ciclo 'para' es mayor que el final y no se especificó un paso negativo", node.linea)


        # ✅ Registrar la variable de control antes de visitar el cuerpo
        self.variables[node.variable.nombre] = ("entero", None, node.linea)

        # Visitar cuerpo del ciclo
        for stmt in node.cuerpo:
            self.visit(stmt)

            
    def visit_nodorepetir(self, node):
        """Verifica sentencias repetir-hasta"""

        self._verificar_estructura('repetir', node, [
            ('cuerpo', "un bloque de instrucciones dentro del ciclo"),
            ('condicion', "una condición después de 'HASTA_QUE'")
        ])

        # Verificar cuerpo del repetir
        for stmt in node.cuerpo:
            self.visit(stmt)
        
        # Verificar que la condición sea booleana
        cond_type = self.visit(node.condicion)
        if cond_type != "booleano":
            self._add_error("La condición del 'hasta_que' debe ser booleana", node.linea)

    def visit_nodobinario(self, node):
        """Verifica operaciones binarias de manera optimizada"""
        # Memoización: Verificar si ya hemos analizado este nodo
        if hasattr(node, '_cached_type'):
            return node._cached_type
            
        # Visitar subárboles solo una vez
        left_type = self.visit(node.izquierda)
        right_type = self.visit(node.derecha)
        
        print(f"👉 Operación: {node.operador} | Izq: {left_type} | Der: {right_type} (Línea {node.linea})")
        
        # Validación temprana si hay tipos nulos (por errores previos)
        if left_type is None or right_type is None:
            return None
        
        # Diccionario de operaciones para mejor rendimiento
        OPERACIONES = {
            # Operadores aritméticos
            '+': self._validar_aritmetica,
            '-': self._validar_aritmetica,
            '*': self._validar_aritmetica,
            '/': self._validar_aritmetica,
            '%': self._validar_aritmetica,
            
            # Operadores lógicos
            'AND': self._validar_logica,
            'OR': self._validar_logica,
            
            # Operadores de comparación
            '>': self._validar_comparacion,
            '<': self._validar_comparacion,
            '>=': self._validar_comparacion,
            '<=': self._validar_comparacion,
            '==': self._validar_comparacion,
            '!=': self._validar_comparacion
        }
        
        # Obtener la función de validación adecuada
        validacion = OPERACIONES.get(node.operador)
        if validacion is None:
            self._add_error(f"Operador '{node.operador}' no reconocido", node.linea)
            return None
        
        # Ejecutar validación específica
        result_type = validacion(node, left_type, right_type)
        
        # Cachear el resultado para futuras visitas
        node._cached_type = result_type
        return result_type

    def _validar_aritmetica(self, node, left_type, right_type):
        """Valida operaciones aritméticas"""
        if node.operador == '%':
            if left_type != 'entero' or right_type != 'entero':
                self._add_error(f"El operador '%' solo acepta operandos enteros", node.linea)
                return None
            return 'entero'

        if left_type not in ['entero', 'decimal'] or right_type not in ['entero', 'decimal']:
            self._add_error(f"Operación '{node.operador}' no válida para tipos '{left_type}' y '{right_type}'", node.linea)
            return None
        
        if node.operador == '/' and isinstance(node.derecha, AST.NodoLiteral) and node.derecha.valor == 0:
            self._add_error("División entre cero detectada", node.linea)

        return 'decimal' if 'decimal' in [left_type, right_type] else 'entero'



    def _validar_logica(self, node, left_type, right_type):
        """Valida operaciones lógicas"""
        if left_type != 'booleano' or right_type != 'booleano':
            self._add_error(f"Operación '{node.operador}' requiere operandos booleanos", node.linea)
            return None
        return 'booleano'

    def _validar_comparacion(self, node, left_type, right_type):
        """Valida operaciones de comparación"""
        if left_type != right_type:
            self._add_error(f"Tipos incompatibles en comparación '{node.operador}': {left_type} y {right_type}", node.linea)
            return None
        return 'booleano'

    def visit_nodounario(self, node):
        """Verifica operaciones unarias"""
        expr_type = self.visit(node.expresion)
        
        if node.operador == 'NOT':
            if expr_type != 'booleano':
                self._add_error("Operador 'NOT' requiere operando booleano", node.linea)
            return 'booleano'
        elif node.operador == '-':
            if expr_type not in ['entero', 'decimal']:
                self._add_error("Negación solo aplica a números", node.linea)
            return expr_type
        
        return None

    def visit_nodoidentificador(self, node):
        """Verifica referencias a variables"""
        if node.nombre not in self.variables and node.nombre not in self.constantes:
            self._add_error(f"Identificador '{node.nombre}' no declarado", node.linea)
            return None
        
        # Retornar el tipo de la variable/constante
        if node.nombre in self.variables:
            return self.variables[node.nombre][0]
        else:
            return self.constantes[node.nombre][0]
        
    def visit_nodomostrar(self, node):
        """Análisis semántico para sentencias mostrar"""
        if not node.expresiones:
            self._add_error("La sentencia 'mostrar' debe incluir al menos una expresión", node.linea)
            return None
        
        for expr in node.expresiones:
            expr_type = self.visit(expr)
            if expr_type is None:
                self._add_error(f"Expresión inválida en 'mostrar'", 
                            getattr(expr, 'linea', node.linea))
        
        return None  # Mostrar no devuelve valor

    def visit_nodoliteral(self, node):
        """Retorna el tipo de un literal"""
        return node.tipo

    # ---------------------------------------------------------------
    # Métodos auxiliares
    # ---------------------------------------------------------------

    def _check_type_compatibility(self, expected_type, actual_type, context):
        """Verifica compatibilidad de tipos"""
        valid_combinations = {
            "entero": ["entero"],
            "decimal": ["entero", "decimal"],
            "cadena": ["cadena"],
            "booleano": ["booleano"],
            "constante": ["entero", "decimal", "cadena", "booleano"],
        }
        return expected_type in valid_combinations and actual_type in valid_combinations[expected_type]
    
    def _verificar_estructura(self, nombre, nodo, campos):
        """
        Verifica que los campos clave de una estructura de control estén definidos.
        Si falta alguno, lanza un error semántico claro.
        
        Parámetros:
        - nombre: Nombre de la estructura ('si', 'mientras', etc.)
        - nodo: El nodo AST a verificar
        - campos: Lista de tuplas (nombre_campo, mensaje_descriptivo)
        """
        for campo, descripcion in campos:
            valor = getattr(nodo, campo, None)
            if valor is None or (isinstance(valor, list) and len(valor) == 0):
                self._add_error(
                    f"La sentencia '{nombre}' no tiene {descripcion}",
                    getattr(nodo, "linea", 0)
                )


    def _add_error(self, message, line):
        """Agrega un error semántico a la lista global"""
        self.errors.append({
            "tipo": "semántico",
            "linea": line,
            "mensaje": f"❌ {message}"
        })
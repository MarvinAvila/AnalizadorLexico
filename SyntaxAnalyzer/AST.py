# AST.py
class Nodo:
    """Clase base para todos los nodos del AST."""
    def accept(self, visitor):
        """Patrón Visitor para recorrer el AST."""
        return visitor.visit(self)


class NodoPrograma(Nodo):
    """Nodo raíz del AST. Representa un programa completo."""
    def __init__(self, declaraciones, linea):
        self.declaraciones = declaraciones  # Lista de nodos (declaraciones, if, while, etc.)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"
        
# ---------------------------------------------------------------
# Estructuras de Control
# ---------------------------------------------------------------

class NodoIf(Nodo):
    """Nodo para la estructura 'si-entonces-sino'."""
    def __init__(self, condicion, cuerpo_if, cuerpo_else, linea):
        self.condicion = condicion  # NodoExpresion (debe ser booleana)
        self.cuerpo_if = cuerpo_if    # Lista de nodos (bloque THEN)
        self.cuerpo_else = cuerpo_else  # Lista de nodos (bloque ELSE, opcional)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoMientras(Nodo):
    """Nodo para la estructura 'mientras-hacer'."""
    def __init__(self, condicion, cuerpo, linea):
        self.condicion = condicion  # NodoExpresion (debe ser booleana)
        self.cuerpo = cuerpo        # Lista de nodos (bloque DO)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoRepetir(Nodo):
    """Nodo para la estructura 'repetir-hasta_que'."""
    def __init__(self, cuerpo, condicion, linea):
        self.cuerpo = cuerpo      # Lista de nodos (bloque REPEAT)
        self.condicion = condicion  # NodoExpresion (debe ser booleana)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoPara(Nodo):
    """Nodo para la estructura 'para-desde-hasta-con_paso'."""
    def __init__(self, variable, inicio, fin, paso, cuerpo, linea):
        self.variable = variable  # NodoIdentificador (variable de iteración)
        self.inicio = inicio      # NodoExpresion (valor inicial, debe ser entero)
        self.fin = fin            # NodoExpresion (valor final, debe ser entero)
        self.paso = paso          # NodoExpresion (opcional, debe ser entero)
        self.cuerpo = cuerpo      # Lista de nodos (bloque DO)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoMostrar(Nodo):
    """Nodo para la estructura 'mostrar'."""
    def __init__(self, expresiones, linea):
        self.expresiones = expresiones  # Lista de nodos expresión
        self.linea = linea
        
    def __repr__(self):
        return f"Mostrar(linea={self.linea}, exprs={len(self.expresiones)})"

# ---------------------------------------------------------------
# Declaraciones y Expresiones
# ---------------------------------------------------------------

class NodoDeclaracion(Nodo):
    """Nodo para declaración de variables (con/sin asignación)."""
    def __init__(self, tipo, identificador, expresion, linea, es_constante=False):
        self.tipo = tipo          # Tipo de dato ("entero", "cadena", etc.)
        self.identificador = identificador  # Nombre de la variable
        self.expresion = expresion  # NodoExpresion (valor inicial, opcional)
        self.linea = linea
        self.es_constante = es_constante  
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoAsignacion(Nodo):
    """Nodo para asignación de variables."""
    def __init__(self, identificador, expresion, linea):
        self.identificador = identificador  # Nombre de la variable
        self.expresion = expresion  # NodoExpresion (valor a asignar)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoIdentificador(Nodo):
    """Nodo para referencias a variables/constantes."""
    def __init__(self, nombre, linea):
        self.nombre = nombre      # Nombre del identificador
        self.linea = linea
        
    def __repr__(self):
        return f"{type(self).__name__}(nombre='{self.nombre}', linea={self.linea})"
    
    def __str__(self):
        return self.__repr__()

class NodoLiteral(Nodo):
    """Nodo para valores literales (números, cadenas, booleanos)."""
    def __init__(self, tipo, valor, linea):
        self.tipo = tipo          # Tipo del literal ("entero", "cadena", etc.)
        self.valor = valor        # Valor concreto (42, "hola", True, etc.)
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"

class NodoBinario(Nodo):
    """Nodo para operaciones binarias (+, -, *, /, AND, OR, etc.)."""
    def __init__(self, operador, izquierda, derecha, linea):
        self.operador = operador
        self.izquierda = izquierda
        self.derecha = derecha
        self.linea = linea
        self.tipo = None  # Para ser determinado por el analizador semántico
        
    def __repr__(self):
        return f"Binario({self.operador}, {self.izquierda}, {self.derecha})"

class NodoUnario(Nodo):
    """Nodo para operaciones unarias (NOT, negativo)."""
    def __init__(self, operador, expresion, linea):
        self.operador = operador  # Operador ("NOT", "-")
        self.expresion = expresion  # NodoExpresion
        self.linea = linea
    def __repr__(self):
        return f"{type(self).__name__}(linea={self.linea})"
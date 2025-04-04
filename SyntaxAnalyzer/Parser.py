import ply.yacc as yacc
from LexicalAnalyzer.Lexer import tokens
from GlobalErrors.ErrorsManager import global_errors
from SyntaxAnalyzer.AST import Nodo,NodoIf,NodoAsignacion,NodoDeclaracion,NodoBinario,NodoIdentificador,NodoLiteral,NodoMientras,NodoMostrar,NodoRepetir,NodoPara,NodoUnario,NodoPrograma
from SemanticAnalyzer.SemanticAnalyzer import SemanticAnalyzer


semantic_analyzer = SemanticAnalyzer()

# Definir precedencia para resolver conflictos
precedence = (
    ("left", "AND", "OR"),
    ("left", "SUMA", "RESTA"),
    ("left", "MULTIPLICACION", "DIVISION"),
    ("right", "NOT"),
    ("left", "ASIGNACION"),
    ("left", "PUNTO_COMA"),
    ("nonassoc", "MAYOR_QUE", "MENOR_QUE", "MAYOR_IGUAL", "MENOR_IGUAL", "IGUAL_IGUAL", "DIFERENTE"),
)

# Diccionario de tipos de datos normalizados
TIPOS_DE_DATOS = {
    "ENTERO": "entero",
    "DECIMAL": "decimal",
    "CADENA": "cadena",
    "BOOLEANO": "booleano",
    "CONSTANTE": "constante",
}

# Excepción para errores semánticos
class SemanticError(Exception):
    """Excepción para errores semánticos."""
    pass

if not isinstance(global_errors, list):
    global_errors = []

variables = {}  
constantes = {} 


# Modifica la función p_programa:
def p_programa(p):
    """programa : INICIO declaraciones FIN"""
    program_node = NodoPrograma(declaraciones=p[2], linea=p.lineno(1))
    
    # Realizar análisis semántico
    semantic_analyzer.analyze(program_node)
    
    p[0] = program_node

def p_declaraciones(p):
    """declaraciones : declaraciones declaracion
                    | declaracion"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]  
    else:
        p[0] = [p[1]] 

def p_declaracion(p):
    """declaracion : declaracion_simple
                | declaracion_con_asignacion
                | asignacion
                | constante
                | sentencia_if
                | sentencia_mientras
                | sentencia_para
                | sentencia_repetir
                | sentencia_mostrar
                | empty"""
    
    p[0]=p[1]


def p_empty(p):
    "empty :"
    pass

def normalizar_tipo(tipo):
    """Normaliza un tipo de dato a su formato estándar (minúsculas)."""
    return TIPOS_DE_DATOS.get(tipo.upper(), tipo.lower())

def p_sentencia_if(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones FIN_SI
                   | SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones SINO declaraciones FIN_SI"""
    # Generar NodoIf(condicion, cuerpo_if, cuerpo_else, linea)
    p[0] = NodoIf(
        condicion=p[3], 
        cuerpo_if=p[6], 
        cuerpo_else=p[8] if len(p) > 7 else None, 
        linea=p.lineno(1)
    )

def p_sentencia_mientras(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER HACER declaraciones FIN_MIENTRAS"""
    # Generar NodoWhile(condicion, cuerpo, linea)
    p[0] = NodoMientras(
        condicion=p[3], 
        cuerpo=p[6], 
        linea=p.lineno(1)
    )

def p_sentencia_para(p):
    """sentencia_para : PARA IDENTIFICADOR DESDE expresion HASTA expresion HACER declaraciones FIN_PARA
                     | PARA IDENTIFICADOR DESDE expresion HASTA expresion CON_PASO expresion HACER declaraciones FIN_PARA"""
    var_node = NodoIdentificador(nombre=p[2], linea=p.lineno(2))
    
    if len(p) == 10:  # Sin paso
        cuerpo = p[8]
        paso = None
    else:  # Con paso
        cuerpo = p[10]
        paso = p[8]
    
    p[0] = NodoPara(
        variable=var_node,
        inicio=p[4],
        fin=p[6],
        paso=paso,
        cuerpo=cuerpo,  # Asegurar que sea lista de declaraciones
        linea=p.lineno(1)
    )

def p_instrucciones_para(p):
    """instrucciones_para : instruccion_para
                         | instrucciones_para instruccion_para"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

# Instrucciones específicas para PARA
def p_instruccion_para(p):
    """instruccion_para : sentencia_mostrar
                       | asignacion
                       | sentencia_if
                       | sentencia_mientras"""
    p[0] = p[1]
    

def p_sentencia_repetir(p):
    """sentencia_repetir : REPETIR declaraciones HASTA_QUE PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    p[0] = NodoRepetir(
        cuerpo=p[2],          # Lista de nodos (declaraciones dentro del REPETIR)
        condicion=p[5],       # Nodo de la expresión (condición del HASTA_QUE)
        linea=p.lineno(1)     # Línea donde empieza la sentencia
    )
    print(f"📌 Sentencia REPETIR convertida a AST en línea {p.lineno(1)}")

def p_sentencia_mostrar(p):
    """sentencia_mostrar : MOSTRAR lista_expresiones PUNTO_COMA"""
    if not p[2]:  # Si lista_expresiones está vacía
        raise SyntaxError("La sentencia 'mostrar' debe incluir expresiones", p.lineno(1))
    
    p[0] = NodoMostrar(
        expresiones=p[2],
        linea=p.lineno(1)
    )

def p_expresion(p):
    """expresion : LITERAL_ENTERO
                 | LITERAL_DECIMAL
                 | LITERAL_CADENA
                 | LITERAL_BOOLEANO
                 | IDENTIFICADOR
                 | expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | NOT expresion
                 | expresion MAYOR_QUE expresion
                 | expresion MENOR_QUE expresion
                 | expresion MAYOR_IGUAL expresion
                 | expresion MENOR_IGUAL expresion
                 | expresion IGUAL_IGUAL expresion
                 | expresion DIFERENTE expresion
                 | PARENTESIS_IZQ expresion PARENTESIS_DER"""
    
    # --- Caso 1: Literales o identificadores ---
    if len(p) == 2:
        if isinstance(p[1], tuple):  # Literal (ej: ("entero", 42))
            tipo, valor = p[1]
            p[0] = NodoLiteral(tipo=normalizar_tipo(tipo), valor=valor, linea=p.lineno(1))
        elif isinstance(p[1], str):  # Identificador (ej: "x")
            p[0] = NodoIdentificador(nombre=p[1], linea=p.lineno(1))
        else:
            raise SyntaxError(f"Tipo de expresión no reconocido: {type(p[1])}")

    # --- Caso 2: Expresión entre paréntesis ---
    elif len(p) == 4 and p[1] == '(' and p[3] == ')':
        p[0] = p[2]

    # --- Caso 3: Operaciones binarias/unarias ---
    else:
        if p[1] == 'NOT':
            if not isinstance(p[2], Nodo):
                raise SyntaxError(f"Operando de NOT debe ser expresión válida")
            p[0] = NodoUnario(operador="NOT", expresion=p[2], linea=p.lineno(1))
        else:
            if not isinstance(p[1], Nodo) or not isinstance(p[3], Nodo):
                raise SyntaxError(f"Operandos deben ser expresiones válidas")
            p[0] = NodoBinario(
                operador=p[2],
                izquierda=p[1],
                derecha=p[3],
                linea=p.lineno(2)
            )

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMA expresion
                         | expresion'''
    if len(p) == 4:
        if not isinstance(p[1], list):
            p[1] = [p[1]]  # Convertir a lista si no lo es
        p[0] = p[1] + [p[3]]
    else:
        # Asegurar que siempre devolvemos una lista de nodos
        p[0] = [p[1]] if isinstance(p[1], Nodo) else []


def p_declaracion_simple(p):
    """declaracion_simple : TIPO IDENTIFICADOR PUNTO_COMA"""
    # Generar NodoDeclaracion(tipo, identificador, valor=None, linea)
    p[0] = NodoDeclaracion(
        tipo=p[1], 
        identificador=NodoIdentificador(nombre=p[2], linea=p.lineno(2)), 
        expresion=None, 
        linea=p.lineno(2)
    )

def p_declaracion_con_asignacion(p):
    """declaracion_con_asignacion : TIPO IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""
    # Generar NodoDeclaracion(tipo, identificador, expresion, linea)
    p[0] = NodoDeclaracion(
        tipo=p[1], 
        identificador=NodoIdentificador(nombre=p[2], linea=p.lineno(2)), 
        expresion=p[4], 
        linea=p.lineno(2)
    )

def p_asignacion(p):
    """asignacion : IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""
    # Verificar que el identificador sea un string, no un nodo
    if isinstance(p[1], str):
        ident = NodoIdentificador(nombre=p[1], linea=p.lineno(1))
    else:
        # Manejar caso donde ya es un nodo (por si acaso)
        ident = p[1]
    
    p[0] = NodoAsignacion(
        identificador=ident,
        expresion=p[3],
        linea=p.lineno(1)
    )

def p_constante(p):
    """constante : CONSTANTE IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""  
    p[0] = NodoDeclaracion(
        tipo='constante',
        identificador=NodoIdentificador(nombre=p[2], linea=p.lineno(2)),
        expresion=p[4],
        linea=p.lineno(2),
        es_constante=True  # Marcar explícitamente como constante
    )

def es_tipo_valido(tipo_variable, tipo_valor):
    """Verifica si el tipo del valor es compatible con el tipo de la variable."""
    tipo_variable = tipo_variable.upper()
    tipo_valor = tipo_valor.upper()
    
    # Solo se permiten estos tipos de datos
    tipos_permitidos = {
        "ENTERO": ["ENTERO"],
        "DECIMAL": ["ENTERO", "DECIMAL"],
        "CADENA": ["CADENA"],
        "BOOLEANO": ["BOOLEANO"],
        "CONSTANTE": ["ENTERO", "DECIMAL", "CADENA", "BOOLEANO"],  # Constante puede ser de cualquier tipo
    }
    
    if tipo_variable not in tipos_permitidos:
        global_errors.append({
            "tipo": "semántico",
            "linea": 0, # No hay línea específica aquí
            "mensaje": f"Tipo de variable '{tipo_variable}' no permitido."
        })
    
    return tipo_valor in tipos_permitidos[tipo_variable]


def p_error(p):
    """Manejo de errores de sintaxis sin interrumpir el análisis."""
    if p:
        # Manejar caso específico de NodoIdentificador mal formado
        if hasattr(p, 'value') and isinstance(p.value, NodoIdentificador):
            error_msg = f"Error de sintaxis en línea {p.lineno}: Identificador '{p.value.nombre}' mal formado"
        else:
            error_msg = f"Error de sintaxis en línea {p.lineno}: Token inesperado '{p.value}'"
        
        global_errors.append({
            "tipo": "sintáctico",
            "linea": p.lineno,
            "mensaje": error_msg
        })
    else:
        error_msg = "Error de sintaxis: Fin de archivo inesperado"
        global_errors.append({
            "tipo": "sintáctico",
            "linea": 0,
            "mensaje": error_msg
        })


# Construcción del Parser
parser = yacc.yacc(start="programa")

def parse(self, code, **kwargs):
    self.code = code  # Almacenar el contenido del área de texto
    return super().parse(code, **kwargs)

# Definir mostrar_en_consola como un atributo del parser
parser.mostrar_en_consola = None
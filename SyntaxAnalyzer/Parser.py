import ply.yacc as yacc
from ply.yacc import errok
from LexicalAnalyzer.Lexer import tokens
from GlobalErrors.ErrorsManager import global_errors
from SyntaxAnalyzer.AST import Nodo,NodoIf,NodoAsignacion,NodoDeclaracion,NodoBinario,NodoIdentificador,NodoLiteral,NodoMientras,NodoMostrar,NodoRepetir,NodoPara,NodoUnario,NodoPrograma,NodoError
from SemanticAnalyzer.SemanticAnalyzer import SemanticAnalyzer


semantic_analyzer = SemanticAnalyzer()

# Definir precedencia para resolver conflictos
precedence = (
    ("left", "OR"),
    ("left", "AND"),
    ("right", "NOT"),
    ("left", "SUMA", "RESTA"),
    ("left", "MULTIPLICACION", "DIVISION", "MODULO"),
    ("nonassoc", "MAYOR_QUE", "MENOR_QUE", "MAYOR_IGUAL", "MENOR_IGUAL"),
    ("nonassoc", "IGUAL_IGUAL", "DIFERENTE"),
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

def p_sentencia_if_simple(p):
    "sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones FIN_SI"
    p[0] = NodoIf(condicion=p[3], cuerpo_if=p[6], cuerpo_else=[], linea=p.lineno(1))
    p[0].tiene_sino = False  # ← agregamos esta bandera

def p_sentencia_if_con_sino(p):
    "sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones SINO declaraciones FIN_SI"
    p[0] = NodoIf(condicion=p[3], cuerpo_if=p[6], cuerpo_else=p[8], linea=p.lineno(1))
    p[0].tiene_sino = True  # ← también aquí

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

def p_sentencia_repetir(p):
    """sentencia_repetir : REPETIR declaraciones HASTA_QUE PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    p[0] = NodoRepetir(
        cuerpo=p[2],          # Lista de nodos (declaraciones dentro del REPETIR)
        condicion=p[5],       # Nodo de la expresión (condición del HASTA_QUE)
        linea=p.lineno(1)     # Línea donde empieza la sentencia
    )

def p_sentencia_mostrar(p):
    """sentencia_mostrar : MOSTRAR lista_expresiones PUNTO_COMA"""
    if not p[2]:
        global_errors.append({
            "tipo": "semántico",
            "linea": p.lineno(1),
            "mensaje": "La sentencia 'mostrar' debe incluir al menos una expresión"
        })
        p[0] = NodoMostrar(expresiones=[], linea=p.lineno(1))
    else:
        p[0] = NodoMostrar(expresiones=p[2], linea=p.lineno(1))


def p_expresion_binaria(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion
                 | expresion MODULO expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | expresion MAYOR_QUE expresion
                 | expresion MENOR_QUE expresion
                 | expresion MAYOR_IGUAL expresion
                 | expresion MENOR_IGUAL expresion
                 | expresion IGUAL_IGUAL expresion
                 | expresion DIFERENTE expresion'''
    p[0] = NodoBinario(
        operador=p[2],
        izquierda=p[1],
        derecha=p[3],
        linea=p.lineno(2)
    )

def p_expresion_unaria(p):
    "expresion : NOT expresion"
    p[0] = NodoUnario(operador="NOT", expresion=p[2], linea=p.lineno(1))

def p_expresion_paren(p):
    "expresion : PARENTESIS_IZQ expresion PARENTESIS_DER"
    p[0] = p[2]

def p_expresion_literal(p):
    '''expresion : LITERAL_ENTERO
                 | LITERAL_DECIMAL
                 | LITERAL_CADENA
                 | LITERAL_BOOLEANO'''
    tipo, valor = p[1]
    p[0] = NodoLiteral(tipo=normalizar_tipo(tipo), valor=valor, linea=p.lineno(1))

def p_expresion_identificador(p):
    "expresion : IDENTIFICADOR"
    p[0] = NodoIdentificador(nombre=p[1], linea=p.lineno(1))


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

def p_declaracion_error(p):
    "declaracion : error PUNTO_COMA"
    linea = p.lineno(1)
    mensaje = "Error de sintaxis: se esperaba una sentencia válida"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": mensaje
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)





def p_error(p):
    if p:
        global_errors.append({
            "tipo": "sintáctico",
            "linea": p.lineno,
            "mensaje": f"❌ Error de sintaxis en línea {p.lineno}: se encontró token inesperado '{p.value}' (tipo: {p.type})"
        })
    else:
        global_errors.append({
            "tipo": "sintáctico",
            "linea": 0,
            "mensaje": "❌ Error de sintaxis: se alcanzó el fin de archivo sin cerrar correctamente una estructura"
        })






# Reglas de produccion con manejo de errores para cada sentencia
# Esto debe añadirse junto con tus reglas normales, no reemplazarlas

# ================================
# SENTENCIA IF (con errores)
# ================================
def p_error_if_sin_condicion(p):
    """sentencia_if : SI  ENTONCES declaraciones FIN_SI"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'si' no tiene una condición válida entre paréntesis"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok

def p_error_if_sin_entonces(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER declaraciones FIN_SI"""
    linea = p.lineno(1)
    mensaje = "❌ Falta la palabra clave 'ENTONCES' después de la condición en la sentencia 'si'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": mensaje
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok 

def p_error_if_sin_declaraciones(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES FIN_SI"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'si' no tiene cuerpo de declaraciones después de ENTONCES"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok

def p_error_if_sin_fin(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'si' no tiene 'FIN_SI'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok

# ================================
# SENTENCIA MIENTRAS (con errores)
# ================================
def p_error_mientras_sin_condicion(p):
    """sentencia_mientras : MIENTRAS  HACER declaraciones FIN_MIENTRAS"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'mientras' no tiene una condición válida"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok

def p_error_mientras_sin_hacer(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER declaraciones FIN_MIENTRAS"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'mientras' no tiene 'HACER'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok
    
def p_error_mientras_sin_declaraciones(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER HACER  FIN_MIENTRAS"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'mientras' no tiene cuerpo de declaraciones después de HACER"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

def p_error_mientras_si_fin_mientras(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER HACER declaraciones"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'mientras' no tiene 'FIN_MIENTRAS'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
# ================================
# SENTENCIA PARA (con errores)
# ================================
def p_error_para_sin_limites(p):
    """sentencia_para : PARA IDENTIFICADOR HACER declaraciones FIN_PARA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'para' tiene una sintaxis inválida en los límites (DESDE/HASTA)"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
def p_error_para_sin_hacer(p):
    """sentencia_para : PARA IDENTIFICADOR DESDE expresion HASTA expresion declaraciones FIN_PARA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'para' no tiene 'HACER'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
def p_error_para_sin_declaraciones(p):
    """sentencia_para : PARA IDENTIFICADOR DESDE expresion HASTA expresion HACER FIN_PARA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'para' no tiene cuerpo de declaraciones después de 'HACER'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
def p_error_para_sin_fin_para(p):
    """sentencia_para : PARA IDENTIFICADOR DESDE expresion HASTA expresion HACER declaraciones"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'para' no tiene 'FIN_PARA'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

# ================================
# SENTENCIA REPETIR (con errores)
# ================================
def p_error_repetir_sin_condicion(p):
    """sentencia_repetir : REPETIR declaraciones HASTA_QUE  PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'repetir' no tiene una condición válida en 'HASTA_QUE'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
def p_error_repetir_sin_hasta_que(p):
    """sentencia_repetir : REPETIR declaraciones  PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'repetir' no tiene 'HASTA_QUE'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

def p_error_repetir_sin_declaraciones(p):
    """sentencia_repetir : REPETIR  HASTA_QUE PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'repetir' no tiene cuerpo de declaraciones después de 'REPETIR'"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

# ================================
# SENTENCIA MOSTRAR (con errores)
# ================================
def p_error_mostrar_sin_expresion(p):
    """sentencia_mostrar : MOSTRAR  PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "La sentencia 'mostrar' no tiene expresiones válidas para mostrar"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

# ================================
# DECLARACIONES (con errores)
# ================================
def p_error_declaracion_incompleta(p):
    """declaracion : TIPO  PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "Declaración incompleta: falta el identificador o asignación"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()

# ================================
# ASIGNACIONES (con errores)
# ================================
def p_error_asignacion_invalida(p):
    """asignacion : IDENTIFICADOR ASIGNACION PUNTO_COMA"""
    linea = p.lineno(1)
    mensaje = "Asignación inválida: la expresión no es válida"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": linea,
        "mensaje": f"❌ {mensaje}"
    })
    p[0] = NodoError(mensaje=mensaje, linea=linea)
    errok()
    
def p_expresion_error(p):
    "expresion : error"
    global_errors.append({
        "tipo": "sintáctico",
        "linea": p.lineno(1),
        "mensaje": "Error en la expresión: sintaxis inválida"
    })
    p[0] = NodoLiteral(tipo="entero", valor=0, linea=p.lineno(1))  # Valor de recuperación





# Construcción del Parser
parser = yacc.yacc(start="programa", debug=False, write_tables=True)

def parse(self, code, **kwargs):
    self.code = code  # Almacenar el contenido del área de texto
    return super().parse(code, **kwargs)

# Definir mostrar_en_consola como un atributo del parser
parser.mostrar_en_consola = None
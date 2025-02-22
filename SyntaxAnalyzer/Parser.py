import ply.yacc as yacc
from LexicalAnalyzer.Lexer import tokens

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

variables = {}  
constantes = {} 

def p_programa(p):
    """programa : INICIO declaraciones FIN"""
    print(
        "📌 Entrando en `p_programa()`, procesando declaraciones entre `inicio` y `fin`..."
    )
    print(f"📄 Tokens recibidos: INICIO={p[1]}, FIN={p[3]}")  
    p[0] = p[2] if p[2] else []  


def p_declaraciones(p):
    """declaraciones : declaraciones declaracion_simple
    | declaraciones declaracion_con_asignacion
    | declaraciones constante
    | declaraciones asignacion
    | declaraciones sentencia_if
    | declaraciones sentencia_mientras
    | declaraciones sentencia_para
    | declaraciones sentencia_repetir
    | declaraciones sentencia_mostrar
    | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]  
    else:
        p[0] = [p[1]] if p[1] else []


def p_empty(p):
    "empty :"
    pass


# Reglas para estructuras de control
# Sentencia IF
def p_sentencia_if(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones FIN_SI
    | SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones SINO declaraciones FIN_SI"""
    tipo_condicion, valor_condicion = p[3]
    if tipo_condicion != "BOOLEANO":
        print(
            f"⚠️ Error: La condición del 'si' debe ser booleana, pero se encontró {tipo_condicion}"
        )
        return
    if len(p) == 6:  # IF sin ELSE
        print(f"📌 Sentencia IF detectada: condición={valor_condicion}")
    else:  # IF con ELSE
        print(f"📌 Sentencia IF-ELSE detectada: condición={valor_condicion}")


# Estructura de control WHILE
def p_sentencia_mientras(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER HACER declaraciones FIN_MIENTRAS"""
    tipo_condicion, valor_condicion = p[3]  # Asegúrate de que p[3] sea la expresión de la condición
    if tipo_condicion != "BOOLEANO":
        print(
            f"⚠️ Error: La condición del 'mientras' debe ser booleana, pero se encontró {tipo_condicion}"
        )
        return
    print(f"📌 Sentencia MIENTRAS detectada: condición={valor_condicion}")


# Estructura de control FOR
def p_sentencia_para(p):
    """sentencia_para : PARA TIPO IDENTIFICADOR DESDE expresion HASTA expresion HACER declaraciones FIN_PARA
                     | PARA TIPO IDENTIFICADOR DESDE expresion HASTA expresion CON_PASO expresion HACER declaraciones FIN_PARA"""
    tipo_variable = p[2]  # Tipo de la variable de iteración (entero)
    nombre_variable = p[3]  # Nombre de la variable de iteración (i)
    desde_tipo, desde_valor = p[5]  # Expresión DESDE
    hasta_tipo, hasta_valor = p[7]  # Expresión HASTA

    # Verificar que el tipo de la variable de iteración sea ENTERO
    if tipo_variable != "entero":
        print(f"⚠️ Error: La variable de iteración '{nombre_variable}' debe ser de tipo ENTERO")
        return

    # Declarar la variable de iteración como ENTERO
    variables[nombre_variable] = ("ENTERO", desde_valor)

    # Verificar que las expresiones DESDE y HASTA sean ENTERO
    if desde_tipo != "ENTERO" or hasta_tipo != "ENTERO":
        print(f"⚠️ Error: Las expresiones DESDE y HASTA deben ser de tipo ENTERO")
        return

    # Manejar el caso con paso
    if len(p) == 13:  # PARA con paso
        paso_tipo, paso_valor = p[9]  # Expresión CON_PASO
        if paso_tipo != "ENTERO":
            print(f"⚠️ Error: El paso debe ser de tipo ENTERO")
            return
        print(
            f"📌 Sentencia PARA detectada: variable={nombre_variable}, desde={desde_valor}, hasta={hasta_valor}, paso={paso_valor}"
        )
    else:  # PARA sin paso
        print(
            f"📌 Sentencia PARA detectada: variable={nombre_variable}, desde={desde_valor}, hasta={hasta_valor}"
        )


# Estructura de control DO-WHILE
def p_sentencia_repetir(p):
    """sentencia_repetir : REPETIR declaraciones HASTA_QUE PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    tipo_condicion, valor_condicion = p[5]  # La condición está en p[5]
    if tipo_condicion != "BOOLEANO":
        print(
            f"⚠️ Error: La condición del 'repetir' debe ser booleana, pero se encontró {tipo_condicion}"
        )
        return
    print(f"📌 Sentencia REPETIR detectada: condición={valor_condicion}")
    
# ------------------------ Regla para MOSTRAR ------------------------

def p_sentencia_mostrar(p):
    '''sentencia_mostrar : MOSTRAR lista_expresiones PUNTO_COMA'''
    mensaje = " ".join(str(exp[1]) for exp in p[2])  # Concatenar todas las expresiones
    print(f"📢 Mostrando: {mensaje}")
    if parser.mostrar_en_consola:  # 🔥 Verificar si la función está definida
        parser.mostrar_en_consola(f"📢 Mostrando: {mensaje}")
    
# ------------------------ Reglas para Expresiones ------------------------


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
    | expresion DIFERENTE expresion"""

    if len(p) == 2:  # Caso base (literales o identificadores)
        if isinstance(p[1], tuple):  # Extraer tipo y valor
            tipo_valor, valor = p[1]
            p[0] = (tipo_valor, valor)
        elif isinstance(p[1], str) and p[1] in variables:
            p[0] = variables[p[1]]  # Obtener tipo y valor de la variable
        elif isinstance(p[1], str) and p[1] in constantes:
            p[0] = (constantes[p[1]][0], p[1])  # Obtener tipo de constante
        else:
            print(f"⚠️ Error: Variable '{p[1]}' no definida")
            p[0] = ("ERROR", p[1])
        
    else:  # Expresiones aritméticas, lógicas o de comparación
        if p[2] == '+':
            p[0] = ("ENTERO", p[1][1] + p[3][1])
        elif p[2] == '-':
            p[0] = ("ENTERO", p[1][1] - p[3][1])
        elif p[2] == '*':
            p[0] = ("ENTERO", p[1][1] * p[3][1])
        elif p[2] == '/':
            p[0] = ("DECIMAL", p[1][1] / p[3][1])
        elif p[2] == 'AND':
            p[0] = ("BOOLEANO", p[1][1] and p[3][1])
        elif p[2] == 'OR':
            p[0] = ("BOOLEANO", p[1][1] or p[3][1])
        elif p[1] == 'NOT':
            p[0] = ("BOOLEANO", not p[2][1])
        elif p[2] == '>':
            p[0] = ("BOOLEANO", p[1][1] > p[3][1])
        elif p[2] == '<':
            p[0] = ("BOOLEANO", p[1][1] < p[3][1])
        elif p[2] == '>=':
            p[0] = ("BOOLEANO", p[1][1] >= p[3][1])
        elif p[2] == '<=':
            p[0] = ("BOOLEANO", p[1][1] <= p[3][1])
        elif p[2] == '==':
            p[0] = ("BOOLEANO", p[1][1] == p[3][1])
        elif p[2] == '!=':
            p[0] = ("BOOLEANO", p[1][1] != p[3][1])
            
# ------------------------ Reglas para Declaración de Variables ------------------------

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMA expresion
                         | expresion'''
    if len(p) == 4:  # Si hay una lista de expresiones
        p[0] = p[1] + [p[3]]  # Agregar la nueva expresión a la lista
    else:  # Si es una sola expresión
        p[0] = [p[1]]  # Crear una lista con una sola expresión


# ------------------------ Reglas para Declaración de Variables ------------------------


def p_declaracion_simple(p):
    """declaracion_simple : TIPO IDENTIFICADOR PUNTO_COMA"""
    print(f"➡️ Entrando a `p_declaracion_simple()`, Tokens: {p[:]}")
    tipo_variable = p[1]
    nombre_variable = p[2]
    variables[nombre_variable] = (tipo_variable, None)
    print(
        f"✔️ Declaración válida: {nombre_variable} es de tipo {tipo_variable} (sin valor asignado)"
    )


def p_declaracion_con_asignacion(p):
    """declaracion_con_asignacion : TIPO IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""
    print(f"➡️ Entrando a `p_declaracion_con_asignacion()`, Tokens: {p[:]}")
    tipo_variable = p[1]
    nombre_variable = p[2]
    tipo_valor, valor = p[4]
    print(
        f"📌 Variable detectada: {nombre_variable} ({tipo_variable}) = {valor} ({tipo_valor})"
    )
    if not es_tipo_valido(tipo_variable, tipo_valor):
        print(
            f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})"
        )
        return
    variables[nombre_variable] = (tipo_variable, valor)
    print(
        f"✔️ Declaración válida: {nombre_variable} es de tipo {tipo_variable} con valor {valor}"
    )


# ------------------------ Reglas para Asignaciones ------------------------


def p_asignacion(p):
    """asignacion : IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""
    print(f"➡️ Entrando a `p_asignacion()`, Tokens: {p[:]}")
    nombre_variable = p[1]
    if nombre_variable not in variables:
        print(f"⚠️ Error: La variable '{nombre_variable}' no ha sido declarada")
        return
    tipo_variable = variables[nombre_variable][0]
    tipo_valor, valor = p[3]
    print(f"📌 Asignación detectada: {nombre_variable} = {valor} ({tipo_valor})")
    if not es_tipo_valido(tipo_variable, tipo_valor):
        print(
            f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})"
        )
        return
    variables[nombre_variable] = (tipo_variable, valor)
    print(f"✔️ Asignación válida: {nombre_variable} = {valor}")


# ------------------------ Reglas para Declaración de Constantes ------------------------


def p_constante(p):
    """constante : TIPO IDENTIFICADOR ASIGNACION expresion"""
    tipo_variable = p[1][1].upper()  # Asegúrate de que p[1] sea el tipo correcto
    nombre_variable = p[2]
    tipo_valor, valor = p[4]
    if nombre_variable in constantes:
        print(f"⚠️ Error: La constante '{nombre_variable}' ya fue declarada")
        return
    if not es_tipo_valido(tipo_variable, tipo_valor):
        print(
            f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a la constante '{nombre_variable}' (tipo {tipo_variable})"
        )
        return
    constantes[nombre_variable] = (tipo_variable, valor)
    print(f"✔️ Constante válida: {nombre_variable} = {valor} ({tipo_variable})")


# ------------------------ Función de Validación de Tipos ------------------------


def es_tipo_valido(tipo_variable, tipo_valor):
    """Verifica si el tipo del valor es compatible con el tipo de la variable."""
    tipo_variable = tipo_variable.upper()
    tipo_valor = tipo_valor.upper()
    if tipo_variable == "ENTERO":
        return tipo_valor == "ENTERO"
    elif tipo_variable == "DECIMAL":
        return tipo_valor in ["ENTERO", "DECIMAL"]
    elif tipo_variable == "CADENA":
        return tipo_valor == "CADENA"
    elif tipo_variable == "BOOLEANO":
        return tipo_valor == "BOOLEANO"
    return False


def p_error(p):
    if p:
        error_msg = f"❌ Error de sintaxis en línea {p.lineno}, token inesperado: {p.type} ('{p.value}')"
    else:
        error_msg = "❌ Error de sintaxis: Fin de archivo inesperado"
    print(error_msg)
    raise SyntaxError(error_msg)  # 🔥 Detener análisis en caso de error


# ------------------------ Construcción del Parser ------------------------

parser = yacc.yacc(start="programa")

# Definir mostrar_en_consola como un atributo del parser

parser.mostrar_en_consola = None

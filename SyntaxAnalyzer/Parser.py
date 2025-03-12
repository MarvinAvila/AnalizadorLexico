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

def normalizar_tipo(tipo):
    """Normaliza un tipo de dato a su formato estándar (minúsculas)."""
    return TIPOS_DE_DATOS.get(tipo.upper(), tipo.lower())

# Reglas para estructuras de control
def p_sentencia_if(p):
    """sentencia_if : SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones FIN_SI
    | SI PARENTESIS_IZQ expresion PARENTESIS_DER ENTONCES declaraciones SINO declaraciones FIN_SI"""
    tipo_condicion, valor_condicion = p[3]
    if normalizar_tipo(tipo_condicion) != "booleano":  # Usar tipo normalizado
        semantic_errors.append("La condición del 'si' debe ser booleana, pero se encontró {tipo_condicion}")
    if len(p) == 6:  # IF sin ELSE
        print(f"📌 Sentencia IF detectada: condición={valor_condicion}")
    else:  # IF con ELSE
        print(f"📌 Sentencia IF-ELSE detectada: condición={valor_condicion}")

def p_sentencia_mientras(p):
    """sentencia_mientras : MIENTRAS PARENTESIS_IZQ expresion PARENTESIS_DER HACER declaraciones FIN_MIENTRAS"""
    tipo_condicion, valor_condicion = p[3]  # Asegúrate de que p[3] sea la expresión de la condición
    if normalizar_tipo(tipo_condicion) != "booleano":
        semantic_errors.append("La condición del 'mientras' debe ser booleana, pero se encontró {tipo_condicion}")
    print(f"📌 Sentencia MIENTRAS detectada: condición={valor_condicion}")

def p_sentencia_para(p):
    """sentencia_para : PARA IDENTIFICADOR DESDE expresion HASTA expresion HACER declaraciones FIN_PARA
                     | PARA IDENTIFICADOR DESDE expresion HASTA expresion CON_PASO expresion HACER declaraciones FIN_PARA"""
    nombre_variable = p[2]  # Nombre de la variable de iteración (i)
    desde_tipo, desde_valor = p[4]  # Expresión DESDE
    hasta_tipo, hasta_valor = p[6]  # Expresión HASTA

    # Verificar que la variable de iteración ya esté declarada
    if nombre_variable not in variables:
        semantic_errors.append(f"La variable de iteración '{nombre_variable}' no ha sido declarada")

    # Verificar que las expresiones DESDE y HASTA sean ENTERO
    if desde_tipo != "entero" or hasta_tipo != "entero":
        semantic_errors.append(f"Las expresiones DESDE y HASTA deben ser de tipo ENTERO")

    # Manejar el caso con paso
    if len(p) == 11:  # PARA con paso
        paso_tipo, paso_valor = p[8]  # Expresión CON_PASO
        if paso_tipo != "entero":
            semantic_errors.append(f"El paso debe ser de tipo ENTERO")
        print(f"📌 Sentencia PARA detectada: variable={nombre_variable}, desde={desde_valor}, hasta={hasta_valor}, paso={paso_valor}")
    else:  # PARA sin paso
        print(f"📌 Sentencia PARA detectada: variable={nombre_variable}, desde={desde_valor}, hasta={hasta_valor}")

def p_sentencia_repetir(p):
    """sentencia_repetir : REPETIR declaraciones HASTA_QUE PARENTESIS_IZQ expresion PARENTESIS_DER PUNTO_COMA"""
    tipo_condicion, valor_condicion = p[5]  # La condición está en p[5]
    if normalizar_tipo(tipo_condicion) != "booleano":
        semantic_errors.append(f"La condición del 'repetir' debe ser booleana, pero se encontró {tipo_condicion}")
    print(f"📌 Sentencia REPETIR detectada: condición={valor_condicion}")

def p_sentencia_mostrar(p):
    '''sentencia_mostrar : MOSTRAR lista_expresiones PUNTO_COMA'''
    mensaje = " ".join(str(exp[1]) for exp in p[2])  # Concatenar todas las expresiones
    print(f"📢 Mostrando: {mensaje}")
    if parser.mostrar_en_consola:  # 🔥 Verificar si la función está definida
        parser.mostrar_en_consola(f"📢 Mostrando: {mensaje}")

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
    
    print(f"📌 Procesando expresión: {p[:]}")  # Mensaje de depuración

    if len(p) == 2:  # Literales o identificadores
        if isinstance(p[1], tuple):  # Extraer tipo y valor
            tipo_valor, valor = p[1]
            p[0] = (normalizar_tipo(tipo_valor), valor)
        elif isinstance(p[1], str) and p[1] in variables:
            tipo_variable, valor_variable = variables[p[1]]
            p[0] = (normalizar_tipo(tipo_variable), valor_variable)
        elif isinstance(p[1], str) and p[1] in constantes:
            tipo_constante, valor_constante = constantes[p[1]]
            p[0] = (normalizar_tipo(tipo_constante), valor_constante)
        else:
            semantic_errors.append(f"Variable '{p[1]}' no definida")
            p[0] = ("error", None)  # Evitar acceso a None

    elif len(p) == 4 and p[1] == '(' and p[3] == ')':  # Expresión entre paréntesis
        p[0] = p[2]

    else:  # Operaciones aritméticas, lógicas o de comparación
        if p[1] is None or p[3] is None:  # Evitar errores si p[1] o p[3] no están definidos
            semantic_errors.append(f"Error en la operación '{p[2]}': uno de los operandos no es válido")
            p[0] = ("error", None)
            return

        tipo1, val1 = p[1] if isinstance(p[1], tuple) else ("error", None)
        tipo2, val2 = p[3] if isinstance(p[3], tuple) else ("error", None)

        if tipo1 == "error" or tipo2 == "error":
            semantic_errors.append(f"Error en la operación '{p[2]}': operandos inválidos")
            p[0] = ("error", None)
            return

        try:
            if p[2] == '+':
                p[0] = ("entero", val1 + val2)
            elif p[2] == '-':
                p[0] = ("entero", val1 - val2)
            elif p[2] == '*':
                p[0] = ("entero", val1 * val2)
            elif p[2] == '/':
                p[0] = ("decimal", val1 / val2 if val2 != 0 else 0)  # Evitar división por cero
            elif p[2] == 'AND':
                p[0] = ("booleano", val1 and val2)
            elif p[2] == 'OR':
                p[0] = ("booleano", val1 or val2)
            elif p[1] == 'NOT':
                p[0] = ("booleano", not val1)
            elif p[2] == '>':
                p[0] = ("booleano", val1 > val2)
            elif p[2] == '<':
                p[0] = ("booleano", val1 < val2)
            elif p[2] == '>=':
                p[0] = ("booleano", val1 >= val2)
            elif p[2] == '<=':
                p[0] = ("booleano", val1 <= val2)
            elif p[2] == '==':
                p[0] = ("booleano", val1 == val2)
            elif p[2] == '!=':
                p[0] = ("booleano", val1 != val2)
        except Exception as e:
            semantic_errors.append(f"Error en la operación '{p[2]}': {str(e)}")
            p[0] = ("error", None)

def p_lista_expresiones(p):
    '''lista_expresiones : lista_expresiones COMA expresion
                         | expresion'''
    if len(p) == 4:  # Si hay una lista de expresiones
        p[0] = p[1] + [p[3]]  # Agregar la nueva expresión a la lista
    else:  # Si es una sola expresión
        p[0] = [p[1]]  # Crear una lista con una sola expresión

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
    tipo_valor, valor = p[4]  # La expresión ya fue procesada por la regla `expresion`
    
    print(f"📌 Variable detectada: {nombre_variable} ({tipo_variable}) = {valor} ({tipo_valor})")

    if not es_tipo_valido(tipo_variable, tipo_valor):
        error_msg = f"No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})"
        semantic_errors.append(error_msg)  # Agregar error a la lista en vez de lanzar excepción
        print(f"❌ Error semántico: {error_msg}")
    else:
        variables[nombre_variable] = (tipo_variable, valor)
        print(f"✔️ Declaración válida: {nombre_variable} = {valor}")

def p_asignacion(p):
    """asignacion : IDENTIFICADOR ASIGNACION expresion PUNTO_COMA"""
    print(f"➡️ Entrando a `p_asignacion()`, Tokens: {p[:]}")
    nombre_variable = p[1]
    if nombre_variable not in variables:
        semantic_errors.append(f"La variable '{nombre_variable}' no ha sido declarada")
    tipo_variable = variables[nombre_variable][0]
    tipo_valor, valor = p[3]
    print(f"📌 Asignación detectada: {nombre_variable} = {valor} ({tipo_valor})")
    if not es_tipo_valido(tipo_variable, tipo_valor):
        semantic_errors.append(f"No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})")
    variables[nombre_variable] = (tipo_variable, valor)
    print(f"✔️ Asignación válida: {nombre_variable} = {valor}")

def p_constante(p):
    """constante : TIPO IDENTIFICADOR ASIGNACION expresion"""
    tipo_variable = p[1].lower()  # Convertir a minúsculas
    nombre_variable = p[2]
    tipo_valor, valor = p[4]
    if nombre_variable in constantes:
        semantic_errors.append(f"La constante '{nombre_variable}' ya fue declarada")
    if not es_tipo_valido(tipo_variable, tipo_valor):
        semantic_errors.append(f"No se puede asignar '{valor}' (tipo {tipo_valor}) a la constante '{nombre_variable}' (tipo {tipo_variable})")
    constantes[nombre_variable] = (tipo_variable, valor)
    print(f"✔️ Constante válida: {nombre_variable} = {valor} ({tipo_variable})")

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
        semantic_errors.append(f"Tipo de variable '{tipo_variable}' no permitido.")
    
    return tipo_valor in tipos_permitidos[tipo_variable]

syntax_errors = []  # Lista para errores sintácticos
semantic_errors = []  # Lista para errores semánticos

def p_error(p):
    """Manejo de errores de sintaxis sin interrumpir el análisis."""
    if p:
        error_msg = f"❌ Error de sintaxis en línea {p.lineno}: Token inesperado '{p.value}'"
        syntax_errors.append(error_msg)  # Agregar error a la lista
        print(error_msg)
    else:
        error_msg = "❌ Error de sintaxis: Fin de archivo inesperado"
        syntax_errors.append(error_msg)



# Construcción del Parser
parser = yacc.yacc(start="programa")

def parse(self, code, **kwargs):
    self.code = code  # Almacenar el contenido del área de texto
    return super().parse(code, **kwargs)

# Definir mostrar_en_consola como un atributo del parser
parser.mostrar_en_consola = None
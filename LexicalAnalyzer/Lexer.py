import ply.lex as lex

# ------------------------ Definición de Tokens ------------------------

reserved = {
    "inicio": "INICIO",
    "fin": "FIN",
    "si": "SI",
    "entonces": "ENTONCES",
    "sino": "SINO",
    "fin_si": "FIN_SI",
    "mientras": "MIENTRAS",
    "fin_mientras": "FIN_MIENTRAS",
    "para": "PARA",
    "desde": "DESDE",
    "hasta": "HASTA",
    "con_paso": "CON_PASO",
    "fin_para": "FIN_PARA",
    "repetir": "REPETIR",
    "hasta_que": "HASTA_QUE",
    "mostrar": "MOSTRAR",
    "hacer": "HACER",
    
}

tokens = [
    "LITERAL_ENTERO",
    "LITERAL_DECIMAL",
    "LITERAL_CADENA",
    "LITERAL_BOOLEANO",
    "IDENTIFICADOR",
    "TIPO",
    "ASIGNACION",
    "PUNTO_COMA",
    "PARENTESIS_IZQ",  
    "PARENTESIS_DER",
    "SUMA",
    "RESTA",
    "MULTIPLICACION",
    "DIVISION",
    "AND",
    "OR",
    "NOT",
    "COMA",
] + list(reserved.values())


# 🔹 Tipos de Datos (entero, decimal, cadena, booleano)
def t_TIPO(t):
    r"\b(entero|decimal|cadena|booleano)\b"
    print(f"📌 Token detectado: {t.type} -> {t.value}")
    return t


# 🔹 Valores booleanos (verdadero, falso)
def t_LITERAL_BOOLEANO(t):
    r"\b(verdadero|falso)\b"
    t.value = ("BOOLEANO", t.value == "verdadero")  # 🔥 Convertir a `True/False`
    print(f"📌 Token detectado: {t.type} -> {t.value}")
    return t


def t_IDENTIFICADOR(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    t.type = reserved.get(t.value, "IDENTIFICADOR")  # Verifica si es palabra reservada
    print(f"📌 Token detectado: {t.type} -> {t.value}")
    return t


# 🔹 Definir `;` como token válido
t_PUNTO_COMA = r";"


# 🔹 Números decimales
def t_LITERAL_DECIMAL(t):
    r"\d+\.\d+"
    t.value = ("DECIMAL", float(t.value))
    print(f"📌 Token detectado: LITERAL_DECIMAL -> {t.value}")
    return t


# 🔹 Números enteros
def t_LITERAL_ENTERO(t):
    r"\d+"
    t.value = ("ENTERO", int(t.value))
    print(f"📌 Token detectado: LITERAL_ENTERO -> {t.value}")
    return t


# 🔹 Cadenas de texto entre comillas
def t_LITERAL_CADENA(t):
    r'"[^"]*"'  # 🔥 Coincide con cualquier texto entre comillas dobles
    t.value = ("CADENA", t.value.strip('"'))  # 🔥 Remueve las comillas al almacenar
    print(f"📌 Token detectado: LITERAL_CADENA -> {t.value}")
    return t


# 🔹 Asignación "="
t_ASIGNACION = r"="

# Definir los tokens para los paréntesis
t_PARENTESIS_IZQ = r'\('
t_PARENTESIS_DER = r'\)'

#   Coma
t_COMA = r','

# Definir los tokens para operadores aritméticos y lógicos
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_AND = r'AND'
t_OR = r'OR'
t_NOT = r'NOT'

# 🔹 Ignorar espacios en blanco
t_ignore = " \t\n"

# 🔹 Ignorar comentarios
def t_ignore_COMENTARIO(t):
    r'//.*'
    pass  # Ignora los comentarios

# ------------------------ Manejo de Errores ------------------------


def t_error(t):
    print(f"❌ Error léxico: Carácter inesperado '{t.value[0]}'")
    t.lexer.skip(1)

# ------------------------ Construcción del Lexer ------------------------

lexer = lex.lex()

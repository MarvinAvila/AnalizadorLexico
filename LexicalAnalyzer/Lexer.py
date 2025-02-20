import ply.lex as lex

# ------------------------ Definición de Tokens ------------------------

tokens = [
    'LITERAL_ENTERO',
    'LITERAL_DECIMAL',
    'LITERAL_CADENA',
    'LITERAL_BOOLEANO',
    'IDENTIFICADOR',
    'TIPO',
    'ASIGNACION',
    'PUNTO_COMA'
]

# 🔹 Definir `;` como token válido
t_PUNTO_COMA = r';'

# 🔹 Tipos de Datos (entero, decimal, cadena, booleano)
def t_TIPO(t):
    r'\b(entero|decimal|cadena|booleano)\b'
    return t


# 🔹 Números decimales
def t_LITERAL_DECIMAL(t):
    r'\d+\.\d+'
    t.value = ("DECIMAL", float(t.value))
    return t

# 🔹 Números enteros
def t_LITERAL_ENTERO(t):
    r'\d+'
    t.value = ("ENTERO", int(t.value))
    return t

# 🔹 Cadenas de texto entre comillas
def t_LITERAL_CADENA(t):
    r'"[^"]*"'  # 🔥 Coincide con cualquier texto entre comillas dobles
    t.value = ("CADENA", t.value)
    return t

# 🔹 Booleanos (verdadero, falso)
def t_LITERAL_BOOLEANO(t):
    r'\b(verdadero|falso)\b'  # 🔥 Coincide con "verdadero" o "falso"
    t.value = ("BOOLEANO", t.value)
    return t

# 🔹 Identificadores (nombres de variables)
def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

# 🔹 Asignación "="
t_ASIGNACION = r'='

# 🔹 Ignorar espacios en blanco
t_ignore = ' \t\n'

# ------------------------ Manejo de Errores ------------------------

def t_error(t):
    print(f"❌ Error léxico: Carácter inesperado '{t.value[0]}'")
    t.lexer.skip(1)

lexer = lex.lex()

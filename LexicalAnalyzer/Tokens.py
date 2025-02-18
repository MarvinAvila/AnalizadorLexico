TOKENS = [
    # Palabras clave
    ("ENTERO", r"\bentero\b"),
    ("DECIMAL", r"\bdecimal\b"),
    ("CADENA", r"\bcadena\b"),
    ("BOOLEANO", r"\bbooleano\b"),
    ("SI", r"\bsi\b"),
    ("SINO", r"\bsino\b"),
    ("MIENTRAS", r"\bmientras\b"),
    ("PARA", r"\bpara\b"),
    ("REPETIR", r"\brepetir\b"),  # Para DO-WHILE
    ("HASTA", r"\bhasta\b"),  # Para DO-WHILE
    ("DEFINIR", r"\bdefinir\b"),
    ("DEVOLVER", r"\bdevolver\b"),
    ("MOSTRAR", r"\bmostrar\b"),
    ("ENTRADA", r"\bentrada\b"),
    ("FIN", r"\bfin\b"),
    ("HACER", r"\bhacer\b"),
    ("ENTONCES", r"\bentonces\b"),
    ("DESDE", r"\bdesde\b"),

    # Operadores lógicos
    ("Y", r"\by\b"),
    ("O", r"\bo\b"),
    ("NO", r"\bno\b"),

    # Operadores relacionales
    ("IGUAL", r"=="),
    ("DIFERENTE", r"!="),
    ("MAYOR_IGUAL", r">="),
    ("MENOR_IGUAL", r"<="),
    ("MAYOR", r">"),
    ("MENOR", r"<"),

    # Operadores aritméticos
    ("SUMA", r"\+"),
    ("RESTA", r"-"),
    ("MULTIPLICACION", r"\*"),
    ("DIVISION", r"/"),
    ("MODULO", r"%"),

    # Asignación
    ("ASIGNACION", r"="),

    # Delimitadores
    ("PARENTESIS_IZQ", r"\("),
    ("PARENTESIS_DER", r"\)"),
    ("LLAVE_IZQ", r"\{"),
    ("LLAVE_DER", r"\}"),
    ("COMA", r","),
    ("PUNTO", r"\."),
    ("DOS_PUNTOS", r":"),
    ("PUNTO_COMA", r";"),
    ("CORCHETE_IZQ", r"\["),
    ("CORCHETE_DER", r"\]"),

    # Literales
    ("LITERAL_NUMERICA", r"\d+(\.\d+)?"),  # Enteros y decimales
    ("LITERAL_CADENA", r"\"[^\"]*\""),  # Cadenas entre comillas dobles
    ("LITERAL_BOOLEANO", r"\bverdadero\b|\bfalso\b"),  # Booleanos

    # Identificadores (nombres de variables)
    ("IDENTIFICADOR", r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # Espacios en blanco (ignorados)
    ("ESPACIO", r"\s+"),
]
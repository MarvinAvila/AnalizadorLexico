import re

# Definición de tokens y expresiones regulares
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
    ("REPETIR", r"\brepetir\b"),  # Agregado para DO-WHILE
    ("HASTA", r"\bhasta\b"),  # Agregado para DO-WHILE
    ("DEFINIR", r"\bdefinir\b"),
    ("DEVOLVER", r"\bdevolver\b"),
    ("MOSTRAR", r"\bmostrar\b"),
    ("ENTRADA", r"\bentrada\b"),
    ("FIN", r"\bfin\b"),
    ("HACER", r"\bhacer\b"),
    ("ENTONCES", r"\bentonces\b"),
    ("DESDE",r"\bdesde\b"),

    # Operadores lógicos
    ("Y", r"\by\b"),
    ("O", r"\bo\b"),
    ("NO", r"\bno\b"),

    # Operadores relacionales
    ("IGUAL", r"=="),
    ("DIFERENTE", r"!="),
    ("MAYOR", r">"),
    ("MENOR", r"<"),
    ("MAYOR_IGUAL", r">="),
    ("MENOR_IGUAL", r"<="),

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
    ("LITERAL_NUMERICA", r"\d+(\.\d+)?"),  # Números enteros o decimales
    ("LITERAL_CADENA", r"\".*\""),  # Cadenas entre comillas dobles
    ("LITERAL_BOOLEANO", r"\bverdadero\b|\bfalso\b"),  # Booleanos

    # Identificadores (nombres de variables)
    ("IDENTIFICADOR", r"[a-zA-Z_][a-zA-Z0-9_]*"),

    # Espacios en blanco (ignorados)
    ("ESPACIO", r"\s+"),
]

# Función para analizar el código fuente
def analizador_lexico(codigo_fuente):
    tokens = []
    posicion = 0

    while posicion < len(codigo_fuente):
        # Ignorar espacios en blanco
        if re.match(r"\s", codigo_fuente[posicion]):
            posicion += 1
            continue

        # Buscar coincidencias con los tokens
        encontrado = False
        for token_nombre, token_regex in TOKENS:
            regex = re.compile(token_regex)
            coincidencia = regex.match(codigo_fuente, posicion)
            if coincidencia:
                valor = coincidencia.group(0)
                if token_nombre != "ESPACIO":  # Ignorar espacios
                    tokens.append((token_nombre, valor))
                posicion = coincidencia.end()
                encontrado = True
                break

        # Si no se encuentra un token válido, es un error léxico
        if not encontrado:
            raise SyntaxError(f"Error léxico: Carácter no reconocido '{codigo_fuente[posicion]}' en la posición {posicion}")

    return tokens

# Función principal para ingresar el pseudocódigo
def main():
    print("Analizador Léxico - Ingresa tu pseudocódigo (escribe 'fin' en una línea nueva para terminar):")
    codigo_fuente = ""
    while True:
        linea = input()
        if linea.strip() == "fin":
            break
        codigo_fuente += linea + "\n"

    try:
        tokens = analizador_lexico(codigo_fuente)
        print("\nTokens encontrados:")
        for token in tokens:
            print(token)
    except SyntaxError as e:
        print(e)

# Ejecutar el programa
if __name__ == "__main__":
    main()
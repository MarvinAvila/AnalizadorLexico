import ply.yacc as yacc
from LexicalAnalyzer.Lexer import tokens

variables = {}  # 🔥 Diccionario de variables con su tipo
constantes = {}  # 🔥 Diccionario de constantes con su valor fijo

# ------------------------ Reglas para Expresiones ------------------------

def p_expresion(p):
    '''expresion : LITERAL_ENTERO
                 | LITERAL_DECIMAL
                 | LITERAL_CADENA
                 | LITERAL_BOOLEANO
                 | IDENTIFICADOR'''

    if isinstance(p[1], tuple):  # 🔥 Extraer tipo y valor
        tipo_valor, valor = p[1]
        p[0] = (tipo_valor, valor)
    elif isinstance(p[1], str) and p[1] in variables:
        p[0] = (variables[p[1]], p[1])  # 🔥 Obtener tipo de variable
    elif isinstance(p[1], str) and p[1] in constantes:
        p[0] = (constantes[p[1]][0], p[1])  # 🔥 Obtener tipo de constante
    else:
        print(f"⚠️ Error: Variable '{p[1]}' no definida")
        p[0] = ("ERROR", p[1])  

# ------------------------ Reglas para Declaración de Variables ------------------------

def p_declaracion(p):
    '''declaracion : TIPO IDENTIFICADOR PUNTO_COMA
                   | TIPO IDENTIFICADOR ASIGNACION expresion PUNTO_COMA'''
    
    tipo_variable = p[1].upper()  # 🔥 Convertir a mayúsculas
    nombre_variable = p[2]

    if len(p) == 6:  # Declaración con asignación
        tipo_valor, valor = p[4]

        if not es_tipo_valido(tipo_variable, tipo_valor):  
            print(f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})")
            return  

        variables[nombre_variable] = tipo_variable
        print(f"✔️ Declaración válida: {nombre_variable} es de tipo {tipo_variable} con valor {valor}")
    else:
        variables[nombre_variable] = tipo_variable  # Guardar sin valor
        print(f"✔️ Declaración válida: {nombre_variable} es de tipo {tipo_variable} (sin valor asignado)")

# ------------------------ Reglas para Declaración de Constantes ------------------------

def p_constante(p):
    '''constante : TIPO IDENTIFICADOR ASIGNACION expresion'''

    tipo_variable = p[1][1].upper()
    nombre_variable = p[2]
    tipo_valor, valor = p[4]

    if nombre_variable in constantes:
        print(f"⚠️ Error: La constante '{nombre_variable}' ya fue declarada")
        return

    if not es_tipo_valido(tipo_variable, tipo_valor):  
        print(f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a la constante '{nombre_variable}' (tipo {tipo_variable})")
        return  

    constantes[nombre_variable] = (tipo_variable, valor)  # Guardar como constante
    print(f"✔️ Constante válida: {nombre_variable} = {valor} ({tipo_variable})")

# ------------------------ Reglas para Asignaciones ------------------------

def p_asignacion(p):
    '''asignacion : IDENTIFICADOR ASIGNACION expresion'''

    nombre_variable = p[1]

    if nombre_variable in constantes:
        print(f"⚠️ Error: No se puede reasignar la constante '{nombre_variable}'")
        return

    if nombre_variable not in variables:
        print(f"⚠️ Error: La variable '{nombre_variable}' no ha sido declarada")
        return

    tipo_variable = variables[nombre_variable]
    tipo_valor, valor = p[3]

    if not es_tipo_valido(tipo_variable, tipo_valor):  
        print(f"⚠️ Error: No se puede asignar '{valor}' (tipo {tipo_valor}) a '{nombre_variable}' (tipo {tipo_variable})")
        return

    print(f"✔️ Asignación válida: {nombre_variable} = {valor}")

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
        print(f"❌ Error de sintaxis en línea {p.lineno}, token inesperado: {p.type} ('{p.value}')")
    else:
        print("❌ Error de sintaxis: Fin de archivo inesperado")
        
def p_programa(p):
    '''programa : declaraciones'''
    pass

def p_declaraciones(p):
    '''declaraciones : declaraciones declaracion
                     | declaraciones constante
                     | declaraciones asignacion
                     | declaracion
                     | constante
                     | asignacion
                     | declaraciones PUNTO_COMA'''
    pass

# ------------------------ Construcción del Parser ------------------------

parser = yacc.yacc()

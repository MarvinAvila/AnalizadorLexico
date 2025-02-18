class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.errors = []

    def parse(self):
        while self.position < len(self.tokens):
            token_type, value = self.tokens[self.position]

            if token_type == "SI":
                self.parse_if()
            elif token_type == "PARA":
                self.parse_for()
            elif token_type == "MIENTRAS":
                self.parse_while()
            elif token_type == "REPETIR":
                self.parse_repeat()
            elif token_type == "DEFINIR":
                self.parse_define()
            elif token_type == "DEVOLVER":
                self.parse_return()
            elif token_type == "ENTRADA":
                self.parse_input()
            elif token_type == "MOSTRAR":
                self.parse_print()
            elif token_type in ["ENTERO", "DECIMAL", "CADENA", "BOOLEANO"]:
                self.parse_variable_declaration()
            elif token_type == "IDENTIFICADOR":
                self.parse_assignment()
            else:
                self.errors.append(
                    f"Error de sintaxis: Token inesperado '{value}' en posición {self.position}"
                )

            self.position += 1  # Mover al siguiente token

        return self.errors


def parse_if(self):
    estados = ["q0", "q1", "q2", "q3", "q4", "q5", "q6"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "SI":
            estado_actual = "q1"

        elif estado_actual == "q1" and token_type in [
            "IDENTIFICADOR",
            "LITERAL_NUMERICA",
        ]:
            estado_actual = "q2"

        elif estado_actual == "q2" and token_type in [
            "IGUAL",
            "DIFERENTE",
            "MAYOR",
            "MENOR",
            "MAYOR_IGUAL",
            "MENOR_IGUAL",
        ]:
            estado_actual = "q3"

        elif estado_actual == "q3" and token_type in [
            "IDENTIFICADOR",
            "LITERAL_NUMERICA",
        ]:
            estado_actual = "q4"

        elif estado_actual == "q4" and token_type == "ENTONCES":
            estado_actual = "q5"

        elif estado_actual == "q5":
            if token_type == "FIN":
                estado_actual = "q6"
                break  # Fin del bloque

        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'si' en posición {self.position}"
            )
            break

        self.position += 1  # Avanzar al siguiente token

    if estado_actual != "q6":
        self.errors.append("Error: Estructura 'si' incompleta, falta 'fin'")


def parse_for(self):
    estados = ["q0", "q1", "q2", "q3", "q4", "q5", "q6", "q7", "q8"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "PARA":
            estado_actual = "q1"

        elif estado_actual == "q1" and token_type == "IDENTIFICADOR":
            estado_actual = "q2"

        elif estado_actual == "q2" and token_type == "DESDE":
            estado_actual = "q3"

        elif estado_actual == "q3" and token_type == "LITERAL_NUMERICA":
            estado_actual = "q4"

        elif estado_actual == "q4" and token_type == "HASTA":
            estado_actual = "q5"

        elif estado_actual == "q5" and token_type == "LITERAL_NUMERICA":
            estado_actual = "q6"

        elif estado_actual == "q6" and token_type == "HACER":
            estado_actual = "q7"

        elif estado_actual == "q7":  # Código dentro del bucle
            if token_type == "FIN":
                estado_actual = "q0"
                break  # Fin del bloque

        else:
            self.errors.append(
                f"Error de sintaxis en 'para' en posición {self.position}"
            )
            break

        self.position += 1  # Avanzar al siguiente token

    if estado_actual != "q0":
        self.errors.append("Error: 'para' sin 'fin' o estructura incorrecta.")


def parse_while(self):
    estados = ["q0", "q1", "q2", "q3"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "MIENTRAS":
            estado_actual = "q1"

        elif estado_actual == "q1" and token_type in [
            "IDENTIFICADOR",
            "LITERAL_NUMERICA",
        ]:
            estado_actual = "q2"

        elif estado_actual == "q2" and token_type == "HACER":
            estado_actual = "q3"
            break

        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'mientras' en posición {self.position}"
            )
            break

        self.position += 1  # Avanzar al siguiente token

    if estado_actual != "q3":
        self.errors.append("Error: Estructura 'mientras' incompleta, falta 'hacer'")


def parse_repeat(self):
    estados = ["q0", "q1", "q2"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "REPETIR":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "HASTA":
            estado_actual = "q2"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'repetir-hasta' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q2":
        self.errors.append(
            "Error: Estructura 'repetir-hasta' incompleta, falta 'hasta'"
        )


def parse_define(self):
    estados = ["q0", "q1", "q2", "q3"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "DEFINIR":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "IDENTIFICADOR":
            estado_actual = "q2"
        elif estado_actual == "q2" and token_type in [
            "ENTERO",
            "DECIMAL",
            "CADENA",
            "BOOLEANO",
        ]:
            estado_actual = "q3"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'definir' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q3":
        self.errors.append("Error: Estructura 'definir' incompleta, falta tipo de dato")


def parse_return(self):
    estados = ["q0", "q1", "q2"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "DEVOLVER":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type in [
            "IDENTIFICADOR",
            "LITERAL_NUMERICA",
            "LITERAL_CADENA",
            "LITERAL_BOOLEANO",
        ]:
            estado_actual = "q2"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'devolver' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q2":
        self.errors.append(
            "Error: Estructura 'devolver' incompleta, falta valor de retorno"
        )


def parse_input(self):
    estados = ["q0", "q1", "q2"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "ENTRADA":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "IDENTIFICADOR":
            estado_actual = "q2"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'entrada' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q2":
        self.errors.append(
            "Error: Estructura 'entrada' incompleta, falta identificador"
        )


def parse_print(self):
    estados = ["q0", "q1", "q2", "q3"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "MOSTRAR":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "PARENTESIS_IZQ":
            estado_actual = "q2"
        elif estado_actual == "q2" and token_type in [
            "IDENTIFICADOR",
            "LITERAL_CADENA",
        ]:
            estado_actual = "q3"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'mostrar' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q3":
        self.errors.append(
            "Error: Estructura 'mostrar' incompleta, falta contenido a imprimir"
        )


def parse_variable_declaration(self):
    estados = ["q0", "q1", "q2"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type in [
            "ENTERO",
            "DECIMAL",
            "CADENA",
            "BOOLEANO",
        ]:
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "IDENTIFICADOR":
            estado_actual = "q2"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la declaración de variable en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q2":
        self.errors.append(
            "Error: Declaración de variable incompleta, falta identificador"
        )


def parse_print(self):
    estados = ["q0", "q1", "q2", "q3"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "MOSTRAR":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "PARENTESIS_IZQ":
            estado_actual = "q2"
        elif estado_actual == "q2" and token_type == "LITERAL_CADENA":
            estado_actual = "q3"
        elif estado_actual == "q3" and token_type == "PARENTESIS_DER":
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la estructura 'mostrar' en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q3":
        self.errors.append(
            "Error: Estructura 'mostrar' incompleta, falta contenido o cierre de paréntesis"
        )


def parse_assignment(self):
    estados = ["q0", "q1", "q2", "q3"]
    estado_actual = "q0"

    while self.position < len(self.tokens):
        token_type, value = self.tokens[self.position]

        if estado_actual == "q0" and token_type == "IDENTIFICADOR":
            estado_actual = "q1"
        elif estado_actual == "q1" and token_type == "ASIGNACION":
            estado_actual = "q2"
        elif estado_actual == "q2" and token_type == "ENTRADA":
            estado_actual = "q3"
            break
        else:
            self.errors.append(
                f"Error de sintaxis en la asignación en posición {self.position}"
            )
            break

        self.position += 1

    if estado_actual != "q3":
        self.errors.append("Error: Asignación incompleta, falta 'entrada()'")

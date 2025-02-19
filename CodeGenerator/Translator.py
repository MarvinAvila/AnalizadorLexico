class Translator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.translated_code = ""
        self.indentation = 0  # Controla la indentación

    def add_line(self, line):
        """Agrega una línea al código traducido con la indentación adecuada"""
        self.translated_code += "    " * self.indentation + line + "\n"

    def translate(self):
        token_iter = iter(self.tokens)
        for token in token_iter:
            token_type, value = token

            if token_type == "SI":
                self.add_line("if ")
            elif token_type == "ENTONCES":
                self.translated_code = self.translated_code.rstrip() + ":\n"  # Corrige la línea anterior
                self.indentation += 1
            elif token_type == "SINO":
                self.indentation -= 1
                self.add_line("else:")
                self.indentation += 1
            elif token_type == "FIN":
                self.indentation -= 1
            elif token_type == "MIENTRAS":
                self.add_line("while ")
            elif token_type == "HACER":
                self.translated_code = self.translated_code.rstrip() + ":\n"
                self.indentation += 1
            elif token_type == "MOSTRAR":
                self.add_line("print(")
            elif token_type == "PARENTESIS_IZQ":
                self.translated_code += "("
            elif token_type == "PARENTESIS_DER":
                self.translated_code += ")"
            elif token_type == "ENTRADA":
                self.add_line("input()")
            elif token_type == "IDENTIFICADOR":
                self.translated_code += value + " "
            elif token_type == "ASIGNACION":
                self.translated_code += "= "
            elif token_type in ["LITERAL_NUMERICA", "LITERAL_CADENA", "LITERAL_BOOLEANO"]:
                self.translated_code += value + " "

        return self.translated_code

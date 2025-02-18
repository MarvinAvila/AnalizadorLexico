class Translator:
    def __init__(self, tokens):
        self.tokens = tokens
        self.translated_code = ""

    def translate(self):
        for token in self.tokens:
            if token[0] == "IF":
                self.translated_code += "if "
            elif token[0] == "PRINT":
                self.translated_code += "print"
            else:
                self.translated_code += token[1] + " "
        return self.translated_code
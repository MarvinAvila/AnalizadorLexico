import re
from LexicalAnalyzer.Tokens import TOKENS
from LexicalAnalyzer.LexicalErrors import LexicalErrors

class Lexer:
    def __init__(self):
        self.tokens = []
        self.errors = LexicalErrors()

    def tokenize(self, code):
        position = 0
        while position < len(code):
            found = False
            for token_name, token_regex in TOKENS:
                regex = re.compile(token_regex)
                match = regex.match(code, position)
                if match:
                    value = match.group(0)
                    if token_name != "ESPACIO":
                        self.tokens.append((token_name, value))
                    position = match.end()
                    found = True
                    break
            if not found:
                self.errors.add_error(position, code[position])  # Usar la clase de errores
                position += 1
        return self.tokens, self.errors.get_errors()
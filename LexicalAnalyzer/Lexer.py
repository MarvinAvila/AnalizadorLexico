import re
from LexicalAnalyzer.Tokens import TOKENS

class Lexer:
    def __init__(self):
        self.tokens = []
        self.errors = []

    def tokenize(self, code):
        position = 0
        while position < len(code):
            found = False
            for token_name, token_regex in TOKENS:
                regex = re.compile(token_regex)
                match = regex.match(code, position)
                if match:
                    value = match.group(0)
                    if token_name != "WHITESPACE":
                        self.tokens.append((token_name, value))
                    position = match.end()
                    found = True
                    break
            if not found:
                self.errors.append(f"Error at position {position}: '{code[position]}' not recognized")
                position += 1
        return self.tokens, self.errors
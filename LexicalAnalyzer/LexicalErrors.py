# LexicalAnalyzer/LexicalErrors.py
class LexicalErrors:
    def __init__(self):
        self.errors = []

    def add_error(self, position, char):
        self.errors.append(f"Error léxico en posición {position}: '{char}' no reconocido")

    def get_errors(self):
        return self.errors

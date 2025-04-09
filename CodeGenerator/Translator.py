class Translator:
    def __init__(self, tac_code):
        self.tac_code = tac_code
        self.python_code = []
        self.indent_level = 0
        self.indent_size = 4

    def add_line(self, line):
        """Añade línea con identación correcta"""
        indented = ' ' * self.indent_level + line
        self.python_code.append(indented)

    def translate(self):
        """Convierte TAC a Python con identación perfecta"""
        i = 0
        while i < len(self.tac_code):
            line = self.tac_code[i].strip()
            
            # Manejar fin de bloque
            if line == '}':
                self.indent_level = max(0, self.indent_level - self.indent_size)
                i += 1
                continue
                
            # Manejar estructuras de control
            if line.endswith(':'):
                self.add_line(line)
                self.indent_level += self.indent_size
                i += 1
                
                # Verificar si el siguiente es { y saltarlo
                if i < len(self.tac_code) and self.tac_code[i].strip() == '{':
                    i += 1
                continue
                
            # Manejar else
            if line == 'else:':
                self.indent_level -= self.indent_size
                self.add_line('else:')
                self.indent_level += self.indent_size
                i += 1
                
                # Verificar si el siguiente es { y saltarlo
                if i < len(self.tac_code) and self.tac_code[i].strip() == '{':
                    i += 1
                continue
                
            # Ignorar llaves de apertura
            if line == '{':
                i += 1
                continue
                
            # Línea normal de código
            self.add_line(line)
            i += 1
        
        # Validar identación final
        if self.indent_level != 0:
            raise ValueError("Error de identación: Bloques no balanceados")
        
        return '\n'.join(self.python_code)
class Optimizer:
    def __init__(self):
        self.essential_vars = set()
        self.keep_lines = set()

    def analyze_dependencies(self, tac_code):
        """Identifica variables realmente usadas en el código"""
        # Primero identificar todas las variables usadas en expresiones
        used_vars = set()
        
        for i, line in enumerate(tac_code):
            # Identificar variables en prints
            if line.strip().startswith('print('):
                args = line[line.find('(')+1:line.rfind(')')].split(',')
                for arg in args:
                    var = arg.strip().strip('"\'')
                    if var.isidentifier() and not var[0].isdigit():
                        used_vars.add(var)
            
            # Identificar variables en condiciones
            if any(kw in line for kw in ['if', 'while']):
                cond_part = line.split(':')[0]
                for token in cond_part.split():
                    if token.isidentifier() and token not in ['if', 'while', 'else']:
                        used_vars.add(token)
            
            # Identificar variables en expresiones
            if '=' in line:
                expr = line.split('=')[1].strip()
                for token in expr.split():
                    if token.isidentifier() and token not in ['True', 'False']:
                        used_vars.add(token)
        
        # Rastrear dependencias hacia atrás
        self.essential_vars = used_vars.copy()
        changed = True
        while changed:
            changed = False
            for line in reversed(tac_code):
                if '=' in line:
                    var = line.split('=')[0].strip()
                    expr = line.split('=')[1].strip()
                    if var in self.essential_vars:
                        # Agregar variables usadas en la expresión
                        for token in expr.split():
                            if token.isidentifier() and token not in self.essential_vars:
                                self.essential_vars.add(token)
                                changed = True
        
        # Identificar líneas esenciales
        for i, line in enumerate(tac_code):
            # Conservar todas las declaraciones de variables esenciales
            if any(line.startswith(f"{var} =") for var in self.essential_vars):
                self.keep_lines.add(i)
            # Conservar estructuras de control
            if any(kw in line for kw in ['if', 'while', 'for', 'else', '{', '}']):
                self.keep_lines.add(i)
            # Conservar prints
            if line.strip().startswith('print('):
                self.keep_lines.add(i)

    def optimize(self, tac_code):
        """Optimiza conservando solo lo esencial"""
        self.analyze_dependencies(tac_code)
        optimized = []
        
        for i, line in enumerate(tac_code):
            # Conservar líneas marcadas como esenciales
            if i in self.keep_lines:
                optimized.append(line)
            # Conservar asignaciones a variables esenciales
            elif '=' in line:
                var = line.split('=')[0].strip()
                if var in self.essential_vars:
                    optimized.append(line)
        
        return optimized
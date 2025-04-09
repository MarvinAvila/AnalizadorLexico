from SyntaxAnalyzer.AST import (
    NodoPrograma, NodoBinario, NodoLiteral, NodoIdentificador,
    NodoIf, NodoMientras, NodoRepetir, NodoPara, NodoMostrar,
    NodoDeclaracion, NodoAsignacion, NodoUnario
)

class TACGenerator:
    def __init__(self):
        self.temp_count = 0
        self.code = []
        self.current_temp = None
    
    def new_temp(self):
        """Genera un nuevo nombre de variable temporal"""
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp
    
    def emit(self, instruction):
        """Agrega una instrucción al código TAC"""
        self.code.append(instruction)
    
    def generate(self, ast_node):
        """Método principal para generar TAC a partir del AST"""
        if isinstance(ast_node, NodoPrograma):
            return self.generate_programa(ast_node)
        elif isinstance(ast_node, NodoBinario):
            return self.generate_binario(ast_node)
        elif isinstance(ast_node, NodoLiteral):
            return self.generate_literal(ast_node)
        elif isinstance(ast_node, NodoIdentificador):
            return self.generate_identificador(ast_node)
        elif isinstance(ast_node, NodoIf):
            return self.generate_if(ast_node)
        elif isinstance(ast_node, NodoMientras):
            return self.generate_mientras(ast_node)
        elif isinstance(ast_node, NodoRepetir):
            return self.generate_repetir(ast_node)
        elif isinstance(ast_node, NodoPara):
            return self.generate_para(ast_node)
        elif isinstance(ast_node, NodoMostrar):
            return self.generate_mostrar(ast_node)
        elif isinstance(ast_node, NodoDeclaracion):
            return self.generate_declaracion(ast_node)
        elif isinstance(ast_node, NodoAsignacion):
            return self.generate_asignacion(ast_node)
        elif isinstance(ast_node, NodoUnario):
            return self.generate_unario(ast_node)
        else:
            raise ValueError(f"Nodo AST no reconocido: {type(ast_node)}")
        
        return self.code

    def generate_programa(self, node):
        """Genera TAC para un programa completo"""
        for decl in node.declaraciones:
            self.generate(decl)
        return self.code
    
    def generate_binario(self, node):
        """Genera TAC para operaciones binarias"""
        left_temp = self.generate(node.izquierda)
        right_temp = self.generate(node.derecha)
        self.current_temp = self.new_temp()
        self.emit(f"{self.current_temp} = {left_temp} {node.operador} {right_temp}")
        return self.current_temp
    
    def generate_literal(self, node):
        """Genera TAC para literales"""
        if node.tipo == "cadena":
            return f'"{node.valor}"'
        elif node.tipo == "booleano":
            return "True" if node.valor else "False"  # Cambiado a inglés
        return str(node.valor)
    
    def generate_identificador(self, node):
        """Genera TAC para identificadores"""
        return node.nombre
    
    def generate_if(self, node):
        """Genera TAC para if-then-else con marcas de indentación"""
        cond_temp = self.generate(node.condicion)
        self.emit(f"if {cond_temp}:")
        self.emit("{")  # Marca de inicio de bloque
        for stmt in node.cuerpo_if:
            self.generate(stmt)
        if node.cuerpo_else:
            self.emit("}")  # Cierre de bloque if
            self.emit("else:")
            self.emit("{")  # Marca de inicio de bloque else
            for stmt in node.cuerpo_else:
                self.generate(stmt)
        self.emit("}")  # Cierre de bloque
    
    def generate_mientras(self, node):
        """Genera TAC para MIENTRAS-HACER"""
        cond_temp = self.generate(node.condicion)
        self.emit(f"while {cond_temp}:  # MIENTRAS")
        self.emit("{")
        for stmt in node.cuerpo:
            self.generate(stmt)
        self.emit("}")
    
    def generate_repetir(self, node):
        """Genera TAC para REPETIR-HASTA_QUE"""
        self.emit("# Inicio REPETIR-HASTA_QUE")
        self.emit("while True:")
        self.emit("{")
        
        # Cuerpo del REPETIR
        for stmt in node.cuerpo:
            self.generate(stmt)
        
        # Condición HASTA_QUE
        cond_temp = self.generate(node.condicion)
        self.emit(f"if {cond_temp}:")
        self.emit("{")
        self.emit("    break")
        self.emit("}")
        self.emit("}")
        self.emit("# Fin REPETIR-HASTA_QUE")
        
    def generate_para(self, node):
        """Genera TAC para for sin etiquetas"""
        init_temp = self.generate(node.inicio)
        self.emit(f"{node.variable.nombre} = {init_temp}")
        
        fin_temp = self.generate(node.fin)
        self.emit(f"while {node.variable.nombre} <= {fin_temp}:")
        self.emit("{")  # Inicio del bloque
        
        for stmt in node.cuerpo:
            self.generate(stmt)
        
        if node.paso:
            paso_temp = self.generate(node.paso)
            self.emit(f"{node.variable.nombre} += {paso_temp}")
        else:
            self.emit(f"{node.variable.nombre} += 1")
        
        self.emit("}")  # Fin del bloque
    
    def generate_mostrar(self, node):
        """Genera TAC para mostrar (unificado en un print)"""
        exprs = [self.generate(expr) for expr in node.expresiones]
        self.emit(f'print({", ".join(exprs)})')
    
    def generate_declaracion(self, node):
        """Genera TAC para declaraciones"""
        if node.expresion:
            expr_temp = self.generate(node.expresion)
            self.emit(f"{node.identificador.nombre} = {expr_temp}")
    
    def generate_asignacion(self, node):
        """Genera TAC para asignaciones"""
        expr_temp = self.generate(node.expresion)
        self.emit(f"{node.identificador.nombre} = {expr_temp}")
    
    def generate_unario(self, node):
        """Genera TAC para operaciones unarias"""
        expr_temp = self.generate(node.expresion)
        self.current_temp = self.new_temp()
        if node.operador == "NOT":
            self.emit(f"{self.current_temp} = not {expr_temp}")
        else:  # Operador unario negativo
            self.emit(f"{self.current_temp} = -{expr_temp}")
        return self.current_temp
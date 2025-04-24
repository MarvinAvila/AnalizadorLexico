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
        self.indent_level = 0

    def new_temp(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def emit(self, instruction):
        indent = "    " * self.indent_level
        self.code.append(f"{indent}{instruction}")

    def generate(self, ast_node):
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

    def generate_programa(self, node):
        for decl in node.declaraciones:
            self.generate(decl)
        return self.code

    def generate_binario(self, node):
        left_temp = self.generate(node.izquierda)
        right_temp = self.generate(node.derecha)
        self.current_temp = self.new_temp()

        # Mapeo de operadores lógicos de PSeInt a Python
        op = node.operador
        if op == "AND":
            op = "and"
        elif op == "OR":
            op = "or"
        elif op == "NOT":
            op = "not"

        self.emit(f"{self.current_temp} = {left_temp} {op} {right_temp}")
        return self.current_temp


    def generate_literal(self, node):
        if node.tipo == "cadena":
            return f'"{node.valor}"'
        elif node.tipo == "booleano":
            return "True" if node.valor else "False"
        return str(node.valor)

    def generate_identificador(self, node):
        return node.nombre

    def generate_if(self, node):
        cond_temp = self.generate(node.condicion)
        self.emit(f"if {cond_temp}:")
        self.indent_level += 1
        for stmt in node.cuerpo_if:
            self.generate(stmt)
        self.indent_level -= 1
        if node.cuerpo_else is not None and len(node.cuerpo_else) > 0:
            self.emit("else:")
            self.indent_level += 1
            for stmt in node.cuerpo_else:
                self.generate(stmt)
            self.indent_level -= 1

    def generate_mientras(self, node):
        self.emit("# inicio mientras")
        self.emit("while True:")
        self.indent_level += 1
        cond_temp = self.generate(node.condicion)
        self.emit(f"if not {cond_temp}:")
        self.indent_level += 1
        self.emit(f"break")
        self.indent_level -= 1
        for stmt in node.cuerpo:
            self.generate(stmt)
        self.indent_level -= 1
        self.emit("# fin mientras")

    def generate_repetir(self, node):
        self.emit("while True:")
        self.indent_level += 1
        for stmt in node.cuerpo:
            self.generate(stmt)
        cond_temp = self.generate(node.condicion)
        self.emit(f"if {cond_temp}:")
        self.indent_level += 1
        self.emit("break")
        self.indent_level -= 1
        self.indent_level -= 1

    def generate_para(self, node):
        self.emit(f"{node.variable.nombre} = {self.generate(node.inicio)}")
        fin_temp = self.generate(node.fin)
        paso_temp = self.generate(node.paso) if node.paso else "1"
        self.emit("# inicio para")
        self.emit("while True:")
        self.indent_level += 1
        cond_temp = self.new_temp()
        self.emit(f"{cond_temp} = {node.variable.nombre} <= {fin_temp}")
        self.emit(f"if not {cond_temp}:")
        self.indent_level += 1
        self.emit(f"break")
        self.indent_level -= 1
        for stmt in node.cuerpo:
            self.generate(stmt)
        self.emit(f"{node.variable.nombre} += {paso_temp}")
        self.indent_level -= 1
        self.emit("# fin para")


    def generate_mostrar(self, node):
        exprs = [self.generate(expr) for expr in node.expresiones]
        self.emit(f'print({", ".join(exprs)})')

    def generate_declaracion(self, node):
        if node.expresion:
            expr_temp = self.generate(node.expresion)
            self.emit(f"{node.identificador.nombre} = {expr_temp}")

    def generate_asignacion(self, node):
        expr_temp = self.generate(node.expresion)
        self.emit(f"{node.identificador.nombre} = {expr_temp}")

    def generate_unario(self, node):
        expr_temp = self.generate(node.expresion)
        self.current_temp = self.new_temp()
        if node.operador == "NOT":
            self.emit(f"{self.current_temp} = not {expr_temp}")
        else:
            self.emit(f"{self.current_temp} = -{expr_temp}")
        return self.current_temp

    def _indent(self):
        return "    " * self.indent_level

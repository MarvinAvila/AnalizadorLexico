from .TACGenerator import TACGenerator

def generate_tac(ast):
    generator = TACGenerator()
    return generator.generate(ast)
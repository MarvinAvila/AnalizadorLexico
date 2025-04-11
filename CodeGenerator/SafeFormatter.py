# SafeFormatter.py
import ast
import autopep8
from redbaron import RedBaron

def ensure_minimum_indent(code_lines):
    """Aplica indentación mínima a bloques con ':'"""
    result = []
    indent_level = 0
    indent_stack = []

    i = 0
    while i < len(code_lines):
        line = code_lines[i].rstrip()
        stripped = line.strip()

        # Detectar líneas que abren bloque
        if stripped.endswith(":"):
            result.append("    " * indent_level + stripped)
            indent_stack.append(indent_level)
            indent_level += 1
            i += 1
            # Asegurar que el siguiente bloque esté indentado
            if i < len(code_lines):
                next_line = code_lines[i].strip()
                if not next_line or next_line.endswith(":"):
                    result.append("    " * indent_level + "pass")
                elif not code_lines[i].startswith(" "):
                    code_lines[i] = "    " * indent_level + next_line
        else:
            result.append("    " * indent_level + stripped)
            i += 1

    return "\n".join(result)

def safe_redbaron_parse(code):
    """Formatea, valida y devuelve el árbol de RedBaron si es válido"""
    # 1. Asegura indentación básica
    preformatted = ensure_minimum_indent(code.split("\n"))

    # 2. Formatea el código
    formatted = autopep8.fix_code(preformatted)

    # 3. Valida sintaxis antes de usar RedBaron
    try:
        ast.parse(formatted)
    except SyntaxError as e:
        raise ValueError(f"❌ Error de sintaxis antes de RedBaron: línea {e.lineno} → {e.msg}")

    # 4. Pasar a RedBaron
    return RedBaron(formatted)

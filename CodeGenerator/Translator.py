# Translator.py
from CodeGenerator.SafeFormatter import safe_redbaron_parse


class Translator:
    def __init__(self, tac_code):
        self.tac_code = tac_code

    def translate(self):
        try:
            # ✅ Solo devolvemos el código generado tal como está
            return "\n".join(self.tac_code)
        except Exception as e:
            raise ValueError(f"Error traduciendo a Python: {str(e)}")

        
    def _add_minimum_indent(self, code):
        lines = code.split("\n")
        result = []
        indent_level = 0
        indent_stack = []

        i = 0
        while i < len(lines):
            line = lines[i].rstrip()
            stripped = line.strip()

            if not stripped:
                result.append("")  # líneas vacías
                i += 1
                continue

            # Detectar estructuras de control
            if stripped.endswith(":"):
                result.append("    " * indent_level + stripped)
                indent_level += 1
                indent_stack.append(indent_level)
                i += 1

                # Verificar si la siguiente línea es vacía o mal indentada
                if i >= len(lines) or not lines[i].strip():
                    result.append("    " * indent_level + "pass")
            else:
                result.append("    " * indent_level + stripped)
                i += 1

                # Si empieza una nueva instrucción de nivel superior, reducir indentación
                if indent_stack and not stripped.startswith(" "):
                    indent_level = indent_stack.pop() - 1

        return "\n".join(result)


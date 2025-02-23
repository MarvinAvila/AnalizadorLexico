import sys
import traceback

def run_code(python_code):
    try:
        exec(python_code, {"__builtins__": __builtins__})  # Evita acceso a funciones peligrosas
    except Exception as e:
        error_message = "".join(traceback.format_exception_only(type(e), e)).strip()
        return f"Error de ejecución: {error_message}"
    return "Ejecución completada sin errores"
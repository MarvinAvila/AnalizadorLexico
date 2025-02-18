def run_code(python_code):
    try:
        exec(python_code)
    except Exception as e:
        print(f"Execution Error: {e}")

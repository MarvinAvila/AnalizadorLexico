import tkinter as tk
from tkinter import ttk
from CodeEditor import CodeEditor
from ErrorPanel import ErrorPanel
from ConsolePanel import ConsolePanel
from CompilerController import CompilerController
import sys
import os

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador PSeInt en Español")
        self.root.geometry("1100x750")
        self._configure_window()
        self._create_widgets()
        self._setup_layout()
        
    def _configure_window(self):
        """Configura propiedades básicas de la ventana principal"""
        self.root.minsize(800, 600)
        self.root.option_add('*tearOff', False)
        self._setup_theme()

    def _setup_theme(self):
        """Configura el tema visual de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TButton', padding=6, font=('Segoe UI', 10))
        style.configure('TFrame', background='#f0f0f0')

    def _create_widgets(self):
        """Crea e inicializa todos los componentes de la UI"""
        # Frame principal para mejor organización
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Componentes principales
        self.code_editor = CodeEditor(self.main_frame)
        self.error_panel = ErrorPanel(self.main_frame)
        self.console_panel = ConsolePanel(self.main_frame)
        
        # Controlador del compilador (conexión entre componentes)
        self.compiler_controller = CompilerController(
            self.code_editor,
            self.error_panel,
            self.console_panel
        )
        
        # Botón de análisis
        self.analyze_btn = ttk.Button(
            self.main_frame,
            text="Analizar Código",
            command=self.compiler_controller.analyze_code,
            style='Accent.TButton'
        )
        
        # Configurar estilo especial para el botón principal
        style = ttk.Style()
        style.configure('Accent.TButton', foreground='white', background='#0078d7')

    def _setup_layout(self):
        """Configura el diseño de la interfaz usando grid"""
        # Configurar grid principal
        self.main_frame.columnconfigure(0, weight=3, uniform='col')
        self.main_frame.columnconfigure(1, weight=2, uniform='col')
        self.main_frame.rowconfigure(0, weight=2)
        self.main_frame.rowconfigure(1, weight=0)
        self.main_frame.rowconfigure(2, weight=1)
        
        # Posicionamiento de componentes
        self.code_editor.grid(
            row=0, column=0, 
            rowspan=3, 
            padx=(0, 10), pady=(0, 10), 
            sticky="nsew"
        )
        
        self.error_panel.grid(
            row=0, column=1, 
            padx=(0, 0), pady=(0, 10), 
            sticky="nsew"
        )
        
        self.analyze_btn.grid(
            row=1, column=1, 
            padx=(0, 0), pady=(0, 10), 
            sticky="ew"
        )
        
        self.console_panel.grid(
            row=2, column=1, 
            padx=(0, 0), pady=(0, 0), 
            sticky="nsew"
        )

    def run(self):
        """Inicia el bucle principal de la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    app = CompilerApp()
    app.run()
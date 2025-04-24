import tkinter as tk
from tkinter import ttk
from UI.CodeEditor import CodeEditor
from UI.ErrorPanel import ErrorPanel
from UI.ConsolePanel import ConsolePanel
from UI.CompilerController import CompilerController
import sys
import os

# Agregar la ruta del proyecto para importar los módulos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class CompilerApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Compilador PSeInt en Español")
        self.root.state('zoomed')
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
        
        self.button_frame = ttk.Frame(self.main_frame)
        
        
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
        
        # Botones dentro del frame
        self.analyze_btn = ttk.Button(
            self.button_frame,  # Cambiado a button_frame
            text="Analizar Código",
            command=self.compiler_controller.analyze_code,
            style='Accent.TButton'
        )
        self.analyze_btn.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        self.stop_btn = ttk.Button(
            self.button_frame,  # Cambiado a button_frame
            text="Detener ejecución",
            command=self.compiler_controller.stop_execution,
            style='Accent.TButton'
        )
        self.stop_btn.grid(row=0, column=1, sticky="ew")

            # Configurar peso de columnas en button_frame
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        
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
        self.code_editor.grid(row=0, column=0, rowspan=3, padx=(0, 10), pady=(0, 10), sticky="nsew")
        self.error_panel.grid(row=0, column=1, padx=(0, 0), pady=(0, 10), sticky="nsew")
        self.button_frame.grid(row=1, column=1, padx=(0, 0), pady=(0, 10), sticky="ew")
        self.console_panel.grid(row=2, column=1, padx=(0, 0), pady=(0, 0), sticky="nsew")
        
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
        
        self.button_frame.grid(
        row=1, column=1,
        padx=(0, 0), pady=(0, 10),
        sticky="ew"
        )

        self.console_panel.grid(
            row=2, column=1, 
            padx=(0, 0), pady=(0, ), 
            sticky="nsew"
        )
        

    def run(self):
        """Inicia el bucle principal de la aplicación"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CompilerApp()
    app.run()
# Interfaces graficas
import sys
import tkinter as ttk
from tkinter import *
import customtkinter as ctk
from CTkMenuBarPlus import CTkMenuBar, CustomDropdownMenu
import ctypes, os
from panels.ConfigDialog import ConfigDialog
from panels.ConfigManager import ConfigManager
from serialyzer import Serialyzer
# Frames
from panels.translationEditor import TranslationEditor
from panels.nodeEditor import NodeEditorFrame
from panels.charactersEditor import CharacterEditorFrame

# Este codigo le dice a Windows que trate este script como una aplicacion independiente
try:
    myappid = 'dialogue_editor.alcanciles_con_miopia' # Da igual lo que ponga, es un id propio
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    ctypes.windll.shcore.SetProcessDpiAwareness(1) # 1 = Process_System_DPI_Aware
except Exception as e:
    print(f"No se pudo configurar el ID de la barra de tareas: {e}")

def resource_path(relative_path):
    """ Gestiona rutas para que funcionen en desarrollo y en el .exe """
    try:
        # Carpeta temporal de PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        # Tema del sistema
        ctk.set_appearance_mode("System")
        # Color por defecto
        ctk.set_default_color_theme("green")
        # Creacion de la ventana
        self.geometry("1080x720")
        self.title("Editor de Dialogos")

        # Configuracion de resolucion dinamica
        width = 1080
        height = 720
        
        # Obtener resolucion de pantalla del usuario
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calcular posicion para centrar la ventana
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        self.geometry(f"{width}x{height}+{x}+{y}")

        # Ruta del icono
        # Usamos resource_path para que encuentre los archivos dentro del .exe
        icon_path_ico = resource_path(os.path.join("images", "icon.ico"))
        icon_path_png = resource_path(os.path.join("images", "icon.png"))

        if os.path.exists(icon_path_ico):
            # Icono de la ventana (esquina superior izquierda)
            self.iconbitmap(icon_path_ico)
            
            # Icono de la barra de tareas y Alt+Tab
            # Cargamos el PNG (es mas estable para iconphoto)
            if os.path.exists(icon_path_png):
                img = PhotoImage(file=icon_path_png)
                self.iconphoto(False, img)
        else:
            print(f"Error: No se encontro el icono en {icon_path_ico}")

        self.active_nodes = []
        
        # Inicializar el gestor de configuración
        self.config_manager = ConfigManager()

    def notify_character_change(self):
        '''
        Avisa a todos los nodos registrados que actualicen su lista de personajes
        '''
        print("Notificando que se ha creado un personaje")
        for node in self.active_nodes:
            # Verificamos que el nodo aun exista y tenga el metodo
            if hasattr(node, 'refresh_character_options'):
                node.refresh_character_options()

    def run(self):
        self._set_ui()

        # Pestanyas
        self.tabview = ctk.CTkTabview(master=self, command=self._on_tab_changed)
        self.tabview.pack(fill='both', expand=True)
        # Editor de nodos
        nodesTab = self.tabview.add("Editor de nodos")
        self.nodeEditorFrame = NodeEditorFrame(master=nodesTab)
        self.nodeEditorFrame.pack(fill='both', expand=True)
        # Editor de personajes
        charactersTab = self.tabview.add("Editor de personajes")
        self.characterEditorFrame = CharacterEditorFrame(master=charactersTab, config_manager=self.config_manager)
        self.characterEditorFrame.pack(fill='both', expand=True)
        # Editor de parametros extra (Ej: Botones de UI, imagenes con texto...)
        parametersTab = self.tabview.add("Parametros de juego")
        self.translationTab = TranslationEditor(parametersTab)
        self.translationTab.pack(fill='both', expand=True)

        # serializador
        self.seryalizer = Serialyzer(nodeEditor=self.nodeEditorFrame, charactersEditor=self.characterEditorFrame, translationEditor=self.translationTab)
        self.mainloop()

    def _set_ui(self):
        menu_bar = CTkMenuBar(self)
        menu_bar.pack(fill="x", side=TOP)

        # --- MENU ARCHIVOS ---
        file_btn = menu_bar.add_cascade("Archivo")
        # Menu desplegable
        file_dropdown = CustomDropdownMenu(widget=file_btn)
        file_dropdown.add_option("Nuevo", command=lambda: print("Nuevo"))
        file_dropdown.add_option("Abrir", command=lambda:self.seryalizer.load_project())
        file_dropdown.add_option("Exportar", command=lambda:self.seryalizer.save_project())
   
        # --- MENU EDITAR ---
        edit_btn = menu_bar.add_cascade("Editar")
        edit_dropdown = CustomDropdownMenu(widget=edit_btn)
        #edit_dropdown.add_option("Cortar")
        #edit_dropdown.add_option("Pegar")
        #edit_dropdown.add_separator()
        edit_dropdown.add_option("Configuracion", command=self._open_config_dialog)
        menu = ttk.Menu(self)
        self.config(menu=menu)
        # --- MENU VER ---
        #see_btn = menu_bar.add_cascade("Ver")
        #see_dropdown = CustomDropdownMenu(widget=see_btn)
        #see_dropdown.add_option("Panel Izquierdo", checkable=True, command=lambda: print("Ver Panel Izquierdo"))
        #see_dropdown.add_option("Panel Derecho", checkable=True, command=lambda: print("Ver Panel Derecho"))
    
    def _open_config_dialog(self):
        """Abre la ventana de configuración"""
        config_dialog = ConfigDialog(self, self.config_manager)
        # Esperar a que se cierre el diálogo
        self.wait_window(config_dialog)
        # Refrescar el editor de personajes si existe
        if hasattr(self, 'characterEditorFrame'):
            self.characterEditorFrame.refresh_audio_fonts_lists()

    def _on_tab_changed(self):
        '''
        Al cambiar de pestanya, quitamos el foco del teclado de cualquier sitio
        '''
        # Esto obliga a que el canvas pierda el control del teclado (NO FUNCIONA)
        # hasta que el usuario vuelva a hacer clic fisicamente en el.
        self.focus_set() 
        print(f"Cambiado a pestaña: {self.tabview.get()}")

if __name__ == "__main__":
    App().run()

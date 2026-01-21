# Interfaces graficas
import tkinter as ttk
from tkinter import *
import customtkinter as ctk
from CTkMenuBarPlus import CTkMenuBar, CustomDropdownMenu
import ctypes, os
from serialyzer import Serialyzer
# Frames
from panels.MiscelaneousEditor import MiscelaneousEditor
from panels.nodeEditor import NodeEditorFrame
from panels.charactersEditor import CharacterEditorFrame

# Este codigo le dice a Windows que trate este script como una aplicacion independiente
try:
    myappid = 'dialogue_editor.alcanciles_con_miopia' # Da igual lo que ponga, es un id propio
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(f"No se pudo configurar el ID de la barra de tareas: {e}")

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

        # Ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), "images", "icon.ico")
        if os.path.exists(icon_path):
            # Icono de la ventana
            self.iconbitmap(icon_path)
            # Icono para la barra de tareas y el selector Alt+Tab
            # A veces iconbitmap no es suficiente para CustomTkinter
            img = PhotoImage(file=icon_path.replace(".ico", ".png"))
            # Fuerza el icono:
            self.iconphoto(False, img)
        else:
            print(f"No se encontro el icono en {icon_path}")

        self.active_nodes = []

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
        self.nodesTab = self.tabview.add("Editor de nodos")
        nodeEditorFrame = NodeEditorFrame(master=self.nodesTab)
        nodeEditorFrame.pack(fill='both', expand=True)
        # Editor de personajes
        self.charactersTab = self.tabview.add("Editor de personajes")
        characterEditorFrame = CharacterEditorFrame(master=self.charactersTab)
        characterEditorFrame.pack(fill='both', expand=True)
        # Editor de parametros extra (Ej: Botones de UI, imagenes con texto...)
        self.parametersTab = self.tabview.add("Parametros de juego")
        miscelaneousTab = MiscelaneousEditor(self.parametersTab)
        miscelaneousTab.pack(fill='both', expand=True)

        # serializador
        self.seryalizer = Serialyzer(nodesTab=nodeEditorFrame, charactersTab=self.charactersTab)
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
        edit_dropdown.add_option("Cortar")
        edit_dropdown.add_option("Pegar")
        edit_dropdown.add_separator()
        edit_dropdown.add_option("Configuracion")
        menu = ttk.Menu(self)
        self.config(menu=menu)
        # --- MENU VER ---
        see_btn = menu_bar.add_cascade("Ver")
        see_dropdown = CustomDropdownMenu(widget=see_btn)
        see_dropdown.add_option("Panel Izquierdo", checkable=True, command=lambda: print("Ver Panel Izquierdo"))
        see_dropdown.add_option("Panel Derecho", checkable=True, command=lambda: print("Ver Panel Derecho"))
    
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

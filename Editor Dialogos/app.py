# Interfaces graficas
import tkinter as ttk
from tkinter import *
import customtkinter as ctk
from panels.nodeEditor import NodeEditorFrame
from panels.charactersEditor import CharacterEditorFrame
from CTkMenuBarPlus import CTkMenuBar, CustomDropdownMenu

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

    def run(self):
        self._set_ui()

        # Pestanyas
        tabview = ctk.CTkTabview(master=self)
        tabview.pack(fill='both', expand=True)
        # Editor de nodos
        self.nodesTab = tabview.add("Editor de nodos")
        nodeEditorFrame = NodeEditorFrame(master=self.nodesTab)
        nodeEditorFrame.pack(fill='both', expand=True)
        # Editor de personajes
        self.charactersTab = tabview.add("Editor de personajes")
        characterEditorFrame = CharacterEditorFrame(master=self.charactersTab)
        characterEditorFrame.pack(fill='both', expand=True)
        # Editor de parametros extra (Ej: Botones de UI, imagenes con texto...)
        self.parametersTab = tabview.add("Parametros de juego")

        self.mainloop()

    def _set_ui(self):
        menu_bar = CTkMenuBar(self)
        menu_bar.pack(fill="x", side=TOP)

        # --- MENU ARCHIVOS ---
        file_btn = menu_bar.add_cascade("Archivo")
        # Menu desplegable
        file_dropdown = CustomDropdownMenu(widget=file_btn)
        file_dropdown.add_option("Nuevo", command=lambda: print("Nuevo"))
        file_dropdown.add_option("Abrir", command=lambda: print("Abrir"))

        # --- MENU EDITAR ---
        edit_btn = menu_bar.add_cascade("Editar")
        edit_dropdown = CustomDropdownMenu(widget=edit_btn)
        edit_dropdown.add_option("Cortar")
        edit_dropdown.add_option("Pegar")
        edit_dropdown.add_separator()
        edit_dropdown.add_option("Configuración")
        menu = ttk.Menu(self)
        self.config(menu=menu)
        # --- MENU VER ---
        see_btn = menu_bar.add_cascade("Ver")
        see_dropdown = CustomDropdownMenu(widget=see_btn)
        see_dropdown.add_option("Panel Izquierdo", checkable=True, command=lambda: print("Ver Panel Izquierdo"))
        see_dropdown.add_option("Panel Derecho", checkable=True, command=lambda: print("Ver Panel Derecho"))

        




if __name__ == "__main__":
    App().run()

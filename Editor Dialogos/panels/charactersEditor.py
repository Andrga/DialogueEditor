import customtkinter as ctk
from tkinter import *
from panels.defs import characters, character
from customtkinter import CTkFrame

class CharacterEditorFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        # Configuramos el grid para que el panel izquierdo sea fijo y el derecho se expanda
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # --- CREAMOS LAS COSAS ---
        self._create_left_panel()

    def _create_left_panel(self):
        '''
        Metodo para crear un panel izquierdo (Lista de personajes)
        '''
        # Panel contenedor
        self.left_panel = CTkFrame(self, width=250, corner_radius=0, fg_color="#2b2b2b")
        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.left_panel.grid_propagate(False)
        
        # Titulo
        lbl_left = ctk.CTkLabel(self.left_panel, text="MIS PERSONAJES", font=("Roboto", 16, "bold"))
        lbl_left.pack(fill="x", pady=10)

        # Frame con scroll para la lista de personajes
        self.list_container = ctk.CTkScrollableFrame(self.left_panel, fg_color="transparent")
        self.list_container.pack(fill="both", expand=True, padx=5, pady=5)

        # Boton para anyadir nuevo personaje
        self.btn_add = ctk.CTkButton(self.left_panel, text="Nuevo Personaje", 
                                     command=self._on_add_click)
        self.btn_add.pack(fill="x", padx=10, pady=10)

        # Cargar personajes iniciales
        self.refresh_character_list()

    def refresh_character_list(self):
        '''
        Limpia y vuelve a dibujar la lista de personajes basada en la variable global
        '''
        global characters
        
        # Limpiar widgets actuales en la lista
        for widget in self.list_container.winfo_children():
            widget.destroy()

        # Crear un boton/item por cada personaje
        for name, char_obj in characters.items():
            char_item = ctk.CTkButton(
                self.list_container, 
                text=name,
                fg_color="#3d3d3d",
                border_color=char_obj.color, # Usamos el color del objeto character
                border_width=2,
                hover_color="#4d4d4d",
                anchor="w", # Texto alineado a la izquierda
                command=lambda n=name: self._select_character(n)
            )
            char_item.pack(fill="x", pady=2)

    def _on_add_click(self):
        '''
        Anyadimos un personaje default
        '''        
        # Anyadimos uno de prueba
        i = 1
        while True:
            char_name = f"Nuevo Personaje {i}"
            if char_name not in characters:
                break
            i += 1

        self.add_character(char_name, "#ffffff")
        self.refresh_character_list()
        
        # CharacterEditorFrame -> nose -> app
        app = self.master.master.master
        if hasattr(app, "notify_character_change"):
            app.notify_character_change()
        else:
            print(f"Algo ha ido mal notificando el añadir un personaje {app}")
    
    def _select_character(self, name):
        '''
        Selecciona un personaje para editar
        '''
        print(f"Editando a: {name}")
        # Codigo para cargar los datos en el panel derecho

    def add_character(self, name, color):
        global characters
        characters[name] = character(name, color)

    def remove_character(self, name):
        global characters
        del characters[name]
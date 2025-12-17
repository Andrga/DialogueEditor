import customtkinter as ctk
from tkinter import *
from panels.defs import characters, character
from CTkColorPicker import AskColor
from customtkinter import CTkFrame

class CharacterEditorFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        # Configuramos el grid para que el panel izquierdo sea fijo y el derecho se expanda
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        # --- CREAMOS LAS COSAS ---
        # feedback para cuando se ha seleccionado un personaje
        self.selected_char_button = None
        # Variables
        self.name_var = ctk.StringVar()
        self.color_var = ctk.StringVar()

        self._create_left_panel()
        self._create_rigth_panel()

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

    def _create_rigth_panel(self):
        '''
        Metodo para crear un panel izquierdo (Lista de personajes)
        '''
        # Panel contenedor
        self.right_panel = ctk.CTkFrame(self, corner_radius=0, fg_color="#1e1e1e")
        self.right_panel.grid(row=0, column=1, sticky="nsew")
        
        self.lbl_right = ctk.CTkLabel(self.right_panel, text="Editor de personaje", font=("Roboto", 18, "bold"))
        self.lbl_right.pack(pady=20)
        
        self.buttons_panel = ctk.CTkFrame(self.right_panel, corner_radius=0, fg_color="#1e1e1e")
        self.buttons_panel.pack(pady=5, side=BOTTOM)
        self.delete_button = ctk.CTkButton(self.buttons_panel, text="Eliminar", 
                                           command=self._on_delete_click, fg_color="#A32525", hover_color="#700F0F")
        self.delete_button.pack(pady=10, side=RIGHT)
        self.accept_button = ctk.CTkButton(self.buttons_panel, text="Guardar", 
                                           command=self._on_save_click)
        self.accept_button.pack(pady=10, side=RIGHT)

        # --- SECCION DE CAMPOS EDITABLES ---
        # Usamos un frame para agrupar los campos y hacerlo extensible
        self.edit_area = ctk.CTkScrollableFrame(self.right_panel, fg_color="#141414")
        self.edit_area.pack(fill="both", expand=True, padx=20)

        # Campo: Nombre
        ctk.CTkLabel(self.edit_area, text="Nombre del Personaje:").pack(anchor="w")
        self.entry_name = ctk.CTkEntry(self.edit_area, textvariable=self.name_var)
        self.entry_name.pack(fill="x", pady=(5, 15))
        # Campo: Color
        ctk.CTkLabel(self.edit_area, text="Color del Personaje:").pack(anchor="w")
        # Frame para el selector de color
        self.color_frame = ctk.CTkFrame(self.edit_area, fg_color="transparent")
        self.color_frame.pack(fill="x", pady=(5, 15))
        # Boton que abre el selector
        self.color_display = ctk.CTkButton(
            self.color_frame, 
            text="", 
            width=40, 
            height=40,
            corner_radius=20, # Lo hace circular
            border_width=2,
            border_color="#ffffff",
            command=self._choose_color
        )
        self.color_display.pack(side="left")
        
        self.color_label = ctk.CTkLabel(self.color_frame, text="#ffffff", font=("Consolas", 12))
        self.color_label.pack(side="left", padx=10)

    def _choose_color(self):
        '''Abre el selector de color del sistema'''
        # Seguridad
        if not hasattr(self, 'edit_char_obj') or not self.edit_char_obj:
            return

        # Creamos la ventana del selector
        pick_color = AskColor() 
        color = pick_color.get()

        if color:
            # Actualizar visualmente el editor
            self._update_color_ui(color)
            # Guardar inmediatamente en el objeto
            self.color_var.set(color)
    
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
                hover_color="#2e2d2d",
                anchor="w", # Texto alineado a la izquierda
                command=lambda n=name: self._select_character(n)
            )
            #Configuramos el comando pasando el nombre Y el propio botón (char_item)
            char_item.configure(command=lambda n=name, b=char_item: self._select_character(n, b))
            char_item.pack(fill="x", pady=2)
            
            # Si acabamos de refrescar y este era el seleccionado, lo resaltamos de nuevo
            if hasattr(self, 'current_char_name') and name == self.current_char_name:
                self._highlight_button(char_item)

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
        
        self._notify_app()

    def _on_save_click(self):
        '''
        Guarda los campos del personaje editado en el mapa global
        '''
        global characters
        
        # Verificamos que tengamos un personaje seleccionado para editar
        if hasattr(self, 'edit_char_obj') and self.edit_char_obj:
            new_name = self.name_var.get().strip()
            old_name = self.current_char_name

            # Combprobamos que el nombre no este vacio
            if not new_name:
                print("Error: El nombre no puede estar vacío")
                return
            # Cambiamos la key del diccionario
            if new_name != old_name:
                if new_name in characters:
                    print("Error: Ya existe un personaje con ese nombre")
                    return
                # Setteamos el objeto a la nueva key
                characters[new_name] = characters.pop(old_name)
                self.current_char_name = new_name
            # Resto de atributos
            self.edit_char_obj.color = self.color_var.get().strip()

            # Actualizamos la interfaz
            self.lbl_right.configure(text=f"Editando: {new_name}")
            self.refresh_character_list()
            self._notify_app()
            print(f"Personaje '{new_name}' guardado correctamente.")
        else:
            print("Error: no se ha guardado el personaje")
            

    def _on_delete_click(self):
        '''
        Elimina el personaje seleccionado actualmente del mapa global
        '''
        global characters
        
        # Verificamos que haya algo seleccionado para borrar
        if hasattr(self, 'current_char_name') and self.current_char_name:
            char_to_remove = self.current_char_name
            
            # Eliminar del diccionario
            if char_to_remove in characters:
                del characters[char_to_remove]
                print(f"Personaje '{char_to_remove}' eliminado.")

            # Resetear variables para limpiar el panel derecho
            self.edit_char_obj = None
            self.current_char_name = None
            self.name_var.set("") # Limpia el campo de texto
            self.lbl_right.configure(text="Editor de personaje")

            # Refrescar la lista de la izquierda
            self.refresh_character_list()

            # Notificar a los nodos del canvas para que actualicen sus ComboBox
            self._notify_app()
        else:
            print("No hay ningún personaje seleccionado para eliminar")

    def _notify_app(self):
        '''
        Notifica a la aplicacion que los personajes han cambiado
        '''
        # CharacterEditorFrame -> nose -> app
        app = self.master.master.master
        if hasattr(app, "notify_character_change"):
            app.notify_character_change()
        else:
            print(f"Algo ha ido mal notificando el añadir un personaje {app}")
    
    def _select_character(self, name, button_widget):
        global characters
        self.edit_char_obj = characters.get(name)
        
        if self.edit_char_obj:
            # -- Nombre
            self.current_char_name = name
            self.name_var.set(name)
            self.lbl_right.configure(text=f"Editando: {name}")
            # -- Color
            self.color_var.set(self.edit_char_obj.color)
            # Actualizar visualmente el editor
            self._update_color_ui(self.edit_char_obj.color)
            
            # Gestionar el resaltado visual
            self._highlight_button(button_widget)
        else:
            print(f"Personaje {name} no encontrado")
            
    
    def _update_color_ui(self, color):
        '''Actualiza los elementos visuales del panel derecho'''
        self.color_display.configure(fg_color=color, hover_color=color)
        self.color_label.configure(text=color.upper())
        self.accept_button.configure(border_color=color, border_width=2)

    def _highlight_button(self, button):
        '''
        Cambia los colores para resaltar el boton seleccionado
        '''
        # Devolver el boton anterior a su color normal
        if self.selected_char_button and self.selected_char_button.winfo_exists():
            self.selected_char_button.configure(fg_color="#3d3d3d")
        
        # Resaltar el nuevo boton
        self.selected_char_button = button
        self.selected_char_button.configure(fg_color="#1F1F1F")

    def add_character(self, name, color):
        global characters
        characters[name] = character(color)
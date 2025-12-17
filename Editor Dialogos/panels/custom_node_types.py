import __main__
import customtkinter as ctk
from tknodesystem.node import Node
from tknodesystem.node_socket import NodeSocket
from tknodesystem.node_args import Args
from panels.defs import characters, character
import warnings

class NodeEditable(Node):
    '''
    Referenciado de los nodos dados por tknodesystem en el archivo node_types.py
    '''
    def __init__(self, canvas, x=100, y=100, text="NPC Dialogo"):
        width = 240
        height = 200
        # tknodesystem dibuja basandose en el centro, no en la esquina superior izquierda.
        center = (x, y) 

        # Socket de Entrada (izquierdo)
        self.input_ = NodeSocket(
            canvas, 
            center=(x - width/2, y), # Posicion relativa al centro
            radius=8, 
            fg_color="#ffcc00",
            socket_num=1
        )
        # Socket de Salida (Derecha)
        self.output_ = NodeSocket(
            canvas, 
            center=(x + width/2, y), 
            radius=8, 
            fg_color="#ffcc00",
            socket_num=2
        )

        super().__init__(
            canvas=canvas,
            width=width,
            height=height,
            center=center,
            text=text,
            corner_radius=10,
            fg_color="#3b3b3b",
            border_color="#555555",
            text_color="white"
        )

        # Lista interna para que se muevan con el nodo
        self.allIDs = self.allIDs + [self.input_.ID, self.output_.ID]

        # --- CONTENIDO INTERNO ---
        self.container = ctk.CTkFrame(self.canvas, fg_color="transparent")
        # Ajustamos la posicion del contenedor relativa al centro del nodo
        # (tknodesystem usa create_window para meter widgets en el canvas)
        self.window_id = self.canvas.create_window(
            x, y,
            window=self.container, 
            width=width-15, 
            height=height-30
        )
        self.allIDs.append(self.window_id)
        # Selector de personaje
        global characters
        self.characterSelector = ctk.CTkComboBox(
            self.container, 
            values=list(characters.keys()), 
            command=self.on_selection,
            corner_radius=5
        )
        self.characterSelector.pack(fill="x", padx=0, pady=(0,5))
        self.characterSelector.set("Seleccionar")
        # Nombre
        #self.character = character("Default")
        #self.nombre = ctk.CTkTextbox(self.container, text_color=self.character.color, fg_color="#222222")
        #self.nombre.pack(fill="both", expand=True)
        #self.nombre.insert("0.0", self.character.name)
        # Dialogo
        self.textbox = ctk.CTkTextbox(
            self.container,
            text_color="white",
            fg_color="#222222",
            corner_radius=5
        )
        self.textbox.pack(fill="both", expand=True, padx=0, pady=0)
        self.textbox.insert("0.0", "Escribe aquí...")

        # Vincular el movimiento porque hemos anyadido elementos nuevos
        self.bind_all_to_movement()

        # Registrar observer para cuando se anyada nuevo personaje
        try:
            # Nodo -> Canvas -> CanvasContainer -> NodeEditorFrame -> nose -> app
            self.app = self.canvas.master.master.master.master.master 
            if hasattr(self.app, "active_nodes"):
                self.app.active_nodes.append(self)
            else:
                print("No se pudo registrar el nodo en App")
        except:
            print("No se pudo registrar el nodo en App")


    def refresh_character_options(self):
        '''
        Actualiza el ComboBox con el estado actual del diccionario global
        '''
        print("LISTA DE PERSONAJES ACTUALIZADOS")
        global characters
        self.characterSelector.configure(values=list(characters.keys()))
    

    def on_selection(self, characterSelected):
        global characters
        print(f"Personaje seleccionado: {characterSelected}")  

        char_obj = characters.get(characterSelected)

        # Si el personaje existe actualiza visualmente
        if char_obj:
            # Actualizando el personaje
            self.character = char_obj
            self.textbox.configure(text_color=self.character.color)
        else:
            # Caso por defecto si no se encuentra
            self.textbox.configure(text_color="white")

    # Sobreescribimos move para mover también la ventana del textbox
    def move(self, x, y):
        super().move(x, y)
        self.canvas.move(self.window_id, x, y)

class NodeDialogue(NodeEditable):
    pass
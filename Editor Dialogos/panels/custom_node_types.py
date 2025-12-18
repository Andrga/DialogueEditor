import __main__
import customtkinter as ctk
from tknodesystem.node import Node
from tknodesystem.node_socket import NodeSocket
from panels.defs import characters

class NodeEditable(Node):
    '''
    Nodo base editable.
    Incluye:
    - 1 input
    - 1 output
    - Selector de personaje
    - Textbox de contenido
    '''

    WIDTH = 240
    HEIGHT = 200
    def __init__(self, canvas, x=200, y=200, text="NPC Dialogo"):
        # tknodesystem dibuja basandose en el centro, no en la esquina superior izquierda.
        center = (x, y) 
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text=text,
            corner_radius=10,
            fg_color="#3b3b3b",
            border_color="#292929",
            text_color="white"
        )

        # --- SOCKETS ---
        self.inputs = []
        self.outputs = []

        self._create_sockets(x, y)
        
        # --- CONTENIDO INTERNO ---
        self._create_container(x, y)

        # Movimiento conjunto
        self.bind_all_to_movement()
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>',
                     lambda e: self.connect_input('input1'))
        self.canvas.bind_all("<Delete>", lambda e: self.destroy() if self.signal else None, add="+")
        self.socket_nums = len(self.outputs)
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        # Mueve a la posicion inicial
        if x or y:
            super().move(x,y)
            
        # Registro en la app (observer)
        self._register_in_app()
        self.canvas.obj_list.add(self)


    # =====================================================
    # SOCKETS
    # =====================================================

    def _create_sockets(self, x, y):
        # Input (izquierda)
        self.input_1 = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=1
        )
        self.inputs.append(self.input_1)

        # Output (derecha)
        self.output_ = NodeSocket(
            self.canvas,
            center=(x + self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=2
        )
        self.outputs.append(self.output_)

        self.allIDs.extend([
            self.input_1.ID,
            self.output_.ID
        ])
    
    # =====================================================
    # UI
    # =====================================================

    def _create_container(self, x, y):
        self.container = ctk.CTkFrame(self.canvas, fg_color="#3b3b3b")

        self.window_id = self.canvas.create_window(
            x,
            y,
            window=self.container,
            width=self.WIDTH - 15,
            height=self.HEIGHT - 30
        )

        self.allIDs.append(self.window_id)

    # =====================================================
    # CONNECTIONS
    # =====================================================

    def connect_output(self, event):
        """ connect output socket """
        
        self.canvas.clickcount += 1
        self.canvas.outputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
 
        self.output_.connect_wire()
    

    def connect_input(self, input_id):
        if self.canvas.outputcell is None:
            return

        self.canvas.clickcount += 1
        self.canvas.inputcell = self
        self.canvas.IDc = input_id

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            self.canvas.conectcells()

    def update(self):
        self.output_.value = True
    
    # =====================================================
    # EVENTOS
    # =====================================================

    def on_character_selected(self, name):
        char = characters.get(name)

        if char:
            self.character = char
            self.textbox.configure(text_color=char.color)
        else:
            self.character = None
            self.textbox.configure(text_color="white")

    # =====================================================
    # DATOS
    # =====================================================

    def get_data(self):
        return {
            "character": self.character.name if self.character else None,
            "text": self.textbox.get("0.0", "end").strip()
        }
    

    # =====================================================
    # UTILS
    # =====================================================

    def refresh_character_options(self):
        self.character_selector.configure(
            values=list(characters.keys())
        )

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass

class NodeStart(NodeEditable):
    TYPE = "start"
    def __init__(self, canvas, x=200, y=200, text="NPC Dialogo"):
        super().__init__(canvas, x, y, text)

class NodeDialogue(NodeEditable):
    TYPE = "dialogue"

    def __init__(self, canvas, x=200, y=200):
        super().__init__(canvas, x, y, text="Diálogo")
        
        # --- CONTENIDO INTERNO ---
        self._create_character_selector()
        self._create_textbox()

    def get_next_node(self):
        if not hasattr(self.canvas, "connections"):
            return None

        for conn in self.canvas.connections:
            if conn.output_socket == self.output_:
                return conn.input_socket.node
        return None

    def get_data(self):
        data = super().get_data()
        data.update({
            "type": self.TYPE
        })
        return data
    
    def destroy(self):
        super().destroy()
        # Destruir widgets embebidos
        try:
            if hasattr(self, "textbox"):
                self.textbox.destroy()
            if hasattr(self, "character_selector"):
                self.character_selector.destroy()
            if hasattr(self, "container"):
                self.container.destroy()
        except Exception:
            print(f"ERROR: {Exception}")
            pass
    
    # =====================================================
    # UI
    # =====================================================
    def _create_character_selector(self):
        self.character = None

        self.character_selector = ctk.CTkComboBox(
            self.container,
            values=list(characters.keys()),
            command=self.on_character_selected,
            corner_radius=5
        )
        self.character_selector.pack(fill="x", pady=(0, 5))
        self.character_selector.set("Seleccionar")

    def _create_textbox(self):
        self.textbox = ctk.CTkTextbox(
            self.container,
            fg_color="#222222",
            text_color="white",
            corner_radius=5
        )
        self.textbox.pack(fill="both", expand=True)
        self.textbox.insert("0.0", "Escribe aquí...")

class NodeDecision(NodeEditable):
    OPTION_HEIGHT = 30
    def __init__(self, canvas, x=200, y=200):
        self.options = []
        super().__init__(canvas, x, y, text="Decisión")


        # Botón añadir opción
        self.add_button = ctk.CTkButton(
            self.container,
            text="+ Añadir opción",
            command=self.add_option,
            height=24
        )
        self.add_button.pack(fill="x", pady=(5, 0))

        # Crear opciones iniciales
        self.add_option()
        self.add_option()

    # --------------------------------
    # OPCIONES
    # --------------------------------  

    def add_option(self):
        index = len(self.options)

        # Campo de texto
        entry = ctk.CTkEntry(
            self.container,
            placeholder_text=f"Opción {index + 1}"
        )
        entry.pack(fill="x", pady=2)

        # Socket de salida
        socket = NodeSocket(
            self.canvas,
            center=self._get_output_position(index),
            radius=10,
            fg_color="#00ccff",
            socket_num=10 + index
        )

        self.outputs.append(socket)
        self.allIDs.append(socket.ID)

        self.options.append({
            "entry": entry,
            "socket": socket,
            "index": index
        })

        self._resize_node()


    def _get_output_position(self, index):
        # Borde derecho
        x = self.center[0] + self.WIDTH / 2
        # Calculamos desde el borde superior actual
        y_top = self.center[1] - (self.height / 2)
        # Ajustamos el offset (85px suele ser el espacio del botón + padding)
        y = y_top + 85 + (index * self.OPTION_HEIGHT)
        return (x, y)

    def update_sockets(self):
        # Usar self.center como referencia absoluta
        x, y = self.center
        
        # Input principal (izquierda)
        if hasattr(self, "input_1"):
            r = self.input_1.radius
            # El borde izquierdo es x - ancho/2
            self.canvas.coords(self.input_1.ID, 
                               x - self.WIDTH/2 - r, y - r, 
                               x - self.WIDTH/2 + r, y + r)
            self.input_1.update()

        # Sockets de opciones (derecha)
        if hasattr(self, "options"):
            for opt in self.options:
                pos = self._get_output_position(opt["index"])
                r = opt["socket"].radius
                self.canvas.coords(opt["socket"].ID, 
                                   pos[0]-r, pos[1]-r, 
                                   pos[0]+r, pos[1]+r)
                opt["socket"].update()

        # Actualizar cables
        for i in self.canvas.line_ids:
            i.update()


    def _resize_node(self):
        # Nueva altura basada en la cantidad de opciones
        self.height = self.HEIGHT + (len(self.options) * self.OPTION_HEIGHT)
        
        # REcalculamos UNO A UNO los puntos del poligono
        x, y = self.center
        x1, y1 = x - self.WIDTH / 2, y - self.height / 2
        x2, y2 = x + self.WIDTH / 2, y + self.height / 2
        r = self.corner_radius
        
        new_points = [
            x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, 
            x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, 
            x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1
        ]
        
        self.canvas.coords(self.ID, *new_points)

        # Sincronizar el contenedor CTK
        self.canvas.coords(self.window_id, x, y)
        self.canvas.itemconfig(self.window_id, height=self.height - 40)

        # Refrescar posiciones de sockets
        self.update_sockets()

    def get_data(self):
        return {
            "type": self.TYPE,
            "options": [
                {
                    "text": opt["entry"].get(),
                    "socket": opt["index"]
                }
                for opt in self.options
            ]
        }

    def destroy(self):
        for opt in self.options:
            opt["entry"].destroy()
            opt["socket"].destroy()

        self.add_button.destroy()
        super().destroy()

class NodeEvent(NodeEditable):
    TYPE = "event"

    def __init__(self, canvas, x=200, y=200):
        super().__init__(canvas, x, y, text="Evento")

        # Cambiar UI: no necesitamos textbox
        self.textbox.destroy()

        self.event_name = ctk.CTkEntry(
            self.container,
            placeholder_text="Nombre del evento"
        )
        self.event_name.pack(fill="x", pady=5)

    def get_data(self):
        return {
            "type": self.TYPE,
            "event": self.event_name.get()
        }

    def get_next_node(self):
        if not hasattr(self.canvas, "connections"):
            return None

        for conn in self.canvas.connections:
            if conn.output_socket == self.output_:
                return conn.input_socket.node
        return None

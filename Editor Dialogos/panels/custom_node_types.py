from tkinter import Menu
import customtkinter as ctk
from panels.defs import nodeBase

class ConnectableNode(nodeBase):
    '''
    Nodo con conectores de entrada y salida
    '''
    # Variable de clase para rastrear conexiones
    _active_connector = None
    _temp_line = None
    _all_nodes = []
    
    _node_id_counter = 0  # Contador global para IDs unicos
    def __init__(self, canvas, x, y, width=200, height=120, title="Nodo Conectable", **kwargs):
        self.input_connector = None
        self.output_connector = []   # Soporta multiples conectores de salida
        self.output_connections = [] # Lista de conexiones desde este nodo
        self.input_connections = []  # Conexiones entrantes
       
        super().__init__(canvas, x, y, width=width, height=height, title=title, **kwargs)

        # Personaje asociado
        self.character = None  
        # ID del nodo
        self.node_id = ConnectableNode._node_id_counter
        ConnectableNode._node_id_counter += 1
        
        # Registrar este nodo
        ConnectableNode._all_nodes.append(self)
        # Menu contextual de personajes
        self.create_context_menu()
        self.title_bar.bind("<Button-3>", self.show_context_menu)
        self.title_label.bind("<Button-3>", self.show_context_menu)
        # Crear conectores despues de que el frame este en el canvas
        self.create_connectors()
    
    def setup_content(self):
        # Contenido central
        label = ctk.CTkLabel(
            self.content_frame,
            text="Nodo Conectable\nConecta las bolitas",
            justify="center"
        )
        label.pack(expand=True, pady=10)
    
    def create_connectors(self):
        '''
        Crea las bolitas de entrada y salida
        '''
        print("Creando conectores para el nodo")
        # Obtener posicion del frame
        x, y = self.get_position()
        frame_height = self.winfo_height()
        
        # Conector de entrada (izquierda)
        input_y = y + frame_height // 2
        self.input_connector = self.canvas.create_oval(
            x - 10, input_y - 8,
            x + 2, input_y + 8,
            fill="#4CAF50",
            outline="#ffffff",
            width=2,
            tags=("connector", "input", f"node_{id(self)}")
        )
        
        # Conector de salida (derecha)
        frame_width = self.winfo_width()
        output_x = x + frame_width
        output_y = y + frame_height // 2
        self.output_connector.append(self.canvas.create_oval(
            output_x - 2, output_y - 8,
            output_x + 10, output_y + 8,
            fill="#2196F3",
            outline="#ffffff",
            width=2,
            tags=("connector", "output", f"node_{id(self)}")
        ))
        
        # Eventos para el conector de salida (inicio de conexion)
        self.canvas.tag_bind(self.output_connector[0], "<ButtonPress-1>", self.start_connection)
        self.canvas.tag_bind(self.output_connector[0], "<B1-Motion>", self.drag_connection)
        self.canvas.tag_bind(self.output_connector[0], "<ButtonRelease-1>", self.end_connection)

    def start_connection(self, event, option_index=0):
        '''
        Inicia una nueva conexion desde el conector de salida
        '''
        #print("Starting connection")
        # Indicar que se esta arrastrando una conexion
        self.canvasGrid.draggingConnection = True
        ConnectableNode._active_connector = self
        self._active_option_index = option_index
        
        # Obtener posicion del conector de salida
        coords = self.canvas.coords(self.output_connector[option_index])
        start_x = (coords[0] + coords[2]) / 2
        start_y = (coords[1] + coords[3]) / 2
        
        # Crear linea temporal
        ConnectableNode._temp_line = self.canvas.create_line(
            start_x, start_y, event.x, event.y,
            fill="#FFD700",
            width=3,
            tags="temp_connection"
        )
    
    def drag_connection(self, event):
        '''
        Arrastra la linea de conexion temporal
        '''
        #print("Dragging connection")
        #self.canvasGrid.draggingConnection = True
        if ConnectableNode._temp_line:
            coords = self.canvas.coords(ConnectableNode._temp_line)
            self.canvas.coords(ConnectableNode._temp_line, coords[0], coords[1], event.x, event.y)
    
    def end_connection(self, event, option_index=0):
        '''
        Finaliza la conexion
        '''
        #print("Ending connection")
        self.canvasGrid.draggingConnection = False
        if ConnectableNode._temp_line:
            # Buscar si se solto sobre un conector de entrada
            items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
            
            connected = False
            for item in items:
                tags = self.canvas.gettags(item)
                if "input" in tags and "connector" in tags:
                    # Encontrar el nodo al que pertenece este conector
                    for node in ConnectableNode._all_nodes:
                        if node.input_connector == item and node != self:
                            self.connect_to(target_node=node, option_index=option_index)
                            connected = True
                            break
                    break
            
            # Si no se conecto, eliminar linea temporal
            if not connected:
                self.canvas.delete(ConnectableNode._temp_line)
            
            ConnectableNode._temp_line = None
            ConnectableNode._active_connector = None 
            
            if hasattr(self, '_active_option_index'):
                delattr(self, '_active_option_index')

    def connect_to(self, target_node, option_index=0):
        '''
        Conecta este nodo con otro nodo
        '''
        # Eliminar conexion anterior desde este nodo (solo una salida permitida)
        if self.output_connections:
            for conn in self.output_connections:
                # Hay que procesar solo las conexiones desde el conector activo "option_index"
                if conn["option_index"] != option_index:
                    continue
                try:
                    self.canvas.delete(conn["line"])
                    # Eliminar referencia de input_connections del nodo destino anterior
                    if conn["line"] in [ic["line"] for ic in conn["target"].input_connections]:
                        conn["target"].input_connections = [
                            ic for ic in conn["target"].input_connections 
                            if ic["line"] != conn["line"]
                        ]
                except:
                    pass
                self.output_connections.remove(conn)
        if not self.output_connector:
            print("Error: No hay conectores.")
            return
        
        # Crear linea de conexion permanente
        print(f"Lista de conectores de salida: {self.output_connector}, usando indice {option_index}")
        out_coords = self.canvas.coords(self.output_connector[option_index])
        if not out_coords or len(out_coords) < 4:
            print(f"Error: Coordenadas invalidas para conector de salida del nodo origen {out_coords}")
            return
        in_coords = self.canvas.coords(target_node.input_connector)
        if not in_coords or len(in_coords) < 4:
            print(f"Error: Coordenadas invalidas para conector de entrada del nodo destino {in_coords}")
            return
            return
        out_x = (out_coords[0] + out_coords[2]) / 2
        out_y = (out_coords[1] + out_coords[3]) / 2
        in_x = (in_coords[0] + in_coords[2]) / 2
        in_y = (in_coords[1] + in_coords[3]) / 2
        
        connection_line = self.canvas.create_line(
            out_x, out_y, in_x, in_y,
            fill="#00FF88",
            width=3,
            tags="connection",
            arrow="last",
            arrowshape=(10, 12, 5)
        )
        
        # Enviar linea al fondo (pero encima de la cuadricula)
        self.canvas.tag_lower(connection_line)
        self.canvas.tag_raise(connection_line, "grid")
        
        # Eliminar linea temporal si existe
        if ConnectableNode._temp_line:
            self.canvas.delete(ConnectableNode._temp_line)
        
        # Registrar conexion de salida
        self.output_connections.append({
            "target": target_node,
            "line": connection_line,
            "option_index": option_index
        })
        
        # Registrar conexion de entrada en el nodo destino
        target_node.input_connections.append({
            "source": self,
            "line": connection_line,
            "option_index": option_index
        })
        
    def update_connections(self):
        '''
        Actualiza las posiciones de las lineas de conexion
        '''
        # Actualizar conexiones salientes
        for conn in self.output_connections:
            target = conn["target"] # Instancia del nodo destino
            line = conn["line"]     # ID de la linea de conexion
            
            out_coords = self.canvas.coords(self.output_connector[conn["option_index"]])
            in_coords = self.canvas.coords(target.input_connector)
            
            if out_coords and in_coords:
                # Ecuaciones para obtener el centro de los conectores
                out_x = (out_coords[0] + out_coords[2]) / 2
                out_y = (out_coords[1] + out_coords[3]) / 2
                in_x = (in_coords[0] + in_coords[2]) / 2
                in_y = (in_coords[1] + in_coords[3]) / 2
                
                self.canvas.coords(line, out_x, out_y, in_x, in_y)
    
    def _on_drag(self, event):
        '''
        Arrastrar el frame y actualizar conectores
        '''
        if not self.drag_data["dragging"]: 
            return
        
        self.set_position(
            event.x_root - self.drag_data["x"] + self.get_position()[0],
            event.y_root - self.drag_data["y"] + self.get_position()[1]
        )

        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
    
    def set_position(self, x, y):
        dx, dy = super().set_position(x, y)
    
        # Si es un nodo conectable, actualizar tambien los conectores
        if self.input_connector:
            self.canvas.move(self.input_connector, dx, dy)
        for connector in self.output_connector:
            self.canvas.move(connector, dx, dy)
        
        # Actualizar conexiones si existen
        if hasattr(self, 'update_connections'):
            self.update_connections()
            
        # Actualizar conexiones de otros nodos que apuntan a este
        if hasattr(self, 'input_connections'):
            for conn in self.input_connections:
                source_node = conn["source"]
                if hasattr(source_node, 'update_connections'):
                    source_node.update_connections()

        return dx, dy
    
    def set_character(self, character):
        '''
        Asigna un personaje a este nodo
        '''
        if character is None:
            print("No se proporciono ningun personaje para asignar")
            return
        # Guardar la referencia del objeto personaje
        self.character = character
        # Actualizar el titulo
        self.title_label.configure(text=character.name)
        self.title_bar.configure(fg_color=character.color)
        # Eliminar el '#' si existe
        hex_color = character.color.lstrip('#')
        # Convertir Hex a RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        # Formula de luminancia percibida
        brightness = (r * 0.2126   + g * 0.7152  + b * 0.0722 )
        # Si el brillo es mayor a 128 (la mitad de 255), el fondo es claro -> texto negro
        # Si es menor, el fondo es oscuro -> texto blanco
        self.title_label.configure(text_color=("#000000" if brightness > 128 else "#FFFFFF"))
        
        print(f"Personaje {character.name} asignado al nodo {self.node_id}")

    def show_context_menu(self, event):
        '''
        Muestra el menu contextual en la posicion del clic
        '''
        self.right_click_pos = (event.x, event.y)
        # Actualizar opciones del menu
        self.update_context_menu_items()
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def update_context_menu_items(self):
        '''
        Borra las opciones viejas y anyade las actuales
        '''
        # Borrar todo el contenido actual del menu
        
        self.context_menu.delete(0, "end")

        from panels.defs import characters # Importamos aqui por si cambio la lista

        if characters:
            for name, char_obj in characters.items():
                self.context_menu.add_command(
                    label=name,
                    command=lambda character=char_obj: self.set_character(character)
                )
        else:
            self.context_menu.add_command(label="No hay personajes disponibles", state="disabled")
  
    def create_context_menu(self):
        '''
        Crea el menu contextual con los tipos de nodos
        '''
        self.context_menu = Menu(self.canvas, tearoff=0, bg="#2b2b2b", fg="white", 
                                activebackground="#1f6aa5", activeforeground="white",
                                font=("Arial", 10))
        from panels.defs import  characters
        if characters:
            for name, char_obj in characters.items():
                self.context_menu.add_command(
                    label=name,
                    command=lambda character=char_obj: self.set_character(character)
                )
        else:
            self.context_menu.add_command(label="No hay personajes disponibles", state="disabled")

    def destroy(self):
        '''Limpia las conexiones antes de destruir el nodo'''
        try:
            # Verificar si el canvas todavia existe
            if self.canvas and self.canvas.winfo_exists():
                # Eliminar todas las conexiones salientes
                for conn in self.output_connections:
                    try:
                        self.canvas.delete(conn["line"])
                        # Limpiar referencia en el nodo destino
                        if conn["target"]:
                            conn["target"].input_connections = [
                                ic for ic in conn["target"].input_connections 
                                if ic["line"] != conn["line"]
                            ]
                    except:
                        pass
                
                # Eliminar conexiones entrantes
                for conn in self.input_connections:
                    try:
                        self.canvas.delete(conn["line"])
                        # Limpiar referencia en el nodo origen
                        if conn["source"]:
                            conn["source"].connections = [
                                c for c in conn["source"].connections 
                                if c["line"] != conn["line"]
                            ]
                    except:
                        pass
                
                # Eliminar conectores
                if self.input_connector:
                    try:
                        self.canvas.delete(self.input_connector)
                    except:
                        pass
                if self.output_connector:
                    for connector in self.output_connector:
                        try:
                            self.canvas.delete(connector)
                        except:
                            pass
            print("Node deleted")
        except:
            pass
        
        # Eliminar de la lista de nodos
        if self in ConnectableNode._all_nodes:
            ConnectableNode._all_nodes.remove(self)
        
        super().destroy()

class StartNode(ConnectableNode):
    '''    
    Nodo de inicio, solo tiene salida
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        super().__init__(canvas, x, y, width=150, height=100, title="Start", **kwargs)
        # Tipo de nodo
        self.type = "START"
    
    def setup_content(self):
        self.text = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=90,
            font=("Arial", 12),
            wrap="word"
        )
        self.text.pack(expand=True, pady=1)
    
    def create_connectors(self):
        '''
        Crea solo el conector de salida
        '''
        # Obtener posicion del frame
        x, y = self.get_position()
        frame_height = self.winfo_height()
        frame_width = self.winfo_width()
        
        # Solo conector de salida (derecha)
        output_x = x + frame_width
        output_y = y + frame_height // 2
        self.output_connector.append(self.canvas.create_oval(
            output_x - 2, output_y - 8,
            output_x + 10, output_y + 8,
            fill="#4CAF50",  # Verde para inicio
            outline="#ffffff",
            width=2,
            tags=("connector", "output", f"node_{id(self)}")
        ))
        
        # Eventos para el conector de salida
        self.canvas.tag_bind(self.output_connector, "<ButtonPress-1>", self.start_connection)
        self.canvas.tag_bind(self.output_connector, "<B1-Motion>", self.drag_connection)
        self.canvas.tag_bind(self.output_connector, "<ButtonRelease-1>", self.end_connection)

class EndNode(ConnectableNode):
    '''
    Nodo de fin, solo tiene entrada
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        # Establecer valores por defecto si no se proporcionan
        super().__init__(canvas, x, y, width=150, height=100, title="End", **kwargs)
        # Tipo de nodo
        self.type = "END"
    
    def setup_content(self):
        self.text = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=90,
            font=("Arial", 12),
            wrap="word"
        )
        self.text.pack(expand=True, pady=10)
    
    def create_connectors(self):
        '''
        Crea solo el conector de entrada
        '''
        # Obtener posicion del frame
        x, y = self.get_position()
        frame_height = self.winfo_height()
        
        # Solo conector de entrada (izquierda)
        input_y = y + frame_height // 2
        self.input_connector = self.canvas.create_oval(
            x - 10, input_y - 8,
            x + 2, input_y + 8,
            fill="#FF5252",  # Rojo para fin
            outline="#ffffff",
            width=2,
            tags=("connector", "input", f"node_{id(self)}")
        )

class DialogueNode (ConnectableNode):
    '''    
    Nodo de dialogo
    '''
    def __init__(self, canvas, x, y, **kwargs):
        super().__init__(canvas, x, y, width=200, height=150, title="Dialogue", **kwargs)
        # Tipo de nodo
        self.type = "DIALOGUE"
    
    def setup_content(self):
        self.text = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=140,
            font=("Arial", 12),
            wrap="word"
        )
        self.text.pack(expand=True, pady=1)

class DecisionNode(ConnectableNode):
    '''
    Nodo de decision con multiples opciones de salida
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        self.options = []  # Lista de opciones (cada una tiene texto y conector)
        self.option_connections = []  # Conexiones para cada opcion
        super().__init__(canvas, x, y, width=250, height=200, title="Decision", **kwargs)
        self.type = "DECISION"
    
    def setup_content(self):
        # Campo de pregunta
        question_label = ctk.CTkLabel(
            self.content_frame,
            text="Pregunta:",
            font=("Arial", 10, "bold")
        )
        question_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        self.question_text = ctk.CTkTextbox(
            self.content_frame,
            width=230,
            height=60,
            font=("Arial", 11),
            wrap="word"
        )
        self.question_text.pack(padx=5, pady=5)
        
        # Separador
        separator = ctk.CTkFrame(self.content_frame, height=2, fg_color="#444444")
        separator.pack(fill="x", padx=5, pady=5)
        
        # Label para opciones
        options_label = ctk.CTkLabel(
            self.content_frame,
            text="Opciones:",
            font=("Arial", 10, "bold")
        )
        options_label.pack(anchor="w", padx=5)
        
        # Frame scrollable para las opciones
        self.options_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            width=230,
            height=80,
            fg_color="transparent"
        )
        self.options_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Boton para anyadir opciones
        add_button = ctk.CTkButton(
            self.content_frame,
            text="+ Añadir Opcion",
            width=100,
            height=25,
            command=self.add_option,
            fg_color="#2196F3",
            hover_color="#1976D2"
        )
        add_button.pack(pady=5)
        
        # Anyadir dos opciones por defecto
        # Forzamos a que el sistema de layouts calcule posiciones YA
        self.update_idletasks() 
        self.add_option("Si")
        self.add_option("No")
    
    def add_option(self, default_text="", immediate=False):
        '''
        Anyade una nueva opcion con su campo de texto y conector de salida
        '''
        option_index = len(self.options)
        
        # Frame para cada opcion
        option_frame = ctk.CTkFrame(self.options_frame, fg_color="#2a2a2a", corner_radius=5)
        option_frame.pack(fill="x", pady=3)
        
        # Entry para el texto de la opcion
        option_entry = ctk.CTkEntry(
            option_frame,
            width=170,
            height=25,
            placeholder_text=f"Opcion {option_index + 1}"
        )
        option_entry.pack(side="left", padx=5, pady=5)
        
        if default_text:
            option_entry.insert(0, default_text)
        
        # Boton para eliminar esta opcion
        delete_btn = ctk.CTkButton(
            option_frame,
            text="✕",
            width=25,
            height=25,
            fg_color="#ff4d4d",
            hover_color="#ff1a1a",
            command=lambda: self.remove_option(option_index)
        )
        delete_btn.pack(side="right", padx=5)
        
        # Guardar la opcion
        option_data = {
            'frame': option_frame,
            'entry': option_entry,
            'connector': None,
            'connections': []
        }
        self.options.append(option_data)
        
        # Actualizar el tamanyo del nodo
        new_height = 200 + (len(self.options) * 35)
        self.configure(height=new_height)
        
        if immediate:
            # Forzamos a que el sistema de layouts calcule posiciones YA
            self.update_idletasks() 
            self.create_option_connector(option_index)
        else:
            # Crear el conector despues de un pequenyo delay
            self.after(100, lambda: self.create_option_connector(option_index))
    
    def remove_option(self, option_index):
        '''
        Elimina una opcion y su conector
        '''
        if option_index >= len(self.options):
            return
        
        option = self.options[option_index]
        # Filtramos: nos quedamos con las que NO pertenecen a este indice
        to_delete = [c for c in self.output_connections if c["option_index"] == option_index]
        # Eliminar conexiones asociadas
        for conn in to_delete:
            try:
                self.canvas.delete(conn["line"])
                # Limpiar referencia en el destino
                target = conn["target"]
                target.input_connections = [ic for ic in target.input_connections if ic["line"] != conn["line"]]
            except:
                pass
            self.output_connections.remove(conn)
        
        # Si borras la opcion 1, la conexion de la opcion 2 debe bajar al indice 1
        for conn in self.output_connections:
            if conn["option_index"] > option_index:
                conn["option_index"] -= 1

        # Eliminar conector visual
        if option['connector']:
            self.canvas.delete(option['connector'])
            if option['connector'] in self.output_connector:
                self.output_connector.remove(option['connector'])

        # Eliminar el frame visual
        option['frame'].destroy()        
        # Eliminar de la lista
        self.options.pop(option_index)
        
        # Actualizar altura
        new_height = 200 + (len(self.options) * 35)
        self.configure(height=new_height)
        
        # Recrear todos los conectores con las nuevas posiciones
        self.recreate_all_connectors()
    
    def create_option_connector(self, option_index):
        '''
        Crea el conector de salida para una opcion especifica
        '''
        if option_index >= len(self.options):
            return
        
        option = self.options[option_index]
        
        # Obtener posicion del nodo
        x, y = self.get_position()
        frame_width = self.winfo_width()
        
        # Calcular posicion Y basada en el indice de la opcion
        # Ajustar para que esten distribuidos verticalmente
        base_y = y + 120  # Posicion base despues de la pregunta
        connector_y = base_y + (option_index * 35) + 15
        
        # Crear conector a la derecha
        output_x = x + frame_width
        connector = self.canvas.create_oval(
            output_x - 2, connector_y - 6,
            output_x + 10, connector_y + 6,
            fill="#FFA726",  # Naranja para opciones
            outline="#ffffff",
            width=2,
            tags=("connector", "output", f"option_{option_index}", f"node_{id(self)}")
        )
        
        self.output_connector.append(connector)
        option['connector'] = connector
        
        # Eventos para el conector
        self.canvas.tag_bind(connector, "<ButtonPress-1>", 
                            lambda e, idx=option_index: self.start_connection(e, idx))
        self.canvas.tag_bind(connector, "<B1-Motion>", 
                            lambda e, idx=option_index: self.drag_connection(e))
        self.canvas.tag_bind(connector, "<ButtonRelease-1>", 
                            lambda e, idx=option_index: self.end_connection(e, idx))
    
    def recreate_all_connectors(self):
        '''
        Recrea todos los conectores de opciones con las posiciones actualizadas
        '''
        # Limpiar lista de conectores
        for connector_id in self.output_connector:
            try:
                self.canvas.delete(connector_id)
            except:
                pass
    
        self.output_connector.clear()
        
        for i, option in enumerate(self.options):
            if option['connector']:
                self.canvas.delete(option['connector'])
            self.create_option_connector(i)
            
        # Actualizar conexiones
        self.update_connections()
    
    def create_connectors(self):
        '''
        Crea el conector de entrada (las salidas se crean con las opciones)
        '''
        x, y = self.get_position()
        frame_height = self.winfo_height()
        
        # Conector de entrada (izquierda)
        input_y = y + 60  # Centrado con la pregunta
        self.input_connector = self.canvas.create_oval(
            x - 10, input_y - 8,
            x + 2, input_y + 8,
            fill="#4CAF50",
            outline="#ffffff",
            width=2,
            tags=("connector", "input", f"node_{id(self)}")
        )
        # Asegurar que output_connector este inicializado como lista vacia
        if not hasattr(self, 'output_connector') or not isinstance(self.output_connector, list):
            self.output_connector = []   
    
class ActionNode (ConnectableNode):
    '''    
    Nodo de accion
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        super().__init__(canvas, x, y, width=200, height=150, title="Action", **kwargs)
        # Tipo de nodo
        self.type = "ACTION"
    
    def setup_content(self):
        self.text = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=140,
            font=("Arial", 12),
            wrap="word"
        )
        self.text.pack(expand=True, pady=1)

class ConditionNode(ConnectableNode):
    '''
    Nodo que espera a que se cumpla una condicion antes de continuar.
    SIN TERMINAR, HAY QUE DARLE UNA VUELTA.
    '''
    
    # Tipos de condiciones disponibles
    CONDITION_TYPES = {
        "variable_equals": "Variable es igual a",
        "variable_greater": "Variable mayor que",
        "variable_less": "Variable menor que",
        "flag_true": "Bandera activada",
        "flag_false": "Bandera desactivada",
        "timer_elapsed": "Tiempo transcurrido",
        "custom": "Condicion personalizada"
    }
    
    def __init__(self, canvas, x, y, **kwargs):
        self.condition_type = "flag_true"  # Tipo de condicion por defecto
        self.condition_value = ""  # Valor de la condicion
        self.condition_target = ""  # Objetivo (nombre de variable, flag, etc.)
        
        super().__init__(canvas, x, y, width=280, height=220, title="Condition", **kwargs)
        self.type = "CONDITION"
    
    def setup_content(self):
        # Label de descripcion
        desc_label = ctk.CTkLabel(
            self.content_frame,
            text="Esperar hasta que:",
            font=("Arial", 10, "bold")
        )
        desc_label.pack(anchor="w", padx=5, pady=(5, 0))
        
        # Dropdown para tipo de condicion
        self.condition_type_var = ctk.StringVar(value="flag_true")
        self.condition_dropdown = ctk.CTkOptionMenu(
            self.content_frame,
            variable=self.condition_type_var,
            values=list(self.CONDITION_TYPES.values()),
            width=260,
            command=self.on_condition_type_changed
        )
        self.condition_dropdown.pack(padx=5, pady=5)
        
        # Frame para los campos de condicion
        self.condition_fields_frame = ctk.CTkFrame(
            self.content_frame,
            fg_color="transparent"
        )
        self.condition_fields_frame.pack(fill="x", padx=5, pady=5)
        
        # Campo para el objetivo (variable, flag, etc.)
        target_label = ctk.CTkLabel(
            self.condition_fields_frame,
            text="Nombre:",
            font=("Arial", 9)
        )
        target_label.pack(anchor="w", padx=2)
        
        self.target_entry = ctk.CTkEntry(
            self.condition_fields_frame,
            width=260,
            placeholder_text=""
        )
        self.target_entry.pack(padx=2, pady=2)
        
        # Frame para valor (se muestra/oculta segun el tipo)
        self.value_frame = ctk.CTkFrame(
            self.condition_fields_frame,
            fg_color="transparent"
        )
        
        value_label = ctk.CTkLabel(
            self.value_frame,
            text="Valor:",
            font=("Arial", 9)
        )
        value_label.pack(anchor="w", padx=2)
        
        self.value_entry = ctk.CTkEntry(
            self.value_frame,
            width=260,
            placeholder_text="ej: 100, true, sword"
        )
        self.value_entry.pack(padx=2, pady=2)
        
        # Mostrar/ocultar campo de valor segun tipo
        self.update_condition_fields()
        
        # Separador
        separator = ctk.CTkFrame(self.content_frame, height=2, fg_color="#444444")
        separator.pack(fill="x", padx=5, pady=5)
        
        # Label informativo
        info_label = ctk.CTkLabel(
            self.content_frame,
            text="El dialogo se pausara hasta que\nse cumpla esta condicion",
            font=("Arial", 8),
            text_color="#888888"
        )
        info_label.pack(pady=(0, 5))
    
    def on_condition_type_changed(self, selected_value):
        '''Actualiza los campos cuando cambia el tipo de condicion'''
        # Convertir el valor legible al codigo interno
        for key, value in self.CONDITION_TYPES.items():
            if value == selected_value:
                self.condition_type = key
                break
        
        self.update_condition_fields()
    
    def update_condition_fields(self):
        '''Muestra u oculta campos segun el tipo de condicion'''
        # Tipos que necesitan valor
        needs_value = ["variable_equals", "variable_greater", "variable_less",
                       "timer_elapsed", "custom"]
        
        if self.condition_type in needs_value:
            self.value_frame.pack(fill="x", pady=2)
        else:
            self.value_frame.pack_forget()
        
        # Actualizar placeholders segun tipo
        placeholders = {
            "variable_equals": ("nombre_variable", "valor_esperado"),
            "variable_greater": ("nombre_variable", "valor_minimo"),
            "variable_less": ("nombre_variable", "valor_maximo"),
            "flag_true": ("nombre_bandera", ""),
            "flag_false": ("nombre_bandera", ""),
            "timer_elapsed": ("nombre_timer", "segundos"),
            "custom": ("expresion_completa", "")
        }
        
        if self.condition_type in placeholders:
            target_ph, value_ph = placeholders[self.condition_type]
            self.target_entry.configure(placeholder_text=target_ph)
            if value_ph:
                self.value_entry.configure(placeholder_text=value_ph)
    
    def get_condition_data(self):
        '''Retorna los datos de la condicion para exportar'''
        return {
            "type": self.condition_type,
            "target": self.target_entry.get(),
            "value": self.value_entry.get() if self.condition_type in [
                "variable_equals", "variable_greater", "variable_less",
                "item_in_inventory", "timer_elapsed", "custom"
            ] else None
        }
    
    def set_condition_data(self, condition_data):
        '''Carga los datos de una condicion desde JSON'''
        self.condition_type = condition_data.get("type", "flag_true")
        
        # Actualizar dropdown
        readable_type = self.CONDITION_TYPES.get(self.condition_type, "Bandera activada")
        self.condition_type_var.set(readable_type)
        
        # Actualizar campos
        self.target_entry.delete(0, "end")
        self.target_entry.insert(0, condition_data.get("target", ""))
        
        if condition_data.get("value"):
            self.value_entry.delete(0, "end")
            self.value_entry.insert(0, condition_data.get("value", ""))
        
        self.update_condition_fields()
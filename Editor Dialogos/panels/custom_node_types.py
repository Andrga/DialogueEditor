import customtkinter as ctk
from tkinter import Canvas, Menu

class GridCanvas(ctk.CTkFrame):
    def __init__(self, master, grid_size=20, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_size = grid_size
        self.offset_x = 0
        self.offset_y = 0
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.draggingConnection = False
        
        # Canvas para la cuadricula y objetos
        self.canvas = Canvas(
            self,
            bg="#1a1a1a",
            highlightthickness=0
            #, cursor="fleur"
        )
        self.canvas.pack(fill="both", expand=True)

        # Lista de nodos en el canvas
        self.nodes = []
        
        self.node_types = {}
        
        # Bindeo de eventos
        self.canvas.bind("<ButtonPress-1>", self.on_canvas_press)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Button-3>", self.show_context_menu) # Evento de clic derecho para menu contextual

        # Crear menu contextual
        self.create_context_menu()
        # Dibujar cuadricula inicial
        self.draw_grid()
    
    def draw_grid(self):
        # Limpiar cuadricula anterior
        self.canvas.delete("grid")
        
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calcular offset normalizado
        offset_x = self.offset_x % self.grid_size
        offset_y = self.offset_y % self.grid_size
        
        # Lineas verticales
        for i in range(0, width + self.grid_size, self.grid_size):
            x = i + offset_x
            self.canvas.create_line(
                x, 0, x, height,
                fill="#2a2a2a",
                tags="grid"
            )
        
        # Lineas horizontales
        for i in range(0, height + self.grid_size, self.grid_size):
            y = i + offset_y
            self.canvas.create_line(
                0, y, width, y,
                fill="#2a2a2a",
                tags="grid"
            )
        
        # Enviar cuadricula al fondo
        self.canvas.tag_lower("grid")
    
    def on_canvas_press(self, event):
        # Cogemos los objetos en la posicion del clic
        items = self.canvas.find_overlapping(event.x-5, event.y-5, event.x+5, event.y+5)
        
        # De todos los objetos a los que se ha hecho clic, cuyo tag no sea "grid" o "draggable_frame"
        obj_items = [item for item in items if "grid" not in self.canvas.gettags(item) 
                        and "draggable_frame" not in self.canvas.gettags(item)]
        
        # Si no se ha hecho clic en ningun objeto, se ha hecho clic en el fondo
        if not obj_items:
            # Arrastrar el canvas
            self.drag_start_x = event.x
            self.drag_start_y = event.y
    
    def on_canvas_drag(self, event):
        #print("Canvas drag event, draggingConnection =", self.draggingConnection)
        # Si se esta arrastrando una conexion, no mover el canvas
        if self.draggingConnection:
            #print("Dragging connection, not moving canvas")
            return
        # Arrastrar el canvas
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y
        
        self.offset_x += dx
        self.offset_y += dy
        
        # Mover todos los elementos del canvas
        for node in self.nodes:
            if hasattr(node, 'canvas_window') and node.canvas_window:
                self.canvas.move(node.canvas_window, dx, dy)
                
                # Si es un nodo conectable, mover tambien sus conectores y actualizar conexiones
                if isinstance(node, ConnectableNode):
                    if node.input_connector:
                        self.canvas.move(node.input_connector, dx, dy)
                    if node.output_connector:
                        self.canvas.move(node.output_connector, dx, dy)
                    
                    # Actualizar todas las conexiones despues de mover todos los nodos
                    node.update_connections()
        
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        
        self.draw_grid()
    
    def on_resize(self, event):
        self.draw_grid()

    def show_context_menu(self, event):
        '''
        Muestra el menu contextual en la posicion del clic
        '''
        self.right_click_pos = (event.x, event.y)
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def create_context_menu(self):
        '''
        Crea el menu contextual con los tipos de nodos
        '''
        self.context_menu = Menu(self.canvas, tearoff=0, bg="#2b2b2b", fg="white", 
                                activebackground="#1f6aa5", activeforeground="white",
                                font=("Arial", 10))
        
        if self.node_types:
            for node_name, node_class in self.node_types.items():
                self.context_menu.add_command(
                    label=node_name,
                    command=lambda nc=node_class, nn=node_name: self.create_node_at_cursor(nc, nn)
                )
        else:
            self.context_menu.add_command(label="No hay tipos de nodos disponibles", state="disabled")

    def create_node_at_cursor(self, node_class, node_name):
        '''
        Crea un nodo en la posicion del clic derecho
        '''
        x, y = self.right_click_pos
        node = node_class(self, x, y)
        self.add_node(node)
    
    def register_node_type(self, name, node_class):
        '''
        Registra un nuevo tipo de nodo en el menu contextual
        '''
        self.node_types[name] = node_class
        # Recrear el menu contextual con el nuevo tipo
        self.context_menu.destroy()
        self.create_context_menu()

    def add_node(self, node=None):
        '''
        Anyade un nodo arrastrable al canvas
        '''
        if node is not None:
            self.nodes.append(node)
        return node
    
class nodeBase(ctk.CTkFrame):
    '''
    Clase base para frames arrastrables en el canvas
    '''
    _selected_node = None  # Nodo actualmente seleccionado (variable de clase)

    def __init__(self, canvas, x, y, width=150, height=100, title="Frame", **kwargs):
        super().__init__(canvas, width=width, height=height, corner_radius=10, **kwargs)
        
        self.canvas = canvas.canvas
        self.canvasGrid = canvas
        self.canvas_window = None
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        
        # Crear titulo
        self.title_bar = ctk.CTkFrame(self, fg_color="#1f6aa5", corner_radius=8, height=30)
        self.title_bar.pack(fill="x", padx=5, pady=(5, 0))
        self.title_bar.pack_propagate(False)
        
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text=title,
            font=("Arial", 12, "bold")
        )
        self.title_label.pack(side="left", padx=10, pady=5)
        delete_btn = ctk.CTkButton(
            self.title_bar,
            text="X",
            width=20,
            height=20,
            fg_color="#ff4d4d",
            hover_color="#ff1a1a",
            command=self.delete_node
        )
        delete_btn.pack(side="right", padx=5, pady=5)
        
        # Contenedor para el contenido personalizado
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar eventos de arrastre
        self.title_bar.bind("<ButtonPress-1>", self._on_press)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self._on_release)
        self.title_label.bind("<ButtonPress-1>", self._on_press)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<ButtonRelease-1>", self._on_release)
        self.title_label.bind("<BackSpace>", self.delete_node)
        
        # Anyadir al canvas
        self.canvas_window = self.canvas.create_window(x, y, window=self, anchor="nw", tags="draggable_frame")
        
        # Llamar al metodo de inicializacion del contenido
        self.setup_content()
    
    def setup_content(self):
        '''
        Metodo para sobrescribir en clases hijas con el contenido personalizado
        '''

        # Contenido por defecto
        label = ctk.CTkLabel(
            self.content_frame,
            text="Frame arrastrable\nSobrescribe setup_content()"
        )
        label.pack(expand=True, pady=10)
    
    def _on_press(self, event):
        '''
        Iniciar arrastre
        '''

        self.drag_data["dragging"] = True
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.title_bar.configure(cursor="fleur")
        self.title_label.configure(cursor="fleur")
        # Seleccionar el nodo al hacer clic en la barra de título
        self.select()

    def _on_select(self, event):
        """Seleccionar este nodo"""
        self.select()
    
    def select(self):
        """Marca este nodo como seleccionado"""
        # Deseleccionar el nodo anterior
        if nodeBase._selected_node and nodeBase._selected_node != self:
            nodeBase._selected_node.deselect()
        
        self.is_selected = True
        nodeBase._selected_node = self
        self.configure(border_width=3, border_color="#FFD700")  # Borde dorado
    
    def deselect(self):
        """Desmarca este nodo como seleccionado"""
        self.is_selected = False
        self.configure(border_width=0)
    
    def delete_node(self):
        """Elimina este nodo del canvas"""
        print("Deleting node")
        # Eliminar de la lista de nodos del canvas
        if self in self.canvasGrid.nodes:
            self.canvasGrid.nodes.remove(self)
        
        # Si este nodo estaba seleccionado, limpiar la selección
        if nodeBase._selected_node == self:
            nodeBase._selected_node = None
        
        # Destruir el nodo (esto llamará al método destroy personalizado si existe)
        self.destroy()
    
    def _on_delete_key(self, event):
        """Elimina el nodo seleccionado cuando se presiona Delete/Backspace"""
        if nodeBase._selected_node:
            nodeBase._selected_node.delete_node()
    
    def _on_drag(self, event):
        '''
        Arrastrar el frame
        '''

        if self.drag_data["dragging"]:
            dx = event.x_root - self.drag_data["x"]
            dy = event.y_root - self.drag_data["y"]
            self.canvas.move(self.canvas_window, dx, dy)
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root
    
    def _on_release(self, event):
        '''
        Finalizar arrastre
        '''

        self.drag_data["dragging"] = False
        self.title_bar.configure(cursor="")
        self.title_label.configure(cursor="")
    
    def get_position(self):
        '''
        Obtener posicion actual del frame
        '''

        coords = self.canvas.coords(self.canvas_window)
        return coords[0], coords[1] if coords else (0, 0)
    
    def set_position(self, x, y):
        '''
        Establecer posicion del frame
        '''
        current_x, current_y = self.get_position()
        dx = x - current_x
        dy = y - current_y
        self.canvas.move(self.canvas_window, dx, dy)
        
        # Si es un nodo conectable, actualizar también los conectores
        if hasattr(self, 'input_connector') and self.input_connector:
            self.canvas.move(self.input_connector, dx, dy)
        if hasattr(self, 'output_connector') and self.output_connector:
            self.canvas.move(self.output_connector, dx, dy)
        
        # Actualizar conexiones si existen
        if hasattr(self, 'update_connections'):
            self.update_connections()
            
        # Actualizar conexiones de otros nodos que apuntan a este
        if hasattr(self, '__class__') and hasattr(self.__class__, '_all_nodes'):
            for node in self.__class__._all_nodes:
                if node != self and hasattr(node, 'connections'):
                    for conn in node.connections:
                        if conn.get("target") == self:
                            node.update_connections()

class NodeFrame(nodeBase):
    '''
    Frame de nodo con entradas y salidas
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        super().__init__(canvas, x, y, width=180, height=150, title="Nodo", **kwargs)
    
    def setup_content(self):
        # Input
        input_label = ctk.CTkLabel(self.content_frame, text="Input:", anchor="w")
        input_label.pack(fill="x", padx=10, pady=(5, 0))
        
        self.input_entry = ctk.CTkEntry(self.content_frame, placeholder_text="Valor de entrada")
        self.input_entry.pack(fill="x", padx=10, pady=5)
        
        # Button
        process_btn = ctk.CTkButton(
            self.content_frame,
            command=self.process,
            height=3,width=3
        )
        process_btn.pack(padx=10, pady=5)
        
        # Output
        self.output_label = ctk.CTkLabel(
            self.content_frame,
            text="Output: -",
            anchor="w"
        )
        self.output_label.pack(fill="x", padx=10, pady=5)
    
    def process(self):
        value = self.input_entry.get()
        self.output_label.configure(text=f"Output: {value.upper()}")

class ConnectableNode(nodeBase):
    '''
    Nodo con conectores de entrada y salida
    '''
    # Variable de clase para rastrear conexiones
    _active_connector = None
    _temp_line = None
    _all_nodes = []
    
    def __init__(self, canvas, x, y, width=200, height=120, title="Nodo Conectable", **kwargs):
        self.input_connector = None
        self.output_connector = None
        self.connections = []  # Lista de conexiones desde este nodo
        self.input_connections = []  # Conexiones entrantes
        
        super().__init__(canvas, x, y, width=width, height=height, title=title, **kwargs)
        
        # Registrar este nodo
        ConnectableNode._all_nodes.append(self)
        
        # Crear conectores después de que el frame esté en el canvas
        self.after(100, self.create_connectors)
    
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
        self.output_connector = self.canvas.create_oval(
            output_x - 2, output_y - 8,
            output_x + 10, output_y + 8,
            fill="#2196F3",
            outline="#ffffff",
            width=2,
            tags=("connector", "output", f"node_{id(self)}")
        )
        
        # Eventos para el conector de salida (inicio de conexion)
        self.canvas.tag_bind(self.output_connector, "<ButtonPress-1>", self.start_connection)
        self.canvas.tag_bind(self.output_connector, "<B1-Motion>", self.drag_connection)
        self.canvas.tag_bind(self.output_connector, "<ButtonRelease-1>", self.end_connection)
        
        # Eventos para el conector de entrada (finalizar conexion)
        self.canvas.tag_bind(self.input_connector, "<ButtonRelease-1>", self.receive_connection)
    
    def start_connection(self, event):
        '''
        Inicia una nueva conexion desde el conector de salida
        '''
        #print("Starting connection")
        # Indicar que se esta arrastrando una conexion
        self.canvasGrid.draggingConnection = True
        ConnectableNode._active_connector = self
        
        # Obtener posicion del conector de salida
        coords = self.canvas.coords(self.output_connector)
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
        self.canvasGrid.draggingConnection = True
        if ConnectableNode._temp_line:
            coords = self.canvas.coords(ConnectableNode._temp_line)
            self.canvas.coords(ConnectableNode._temp_line, coords[0], coords[1], event.x, event.y)
    
    def end_connection(self, event):
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
                            self.connect_to(node)
                            connected = True
                            break
                    break
            
            # Si no se conecto, eliminar linea temporal
            if not connected:
                self.canvas.delete(ConnectableNode._temp_line)
            
            ConnectableNode._temp_line = None
            ConnectableNode._active_connector = None 
    
    def receive_connection(self, event):
        '''
        Recibe una conexion en el conector de entrada
        '''
        if ConnectableNode._active_connector and ConnectableNode._active_connector != self:
            ConnectableNode._active_connector.connect_to(self)
    
    def connect_to(self, target_node):
        """Conecta este nodo con otro nodo"""
        # Eliminar conexión anterior desde este nodo (solo una salida permitida)
        if self.connections:
            for conn in self.connections:
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
            self.connections.clear()
        
        # Crear línea de conexión permanente
        out_coords = self.canvas.coords(self.output_connector)
        in_coords = self.canvas.coords(target_node.input_connector)
        
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
        
        # Enviar línea al fondo (pero encima de la cuadrícula)
        self.canvas.tag_lower(connection_line)
        self.canvas.tag_raise(connection_line, "grid")
        
        # Eliminar línea temporal si existe
        if ConnectableNode._temp_line:
            self.canvas.delete(ConnectableNode._temp_line)
        
        # Registrar conexión de salida
        self.connections.append({
            "target": target_node,
            "line": connection_line
        })
        
        # Registrar conexión de entrada en el nodo destino
        target_node.input_connections.append({
            "source": self,
            "line": connection_line
        })
    
    def update_connections(self):
        '''
        Actualiza las posiciones de las lineas de conexion
        '''
        # Actualizar conexiones salientes
        for conn in self.connections:
            target = conn["target"]
            line = conn["line"]
            
            out_coords = self.canvas.coords(self.output_connector)
            in_coords = self.canvas.coords(target.input_connector)
            
            if out_coords and in_coords:
                out_x = (out_coords[0] + out_coords[2]) / 2
                out_y = (out_coords[1] + out_coords[3]) / 2
                in_x = (in_coords[0] + in_coords[2]) / 2
                in_y = (in_coords[1] + in_coords[3]) / 2
                
                self.canvas.coords(line, out_x, out_y, in_x, in_y)
    
    def _on_drag(self, event):
        '''
        Arrastrar el frame y actualizar conectores
        '''
        if self.drag_data["dragging"]:
            dx = event.x_root - self.drag_data["x"]
            dy = event.y_root - self.drag_data["y"]
            
            # Mover el frame
            self.canvas.move(self.canvas_window, dx, dy)
            
            # Mover conectores
            self.canvas.move(self.input_connector, dx, dy)
            self.canvas.move(self.output_connector, dx, dy)
            
            # Actualizar mis conexiones
            self.update_connections()
            
            # Actualizar conexiones de otros nodos que apuntan a mi
            for node in ConnectableNode._all_nodes:
                if node != self:
                    for conn in node.connections:
                        if conn["target"] == self:
                            node.update_connections()
            
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root
    
    def destroy(self):
        """Limpia las conexiones antes de destruir el nodo"""
        try:
            # Verificar si el canvas todavía existe
            if self.canvas and self.canvas.winfo_exists():
                # Eliminar todas las conexiones salientes
                for conn in self.connections:
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
                    try:
                        self.canvas.delete(self.output_connector)
                    except:
                        pass
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
    
    def setup_content(self):
        label = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=90,
            font=("Arial", 12),
            wrap="word"
        )
        label.pack(expand=True, pady=1)
    
    def create_connectors(self):
        '''
        Crea solo el conector de salida
        '''
        # Obtener posición del frame
        x, y = self.get_position()
        frame_height = self.winfo_height()
        frame_width = self.winfo_width()
        
        # Solo conector de salida (derecha)
        output_x = x + frame_width
        output_y = y + frame_height // 2
        self.output_connector = self.canvas.create_oval(
            output_x - 2, output_y - 8,
            output_x + 10, output_y + 8,
            fill="#4CAF50",  # Verde para inicio
            outline="#ffffff",
            width=2,
            tags=("connector", "output", f"node_{id(self)}")
        )
        
        # Eventos para el conector de salida
        self.canvas.tag_bind(self.output_connector, "<ButtonPress-1>", self.start_connection)
        self.canvas.tag_bind(self.output_connector, "<B1-Motion>", self.drag_connection)
        self.canvas.tag_bind(self.output_connector, "<ButtonRelease-1>", self.end_connection)
        
        # No crear input_connector (permanece None)
    
    def _on_drag(self, event):
        '''
        Arrastrar el frame y actualizar conector de salida
        '''
        if self.drag_data["dragging"]:
            dx = event.x_root - self.drag_data["x"]
            dy = event.y_root - self.drag_data["y"]
            
            # Mover el frame
            self.canvas.move(self.canvas_window, dx, dy)
            
            # Mover solo el conector de salida
            if self.output_connector:
                self.canvas.move(self.output_connector, dx, dy)
            
            # Actualizar mis conexiones
            self.update_connections()
            
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root


class EndNode(ConnectableNode):
    '''
    Nodo de fin, solo tiene entrada
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        # Establecer valores por defecto si no se proporcionan
        super().__init__(canvas, x, y, width=150, height=100, title="End", **kwargs)
    
    def setup_content(self):
        label = ctk.CTkTextbox(
            self.content_frame,
            width=140,
            height=80,
            font=("Arial", 12),
            wrap="word"
        )
        label.pack(expand=True, pady=10)
    
    def create_connectors(self):
        '''
        Crea solo el conector de entrada
        '''
        # Obtener posición del frame
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
        
        # Eventos para el conector de entrada
        self.canvas.tag_bind(self.input_connector, "<ButtonRelease-1>", self.receive_connection)
        
        # No crear output_connector (permanece None)
    
    def _on_drag(self, event):
        '''
        Arrastrar el frame y actualizar conector de entrada
        '''
        if self.drag_data["dragging"]:
            dx = event.x_root - self.drag_data["x"]
            dy = event.y_root - self.drag_data["y"]
            
            # Mover el frame
            self.canvas.move(self.canvas_window, dx, dy)
            
            # Mover solo el conector de entrada
            if self.input_connector:
                self.canvas.move(self.input_connector, dx, dy)
            
            # Actualizar conexiones de otros nodos que apuntan a mí
            for node in ConnectableNode._all_nodes:
                if node != self:
                    for conn in node.connections:
                        if conn["target"] == self:
                            node.update_connections()
            
            self.drag_data["x"] = event.x_root
            self.drag_data["y"] = event.y_root

class DialogueNode (ConnectableNode):
    '''    
    Nodo de dialogo
    '''
    
    def __init__(self, canvas, x, y, **kwargs):
        super().__init__(canvas, x, y, width=200, height=150, title="Start", **kwargs)
    
    def setup_content(self):
        label = ctk.CTkTextbox(
            self.content_frame,
            width=200,
            height=140,
            font=("Arial", 12),
            wrap="word"
        )
        label.pack(expand=True, pady=1)
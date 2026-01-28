# Variable global que almacena personajes
characters = {}

class character:
    def __init__(self, name="Character", color="#ffffff", font="", 
    sounds=None):
        self.name = name
        self.color = color
        self.font = font
        self.sounds =  sounds if sounds is not None else {}

import csv
from tkinter import Canvas, Menu
import customtkinter as ctk

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
                #self.canvas.move(node.canvas_window, dx, dy)
                ndx = node.get_position()[0] + dx
                ndy = node.get_position()[1] + dy
                node.set_position(ndx, ndy) # Actualizar posicion interna del nodo
        
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
    
    def clear_canvas(self):
        '''
        Limpia todos los nodos del canvas
        '''
        # Eliminar todos los nodos uno por uno
        while len(self.nodes) > 0:
            self.nodes[0].delete_node()

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
        # Frame de la barra de titulo
        self.title_bar = ctk.CTkFrame(self, fg_color="#1f6aa5", corner_radius=8, height=30)
        self.title_bar.pack(fill="x", padx=5, pady=(5, 0))
        self.title_bar.pack_propagate(False)
        # Label de titulo
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text=title,
            font=("Arial", 12, "bold")
        )
        self.title_label.pack(side="left", padx=10, pady=5)
        # Boton de eliminar
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
        
        # Configurar eventos
        self.title_bar.bind("<ButtonPress-1>", self._on_press)
        self.title_bar.bind("<B1-Motion>", self._on_drag)
        self.title_bar.bind("<ButtonRelease-1>", self._on_release)
        self.title_label.bind("<ButtonPress-1>", self._on_press)
        self.title_label.bind("<B1-Motion>", self._on_drag)
        self.title_label.bind("<ButtonRelease-1>", self._on_release)
        self.title_label.bind("<BackSpace>", self.delete_node)
        
        # Anyadir al canvas
        self.canvas_window = self.canvas.create_window(0, 0, window=self, anchor="nw", tags="draggable_frame")
        # Establecer posicion inicial
        self.set_position(x, y)        
        # Llamar al metodo de inicializacion del contenido
        self.setup_content()
    
    def setup_content(self):
        '''
        Metodo para sobrescribir en clases hijas con el contenido personalizado
        '''
        # Contenido por defecto
        label = ctk.CTkLabel(
            self.content_frame,
            text="Sobrescribir setup_content()"
        )
        label.pack(expand=True, pady=10)
    
    def _on_press(self, event):
        '''
        Iniciar arrastre
        '''
        self.drag_data["dragging"] = True
        self.drag_data["x"] = event.x_root
        self.drag_data["y"] = event.y_root
        self.title_bar.configure(cursor="fleur")    # tipo de cursor
        self.title_label.configure(cursor="fleur")  # tipo de cursor

        ## Seleccionar el nodo al hacer clic en la barra de titulo
        # Deseleccionar el nodo anterior
        if nodeBase._selected_node and nodeBase._selected_node != self:
            nodeBase._selected_node.deselect()
        
        self.is_selected = True
        nodeBase._selected_node = self
        self.configure(border_width=3, border_color="#FFD700")  # Borde dorado
    
    def deselect(self):
        '''
        Desmarca este nodo como seleccionado
        '''
        self.is_selected = False
        self.configure(border_width=0)
    
    def delete_node(self):
        '''
        Elimina este nodo del canvas
        '''
        print("Deleting node")
        # Eliminar de la lista de nodos del canvas
        if self in self.canvasGrid.nodes:
            self.canvasGrid.nodes.remove(self)
        
        # Si este nodo estaba seleccionado, limpiar la seleccion
        if nodeBase._selected_node == self:
            nodeBase._selected_node = None

        # Destruir el nodo (esto llamara al metodo destroy personalizado si existe)
        self.destroy()

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
        return dx, dy

class TranslationTable:
    def __init__(self):
        self.languages = ["español"]
        self.translations = {}

    # ----- Idiomas -----
    def add_language(self, lang):
        if lang not in self.languages:
            self.languages.append(lang)
            for key in self.translations:
                self.translations[key][lang] = ""

    def remove_language(self, lang):
        if lang in self.languages:
            self.languages.remove(lang)
            for key in self.translations:
                self.translations[key].pop(lang, None)

    # ----- Claves -----
    def add_key(self, key):
        if key not in self.translations:
            self.translations[key] = {l: "" for l in self.languages}

    def remove_key(self, key):
        self.translations.pop(key, None)

    # ----- Traducciones -----
    def set(self, key, lang, text):
        self.translations[key][lang] = text

    def get(self, key, lang):
        return self.translations.get(key, {}).get(lang, "")

    # ----- CSV -----
    def export_csv(self, path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["KEY"] + self.languages)
            for key, values in self.translations.items():
                writer.writerow([key] + [values[l] for l in self.languages])

    def import_csv(self, path):
        with open(path, encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.languages = header[1:]
            self.translations = {
                row[0]: {self.languages[i]: row[i+1] if i+1 < len(row) else ""
                         for i in range(len(self.languages))}
                for row in reader
            }
import customtkinter as ctk
from customtkinter import CTkFrame, CTkButton, CTkLabel
from tknodesystem import NodeCanvas, NodeValue, NodeOperation, NodeCompile, NodeMenu



class NodeEditorFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        # Columna 0: Panel Izquierdo
        # Columna 1: Canvas Central (Weight 1 hace que se expanda para ocupar espacio libre)
        # Columna 2: Panel Derecho
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # Fila 1 es el contenido principal

        # --- Fila 0: Barra de Herramientas (Toolbar) ---
        self.toolbar = CTkFrame(self, height=40, corner_radius=0)
        self.toolbar.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Botones para alternar paneles
        self.btn_toggle_left = CTkButton(self.toolbar, text="Panel Izquierdo", width=100, command=self.toggle_left_panel)
        self.btn_toggle_left.pack(side="left", padx=10, pady=5)

        self.btn_toggle_right = CTkButton(self.toolbar, text="Panel Derecho", width=100, command=self.toggle_right_panel)
        self.btn_toggle_right.pack(side="right", padx=10, pady=5)

        self._create_left_panel()
        self._create_right_panel()
        self._create_canvas()

        # Mostramos todo al principio
        self.left_panel.grid(row=1, column=0, sticky="nsew")
        self.canvas_container.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid(row=1, column=2, sticky="nsew")

        # Variables de estado
        self.left_visible = True
        self.right_visible = True

    def _create_canvas(self):
        '''
        Metodo para crear el canvas con nodos
        copiado de la documentacion ofical:
            https://github.com/Akascape/TkNodeSystem/wiki/Usage
        '''
        # Lo metemos en un frame contenedor para asegurar que el grid funcione limpio
        self.canvas_container = CTkFrame(self, corner_radius=0)
        self.canvas = NodeCanvas(self.canvas_container, bg="black")
        self.canvas.pack(fill="both", expand=True)
        
        # Nodos default ?
        NodeValue(self.canvas, x=50, y=50)
        NodeOperation(self.canvas, x=250, y=50)
        NodeCompile(self.canvas, x=450, y=50)

        # Menu contextual para nodos a crear
        menu = NodeMenu(self.canvas)
        menu.add_node(label="NodeValue", command=lambda: NodeValue(self.canvas))
        menu.add_node(label="NodeOperation", command=lambda: NodeOperation(self.canvas))
        menu.add_node(label="NodeCompile", command=lambda: NodeCompile(self.canvas))

    def _create_left_panel(self):
        '''
        Metodo para crear un panel izquierdo (Diferentes conversaciones?)
        '''
        self.left_panel = CTkFrame(self, width=1000, corner_radius=0, fg_color="#2b2b2b")
        # Esto evita que se encoja si esta vacio
        self.left_panel.grid_propagate(False)
        
        # --- CONTENIDO ---
        lbl_left = CTkLabel(self.left_panel, text="Conversaciones")
        lbl_left.pack(pady=10)
    
    def _create_right_panel(self):
        '''
        Metodo para crear el panel derecho (Editor del nodo?)
        '''
        self.right_panel = CTkFrame(self, width=1000, corner_radius=0, fg_color="#2b2b2b")
        # Esto evita que se encoja si esta vacio
        self.right_panel.grid_propagate(False)
        
        # --- CONTENIDO ---
        lbl_right = CTkLabel(self.right_panel, text="Editor del nodo")
        lbl_right.pack(pady=10)


    def toggle_left_panel(self):
        if self.left_visible:
            self.left_panel.grid_remove() # grid_remove oculta pero recuerda la posicion
        else:
            self.left_panel.grid() # grid() restaura la posicion
        self.left_visible = not self.left_visible

    def toggle_right_panel(self):
        if self.right_visible:
            self.right_panel.grid_remove()
        else:
            self.right_panel.grid()
        self.right_visible = not self.right_visible


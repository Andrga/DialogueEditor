import tkinter as ttk
import customtkinter as ctk
from customtkinter import CTkFrame
from panels.custom_node_types import StartNode, EndNode, DialogueNode, DecisionNode, ActionNode, ConditionNode
from panels.defs import GridCanvas


class NodeEditorFrame(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        # Creamos el canvas de nodos
        self._create_canvas()
        self.canvas_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def _create_canvas(self):
        '''
        Metodo para crear el canvas con nodos
        '''
        # Usamos canvas personalizado
        self.canvas_container = GridCanvas(self, grid_size=50)
        
        # Menu contextual para nodos a crear
        #self.canvas_container.register_node_type("ConnectableNode", ConnectableNode)
        self.canvas_container.register_node_type("StartNode", StartNode)
        self.canvas_container.register_node_type("EndNode", EndNode)
        self.canvas_container.register_node_type("DialogueNode", DialogueNode)
        self.canvas_container.register_node_type("DecisionNode", DecisionNode)
        self.canvas_container.register_node_type("ConditionNode", ConditionNode)
        self.canvas_container.register_node_type("ActionNode", ActionNode)

        # Nodos default ?
        startNode = StartNode(self.canvas_container, 0, 0)
        self.canvas_container.add_node(startNode)
        startNode.set_position(100, 100)
        endNode = EndNode(self.canvas_container, 0, 0)
        self.canvas_container.add_node(endNode)
        endNode.set_position(1000, 100)
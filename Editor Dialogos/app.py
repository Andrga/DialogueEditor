# Interfaces graficas
import tkinter as ttk
from tkinter import *
import customtkinter as ctk
from panels.nodeEditor import NodeEditorFrame
from panels.charactersEditor import CharacterEditorFrame
from CTkMenuBarPlus import CTkMenuBar, CustomDropdownMenu
import ctypes
import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox
from panels.defs import Digraph

# Este codigo le dice a Windows que trate este script como una aplicacion independiente
try:
    myappid = 'dialogue_editor.alcanciles_con_miopia' # Da igual lo que ponga, es un id propio
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception as e:
    print(f"No se pudo configurar el ID de la barra de tareas: {e}")

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

        # Ruta del icono
        icon_path = os.path.join(os.path.dirname(__file__), "images", "icon.ico")
        if os.path.exists(icon_path):
            # Icono de la ventana
            self.iconbitmap(icon_path)
            # Icono para la barra de tareas y el selector Alt+Tab
            # A veces iconbitmap no es suficiente para CustomTkinter
            img = PhotoImage(file=icon_path.replace(".ico", ".png"))
            # Fuerza el icono:
            self.iconphoto(False, img)
        else:
            print(f"No se encontro el icono en {icon_path}")

        self.active_nodes = []

    def notify_character_change(self):
        '''
        Avisa a todos los nodos registrados que actualicen su lista de personajes
        '''
        print("Notificando que se ha creado un personaje")
        for node in self.active_nodes:
            # Verificamos que el nodo aun exista y tenga el metodo
            if hasattr(node, 'refresh_character_options'):
                node.refresh_character_options()

    def run(self):
        self._set_ui()

        # Pestanyas
        self.tabview = ctk.CTkTabview(master=self, command=self._on_tab_changed)
        self.tabview.pack(fill='both', expand=True)
        # Editor de nodos
        self.nodesTab = self.tabview.add("Editor de nodos")
        nodeEditorFrame = NodeEditorFrame(master=self.nodesTab)
        nodeEditorFrame.pack(fill='both', expand=True)
        # Editor de personajes
        self.charactersTab = self.tabview.add("Editor de personajes")
        characterEditorFrame = CharacterEditorFrame(master=self.charactersTab)
        characterEditorFrame.pack(fill='both', expand=True)
        # Editor de parametros extra (Ej: Botones de UI, imagenes con texto...)
        self.parametersTab = self.tabview.add("Parametros de juego")

        self.mainloop()

    def _set_ui(self):
        menu_bar = CTkMenuBar(self)
        menu_bar.pack(fill="x", side=TOP)

        # --- MENU ARCHIVOS ---
        file_btn = menu_bar.add_cascade("Archivo")
        # Menu desplegable
        file_dropdown = CustomDropdownMenu(widget=file_btn)
        file_dropdown.add_option("Nuevo", command=lambda: print("Nuevo"))
        file_dropdown.add_option("Abrir", command=lambda:self.load_project("mi_dialogo"))
        file_dropdown.add_separator()
        file_dropdown.add_option("Guardar Dialogos", command=lambda:self.save_project("mi_dialogo"))
   

        # --- MENU EDITAR ---
        edit_btn = menu_bar.add_cascade("Editar")
        edit_dropdown = CustomDropdownMenu(widget=edit_btn)
        edit_dropdown.add_option("Cortar")
        edit_dropdown.add_option("Pegar")
        edit_dropdown.add_separator()
        edit_dropdown.add_option("Configuracion")
        menu = ttk.Menu(self)
        self.config(menu=menu)
        # --- MENU VER ---
        see_btn = menu_bar.add_cascade("Ver")
        see_dropdown = CustomDropdownMenu(widget=see_btn)
        see_dropdown.add_option("Panel Izquierdo", checkable=True, command=lambda: print("Ver Panel Izquierdo"))
        see_dropdown.add_option("Panel Derecho", checkable=True, command=lambda: print("Ver Panel Derecho"))
    
    def _on_tab_changed(self):
        '''
        Al cambiar de pestanya, quitamos el foco del teclado de cualquier sitio
        '''
        # Esto obliga a que el canvas pierda el control del teclado (NO FUNCIONA)
        # hasta que el usuario vuelva a hacer clic fisicamente en el.
        self.focus_set() 
        print(f"Cambiado a pestaña: {self.tabview.get()}")


    def choose_save_directory(self):
        '''
        Abre un cuadro de dialogo para elegir un directorio
        '''
        directory = filedialog.askdirectory(
            title="Seleccionar carpeta para guardar",
            initialdir="."
        )

        if directory:
            print(f"Carpeta seleccionada: {directory}")
            return directory

        return None

    # ===================================
    # SERIALIZACION
    # ===================================
    
    def save_project(self, filename="dialogue_project"):
        directory = self.choose_save_directory()
        if not directory: # Si cancela, salimos
            return

        try:
            # Serializar personajes
            characters_data = self._serialize_characters()
            characters_path = os.path.join(directory, f"{filename}_characters.json")
            with open(characters_path, 'w', encoding='utf-8') as f:
                json.dump(characters_data, f, ensure_ascii=False, indent=2)

            # Serializar dialogos
            dialogues_data = self._serialize_dialogues()
            dialogues_path = os.path.join(directory, f"{filename}_dialogues.json")
            with open(dialogues_path, 'w', encoding='utf-8') as f:
                json.dump(dialogues_data, f, ensure_ascii=False, indent=2)

            messagebox.showinfo("Exito", f"Proyecto guardado correctamente en:\n{directory}")

        except Exception as e:
            print(f"Error critico al guardar: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")

    def _serialize_characters(self):
        '''
        Convierte los personajes en un diccionario para exportar
        '''
        from panels.defs import characters

        serialized_chars = []
        # Recorremos todos los personajes
        for name, obj in characters.items():
            char = {
                "name": name,
                "font":obj.font or "default_font",
                "sounds":{
                    "neutral": [],
                    "happy": [],
                    "sad": [],
                    "angry": [],
                    "surprised": [],
                    "suspicious": []
                },
                "Color": obj.color
            }

            serialized_chars.append(char)
        
        return {
        "characters": serialized_chars,
        "lastModified": datetime.now().isoformat()
            }

    def _serialize_dialogues(self):
        try:
            node_editor_frame = self.nodesTab.children['!nodeeditorframe']
            canvas = node_editor_frame.canvas
        except (KeyError, AttributeError):
            return {"Dialogues": [], "LastModified": datetime.now().isoformat()}

        # Cogemos la info
        nodes = list(canvas.obj_list)
        line_list = list(canvas.line_list)
        socket_to_node = {}
        nodes_by_id = {} # Diccionario [id_nodo] objeto_nodo

        for node in nodes:
            node_id = id(node)
            nodes_by_id[node_id] = node

            # Registrar sockets de entrada
            if hasattr(node, 'input_1'):
                socket_to_node[node.input_1.socket_num] = node
            # Registrar sockets de salida (normales y de decision)
            if hasattr(node, 'output_') and node.output_:
                socket_to_node[node.output_.socket_num] = node
            if hasattr(node, 'outputs'):
                for out in node.outputs:
                    socket_to_node[out.socket_num] = node

        # CONSTRUCCION DEL GRAFO
        grafo = Digraph()
        for out_id, in_id in line_list:
            n_origen = socket_to_node.get(out_id)
            n_destino = socket_to_node.get(in_id)
            if n_origen and n_destino:
                grafo.add_edge(id(n_origen), id(n_destino))

        # VALIDACION DE CICLOS
        if grafo.check_cycles():
            messagebox.showerror("Error de Logica", 
                "Se ha detectado un bucle infinito. El dialogo no puede exportarse asi.")
            return None

        # RECORRIDO Y CONSTRUCCION DE JSON
        dialogues_output = []
        start_nodes = [n for n in nodes if getattr(n, 'type', '') == "START"]



        for start_idx, start_node in enumerate(start_nodes):
            dialogue_entry = {"DialogueID": start_idx, "Texts": []}
            visited = set()

            # Usamos DFS simple para recolectar los textos del camino
            stack = [start_node]
            while stack:
                current = stack.pop()
                curr_ptr = id(current)

                if curr_ptr in visited: continue
                visited.add(curr_ptr)

                # Procesar el nodo segun su tipo
                n_type = getattr(current, 'type', 'Unknown')
                if n_type == "DIALOGO":
                    dialogue_entry["Texts"].append(self._create_text_entry(current))
                elif n_type == "DECISION":
                    dialogue_entry["Texts"].extend(self._create_decision_entries(current))
                elif n_type == "EVENTO":
                    dialogue_entry["Texts"].append(self._create_event_entry(current))
                elif n_type == "END":
                    continue # El fin no anyade texto

                # Obtener hijos desde el grafo para seguir el camino
                hijos_ids = grafo.addys.get(curr_ptr, [])
                for h_id in hijos_ids:
                    stack.append(nodes_by_id[h_id])

            if dialogue_entry["Texts"]:
                dialogues_output.append(dialogue_entry)

        return {
            "Dialogues": dialogues_output,
            "LastModified": datetime.now().isoformat(),
            "Version": "1.0"
        }

    def _create_text_entry(self, node):
        '''
        Crea una entrada de texto desde un NodeDialogue
        '''
        from panels.defs import characters
        
        char_idx = 0
        if hasattr(node, 'character') and node.character:
            # Encontrar el indice del personaje
            char_list = list(characters.keys())
            try:
                char_idx = char_list.index(node.character.name)
            except ValueError:
                char_idx = 0
        
        text = ""
        if hasattr(node, 'textbox'):
            try:
                text = node.textbox.get("0.0", "end").strip()
            except:
                text = ""
        
        return {
            "Person": char_idx,
            "Emotion": "neutral",
            "Text": text,
            "Callbacks": [],
            "Type": "dialogue"
        }

    def _create_decision_entries(self, node):
        '''
        Crea entradas de texto desde un NodeDecision
        '''
        entries = []
        
        # Agregar la pregunta
        question = ""
        if hasattr(node, 'question_textbox'):
            try:
                question = node.question_textbox.get("0.0", "end").strip()
            except:
                question = ""
        
        entries.append({
            "Person": -1,
            "Emotion": "neutral",
            "Text": question,
            "Callbacks": [],
            "Type": "decision_question"
        })
        
        # Agregar cada opcion
        if hasattr(node, 'option_textboxes') and hasattr(node, 'num_options'):
            for i in range(min(node.num_options, len(node.option_textboxes))):
                textbox = node.option_textboxes[i]
                if textbox:
                    try:
                        option_text = textbox.get("0.0", "end").strip()
                    except:
                        option_text = ""
                    
                    entries.append({
                        "Person": -1,
                        "Emotion": "neutral",
                        "Text": option_text,
                        "OptionIndex": i,
                        "Callbacks": [],
                        "Type": "decision_option"
                    })
        
        return entries

    def _create_event_entry(self, node):
        '''
        Crea una entrada de evento desde un NodeEvent
        '''
        text = ""
        event_name = ""
        
        if hasattr(node, 'textbox'):
            try:
                text = node.textbox.get("0.0", "end").strip()
            except:
                text = ""
        
        if hasattr(node, 'event_entry'):
            try:
                event_name = node.event_entry.get()
            except:
                event_name = ""
        
        return {
            "Person": -1,
            "Emotion": "neutral",
            "Text": text,
            "Event": event_name,
            "Callbacks": [],
            "Type": "event"
        }
    
    def load_project(self):
        '''
        Carga un proyecto guardado desde dos archivos JSON
        '''

if __name__ == "__main__":
    App().run()

import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

class Serialyzer:
    def __init__(self, nodesTab, charactersTab):
        self.nodesTab = nodesTab
        self.charactersTab = charactersTab

    def choose_save_directory(self):
        '''
        Abre un cuadro de dialogo para elegir un directorio,
        pide un nombre al usuario y crea una carpeta nueva
        '''
        # Seleccionar directorio base
        
        initialdir="./projects"
        # Crear la carpeta si no existe
        if not os.path.exists(initialdir):
            os.makedirs(initialdir)
            print(f"Carpeta creada: {initialdir}")
        directory = filedialog.askdirectory(
            title="Seleccionar carpeta donde crear el proyecto",
            initialdir=initialdir
        )

        if not directory:
            return None

        # Pedir nombre de la carpeta al usuario
        folder_name = simpledialog.askstring(
            "Editor de Dialogos",
            "Ingrese el nombre para la carpeta del proyecto:",
            initialvalue="mi_proyecto"
        )

        if not folder_name:
            return None

        # Crear la ruta completa de la nueva carpeta
        new_folder_path = os.path.join(directory, folder_name)

        try:
            # Crear la carpeta si no existe
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                print(f"Carpeta creada: {new_folder_path}")
            else:
                # Si ya existe, preguntar si desea sobrescribir
                overwrite = messagebox.askyesno(
                    "Carpeta existente",
                    f"La carpeta '{folder_name}' ya existe.\n¿Desea usar esta carpeta de todos modos?"
                )
                if not overwrite:
                    return None

            return new_folder_path, folder_name

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo crear la carpeta:\n{str(e)}")
            return None

    def save_project(self):
        directory, filename = self.choose_save_directory()
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
            
    def load_project(self):
        '''
        Carga un proyecto guardado desde archivos JSON
        '''
        from panels.defs import characters, character

        # Seleccionar directorio
        directory = filedialog.askdirectory(
            title="Seleccionar carpeta del proyecto",
            initialdir="."
        )

        if not directory:
            return

        try:
            # === CARGAR PERSONAJES ===
            characters_path = None
            dialogues_path = None

            # Buscar archivos en el directorio
            for file in os.listdir(directory):
                if file.endswith('_characters.json'):
                    characters_path = os.path.join(directory, file)
                elif file.endswith('_dialogues.json'):
                    dialogues_path = os.path.join(directory, file)

            if not characters_path or not dialogues_path:
                messagebox.showerror("Error", "No se encontraron los archivos del proyecto")
                return

            # Cargar personajes
            with open(characters_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)

            # Limpiar y recargar personajes
            characters.clear()
            for char_info in characters_data.get('characters', []):
                characters[char_info['name']] = character(
                    name=char_info['name'],
                    color=char_info.get('Color', '#ffffff')
                )

            # Actualizar UI de personajes
            try:
                char_editor = self.charactersTab.children.get('!charactereditorframe')
                if char_editor:
                    char_editor.refresh_character_list()
            except Exception as e:
                print(f"No se pudo actualizar editor de personajes: {e}")

            # === CARGAR DIALOGOS ===
            with open(dialogues_path, 'r', encoding='utf-8') as f:
                dialogues_data = json.load(f)

            # Acceder al canvas
            try:
                node_editor_frame = self.nodesTab.children['!nodeeditorframe']
                canvas = node_editor_frame.canvas
            except (KeyError, AttributeError) as e:
                messagebox.showerror("Error", f"No se pudo acceder al canvas: {e}")
                return

            # === LIMPIAR CANVAS ===
            canvas.clear()

            # === CREAR NODOS ===
            from panels.custom_node_types import NodeStart, NodeEnd
            dialogues = dialogues_data.get('Dialogues', [])

            for dialogue_idx, dialogue in enumerate(dialogues):
                # Posicion inicial para esta rama
                start_y = 100 + (dialogue_idx * 600)
                current_x = 100
                x_spacing = 300

                # Crear nodo START
                start_node = NodeStart(canvas, x=current_x, y=start_y)
                current_x += x_spacing

                previous_node = start_node
                previous_output = start_node.output_

                # Procesar cada texto
                texts = dialogue.get('Texts', [])
                i = 0
                while i < len(texts):
                    text_entry = texts[i]
                    text_type = text_entry.get('Type', '')

                    if text_type == 'dialogue':
                        # Crear nodo de dialogo
                        node = self._create_dialogue_node(canvas, current_x, start_y, text_entry)
                        #self._connect_nodes(canvas, previous_output, node.input_1)

                        previous_node = node
                        previous_output = node.output_
                        current_x += x_spacing
                        i += 1

                    elif text_type == 'decision_question':
                        # Recopilar opciones de decision
                        options = []
                        j = i + 1
                        while j < len(texts) and texts[j].get('Type') == 'decision_option':
                            options.append(texts[j])
                            j += 1

                        # Crear nodo de decision
                        node = self._create_decision_node(canvas, current_x, start_y, text_entry, options)
                        self._connect_nodes(canvas, previous_output, node.input_1)

                        previous_node = node
                        previous_output = node.outputs[0] if node.outputs else None
                        current_x += x_spacing
                        i = j  # Saltar las opciones procesadas

                    elif text_type == 'event':
                        # Crear nodo de evento
                        node = self._create_event_node(canvas, current_x, start_y, text_entry)
                        self._connect_nodes(canvas, previous_output, node.input_1)

                        previous_node = node
                        previous_output = node.output_
                        current_x += x_spacing
                        i += 1

                    else:
                        i += 1

                # Crear nodo END
                end_node = NodeEnd(canvas, x=current_x, y=start_y)
                #if previous_output:
                #    self._connect_nodes(canvas, previous_output, end_node.input_1)

            messagebox.showinfo("Exito", f"Proyecto cargado correctamente desde:\n{directory}")

        except Exception as e:
            print(f"Error al cargar proyecto: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo cargar el proyecto:\n{str(e)}")
        
    # ===================================
    # SERIALIZACION
    # ===================================
    
    # ============ GUARDADO =============

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
        '''
        Convierte los nodos de dialogo en un diccionario para exportar¡
        '''
        nodes = self.nodesTab.canvas_container.nodes
        dialogue_idx = -1
        # RECORRIDO Y CONSTRUCCION DE JSON
        dialogues_output = []
        start_nodes = [n for n in nodes if getattr(n, 'type', '') == "START"]

        for startnode in start_nodes:
            dialogue_idx += 1
            dialogue_entry = {
                "DialogueID": dialogue_idx,
                "Texts": []
                }
            
            # Recorrido en profundidad desde el nodo Start
            visited = set()

            def dfs(node):
                if node.node_id in visited:
                    return
                visited.add(node.node_id)

                text_entry = {
                    "ID": node.node_id,
                    "Type": node.type,
                    "Character": getattr(node, 'character', ''),
                    "Next": None
                }

                # Procesar el nodo segun su tipo
                n_type = getattr(node, 'type', 'Unknown')
                if n_type in ["START", "DIALOGUE", "END"]:
                    if hasattr(node, 'text'):
                        text_entry["Text"] = node.text.get("1.0", "end-1c") # Si es un CTkTextbox

                    # El "Next" es el ID del primer target en output_connections
                    if node.output_connections:
                        text_entry["Next"] = node.output_connections[0]['target'].node_id
                elif n_type == "DECISION":
                    text_entry["Text"] = node.question_text.get("1.0", "end-1c")
                    #opciones
                    text_entry["Options"] = []
                    for i, option in enumerate(node.options):
                        option_data = {
                            "Text": option['entry'].get(),
                            "Next": None
                        }
                        # Si tienes una lógica donde la conexión i corresponde a la opción i:
                        if i < len(node.output_connections):
                            option_data["Next"] = node.output_connections[i]['target'].node_id

                        text_entry["Options"].append(option_data)
                #elif n_type == "EVENTO":
                #    text_entry["Events"].append(self._create_event_entry(node))
                else:
                    print(f"Tipo de nodo desconocido durante serializacion: {n_type}")
                
                # Anyade la entrada al dialogo
                dialogue_entry["Texts"].append(text_entry)

                # Recorre las conexiones
                for conn in getattr(node, 'output_connections', []):
                    dfs(conn['target'])
            
            # Iniciar DFS desde el nodo Start
            dfs(startnode)
            
            # Anyade el dialogo completo al output
            dialogues_output.append(dialogue_entry)

        return {
            "Dialogues": dialogues_output,
            "LastModified": datetime.now().isoformat()
        }
    # ============ CARGADO =============

    def load_characters(self, filepath):
        '''
        Carga personajes desde un archivo JSON
        '''
        pass

    def load_dialogues(self, data):
        '''
        Carga dialogos desde un archivo JSON
        '''
        # Mapa para relacionar ID del JSON -> Instancia del Objeto Nodo
        id_map = {}

        from panels.custom_node_types import StartNode, EndNode, DialogueNode, DecisionNode, ActionNode
        # Diccionario para mapear strings a clases
        node_classes = {
            "START": StartNode,
            "END": EndNode,
            "DIALOGUE": DialogueNode,
            "DECISION": DecisionNode,
            "ACTION": ActionNode
        }

        # --- PRIMERA PASADA: Crear Nodos ---
        current_x = 100
        current_y = 100

        for dialogue in data.get("Dialogues", []):
            for entry in dialogue.get("Texts", []):
                n_type = entry["Type"].upper()
                n_class = node_classes.get(n_type, DialogueNode)

                # Crear instancia
                new_node = n_class(
                    self.nodesTab.canvas_container.canvas, 
                    x=current_x, 
                    y=current_y
                )

                # Restaurar texto (identificando si es Textbox o Entry)
                if hasattr(new_node, 'text'):
                    new_node.text.insert("1.0", entry.get("Text", ""))
                elif hasattr(new_node, 'question_text'):
                    new_node.question_text.insert("1.0", entry.get("Text", ""))

                # Configurar personaje
                new_node.character = entry.get("Character", "")

                # Registrar en nuestro mapa de IDs
                id_map[entry["ID"]] = new_node

                # Desplazamiento visual simple para que no se solapen
                current_x += 250
                if current_x > 1000:
                    current_x = 100
                    current_y += 200

        # --- SEGUNDA PASADA: Crear Conexiones ---
        for dialogue in data.get("Dialogues", []):
            for entry in dialogue.get("Texts", []):
                source_node = id_map.get(entry["ID"])
                if not source_node: continue

                # Conexión simple (Next)
                if entry.get("Next") is not None:
                    target_node = id_map.get(entry["Next"])
                    if target_node:
                        source_node.connect_to(target_node, option_index=0)

                # Conexiones de Decisión (Options)
                if "Options" in entry:
                    # Primero vaciamos las opciones por defecto que crea el nodo
                    # (Opcional, según cómo funcione tu add_option)
                    for i, opt_data in enumerate(entry["Options"]):
                        # Si el nodo no tiene suficientes opciones creadas, las añadimos
                        if i >= len(source_node.options):
                            source_node.add_option(opt_data["Text"])
                        else:
                            source_node.options[i]['entry'].delete(0, "end")
                            source_node.options[i]['entry'].insert(0, opt_data["Text"])

                        # Conectar cada opción a su destino
                        if opt_data.get("Next") is not None:
                            target_node = id_map.get(opt_data["Next"])
                            if target_node:
                                source_node.connect_to(target_node, option_index=i)
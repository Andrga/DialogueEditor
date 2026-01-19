import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog
from panels.defs import Digraph

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
        try:
            Dialogue_graph = self.nodesTab.canvas_container.graph
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
        
        char = ""
        if hasattr(node, 'character') and node.character:
            try:
                char = node.character.name
            except ValueError:
                char = ""
        
        text = ""
        if hasattr(node, 'textbox'):
            try:
                text = node.textbox.get("0.0", "end").strip()
            except:
                text = ""
        
        return {
            "Person": char,
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
    
    # ============ CARGADO =============
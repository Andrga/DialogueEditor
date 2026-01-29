import json
import os
from datetime import datetime
from tkinter import filedialog, messagebox, simpledialog

class Serialyzer:
    def __init__(self, nodeEditor, charactersEditor, translationEditor):
        self.nodeEditor = nodeEditor
        self.charactersEditor = charactersEditor
        self.translationEditor = translationEditor

    def choose_save_directory(self):
        '''
        Abre un cuadro de dialogo para elegir un directorio,
        pide un nombre al usuario y crea una carpeta nueva
        '''
        base = "./projects"
        os.makedirs(base, exist_ok=True)

        path = filedialog.asksaveasfilename(
            title="Crear proyecto",
            initialdir=base,
            initialfile="mi_proyecto"
        )

        if not path:
            return None

        try:
            # Crear la carpeta si no existe
            os.makedirs(path, exist_ok=True)
            name = os.path.basename(path)
            return path, name
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

            # Serializar traducciones
            if self.translationEditor:
                translations_path = os.path.join(directory, f"{filename}_translations.csv")
                self.translationEditor.table.export_csv(translations_path)
            
            messagebox.showinfo("Exito", f"Proyecto guardado correctamente en:\n{directory}")

        except Exception as e:
            print(f"Error critico al guardar: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el archivo:\n{str(e)}")
            
    def load_project(self):
        '''
        Carga un proyecto guardado desde archivos JSON
        '''
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
            translations_path = None

            # Buscar archivos en el directorio
            for file in os.listdir(directory):
                if file.endswith('_characters.json'):
                    characters_path = os.path.join(directory, file)
                elif file.endswith('_dialogues.json'):
                    dialogues_path = os.path.join(directory, file)
                elif file.endswith('_translations.csv'):
                    translations_path = os.path.join(directory, file)

            if not characters_path or not dialogues_path:
                messagebox.showerror("Error", "No se encontraron los archivos del proyecto")
                return

            #  === CARGAR PERSONAJES ===
            with open(characters_path, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)

            self.load_characters(characters_data)
            
            # Acceder al canvas
            try:
                if self.nodeEditor:
                    canvas = self.nodeEditor.canvas_container
            except (KeyError, AttributeError) as e:
                messagebox.showerror("Error", f"No se pudo acceder al canvas: {e}")
                return
            # === LIMPIAR CANVAS ===
            canvas.clear_canvas()

            # === CARGAR DIALOGOS ===
            with open(dialogues_path, 'r', encoding='utf-8') as f:
                dialogues_data = json.load(f)

            # Cargar dialogos
            self.load_dialogues(dialogues_data)

            # === CARGAR TRADUCCIONES ===
            if self.translationEditor:
                translation_table = self.translationEditor.table
                if translations_path and os.path.exists(translations_path):
                    translation_table.import_csv(translations_path)
                    self.translationEditor.refresh()

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

        serialized_chars = {}
        # Recorremos todos los personajes
        for name, obj in characters.items():
            char = {
                "font":obj.font or "default_font",
                "sound": obj.sound or None,
                "Color": obj.color
            }

            serialized_chars[name] = char
        
        return {
        "characters": serialized_chars,
        "lastModified": datetime.now().isoformat()
            }

    def _serialize_dialogues(self):
        '''
        Convierte los nodos de dialogo en un diccionario para exportar¡
        '''
        nodes = self.nodeEditor.canvas_container.nodes
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
                    "Character": getattr(node, 'character', '').name if hasattr(node, 'character') and node.character else "",
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
                        # Si tienes una logica donde la conexion i corresponde a la opcion i:
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

    def load_characters(self, characters_data):
        '''
        Carga personajes desde un archivo JSON
        '''
        from panels.defs import characters, character
        # Limpiar y recargar personajes
        characters.clear()
        for name, char_info in characters_data.get('characters', {}).items():
            characters[name] = character(
                name=name,
                color=char_info.get('Color', '#ffffff'),
                sound=char_info.get('sound', 'Sin audio'),
                font=char_info.get('font', 'Sin fuente')
            )
        # Actualizar UI de personajes
        try:
            if self.charactersEditor:
                self.charactersEditor.refresh_character_list()
        except Exception as e:
            print(f"No se pudo actualizar editor de personajes: {e}")

        pass

    def load_dialogues(self, data):
        '''
        Carga dialogos desde un archivo JSON
        '''
        # Mapa para relacionar ID del JSON -> Instancia del Objeto Nodo
        id_map = {}

        from panels.custom_node_types import StartNode, EndNode, DialogueNode, DecisionNode, ActionNode
        #print("Cargando dialogos desde JSON...")
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
        #print("Iniciando carga de dialogos...")
        for dialogue in data.get("Dialogues", []):
            for entry in dialogue.get("Texts", []):
                n_type = entry["Type"].upper()
                n_class = node_classes.get(n_type, DialogueNode)

                # Crear instancia
                new_node = n_class(
                    self.nodeEditor.canvas_container, 
                    x=current_x, 
                    y=current_y
                )
                
                # Restaurar texto (identificando si es Textbox o Entry)
                if hasattr(new_node, 'text'):
                    new_node.text.insert("1.0", entry.get("Text", ""))
                elif hasattr(new_node, 'question_text'):
                    new_node.question_text.insert("1.0", entry.get("Text", ""))
                    
                # Configurar personaje
                from panels.defs import characters
                new_node.set_character(characters.get(entry.get("Character", ""), None))

                if n_type == "DECISION" and "Options" in entry:
                    # Limpiar opciones por defecto
                    while len(new_node.options) > 0:
                        new_node.remove_option(0)

                    # Forzar limpieza visual
                    new_node.update_idletasks()

                    # Crear las opciones del JSON inmediatamente
                    for opt_data in entry["Options"]:
                        new_node.add_option(opt_data["Text"], immediate=True)
                
                # Registrar en nuestro mapa de IDs
                id_map[entry["ID"]] = new_node
                # Agregar al canvas
                self.nodeEditor.canvas_container.add_node(new_node)

                # Desplazamiento visual simple para que no se solapen
                current_x += 300
                if current_x > 1000:
                    current_x = 100
                    current_y += 200

        # --- SEGUNDA PASADA: Crear Conexiones ---
        for dialogue in data.get("Dialogues", []):
            for entry in dialogue.get("Texts", []):
                source_node = id_map.get(entry["ID"])
                if not source_node: continue

                # Conexion simple (Next)
                if entry.get("Next") is not None:
                    target_node = id_map.get(entry["Next"])
                    if target_node is not None:
                        print(f"Conectando nodo ID {entry['ID']} al nodo ID {entry['Next']}")
                        source_node.connect_to(target_node)

                # Conexiones de Decision (Options)
                if "Options" in entry:
                    # Crear las opciones del JSON
                    for i, opt_data in enumerate(entry["Options"]):
                        # Conectar cada opcion a su destino
                        if opt_data.get("Next") is not None:
                            target_node = id_map.get(opt_data["Next"])
                            if target_node:
                                source_node.connect_to(target_node=target_node, option_index=i) 
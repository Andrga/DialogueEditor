import __main__
import customtkinter as ctk
from tknodesystem.node import Node
from tknodesystem.node_socket import NodeSocket
from panels.defs import characters


class NodeStart(Node):
    '''
    Nodo de inicio de conversacion.
    - Sin inputs
    - 1 output
    '''

    WIDTH = 160
    HEIGHT = 80
    type = "START"

    def __init__(self, canvas, x=200, y=200):
        center = (x, y)
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text="START",
            corner_radius=10,
            fg_color="#2d5a2d",
            border_color="#1a3a1a",
            text_color="white"
        )

        self._create_sockets(x, y)
        
        self.bind_all_to_movement()
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        self.socket_nums = 1
        
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        
        if x or y:
            super().move(x, y)
            
        self._register_in_app()
        self.canvas.obj_list.add(self)
    
    # =====================================================
    # SOCKETS
    # =====================================================

    def _create_sockets(self, x, y):
        # Output (derecha)
        self.output_ = NodeSocket(
            self.canvas,
            center=(x + self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            border_color="#009945",
            socket_num=self.canvas.socket_num
        )
        self.canvas.socket_num += 1
        self.allIDs.append(self.output_.ID)

    def connect_output(self, event):        
        self.canvas.clickcount += 1
        self.canvas.outputcell = self

        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
 
        self.output_.connect_wire()

    # =====================================================
    # UTILS
    # =====================================================
    def get_data(self):
        return {"type": type}

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass

    def destroy(self):
        """Destruir el nodo correctamente"""
        if self.ID not in self.canvas.find_all():
            return
        
        # Eliminar todos los IDs del canvas
        for i in self.allIDs:
            try:
                self.canvas.delete(i)
            except:
                pass
        
        # Remover de las listas del canvas
        try:
            self.canvas.node_list.remove(self)
        except (KeyError, ValueError):
            pass
        
        try:
            self.canvas.obj_list.remove(self)
        except (KeyError, ValueError, AttributeError):
            pass
        
        # Actualizar lineas
        for i in list(self.canvas.line_ids):
            try:
                i.update()
            except:
                pass


class NodeEnd(Node):
    '''
    Nodo de fin de conversacion.
    - 1 input
    - Sin outputs
    '''
    WIDTH = 160
    HEIGHT = 80
    type = "END"

    def __init__(self, canvas, x=200, y=200):
        center = (x, y)
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text="END",
            corner_radius=10,
            fg_color="#5a2d2d",
            border_color="#3a1a1a",
            text_color="white"
        )

        self._create_sockets(x, y)
        
        self.bind_all_to_movement()
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>',
                     lambda e: self.connect_input('input1'))
        self.socket_nums = 0
        
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        
        if x or y:
            super().move(x, y)
            
        self._register_in_app()
        self.canvas.obj_list.add(self)
    
    def update(self):
        '''
        Copiado parcialmente de node_types.NodeCompile
        '''            
        self.previous_value = self.output_.value

        self.canvas.after(50, self.update)
    
    # =====================================================
    # SOCKETS
    # =====================================================

    def _create_sockets(self, x, y):
        # Input (izquierda)
        self.input_1 = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y),
            radius=10,
            fg_color="#f50000",
            hover_color="#e0af55",
            socket_num=self.canvas.socket_num
        )
        self.canvas.socket_num += 1
        self.output_ = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y),
            radius=10,
            fg_color="#f54500",
            hover_color="#e0af55",
            socket_num=self.canvas.socket_num
        )
        self.canvas.socket_num += 1
        self.allIDs.append(self.input_1.ID)
        self.output_.hide()

    def connect_input(self, input_id):
        if self.canvas.outputcell is None:
            return
        self.canvas.clickcount += 1
        self.canvas.inputcell = self
        self.canvas.IDc = input_id
        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            self.canvas.conectcells()
            # --- PARCHE PARA EL EXPORTADOR ---
            # Guardamos la relación lógica: (ID salida -> ID entrada)
            out_id = self.canvas.outputcell.output_.socket_num
            in_id = self.input_1.socket_num
            self.canvas.line_list.add((out_id, in_id))

        self.output_.connect_wire()

    # =====================================================
    # UTILS
    # =====================================================
    def get_data(self):
        return {"type": type}

    def destroy(self):
        '''
        Destruir el nodo correctamente
        '''
        if self.ID not in self.canvas.find_all():
            return
        
        for i in self.allIDs:
            try:
                self.canvas.delete(i)
            except:
                pass
        
        try:
            self.canvas.node_list.remove(self)
        except (KeyError, ValueError):
            pass
        
        try:
            self.canvas.obj_list.remove(self)
        except (KeyError, ValueError, AttributeError):
            pass

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass


class NodeDialogue(Node):
    '''
    Nodo de dialogo.
    - 1 input
    - 1 output
    - Selector de personaje
    - Textbox de dialogo
    '''

    WIDTH = 280
    HEIGHT = 240
    type = "DIALOGO"

    def __init__(self, canvas, x=200, y=200):
        center = (x, y)
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text="Diálogo",
            corner_radius=10,
            fg_color="#3b3b3b",
            border_color="#292929",
            text_color="white"
        )
        self.character = None

        self._create_sockets(x, y)
        self._create_container(x, y)

        self.bind_all_to_movement()
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>',
                     lambda e: self.connect_input('input1'))
        self.canvas.bind_all("<Delete>", lambda e: self.destroy() if self.signal else None, add="+")
        self.socket_nums = 1
        
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        
        if x or y:
            super().move(x, y)
            
        self._register_in_app()
        self.canvas.obj_list.add(self)

    # =====================================================
    # SOCKETS
    # =====================================================

    def _create_sockets(self, x, y):
        self.input_1 = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=self.canvas.socket_num
        )
        self.canvas.socket_num += 1

        self.output_ = NodeSocket(
            self.canvas,
            center=(x + self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=self.canvas.socket_num
        )
        self.canvas.socket_num += 1

        self.allIDs.extend([self.input_1.ID, self.output_.ID])

    def connect_output(self, event):
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
            # --- PARCHE PARA EL EXPORTADOR ---
            # Guardamos la relación lógica: (ID salida -> ID entrada)
            out_id = self.canvas.outputcell.output_.socket_num
            in_id = self.input_1.socket_num
            self.canvas.line_list.add((out_id, in_id))

    # =====================================================
    # CONTENIDO
    # =====================================================

    def _create_container(self, x, y):
        global characters
        
        self.container = ctk.CTkFrame(self.canvas, fg_color="#3b3b3b")
        
        # Label y Selector de personaje
        lbl_character = ctk.CTkLabel(
            self.container,
            text="Personaje:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_character.pack(pady=(5, 2))

        self.character_selector = ctk.CTkComboBox(
            self.container,
            values=list(characters.keys()),
            command=self.on_character_selected,
            width=250,
            height=25,
            font=("Arial", 9)
        )
        self.character_selector.pack(pady=(0, 5))

        # Label y Textbox para dialogo
        lbl_text = ctk.CTkLabel(
            self.container,
            text="Diálogo:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_text.pack(pady=(0, 2))

        self.textbox = ctk.CTkTextbox(
            self.container,
            width=250,
            height=120,
            font=("Arial", 10),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#1a1a1a"
        )
        self.textbox.pack(pady=(0, 5))

        self.window_id = self.canvas.create_window(
            x, y,
            window=self.container,
            width=self.WIDTH - 15,
            height=self.HEIGHT - 30
        )

        self.allIDs.append(self.window_id)
    
    def on_character_selected(self, name):
        char = characters.get(name)
        if char:
            self.character = char
            self.textbox.configure(text_color=char.color)
        else:
            self.character = None
            self.textbox.configure(text_color="white")
    
    # =====================================================
    # UTILS
    # =====================================================

    def update(self):
        self.output_.value = True

    def get_data(self):
        return {
            "type": "dialogue",
            "character": self.character.name if self.character else None,
            "text": self.textbox.get("0.0", "end").strip()
        }

    def destroy(self):
        '''
        Destruimos el nodo y su contenido
        '''
        if self.ID not in self.canvas.find_all():
            return
        
        for i in self.allIDs:
            try:
                self.canvas.delete(i)
            except:
                pass
        
        try:
            self.canvas.node_list.remove(self)
        except (KeyError, ValueError):
            pass
        
        try:
            self.canvas.obj_list.remove(self)
        except (KeyError, ValueError, AttributeError):
            pass

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass

class NodeDecision(Node):
    '''
    Nodo de decision.
    - 1 input
    - N outputs dinamicos
    - Textbox para pregunta
    - Cada output tiene texto asociado
    '''

    WIDTH = 300
    HEIGHT = 280
    type = "DECISION"

    def __init__(self, canvas, x=200, y=200, num_options=2):
        center = (x, y)
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text="Decisión",
            corner_radius=10,
            fg_color="#3b3b3b",
            border_color="#292929",
            text_color="white"
        )

        self.outputs = []
        self.option_textboxes = []
        self.num_options = num_options
        self.output_ = None 

        self._create_sockets(x, y)
        self._create_container(x, y)

        self.bind_all_to_movement()
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>',
                     lambda e: self.connect_input('input1'))
        
        # Bind outputs
        for i, output in enumerate(self.outputs):
            self.canvas.tag_bind(output.ID, '<Button-1>',
                        lambda e, idx=i: self.connect_output(idx))
        
        self.canvas.bind_all("<Delete>", lambda e: self.destroy() if self.signal else None, add="+")
        self.socket_nums = len(self.outputs)
        
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        
        if x or y:
            super().move(x, y)
            
        self._register_in_app()
        self.canvas.obj_list.add(self)
    
    # =====================================================
    # SOCKETS
    # =====================================================

    def _create_sockets(self, x, y):
        # Input (izquierda)
        self.input_1 = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y - 100),
            radius=10,
            fg_color="#00f56e",
            socket_num=self.canvas.socket_num
        )
        self.allIDs.append(self.input_1.ID)
        self.canvas.socket_num += 1

        # Outputs (derecha, distribuidos verticalmente)
        spacing = 200 / (self.num_options + 1)
        for i in range(self.num_options):
            output_y = y - 100 + (i + 1) * spacing
            output = NodeSocket(
                self.canvas,
                center=(x + self.WIDTH / 2, output_y),
                radius=10,
                fg_color="#ff6b6b",
                socket_num=self.canvas.socket_num
            )
            self.outputs.append(output)
            self.canvas.socket_num += 1
            self.allIDs.append(output.ID)

    def connect_output(self, option_index):
        self.canvas.clickcount += 1
        self.canvas.outputcell = self
        self.canvas.current_output_index = option_index
        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
        self.outputs[option_index].connect_wire()

    def connect_input(self, input_id):
        if self.canvas.outputcell is None:
            return
        self.canvas.clickcount += 1
        self.canvas.inputcell = self
        self.canvas.IDc = input_id
        if self.canvas.clickcount == 2:
            self.canvas.clickcount = 0
            self.canvas.conectcells()
            # --- PARCHE PARA EL EXPORTADOR ---
            # Guardamos la relación lógica: (ID salida -> ID entrada)
            out_id = self.canvas.outputcell.output_.socket_num
            in_id = self.input_1.socket_num
            self.canvas.line_list.add((out_id, in_id))

    def update_sockets(self):
        '''
        Sobrescribimoss update_sockets para actualizar todos los outputs
        '''
        for output in self.outputs:
            output.update()
        
        try:
            self.input_1.update()
        except AttributeError:
            pass
        
        for i in self.canvas.line_ids:
            i.update()
        
        deleted = set()
        for i in self.canvas.line_ids:
            if not i.connected:
                deleted.add(i)
        self.canvas.line_ids = self.canvas.line_ids.difference(deleted)

    # =====================================================
    # CONTENIDO
    # =====================================================

    def _create_container(self, x, y):
        self.container = ctk.CTkFrame(self.canvas, fg_color="#3b3b3b")

        # Label y Textbox para pregunta
        lbl_question = ctk.CTkLabel(
            self.container,
            text="Pregunta:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_question.pack(pady=(5, 2))

        self.question_textbox = ctk.CTkTextbox(
            self.container,
            width=270,
            height=60,
            font=("Arial", 9),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#1a1a1a"
        )
        self.question_textbox.pack(pady=(0, 10))

        # Frame para opciones
        lbl_options = ctk.CTkLabel(
            self.container,
            text="Opciones:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_options.pack(pady=(0, 5))

        options_frame = ctk.CTkScrollableFrame(
            self.container,
            width=270,
            height=120,
            fg_color="#2b2b2b"
        )
        options_frame.pack(pady=(0, 5), fill="both", expand=True)

        # Textboxes para cada opcion
        for i in range(self.num_options):
            lbl = ctk.CTkLabel(
                options_frame,
                text=f"Opción {i + 1}:",
                text_color="#ff6b6b",
                font=("Arial", 9)
            )
            lbl.pack(pady=(5, 2))

            textbox = ctk.CTkTextbox(
                options_frame,
                width=250,
                height=30,
                font=("Arial", 8),
                text_color="white",
                fg_color="#1a1a1a",
                border_color="#0a0a0a"
            )
            textbox.pack(pady=(0, 5))
            self.option_textboxes.append(textbox)

        # Botones de control
        button_frame = ctk.CTkFrame(self.container, fg_color="#3b3b3b")
        button_frame.pack(pady=5)

        btn_add = ctk.CTkButton(
            button_frame,
            text="+",
            width=30,
            height=25,
            font=("Arial", 12),
            command=self.add_option
        )
        btn_add.pack(side="left", padx=5)

        btn_remove = ctk.CTkButton(
            button_frame,
            text="-",
            width=30,
            height=25,
            font=("Arial", 12),
            command=self.remove_option
        )
        btn_remove.pack(side="left", padx=5)

    def add_option(self):
        '''
        Anyadimos una nueva opcion
        '''
        if self.num_options < 5:  # Limite de 5 opciones
            self.num_options += 1
            self.option_textboxes.append(None)

    def remove_option(self):
        '''
        Elimina la ultima opcion creada
        '''
        if self.num_options > 2:
            self.num_options -= 1
            if self.option_textboxes:
                self.option_textboxes.pop()

        self.window_id = self.canvas.create_window(
            x, y,
            window=self.container,
            width=self.WIDTH - 15,
            height=self.HEIGHT - 30
        )

        self.allIDs.append(self.window_id)

    # =====================================================
    # UTILS
    # =====================================================
    def update(self):
        for output in self.outputs:
            output.value = True

    def get_data(self):
        options = []
        for i, textbox in enumerate(self.option_textboxes[:self.num_options]):
            if textbox is not None:
                options.append({
                    "index": i,
                    "text": textbox.get("0.0", "end").strip()
                })
        
        return {
            "type": "decision",
            "question": self.question_textbox.get("0.0", "end").strip(),
            "options": options
        }

    def destroy(self):
        """Destruir el nodo correctamente"""
        if self.ID not in self.canvas.find_all():
            return
        
        for i in self.allIDs:
            try:
                self.canvas.delete(i)
            except:
                pass
        
        try:
            self.canvas.node_list.remove(self)
        except (KeyError, ValueError):
            pass
        
        try:
            self.canvas.obj_list.remove(self)
        except (KeyError, ValueError, AttributeError):
            pass

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass

class NodeEvent(Node):
    '''
    Nodo de evento.
    - 1 input
    - 1 output
    - Textbox para dialogo
    - Campo para nombre del evento
    '''

    WIDTH = 280
    HEIGHT = 220

    def __init__(self, canvas, x=200, y=200):
        center = (x, y)
        super().__init__(
            canvas=canvas,
            width=self.WIDTH,
            height=self.HEIGHT,
            center=center,
            text="Evento",
            corner_radius=10,
            fg_color="#3b3b3b",
            border_color="#292929",
            text_color="white"
        )

        self.inputs = []
        self.outputs = []

        self._create_sockets(x, y)
        self._create_container(x, y)

        self.bind_all_to_movement()
        self.canvas.tag_bind(self.output_.ID, '<Button-1>', self.connect_output)
        self.canvas.tag_bind(self.input_1.ID, '<Button-1>',
                     lambda e: self.connect_input('input1'))
        self.canvas.bind_all("<Delete>", lambda e: self.destroy() if self.signal else None, add="+")
        self.socket_nums = 1
        
        # Escala inicial
        for j in range(self.canvas.gain_in):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 1.1, 1.1)
        for j in range(abs(self.canvas.gain_out)):
            for i in self.allIDs:
                self.canvas.scale(i, 0, 0, 0.9, 0.9)
        
        if x or y:
            super().move(x, y)
            
        self._register_in_app()
        self.canvas.obj_list.add(self)

    def _create_sockets(self, x, y):
        self.input_1 = NodeSocket(
            self.canvas,
            center=(x - self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=self.canvas.socket_num
        )
        self.inputs.append(self.input_1)
        self.canvas.socket_num += 1

        self.output_ = NodeSocket(
            self.canvas,
            center=(x + self.WIDTH / 2, y),
            radius=10,
            fg_color="#00f56e",
            socket_num=self.canvas.socket_num
        )
        self.outputs.append(self.output_)
        self.canvas.socket_num += 1

        self.allIDs.extend([self.input_1.ID, self.output_.ID])

    def _create_container(self, x, y):
        self.container = ctk.CTkFrame(self.canvas, fg_color="#3b3b3b")

        # Label y Textbox para diálogo
        lbl_text = ctk.CTkLabel(
            self.container,
            text="Diálogo:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_text.pack(pady=(5, 2))

        self.textbox = ctk.CTkTextbox(
            self.container,
            width=250,
            height=80,
            font=("Arial", 9),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#1a1a1a"
        )
        self.textbox.pack(pady=(0, 10))

        # Label y Entry para evento
        lbl_event = ctk.CTkLabel(
            self.container,
            text="Nombre del Evento:",
            text_color="white",
            font=("Arial", 10)
        )
        lbl_event.pack(pady=(0, 2))

        self.event_entry = ctk.CTkEntry(
            self.container,
            width=250,
            height=30,
            font=("Arial", 10),
            text_color="white",
            fg_color="#2b2b2b",
            border_color="#1a1a1a"
        )
        self.event_entry.pack(pady=(0, 5))

        self.window_id = self.canvas.create_window(
            x, y,
            window=self.container,
            width=self.WIDTH - 15,
            height=self.HEIGHT - 30
        )

        self.allIDs.append(self.window_id)

    def connect_output(self, event):
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

    def get_data(self):
        return {
            "type": "event",
            "text": self.textbox.get("0.0", "end").strip(),
            "event_name": self.event_entry.get()
        }

    def destroy(self):
        """Destruir el nodo correctamente"""
        if self.ID not in self.canvas.find_all():
            return
        
        for i in self.allIDs:
            try:
                self.canvas.delete(i)
            except:
                pass
        
        try:
            self.canvas.node_list.remove(self)
        except (KeyError, ValueError):
            pass
        
        try:
            self.canvas.obj_list.remove(self)
        except (KeyError, ValueError, AttributeError):
            pass

    def _register_in_app(self):
        try:
            app = self.canvas.master.master.master.master.master
            if hasattr(app, "active_nodes"):
                app.active_nodes.append(self)
        except Exception:
            pass
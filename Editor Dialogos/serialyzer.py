import json, traceback, customtkinter as ctk
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

class Serialyzer:
    def __init__(self, nodeEditor, charactersEditor, translationEditor):
        self.nodeEditor = nodeEditor
        self.charactersEditor = charactersEditor
        self.translationEditor = translationEditor
        # Corrección del error:
        self.projects_base = Path("./projects")
        self.projects_base.mkdir(exist_ok=True)

    def _json_io(self, path, data=None):
        mode = 'w' if data is not None else 'r'
        with open(path, mode, encoding='utf-8') as f:
            return json.dump(data, f, ensure_ascii=False, indent=2) if data else json.load(f)

    def choose_save_directory(self):
        res = {"path": None}
        dialog = ctk.CTkToplevel()
        dialog.title("Guardar Proyecto")
        dialog.geometry("300x280")
        dialog.attributes("-topmost", True) # Asegura que salga al frente
        dialog.grab_set()

        def set_res(p, name):
            # Verificamos si ya existen archivos de proyecto
            if p.exists() and any(p.glob("*_characters.json")):
                if not messagebox.askyesno("Sobrescribir", f"¿Sobrescribir el proyecto '{name}'?"): return
            res["path"] = (p, name)
            dialog.destroy()

        def on_new():
            name = simpledialog.askstring("Nuevo", "Nombre del proyecto:", parent=dialog)
            if name:
                clean_name = "".join(c for c in name if c.isalnum() or c in (' ', '_', '-')).strip()
                if clean_name: set_res(self.projects_base / clean_name, clean_name)

        def on_exist():
            dialog.destroy()
            path = filedialog.askdirectory(title="Seleccionar Carpeta", initialdir=self.projects_base)
            if path: 
                p = Path(path)
                set_res(p, p.name)

        # UI
        ctk.CTkLabel(dialog, text="Gestión de Proyecto", font=("Arial", 16, "bold")).pack(pady=15)
        
        btns = [
            ("Seleccionar Existente", on_exist, None),
            ("Crear Nuevo Proyecto", on_new, None),
            ("Cancelar", dialog.destroy, "gray")
        ]

        for text, cmd, color in btns:
            ctk.CTkButton(dialog, text=text, command=cmd, width=220, height=40, fg_color=color).pack(pady=10)

        # Centrar ventana
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - 150
        y = (dialog.winfo_screenheight() // 2) - 140
        dialog.geometry(f"+{x}+{y}")

        dialog.wait_window()
        return res["path"]

    def save_project(self):
        selected = self.choose_save_directory()
        if not selected: return
        path, name = selected
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            payloads = {
                f"{name}_characters.json": self._serialize_characters(),
                f"{name}_dialogues.json": self._serialize_dialogues()
            }
            
            for fname, data in payloads.items():
                self._json_io(path / fname, data)
            
            if self.translationEditor:
                # Usar export_csv directamente si es el objeto tabla o el editor
                target = getattr(self.translationEditor, 'table', self.translationEditor)
                target.export_csv(path / f"{name}_translations.csv")
            
            messagebox.showinfo("Éxito", f"Proyecto '{name}' guardado correctamente.")
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", f"No se pudo guardar:\n{e}")

    def load_project(self):
        path = filedialog.askdirectory(title="Cargar Proyecto")
        if not path: return
        p = Path(path)
        try:
            files = {f.name.split('_')[-1]: f for f in p.iterdir() if "_" in f.name}
            if not {'characters.json', 'dialogues.json'}.issubset(files.keys()):
                return messagebox.showerror("Error", "No es una carpeta de proyecto válida.")

            self.load_characters(self._json_io(files['characters.json']))
            self.nodeEditor.canvas_container.clear_canvas()
            self.load_dialogues(self._json_io(files['dialogues.json']))

            if self.translationEditor and 'translations.csv' in files:
                self.translationEditor.table.import_csv(files['translations.csv'])
                self.translationEditor.refresh()
            messagebox.showinfo("Éxito", "Carga completa.")
        except Exception as e:
            messagebox.showerror("Error", f"Error de carga: {e}")

    def _serialize_characters(self):
        from panels.defs import characters
        return {"characters": {n: {"font": c.font or "default", "sound": c.sound, "Color": c.color} 
                               for n, c in characters.items()}, "lastModified": datetime.now().isoformat()}

    def _serialize_dialogues(self):
        nodes = self.nodeEditor.canvas_container.nodes
        out = []
        for idx, start in enumerate(n for n in nodes if getattr(n, 'type', '') == "START"):
            visited, texts = set(), []
            def dfs(n):
                if n.node_id in visited: return
                visited.add(n.node_id)
                widget = getattr(n, 'text', getattr(n, 'question_text', None))
                entry = {
                    "ID": n.node_id, "Type": n.type,
                    "Character": getattr(n.character, 'name', "") if getattr(n, 'character', None) else "",
                    "Text": widget.get("1.0", "end-1c") if widget else "",
                    "Next": n.output_connections[0]['target'].node_id if n.output_connections else None
                }
                if n.type == "DECISION":
                    entry["Options"] = [{"Text": o['entry'].get(), "Next": (n.output_connections[i]['target'].node_id 
                                        if i < len(n.output_connections) else None)} for i, o in enumerate(n.options)]
                texts.append(entry)
                for c in getattr(n, 'output_connections', []): dfs(c['target'])
            dfs(start)
            out.append({"DialogueID": idx, "Texts": texts})
        return {"Dialogues": out, "LastModified": datetime.now().isoformat()}

    def load_characters(self, data):
        from panels.defs import characters, character
        characters.clear()
        for n, i in data.get('characters', {}).items():
            characters[n] = character(name=n, color=i.get('Color', '#fff'), sound=i.get('sound', 'N/A'), font=i.get('font', 'N/A'))
        if self.charactersEditor: self.charactersEditor.refresh_character_list()

    def load_dialogues(self, data):
        from panels.custom_node_types import StartNode, EndNode, DialogueNode, DecisionNode, ActionNode
        from panels.defs import characters
        n_map = {"START": StartNode, "END": EndNode, "DIALOGUE": DialogueNode, "DECISION": DecisionNode, "ACTION": ActionNode}
        id_map, canvas = {}, self.nodeEditor.canvas_container
        x, y = 100, 100

        all_entries = [t for d in data.get("Dialogues", []) for t in d.get("Texts", [])]
        for e in all_entries:
            node = n_map.get(e["Type"].upper(), DialogueNode)(canvas, x=x, y=y)
            w = getattr(node, 'text', getattr(node, 'question_text', None))
            if w: w.insert("1.0", e.get("Text", ""))
            node.set_character(characters.get(e.get("Character", "")))
            if e["Type"] == "DECISION":
                while node.options: node.remove_option(0)
                for o in e.get("Options", []): node.add_option(o["Text"], immediate=True)
            id_map[e["ID"]] = node
            canvas.add_node(node)
            x += 300
            if x > 1000: x, y = 100, y + 250

        for e in all_entries:
            src = id_map.get(e["ID"])
            if not src: continue
            if e.get("Next") in id_map: src.connect_to(id_map[e["Next"]])
            for i, o in enumerate(e.get("Options", [])):
                if o.get("Next") in id_map: src.connect_to(id_map[o["Next"]], option_index=i)
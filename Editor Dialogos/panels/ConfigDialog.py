import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

class ConfigDialog(ctk.CTkToplevel):

    def __init__(self, parent, config):
        super().__init__(parent)
        self.config = config

        self.title("Configuración")
        self.geometry("600x300")
        self.transient(parent)
        self.grab_set()

        self._center()
        self._ui()
        self._load()

    # ---------- UI ----------
    def _center(self):
        self.update_idletasks()
        w, h = 600, 300
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _ui(self):
        self.entries = {}

        frame = ctk.CTkFrame(self)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="Configuración de Rutas",
                     font=ctk.CTkFont(size=16, weight="bold")).pack(pady=10)

        self._path_row(frame, "audio_folder", "Carpeta de Audios")
        self._path_row(frame, "fonts_folder", "Carpeta de Fuentes")

        btns = ctk.CTkFrame(frame)
        btns.pack(fill="x", pady=15)

        ctk.CTkButton(btns, text="Cancelar",
                      fg_color="gray", command=self.destroy).pack(side="right", padx=5)
        ctk.CTkButton(btns, text="Guardar",
                      command=self._save).pack(side="right")

    def _path_row(self, parent, key, label):
        box = ctk.CTkFrame(parent)
        box.pack(fill="x", pady=8)

        ctk.CTkLabel(box, text=label).pack(anchor="w", padx=10)

        row = ctk.CTkFrame(box)
        row.pack(fill="x", padx=10, pady=5)

        entry = ctk.CTkEntry(row)
        entry.pack(side="left", fill="x", expand=True)

        ctk.CTkButton(
            row, text="Examinar", width=100,
            command=lambda: self._browse(entry)
        ).pack(side="right")

        self.entries[key] = entry

    # ---------- Logic ----------
    def _browse(self, entry):
        path = filedialog.askdirectory(initialdir=entry.get() or os.path.expanduser("~"))
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)

    def _load(self):
        for key, entry in self.entries.items():
            value = self.config.get(key)
            if value:
                entry.insert(0, value)

    def _save(self):
        for key, entry in self.entries.items():
            path = entry.get()
            if path and not os.path.isdir(path):
                return messagebox.showerror("Error", f"La ruta no existe:\n{path}")
            self.config.set(key, path)

        self.destroy()

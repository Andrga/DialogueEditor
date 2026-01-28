from tkinter import filedialog
import webbrowser
import customtkinter as ctk
from tkinter import *
from panels.defs import TranslationTable
from customtkinter import CTkFrame
from tkinter import messagebox

class TranslationEditor(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        self.pack(fill=BOTH, expand=True)

        self.table = TranslationTable()
        self.rows = {}

        # ---- TOP BAR ----
        top = ctk.CTkFrame(self)
        top.pack(fill=X, pady=5)

        ctk.CTkButton(top, text="+ Idioma", fg_color="#B69436", hover_color="#9B7A2D", command=self.add_language).pack(side=LEFT, padx=5)
        ctk.CTkButton(top, text="+ Clave", fg_color="#5AB636", hover_color="#4A9E2D", command=self.add_key).pack(side=LEFT, padx=5)
        ctk.CTkButton(top, text="Web Nomenclatura idiomas", fg_color="#A95A4B", hover_color="#8B4513", command=lambda: webbrowser.open("https://es.wikipedia.org/wiki/ISO_639-1")).pack(side=LEFT, padx=5)
        ctk.CTkButton(top, text="Import CSV", command=self.import_csv).pack(side=RIGHT, padx=5)
        ctk.CTkButton(top, text="Export CSV", command=self.export_csv).pack(side=RIGHT, padx=5)

        # ---- HEADERS ----
        self.headers = ctk.CTkFrame(self)
        self.headers.pack(fill=X, padx=5, pady=(5, 0))

        # ---- CONTENT ----
        self.content = ctk.CTkScrollableFrame(self)
        self.content.pack(fill=BOTH, expand=True)

        self.refresh()

    def draw_headers(self):
        for w in self.headers.winfo_children():
            w.destroy()

        ctk.CTkLabel(self.headers, text="KEY", width=200).pack(side=LEFT, padx=5)
        for lang in self.table.languages:
            col = ctk.CTkFrame(self.headers, fg_color="transparent")
            col.pack(side=LEFT, fill=X, expand=True, padx=2)

            ctk.CTkLabel(col, text=lang.upper()).pack(side=LEFT)

            if len(self.table.languages) > 1:
                ctk.CTkButton(
                    col,
                    text="✕",
                    width=18,
                    height=18,
                    fg_color="#ff4d4d",
                    hover_color="#ff1a1a",
                    command=lambda l=lang: self.delete_language(l)
                ).pack(side=LEFT, padx=3)
        
        ctk.CTkLabel(self.headers, text="", width=40).pack(side=LEFT)

    def refresh(self):
        self.draw_headers()

        for w in self.content.winfo_children():
            w.destroy()
        self.rows.clear()

        for key in sorted(self.table.translations):
            row = TranslationRowWidget(
                self.content,
                key,
                self.table.languages,
                self.delete_key,
                self.rename_key
            )
            row.pack(fill=X, pady=2)

            row.set_values(self.table.translations[key])
            self.rows[key] = row

    # ---------- Actions ----------
    def add_language(self):
        lang = ctk.CTkInputDialog(text="Idioma:", title="Nuevo idioma").get_input()
        if lang:
            self.save()
            self.table.add_language(lang.strip().lower())
            self.refresh()

    def add_key(self):
        key = ctk.CTkInputDialog(text="Clave:", title="Nueva clave").get_input()
        if key:
            self.save()
            self.table.add_key(key.strip().upper())
            self.refresh()

    def delete_key(self, key):
        self.table.remove_key(key)
        self.refresh()

    def rename_key(self, old, new):
        if old == new or not new:
            return
        if new in self.table.translations:
            messagebox.showwarning("Error", "La clave ya existe")
            self.refresh()
            return
        self.save()
        self.table.translations[new] = self.table.translations.pop(old)
        self.refresh()
    
    def delete_language(self, lang):
        if len(self.table.languages) <= 1:
            return

        self.save()
        self.table.remove_language(lang)
        self.refresh()

    # ---------- Data ----------
    def save(self):
        for key, row in self.rows.items():
            for lang, text in row.get_values().items():
                self.table.set(key, lang, text)

    def export_csv(self):
        self.save()
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        if path:
            self.table.export_csv(path)

    def import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if path:
            self.table.import_csv(path)
            self.refresh()

class TranslationRowWidget(ctk.CTkFrame):
    def __init__(self, master, key, languages, on_delete, on_rename):
        super().__init__(master, fg_color="#2a2a2a")

        self.on_rename = on_rename
        self.textboxes = {}

        # KEY
        self.key_entry = ctk.CTkEntry(self, width=200)
        self.key_entry.insert(0, key)
        self.key_entry.pack(side=LEFT, padx=5, fill=Y)
        self.key_entry.bind("<FocusOut>", lambda e: on_rename(key, self.key_entry.get()))

        # TEXTOS
        for lang in languages:
            tb = ctk.CTkTextbox(self, height=50)
            tb.pack(side=LEFT, fill=BOTH, expand=True, padx=2)
            self.textboxes[lang] = tb

        # DELETE
        ctk.CTkButton(
            self,
            text="✕",
            width=30,
            fg_color="#ff4d4d",
            command=lambda: on_delete(self.key_entry.get())
        ).pack(side=LEFT, padx=5)

    def get_values(self):
        return {l: t.get("1.0", "end-1c") for l, t in self.textboxes.items()}

    def set_values(self, data):
        for l, v in data.items():
            if l in self.textboxes:
                self.textboxes[l].insert("1.0", v)
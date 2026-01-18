import customtkinter as ctk
from tkinter import *
from panels.defs import characters, character, miscelaneousTexts
from CTkColorPicker import AskColor
from customtkinter import CTkFrame
from tkinter import messagebox

class MiscelaneousEditor(CTkFrame):
    def __init__(self, master):
        super().__init__(master=master)
        
        # Contenido
        keytext = ctk.CTkLabel(master=self, width=200, height=50, text="[KEY] : ", anchor="center")
        keytext.pack(side=TOP)
        lenguajeText = ctk.CTkLabel(master=self, width=200, height=50, text="Español", anchor="center")
        lenguajeText.pack(side=TOP)
        self.content = ctk.CTkScrollableFrame(master=self)
        self.content.pack(fill=BOTH)
        # Botones para anyadir elemento
        self.buttons = ctk.CTkFrame(master=self)
        self.buttons.pack()
        addParameter = ctk.CTkButton(master=self.buttons, text="+ parametro", command=self.add_parameter)
        addParameter.pack(side=LEFT, padx=10)
        addLenguage = ctk.CTkButton(master=self.buttons, text="+ Lenguaje", command=self.add_lenguaje)
        addLenguage.pack(side=LEFT, padx=10)

    def add_parameter(self):
        global miscelaneousTexts
        nlenguajes = len(miscelaneousTexts["lenguajes"])
        frame = ctk.CTkFrame(master=self.content)
        frame.pack(pady=5)
        key = ctk.CTkTextbox(master=frame, width=200, height=50)#, text="Key")
        key.pack(side=LEFT, fill=X, expand=True)
        for i in range(nlenguajes):
            miscelaneousTexts["text"] = {}
            trad = ctk.CTkTextbox(master=frame, width=500, height=50)#, text="Trad")
            trad.pack(side=LEFT, fill=X, expand=True, padx=10)
            print("PArametro añadido?")
        print("PArametro añadido?")

    def add_lenguaje(self):
        pass
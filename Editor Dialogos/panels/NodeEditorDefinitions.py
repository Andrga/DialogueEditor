import customtkinter as ctk

class Node:
    def __init__(self, canvas, x, y, text):
        self.canvas = canvas
        self.id = canvas.create_rectangle(x, y, x+120, y+60, fill="#444")
        self.text = canvas.create_text(x+60, y+30, text=text, fill="white")

        self._drag_data = {"x":0, "y":0}
        self.canvas.tag_bind(self.id, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.id, "<B1-Motion>", self.on_drag)
        self.canvas.tag_bind(self.text, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.text, "<B1-Motion>", self.on_drag)

    def on_press(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        self.canvas.move(self.id, dx, dy)
        self.canvas.move(self.text, dx, dy)
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

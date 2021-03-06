import tkinter as tk
from view.common_components import NavBarComponent, SnipeFormComponent


class SnipeScreen(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        NavBarComponent(master).grid(row=0, column=0)
        self.snipe_form_component = SnipeFormComponent(self)
        self.snipe_form_component.grid(row=1, column=0)

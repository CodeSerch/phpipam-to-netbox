import tkinter as tk

from .main_window import MainWindow
from .state import AppState
from .controller import AppController
from .menu import AppMenu


class App:

    def __init__(self):

        self.root = tk.Tk()

        self.state = AppState()

        self.view = MainWindow(
            self.root
        )

        self.controller = AppController(
            self.root,
            self.state,
            self.view
        )

        self.menu = AppMenu(
            self.root,
            on_xls_to_csv=self.controller.convertir_xls_a_csv
        )

        self.menu.crear()

        print("MENU CREADO")

    def run(self):

        self.root.mainloop()
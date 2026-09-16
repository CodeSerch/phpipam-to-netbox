from .main_window import MainWindow
from .state import AppState
from .controller import AppController


class App:

    def __init__(self):

        import tkinter as tk

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

    def run(self):

        self.root.mainloop()
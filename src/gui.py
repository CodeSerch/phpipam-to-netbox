import tkinter as tk

from gui.main_window import MainWindow
from gui.state import AppState
from gui.controller import AppController
from gui.menu import AppMenu


class App:

    def __init__(self):

        self.root = tk.Tk()

        self.state = AppState()

        self.window = MainWindow(
            self.root
        )

        self.controller = AppController(
            self.root,
            self.state,
            self.window
        )

        self.menu = AppMenu(
            self.root,
            on_xls_to_csv=self.controller.convertir_xls_a_csv
        )

        self.menu.crear()

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = App()

    app.run()

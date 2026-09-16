import tkinter as tk

from gui.main_window import MainWindow
from gui.state import AppState


class App:

    def __init__(self):

        self.root = tk.Tk()

        self.state = AppState()

        self.window = MainWindow(
            self.root
        )

    def run(self):

        self.root.mainloop()


if __name__ == "__main__":

    app = App()

    app.run()
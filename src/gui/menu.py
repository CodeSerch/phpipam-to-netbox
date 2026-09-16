import tkinter as tk


class AppMenu:

    def __init__(self, root):

        self.root = root

    def crear(self):

        menubar = tk.Menu(
            self.root
        )

        # ====================================================
        # HERRAMIENTAS
        # ====================================================

        herramientas_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        herramientas_menu.add_command(
            label="XLS / XLSX → CSV"
        )

        menubar.add_cascade(
            label="Herramientas",
            menu=herramientas_menu
        )

        # ====================================================
        # CONFIGURACIÓN
        # ====================================================

        configuracion_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        configuracion_menu.add_command(
            label="Configuración general..."
        )

        menubar.add_cascade(
            label="Configuración",
            menu=configuracion_menu
        )

        # ====================================================
        # AYUDA
        # ====================================================

        ayuda_menu = tk.Menu(
            menubar,
            tearoff=0
        )

        ayuda_menu.add_command(
            label="Información del software"
        )

        menubar.add_cascade(
            label="Ayuda",
            menu=ayuda_menu
        )

        # ====================================================
        # APLICAR MENÚ
        # ====================================================

        self.root.config(
            menu=menubar
        )
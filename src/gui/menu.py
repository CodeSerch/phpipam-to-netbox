import tkinter as tk


class AppMenu:

    def __init__(self, root, on_xls_to_csv=None):

        self.root = root
        self.on_xls_to_csv = on_xls_to_csv

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
            label="XLS → CSV",
            command=self.on_xls_to_csv
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

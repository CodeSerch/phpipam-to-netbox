import tkinter as tk
from tkinter import ttk


class MainWindow:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "phpIPAM → NetBox Converter"
        )

        self.root.geometry(
            "1050x820"
        )

        self.root.resizable(
            False,
            False
        )

        self.crear_variables()
        self.crear_interfaz()

    # ========================================================
    # VARIABLES
    # ========================================================

    def crear_variables(self):

        self.origen_var = tk.StringVar()
        self.destino_var = tk.StringVar()
        self.site_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value="Listo."
        )

        self.progress_text_var = tk.StringVar(
            value="0% - Esperando..."
        )

        self.time_var = tk.StringVar(
            value="Tiempo transcurrido: 0.0 s"
        )

    # ========================================================
    # INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        self.frame_principal = ttk.Frame(
            self.root,
            padding=10
        )

        self.frame_principal.pack(
            fill="both",
            expand=True
        )

        self.crear_encabezado()
        self.crear_configuracion()
        self.crear_botones()
        self.crear_progreso()
        self.crear_procesos()
        self.crear_resultados()
        self.crear_statusbar()

    # ========================================================
    # ENCABEZADO
    # ========================================================

    def crear_encabezado(self):

        ttk.Label(
            self.frame_principal,
            text="phpIPAM → NetBox Converter",
            font=("Segoe UI", 20, "bold")
        ).pack(
            pady=(5, 5)
        )

        ttk.Label(
            self.frame_principal,
            text=(
                "Herramienta para analizar y convertir "
                "datos de phpIPAM hacia NetBox."
            )
        ).pack(
            pady=(0, 15)
        )

    # ========================================================
    # CONFIGURACIÓN
    # ========================================================

    def crear_configuracion(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Configuración"
        )

        frame.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            frame,
            text="Carpeta de origen:"
        ).grid(
            row=0,
            column=0,
            padx=10,
            pady=8,
            sticky="w"
        )

        self.entry_origen = ttk.Entry(
            frame,
            textvariable=self.origen_var,
            width=70
        )

        self.entry_origen.grid(
            row=0,
            column=1,
            padx=10,
            pady=8
        )

        self.boton_origen = ttk.Button(
            frame,
            text="Examinar..."
        )

        self.boton_origen.grid(
            row=0,
            column=2,
            padx=10,
            pady=8
        )

        ttk.Label(
            frame,
            text="Carpeta de destino:"
        ).grid(
            row=1,
            column=0,
            padx=10,
            pady=8,
            sticky="w"
        )

        self.entry_destino = ttk.Entry(
            frame,
            textvariable=self.destino_var,
            width=70
        )

        self.entry_destino.grid(
            row=1,
            column=1,
            padx=10,
            pady=8
        )

        self.boton_destino = ttk.Button(
            frame,
            text="Examinar..."
        )

        self.boton_destino.grid(
            row=1,
            column=2,
            padx=10,
            pady=8
        )

        ttk.Label(
            frame,
            text="Site de NetBox:"
        ).grid(
            row=2,
            column=0,
            padx=10,
            pady=8,
            sticky="w"
        )

        self.entry_site = ttk.Entry(
            frame,
            textvariable=self.site_var,
            width=70
        )

        self.entry_site.grid(
            row=2,
            column=1,
            padx=10,
            pady=8,
            sticky="w"
        )

    # ========================================================
    # BOTONES
    # ========================================================

    def crear_botones(self):

        frame = ttk.Frame(
            self.frame_principal
        )

        frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.boton_analizar = ttk.Button(
            frame,
            text="Analizar",
            width=15
        )

        self.boton_analizar.pack(
            side="left",
            padx=5
        )

        self.boton_convertir = ttk.Button(
            frame,
            text="Convertir",
            width=15
        )

        self.boton_convertir.pack(
            side="left",
            padx=5
        )

        self.boton_detener = ttk.Button(
            frame,
            text="Detener",
            width=15,
            state="disabled"
        )

        self.boton_detener.pack(
            side="left",
            padx=5
        )

    # ========================================================
    # PROGRESO
    # ========================================================

    def crear_progreso(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Progreso"
        )

        frame.pack(
            fill="x",
            pady=(0, 10)
        )

        self.progressbar = ttk.Progressbar(
            frame,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.progressbar.pack(
            fill="x",
            padx=10,
            pady=(10, 5)
        )

        ttk.Label(
            frame,
            textvariable=self.progress_text_var
        ).pack(
            anchor="w",
            padx=10,
            pady=2
        )

        ttk.Label(
            frame,
            textvariable=self.time_var
        ).pack(
            anchor="w",
            padx=10,
            pady=(2, 10)
        )

    # ========================================================
    # PROCESOS
    # ========================================================

    def crear_procesos(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Proceso"
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=(0, 10)
        )

        self.lista_procesos = tk.Listbox(
            frame,
            height=10
        )

        self.lista_procesos.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # RESULTADOS
    # ========================================================

    def crear_resultados(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Resultados del análisis"
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=(0, 10)
        )

        columnas = (
            "estado",
            "tipo",
            "archivo",
            "registros"
        )

        self.tree_resultados = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=8
        )

        self.tree_resultados.heading(
            "estado",
            text="Estado"
        )

        self.tree_resultados.heading(
            "tipo",
            text="Tipo"
        )

        self.tree_resultados.heading(
            "archivo",
            text="Archivo / Información"
        )

        self.tree_resultados.heading(
            "registros",
            text="Registros"
        )

        self.tree_resultados.column(
            "estado",
            width=100,
            anchor="center"
        )

        self.tree_resultados.column(
            "tipo",
            width=180,
            anchor="w"
        )

        self.tree_resultados.column(
            "archivo",
            width=500,
            anchor="w"
        )

        self.tree_resultados.column(
            "registros",
            width=180,
            anchor="center"
        )

        self.tree_resultados.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

    # ========================================================
    # STATUS
    # ========================================================

    def crear_statusbar(self):

        frame = ttk.Frame(
            self.frame_principal
        )

        frame.pack(
            fill="x"
        )

        ttk.Label(
            frame,
            textvariable=self.status_var,
            anchor="w"
        ).pack(
            fill="x",
            padx=5,
            pady=5
        )
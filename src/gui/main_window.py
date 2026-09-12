
import tkinter as tk
from tkinter import ttk


class MainWindow:

    def __init__(self, root):

        self.root = root

        self.root.title("phpIPAM → NetBox Converter")
        self.root.geometry("1050x820")
        self.root.resizable(False, False)

        self.crear_variables()
        self.crear_interfaz()

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

    def crear_encabezado(self):

        titulo = ttk.Label(
            self.frame_principal,
            text="phpIPAM → NetBox Converter",
            font=("Segoe UI", 20, "bold")
        )

        titulo.pack(
            pady=(5, 5)
        )

        descripcion = ttk.Label(
            self.frame_principal,
            text=(
                "Herramienta para analizar y convertir "
                "datos de phpIPAM hacia NetBox."
            )
        )

        descripcion.pack(
            pady=(0, 15)
        )

    def crear_configuracion(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Configuración"
        )

        frame.pack(
            fill="x",
            pady=(0, 10)
        )

        # Origen

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

        ttk.Entry(
            frame,
            textvariable=self.origen_var,
            width=70
        ).grid(
            row=0,
            column=1,
            padx=10,
            pady=8
        )

        ttk.Button(
            frame,
            text="Examinar..."
        ).grid(
            row=0,
            column=2,
            padx=10,
            pady=8
        )

        # Destino

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

        ttk.Entry(
            frame,
            textvariable=self.destino_var,
            width=70
        ).grid(
            row=1,
            column=1,
            padx=10,
            pady=8
        )

        ttk.Button(
            frame,
            text="Examinar..."
        ).grid(
            row=1,
            column=2,
            padx=10,
            pady=8
        )

        # Site

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

        ttk.Entry(
            frame,
            textvariable=self.site_var,
            width=70
        ).grid(
            row=2,
            column=1,
            padx=10,
            pady=8,
            sticky="w"
        )

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

    def crear_resultados(self):

        frame = ttk.LabelFrame(
            self.frame_principal,
            text="Resultados"
        )

        frame.pack(
            fill="both",
            expand=True,
            pady=(0, 10)
        )

        columnas = (
            "categoria",
            "cantidad",
            "detalle"
        )

        self.tree_resultados = ttk.Treeview(
            frame,
            columns=columnas,
            show="headings",
            height=8
        )

        self.tree_resultados.heading(
            "categoria",
            text="Categoría"
        )

        self.tree_resultados.heading(
            "cantidad",
            text="Cantidad"
        )

        self.tree_resultados.heading(
            "detalle",
            text="Detalle"
        )

        self.tree_resultados.column(
            "categoria",
            width=180
        )

        self.tree_resultados.column(
            "cantidad",
            width=100,
            anchor="center"
        )

        self.tree_resultados.column(
            "detalle",
            width=600
        )

        self.tree_resultados.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

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


if __name__ == "__main__":

    root = tk.Tk()

    app = MainWindow(root)

    root.mainloop()        
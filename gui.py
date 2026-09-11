import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import threading
import time


# ============================================================
# CANCELACIÓN
# ============================================================

class ProcesoCancelado(Exception):
    pass


class App:

    # ========================================================
    # INICIALIZACIÓN
    # ========================================================

    def __init__(self):

        self.root = tk.Tk()

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

        # ----------------------------------------------------
        # VARIABLES
        # ----------------------------------------------------

        self.origen_var = tk.StringVar()

        self.destino_var = tk.StringVar()

        self.site_var = tk.StringVar()

        self.status_var = tk.StringVar(
            value=(
                "Estado: esperando selección "
                "de carpetas..."
            )
        )

        self.progress_text_var = tk.StringVar(
            value="Esperando..."
        )

        self.time_var = tk.StringVar(
            value="Tiempo transcurrido: 0.0 s"
        )

        # ----------------------------------------------------
        # DATOS
        # ----------------------------------------------------

        self.analisis = None

        self.roles_por_tipo = {}

        # ----------------------------------------------------
        # ESTADO DE TRABAJO
        # ----------------------------------------------------

        self.proceso_activo = False

        self.tiempo_inicio = None

        self.timer_id = None

        self.cancel_event = threading.Event()

        self.tipo_proceso = ""

        # ----------------------------------------------------
        # CREAR INTERFAZ
        # ----------------------------------------------------

        self.crear_interfaz()


    # ========================================================
    # CREAR INTERFAZ
    # ========================================================

    def crear_interfaz(self):

        # ----------------------------------------------------
        # FRAME PRINCIPAL
        # ----------------------------------------------------

        main_frame = ttk.Frame(
            self.root,
            padding=30
        )

        main_frame.pack(
            fill="both",
            expand=True
        )

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        title = ttk.Label(
            main_frame,
            text="phpIPAM → NetBox Converter",
            font=(
                "Segoe UI",
                20,
                "bold"
            )
        )

        title.pack(
            pady=(5, 10)
        )

        # ----------------------------------------------------
        # DESCRIPCIÓN
        # ----------------------------------------------------

        description = ttk.Label(
            main_frame,
            text=(
                "Analiza exportaciones CSV de phpIPAM "
                "y genera archivos CSV compatibles con NetBox."
            ),
            justify="center"
        )

        description.pack(
            pady=(0, 25)
        )

        # ====================================================
        # ORIGEN
        # ====================================================

        ttk.Label(
            main_frame,
            text="Carpeta de origen:"
        ).pack(
            anchor="w"
        )

        origen_frame = ttk.Frame(
            main_frame
        )

        origen_frame.pack(
            fill="x",
            pady=(5, 15)
        )

        self.origen_entry = ttk.Entry(
            origen_frame,
            textvariable=self.origen_var
        )

        self.origen_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.origen_button = ttk.Button(
            origen_frame,
            text="Examinar...",
            command=self.seleccionar_origen
        )

        self.origen_button.pack(
            side="left",
            padx=(10, 0)
        )

        # ====================================================
        # DESTINO
        # ====================================================

        ttk.Label(
            main_frame,
            text="Carpeta de destino:"
        ).pack(
            anchor="w"
        )

        destino_frame = ttk.Frame(
            main_frame
        )

        destino_frame.pack(
            fill="x",
            pady=(5, 15)
        )

        self.destino_entry = ttk.Entry(
            destino_frame,
            textvariable=self.destino_var
        )

        self.destino_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.destino_button = ttk.Button(
            destino_frame,
            text="Examinar...",
            command=self.seleccionar_destino
        )

        self.destino_button.pack(
            side="left",
            padx=(10, 0)
        )

        # ====================================================
        # SITE
        # ====================================================

        ttk.Label(
            main_frame,
            text="Site de destino en NetBox:"
        ).pack(
            anchor="w"
        )

        site_frame = ttk.Frame(
            main_frame
        )

        site_frame.pack(
            fill="x",
            pady=(5, 20)
        )

        self.site_entry = ttk.Entry(
            site_frame,
            textvariable=self.site_var
        )

        self.site_entry.pack(
            side="left",
            fill="x",
            expand=True
        )

        # ====================================================
        # BOTONES
        # ====================================================

        buttons_frame = ttk.Frame(
            main_frame
        )

        buttons_frame.pack(
            pady=(0, 20)
        )

        self.analizar_button = ttk.Button(
            buttons_frame,
            text="Analizar",
            command=self.analizar
        )

        self.analizar_button.pack(
            side="left",
            padx=5
        )

        self.convertir_button = ttk.Button(
            buttons_frame,
            text="Convertir",
            command=self.convertir
        )

        self.convertir_button.pack(
            side="left",
            padx=5
        )

        self.detener_button = ttk.Button(
            buttons_frame,
            text="Detener",
            command=self.detener,
            state="disabled"
        )

        self.detener_button.pack(
            side="left",
            padx=5
        )

        # ====================================================
        # PROGRESO
        # ====================================================

        progress_frame = ttk.LabelFrame(
            main_frame,
            text="Progreso",
            padding=15
        )

        progress_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.progressbar = ttk.Progressbar(
            progress_frame,
            orient="horizontal",
            mode="determinate",
            maximum=100
        )

        self.progressbar.pack(
            fill="x",
            pady=(0, 10)
        )

        ttk.Label(
            progress_frame,
            textvariable=self.progress_text_var
        ).pack(
            anchor="w"
        )

        ttk.Label(
            progress_frame,
            textvariable=self.time_var
        ).pack(
            anchor="w",
            pady=(5, 0)
        )

        # ====================================================
        # DESGLOSE DE PROCESOS
        # ====================================================

        proceso_frame = ttk.LabelFrame(
            main_frame,
            text="Procesos",
            padding=10
        )

        proceso_frame.pack(
            fill="x",
            pady=(0, 15)
        )

        self.proceso_listbox = tk.Listbox(
            proceso_frame,
            height=5,
            activestyle="none"
        )

        self.proceso_listbox.pack(
            fill="x"
        )

        # ====================================================
        # RESULTADOS
        # ====================================================

        ttk.Label(
            main_frame,
            text="Resultados del análisis:",
            font=(
                "Segoe UI",
                11,
                "bold"
            )
        ).pack(
            anchor="w",
            pady=(0, 8)
        )

        tabla_frame = ttk.Frame(
            main_frame
        )

        tabla_frame.pack(
            fill="both",
            expand=True
        )

        columnas = (
            "estado",
            "tipo",
            "archivo",
            "registros"
        )

        self.tabla = ttk.Treeview(
            tabla_frame,
            columns=columnas,
            show="headings",
            height=11
        )

        # ----------------------------------------------------
        # HEADINGS
        # ----------------------------------------------------

        self.tabla.heading(
            "estado",
            text="Estado"
        )

        self.tabla.heading(
            "tipo",
            text="Tipo"
        )

        self.tabla.heading(
            "archivo",
            text="Archivo / Información"
        )

        self.tabla.heading(
            "registros",
            text="Registros"
        )

        # ----------------------------------------------------
        # COLUMNAS
        # ----------------------------------------------------

        self.tabla.column(
            "estado",
            width=100,
            anchor="center"
        )

        self.tabla.column(
            "tipo",
            width=180,
            anchor="w"
        )

        self.tabla.column(
            "archivo",
            width=500,
            anchor="w"
        )

        self.tabla.column(
            "registros",
            width=180,
            anchor="center"
        )

        # ----------------------------------------------------
        # SCROLLBAR
        # ----------------------------------------------------

        scrollbar = ttk.Scrollbar(
            tabla_frame,
            orient="vertical",
            command=self.tabla.yview
        )

        self.tabla.configure(
            yscrollcommand=scrollbar.set
        )

        self.tabla.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        # ====================================================
        # ESTADO
        # ====================================================

        ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief="sunken",
            anchor="w"
        ).pack(
            fill="x",
            pady=(15, 0)
        )


    # ========================================================
    # SELECCIONAR ORIGEN
    # ========================================================

    def seleccionar_origen(self):

        if self.proceso_activo:
            return

        carpeta = filedialog.askdirectory(
            title=(
                "Seleccionar carpeta de "
                "exportación phpIPAM"
            )
        )

        if carpeta:

            self.origen_var.set(
                carpeta
            )

            self.status_var.set(
                "Estado: carpeta de origen seleccionada."
            )


    # ========================================================
    # SELECCIONAR DESTINO
    # ========================================================

    def seleccionar_destino(self):

        if self.proceso_activo:
            return

        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta de destino"
        )

        if carpeta:

            self.destino_var.set(
                carpeta
            )

            self.status_var.set(
                "Estado: carpeta de destino seleccionada."
            )


    # ========================================================
    # LIMPIAR TABLA
    # ========================================================

    def limpiar_tabla(self):

        for item in self.tabla.get_children():

            self.tabla.delete(
                item
            )


    # ========================================================
    # LIMPIAR PROCESOS
    # ========================================================

    def limpiar_procesos(self):

        self.proceso_listbox.delete(
            0,
            tk.END
        )


    # ========================================================
    # AGREGAR PROCESO
    # ========================================================

    def agregar_proceso(
        self,
        mensaje,
    ):

        texto = f"• {mensaje}"

        self.proceso_listbox.insert(
            tk.END,
            texto
        )

        self.proceso_listbox.see(
            tk.END
        )


    # ========================================================
    # CONTROL DE BOTONES
    # ========================================================

    def bloquear_interfaz(self):

        self.proceso_activo = True

        self.analizar_button.config(
            state="disabled"
        )

        self.convertir_button.config(
            state="disabled"
        )

        self.detener_button.config(
            state="normal"
        )

        self.origen_button.config(
            state="disabled"
        )

        self.destino_button.config(
            state="disabled"
        )

        self.origen_entry.config(
            state="disabled"
        )

        self.destino_entry.config(
            state="disabled"
        )

        self.site_entry.config(
            state="disabled"
        )


    def desbloquear_interfaz(self):

        self.proceso_activo = False

        self.analizar_button.config(
            state="normal"
        )

        self.convertir_button.config(
            state="normal"
        )

        self.detener_button.config(
            state="disabled"
        )

        self.origen_button.config(
            state="normal"
        )

        self.destino_button.config(
            state="normal"
        )

        self.origen_entry.config(
            state="normal"
        )

        self.destino_entry.config(
            state="normal"
        )

        self.site_entry.config(
            state="normal"
        )


    # ========================================================
    # CRONÓMETRO
    # ========================================================

    def iniciar_cronometro(self):

        self.tiempo_inicio = time.perf_counter()

        self.actualizar_cronometro()


    def actualizar_cronometro(self):

        if not self.proceso_activo:
            return

        if self.tiempo_inicio is None:
            return

        tiempo = (
            time.perf_counter()
            - self.tiempo_inicio
        )

        self.time_var.set(
            f"Tiempo transcurrido: {tiempo:.1f} s"
        )

        self.timer_id = self.root.after(
            100,
            self.actualizar_cronometro
        )


    def detener_cronometro(self):

        if self.timer_id is not None:

            self.root.after_cancel(
                self.timer_id
            )

            self.timer_id = None

        if self.tiempo_inicio is not None:

            tiempo = (
                time.perf_counter()
                - self.tiempo_inicio
            )

            self.time_var.set(
                f"Tiempo total: {tiempo:.2f} s"
            )


    # ========================================================
    # ACTUALIZAR PROGRESO
    # ========================================================

    def actualizar_progreso(
        self,
        porcentaje,
        mensaje,
    ):

        self.progressbar["value"] = porcentaje

        self.progress_text_var.set(
            f"{porcentaje}% - {mensaje}"
        )

        self.agregar_proceso(
            mensaje
        )


    # ========================================================
    # CALLBACK DESDE THREAD
    # ========================================================

    def progreso_desde_thread(
        self,
        porcentaje,
        mensaje,
    ):
        """
        Se ejecuta dentro del thread de trabajo.

        Si se solicitó detener el proceso, lanza
        ProcesoCancelado y corta el trabajo.
        """

        if self.cancel_event.is_set():

            raise ProcesoCancelado()

        self.root.after(
            0,
            self.actualizar_progreso,
            porcentaje,
            mensaje
        )


    # ========================================================
    # DETENER
    # ========================================================

    def detener(self):

        if not self.proceso_activo:
            return

        respuesta = messagebox.askyesno(
            "Detener proceso",
            (
                "¿Querés detener el proceso actual?\n\n"
                "Los archivos que ya se hayan generado "
                "pueden quedar incompletos."
            )
        )

        if not respuesta:
            return

        self.cancel_event.set()

        self.detener_button.config(
            state="disabled"
        )

        self.status_var.set(
            "Estado: deteniendo proceso..."
        )

        self.progress_text_var.set(
            "Cancelando..."
        )

        self.agregar_proceso(
            "Solicitud de detención enviada."
        )


    # ========================================================
    # ANALIZAR
    # ========================================================

    def analizar(self):

        if self.proceso_activo:
            return

        origen = (
            self.origen_var
            .get()
            .strip()
        )

        if not origen:

            messagebox.showwarning(
                "Origen faltante",
                "Seleccioná primero la carpeta de origen."
            )

            return

        self.tipo_proceso = "analisis"

        self.cancel_event.clear()

        self.limpiar_tabla()

        self.limpiar_procesos()

        self.progressbar["value"] = 0

        self.progress_text_var.set(
            "0% - Preparando análisis..."
        )

        self.status_var.set(
            "Estado: analizando exportación..."
        )

        self.bloquear_interfaz()

        self.iniciar_cronometro()

        self.agregar_proceso(
            "Iniciando análisis."
        )

        hilo = threading.Thread(
            target=self.ejecutar_analisis,
            args=(origen,),
            daemon=True
        )

        hilo.start()


    # ========================================================
    # EJECUTAR ANÁLISIS
    # ========================================================

    def ejecutar_analisis(
        self,
        origen,
    ):

        try:

            from analyzer import analizar_exportacion

            resultado = analizar_exportacion(
                origen,
                progress_callback=self.progreso_desde_thread
            )

            if self.cancel_event.is_set():

                raise ProcesoCancelado()

            self.root.after(
                0,
                self.finalizar_analisis,
                resultado
            )

        except ProcesoCancelado:

            self.root.after(
                0,
                self.finalizar_proceso_cancelado
            )

        except Exception as error:

            self.root.after(
                0,
                self.error_analisis,
                error
            )


    # ========================================================
    # FINALIZAR ANÁLISIS
    # ========================================================

    def finalizar_analisis(
        self,
        resultado,
    ):

        self.analisis = resultado

        self.cargar_roles_por_tipo(
            resultado
        )

        self.limpiar_tabla()

        self.mostrar_resultados(
            resultado
        )

        self.progressbar["value"] = 100

        self.progress_text_var.set(
            "100% - Análisis terminado."
        )

        self.status_var.set(
            "Estado: análisis terminado."
        )

        self.agregar_proceso(
            "Análisis terminado correctamente."
        )

        self.detener_cronometro()

        self.desbloquear_interfaz()


    # ========================================================
    # CARGAR ROLES
    # ========================================================

    def cargar_roles_por_tipo(
        self,
        analisis,
    ):

        self.roles_por_tipo = {}

        resultados = (
            analisis
            .get(
                "roles",
                {}
            )
            .get(
                "resultados",
                []
            )
        )

        for resultado in resultados:

            tipo = str(
                resultado.get(
                    "device_type",
                    ""
                )
            ).strip()

            role = str(
                resultado.get(
                    "recommended_role",
                    ""
                )
            ).strip()

            if not tipo:
                continue

            self.roles_por_tipo[
                tipo.lower()
            ] = role


    # ========================================================
    # MOSTRAR RESULTADOS
    # ========================================================

    def mostrar_resultados(
        self,
        resultado,
    ):

        # ----------------------------------------------------
        # ARCHIVOS
        # ----------------------------------------------------

        for item in resultado.get(
            "archivos",
            []
        ):

            self.tabla.insert(
                "",
                "end",
                values=(
                    item.get(
                        "estado",
                        "-"
                    ),
                    item.get(
                        "tipo",
                        "-"
                    ),
                    item.get(
                        "archivo",
                        "-"
                    ),
                    item.get(
                        "registros",
                        "-"
                    ),
                )
            )

        # ----------------------------------------------------
        # MANUFACTURERS
        # ----------------------------------------------------

        manufacturers = resultado.get(
            "manufacturers",
            {}
        )

        self.tabla.insert(
            "",
            "end",
            values=(
                "DERIVADO",
                "Manufacturers",
                "Desde Device Types",
                (
                    f"{manufacturers.get('resueltos', 0)} "
                    f"resueltos | "
                    f"{manufacturers.get('manual', 0)} manual | "
                    f"{manufacturers.get('desconocidos', 0)} desconocidos"
                ),
            )
        )

        # ----------------------------------------------------
        # ROLES
        # ----------------------------------------------------

        roles = resultado.get(
            "roles",
            {}
        )

        roles_detectados = roles.get(
            "roles_detectados",
            []
        )

        for role in roles_detectados:

            self.tabla.insert(
                "",
                "end",
                values=(
                    "RECOMENDADO",
                    "Role",
                    role.get(
                        "role",
                        "-"
                    ),
                    (
                        f"{role.get('devices', 0)} "
                        f"devices | "
                        f"confianza "
                        f"{role.get('confidence', 'unknown')}"
                    ),
                )
            )


    # ========================================================
    # ERROR ANÁLISIS
    # ========================================================

    def error_analisis(
        self,
        error,
    ):

        self.detener_cronometro()

        self.progress_text_var.set(
            "Error durante el análisis."
        )

        self.status_var.set(
            "Estado: error durante el análisis."
        )

        self.agregar_proceso(
            f"Error: {error}"
        )

        self.desbloquear_interfaz()

        messagebox.showerror(
            "Error durante el análisis",
            str(error)
        )


    # ========================================================
    # CONVERTIR
    # ========================================================

    def convertir(self):

        if self.proceso_activo:
            return

        origen = (
            self.origen_var
            .get()
            .strip()
        )

        destino = (
            self.destino_var
            .get()
            .strip()
        )

        site = (
            self.site_var
            .get()
            .strip()
        )

        # ----------------------------------------------------
        # VALIDAR ORIGEN
        # ----------------------------------------------------

        if not origen:

            messagebox.showwarning(
                "Origen faltante",
                "Seleccioná primero la carpeta de origen."
            )

            return

        # ----------------------------------------------------
        # VALIDAR DESTINO
        # ----------------------------------------------------

        if not destino:

            messagebox.showwarning(
                "Destino faltante",
                "Seleccioná primero la carpeta de destino."
            )

            return

        # ----------------------------------------------------
        # VALIDAR SITE
        # ----------------------------------------------------

        if not site:

            messagebox.showwarning(
                "Site faltante",
                "Ingresá el Site de destino de NetBox."
            )

            return

        # ----------------------------------------------------
        # VALIDAR ANÁLISIS
        # ----------------------------------------------------

        if self.analisis is None:

            messagebox.showwarning(
                "Análisis requerido",
                "Primero ejecutá el análisis."
            )

            return

        self.tipo_proceso = "conversion"

        self.cancel_event.clear()

        self.limpiar_procesos()

        self.progressbar["value"] = 0

        self.progress_text_var.set(
            "0% - Preparando conversión..."
        )

        self.status_var.set(
            "Estado: convirtiendo exportación..."
        )

        self.bloquear_interfaz()

        self.iniciar_cronometro()

        self.agregar_proceso(
            "Iniciando conversión."
        )

        hilo = threading.Thread(
            target=self.ejecutar_conversion,
            args=(
                origen,
                destino,
                site,
                self.roles_por_tipo,
                self.analisis,
            ),
            daemon=True
        )

        hilo.start()


    # ========================================================
    # EJECUTAR CONVERSIÓN
    # ========================================================

    def ejecutar_conversion(
        self,
        origen,
        destino,
        site,
        roles_por_tipo,
        analisis,
    ):

        try:

            from converter import convertir_exportacion

            resultado = convertir_exportacion(
                origen,
                destino,
                site,
                roles_por_tipo,
                analisis,
                progress_callback=self.progreso_desde_thread
            )

            if self.cancel_event.is_set():

                raise ProcesoCancelado()

            self.root.after(
                0,
                self.finalizar_conversion,
                resultado
            )

        except ProcesoCancelado:

            self.root.after(
                0,
                self.finalizar_proceso_cancelado
            )

        except Exception as error:

            self.root.after(
                0,
                self.error_conversion,
                error
            )


    # ========================================================
    # FINALIZAR CONVERSIÓN
    # ========================================================

    def finalizar_conversion(
        self,
        resultado,
    ):

        self.progressbar["value"] = 100

        self.progress_text_var.set(
            "100% - Conversión terminada."
        )

        self.status_var.set(
            "Estado: conversión terminada."
        )

        self.agregar_proceso(
            "Conversión terminada correctamente."
        )

        self.detener_cronometro()

        self.desbloquear_interfaz()

        archivos_generados = []

        for nombre, informacion in resultado.items():

            if isinstance(
                informacion,
                dict
            ):

                archivo = informacion.get(
                    "archivo"
                )

                registros = informacion.get(
                    "registros"
                )

                errores = informacion.get(
                    "errores",
                    []
                )

                if archivo:

                    texto = (
                        f"{nombre}: "
                        f"{registros} registros"
                    )

                    if errores:

                        texto += (
                            f" | "
                            f"{len(errores)} errores"
                        )

                    archivos_generados.append(
                        texto
                    )

            else:

                archivos_generados.append(
                    str(nombre)
                )

        if not archivos_generados:

            mensaje = (
                "La conversión terminó, "
                "pero no se generaron archivos."
            )

        else:

            mensaje = (
                "Conversión terminada.\n\n"
                "Archivos generados:\n"
                + "\n".join(
                    archivos_generados
                )
            )

        messagebox.showinfo(
            "Conversión",
            mensaje
        )


    # ========================================================
    # FINALIZAR PROCESO CANCELADO
    # ========================================================

    def finalizar_proceso_cancelado(self):

        self.detener_cronometro()

        self.progress_text_var.set(
            "Proceso detenido."
        )

        self.status_var.set(
            "Estado: proceso detenido por el usuario."
        )

        self.agregar_proceso(
            "Proceso detenido por el usuario."
        )

        self.desbloquear_interfaz()


    # ========================================================
    # ERROR CONVERSIÓN
    # ========================================================

    def error_conversion(
        self,
        error,
    ):

        self.detener_cronometro()

        self.progress_text_var.set(
            "Error durante la conversión."
        )

        self.status_var.set(
            "Estado: error durante la conversión."
        )

        self.agregar_proceso(
            f"Error: {error}"
        )

        self.desbloquear_interfaz()

        messagebox.showerror(
            "Error durante la conversión",
            str(error)
        )


    # ========================================================
    # EJECUTAR
    # ========================================================

    def run(self):

        self.root.mainloop()
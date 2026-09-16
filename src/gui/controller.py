from tkinter import filedialog

from gui.dialogs import (
    mostrar_error,
    mostrar_advertencia,
    mostrar_info,
    confirmar,
)
from gui.progress import (
    ProgressManager,
    ProcesoCancelado,
)
from gui.workers import Worker


class AppController:

    def __init__(self, root, state, view):

        self.root = root
        self.state = state
        self.view = view

        self.progress = ProgressManager(
            root=self.root,
            state=self.state,
            progressbar=self.view.progressbar,
            progress_text_var=self.view.progress_text_var,
            time_var=self.view.time_var,
            agregar_proceso_callback=self.agregar_proceso,
        )

        self.conectar_eventos()

    # ========================================================
    # EVENTOS
    # ========================================================

    def conectar_eventos(self):

        self.view.boton_origen.config(
            command=self.seleccionar_origen
        )

        self.view.boton_destino.config(
            command=self.seleccionar_destino
        )

        self.view.boton_analizar.config(
            command=self.analizar
        )

        self.view.boton_convertir.config(
            command=self.convertir
        )

        self.view.boton_detener.config(
            command=self.detener
        )

    # ========================================================
    # CARPETAS
    # ========================================================

    def seleccionar_origen(self):

        if self.state.proceso_activo:
            return

        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta de exportación phpIPAM"
        )

        if carpeta:

            self.view.origen_var.set(
                carpeta
            )

            self.view.status_var.set(
                "Estado: carpeta de origen seleccionada."
            )

    def seleccionar_destino(self):

        if self.state.proceso_activo:
            return

        carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta de destino"
        )

        if carpeta:

            self.view.destino_var.set(
                carpeta
            )

            self.view.status_var.set(
                "Estado: carpeta de destino seleccionada."
            )

    # ========================================================
    # LIMPIEZA
    # ========================================================

    def limpiar_tabla(self):

        for item in self.view.tree_resultados.get_children():

            self.view.tree_resultados.delete(
                item
            )

    def limpiar_procesos(self):

        self.view.lista_procesos.delete(
            0,
            "end"
        )

    def agregar_proceso(self, mensaje):

        texto = f"• {mensaje}"

        self.view.lista_procesos.insert(
            "end",
            texto
        )

        self.view.lista_procesos.see(
            "end"
        )

    # ========================================================
    # BLOQUEO DE INTERFAZ
    # ========================================================

    def bloquear_interfaz(self):

        self.state.proceso_activo = True

        self.view.boton_analizar.config(
            state="disabled"
        )

        self.view.boton_convertir.config(
            state="disabled"
        )

        self.view.boton_detener.config(
            state="normal"
        )

        self.view.boton_origen.config(
            state="disabled"
        )

        self.view.boton_destino.config(
            state="disabled"
        )

        self.view.entry_origen.config(
            state="disabled"
        )

        self.view.entry_destino.config(
            state="disabled"
        )

        self.view.entry_site.config(
            state="disabled"
        )

    def desbloquear_interfaz(self):

        self.state.proceso_activo = False

        self.view.boton_analizar.config(
            state="normal"
        )

        self.view.boton_convertir.config(
            state="normal"
        )

        self.view.boton_detener.config(
            state="disabled"
        )

        self.view.boton_origen.config(
            state="normal"
        )

        self.view.boton_destino.config(
            state="normal"
        )

        self.view.entry_origen.config(
            state="normal"
        )

        self.view.entry_destino.config(
            state="normal"
        )

        self.view.entry_site.config(
            state="normal"
        )

    # ========================================================
    # ANÁLISIS
    # ========================================================

    def analizar(self):

        if self.state.proceso_activo:
            return

        origen = self.view.origen_var.get().strip()

        if not origen:

            mostrar_advertencia(
                "Origen faltante",
                "Seleccioná primero la carpeta de origen."
            )

            return

        self.state.tipo_proceso = "analisis"

        self.state.cancel_event.clear()

        self.limpiar_tabla()
        self.limpiar_procesos()

        self.view.progressbar["value"] = 0

        self.view.progress_text_var.set(
            "0% - Preparando análisis..."
        )

        self.view.status_var.set(
            "Estado: analizando exportación..."
        )

        self.bloquear_interfaz()

        self.progress.iniciar_cronometro()

        self.agregar_proceso(
            "Iniciando análisis."
        )

        worker = Worker(
            target=lambda: self.ejecutar_analisis(
                origen
            )
        )

        worker.ejecutar()

    def ejecutar_analisis(self, origen):

        try:

            from analyzer import analizar_exportacion

            resultado = analizar_exportacion(
                origen,
                progress_callback=(
                    self.progress.progreso_desde_thread
                )
            )

            if self.state.cancel_event.is_set():

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

    def finalizar_analisis(self, resultado):

        self.state.analisis = resultado

        self.cargar_roles_por_tipo(
            resultado
        )

        self.limpiar_tabla()

        self.mostrar_resultados(
            resultado
        )

        self.view.progressbar["value"] = 100

        self.view.progress_text_var.set(
            "100% - Análisis terminado."
        )

        self.view.status_var.set(
            "Estado: análisis terminado."
        )

        self.agregar_proceso(
            "Análisis terminado correctamente."
        )

        self.progress.detener_cronometro()

        self.desbloquear_interfaz()

    def cargar_roles_por_tipo(self, analisis):

        self.state.roles_por_tipo = {}

        resultados = (
            analisis
            .get("roles", {})
            .get("resultados", [])
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

            self.state.roles_por_tipo[
                tipo.lower()
            ] = role

    def mostrar_resultados(self, resultado):

        for item in resultado.get(
            "archivos",
            []
        ):

            self.view.tree_resultados.insert(
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

        manufacturers = resultado.get(
            "manufacturers",
            {}
        )

        self.view.tree_resultados.insert(
            "",
            "end",
            values=(
                "DERIVADO",
                "Manufacturers",
                "Desde Device Types",
                (
                    f"{manufacturers.get('resueltos', 0)} "
                    f"resueltos | "
                    f"{manufacturers.get('manual', 0)} "
                    f"manual | "
                    f"{manufacturers.get('desconocidos', 0)} "
                    f"desconocidos"
                ),
            )
        )

        roles = resultado.get(
            "roles",
            {}
        )

        roles_detectados = roles.get(
            "roles_detectados",
            []
        )

        for role in roles_detectados:

            self.view.tree_resultados.insert(
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

    def error_analisis(self, error):

        self.progress.detener_cronometro()

        self.view.progress_text_var.set(
            "Error durante el análisis."
        )

        self.view.status_var.set(
            "Estado: error durante el análisis."
        )

        self.agregar_proceso(
            f"Error: {error}"
        )

        self.desbloquear_interfaz()

        mostrar_error(
            "Error durante el análisis",
            str(error)
        )

    # ========================================================
    # CONVERSIÓN
    # ========================================================

    def convertir(self):

        if self.state.proceso_activo:
            return

        origen = self.view.origen_var.get().strip()
        destino = self.view.destino_var.get().strip()
        site = self.view.site_var.get().strip()

        if not origen:

            mostrar_advertencia(
                "Origen faltante",
                "Seleccioná primero la carpeta de origen."
            )

            return

        if not destino:

            mostrar_advertencia(
                "Destino faltante",
                "Seleccioná primero la carpeta de destino."
            )

            return

        if not site:

            mostrar_advertencia(
                "Site faltante",
                "Ingresá el Site de NetBox."
            )

            return

        if not self.state.analisis:

            mostrar_advertencia(
                "Análisis requerido",
                "Primero ejecutá el análisis antes de convertir."
            )

            return

        self.state.tipo_proceso = "conversion"

        self.state.cancel_event.clear()

        self.limpiar_procesos()

        self.view.progressbar["value"] = 0

        self.view.progress_text_var.set(
            "0% - Preparando conversión..."
        )

        self.view.status_var.set(
            "Estado: convirtiendo exportación..."
        )

        self.bloquear_interfaz()

        self.progress.iniciar_cronometro()

        self.agregar_proceso(
            "Iniciando conversión."
        )

        worker = Worker(
            target=lambda: self.ejecutar_conversion(
                origen,
                destino,
                site
            )
        )

        worker.ejecutar()

    def ejecutar_conversion(
        self,
        origen,
        destino,
        site
    ):

        try:

            from converter import convertir_exportacion

            resultado = convertir_exportacion(
                carpeta_origen=origen,
                carpeta_destino=destino,
                site=site,
                roles_por_tipo=self.state.roles_por_tipo,
                analisis=self.state.analisis,
                progress_callback=(
                    self.progress.progreso_desde_thread
                )
            )

            if self.state.cancel_event.is_set():

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

    def finalizar_conversion(self, resultado):

        self.view.progressbar["value"] = 100

        self.view.progress_text_var.set(
            "100% - Conversión terminada."
        )

        self.view.status_var.set(
            "Estado: conversión terminada."
        )

        self.agregar_proceso(
            "Conversión terminada correctamente."
        )

        self.progress.detener_cronometro()

        self.desbloquear_interfaz()

        archivos_generados = []

        if isinstance(resultado, dict):

            archivos_generados = resultado.get(
                "archivos",
                []
            )

        if archivos_generados:

            mensaje = (
                "Conversión terminada correctamente.\n\n"
                "Archivos generados:\n\n"
                + "\n".join(
                    str(archivo)
                    for archivo in archivos_generados
                )
            )

        else:

            mensaje = (
                "Conversión terminada correctamente."
            )

        mostrar_info(
            "Conversión completada",
            mensaje
        )

    def error_conversion(self, error):

        self.progress.detener_cronometro()

        self.view.progress_text_var.set(
            "Error durante la conversión."
        )

        self.view.status_var.set(
            "Estado: error durante la conversión."
        )

        self.agregar_proceso(
            f"Error: {error}"
        )

        self.desbloquear_interfaz()

        mostrar_error(
            "Error durante la conversión",
            str(error)
        )

    # ========================================================
    # DETENER
    # ========================================================

    def detener(self):

        if not self.state.proceso_activo:
            return

        respuesta = confirmar(
            "Detener proceso",
            (
                "¿Querés detener el proceso actual?\n\n"
                "Los archivos que ya se hayan generado "
                "pueden quedar incompletos."
            )
        )

        if not respuesta:
            return

        self.state.cancel_event.set()

        self.view.boton_detener.config(
            state="disabled"
        )

        self.view.status_var.set(
            "Estado: deteniendo proceso..."
        )

        self.view.progress_text_var.set(
            "Cancelando..."
        )

        self.agregar_proceso(
            "Solicitud de detención enviada."
        )

    def finalizar_proceso_cancelado(self):

        self.progress.detener_cronometro()

        self.view.progress_text_var.set(
            "Proceso detenido."
        )

        self.view.status_var.set(
            "Estado: proceso detenido por el usuario."
        )

        self.agregar_proceso(
            "Proceso detenido por el usuario."
        )

        self.desbloquear_interfaz()
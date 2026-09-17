import time


class ProcesoCancelado(Exception):
    pass


class ProgressManager:

    def __init__(
        self,
        root,
        state,
        progressbar,
        progress_text_var,
        time_var,
        agregar_proceso_callback,
    ):
        self.root = root
        self.state = state
        self.progressbar = progressbar
        self.progress_text_var = progress_text_var
        self.time_var = time_var
        self.agregar_proceso = agregar_proceso_callback

    # --------------------------------------------------------
    # CRONÓMETRO
    # --------------------------------------------------------

    def iniciar_cronometro(self):

        self.state.tiempo_inicio = time.perf_counter()

        self.actualizar_cronometro()

    def actualizar_cronometro(self):

        if not self.state.proceso_activo:
            return

        if self.state.tiempo_inicio is None:
            return

        tiempo = (
            time.perf_counter()
            - self.state.tiempo_inicio
        )

        self.time_var.set(
            f"Tiempo transcurrido: {tiempo:.1f} s"
        )

        self.state.timer_id = self.root.after(
            100,
            self.actualizar_cronometro
        )

    def detener_cronometro(self):

        if self.state.timer_id is not None:

            self.root.after_cancel(
                self.state.timer_id
            )

            self.state.timer_id = None

        if self.state.tiempo_inicio is not None:

            tiempo = (
                time.perf_counter()
                - self.state.tiempo_inicio
            )

            self.time_var.set(
                f"Tiempo total: {tiempo:.2f} s"
            )

    # --------------------------------------------------------
    # PROGRESO
    # --------------------------------------------------------

    def actualizar_progreso(
        self,
        porcentaje,
        mensaje,
    ):

        self.progressbar["value"] = porcentaje

        self.progress_text_var.set(
            f"{porcentaje}% - {mensaje}"
        )

        self.agregar_proceso(mensaje)

    # --------------------------------------------------------
    # CALLBACK DESDE THREAD
    # --------------------------------------------------------

    def progreso_desde_thread(
        self,
        porcentaje,
        mensaje,
    ):

        if self.state.cancel_event.is_set():
            raise ProcesoCancelado()

        self.root.after(
            0,
            self.actualizar_progreso,
            porcentaje,
            mensaje
        )
import threading


class AppState:

    def __init__(self):

        # Datos del análisis
        self.analisis = None
        self.roles_por_tipo = {}

        # Estado del proceso
        self.proceso_activo = False
        self.tipo_proceso = ""

        # Cronómetro
        self.tiempo_inicio = None
        self.timer_id = None

        # Cancelación
        self.cancel_event = threading.Event()
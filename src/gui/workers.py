import threading


class Worker:

    def __init__(
        self,
        target,
        callback=None,
        error_callback=None,
    ):
        self.target = target
        self.callback = callback
        self.error_callback = error_callback

    def ejecutar(self):

        thread = threading.Thread(
            target=self._run,
            daemon=True
        )

        thread.start()

        return thread

    def _run(self):

        try:

            resultado = self.target()

            if self.callback:
                self.callback(resultado)

        except Exception as error:

            if self.error_callback:
                self.error_callback(error)
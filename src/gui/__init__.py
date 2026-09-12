def __init__(self):

    self.root = tk.Tk()

    self.root.title("phpIPAM → NetBox Converter")
    self.root.geometry("1050x820")
    self.root.resizable(False, False)

    # Estado de la aplicación
    self.state = AppState()

    # Variables de la interfaz
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

    self.crear_interfaz()
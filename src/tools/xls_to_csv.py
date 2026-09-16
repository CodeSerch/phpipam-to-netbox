from pathlib import Path

import pandas as pd


def convertir_xls_a_csv(archivo_origen, archivo_destino):
    """Convierte un archivo XLS en CSV.

    Args:
        archivo_origen: Ruta al archivo .xls de entrada.
        archivo_destino: Ruta donde se guardará el .csv.

    Returns:
        dict: Información del archivo generado y cantidad de registros.
    """
    origen = Path(archivo_origen)
    destino = Path(archivo_destino)

    if not origen.exists():
        raise FileNotFoundError(
            f"No se encontró el archivo de origen: {origen}"
        )

    if origen.suffix.lower() != ".xls":
        raise ValueError(
            "El archivo de origen debe tener extensión .xls."
        )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe = pd.read_excel(
        origen,
        engine="xlrd"
    )

    dataframe.to_csv(
        destino,
        index=False,
        encoding="utf-8-sig"
    )

    return {
        "archivo": str(destino),
        "registros": len(dataframe),
    }

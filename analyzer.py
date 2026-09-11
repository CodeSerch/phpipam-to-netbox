from pathlib import Path

import pandas as pd

from manufacturer_finder import buscar_manufacturer
from role_mapper import recomendar_role


# ============================================================
# ARCHIVOS ESPERADOS
# ============================================================

ARCHIVOS_ESPERADOS = {
    "Devices": "*_devices_export.csv",
    "Device Types": "*_deviceTypes_export.csv",
    "IP Addresses": "*_ip_address_export.csv",
    "Subnets": "*_subnets_export.csv",
    "VLAN": "*_VLAN_export.csv",
    "VRF": "*_VRF_export.csv",
}


# ============================================================
# PROGRESO
# ============================================================

def actualizar_progreso(
    callback,
    porcentaje: int,
    mensaje: str,
):
    """
    Actualiza el progreso si se proporcionó un callback.
    """

    if callback is not None:

        callback(
            porcentaje,
            mensaje,
        )


# ============================================================
# UTILIDADES
# ============================================================

def leer_csv(
    archivo: str | Path,
) -> pd.DataFrame:
    """
    Lee un CSV de phpIPAM detectando automáticamente
    el separador.
    """

    return (
        pd.read_csv(
            archivo,
            sep=None,
            engine="python",
            dtype=str,
        )
        .fillna("")
    )


def buscar_archivo(
    carpeta: Path,
    patron: str,
) -> Path | None:
    """
    Busca el primer archivo que coincida con el patrón.
    """

    archivos = sorted(
        carpeta.glob(patron)
    )

    if not archivos:
        return None

    return archivos[0]


def normalizar_valor(
    valor,
) -> str:
    """
    Convierte un valor a texto limpio.
    """

    if valor is None:
        return ""

    return str(
        valor
    ).strip()


# ============================================================
# OBTENER TIPOS
# ============================================================

def obtener_tipos(
    archivos_encontrados: dict[str, pd.DataFrame],
) -> list[str]:

    tipos = set()

    # --------------------------------------------------------
    # DEVICES
    # --------------------------------------------------------

    df_devices = archivos_encontrados.get(
        "Devices"
    )

    if (
        df_devices is not None
        and "type" in df_devices.columns
    ):

        valores = (
            df_devices["type"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .tolist()
        )

        tipos.update(
            valores
        )

    # --------------------------------------------------------
    # DEVICE TYPES
    # --------------------------------------------------------

    df_device_types = archivos_encontrados.get(
        "Device Types"
    )

    if (
        df_device_types is not None
        and "Name" in df_device_types.columns
    ):

        valores = (
            df_device_types["Name"]
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .tolist()
        )

        tipos.update(
            valores
        )

    return sorted(
        tipos
    )


# ============================================================
# OBTENER DEVICES
# ============================================================

def obtener_devices(
    archivos_encontrados: dict[str, pd.DataFrame],
) -> list[dict]:

    df_devices = archivos_encontrados.get(
        "Devices"
    )

    if df_devices is None:
        return []

    dispositivos = []

    for _, fila in df_devices.iterrows():

        hostname = normalizar_valor(
            fila.get(
                "hostname",
                ""
            )
        )

        tipo = normalizar_valor(
            fila.get(
                "type",
                ""
            )
        )

        description = normalizar_valor(
            fila.get(
                "description",
                ""
            )
        )

        if not hostname and not tipo:
            continue

        dispositivos.append(
            {
                "name": hostname,
                "type": tipo,
                "description": description,
            }
        )

    return dispositivos


# ============================================================
# ANALIZAR MANUFACTURERS
# ============================================================

def analizar_manufacturers(
    tipos: list[str],
    progress_callback=None,
) -> dict:

    resultados = []

    resueltos = 0
    manual = 0
    desconocidos = 0

    total = len(tipos)

    for indice, tipo in enumerate(
        tipos,
        start=1,
    ):

        if total:

            porcentaje = 35 + int(
                (indice / total) * 25
            )

        else:

            porcentaje = 60

        actualizar_progreso(
            progress_callback,
            porcentaje,
            f"Buscando manufacturer: {tipo}",
        )

        resultado = buscar_manufacturer(
            tipo
        )

        resultados.append(
            {
                "original": tipo,
                "manufacturer": resultado.manufacturer,
                "matched_model": resultado.matched_model,
                "confidence": resultado.confidence,
                "match_type": resultado.match_type,
                "source": resultado.source,
            }
        )

        if resultado.manufacturer:

            resueltos += 1

        elif resultado.confidence == "manual":

            manual += 1

        else:

            desconocidos += 1

    return {
        "resultados": resultados,
        "resueltos": resueltos,
        "manual": manual,
        "desconocidos": desconocidos,
    }


# ============================================================
# ÍNDICE DE MANUFACTURERS
# ============================================================

def obtener_manufacturer_por_tipo(
    manufacturers: dict,
) -> dict[str, dict]:

    indice = {}

    for resultado in manufacturers.get(
        "resultados",
        [],
    ):

        tipo = resultado.get(
            "original",
            ""
        )

        if not tipo:
            continue

        indice[
            tipo.lower()
        ] = resultado

    return indice


# ============================================================
# ANALIZAR ROLES
# ============================================================

def analizar_roles(
    dispositivos: list[dict],
    manufacturers: dict,
    progress_callback=None,
) -> dict:

    resultados = []

    indice_manufacturers = (
        obtener_manufacturer_por_tipo(
            manufacturers
        )
    )

    roles_detectados = {}

    total = len(
        dispositivos
    )

    for indice, dispositivo in enumerate(
        dispositivos,
        start=1,
    ):

        tipo = normalizar_valor(
            dispositivo.get(
                "type",
                ""
            )
        )

        nombre = normalizar_valor(
            dispositivo.get(
                "name",
                ""
            )
        )

        description = normalizar_valor(
            dispositivo.get(
                "description",
                ""
            )
        )

        manufacturer_resultado = (
            indice_manufacturers.get(
                tipo.lower(),
                {}
            )
        )

        manufacturer = manufacturer_resultado.get(
            "manufacturer",
            ""
        )

        matched_model = (
            manufacturer_resultado.get(
                "matched_model",
                ""
            )
        )

        if total:

            porcentaje = 60 + int(
                (indice / total) * 25
            )

        else:

            porcentaje = 85

        actualizar_progreso(
            progress_callback,
            porcentaje,
            f"Analizando Role: {tipo}",
        )

        recomendacion = recomendar_role(
            tipo=tipo,
            manufacturer=manufacturer,
            matched_model=matched_model,
            description=description,
        )

        role = recomendacion.get(
            "role",
            ""
        )

        confidence = recomendacion.get(
            "confidence",
            "unknown"
        )

        resultado = {
            "device": nombre,
            "device_type": tipo,
            "manufacturer": manufacturer,
            "recommended_role": role,
            "confidence": confidence,
            "score": recomendacion.get(
                "score",
                0
            ),
            "matched_keywords": recomendacion.get(
                "matched_keywords",
                []
            ),
        }

        resultados.append(
            resultado
        )

        if role:

            if role not in roles_detectados:

                roles_detectados[
                    role
                ] = {
                    "role": role,
                    "devices": 0,
                    "confidence": confidence,
                }

            roles_detectados[
                role
            ]["devices"] += 1

    return {
        "resultados": resultados,
        "roles_detectados": list(
            roles_detectados.values()
        ),
    }


# ============================================================
# ANÁLISIS COMPLETO
# ============================================================

def analizar_exportacion(
    carpeta_origen: str | Path,
    progress_callback=None,
) -> dict:
    """
    Analiza una exportación de phpIPAM.

    No convierte ni modifica archivos.

    progress_callback:
        función(porcentaje, mensaje)
    """

    carpeta = Path(
        carpeta_origen
    )

    if not carpeta.exists():

        raise FileNotFoundError(
            f"La carpeta no existe: {carpeta}"
        )

    if not carpeta.is_dir():

        raise NotADirectoryError(
            f"La ruta no es una carpeta: {carpeta}"
        )

    archivos_resultado = []

    archivos_encontrados = {}

    # ========================================================
    # DETECTAR ARCHIVOS
    # ========================================================

    actualizar_progreso(
        progress_callback,
        5,
        "Detectando archivos CSV...",
    )

    total_archivos = len(
        ARCHIVOS_ESPERADOS
    )

    for indice, (tipo, patron) in enumerate(
        ARCHIVOS_ESPERADOS.items(),
        start=1,
    ):

        porcentaje = 5 + int(
            (indice / total_archivos) * 20
        )

        actualizar_progreso(
            progress_callback,
            porcentaje,
            f"Buscando {tipo}...",
        )

        archivo = buscar_archivo(
            carpeta,
            patron,
        )

        if archivo is None:

            archivos_resultado.append(
                {
                    "estado": "NO",
                    "tipo": tipo,
                    "archivo": "-",
                    "registros": "-",
                }
            )

            continue

        try:

            actualizar_progreso(
                progress_callback,
                porcentaje,
                f"Leyendo {archivo.name}...",
            )

            df = leer_csv(
                archivo
            )

            archivos_encontrados[
                tipo
            ] = df

            archivos_resultado.append(
                {
                    "estado": "OK",
                    "tipo": tipo,
                    "archivo": archivo.name,
                    "registros": len(df),
                }
            )

        except Exception as error:

            archivos_resultado.append(
                {
                    "estado": "ERROR",
                    "tipo": tipo,
                    "archivo": archivo.name,
                    "registros": str(error),
                }
            )

    # ========================================================
    # OBTENER TIPOS
    # ========================================================

    actualizar_progreso(
        progress_callback,
        30,
        "Analizando Device Types...",
    )

    tipos = obtener_tipos(
        archivos_encontrados
    )

    # ========================================================
    # OBTENER DEVICES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        32,
        "Analizando Devices...",
    )

    dispositivos = obtener_devices(
        archivos_encontrados
    )

    # ========================================================
    # ANALIZAR MANUFACTURERS
    # ========================================================

    manufacturers = analizar_manufacturers(
        tipos,
        progress_callback,
    )

    # ========================================================
    # ANALIZAR ROLES
    # ========================================================

    roles = analizar_roles(
        dispositivos,
        manufacturers,
        progress_callback,
    )

    # ========================================================
    # FINALIZAR
    # ========================================================

    actualizar_progreso(
        progress_callback,
        100,
        "Análisis terminado.",
    )

    # ========================================================
    # RESULTADO FINAL
    # ========================================================

    return {
        "archivos": archivos_resultado,
        "tipos": tipos,
        "devices": dispositivos,
        "manufacturers": manufacturers,
        "roles": roles,
    }
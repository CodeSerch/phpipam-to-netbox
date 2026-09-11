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
# OBTENER DEVICE TYPES
# ============================================================

def obtener_device_types(
    archivos_encontrados: dict[str, pd.DataFrame],
) -> list[str]:
    """
    Obtiene exclusivamente los Device Types desde:

        Device Types -> Name

    Esta es la única fuente utilizada para la búsqueda
    de Manufacturers y para la recomendación de Roles.
    """

    df_device_types = archivos_encontrados.get(
        "Device Types"
    )

    if df_device_types is None:
        return []

    if "Name" not in df_device_types.columns:
        return []

    tipos = (
        df_device_types["Name"]
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .unique()
        .tolist()
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
    """
    Obtiene los Devices de phpIPAM.

    Los Devices se utilizan posteriormente para asociar
    el Role recomendado según su Device Type.

    NO se utilizan para buscar Manufacturers.
    """

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
    device_types: list[str],
    progress_callback=None,
) -> dict:
    """
    Busca Manufacturers exclusivamente para los
    Device Types de phpIPAM.
    """

    resultados = []

    resueltos = 0
    manual = 0
    desconocidos = 0

    total = len(
        device_types
    )

    for indice, device_type in enumerate(
        device_types,
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
            f"Buscando manufacturer: {device_type}",
        )

        resultado = buscar_manufacturer(
            device_type
        )

        resultados.append(
            {
                "original": device_type,
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
    """
    Crea un índice:

        Device Type -> resultado Manufacturer
    """

    indice = {}

    for resultado in manufacturers.get(
        "resultados",
        [],
    ):

        device_type = normalizar_valor(
            resultado.get(
                "original",
                ""
            )
        )

        if not device_type:
            continue

        indice[
            device_type.lower()
        ] = resultado

    return indice


# ============================================================
# ANALIZAR ROLES POR DEVICE TYPE
# ============================================================

def analizar_roles(
    device_types: list[str],
    dispositivos: list[dict],
    manufacturers: dict,
    progress_callback=None,
) -> dict:
    """
    Analiza el Role UNA SOLA VEZ por cada Device Type.

    Después asocia el Role recomendado a cada Device
    que utilice ese Device Type.

    No realiza búsquedas web.
    """

    indice_manufacturers = (
        obtener_manufacturer_por_tipo(
            manufacturers
        )
    )

    roles_por_tipo = {}
    total = len(
        device_types
    )

    # ========================================================
    # ANALIZAR CADA DEVICE TYPE
    # ========================================================

    for indice, tipo in enumerate(
        device_types,
        start=1,
    ):

        tipo = normalizar_valor(
            tipo
        )

        if not tipo:
            continue

        manufacturer_resultado = (
            indice_manufacturers.get(
                tipo.lower(),
                {}
            )
        )

        manufacturer = normalizar_valor(
            manufacturer_resultado.get(
                "manufacturer",
                ""
            )
        )

        matched_model = normalizar_valor(
            manufacturer_resultado.get(
                "matched_model",
                ""
            )
        )

        # Tomamos una descripción representativa
        # de algún Device de este Device Type.
        description = ""

        for dispositivo in dispositivos:

            dispositivo_tipo = normalizar_valor(
                dispositivo.get(
                    "type",
                    ""
                )
            )

            if dispositivo_tipo.lower() == tipo.lower():

                description = normalizar_valor(
                    dispositivo.get(
                        "description",
                        ""
                    )
                )

                if description:
                    break

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

        role = normalizar_valor(
            recomendacion.get(
                "role",
                ""
            )
        )

        confidence = normalizar_valor(
            recomendacion.get(
                "confidence",
                "unknown"
            )
        )

        roles_por_tipo[
            tipo.lower()
        ] = {
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

    # ========================================================
    # ASOCIAR ROLE A CADA DEVICE
    # ========================================================

    resultados = []

    roles_detectados = {}

    for dispositivo in dispositivos:

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

        resultado_tipo = roles_por_tipo.get(
            tipo.lower(),
            {}
        )

        role = normalizar_valor(
            resultado_tipo.get(
                "recommended_role",
                ""
            )
        )

        confidence = normalizar_valor(
            resultado_tipo.get(
                "confidence",
                "unknown"
            )
        )

        manufacturer = normalizar_valor(
            resultado_tipo.get(
                "manufacturer",
                ""
            )
        )

        resultado = {
            "device": nombre,
            "device_type": tipo,
            "manufacturer": manufacturer,
            "recommended_role": role,
            "confidence": confidence,
            "score": resultado_tipo.get(
                "score",
                0
            ),
            "matched_keywords": resultado_tipo.get(
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
        "roles_por_tipo": roles_por_tipo,
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

    Manufacturer Finder recibe exclusivamente
    los Device Types.

    Role Mapper recomienda un Role una sola vez
    por cada Device Type.
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
    # OBTENER DEVICE TYPES
    # ========================================================

    actualizar_progreso(
        progress_callback,
        30,
        "Analizando Device Types...",
    )

    device_types = obtener_device_types(
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
        device_types,
        progress_callback,
    )

    # ========================================================
    # ANALIZAR ROLES
    # ========================================================

    roles = analizar_roles(
        device_types,
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
        "device_types": device_types,
        "devices": dispositivos,
        "manufacturers": manufacturers,
        "roles": roles,
    }
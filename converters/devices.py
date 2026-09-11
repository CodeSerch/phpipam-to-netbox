from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "name",
    "role",
    "device_type",
    "status",
    "site",
]

FIELD_OPTIONS = [
    "name",
    "role",
    "device_type",
    "status",
    "site",
    "location",
    "rack",
    "position",
    "face",
    "serial",
    "asset_tag",
    "description",
    "comments",
    "platform",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "name",
    "role",
    "device_type",
    "status",
    "site",
    "location",
    "rack",
    "position",
    "face",
    "serial",
    "asset_tag",
    "description",
    "comments",
    "platform",
    "tags",
]


# ============================================================
# VALORES POR DEFECTO
# ============================================================

DEFAULT_STATUS = "active"


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_valor(
    valor,
) -> str:

    if valor is None:
        return ""

    return str(
        valor
    ).strip()


# ============================================================
# NORMALIZAR DEVICE
# ============================================================

def normalizar_device(
    registro: dict,
    site: str,
    role: str,
) -> dict:
    """
    Normaliza un dispositivo para NetBox.

    site y role son obligatorios y se reciben
    desde el proceso de conversión.
    """

    name = normalizar_valor(
        registro.get(
            "name",
            ""
        )
    )

    device_type = normalizar_valor(
        registro.get(
            "device_type",
            ""
        )
    )

    status = normalizar_valor(
        registro.get(
            "status",
            ""
        )
    )

    if not status:

        status = DEFAULT_STATUS

    return {
        "name": name,
        "role": normalizar_valor(
            role
        ),
        "device_type": device_type,
        "status": status,
        "site": normalizar_valor(
            site
        ),
        "location": normalizar_valor(
            registro.get(
                "location",
                ""
            )
        ),
        "rack": normalizar_valor(
            registro.get(
                "rack",
                ""
            )
        ),
        "position": normalizar_valor(
            registro.get(
                "position",
                ""
            )
        ),
        "face": normalizar_valor(
            registro.get(
                "face",
                ""
            )
        ),
        "serial": normalizar_valor(
            registro.get(
                "serial",
                ""
            )
        ),
        "asset_tag": normalizar_valor(
            registro.get(
                "asset_tag",
                ""
            )
        ),
        "description": normalizar_valor(
            registro.get(
                "description",
                ""
            )
        ),
        "comments": normalizar_valor(
            registro.get(
                "comments",
                ""
            )
        ),
        "platform": normalizar_valor(
            registro.get(
                "platform",
                ""
            )
        ),
        "tags": normalizar_valor(
            registro.get(
                "tags",
                ""
            )
        ),
    }


# ============================================================
# NORMALIZAR DEVICES
# ============================================================

def normalizar_devices(
    registros: list[dict],
    site: str,
    roles_por_tipo: dict[str, str],
) -> tuple[list[dict], list[dict]]:
    """
    Normaliza todos los Devices.

    roles_por_tipo relaciona el tipo original de phpIPAM
    con el Role seleccionado/recomendado.

    Devuelve:

        (registros_validos, errores)
    """

    resultados = []
    errores = []

    vistos = set()

    for numero, registro in enumerate(
        registros,
        start=1,
    ):

        name = normalizar_valor(
            registro.get(
                "name",
                ""
            )
        )

        device_type = normalizar_valor(
            registro.get(
                "device_type",
                ""
            )
        )

        # ----------------------------------------------------
        # NAME
        # ----------------------------------------------------

        if not name:

            errores.append(
                {
                    "registro": numero,
                    "campo": "name",
                    "valor": "",
                    "error": "Nombre de Device vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # DEVICE TYPE
        # ----------------------------------------------------

        if not device_type:

            errores.append(
                {
                    "registro": numero,
                    "campo": "device_type",
                    "valor": "",
                    "error": "Device Type vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # SITE
        # ----------------------------------------------------

        if not site.strip():

            errores.append(
                {
                    "registro": numero,
                    "campo": "site",
                    "valor": "",
                    "error": "Site no definido.",
                }
            )

            continue

        # ----------------------------------------------------
        # ROLE
        # ----------------------------------------------------

        role = roles_por_tipo.get(
            device_type.lower(),
            ""
        )

        if not role:

            errores.append(
                {
                    "registro": numero,
                    "campo": "role",
                    "valor": "",
                    "error": (
                        f"No se encontró Role para "
                        f"'{device_type}'."
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # DUPLICADOS
        # ----------------------------------------------------

        clave = name.lower()

        if clave in vistos:

            errores.append(
                {
                    "registro": numero,
                    "campo": "name",
                    "valor": name,
                    "error": "Device duplicado.",
                }
            )

            continue

        vistos.add(
            clave
        )

        device = normalizar_device(
            registro,
            site,
            role,
        )

        resultados.append(
            device
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_devices(
    registros: list[dict],
    carpeta_destino: str | Path,
    site: str,
    roles_por_tipo: dict[str, str],
) -> dict:
    """
    Genera devices.csv compatible con NetBox.

    Parameters
    ----------
    registros:
        Lista de Devices.

    carpeta_destino:
        Carpeta de salida.

    site:
        Site de NetBox que utilizarán los Devices.

    roles_por_tipo:
        Mapa:

            tipo phpIPAM -> Role NetBox

    Returns
    -------
    dict
        {
            "archivo": Path,
            "registros": int,
            "errores": list
        }
    """

    destino = Path(
        carpeta_destino
    )

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    registros_validos, errores = (
        normalizar_devices(
            registros,
            site,
            roles_por_tipo,
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "devices.csv"
    )

    df.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig",
    )

    return {
        "archivo": archivo_salida,
        "registros": len(registros_validos),
        "errores": errores,
    }
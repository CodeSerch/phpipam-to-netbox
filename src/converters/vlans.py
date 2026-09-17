from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "vid",
    "name",
    "status",
]

FIELD_OPTIONS = [
    "vid",
    "name",
    "status",
    "group",
    "site",
    "tenant",
    "role",
    "description",
    "comments",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "vid",
    "name",
    "status",
    "group",
    "site",
    "tenant",
    "role",
    "description",
    "comments",
    "tags",
]


# ============================================================
# VALORES POR DEFECTO
# ============================================================

DEFAULT_STATUS = "active"


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_valor(valor) -> str:
    """
    Convierte un valor a texto limpio.
    """

    if valor is None:
        return ""

    return str(
        valor
    ).strip()


def normalizar_vid(
    vid: str,
) -> int | None:
    """
    Valida el VID de una VLAN.

    NetBox requiere un VID entre 1 y 4094.

    No convierte valores vacíos en 0.
    """

    vid = normalizar_valor(
        vid
    )

    if not vid:
        return None

    try:

        numero = int(
            float(vid)
        )

    except ValueError:

        return None

    if numero < 1 or numero > 4094:

        return None

    return numero


def normalizar_vlan(
    registro: dict,
) -> dict:
    """
    Normaliza una VLAN individual
    para la salida de NetBox.
    """

    vid = normalizar_vid(
        registro.get(
            "vid",
            ""
        )
    )

    name = normalizar_valor(
        registro.get(
            "name",
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
        "vid": vid,
        "name": name,
        "status": status,
        "group": normalizar_valor(
            registro.get(
                "group",
                ""
            )
        ),
        "site": normalizar_valor(
            registro.get(
                "site",
                ""
            )
        ),
        "tenant": normalizar_valor(
            registro.get(
                "tenant",
                ""
            )
        ),
        "role": normalizar_valor(
            registro.get(
                "role",
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
        "tags": normalizar_valor(
            registro.get(
                "tags",
                ""
            )
        ),
    }


# ============================================================
# NORMALIZAR VLANS
# ============================================================

def normalizar_vlans(
    registros: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Normaliza todas las VLANs.

    Devuelve:

        (registros_validos, errores)
    """

    resultados = []
    errores = []

    vistos_vid = set()

    for numero, registro in enumerate(
        registros,
        start=1,
    ):

        original_vid = normalizar_valor(
            registro.get(
                "vid",
                ""
            )
        )

        original_name = normalizar_valor(
            registro.get(
                "name",
                ""
            )
        )

        # ----------------------------------------------------
        # VALIDAR VID
        # ----------------------------------------------------

        vid = normalizar_vid(
            original_vid
        )

        if vid is None:

            errores.append(
                {
                    "registro": numero,
                    "campo": "vid",
                    "valor": original_vid,
                    "error": (
                        "VID inválido. "
                        "Debe ser un número entre 1 y 4094."
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # VALIDAR NAME
        # ----------------------------------------------------

        if not original_name:

            errores.append(
                {
                    "registro": numero,
                    "campo": "name",
                    "valor": "",
                    "error": "Nombre de VLAN vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # EVITAR VID DUPLICADOS
        # ----------------------------------------------------

        if vid in vistos_vid:

            errores.append(
                {
                    "registro": numero,
                    "campo": "vid",
                    "valor": str(vid),
                    "error": "VID duplicado.",
                }
            )

            continue

        vistos_vid.add(
            vid
        )

        vlan = normalizar_vlan(
            registro
        )

        vlan["vid"] = vid

        resultados.append(
            vlan
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_vlans(
    registros: list[dict],
    carpeta_destino: str | Path,
) -> dict:
    """
    Genera vlans.csv compatible con NetBox.

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
        normalizar_vlans(
            registros
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "vlans.csv"
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
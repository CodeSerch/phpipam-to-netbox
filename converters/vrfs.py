from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "name",
]

FIELD_OPTIONS = [
    "name",
    "rd",
    "enforce_unique",
    "description",
    "comments",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "name",
    "rd",
    "enforce_unique",
    "description",
    "comments",
    "tags",
]


# ============================================================
# VALORES POR DEFECTO
# ============================================================

DEFAULT_ENFORCE_UNIQUE = ""


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


def normalizar_enforce_unique(
    valor,
) -> str:
    """
    Normaliza el campo enforce_unique.

    Acepta valores booleanos comunes:
        true
        false
        yes
        no
        1
        0

    Si el valor está vacío, devuelve vacío.
    """

    valor = normalizar_valor(
        valor
    ).lower()

    if not valor:
        return DEFAULT_ENFORCE_UNIQUE

    valores_true = {
        "true",
        "yes",
        "si",
        "sí",
        "1",
    }

    valores_false = {
        "false",
        "no",
        "0",
    }

    if valor in valores_true:
        return "true"

    if valor in valores_false:
        return "false"

    return ""


def normalizar_vrf(
    registro: dict,
) -> dict:
    """
    Normaliza un VRF individual
    para la salida de NetBox.
    """

    name = normalizar_valor(
        registro.get(
            "name",
            ""
        )
    )

    rd = normalizar_valor(
        registro.get(
            "rd",
            ""
        )
    )

    enforce_unique = normalizar_enforce_unique(
        registro.get(
            "enforce_unique",
            ""
        )
    )

    return {
        "name": name,
        "rd": rd,
        "enforce_unique": enforce_unique,
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
# NORMALIZAR VRFS
# ============================================================

def normalizar_vrfs(
    registros: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Normaliza todos los VRFs.

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

        vrf = normalizar_vrf(
            registro
        )

        name = vrf[
            "name"
        ]

        # ----------------------------------------------------
        # VALIDAR NAME
        # ----------------------------------------------------

        if not name:

            errores.append(
                {
                    "registro": numero,
                    "campo": "name",
                    "valor": "",
                    "error": "Nombre de VRF vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # EVITAR DUPLICADOS
        # ----------------------------------------------------

        clave = name.lower()

        if clave in vistos:

            errores.append(
                {
                    "registro": numero,
                    "campo": "name",
                    "valor": name,
                    "error": "VRF duplicado.",
                }
            )

            continue

        vistos.add(
            clave
        )

        resultados.append(
            vrf
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_vrfs(
    registros: list[dict],
    carpeta_destino: str | Path,
) -> dict:
    """
    Genera vrfs.csv compatible con NetBox.

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
        normalizar_vrfs(
            registros
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "vrfs.csv"
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
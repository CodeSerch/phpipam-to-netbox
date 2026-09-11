from pathlib import Path
import ipaddress

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "prefix",
    "status",
]

FIELD_OPTIONS = [
    "prefix",
    "status",
    "vrf",
    "tenant",
    "vlan",
    "role",
    "site",
    "description",
    "comments",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "prefix",
    "status",
    "vrf",
    "tenant",
    "vlan",
    "role",
    "site",
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


def normalizar_prefix(
    prefix: str,
) -> str:
    """
    Valida y normaliza un prefijo IPv4 o IPv6.

    No genera máscaras cuando la fuente no las proporciona.

    Ejemplo válido:
        10.55.55.0/24

    Ejemplo inválido:
        /

    También permite redes no estrictas y las normaliza.

        10.55.55.10/24
        ->
        10.55.55.0/24
    """

    prefix = normalizar_valor(
        prefix
    )

    if not prefix:
        return ""

    # --------------------------------------------------------
    # REGISTROS DE CARPETA DE PHPIPAM
    # --------------------------------------------------------

    if prefix == "/":
        return ""

    try:

        network = ipaddress.ip_network(
            prefix,
            strict=False,
        )

    except ValueError:

        return ""

    return str(
        network
    )


def normalizar_prefix_record(
    registro: dict,
) -> dict:
    """
    Normaliza un prefijo individual
    para la salida de NetBox.
    """

    prefix = normalizar_prefix(
        registro.get(
            "prefix",
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
        "prefix": prefix,
        "status": status,
        "vrf": normalizar_valor(
            registro.get(
                "vrf",
                ""
            )
        ),
        "tenant": normalizar_valor(
            registro.get(
                "tenant",
                ""
            )
        ),
        "vlan": normalizar_valor(
            registro.get(
                "vlan",
                ""
            )
        ),
        "role": normalizar_valor(
            registro.get(
                "role",
                ""
            )
        ),
        "site": normalizar_valor(
            registro.get(
                "site",
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
# NORMALIZAR PREFIXES
# ============================================================

def normalizar_prefixes(
    registros: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Normaliza los prefijos.

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

        original = normalizar_valor(
            registro.get(
                "prefix",
                ""
            )
        )

        # ----------------------------------------------------
        # IGNORAR VACÍOS
        # ----------------------------------------------------

        if not original:

            errores.append(
                {
                    "registro": numero,
                    "campo": "prefix",
                    "valor": "",
                    "error": "Prefijo vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # IGNORAR "/" DE PHPIPAM
        # ----------------------------------------------------

        if original == "/":

            errores.append(
                {
                    "registro": numero,
                    "campo": "prefix",
                    "valor": "/",
                    "error": (
                        "Registro de carpeta de phpIPAM "
                        "ignorado."
                    ),
                }
            )

            continue

        prefix = normalizar_prefix_record(
            registro
        )

        valor = prefix[
            "prefix"
        ]

        # ----------------------------------------------------
        # PREFIJO INVÁLIDO
        # ----------------------------------------------------

        if not valor:

            errores.append(
                {
                    "registro": numero,
                    "campo": "prefix",
                    "valor": original,
                    "error": "Prefijo IPv4/IPv6 inválido.",
                }
            )

            continue

        # ----------------------------------------------------
        # EVITAR DUPLICADOS
        # ----------------------------------------------------

        clave = valor.lower()

        if clave in vistos:

            errores.append(
                {
                    "registro": numero,
                    "campo": "prefix",
                    "valor": original,
                    "error": "Prefijo duplicado.",
                }
            )

            continue

        vistos.add(
            clave
        )

        resultados.append(
            prefix
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_prefixes(
    registros: list[dict],
    carpeta_destino: str | Path,
) -> dict:
    """
    Genera prefixes.csv compatible con NetBox.

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
        normalizar_prefixes(
            registros
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "prefixes.csv"
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
from pathlib import Path
import ipaddress

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "address",
    "status",
]

FIELD_OPTIONS = [
    "address",
    "status",
    "vrf",
    "dns_name",
    "description",
    "comments",
    "role",
    "tenant",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "address",
    "status",
    "vrf",
    "dns_name",
    "description",
    "comments",
    "role",
    "tenant",
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


def normalizar_address(
    address: str,
) -> str:
    """
    Normaliza una dirección IP para NetBox.

    IPv4 sin máscara:
        10.55.55.198
        ->
        10.55.55.198/32

    IPv6 sin máscara:
        2001:db8::1
        ->
        2001:db8::1/128
    """

    address = normalizar_valor(
        address
    )

    if not address:
        return ""

    # --------------------------------------------------------
    # YA TIENE CIDR
    # --------------------------------------------------------

    if "/" in address:

        try:

            ipaddress.ip_interface(
                address
            )

            return address

        except ValueError:

            return ""

    # --------------------------------------------------------
    # IP SIN CIDR
    # --------------------------------------------------------

    try:

        ip = ipaddress.ip_address(
            address
        )

    except ValueError:

        return ""

    if ip.version == 4:

        return f"{address}/32"

    return f"{address}/128"


def normalizar_ip_address(
    registro: dict,
) -> dict:
    """
    Normaliza una IP individual
    para la salida de NetBox.
    """

    address = normalizar_address(
        registro.get(
            "address",
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
        "address": address,
        "status": status,
        "vrf": normalizar_valor(
            registro.get(
                "vrf",
                ""
            )
        ),
        "dns_name": normalizar_valor(
            registro.get(
                "dns_name",
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
        "role": normalizar_valor(
            registro.get(
                "role",
                ""
            )
        ),
        "tenant": normalizar_valor(
            registro.get(
                "tenant",
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
# NORMALIZAR IP ADDRESSES
# ============================================================

def normalizar_ip_addresses(
    registros: list[dict],
) -> tuple[list[dict], list[dict]]:
    """
    Normaliza todas las IPs.

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
                "address",
                ""
            )
        )

        ip_address = normalizar_ip_address(
            registro
        )

        address = ip_address[
            "address"
        ]

        # ----------------------------------------------------
        # IP VACÍA
        # ----------------------------------------------------

        if not original:

            errores.append(
                {
                    "registro": numero,
                    "campo": "address",
                    "valor": "",
                    "error": "Dirección IP vacía.",
                }
            )

            continue

        # ----------------------------------------------------
        # IP INVÁLIDA
        # ----------------------------------------------------

        if not address:

            errores.append(
                {
                    "registro": numero,
                    "campo": "address",
                    "valor": original,
                    "error": "Dirección IP inválida.",
                }
            )

            continue

        # ----------------------------------------------------
        # EVITAR DUPLICADOS
        # ----------------------------------------------------

        clave = address.lower()

        if clave in vistos:

            errores.append(
                {
                    "registro": numero,
                    "campo": "address",
                    "valor": original,
                    "error": "Dirección IP duplicada.",
                }
            )

            continue

        vistos.add(
            clave
        )

        resultados.append(
            ip_address
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_ip_addresses(
    registros: list[dict],
    carpeta_destino: str | Path,
) -> dict:
    """
    Genera ip_addresses.csv compatible con NetBox.

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
        normalizar_ip_addresses(
            registros
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "ip_addresses.csv"
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
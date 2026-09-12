import re

from role_defaults import obtener_roles_default


# ============================================================
# REGLAS DE DETECCIÓN
# ============================================================

ROLE_RULES = {
    "Firewall": [
        "firewall",
        "fortigate",
        "palo alto",
        "pan-os",
        "asa",
        "srx",
        "checkpoint",
    ],
    "OLT": [
        "olt",
        "ma5800",
        "ma5600",
        "gpon olt",
        "epon olt",
    ],
    "Router": [
        "router",
        "routing",
        "mx",
        "asr",
        "isr",
        "crs",
        "edge router",
    ],
    "Switch": [
        "switch",
        "switching",
        "catalyst",
        "nexus",
        "arista",
        "juniper ex",
        "ethernet switch",
    ],
    "Server": [
        "server",
        "dl380",
        "dl385",
        "dl360",
        "dl560",
        "r620",
        "r630",
        "r640",
        "r650",
        "r720",
        "r730",
        "r740",
        "r750",
        "r760",
        "7920",
    ],
    "Storage": [
        "storage",
        "san",
        "nas",
        "qnap",
        "synology",
        "me5024",
        "me4024",
        "me5012",
        "powerstore",
        "unity",
        "netapp",
        "pure storage",
        "iscsi storage",
    ],
    "Load Balancer": [
        "load balancer",
        "load-balancer",
        "f5 big-ip",
        "big-ip",
        "citrix adc",
        "netscaler",
        "a10 thunder",
    ],
    "Access Point": [
        "access point",
        "access-point",
        "wifi ap",
        "wireless ap",
        "aruba ap",
        "unifi ap",
        "cisco ap",
    ],
    "Wireless Controller": [
        "wireless controller",
        "wlc",
        "aruba mobility",
        "cisco wireless controller",
        "unifi controller",
    ],
    "Hypervisor": [
        "esxi",
        "vmware",
        "vcenter",
        "hypervisor",
        "proxmox",
        "xcp-ng",
        "xenserver",
        "hyper-v",
    ],
    "Database": [
        "database",
        "postgres",
        "postgresql",
        "mysql",
        "mariadb",
        "oracle database",
        "sql server",
    ],
    "NAS": [
        "nas",
        "qnap",
        "synology",
        "truenas",
    ],
    "Console Server": [
        "console server",
        "terminal server",
        "serial server",
        "console manager",
    ],
    "Power": [
        "ups",
        "pdu",
        "power distribution",
        "power",
        "apc smart-ups",
        "eaton",
    ],
    "Virtual Machine": [
        "virtual machine",
        "vm",
        "guest",
    ],
}


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_texto(valor) -> str:
    """
    Convierte un valor a texto normalizado.
    """

    if valor is None:
        return ""

    texto = str(
        valor
    ).strip().lower()

    texto = re.sub(
        r"\s+",
        " ",
        texto
    )

    return texto


def obtener_texto_busqueda(
    tipo: str = "",
    manufacturer: str = "",
    matched_model: str = "",
    description: str = "",
) -> str:
    """
    Combina los datos disponibles para realizar
    la clasificación.
    """

    partes = [
        tipo,
        manufacturer,
        matched_model,
        description,
    ]

    return " ".join(
        normalizar_texto(parte)
        for parte in partes
        if normalizar_texto(parte)
    )


def obtener_score(
    texto: str,
    keywords: list[str],
) -> int:
    """
    Calcula una puntuación sencilla según
    las palabras/patrones encontrados.
    """

    score = 0

    for keyword in keywords:

        keyword_normalizada = normalizar_texto(
            keyword
        )

        if not keyword_normalizada:
            continue

        if keyword_normalizada in texto:
            score += 1

    return score


def obtener_confianza(
    score: int,
) -> str:
    """
    Determina el nivel de confianza.
    """

    if score >= 3:
        return "high"

    if score == 2:
        return "medium"

    if score == 1:
        return "low"

    return "unknown"


def buscar_role_default(
    nombre: str,
) -> dict | None:

    nombre_normalizado = normalizar_texto(
        nombre
    )

    for role in obtener_roles_default():

        if normalizar_texto(
            role["name"]
        ) == nombre_normalizado:

            return role

    return None


# ============================================================
# CLASIFICACIÓN
# ============================================================

def recomendar_role(
    tipo: str = "",
    manufacturer: str = "",
    matched_model: str = "",
    description: str = "",
) -> dict:
    """
    Recomienda un Device Role.

    No crea el Role y no modifica NetBox.
    """

    texto = obtener_texto_busqueda(
        tipo=tipo,
        manufacturer=manufacturer,
        matched_model=matched_model,
        description=description,
    )

    candidatos = []

    for role_name, keywords in ROLE_RULES.items():

        score = obtener_score(
            texto,
            keywords
        )

        if score <= 0:
            continue

        candidatos.append(
            {
                "role": role_name,
                "score": score,
            }
        )

    if not candidatos:

        return {
            "role": "",
            "confidence": "unknown",
            "score": 0,
            "matched_keywords": [],
        }

    candidatos.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    mejor = candidatos[0]

    keywords = ROLE_RULES[
        mejor["role"]
    ]

    matched_keywords = [
        keyword
        for keyword in keywords
        if normalizar_texto(keyword) in texto
    ]

    return {
        "role": mejor["role"],
        "confidence": obtener_confianza(
            mejor["score"]
        ),
        "score": mejor["score"],
        "matched_keywords": matched_keywords,
    }


def analizar_roles(
    dispositivos: list[dict],
) -> list[dict]:
    """
    Analiza una lista de dispositivos y devuelve
    las recomendaciones de Role.
    """

    resultados = []

    for dispositivo in dispositivos:

        resultado = recomendar_role(
            tipo=dispositivo.get(
                "type",
                dispositivo.get(
                    "device_type",
                    ""
                )
            ),
            manufacturer=dispositivo.get(
                "manufacturer",
                ""
            ),
            matched_model=dispositivo.get(
                "matched_model",
                ""
            ),
            description=dispositivo.get(
                "description",
                ""
            ),
        )

        resultados.append(
            {
                "device": dispositivo.get(
                    "name",
                    dispositivo.get(
                        "hostname",
                        ""
                    )
                ),
                "device_type": dispositivo.get(
                    "type",
                    dispositivo.get(
                        "device_type",
                        ""
                    )
                ),
                "manufacturer": dispositivo.get(
                    "manufacturer",
                    ""
                ),
                "recommended_role": resultado[
                    "role"
                ],
                "confidence": resultado[
                    "confidence"
                ],
                "score": resultado[
                    "score"
                ],
                "matched_keywords": resultado[
                    "matched_keywords"
                ],
            }
        )

    return resultados
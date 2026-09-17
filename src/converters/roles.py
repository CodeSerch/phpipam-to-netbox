from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "name",
    "slug",
    "color",
]

FIELD_OPTIONS = [
    "name",
    "slug",
    "color",
    "parent",
    "vm_role",
    "config_template",
    "description",
    "owner",
    "comments",
    "tags",
    "changelog_message",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "name",
    "slug",
    "color",
]


# ============================================================
# UTILIDADES
# ============================================================

def normalizar_valor(valor) -> str:

    if valor is None:
        return ""

    return str(
        valor
    ).strip()


def generar_slug(nombre: str) -> str:

    nombre = normalizar_valor(
        nombre
    ).lower()

    caracteres = []

    for caracter in nombre:

        if caracter.isalnum():

            caracteres.append(
                caracter
            )

        elif caracter in (" ", "-", "_"):

            caracteres.append(
                "-"
            )

    slug = "".join(
        caracteres
    )

    while "--" in slug:

        slug = slug.replace(
            "--",
            "-"
        )

    return slug.strip("-")


def normalizar_color(
    color: str,
) -> str:
    """
    Normaliza un color hexadecimal.

    Acepta:
        2196f3
        #2196f3

    Devuelve:
        2196f3
    """

    color = normalizar_valor(
        color
    ).replace(
        "#",
        ""
    )

    if len(color) != 6:

        return ""

    caracteres_validos = (
        "0123456789abcdefABCDEF"
    )

    if any(
        caracter not in caracteres_validos
        for caracter in color
    ):

        return ""

    return color.lower()


# ============================================================
# NORMALIZACIÓN
# ============================================================

def normalizar_roles(
    roles: list[dict],
) -> tuple[list[dict], list[dict]]:

    resultados = []

    errores = []

    vistos = set()

    for numero, registro in enumerate(
        roles,
        start=1,
    ):

        name = normalizar_valor(
            registro.get(
                "name",
                ""
            )
        )

        slug = normalizar_valor(
            registro.get(
                "slug",
                ""
            )
        )

        color = normalizar_color(
            registro.get(
                "color",
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
                    "error": "Nombre de Role vacío.",
                }
            )

            continue

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        if not slug:

            slug = generar_slug(
                name
            )

        # ----------------------------------------------------
        # COLOR
        # ----------------------------------------------------

        if not color:

            errores.append(
                {
                    "registro": numero,
                    "campo": "color",
                    "valor": color,
                    "error": (
                        "Color inválido. "
                        "Debe ser hexadecimal de 6 caracteres."
                    ),
                }
            )

            continue

        # ----------------------------------------------------
        # DUPLICADOS
        # ----------------------------------------------------

        clave = slug.lower()

        if clave in vistos:

            errores.append(
                {
                    "registro": numero,
                    "campo": "slug",
                    "valor": slug,
                    "error": "Slug de Role duplicado.",
                }
            )

            continue

        vistos.add(
            clave
        )

        resultados.append(
            {
                "name": name,
                "slug": slug,
                "color": color,
            }
        )

    return resultados, errores


# ============================================================
# CONVERSOR
# ============================================================

def convertir_roles(
    roles: list[dict],
    carpeta_destino: str | Path,
) -> dict:
    """
    Genera roles.csv compatible con NetBox.
    """

    destino = Path(
        carpeta_destino
    )

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    registros_validos, errores = (
        normalizar_roles(
            roles
        )
    )

    df = pd.DataFrame(
        registros_validos,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "roles.csv"
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
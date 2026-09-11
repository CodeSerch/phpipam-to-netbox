from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "name",
    "slug",
]

FIELD_OPTIONS = [
    "name",
    "slug",
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
    "description",
]


# ============================================================
# UTILIDADES
# ============================================================

def generar_slug(nombre: str) -> str:
    """
    Genera un slug básico compatible con NetBox.
    """

    nombre = str(nombre).strip().lower()

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


def normalizar_manufacturers(
    manufacturers: list[str],
) -> list[dict]:
    """
    Convierte una lista de fabricantes
    en registros preparados para NetBox.
    """

    resultados = []

    vistos = set()

    for manufacturer in manufacturers:

        nombre = str(
            manufacturer
        ).strip()

        if not nombre:

            continue

        clave = nombre.lower()

        if clave in vistos:

            continue

        vistos.add(
            clave
        )

        resultados.append(
            {
                "name": nombre,
                "slug": generar_slug(nombre),
                "description": "",
            }
        )

    return resultados


# ============================================================
# CONVERSOR
# ============================================================

def convertir_manufacturers(
    manufacturers: list[str],
    carpeta_destino: str | Path,
) -> Path:
    """
    Genera manufacturers.csv compatible con NetBox.
    """

    destino = Path(
        carpeta_destino
    )

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    registros = normalizar_manufacturers(
        manufacturers
    )

    df = pd.DataFrame(
        registros,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "manufacturers.csv"
    )

    df.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig",
    )

    return archivo_salida
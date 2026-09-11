from pathlib import Path

import pandas as pd


# ============================================================
# NETBOX
# ============================================================

REQUIRED_FIELDS = [
    "manufacturer",
    "model",
    "slug",
    "u_height",
]

FIELD_OPTIONS = [
    "manufacturer",
    "model",
    "slug",
    "part_number",
    "u_height",
    "is_full_depth",
    "airflow",
    "weight",
    "weight_unit",
    "comments",
    "tags",
    "id",
]


# ============================================================
# CAMPOS DE SALIDA
# ============================================================

OUTPUT_FIELDS = [
    "manufacturer",
    "model",
    "slug",
    "part_number",
    "u_height",
    "is_full_depth",
    "airflow",
    "weight",
    "weight_unit",
    "comments",
    "tags",
]


# ============================================================
# UTILIDADES
# ============================================================

def generar_slug(modelo: str) -> str:
    """
    Genera un slug a partir del nombre del modelo.

    Ejemplo:
        DELL-DL380
        ->
        dell-dl380
    """

    modelo = str(
        modelo
    ).strip().lower()

    caracteres = []

    for caracter in modelo:

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


def normalizar_device_types(
    registros: list[dict],
) -> list[dict]:
    """
    Normaliza los Device Types antes de generar
    device_types.csv.

    Cada registro debe contener como mínimo:

        manufacturer
        model

    Si slug o u_height no existen, se generan
    valores por defecto.
    """

    resultados = []

    vistos = set()

    for registro in registros:

        manufacturer = str(
            registro.get(
                "manufacturer",
                ""
            )
        ).strip()

        model = str(
            registro.get(
                "model",
                ""
            )
        ).strip()

        # ----------------------------------------------------
        # CAMPOS OBLIGATORIOS
        # ----------------------------------------------------

        if not manufacturer:
            continue

        if not model:
            continue

        # ----------------------------------------------------
        # EVITAR DUPLICADOS
        # ----------------------------------------------------

        clave = (
            manufacturer.lower(),
            model.lower()
        )

        if clave in vistos:
            continue

        vistos.add(
            clave
        )

        # ----------------------------------------------------
        # SLUG
        # ----------------------------------------------------

        slug = str(
            registro.get(
                "slug",
                ""
            )
        ).strip()

        if not slug:

            slug = generar_slug(
                model
            )

        # ----------------------------------------------------
        # U HEIGHT
        # ----------------------------------------------------

        u_height = str(
            registro.get(
                "u_height",
                ""
            )
        ).strip()

        if not u_height:

            u_height = "0"

        # ----------------------------------------------------
        # REGISTRO
        # ----------------------------------------------------

        resultados.append(
            {
                "manufacturer": manufacturer,
                "model": model,
                "slug": slug,
                "part_number": str(
                    registro.get(
                        "part_number",
                        ""
                    )
                ).strip(),
                "u_height": u_height,
                "is_full_depth": str(
                    registro.get(
                        "is_full_depth",
                        ""
                    )
                ).strip(),
                "airflow": str(
                    registro.get(
                        "airflow",
                        ""
                    )
                ).strip(),
                "weight": str(
                    registro.get(
                        "weight",
                        ""
                    )
                ).strip(),
                "weight_unit": str(
                    registro.get(
                        "weight_unit",
                        ""
                    )
                ).strip(),
                "comments": str(
                    registro.get(
                        "comments",
                        ""
                    )
                ).strip(),
                "tags": str(
                    registro.get(
                        "tags",
                        ""
                    )
                ).strip(),
            }
        )

    return resultados


# ============================================================
# CONVERSOR
# ============================================================

def convertir_device_types(
    registros: list[dict],
    carpeta_destino: str | Path,
) -> Path:
    """
    Genera device_types.csv compatible con NetBox.
    """

    destino = Path(
        carpeta_destino
    )

    destino.mkdir(
        parents=True,
        exist_ok=True,
    )

    registros_normalizados = (
        normalizar_device_types(
            registros
        )
    )

    df = pd.DataFrame(
        registros_normalizados,
        columns=OUTPUT_FIELDS,
    )

    archivo_salida = (
        destino / "device_types.csv"
    )

    df.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8-sig",
    )

    return archivo_salida
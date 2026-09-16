import pandas as pd


def convertir_xls_a_csv(archivo_entrada, archivo_salida):
    df = pd.read_excel(archivo_entrada)

    df.to_csv(
        archivo_salida,
        index=False,
        encoding="utf-8"
    )
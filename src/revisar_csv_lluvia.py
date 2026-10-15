"""Diagnóstico rápido del CSV de precipitación diaria."""

from pathlib import Path

import pandas as pd

ENTRADA = (
    Path(__file__).resolve().parent.parent
    / "raw"
    / "catalogos"
    / "precip_diaria_candidatas.csv"
)

print("Buscando archivo en:")
print(ENTRADA)
print("Existe:", ENTRADA.exists())

if ENTRADA.exists():
    print("Tamaño en bytes:", ENTRADA.stat().st_size)

    df = pd.read_csv(ENTRADA)

    print("\nColumnas:")
    print(list(df.columns))

    print("\nPrimeras 5 filas:")
    print(df.head().to_string())

    print("\nÚltimas 5 filas:")
    print(df.tail().to_string())

    print("\nForma del DataFrame:")
    print(df.shape)

    if "codigoestacion" in df.columns:
        print("\nCódigos de estación encontrados:")
        print(df["codigoestacion"].value_counts())
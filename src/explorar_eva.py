"""Muestra las columnas reales del conjunto EVA (UPRA) en datos.gov.co."""
import pandas as pd

URL = "https://www.datos.gov.co/resource/uejq-wxrr.csv?$limit=5"

df = pd.read_csv(URL)
print("COLUMNAS:")
for c in df.columns:
    print(" -", c)
print()
print(df.head().to_string())
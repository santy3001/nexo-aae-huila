"""Lista las estaciones hidrológicas del IDEAM ubicadas en el Huila."""
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.datos.gov.co/resource/hp9r-jxuu.json"
SALIDA = Path(__file__).resolve().parent.parent / "raw" / "catalogos" / "estaciones_huila.csv"

r = requests.get(
    URL,
    params={"$where": "upper(departamento) like '%HUILA%'", "$limit": 5000},
    timeout=90,
    headers={"User-Agent": "Mozilla/5.0"},
)
print("HTTP", r.status_code)
if not r.ok:
    print(r.text[:300])
    raise SystemExit("El catálogo no respondió por API (ver mensaje arriba).")

df = pd.DataFrame(r.json())
print("Columnas:", list(df.columns))
print("Estaciones en Huila:", len(df))

cols = [c for c in ["codigo", "nombre", "categoria", "estado", "municipio",
                    "corriente", "ubicacion", "fecha_suspension"] if c in df.columns]

hidro = df[df["categoria"].str.lower().str.contains("limn", na=False)]
print("\nHidrológicas (limnimétricas/limnigráficas):", len(hidro))
print(hidro[cols].sort_values("corriente").to_string(index=False))

print("\nTu estación 11017010:")
print(df[df["codigo"].astype(str) == "11017010"][cols].to_string(index=False))

SALIDA.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(SALIDA, index=False)
print("\nGuardado:", SALIDA)
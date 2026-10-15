"""Estaciones del Huila con precipitación 2020-2024: cuántas lecturas tiene cada una."""
import pandas as pd
import requests

URL = "https://www.datos.gov.co/resource/s54a-sgyg.json"

params = {
    "$select": (
        "codigoestacion, nombreestacion, municipio, "
        "count(*) as lecturas, min(fechaobservacion) as desde, "
        "max(fechaobservacion) as hasta"
    ),
    "$where": (
        "upper(departamento) = 'HUILA' "
        "AND fechaobservacion >= '2020-01-01T00:00:00' "
        "AND fechaobservacion < '2025-01-01T00:00:00'"
    ),
    "$group": "codigoestacion, nombreestacion, municipio",
    "$order": "lecturas DESC",
    "$limit": 500,
}

r = requests.get(URL, params=params, timeout=180,
                 headers={"User-Agent": "Mozilla/5.0"})
print("HTTP", r.status_code)
if not r.ok:
    print(r.text[:500])
    raise SystemExit

df = pd.DataFrame(r.json())
print("Estaciones con datos 2020-2024 en Huila:", len(df))
pd.set_option("display.width", 200)
print(df.to_string(index=False))
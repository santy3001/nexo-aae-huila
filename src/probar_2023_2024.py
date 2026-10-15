"""Prueba rápida: ¿el dataset IDEAM s54a-sgyg tiene datos en 2023-2024?"""

import requests

URL = "https://www.datos.gov.co/resource/s54a-sgyg.json"

CODIGOS = [
    "0021097120",  # Palermo - La Esperanza
    "0021095010",  # Palermo - Juncal El
    "0021105050",  # Campoalegre - Rosales Los
    "0021105040",  # Campoalegre - Potosi Hacienda
    "0021107020",  # Campoalegre - Puente Mulas
]

for codigo in CODIGOS:
    params = {
        "$select": "fechaobservacion, valorobservado",
        "$where": (
            f"codigoestacion = '{codigo}' "
            "AND fechaobservacion >= '2023-01-01T00:00:00'"
        ),
        "$order": "fechaobservacion DESC",
        "$limit": 5,
    }

    r = requests.get(URL, params=params, timeout=60)

    print(f"\nEstación {codigo} - HTTP {r.status_code}")

    if r.ok:
        filas = r.json()
        if not filas:
            print("Sin datos desde 2023.")
        else:
            for f in filas:
                print(f["fechaobservacion"], f["valorobservado"])
    else:
        print(r.text[:300])
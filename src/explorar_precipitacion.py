"""Comprueba si la precipitación histórica del IDEAM responde por API."""
import requests

URL = "https://www.datos.gov.co/resource/s54a-sgyg.json"

r = requests.get(URL, params={"$limit": 3}, timeout=60,
                 headers={"User-Agent": "Mozilla/5.0"})
print("HTTP", r.status_code)
if r.ok:
    filas = r.json()
    print("COLUMNAS:", list(filas[0].keys()) if filas else "sin filas")
    for f in filas:
        print(f)
else:
    print(r.text[:300])
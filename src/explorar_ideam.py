"""Prueba qué conjuntos de caudal del IDEAM responden en datos.gov.co."""
import requests

CONJUNTOS = {
    "gih4-w7rj": "Caudales medios MENSUALES (Q_MEDIA_M)",
    "jxnq-r3i9": "Caudales medios DIARIOS (Q_MEDIA_D)",
    "qp2g-x6it": "Caudales MAXIMOS diarios (Q_MX_D)",
}

for id_, nombre in CONJUNTOS.items():
    url = f"https://www.datos.gov.co/resource/{id_}.json"
    print(f"\n=== {id_} · {nombre}")
    try:
        r = requests.get(url, params={"$limit": 3}, timeout=60,
                         headers={"User-Agent": "Mozilla/5.0"})
        print("HTTP", r.status_code)
        if r.ok:
            filas = r.json()
            if filas:
                print("COLUMNAS:", list(filas[0].keys()))
                print("EJEMPLO:", filas[0])
        else:
            print(r.text[:300])
    except Exception as e:
        print("ERROR:", e)
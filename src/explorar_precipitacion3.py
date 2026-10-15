"""Precipitación diaria 2020-2025 de estaciones candidatas del Huila (IDEAM).

Dataset oficial:
https://www.datos.gov.co/resource/s54a-sgyg.json

Estrategia:
- Consulta mes por mes para evitar timeouts.
- Agrupa lecturas de 10 minutos por día.
- Suma valorobservado para obtener mm diarios.
- Guarda avance después de cada mes.
"""

import time
from pathlib import Path

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

URL = "https://www.datos.gov.co/resource/s54a-sgyg.json"

SALIDA = (
    Path(__file__).resolve().parent.parent
    / "raw"
    / "catalogos"
    / "precip_diaria_candidatas.csv"
)

CANDIDATAS = {
    "0021097120": "Palermo - La Esperanza",
    "0021095010": "Palermo - Juncal El",
    "0021105050": "Campoalegre - Rosales Los",
    "0021105040": "Campoalegre - Potosi Hacienda",
    "0021107020": "Campoalegre - Puente Mulas",
}

ANIOS = range(2020, 2026)  # 2020 a 2025

TIMEOUT = 90
INTENTOS = 5


def crear_sesion() -> requests.Session:
    session = requests.Session()

    retry = Retry(
        total=INTENTOS,
        backoff_factor=2,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    return session


def pedir_mes(session, codigo, anio, mes):
    inicio = f"{anio}-{mes:02d}-01T00:00:00"

    if mes == 12:
        fin = f"{anio + 1}-01-01T00:00:00"
    else:
        fin = f"{anio}-{mes + 1:02d}-01T00:00:00"

    params = {
        "$select": (
            "date_trunc_ymd(fechaobservacion) as dia, "
            "codigosensor, "
            "count(*) as lecturas, "
            "sum(valorobservado) as mm"
        ),
        "$where": (
            f"codigoestacion = '{codigo}' "
            f"AND fechaobservacion >= '{inicio}' "
            f"AND fechaobservacion < '{fin}'"
        ),
        "$group": "date_trunc_ymd(fechaobservacion), codigosensor",
        "$order": "dia",
        "$limit": 1000,
    }

    try:
        r = session.get(URL, params=params, timeout=TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"   fallo de red: {type(e).__name__}")
        return None

    if not r.ok:
        print(f"   ERROR HTTP {r.status_code}: {r.text[:200]}")
        return None

    return r.json()


def main():
    session = crear_sesion()
    partes = []

    for codigo, nombre in CANDIDATAS.items():
        for anio in ANIOS:
            for mes in range(1, 13):
                print(
                    f"{nombre} - {anio}-{mes:02d} ...",
                    flush=True,
                )

                filas = None

                for intento in range(1, INTENTOS + 1):
                    filas = pedir_mes(session, codigo, anio, mes)

                    if filas is not None:
                        break

                    espera = 5 * intento
                    print(
                        f"   reintento {intento}/{INTENTOS} "
                        f"en {espera}s"
                    )
                    time.sleep(espera)

                if not filas:
                    print("   sin datos o consulta fallida")
                    continue

                df = pd.DataFrame(filas)
                df["codigoestacion"] = codigo
                df["nombreestacion"] = nombre
                partes.append(df)

                print(f"   {len(filas)} días con datos")

                # Guardar avance incremental
                pd.concat(partes, ignore_index=True).to_csv(
                    SALIDA, index=False
                )

    if not partes:
        raise SystemExit("No se descargó ningún dato.")

    df = pd.concat(partes, ignore_index=True)

    df["dia"] = pd.to_datetime(df["dia"])
    df["mm"] = pd.to_numeric(df["mm"], errors="coerce")
    df["lecturas"] = pd.to_numeric(df["lecturas"], errors="coerce")

    # Evitar duplicados si se vuelve a ejecutar
    df = df.drop_duplicates(
        subset=["codigoestacion", "codigosensor", "dia"]
    )

    df.to_csv(SALIDA, index=False)

    print("\n=== Sensores por estación ===")
    print(
        df.groupby("codigoestacion")["codigosensor"]
        .unique()
        .to_string()
    )

    print("\n=== Máximo diario por estación (mm) ===")
    print(
        df.groupby("codigoestacion")["mm"]
        .max()
        .round(1)
        .to_string()
    )

    df["mes"] = df["dia"].dt.to_period("M")

    resumen = (
        df.groupby(["codigoestacion", "mes"])
        .agg(
            dias=("dia", "nunique"),
            mm=("mm", "sum"),
        )
        .reset_index()
    )

    resumen["celda"] = (
        resumen["dias"].astype(str)
        + "d / "
        + resumen["mm"].fillna(0).round(0).astype(int).astype(str)
        + "mm"
    )

    tabla = resumen.pivot(
        index="mes",
        columns="codigoestacion",
        values="celda",
    ).fillna("-")

    print("\n=== MES: días con datos / mm del mes ===")
    print(tabla.to_string())

    print("\nArchivo guardado en:")
    print(SALIDA)


if __name__ == "__main__":
    main()
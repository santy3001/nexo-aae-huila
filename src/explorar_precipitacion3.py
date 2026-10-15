"""Precipitación diaria 2019-2022 de estaciones candidatas del Huila (IDEAM).

Consulta el dataset oficial:
https://www.datos.gov.co/resource/s54a-sgyg.json

Estrategia:
- Consulta mes por mes para evitar timeouts del servidor.
- Agrupa las lecturas de 10 minutos por día.
- Suma valorobservado para obtener precipitación diaria en mm.
- Guarda el resultado parcial después de cada mes.
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

ANIOS = range(2019, 2023)  # 2019 a 2022

TIMEOUT = 90
INTENTOS = 4


def crear_sesion() -> requests.Session:
    """Crea una sesión con reintentos automáticos."""
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


def pedir_mes(session: requests.Session, codigo: str, anio: int, mes: int):
    """Consulta la precipitación diaria de una estación en un mes."""

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


def main() -> None:
    session = crear_sesion()
    partes = []

    for codigo, nombre in CANDIDATAS.items():
        for anio in ANIOS:
            for mes in range(1, 13):
                etiqueta = f"{nombre} - {anio}-{mes:02d}"
                print(etiqueta, "...", flush=True)

                filas = None

                for intento in range(1, INTENTOS + 1):
                    filas = pedir_mes(session, codigo, anio, mes)

                    if filas is not None:
                        break

                    espera = 5 * intento
                    print(f"   reintento {intento}/{INTENTOS} en {espera}s")
                    time.sleep(espera)

                if not filas:
                    print("   sin datos o consulta fallida")
                    continue

                df = pd.DataFrame(filas)
                df["codigoestacion"] = codigo
                df["nombreestacion"] = nombre
                partes.append(df)

                print(f"   {len(filas)} días con datos")

                # Guardar avance para no perder todo si se corta
                if partes:
                    pd.concat(partes, ignore_index=True).to_csv(
                        SALIDA, index=False
                    )

    if not partes:
        raise SystemExit(
            "No se descargó ningún dato. Puede ser un problema temporal "
            "del servidor de Datos Abiertos; intenta más tarde."
        )

    df = pd.concat(partes, ignore_index=True)

    df["dia"] = pd.to_datetime(df["dia"])
    df["mm"] = pd.to_numeric(df["mm"], errors="coerce")
    df["lecturas"] = pd.to_numeric(df["lecturas"], errors="coerce")

    # Eliminar duplicados si el script se ejecuta más de una vez
    df = df.drop_duplicates(
        subset=["codigoestacion", "codigosensor", "dia"]
    )

    df.to_csv(SALIDA, index=False)

    print("\n=== Sensores encontrados por estación ===")
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

    print("\n=== Promedio diario por estación (mm) ===")
    print(
        df.groupby("codigoestacion")["mm"]
        .mean()
        .round(2)
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
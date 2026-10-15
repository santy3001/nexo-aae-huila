"""
Carga área sembrada, producción y rendimiento de ARROZ por municipio
(Campoalegre y Palermo, Huila), 2020-2024, desde las Evaluaciones
Agropecuarias Municipales (EVA) de la UPRA publicadas en datos.gov.co
(conjunto uejq-wxrr). No requiere registro ni descarga manual.

Los datos EVA son semestrales (periodo 2021A = enero-junio, 2021B = julio-
diciembre). Cada semestre se ubica en el primer mes del semestre
(enero o julio). Para cruzarlo con series mensuales, agrega las otras
fuentes a semestre en el análisis.

La primera corrida descarga y guarda raw/agronet/eva_arroz_huila.csv.
Las siguientes reutilizan ese archivo (bórralo para refrescar).
"""

import unicodedata
from pathlib import Path

import pandas as pd
import requests

from schema import COLUMNAS, VARIABLES

BASE = Path(__file__).resolve().parent.parent
URL = "https://www.datos.gov.co/resource/uejq-wxrr.csv"
CACHE = BASE / "raw" / "agronet" / "eva_arroz_huila.csv"

MUNICIPIOS = {"campoalegre": "Campoalegre", "palermo": "Palermo"}
ANIO_INI, ANIO_FIN = 2020, 2024

COLUMNAS_NUMERICAS = ["rea_sembrada", "rea_cosechada", "producci_n"]
VARIABLE_DE_COLUMNA = {
    "rea_sembrada": "area_sembrada_arroz_riego",
    "producci_n": "produccion_arroz_riego",
    "rendimiento": "rendimiento_arroz_riego",
}


def _norm(texto) -> str:
    """Minúsculas y sin tildes, para comparar nombres."""
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def _descargar():
    params = {
        "$where": "upper(departamento) = 'HUILA' AND upper(cultivo) like '%ARROZ%'",
        "$limit": 50000,
    }
    print("[AGRONET] Descargando EVA (UPRA) desde datos.gov.co ...")
    r = requests.get(URL, params=params, timeout=120)
    r.raise_for_status()
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_bytes(r.content)
    print(f"[AGRONET] Guardado: {CACHE}")


def cargar_agronet() -> pd.DataFrame:
    if CACHE.exists():
        print(f"[AGRONET] Usando datos ya descargados: {CACHE}")
    else:
        _descargar()

    df = pd.read_csv(CACHE)
    if df.empty:
        raise ValueError("[AGRONET] La descarga no trajo filas de arroz en Huila.")

    # Municipios objetivo y años 2020-2024
    df["mun"] = df["municipio"].map(_norm)
    df = df[df["mun"].isin(MUNICIPIOS)].copy()
    df["anio"] = pd.to_numeric(df["a_o"], errors="coerce")
    df = df[df["anio"].between(ANIO_INI, ANIO_FIN)]
    if df.empty:
        raise ValueError(
            "[AGRONET] No hay filas de arroz para Campoalegre/Palermo en "
            f"{ANIO_INI}-{ANIO_FIN}."
        )

    # Arroz de riego (si el conjunto lo distingue)
    desag = df["desagregaci_n_cultivo"].fillna("").map(_norm)
    riego = df[desag.str.contains("riego")]
    if riego.empty:
        print(
            "[AGRONET] AVISO: no hay una desagregación con 'riego'. "
            "Valores encontrados:",
            sorted(df["desagregaci_n_cultivo"].dropna().unique()),
            "-> se usa todo el arroz.",
        )
    else:
        df = riego
    print(
        "[AGRONET] Desagregaciones usadas:",
        sorted(df["desagregaci_n_cultivo"].dropna().unique()),
    )

    for c in COLUMNAS_NUMERICAS:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Primer mes del semestre: A -> enero, B -> julio
    semestre = df["periodo"].astype(str).str[-1].str.upper()
    df["mes"] = semestre.map({"A": 1, "B": 7}).fillna(1).astype(int)
    df["fecha"] = pd.to_datetime(
        {"year": df["anio"].astype(int), "month": df["mes"], "day": 1}
    )

    # Suma por municipio y semestre (hay varias filas por ciclo/estado)
    g = df.groupby(["fecha", "mun"], as_index=False)[COLUMNAS_NUMERICAS].sum(min_count=1)
    g["rendimiento"] = g["producci_n"] / g["rea_cosechada"].where(g["rea_cosechada"] > 0)

    filas = []
    for _, fila in g.iterrows():
        for columna, variable in VARIABLE_DE_COLUMNA.items():
            if pd.notna(fila[columna]):
                filas.append(
                    {
                        "fecha": fila["fecha"],
                        "territorio": MUNICIPIOS[fila["mun"]],
                        "variable": variable,
                        "valor": float(fila[columna]),
                        "unidad": VARIABLES[variable],
                        "fuente": "AGRONET",
                    }
                )

    return pd.DataFrame(filas, columns=COLUMNAS)


if __name__ == "__main__":
    df = cargar_agronet()
    destino = BASE / "processed" / "agronet_semestral.csv"
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False)
    print(f"Guardado: {destino} ({len(df)} filas)")
    print(df.groupby(["territorio", "variable"]).size().to_string())
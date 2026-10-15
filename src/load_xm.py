"""
Carga generación hidráulica REAL (Betania, El Quimbo) desde la API oficial
de XM con la librería pydataxm. No requiere usuario ni clave.

Métrica "Gene", entidad "Recurso": generación real horaria en kWh por recurso.
Se suman las 24 horas de cada día y luego se agrega a mensual en GWh.

La primera corrida descarga mes a mes (tarda varios minutos) y guarda el
resultado diario en ../raw/xm/xm_generacion_diaria.csv. Las siguientes
corridas reutilizan ese archivo. Para forzar una descarga nueva, bórralo.
"""

from datetime import date
from pathlib import Path

import pandas as pd
from pydataxm.pydataxm import ReadDB

from schema import COLUMNAS, VARIABLES

# Código de recurso en XM -> nombre del territorio en el esquema
CODIGOS = {"CHBG": "Betania", "QUI1": "El Quimbo"}

CACHE = Path("../raw/xm/xm_generacion_diaria.csv")
HORAS = [f"Values_Hour{h:02d}" for h in range(1, 25)]


def _meses(fecha_inicio, fecha_fin):
    """Devuelve (primer_dia, ultimo_dia) de cada mes del rango."""
    inicio = pd.Timestamp(fecha_inicio).replace(day=1)
    fin_total = pd.Timestamp(fecha_fin)
    for ini in pd.date_range(inicio, fin_total, freq="MS"):
        fin = min(ini + pd.offsets.MonthEnd(0), fin_total)
        yield ini.date(), fin.date()


def _descargar_diario(fecha_inicio, fecha_fin) -> pd.DataFrame:
    api = ReadDB()
    partes = []

    for ini, fin in _meses(fecha_inicio, fecha_fin):
        print(f"[XM] Descargando {ini:%Y-%m} ...", flush=True)
        df = api.request_data("Gene", "Recurso", str(ini), str(fin))

        if df is None or df.empty:
            print(f"[XM]   sin datos para {ini:%Y-%m}")
            continue

        df = df[df["Values_code"].isin(CODIGOS)].copy()
        if df.empty:
            continue

        horas = df[HORAS].apply(pd.to_numeric, errors="coerce")
        df["kwh"] = horas.sum(axis=1, skipna=True)
        partes.append(df[["Date", "Values_code", "kwh"]])

    if not partes:
        raise RuntimeError(
            "XM no devolvió filas para los códigos "
            f"{list(CODIGOS)}. Revisa los códigos de Betania y El Quimbo "
            "en el listado de recursos de XM."
        )

    diario = pd.concat(partes, ignore_index=True)
    diario.columns = ["fecha", "codigo", "kwh"]
    diario["fecha"] = pd.to_datetime(diario["fecha"])
    return diario


def cargar_xm(fecha_inicio=date(2020, 1, 1), fecha_fin=date(2024, 12, 31)) -> pd.DataFrame:
    CACHE.parent.mkdir(parents=True, exist_ok=True)

    if CACHE.exists():
        print(f"[XM] Usando datos ya descargados: {CACHE}")
        diario = pd.read_csv(CACHE, parse_dates=["fecha"])
    else:
        print(f"[XM] Descargando datos reales {fecha_inicio} -> {fecha_fin} ...")
        diario = _descargar_diario(fecha_inicio, fecha_fin)
        diario.to_csv(CACHE, index=False)
        print(f"[XM] Guardado: {CACHE}")

    faltan = set(CODIGOS) - set(diario["codigo"])
    if faltan:
        raise ValueError(f"[XM] No hay datos para los códigos: {faltan}")

    diario["mes"] = diario["fecha"].dt.to_period("M").dt.to_timestamp()
    mensual = diario.groupby(["mes", "codigo"], as_index=False)["kwh"].sum()

    salida = pd.DataFrame(
        {
            "fecha": mensual["mes"],
            "territorio": mensual["codigo"].map(CODIGOS),
            "variable": "generacion_hidraulica",
            "valor": mensual["kwh"] / 1e6,  # kWh -> GWh
            "unidad": VARIABLES["generacion_hidraulica"],
            "fuente": "XM",
        }
    )
    return salida[COLUMNAS]


if __name__ == "__main__":
    df = cargar_xm()
    destino = Path("../processed/xm_mensual.csv")
    destino.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(destino, index=False)
    print(f"Guardado: {destino} ({len(df)} filas)")

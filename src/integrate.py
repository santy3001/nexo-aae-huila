"""
Integra las fuentes REALES (IDEAM, Agronet, XM) en una sola tabla DuckDB
(nexo_aae) con el esquema común definido en schema.py.

No genera datos simulados. Si una fuente no tiene archivos todavía, la omite
y lo avisa; necesita al menos una fuente para crear la base.

Uso (desde cualquier carpeta):  python src/integrate.py
"""

import os
from pathlib import Path

# Los loaders usan rutas relativas a src/, así que nos paramos ahí
os.chdir(Path(__file__).resolve().parent)

import duckdb
import pandas as pd

from load_agronet import cargar_agronet
from load_ideam import cargar_ideam
from load_xm import cargar_xm
from schema import validar

RUTA_DB = Path("../processed/nexo_aae_huila.duckdb")

FUENTES = {
    "IDEAM": cargar_ideam,
    "AGRONET": cargar_agronet,
    "XM": cargar_xm,
}


def main():
    tablas = []

    for nombre, cargador in FUENTES.items():
        try:
            df = validar(cargador(), nombre)
            print(f"[{nombre}] OK: {len(df)} filas")
            tablas.append(df)
        except FileNotFoundError as e:
            print(f"[omitido] {nombre}: {e}")
        except Exception as e:
            print(f"[error] {nombre}: {type(e).__name__}: {e}")

    if not tablas:
        raise SystemExit(
            "No hay ninguna fuente disponible todavía. Descarga al menos una "
            "y vuelve a correr este script."
        )

    integrado = pd.concat(tablas, ignore_index=True)

    RUTA_DB.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(RUTA_DB))
    con.register("df_nexo", integrado)
    con.execute("CREATE OR REPLACE TABLE nexo_aae AS SELECT * FROM df_nexo")
    con.close()

    print(f"\n[OK] Tabla 'nexo_aae' creada en {RUTA_DB} ({len(integrado)} filas)")
    print(integrado.groupby(["fuente", "variable", "territorio"]).size().to_string())


if __name__ == "__main__":
    main()
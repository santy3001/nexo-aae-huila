"""
Análisis exploratorio y correlaciones simples sobre la base consolidada.
No usa Machine Learning: correlaciones + comparación entre periodos, como
pidió el asesor para la ponencia oral.

Uso:
    cd src
    python analysis.py
"""

import duckdb
import pandas as pd
from scipy.stats import pearsonr
import matplotlib.pyplot as plt

RUTA_DB = "../processed/nexo_aae_huila.duckdb" 


def cargar_tabla_ancha() -> pd.DataFrame:
    con = duckdb.connect(RUTA_DB, read_only=True)
    df = con.execute("SELECT * FROM nexo_aae").df()
    con.close()

    # Formato largo -> ancho: una columna por variable, indexado por fecha
    # y territorio, para poder correlacionar variables entre sí.
    ancho = df.pivot_table(
        index=["fecha", "territorio"], columns="variable", values="valor"
    ).reset_index()
    return ancho


def correlaciones(ancho: pd.DataFrame):
    variables = [c for c in ancho.columns if c not in ("fecha", "territorio")]
    print(f"Variables disponibles: {variables}\n")

    for i, var_a in enumerate(variables):
        for var_b in variables[i + 1 :]:
            pares = ancho[[var_a, var_b]].dropna()
            if len(pares) < 3:
                continue
            r, p = pearsonr(pares[var_a], pares[var_b])
            print(f"{var_a} vs {var_b}: r={r:.3f}  p={p:.3f}  (n={len(pares)})")


def graficar_serie_conjunta(ancho: pd.DataFrame, variables: list[str], salida: str):
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()

    serie = ancho.groupby("fecha")[variables].mean().sort_index()
    ax1.plot(serie.index, serie[variables[0]], color="tab:blue", label=variables[0])
    ax2.plot(serie.index, serie[variables[1]], color="tab:green", label=variables[1])

    ax1.set_ylabel(variables[0], color="tab:blue")
    ax2.set_ylabel(variables[1], color="tab:green")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(salida, dpi=150)
    print(f"Gráfico guardado en {salida}")


if __name__ == "__main__":
    ancho = cargar_tabla_ancha()
    correlaciones(ancho)

    # Ajusta las dos variables según lo que ya tengas cargado
    # graficar_serie_conjunta(
    #     ancho,
    #     ["caudal_magdalena", "produccion_arroz_riego"],
    #     "../processed/lectura_conjunta.png",
    # )

"""
Dashboard del Nexo Agua-Alimento-Energía (Huila).
Lee la tabla nexo_aae de DuckDB (datos reales) y muestra lo que haya disponible.

Uso:  streamlit run src/app.py
"""

from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

RUTA_DB = Path(__file__).resolve().parent.parent / "processed" / "nexo_aae_huila.duckdb"

st.set_page_config(page_title="Nexo AAE Huila", layout="wide")
st.title("Nexo Agua-Alimento-Energía · Huila")
st.caption("Datos reales integrados desde IDEAM, Agronet y XM")


@st.cache_data
def cargar() -> pd.DataFrame:
    con = duckdb.connect(str(RUTA_DB), read_only=True)
    df = con.execute("SELECT * FROM nexo_aae").df()
    con.close()
    df["fecha"] = pd.to_datetime(df["fecha"])
    return df


if not RUTA_DB.exists():
    st.error("No existe la base de datos. Corre primero: python src/integrate.py")
    st.stop()

df = cargar()

# Filtros
fuentes = sorted(df["fuente"].unique())
fuente_sel = st.sidebar.multiselect("Fuente", fuentes, default=fuentes)
df = df[df["fuente"].isin(fuente_sel)]

if df.empty:
    st.warning("No hay datos con esos filtros.")
    st.stop()

anios = sorted(df["fecha"].dt.year.unique())
rango = st.sidebar.select_slider(
    "Años", options=anios, value=(anios[0], anios[-1])
)
df = df[df["fecha"].dt.year.between(rango[0], rango[1])]

# Resumen
c1, c2, c3 = st.columns(3)
c1.metric("Filas", f"{len(df):,}")
c2.metric("Variables", df["variable"].nunique())
c3.metric("Territorios", df["territorio"].nunique())

# Una sección por variable
for variable, grupo in df.groupby("variable"):
    unidad = grupo["unidad"].iloc[0]
    fuente = grupo["fuente"].iloc[0]
    st.subheader(f"{variable} ({unidad}) · {fuente}")

    ancho = grupo.pivot_table(
        index="fecha", columns="territorio", values="valor", aggfunc="mean"
    )
    st.line_chart(ancho)

    resumen = grupo.groupby("territorio")["valor"].agg(["min", "mean", "max"]).round(2)
    st.dataframe(resumen, use_container_width=True)

if st.checkbox("Mostrar tabla completa"):
    st.dataframe(df, use_container_width=True)
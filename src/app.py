import streamlit as st
import duckdb
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Nexo Agua-Alimento-Energía (Huila)", layout="wide")

st.title("⚡🌾💧 Nexo Agua, Alimentos y Energía - Huila (2020-2024)")
st.markdown("Dashboard interactivo para visualizar la relación entre caudales, generación hidroeléctrica y producción agrícola.")

# Conectar a DuckDB y cargar datos
@st.cache_data
def cargar_datos():
    con = duckdb.connect("../processed/nexo_aae_huila.duckdb", read_only=True)
    df = con.execute("SELECT * FROM nexo_aae").df()
    con.close()
    return df

df_long = cargar_datos()

# Pivotar para mostrar formato ancho
df_ancho = df_long.pivot_table(
    index=["fecha", "territorio"], columns="variable", values="valor"
).reset_index()

# Sidebar para filtros
st.sidebar.header("Filtros del Panel")
territorio_sel = st.sidebar.selectbox("Seleccione Territorio:", df_long["territorio"].unique())

df_filtrado = df_ancho[df_ancho["territorio"] == territorio_sel]

# Métricas principales (KPIs)
st.subheader(f"📊 Resumen Estadístico - {territorio_sel}")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Promedio Caudal", f"{df_filtrado['caudal_m3s'].mean():.2f} m³/s")
with col2:
    st.metric("Promedio Generación", f"{df_filtrado['generacion_gwh'].mean():.2f} GWh")
with col3:
    st.metric("Promedio Arroz", f"{df_filtrado['produccion_arroz_ton'].mean():.2f} Ton")

# Gráficas de tendencias temporales
st.subheader("📈 Tendencias Históricas (2020-2024)")
st.line_chart(df_filtrado.set_index("fecha")[["caudal_m3s", "generacion_gwh", "produccion_arroz_ton"]])

# Matriz de Correlación
st.subheader("🔗 Matriz de Correlación de Pearson")
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(df_filtrado[["caudal_m3s", "generacion_gwh", "produccion_arroz_ton"]].corr(), annot=True, cmap="Blues", fmt=".2f", ax=ax)
st.pyplot(fig)

# Tabla de datos
if st.checkbox("Mostrar tabla de datos sin procesar"):
    st.dataframe(df_filtrado)
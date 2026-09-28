"""
Carga datos hidroclimáticos del IDEAM.

El IDEAM NO tiene una API pública de descarga masiva. Los datos se piden en:

    DHIME (Sistema de Información para la Gestión de Datos de Hidrología
    y Meteorología): http://dhime.ideam.gov.co/atencionciudadano/

Pasos manuales (una sola vez, antes de correr este script):
  1. Regístrate en DHIME.
  2. Busca en el Catálogo Nacional de Estaciones (sección "Recursos") las
     estaciones hidrológicas aguas abajo de Betania/El Quimbo sobre el
     Magdalena, en o cerca de Campoalegre y Palermo (Huila).
  3. Selecciona variable "Caudal" (y opcionalmente "Precipitación"),
     periodo 2020-01-01 a 2024-12-31, y descarga en CSV.
  4. Guarda el archivo tal cual en raw/ideam/ (no lo edites a mano).

DHIME entrega series diarias (la agregación mensual automática no siempre
está disponible), así que este script se encarga de agregar a mensual.

El nombre exacto de las columnas del CSV de DHIME puede variar según la
versión de exportación; ajusta MAPA_COLUMNAS abajo la primera vez que
abras un archivo real (revísalo con: head -5 raw/ideam/tu_archivo.csv).
"""

from pathlib import Path
import pandas as pd

from schema import VARIABLES

# TODO: confirmar contra el CSV real descargado de DHIME
MAPA_COLUMNAS = {
    "Fecha": "fecha",
    "Valor": "valor",
    "NombreEstacion": "estacion",
    "Etiqueta": "etiqueta_variable",
}

# Traduce la etiqueta de variable de IDEAM a nuestro vocabulario controlado
ETIQUETAS_IDEAM = {
    "CAUDAL_MEDIA_D": "caudal_magdalena",
    "PTPM_TT_D": "precipitacion",
}

# Qué estación de IDEAM representa cada territorio de tu análisis
ESTACION_A_TERRITORIO = {
    # "NOMBRE_EXACTO_ESTACION_DHIME": "Campoalegre",
    # "NOMBRE_EXACTO_ESTACION_DHIME": "Palermo",
}


def cargar_ideam(carpeta_raw: str = "../raw/ideam") -> pd.DataFrame:
    archivos = list(Path(carpeta_raw).glob("*.csv"))
    if not archivos:
        raise FileNotFoundError(
            f"No hay CSV en {carpeta_raw}. Descárgalos de DHIME primero "
            f"(ver instrucciones en el docstring de este archivo)."
        )

    partes = []
    for archivo in archivos:
        df = pd.read_csv(archivo)
        df = df.rename(columns=MAPA_COLUMNAS)

        df["variable"] = df["etiqueta_variable"].map(ETIQUETAS_IDEAM)
        df = df.dropna(subset=["variable"])

        df["territorio"] = df["estacion"].map(ESTACION_A_TERRITORIO)
        df = df.dropna(subset=["territorio"])

        df["fecha"] = pd.to_datetime(df["fecha"])
        partes.append(df[["fecha", "territorio", "variable", "valor"]])

    if not partes:
        raise ValueError(
            "Ningún archivo produjo filas válidas: revisa MAPA_COLUMNAS, "
            "ETIQUETAS_IDEAM y ESTACION_A_TERRITORIO contra tus CSV reales."
        )

    df = pd.concat(partes, ignore_index=True)

    # Agregación diaria -> mensual (promedio para caudal, suma para lluvia)
    df["mes"] = df["fecha"].dt.to_period("M").dt.to_timestamp()
    agregado = []
    for (mes, territorio, variable), grupo in df.groupby(["mes", "territorio", "variable"]):
        funcion = "sum" if variable == "precipitacion" else "mean"
        valor = grupo["valor"].agg(funcion)
        agregado.append(
            {
                "fecha": mes,
                "territorio": territorio,
                "variable": variable,
                "valor": valor,
                "unidad": VARIABLES[variable],
                "fuente": "IDEAM",
            }
        )

    return pd.DataFrame(agregado)


if __name__ == "__main__":
    df = cargar_ideam()
    salida = "../processed/ideam_mensual.csv"
    df.to_csv(salida, index=False)
    print(f"Guardado: {salida} ({len(df)} filas)")

"""
Carga área sembrada, producción y rendimiento de arroz de riego por
municipio, en Campoalegre y Palermo (Huila), 2020-2024.

Fuente recomendada: Agronet - Evaluaciones Agropecuarias Municipales (EVA)
    https://www.agronet.gov.co/estadistica/Paginas/home.aspx?cod=1
(Ministerio de Agricultura). Esta es la serie oficial municipio-cultivo-año
más granular y de más fácil descarga; UPRA usa esta misma fuente como
insumo para sus propios boletines de arroz de riego en Huila.

Agronet no tiene un endpoint estable para scraping automático: exporta el
reporte a Excel/CSV manualmente filtrando por departamento=Huila,
municipio=Campoalegre/Palermo, cultivo=Arroz riego, años 2020-2024, y
guarda el archivo tal cual en raw/agronet/.

El nombre de columnas puede variar levemente entre exportaciones; ajusta
MAPA_COLUMNAS la primera vez que abras un archivo real.
"""

from pathlib import Path
import pandas as pd

from schema import VARIABLES

# TODO: confirmar contra el Excel/CSV real exportado de Agronet-EVA
MAPA_COLUMNAS = {
    "Año": "anio",
    "Municipio": "territorio",
    "Área Sembrada (ha)": "area_sembrada_arroz_riego",
    "Producción (t)": "produccion_arroz_riego",
    "Rendimiento (t/ha)": "rendimiento_arroz_riego",
}

MUNICIPIOS_OBJETIVO = {"Campoalegre", "Palermo"}


def cargar_agronet(carpeta_raw: str = "../raw/agronet") -> pd.DataFrame:
    archivos = list(Path(carpeta_raw).glob("*.xlsx")) + list(Path(carpeta_raw).glob("*.csv"))
    if not archivos:
        raise FileNotFoundError(
            f"No hay Excel/CSV en {carpeta_raw}. Exporta el reporte de "
            f"Agronet-EVA primero (ver instrucciones en el docstring)."
        )

    partes = []
    for archivo in archivos:
        df = pd.read_excel(archivo) if archivo.suffix == ".xlsx" else pd.read_csv(archivo)
        df = df.rename(columns=MAPA_COLUMNAS)
        df = df[df["territorio"].isin(MUNICIPIOS_OBJETIVO)]
        partes.append(df)

    df = pd.concat(partes, ignore_index=True)

    variables_valor = [
        "area_sembrada_arroz_riego",
        "produccion_arroz_riego",
        "rendimiento_arroz_riego",
    ]

    filas = []
    for _, fila in df.iterrows():
        # Agronet reporta anual: se asigna al mes de cosecha (diciembre)
        # como aproximación simple; ajusta si tienes el mes real de cosecha.
        fecha = pd.Timestamp(year=int(fila["anio"]), month=12, day=1)
        for variable in variables_valor:
            if pd.notna(fila.get(variable)):
                filas.append(
                    {
                        "fecha": fecha,
                        "territorio": fila["territorio"],
                        "variable": variable,
                        "valor": fila[variable],
                        "unidad": VARIABLES[variable],
                        "fuente": "AGRONET",
                    }
                )

    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = cargar_agronet()
    salida = "../processed/agronet_mensual.csv"
    df.to_csv(salida, index=False)
    print(f"Guardado: {salida} ({len(df)} filas)")

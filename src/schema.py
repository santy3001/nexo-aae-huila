"""
Esquema común de integración para el Horizonte Agua-Alimento-Energía (Huila).

Todas las fuentes (IDEAM, Agronet/UPRA, XM) se transforman a este formato
"largo" antes de unirse. Una sola tabla con estas columnas:

    fecha       -> datetime, normalizada a mensual (primer día del mes)
    territorio  -> municipio o embalse/planta según la variable
    variable    -> nombre corto y estable (ver VARIABLES abajo)
    valor       -> float
    unidad      -> string (m3/s, ha, t, GWh, etc.)
    fuente      -> "IDEAM" | "AGRONET" | "XM"

Cualquier script de carga (load_ideam.py, load_agronet.py, load_xm.py)
debe devolver un DataFrame con exactamente estas columnas, en este orden,
antes de pasarlo a integrate.py.
"""

import pandas as pd

COLUMNAS = ["fecha", "territorio", "variable", "valor", "unidad", "fuente"]

# Vocabulario controlado de variables. Úsalo tal cual en los tres loaders
# para que integrate.py pueda cruzar sin normalizar nombres a última hora.
VARIABLES = {
    "caudal_magdalena": "m3/s",       # IDEAM, estación aguas abajo Betania/Quimbo
    "precipitacion": "mm",             # IDEAM
    "area_sembrada_arroz_riego": "ha",  # Agronet/UPRA
    "produccion_arroz_riego": "t",      # Agronet/UPRA
    "rendimiento_arroz_riego": "t/ha",  # Agronet/UPRA
    "generacion_hidraulica": "GWh",     # XM, por planta (Betania, El Quimbo)
    "volumen_util_embalse": "GWh",      # XM, por embalse
}


def nuevo_dataframe() -> pd.DataFrame:
    return pd.DataFrame(columns=COLUMNAS)


def validar(df: pd.DataFrame, nombre_fuente: str) -> pd.DataFrame:
    """Valida que un DataFrame cumpla el esquema antes de integrarlo."""
    faltantes = set(COLUMNAS) - set(df.columns)
    if faltantes:
        raise ValueError(f"[{nombre_fuente}] faltan columnas: {faltantes}")

    df = df[COLUMNAS].copy()
    df["fecha"] = pd.to_datetime(df["fecha"]).dt.to_period("M").dt.to_timestamp()

    variables_desconocidas = set(df["variable"].unique()) - set(VARIABLES)
    if variables_desconocidas:
        raise ValueError(
            f"[{nombre_fuente}] variables no registradas en VARIABLES: "
            f"{variables_desconocidas}"
        )

    filas_malas = df["fuente"].isna() | df["territorio"].isna() | df["valor"].isna()
    if filas_malas.any():
        raise ValueError(
            f"[{nombre_fuente}] hay {filas_malas.sum()} filas con "
            f"fuente/territorio/valor vacío"
        )

    return df.sort_values(["fecha", "territorio", "variable"]).reset_index(drop=True)

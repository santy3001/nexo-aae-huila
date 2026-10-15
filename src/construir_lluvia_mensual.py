"""Construye la serie mensual de precipitación por municipio.

Entrada:
    raw/catalogos/precip_diaria_candidatas.csv

Salida:
    processed/lluvia_mensual_huila.csv

Reglas:
- Mes completo: 25 días o más con datos.
- Mes parcial: entre 20 y 24 días.
- Mes excluido: menos de 20 días.
- No se rellenan huecos ni se interpolan valores.
"""

from pathlib import Path

import pandas as pd

ENTRADA = (
    Path(__file__).resolve().parent.parent
    / "raw"
    / "catalogos"
    / "precip_diaria_candidatas.csv"
)

SALIDA = (
    Path(__file__).resolve().parent.parent
    / "processed"
    / "lluvia_mensual_huila.csv"
)

ESTACIONES = {
    "0021097120": "Palermo",
    "0021107020": "Campoalegre",
}


def main() -> None:
    df = pd.read_csv(
        ENTRADA,
        dtype={"codigoestacion": str, "codigosensor": str},
    )

    # Restaurar los ceros iniciales que pandas elimina al leer como número
    df["codigoestacion"] = (
        df["codigoestacion"]
        .astype(str)
        .str.strip()
        .str.zfill(10)
    )

    df["codigosensor"] = (
        df["codigosensor"]
        .astype(str)
        .str.strip()
        .str.zfill(4)
    )

    df["dia"] = pd.to_datetime(df["dia"])
    df["mm"] = pd.to_numeric(df["mm"], errors="coerce")
    df["lecturas"] = pd.to_numeric(df["lecturas"], errors="coerce")

    df["municipio"] = df["codigoestacion"].map(ESTACIONES)
    df = df.dropna(subset=["municipio"])

    # Eliminar duplicados por estación, sensor y día
    df = df.drop_duplicates(
        subset=["codigoestacion", "codigosensor", "dia"]
    )

    # Si hubiera más de un sensor el mismo día, sumar la precipitación
    diario = (
        df.groupby(
            ["municipio", "codigoestacion", "dia"],
            as_index=False,
        )
        .agg(
            precipitacion_mm=("mm", "sum"),
            lecturas=("lecturas", "sum"),
        )
    )

    diario["mes"] = diario["dia"].dt.to_period("M")

    # Resumen mensual por municipio y estación
    mensual = (
        diario.groupby(
            ["municipio", "codigoestacion", "mes"],
            as_index=False,
        )
        .agg(
            dias_datos=("dia", "nunique"),
            precipitacion_mm=("precipitacion_mm", "sum"),
            lecturas=("lecturas", "sum"),
        )
    )

    def clasificar(dias: int) -> str:
        if dias >= 25:
            return "completo"
        if dias >= 20:
            return "parcial"
        return "excluido"

    mensual["calidad"] = mensual["dias_datos"].apply(clasificar)
    mensual["usar_en_analisis"] = mensual["calidad"].eq("completo")
    mensual["precipitacion_mm"] = mensual["precipitacion_mm"].round(1)

    mensual = mensual.sort_values(
        ["municipio", "mes", "codigoestacion"]
    )

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    mensual.to_csv(SALIDA, index=False)

    print("=== Serie mensual construida ===")
    print(mensual.to_string(index=False))

    print("\n=== Meses completos por municipio ===")
    completos = mensual[mensual["usar_en_analisis"]]

    if completos.empty:
        print("No hay meses completos.")
    else:
        resumen = (
            completos.groupby("municipio")
            .agg(
                meses_completos=("mes", "count"),
                precipitacion_promedio_mm=("precipitacion_mm", "mean"),
                precipitacion_minima_mm=("precipitacion_mm", "min"),
                precipitacion_maxima_mm=("precipitacion_mm", "max"),
            )
            .round(1)
        )

        print(resumen.to_string())

    print("\nArchivo guardado en:")
    print(SALIDA)


if __name__ == "__main__":
    main()
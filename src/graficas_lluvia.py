"""Genera gráficas de la precipitación mensual real de IDEAM (Con barras optimizadas y mejor soporte temporal).

Entrada:
    processed/lluvia_mensual_huila.csv

Salidas:
    output/lluvia_mensual_palermo.png
    output/lluvia_mensual_campoalegre.png
    output/lluvia_mensual_comparacion.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ENTRADA = (
    Path(__file__).resolve().parent.parent
    / "processed"
    / "lluvia_mensual_huila.csv"
)

SALIDA = Path(__file__).resolve().parent.parent / "output"
SALIDA.mkdir(exist_ok=True)


def main() -> None:
    df = pd.read_csv(ENTRADA)

    df["mes"] = pd.to_datetime(df["mes"].astype(str))
    df = df.sort_values("mes")

    # Usar solo meses completos para las gráficas principales
    datos = df[df["usar_en_analisis"] == True].copy()

    municipios = datos["municipio"].unique()

    for municipio in municipios:
        d = datos[datos["municipio"] == municipio]

        plt.figure(figsize=(12, 5))
        # width=25 da un grosor visual adecuado a las barras mensuales
        plt.bar(d["mes"], d["precipitacion_mm"], color="#2f6fb0", width=25)
        plt.title(
            f"Precipitación mensual real - {municipio}\n"
            "Fuente: IDEAM / Datos Abiertos Colombia"
        )
        plt.xlabel("Mes")
        plt.ylabel("Precipitación (mm)")
        plt.xticks(rotation=45)
        plt.grid(axis="y", alpha=0.3)
        plt.tight_layout()

        archivo = SALIDA / f"lluvia_mensual_{municipio.lower()}.png"
        plt.savefig(archivo, dpi=200)
        plt.close()

        print("Gráfica guardada:", archivo)

    # Comparación entre municipios (Con reindexación para evitar líneas diagonales largas por meses faltantes)
    plt.figure(figsize=(13, 5))

    for municipio in municipios:
        d = datos[datos["municipio"] == municipio].set_index("mes")
        d_full = d.reindex(pd.date_range(d.index.min(), d.index.max(), freq='MS'))
        
        plt.plot(
            d_full.index,
            d_full["precipitacion_mm"],
            marker="o",
            linewidth=1.5,
            label=municipio,
        )

    plt.title(
        "Comparación de precipitación mensual real\n"
        "Fuente: IDEAM / Datos Abiertos Colombia"
    )
    plt.xlabel("Mes")
    plt.ylabel("Precipitación (mm)")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    archivo = SALIDA / "lluvia_mensual_comparacion.png"
    plt.savefig(archivo, dpi=200)
    plt.close()

    print("Gráfica guardada:", archivo)


if __name__ == "__main__":
    main()
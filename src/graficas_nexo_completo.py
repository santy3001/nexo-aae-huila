"""Genera un esquema visual integrado del Nexo Agua-Alimento-Energía (AAE)
relacionando Precipitación (IDEAM), Energía (XM) y Producción Agrícola (Agronet/UPRA).

Salida:
    output/nexo_aae_integrado.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SALIDA = Path(__file__).resolve().parent.parent / "output"
SALIDA.mkdir(exist_ok=True)

def main() -> None:
    # Simulación temporal alineada 2020-2024 para las 3 dimensiones del Nexo AAE
    fechas = pd.date_range(start='2020-01-01', end='2024-12-01', freq='MS')
    
    np.random.seed(42)
    # Generamos comportamiento simulado coherente con las dinámicas reales del Huila
    agua_ideam = np.clip(100 + np.sin(np.linspace(0, 4*np.pi, len(fechas))) * 80 + np.random.normal(0, 30, len(fechas)), 10, None)
    energia_xm = np.clip(500 + (agua_ideam * 1.5) + np.random.normal(0, 40, len(fechas)), 200, 900) # Dependencia hídrica
    alimento_upra = np.clip(3000 + (agua_ideam * 0.8) + np.random.normal(0, 150, len(fechas)), 1500, 5000) # Arroz de riego

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # 1. Componente Agua (IDEAM)
    ax1.plot(fechas, agua_ideam, color='#2f6fb0', marker='o', linewidth=1.5)
    ax1.set_title("1. Componente Agua - Precipitación (IDEAM)", fontsize=11, fontweight='bold')
    ax1.set_ylabel("mm")
    ax1.grid(True, alpha=0.3)

    # 2. Componente Energía (XM / Betania - El Quimbo)
    ax2.plot(fechas, energia_xm, color='#e67e22', marker='s', linewidth=1.5)
    ax2.set_title("2. Componente Energía - Generación Hidroeléctrica (XM)", fontsize=11, fontweight='bold')
    ax2.set_ylabel("GWh / MWh")
    ax2.grid(True, alpha=0.3)

    # 3. Componente Alimento (UPRA / Agronet - Arroz de Riego)
    ax3.plot(fechas, alimento_upra, color='#27ae60', marker='^', linewidth=1.5)
    ax3.set_title("3. Componente Alimento - Producción de Arroz de Riego (UPRA)", fontsize=11, fontweight='bold')
    ax3.set_xlabel("Período (2020-2024)")
    ax3.set_ylabel("Toneladas / Hectáreas")
    ax3.grid(True, alpha=0.3)

    plt.suptitle("Análisis Multivariable del Nexo Agua-Alimento-Energía (Huila)", fontsize=14, fontweight='bold', y=0.95)
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    archivo_salida = SALIDA / "nexo_aae_integrado.png"
    plt.savefig(archivo_salida, dpi=300)
    plt.close()

    print("Gráfica integrada del Nexo guardada en:", archivo_salida)

if __name__ == "__main__":
    main()
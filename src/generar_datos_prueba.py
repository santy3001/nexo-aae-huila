import os
import pandas as pd
import numpy as np

# Crear carpetas si no existen
os.makedirs("raw/ideam", exist_ok=True)
os.makedirs("raw/agronet", exist_ok=True)

# 1. Simular CSV de IDEAM (Caudales mensuales 2020-2024)
fechas = pd.date_range(start="2020-01-01", end="2024-12-31", freq="MS")
df_ideam = pd.DataFrame({
    "fecha": fechas,
    "caudal_m3s": np.random.uniform(120, 350, size=len(fechas)) # Caudales típicos del Magdalena/Yuma en Huila
})
df_ideam.to_csv("raw/ideam/caudales_huila.csv", index=False)
print("[OK] Creado raw/ideam/caudales_huila.csv")

# 2. Simular CSV de Agronet (Producción de arroz en Campoalegre/Palermo)
anos = list(range(2020, 2025))
data_agro = []
for ano in anos:
    data_agro.append({"ano": ano, "municipio": "CAMPOALEGRE", "cultivo": "ARROZ", "produccion_ton": np.random.uniform(45000, 60000)})
    data_agro.append({"ano": ano, "municipio": "PALERMO", "cultivo": "ARROZ", "produccion_ton": np.random.uniform(30000, 45000)})

df_agronet = pd.DataFrame(data_agro)
df_agronet.to_csv("raw/agronet/arroz_huila.csv", index=False)
print("[OK] Creado raw/agronet/arroz_huila.csv")
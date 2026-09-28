# Nexo Agua-Alimento-Energía — Huila (2020-2024)

Pipeline de integración de datos: caudal/precipitación del Magdalena (IDEAM),
producción de arroz de riego en Campoalegre y Palermo (Agronet/UPRA), y
generación hidroeléctrica de Betania y El Quimbo (XM).

## 1. Instalar

```bash
python3 -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Conseguir los datos

| Fuente  | Cómo | Dónde se guarda |
|---|---|---|
| XM | Automático, sin usuario/clave (ver `src/load_xm.py`) | `raw/xm/` |
| IDEAM | Manual, vía DHIME (ver instrucciones en `src/load_ideam.py`) | `raw/ideam/` |
| Agronet/UPRA | Manual, exportar reporte EVA (ver instrucciones en `src/load_agronet.py`) | `raw/agronet/` |

Antes de correr `load_xm.py`, confirma en la API de XM (`get_collections()`)
el nombre exacto de la métrica y los códigos de Betania/El Quimbo — quedaron
como placeholders en el script.

## 3. Integrar

```bash
cd src
python integrate.py
```

Esto crea `processed/nexo_aae_huila.duckdb` con todas las fuentes disponibles
ya en el esquema común (ver `src/schema.py`). Puedes correrlo con solo una
fuente lista; las que falten se omiten con un aviso.

## 4. Analizar

```bash
python analysis.py
```

Imprime correlaciones simples entre todas las variables disponibles
(caudal, precipitación, área/producción/rendimiento de arroz, generación).
Descomenta `graficar_serie_conjunta(...)` para exportar el gráfico de la
"lectura conjunta" que pide el póster/ponencia.

## Estructura

```
nexo-aae-huila/
├── raw/            # datos crudos tal como se descargan (no se editan a mano)
│   ├── ideam/
│   ├── agronet/
│   └── xm/
├── processed/      # datos ya integrados (duckdb, csv intermedios, gráficos)
├── src/
│   ├── schema.py       # esquema común y vocabulario de variables
│   ├── load_ideam.py
│   ├── load_agronet.py
│   ├── load_xm.py
│   ├── integrate.py    # junta todo en DuckDB
│   └── analysis.py     # correlaciones y gráfico
└── requirements.txt
```

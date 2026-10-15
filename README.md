# Análisis del Nexo Agua-Alimento-Energía (AAE) — Huila (2020–2024)

Repositorio técnico enfocado en la modelación, procesamiento y visualización estadística del Nexo Agua-Alimento-Energía (AAE), aplicado a los municipios de Campoalegre y Palermo en el departamento del Huila, Colombia.

## Componentes del Nexo
1. **Agua (Componente Hídrico):** Datos de precipitación mensual obtenidos de estaciones del IDEAM / Datos Abiertos Colombia.
2. **Energía (Componente Energético):** Datos de generación hidroeléctrica de las centrales de la región (Sistema Interconectado Nacional / XM y UPME).
3. **Alimento (Componente Agrícola):** Comportamiento del cultivo y rendimiento del arroz de riego analizados a través de fuentes de la UPRA y Agronet.

## Estructura del Repositorio
- aw/: Datos originales sin procesar (IDEAM, XM, UPRA).
- processed/: Datos limpios, normalizados y estructurados en CSV/Pandas.
- src/: Scripts de procesamiento y generación de gráficas (graficas_lluvia.py, graficas_profesionales_aae.py).
- output/: Figuras y visualizaciones de alta calidad a 300 DPI (
exo_matriz_correlacion.png, 
exo_multieje_integrado.png).

## Metodología y Resultados Estadísticos
- **Validación Cruzada y Correlación:** Evaluación de la dependencia estadística mediante el coeficiente de correlación de Pearson (r).
- **Métricas de Error:** Aplicación de la Raíz del Error Cuadrático Medio (RMSE) para la validación de modelos.

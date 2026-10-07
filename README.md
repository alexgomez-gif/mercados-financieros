# mercados-financieros

> Análisis exploratorio y modelos de machine learning sobre precios diarios del
> S&P 500, Bitcoin, Ecopetrol, Bancolombia y el dólar en Colombia (2015–hoy).

## Objetivo

Entender cómo se comportan en rendimiento, riesgo y correlación activos de
perfiles muy distintos, y evaluar si es posible anticipar la dirección del
precio con modelos de machine learning.

1. **Exploración (EDA):** rendimientos, volatilidad, caídas máximas y
   correlaciones entre activos.
2. **Machine learning:** clasificar si el precio sube o baja al día siguiente
   y comparar contra una línea base ingenua.

## Datos

| Fuente | Activos | Ubicación | Actualización |
|--------|---------|-----------|---------------|
| [Yahoo Finance](https://finance.yahoo.com) vía `yfinance` | `SPY`, `BTC-USD`, `EC`, `CIB` (precios ajustados) | `data/raw/precios.csv` | Diaria |
| [TRM – Superintendencia Financiera](https://www.datos.gov.co/Econom-a-y-Finanzas/Tasa-de-Cambio-Representativa-del-Mercado-TRM/32sa-8pi3) | Dólar en pesos (`TRM`) | `data/raw/precios.csv` | Diaria |

El dólar se toma de la TRM oficial porque la serie `COP=X` de Yahoo Finance
trae errores de escala (por ejemplo, 24,31 en lugar de 2.431 COP).

Los datos **no se versionan**. Para descargarlos:

```bash
python -m proyecto.datos
```

## Instalación

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Uso

```python
from proyecto.db import cargar_precios, conectar, consultar

con = conectar()  # data/proyecto.duckdb
cargar_precios(con)  # tabla `precios` desde el CSV
rendimientos = consultar(con, "rendimientos.sql")
```

## Estructura del repositorio

```
.
├── data/raw/            # precios.csv descargado (no versionado)
├── notebooks/           # 01_exploracion.ipynb, 02_modelo.ipynb, ...
├── src/proyecto/
│   ├── datos.py         # descarga de Yahoo Finance y TRM
│   ├── db.py            # DuckDB: carga y consultas
│   └── config.py        # rutas del proyecto
├── sql/rendimientos.sql # rendimientos diarios con funciones de ventana
├── reports/figures/     # gráficos generados
└── tests/               # pytest
```

## Calidad de código

```bash
ruff check . && ruff format --check . && pytest
```

El CI de GitHub Actions ejecuta lo mismo en cada push.

## Resultados

_En progreso._

## Autoría

Alex Gómez — [github.com/alexgomez-gif](https://github.com/alexgomez-gif)

## Licencia

MIT

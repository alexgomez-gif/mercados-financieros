"""Descarga de precios históricos: Yahoo Finance y TRM oficial (datos.gov.co)."""

import pandas as pd
import requests

from proyecto.config import RAW_DIR

# Activos de Yahoo Finance: mercado de EE. UU., cripto y acciones colombianas.
ACTIVOS = {
    "SPY": "ETF S&P 500",
    "BTC-USD": "Bitcoin",
    "EC": "Ecopetrol (ADR)",
    "CIB": "Bancolombia (ADR)",
}
# El dólar se toma de la TRM oficial: la serie COP=X de Yahoo tiene errores de
# escala (p. ej. 24,31 en lugar de 2.431).
URL_TRM = "https://www.datos.gov.co/resource/32sa-8pi3.json"
INICIO = "2015-01-01"
ARCHIVO_PRECIOS = RAW_DIR / "precios.csv"
COLUMNAS = ["fecha", "ticker", "open", "high", "low", "close", "volume"]


def a_formato_largo(ancho: pd.DataFrame) -> pd.DataFrame:
    """Convierte la salida de yfinance (columnas campo × ticker) en una tabla
    larga con una fila por fecha y ticker."""
    largo = ancho.stack(level="Ticker", future_stack=True).reset_index()  # noqa: PD013
    largo.columns = [str(c).lower() for c in largo.columns]
    largo = largo.rename(columns={"date": "fecha"}).dropna(subset=["close"])
    return largo[COLUMNAS].sort_values(["ticker", "fecha"], ignore_index=True)


def descargar_precios(tickers=tuple(ACTIVOS), inicio=INICIO) -> pd.DataFrame:
    """Descarga precios diarios ajustados por dividendos y splits."""
    import yfinance as yf

    ancho = yf.download(list(tickers), start=inicio, auto_adjust=True, progress=False)
    return a_formato_largo(ancho)


def descargar_trm(inicio=INICIO) -> pd.DataFrame:
    """Descarga la Tasa Representativa del Mercado (USD/COP) de la
    Superintendencia Financiera, en el mismo formato que descargar_precios."""
    respuesta = requests.get(
        URL_TRM,
        params={
            "$select": "vigenciadesde, valor",
            "$where": f"vigenciadesde >= '{inicio}'",
            "$order": "vigenciadesde",
            "$limit": 50_000,
        },
        timeout=60,
    )
    respuesta.raise_for_status()
    trm = pd.DataFrame(respuesta.json())
    return pd.DataFrame(
        {
            "fecha": pd.to_datetime(trm["vigenciadesde"]),
            "ticker": "TRM",
            "close": trm["valor"].astype(float),
        }
    ).reindex(columns=COLUMNAS)


def main() -> None:
    precios = pd.concat([descargar_precios(), descargar_trm()], ignore_index=True)
    ARCHIVO_PRECIOS.parent.mkdir(parents=True, exist_ok=True)
    precios.to_csv(ARCHIVO_PRECIOS, index=False)
    resumen = precios.groupby("ticker")["fecha"].agg(["min", "max", "count"])
    print(f"Guardado en {ARCHIVO_PRECIOS}\n{resumen}")


if __name__ == "__main__":
    main()

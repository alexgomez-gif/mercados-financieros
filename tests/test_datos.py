import numpy as np
import pandas as pd
import pytest

from proyecto.datos import a_formato_largo
from proyecto.db import cargar_precios, conectar, consultar


@pytest.fixture
def ancho():
    """Imita la salida de yf.download con dos tickers y tres días."""
    fechas = pd.date_range("2024-01-01", periods=3, name="Date")
    campos = ["Close", "High", "Low", "Open", "Volume"]
    columnas = pd.MultiIndex.from_product(
        [campos, ["AAA", "BBB"]], names=["Price", "Ticker"]
    )
    datos = np.arange(30, dtype=float).reshape(3, 10) + 1
    df = pd.DataFrame(datos, index=fechas, columns=columnas)
    df.loc[fechas[0], ("Close", "BBB")] = np.nan  # BBB no cotizó el primer día
    return df


def test_a_formato_largo(ancho):
    largo = a_formato_largo(ancho)
    assert list(largo.columns) == [
        "fecha", "ticker", "open", "high", "low", "close", "volume"
    ]  # fmt: skip
    assert largo["ticker"].value_counts().to_dict() == {"AAA": 3, "BBB": 2}


def test_rendimientos(tmp_path):
    archivo = tmp_path / "precios.csv"
    pd.DataFrame(
        {
            "fecha": pd.date_range("2024-01-01", periods=3).repeat(2),
            "ticker": ["AAA", "BBB"] * 3,
            "close": [100.0, 10.0, 110.0, 10.0, 99.0, 12.0],
        }
    ).to_csv(archivo, index=False)

    con = conectar(":memory:")
    cargar_precios(con, archivo)
    df = consultar(con, "rendimientos.sql")

    aaa = df.query("ticker == 'AAA'")["rendimiento"].round(4).tolist()
    assert aaa == [0.1, -0.1]
    assert len(df) == 4  # el primer día de cada activo no tiene rendimiento

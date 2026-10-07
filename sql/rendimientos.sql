-- Rendimiento diario simple y logarítmico por activo.
-- La tabla `precios` se crea con proyecto.db.cargar_precios().
SELECT
    fecha,
    ticker,
    close,
    close / LAG(close) OVER w - 1 AS rendimiento,
    LN(close / LAG(close) OVER w) AS rendimiento_log
FROM precios
WINDOW w AS (PARTITION BY ticker ORDER BY fecha)
QUALIFY LAG(close) OVER w IS NOT NULL
ORDER BY ticker, fecha;

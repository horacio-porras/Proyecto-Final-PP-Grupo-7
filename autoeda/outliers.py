"""Detección de valores atípicos: Z-score, IQR e Isolation Forest."""
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

from .profiling import columnas


def detectar(df, tipos, z=3.0, k_iqr=1.5, seed=42):
    """Atípicos por columna (Z-score e IQR) y por fila (Isolation Forest multivariado).

    Isolation Forest no recibe un porcentaje fijo de atípicos: una fila es atípica si su
    puntaje de anomalía queda por encima de Q3 + 1.5·IQR de todos los puntajes. Así el
    número de atípicos depende de los datos.
    """
    num = columnas(tipos, "numeric")
    por_columna = {}
    for c in num:
        s = df[c].dropna()
        if len(s) < 4 or s.std() == 0:
            continue
        zs = (s - s.mean()) / s.std()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        mask_iqr = (s < q1 - k_iqr * iqr) | (s > q3 + k_iqr * iqr)
        por_columna[c] = {
            "zscore": int((zs.abs() > z).sum()),
            "iqr": int(mask_iqr.sum()),
            "pct_iqr": float(mask_iqr.mean()),
            "limites_iqr": (float(q1 - k_iqr * iqr), float(q3 + k_iqr * iqr)),
        }

    multi = {"n": 0, "indices": []}
    if len(num) >= 2 and len(df) >= 20:
        X = df[num].apply(lambda s: s.fillna(s.median()))
        modelo = IsolationForest(random_state=seed).fit(X)
        puntaje = pd.Series(-modelo.score_samples(X), index=df.index)  # mayor = más anómalo
        q1, q3 = puntaje.quantile([0.25, 0.75])
        umbral = q3 + k_iqr * (q3 - q1)
        idx = puntaje[puntaje > umbral].sort_values(ascending=False).index
        multi = {"n": int(len(idx)), "indices": list(idx[:200]), "umbral": float(umbral)}
    return {"por_columna": por_columna, "isolation_forest": multi, "total_filas": len(df)}

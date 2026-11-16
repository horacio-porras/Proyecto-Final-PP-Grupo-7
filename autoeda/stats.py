"""Estadística descriptiva, correlaciones y ANOVA/eta²."""
import itertools
import numpy as np
import pandas as pd
from scipy import stats as sp

from .profiling import columnas


def descriptivas(df, tipos):
    num = columnas(tipos, "numeric")
    if not num:
        return pd.DataFrame()
    d = df[num].describe().T
    d["asimetria"] = df[num].skew()
    d["nulos"] = df[num].isna().sum()
    return d


def correlaciones(df, tipos, umbral=0.5):
    """Matrices Pearson/Spearman y lista de pares con |r| >= umbral."""
    num = columnas(tipos, "numeric")
    if len(num) < 2:
        return {"pearson": pd.DataFrame(), "spearman": pd.DataFrame(), "pares": []}
    pear = df[num].corr(method="pearson")
    spear = df[num].corr(method="spearman")
    pares = []
    for a, b in itertools.combinations(num, 2):
        r, rs = pear.loc[a, b], spear.loc[a, b]
        if pd.notna(r) and max(abs(r), abs(rs)) >= umbral:
            pares.append({"a": a, "b": b, "pearson": float(r), "spearman": float(rs)})
    pares.sort(key=lambda p: -max(abs(p["pearson"]), abs(p["spearman"])))
    return {"pearson": pear, "spearman": spear, "pares": pares}


def anova_eta(df, tipos, max_categorias=20):
    """Para cada par (categórica, numérica): ANOVA de una vía y eta² (varianza explicada)."""
    res = []
    for cat in columnas(tipos, "categorical", "boolean"):
        if not 2 <= df[cat].nunique() <= max_categorias:
            continue
        for num in columnas(tipos, "numeric"):
            sub = df[[cat, num]].dropna()
            grupos = [g[num].values for _, g in sub.groupby(cat) if len(g) >= 2]
            if len(grupos) < 2:
                continue
            f, p = sp.f_oneway(*grupos)
            if not np.isfinite(f):
                continue
            total = ((sub[num] - sub[num].mean()) ** 2).sum()
            entre = sum(len(g) * (g.mean() - sub[num].mean()) ** 2 for g in grupos)
            eta2 = float(entre / total) if total > 0 else 0.0
            res.append({"categoria": cat, "numerica": num, "F": float(f), "p": float(p), "eta2": eta2})
    res.sort(key=lambda r: -r["eta2"])
    return res


def asociaciones_categoricas(df, tipos, max_categorias=20):
    """Dependencia entre pares de variables categóricas/lógicas: chi-cuadrado y V de Cramér.

    V de Cramér va de 0 (independientes) a 1 (una determina a la otra).
    """
    cats = [c for c in columnas(tipos, "categorical", "boolean")
            if 2 <= df[c].nunique() <= max_categorias]
    res = []
    for a, b in itertools.combinations(cats, 2):
        tabla = pd.crosstab(df[a], df[b])
        if tabla.shape[0] < 2 or tabla.shape[1] < 2:
            continue
        chi2, p, _, _ = sp.chi2_contingency(tabla)
        n = tabla.values.sum()
        v = float(np.sqrt(chi2 / (n * (min(tabla.shape) - 1)))) if n else 0.0
        res.append({"a": a, "b": b, "chi2": float(chi2), "p": float(p), "cramer_v": v})
    res.sort(key=lambda r: -r["cramer_v"])
    return res


def tendencias(df, tipos, min_periodos=4):
    """Tendencia de cada variable numérica en el tiempo.

    Agrupa por mes (o por día si los datos abarcan menos de 60 días), calcula el promedio por
    periodo y mide la tendencia con la correlación de Spearman entre el orden del periodo y el promedio.
    """
    res = []
    for fecha in columnas(tipos, "datetime"):
        f = df[fecha].dropna()
        if f.empty:
            continue
        freq = "D" if (f.max() - f.min()).days < 60 else "M"
        periodo = df[fecha].dt.to_period(freq)
        for num in columnas(tipos, "numeric"):
            serie = df[num].groupby(periodo).mean().dropna()
            if len(serie) < min_periodos:
                continue
            rho, p = sp.spearmanr(np.arange(len(serie)), serie.values)
            if not np.isfinite(rho):
                continue
            cambio = (serie.iloc[-1] - serie.iloc[0]) / abs(serie.iloc[0]) if serie.iloc[0] else np.nan
            res.append({"fecha": fecha, "numerica": num, "rho": float(rho), "p": float(p),
                        "periodos": len(serie), "frecuencia": "día" if freq == "D" else "mes",
                        "cambio": float(cambio), "serie": serie})
    res.sort(key=lambda r: -abs(r["rho"]))
    return res

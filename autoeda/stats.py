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
    for cat in columnas(tipos, "categorical"):
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

"""Orquesta todo el análisis sobre un DataFrame."""
from . import clustering, insights, outliers, profiling, stats


def run_analysis(df_raw):
    df, tipos, notas = profiling.profile(df_raw)
    st = {
        "desc": stats.descriptivas(df, tipos),
        "corr": stats.correlaciones(df, tipos),
        "anova": stats.anova_eta(df, tipos),
        "asociaciones": stats.asociaciones_categoricas(df, tipos),
        "tendencias": stats.tendencias(df, tipos),
    }
    out = outliers.detectar(df, tipos)
    cl = clustering.agrupar(df, tipos)
    hallazgos = insights.generar(df, tipos, notas, st, out, cl)
    return {"df": df, "tipos": tipos, "notas": notas, "stats": st,
            "outliers": out, "clusters": cl, "insights": hallazgos}

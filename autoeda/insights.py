"""Convierte resultados numéricos en frases en español."""


def _fuerza(r):
    a = abs(r)
    return "muy fuerte" if a >= 0.8 else "fuerte" if a >= 0.6 else "moderada"


def generar(df, tipos, notas, st, out, cl):
    """Devuelve lista de (seccion, frase)."""
    h = []
    cont = {t: sum(1 for v in tipos.values() if v == t) for t in set(tipos.values())}
    detalle = ", ".join(f"{v} {k}" for k, v in sorted(cont.items()))
    h.append(("Resumen", f"El conjunto tiene {len(df):,} filas y {df.shape[1]} columnas ({detalle})."))
    for n in notas:
        h.append(("Calidad de datos", n))

    for p in st["corr"]["pares"][:5]:
        r_ref = p["pearson"] if abs(p["pearson"]) >= abs(p["spearman"]) else p["spearman"]
        signo = "positiva" if r_ref > 0 else "negativa"
        h.append(("Correlaciones",
                  f"'{p['a']}' y '{p['b']}' tienen una correlación {signo} {_fuerza(r_ref)} "
                  f"(Pearson r={p['pearson']:.2f}, Spearman ρ={p['spearman']:.2f})."))

    if st["corr"]["pares"]:
        h.append(("Correlaciones", "Nota: una correlación describe asociación, no causalidad."))

    for r in [r for r in st["anova"] if r["p"] < 0.05 and r["eta2"] >= 0.06][:5]:
        h.append(("Diferencias entre grupos",
                  f"'{r['categoria']}' explica el {r['eta2']:.0%} de la variación de '{r['numerica']}' "
                  f"(ANOVA F={r['F']:.1f}, p={'<0.001' if r['p'] < 0.001 else format(r['p'], '.3f')})."))

    for c, d in out["por_columna"].items():
        if d["iqr"] or d["zscore"]:
            h.append(("Valores atípicos",
                      f"'{c}' tiene {d['iqr']} atípicos por IQR y {d['zscore']} por Z-score (|z|>3)."))
    m = out["isolation_forest"]
    if m["n"]:
        h.append(("Valores atípicos",
                  f"Isolation Forest marca {m['n']} filas ({m['n'] / out['total_filas']:.1%}) como "
                  "atípicas al considerar todas las variables numéricas a la vez."))

    if cl:
        h.append(("Clustering",
                  f"Se detectaron {cl['k']} grupos con K-means (silhouette={cl['silhouette']:.2f}; "
                  "k elegido por mayor silhouette)."))
        for g in cl["perfil"]:
            rasgos = "; ".join(
                f"{'alto' if z > 0 else 'bajo'} en '{v}' (media {mu:.2f})" for v, z, mu in g["distintivas"])
            h.append(("Clustering", f"Grupo {g['cluster'] + 1} ({g['porcentaje']:.0%} de los datos): {rasgos}."))
        db = cl["dbscan"]
        h.append(("Clustering",
                  f"DBSCAN encontró {db['clusters']} grupos densos y {db['ruido']} puntos de ruido."))
    return h

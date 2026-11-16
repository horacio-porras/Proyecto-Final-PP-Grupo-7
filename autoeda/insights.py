"""Convierte resultados numéricos en frases en español, priorizadas por importancia.

Cada hallazgo es una tupla (seccion, frase, prioridad). La prioridad (0-100) crece con la
fuerza del efecto encontrado: una correlación r=0.9 pesa más que una r=0.5, y un grupo que
explica el 40% de la variación pesa más que uno que explica el 8%. Así la app puede mostrar
primero lo más relevante a un usuario sin conocimientos estadísticos.
"""
from .profiling import NOMBRES_TIPO


def _fuerza(r):
    a = abs(r)
    return "muy fuerte" if a >= 0.8 else "fuerte" if a >= 0.6 else "moderada"


def _p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def generar(df, tipos, notas, st, out, cl):
    """Devuelve la lista de hallazgos (seccion, frase, prioridad), de mayor a menor prioridad."""
    h = []
    cont = {t: sum(1 for v in tipos.values() if v == t) for t in set(tipos.values())}
    detalle = ", ".join(f"{v} {NOMBRES_TIPO.get(k, (k, k))[v != 1]}" for k, v in sorted(cont.items()))
    h.append(("Resumen", f"El conjunto tiene {len(df):,} filas y {df.shape[1]} columnas ({detalle}).", 100))
    for n in notas:
        h.append(("Calidad de datos", n, 35))

    # Correlaciones entre numéricas
    for p in st["corr"]["pares"][:5]:
        r_ref = p["pearson"] if abs(p["pearson"]) >= abs(p["spearman"]) else p["spearman"]
        signo = "positiva" if r_ref > 0 else "negativa"
        h.append(("Correlaciones",
                  f"'{p['a']}' y '{p['b']}' tienen una correlación {signo} {_fuerza(r_ref)} "
                  f"(Pearson r={p['pearson']:.2f}, Spearman ρ={p['spearman']:.2f}).",
                  50 + 45 * abs(r_ref)))
    if st["corr"]["pares"]:
        h.append(("Correlaciones", "Nota: una correlación describe asociación, no causalidad.", 0))

    # Categórica -> numérica (ANOVA)
    for r in [r for r in st["anova"] if r["p"] < 0.05 and r["eta2"] >= 0.06][:5]:
        h.append(("Diferencias entre grupos",
                  f"'{r['categoria']}' explica el {r['eta2']:.0%} de la variación de '{r['numerica']}' "
                  f"(ANOVA F={r['F']:.1f}, p={_p(r['p'])}).",
                  45 + 50 * min(r["eta2"] * 2, 1)))

    # Categórica <-> categórica (chi-cuadrado)
    for r in [r for r in st.get("asociaciones", []) if r["p"] < 0.05 and r["cramer_v"] >= 0.1][:5]:
        grado = "fuerte" if r["cramer_v"] >= 0.5 else "moderada" if r["cramer_v"] >= 0.3 else "débil"
        h.append(("Dependencia entre categorías",
                  f"'{r['a']}' y '{r['b']}' no son independientes: asociación {grado} "
                  f"(V de Cramér={r['cramer_v']:.2f}, χ²={r['chi2']:.1f}, p={_p(r['p'])}).",
                  40 + 55 * r["cramer_v"]))

    # Tendencias temporales
    for r in [r for r in st.get("tendencias", []) if r["p"] < 0.05 and abs(r["rho"]) >= 0.5][:4]:
        sentido = "aumenta" if r["rho"] > 0 else "disminuye"
        cambio = f", con un cambio de {r['cambio']:+.0%} entre el primer y el último {r['frecuencia']}" \
            if r["cambio"] == r["cambio"] else ""
        h.append(("Tendencias en el tiempo",
                  f"El promedio de '{r['numerica']}' {sentido} a lo largo de '{r['fecha']}' "
                  f"(Spearman ρ={r['rho']:.2f} en {r['periodos']} periodos{cambio}).",
                  45 + 45 * abs(r["rho"])))

    # Valores atípicos
    for c, d in out["por_columna"].items():
        if d["iqr"] or d["zscore"]:
            h.append(("Valores atípicos",
                      f"El {d['pct_iqr']:.1%} de los registros de '{c}' son atípicos según IQR "
                      f"({d['iqr']} {'valor' if d['iqr'] == 1 else 'valores'}); {d['zscore']} superan |z|>3.",
                      30 + min(d["pct_iqr"] * 300, 40)))
    m = out["isolation_forest"]
    if m["n"]:
        pct = m["n"] / out["total_filas"]
        h.append(("Valores atípicos",
                  f"Isolation Forest marca {m['n']} filas ({pct:.1%}) como atípicas al considerar "
                  "todas las variables numéricas a la vez.", 50 + min(pct * 300, 30)))

    # Clustering
    if cl:
        h.append(("Clustering",
                  f"Se detectaron {cl['k']} grupos con K-means (silhouette={cl['silhouette']:.2f}; "
                  "k elegido por mayor silhouette).", 60 + 30 * min(cl["silhouette"], 1)))
        for g in cl["perfil"]:
            rasgos = "; ".join(
                f"{'alto' if z > 0 else 'bajo'} en '{v}' (media {mu:.2f})" for v, z, mu in g["distintivas"])
            h.append(("Clustering", f"Grupo {g['cluster'] + 1} ({g['porcentaje']:.0%} de los datos): {rasgos}.",
                      55 + 30 * min(cl["silhouette"], 1)))
        db = cl["dbscan"]
        h.append(("Clustering",
                  f"DBSCAN encontró {db['clusters']} grupos densos y {db['ruido']} puntos de ruido.", 40))
    return sorted(h, key=lambda x: -x[2])


def clave(hallazgos, n=5):
    """Los n hallazgos más importantes, sin contar el resumen ni las notas."""
    return [x for x in hallazgos if x[0] != "Resumen" and x[2] > 0][:n]


def por_seccion(hallazgos):
    """Agrupa los hallazgos por sección; las secciones salen ordenadas por su hallazgo más importante."""
    secciones = {}
    for sec, frase, _ in sorted(hallazgos, key=lambda x: -x[2]):
        secciones.setdefault(sec, []).append(frase)
    # Las notas (prioridad 0) quedan al final de su sección por el orden anterior
    orden = ["Resumen"] + [s for s in secciones if s != "Resumen"]
    return {s: secciones[s] for s in orden if s in secciones}


def para_mostrar(hallazgos, n_clave=5):
    """Secciones listas para la app y el reporte: Resumen, Hallazgos clave y luego el resto."""
    secciones = por_seccion(hallazgos)
    top = clave(hallazgos, n_clave)
    if not top:
        return secciones
    resumen = secciones.pop("Resumen", [])
    return {"Resumen": resumen, "Hallazgos clave": [f for _, f, _ in top], **secciones}

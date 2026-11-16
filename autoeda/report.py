"""Exportación del análisis a un HTML autocontenido con la misma organización del dashboard.

El reporte replica las pestañas de la app:
  Hallazgos | Estadística | Visualizaciones | Valores atípicos | Segmentación
y Visualizaciones tiene las sub-pestañas Distribuciones, Relaciones, Segmentos y Tiempo.

Las pestañas funcionan con un pequeño script. Sin JavaScript, o al imprimir, todas las
secciones se muestran una debajo de otra, cada una con su título.
"""
import html
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go

from . import charts, insights
from .profiling import NOMBRES_TIPO, columnas

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
:root{--canvas:#EDF0F4;--card:#fff;--line:#D9DEE5;--line-soft:#ECEFF3;--ink:#2F3A45;--muted:#6E7A87;
      --nav:#26323F;--blue:#4E8CBA;--blue-dark:#31689B}
*{box-sizing:border-box}
body{font-family:'Open Sans','Segoe UI',Arial,sans-serif;background:var(--canvas);color:var(--ink);margin:0;line-height:1.5}
.wrap{max-width:1180px;margin:0 auto;padding:1rem 1.2rem 3rem}
.topbar{background:var(--nav);color:#fff;border-radius:4px;padding:.85rem 1.3rem;margin-bottom:1rem}
.topbar .brand{font-size:1.2rem;font-weight:700;margin-right:1rem}.topbar .file{font-weight:600}
.topbar p{margin:.2rem 0 0;color:#AEBBC8;font-size:.85rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.7rem;margin-bottom:1rem}
.kpi{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:.75rem 1rem}
.kpi .l{font-size:.8rem;color:var(--muted);font-weight:600}
.kpi .v{font-size:1.75rem;font-weight:600;line-height:1.2;margin-top:.2rem;font-variant-numeric:tabular-nums}
.kpi .s{font-size:.75rem;color:var(--muted)}

/* Pestañas */
.tabs{display:flex;flex-wrap:wrap;gap:4px;background:var(--card);border:1px solid var(--line);border-radius:4px;
      padding:0 .6rem;margin-bottom:1rem}
.tabs button{font:inherit;font-weight:600;font-size:.92rem;color:var(--muted);background:none;border:none;
             border-bottom:3px solid transparent;padding:.7rem .9rem .55rem;cursor:pointer}
.tabs button[aria-selected=true]{color:var(--blue-dark);border-bottom-color:var(--blue)}
.tabs button:focus-visible{outline:2px solid var(--blue);outline-offset:-2px}
.tabs.sub{background:none;border:none;border-bottom:1px solid var(--line);border-radius:0;padding:0}
.tabs.sub button{font-size:.86rem;padding:.5rem .8rem .4rem}
.js .panel{display:none}.js .panel.on{display:block}
.panel-title{font-size:1.15rem;margin:1.2rem 0 .6rem}
.js .panel-title{display:none}

/* Tarjetas */
.card{background:var(--card);border:1px solid var(--line);border-radius:4px;padding:.9rem 1.1rem 1rem;margin-bottom:1rem}
.ct{font-size:.98rem;font-weight:600;margin:0}
.cn{font-size:.8rem;color:var(--muted);margin:.1rem 0 .6rem}
.grid2{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 1rem}
.grid2.top{align-items:start}
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0 1rem}
@media (max-width:900px){.grid3{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media (max-width:640px){.grid2,.grid3{grid-template-columns:1fr}}

/* Hallazgos */
.top-row{display:grid;grid-template-columns:1fr 150px;gap:1.2rem;align-items:center;padding:.6rem 0;
         border-top:1px solid var(--line-soft)}
.top-row:first-of-type{border-top:none}
.top-row .txt{font-size:.92rem}.top-row .sec{display:block;font-size:.75rem;color:var(--muted)}
.bar{height:8px;background:var(--line-soft);border-radius:2px;overflow:hidden}
.bar span{display:block;height:100%;background:var(--c)}
.bar-l{font-size:.72rem;color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
@media (max-width:640px){.top-row{grid-template-columns:1fr;gap:.3rem}}
.sw{display:inline-block;width:10px;height:10px;border-radius:2px;background:var(--c);margin-right:.45rem}
.cnt{float:right;font-size:.78rem;color:var(--muted);font-weight:400}
ul.hl{list-style:none;padding:0;margin:.2rem 0 0}
ul.hl li{padding:.45rem 0;border-top:1px solid var(--line-soft);color:#45515D;font-size:.88rem}
ul.hl li:first-child{border-top:none}

/* Tablas */
.tbl{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:.82rem;font-variant-numeric:tabular-nums}
th{background:#F2F5F8;color:var(--ink);text-align:left;padding:.45rem .6rem;font-weight:600;border-bottom:1px solid var(--line)}
td{padding:.38rem .6rem;border-bottom:1px solid var(--line-soft)}
td.num,th.num{text-align:right}

/* Segmentación */
.grupos{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:.8rem}
.grupo{border:1px solid var(--line);border-top:4px solid var(--c);border-radius:4px;padding:.8rem 1rem}
.grupo .t{font-weight:600}.grupo .p{font-size:1.6rem;font-weight:600}.grupo .n{color:var(--muted);font-size:.8rem}
.grupo ul{padding-left:1rem;margin:.4rem 0 0;font-size:.85rem;color:#45515D}
.vacio{color:var(--muted);font-size:.9rem}

@media print{
  body{background:#fff}.tabs{display:none}.js .panel{display:block}
  .panel-title,.js .panel-title{display:block;font-size:1.15rem;margin:1.2rem 0 .6rem;break-after:avoid}
  .card{break-inside:avoid-page}
}
"""

JS = """
<script>
document.documentElement.classList.add('js');
document.addEventListener('click', function (e) {
  var b = e.target.closest('[data-tab]');
  if (!b) return;
  var grupo = b.parentElement.dataset.group;
  document.querySelectorAll('[data-group="' + grupo + '"] > [data-tab]').forEach(function (x) {
    x.setAttribute('aria-selected', x === b ? 'true' : 'false');
  });
  document.querySelectorAll('.panel[data-group="' + grupo + '"]').forEach(function (p) {
    p.classList.toggle('on', p.id === b.dataset.tab);
  });
  window.dispatchEvent(new Event('resize'));  // Plotly recalcula el ancho de los gráficos visibles
});
</script>
"""

# Explicación en lenguaje sencillo de cada tema de hallazgos
EXPLICACION = {
    "Correlaciones": "Qué tanto se mueven juntas dos variables, de -1 (opuestas) a 1 (iguales).",
    "Diferencias entre grupos": "Porcentaje de la variación de una variable numérica que explica una "
                                "categoría (eta² de ANOVA). p < 0.05 indica que no es azar.",
    "Dependencia entre categorías": "V de Cramér: 0 son independientes, 1 una variable determina a la otra.",
    "Tendencias en el tiempo": "Spearman entre el orden de los periodos y su promedio: cerca de 1 es una "
                               "subida sostenida y cerca de -1 una bajada.",
    "Valores atípicos": "Pueden ser errores de captura o casos especiales que conviene revisar.",
    "Clustering": "K-means agrupa registros parecidos; la silhouette (de -1 a 1) indica qué tan "
                  "separados quedan los grupos.",
    "Calidad de datos": "Conversiones y valores faltantes detectados durante la limpieza.",
}

esc = html.escape


# ---------- Piezas reutilizables ----------

def _es_num(v):
    return pd.api.types.is_number(v) and not pd.api.types.is_bool(v)  # incluye tipos de numpy


def _tabla(df, index=True):
    """DataFrame a tabla HTML. Las columnas numéricas van a la derecha, con separador de miles y
    la misma cantidad de decimales en toda la columna."""
    cols = list(df.columns)
    numerica = {c: df[c].map(_es_num).all() for c in cols}
    decimales = {c: 2 if numerica[c] and not all(float(v).is_integer() for v in df[c].dropna()) else 0
                 for c in cols}
    cab = ("<th></th>" if index else "") + "".join(
        f"<th class='num'>{esc(str(c))}</th>" if numerica[c] else f"<th>{esc(str(c))}</th>" for c in cols)
    filas = []
    for i, fila in df.iterrows():
        celdas = [f"<td><b>{esc(str(i))}</b></td>"] if index else []
        for c in cols:
            v = fila[c]
            if numerica[c]:
                txt = "—" if pd.isna(v) else f"{v:,.{decimales[c]}f}"
                celdas.append(f"<td class='num'>{txt}</td>")
            elif isinstance(v, pd.Timestamp):
                fmt = "%Y-%m-%d" if v == v.normalize() else "%Y-%m-%d %H:%M"
                celdas.append(f"<td>{v.strftime(fmt)}</td>")
            else:
                celdas.append(f"<td>{esc(str(v))}</td>")
        filas.append("<tr>" + "".join(celdas) + "</tr>")
    return f"<div class='tbl'><table><thead><tr>{cab}</tr></thead><tbody>{''.join(filas)}</tbody></table></div>"


def _tarjeta(titulo, cuerpo, nota=""):
    nota = f"<p class='cn'>{esc(nota)}</p>" if nota else "<div style='height:.5rem'></div>"
    return f"<div class='card'><p class='ct'>{esc(titulo)}</p>{nota}{cuerpo}</div>"


class _Graficos:
    """Convierte figuras en tarjetas; incluye plotly.js solo en la primera."""

    def __init__(self):
        self.primero = True

    def tarjeta(self, fig):
        fig = go.Figure(fig)  # copia: el mismo gráfico puede aparecer en dos pestañas
        titulo = fig.layout.title.text or ""
        fig.update_layout(title=None, height=380, margin=dict(t=36),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""))
        cuerpo = fig.to_html(full_html=False, include_plotlyjs="cdn" if self.primero else False,
                             config={"displaylogo": False, "responsive": True})
        self.primero = False
        return _tarjeta(titulo, cuerpo)

    def grid(self, figs, cols=2):
        if not figs:
            return ""
        return f"<div class='grid{cols}'>" + "".join(self.tarjeta(f) for f in figs) + "</div>"


def _tabs(grupo, nombres, activa=0, sub=False):
    botones = "".join(
        f"<button type='button' role='tab' data-tab='{grupo}-{i}' "
        f"aria-selected='{'true' if i == activa else 'false'}'>{esc(n)}</button>"
        for i, n in enumerate(nombres))
    return f"<div class='tabs{' sub' if sub else ''}' role='tablist' data-group='{grupo}'>{botones}</div>"


def _panel(grupo, i, titulo, cuerpo, activa=0):
    on = " on" if i == activa else ""
    return (f"<div class='panel{on}' id='{grupo}-{i}' data-group='{grupo}' role='tabpanel'>"
            f"<h2 class='panel-title'>{esc(titulo)}</h2>{cuerpo}</div>")


def _vacio(texto):
    return f"<div class='card'><p class='vacio'>{esc(texto)}</p></div>"


# ---------- Contenido de cada pestaña ----------

def _kpis(res):
    df, tipos = res["df"], res["tipos"]
    num = sum(t == "numeric" for t in tipos.values())
    m, cl = res["outliers"]["isolation_forest"], res["clusters"]
    items = [("Filas", f"{len(df):,}", ""),
             ("Columnas", df.shape[1], f"{df.shape[1] - num} no numéricas" if df.shape[1] - num else ""),
             ("Numéricas", num, ""),
             ("Faltantes", f"{df.isna().mean().mean():.1%}", "promedio"),
             ("Filas atípicas", m["n"], f"{m['n'] / max(len(df), 1):.1%} del total"),
             ("Grupos", cl["k"] if cl else "—", f"silhouette {cl['silhouette']:.2f}" if cl else "")]
    return "<div class='kpis'>" + "".join(
        f"<div class='kpi'><div class='l'>{l}</div><div class='v'>{v}</div><div class='s'>{s or '&nbsp;'}</div></div>"
        for l, v, s in items) + "</div>"


def _hallazgos(res):
    """Primero los 5 hallazgos clave; después todos, agrupados por tema (en el mismo orden que la app)."""
    secciones = insights.por_seccion(res["insights"])
    resumen = secciones.pop("Resumen", [""])[0]
    colores = insights.COLOR_SECCION
    top = insights.clave(res["insights"])
    out = []
    if top:
        filas = "".join(
            f"<div class='top-row' style='--c:{colores.get(s, '#4E8CBA')}'>"
            f"<div class='txt'>{esc(f)}<span class='sec'>{esc(s)}</span></div>"
            f"<div><div class='bar'><span style='width:{p:.0f}%'></span></div>"
            f"<div class='bar-l'>prioridad {p:.0f}</div></div></div>" for s, f, p in top)
        out.append(_tarjeta("Hallazgos clave", filas, resumen))
    def tarjeta_tema(sec, frases):
        lis = "".join(f"<li>{esc(f)}</li>" for f in frases)
        return (f"<div class='card' style='--c:{colores.get(sec, '#4E8CBA')}'>"
                f"<p class='ct'><span class='sw'></span>{esc(sec)}<span class='cnt'>{len(frases)}</span></p>"
                f"<p class='cn'>{esc(EXPLICACION.get(sec, ''))}</p><ul class='hl'>{lis}</ul></div>")

    # Dos columnas independientes y balanceadas: una tarjeta larga no deja huecos junto a una corta
    cols = insights.repartir_columnas(secciones)
    out.append("<div class='grid2 top'>" + "".join(
        "<div>" + "".join(tarjeta_tema(sec, fr) for sec, fr in grupo) + "</div>" for grupo in cols) + "</div>")
    return "".join(out)


def _estadistica(res):
    df, tipos, st = res["df"], res["tipos"], res["stats"]
    out = []
    out.append(_tarjeta("Variables detectadas", _tabla(pd.DataFrame({
        "Tipo": [NOMBRES_TIPO.get(tipos[c], (tipos[c],))[0] for c in df.columns],
        "Valores distintos": [df[c].nunique() for c in df.columns],
        "Faltantes (%)": [round(df[c].isna().mean() * 100, 2) for c in df.columns],
    }, index=df.columns)), "Tipo asignado automáticamente a cada columna después de la limpieza"))

    num = columnas(tipos, "numeric")
    if num:
        d = pd.DataFrame({
            "Media": df[num].mean(), "Mediana": df[num].median(), "Desv. estándar": df[num].std(),
            "Mínimo": df[num].min(), "Máximo": df[num].max(), "Asimetría": df[num].skew(),
            "Faltantes (%)": df[num].isna().mean() * 100}).round(2)
        out.append(_tarjeta("Estadística descriptiva", _tabla(d), "Variables numéricas"))

    cats = columnas(tipos, "categorical", "boolean")
    if cats:
        filas = {}
        for c in cats:
            vc = df[c].value_counts(normalize=True)
            filas[c] = {"Categorías": df[c].nunique(), "Más frecuente": str(vc.index[0]) if len(vc) else "—",
                        "Frecuencia (%)": round(vc.iloc[0] * 100, 2) if len(vc) else 0,
                        "Faltantes (%)": round(df[c].isna().mean() * 100, 2)}
        out.append(_tarjeta("Variables categóricas y lógicas", _tabla(pd.DataFrame(filas).T),
                            "Categoría más frecuente y su peso"))

    def p_txt(v):
        return "<0.001" if v < 0.001 else f"{v:.3f}"

    if st["anova"]:
        a = pd.DataFrame(st["anova"])
        t = pd.DataFrame({"Categoría": a["categoria"], "Variable numérica": a["numerica"], "F": a["F"].round(1),
                          "p": a["p"].map(p_txt), "Varianza explicada (%)": (a["eta2"] * 100).round(1)})
        out.append(_tarjeta("Efecto de variables categóricas", _tabla(t, index=False),
                            "ANOVA de una vía; varianza explicada = eta²"))
    lado = []
    if st.get("asociaciones"):
        a = pd.DataFrame(st["asociaciones"])
        t = pd.DataFrame({"Variable A": a["a"], "Variable B": a["b"], "χ²": a["chi2"].round(2),
                          "p": a["p"].map(p_txt), "V de Cramér": a["cramer_v"].round(2)})
        lado.append(_tarjeta("Dependencia entre categóricas", _tabla(t, index=False), "Chi-cuadrado y V de Cramér"))
    if st.get("tendencias"):
        a = pd.DataFrame(st["tendencias"])
        t = pd.DataFrame({"Fecha": a["fecha"], "Variable": a["numerica"], "Spearman ρ": a["rho"].round(2),
                          "p": a["p"].map(p_txt), "Periodos": a["periodos"],
                          "Cambio": a["cambio"].map(lambda v: f"{v:+.0%}" if v == v else "—")})
        lado.append(_tarjeta("Tendencias en el tiempo", _tabla(t, index=False),
                             "Spearman entre el orden del periodo y el promedio"))
    if lado:
        out.append("<div class='grid2'>" + "".join(lado) + "</div>")
    return "".join(out)


def _visualizaciones(res, g):
    figs = charts.todos(res)

    def de(*titulos):
        return [f for t, f in figs if t in titulos]

    paneles = [
        ("Distribuciones", g.grid(de("Histogramas", "Boxplots", "Categóricas"), 3)
         or _vacio("No hay variables para graficar.")),
        ("Relaciones", "".join(g.tarjeta(f) for f in de("Correlación"))
         + g.grid(de("Dispersión", "Por categoría", "Entre categorías"), 2)
         or _vacio("No se encontraron relaciones entre variables para graficar.")),
        ("Segmentos", g.grid(de("Clusters", "Silhouette"), 2)
         or _vacio("Se necesitan al menos 2 variables numéricas y 20 filas.")),
        ("Tiempo", g.grid(de("Tendencias"), 2)
         or _vacio("Se necesita una columna de fecha y al menos 4 periodos distintos.")),
    ]
    return (_tabs("viz", [n for n, _ in paneles], sub=True)
            + "".join(_panel("viz", i, n, c) for i, (n, c) in enumerate(paneles)))


def _atipicos(res):
    df, o = res["df"], res["outliers"]
    out = []
    if o["por_columna"]:
        t = pd.DataFrame({c: {"Atípicos IQR": d["iqr"], "IQR (%)": round(d["pct_iqr"] * 100, 2),
                              "Atípicos Z-score": d["zscore"],
                              "Z-score (%)": round(d["zscore"] / max(df[c].notna().sum(), 1) * 100, 2),
                              "Límite inferior": round(d["limites_iqr"][0], 2),
                              "Límite superior": round(d["limites_iqr"][1], 2)}
                          for c, d in o["por_columna"].items()}).T
        out.append(_tarjeta("Atípicos por variable", _tabla(t.sort_values("Atípicos IQR", ascending=False)),
                            "IQR: fuera de 1.5 veces el rango intercuartílico. Z-score: |z| mayor que 3"))
    m = o["isolation_forest"]
    nota = (f"{m['n']} filas atípicas ({m['n'] / max(o['total_filas'], 1):.1%}) al considerar todas las "
            "variables numéricas a la vez; se muestran las más anómalas primero")
    cuerpo = _tabla(df.loc[m["indices"]].head(50)) if m["indices"] else "<p class='vacio'>No se marcaron filas.</p>"
    out.append(_tarjeta("Isolation Forest", cuerpo, nota))
    return "".join(out)


def _segmentacion(res, g):
    cl = res["clusters"]
    if not cl:
        return _vacio("Se necesitan al menos 2 variables numéricas y 20 filas.")
    db = cl["dbscan"]
    grupos = "".join(
        f"<div class='grupo' style='--c:{charts.PALETA[gr['cluster'] % len(charts.PALETA)]}'>"
        f"<div class='t'>Grupo {gr['cluster'] + 1}</div><div class='p'>{gr['porcentaje']:.0%}</div>"
        f"<div class='n'>{gr['tamano']:,} registros</div><ul>"
        + "".join(f"<li>{'Alto' if z > 0 else 'Bajo'} en <b>{esc(v)}</b> (media {mu:,.2f})</li>"
                  for v, z, mu in gr["distintivas"]) + "</ul></div>"
        for gr in cl["perfil"])
    out = [_tarjeta(f"K-means encontró {cl['k']} grupos", f"<div class='grupos'>{grupos}</div>",
                    f"Silhouette {cl['silhouette']:.2f}. DBSCAN: {db['clusters']} "
                    f"{'grupo denso' if db['clusters'] == 1 else 'grupos densos'} y {db['ruido']} puntos de ruido.")]
    datos = res["df"][cl["variables"]].copy()
    datos["Grupo"] = [f"Grupo {int(e) + 1}" for e in cl["etiquetas"]]
    t = datos.groupby("Grupo").mean().round(2)
    t.insert(0, "Registros", datos["Grupo"].value_counts())
    t = t.loc[sorted(t.index, key=lambda x: int(x.split()[1]))]
    out.append(_tarjeta("Perfil promedio de cada grupo", _tabla(t),
                        "Registros y media de cada variable usada en el agrupamiento"))
    figs = [f for t_, f in charts.todos(res) if t_ in ("Clusters", "Silhouette")]
    out.append(g.grid(figs, 2))
    return "".join(out)


# ---------- Documento ----------

def construir_html(nombre, res):
    """Genera el reporte completo, organizado en las mismas pestañas que el dashboard."""
    df = res["df"]
    g = _Graficos()
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    pestanas = [("Hallazgos", _hallazgos(res)), ("Estadística", _estadistica(res)),
                ("Visualizaciones", _visualizaciones(res, g)), ("Valores atípicos", _atipicos(res)),
                ("Segmentación", _segmentacion(res, g))]
    return "\n".join([
        "<!doctype html><html lang='es'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        f"<title>Reporte AutoEDA: {esc(nombre)}</title><style>{CSS}</style>{JS}</head><body><div class='wrap'>",
        f"<div class='topbar'><span class='brand'>AutoEDA</span><span class='file'>{esc(nombre)}</span>"
        f"<p>Reporte de análisis automático generado el {fecha}, con {len(df):,} registros y "
        f"{df.shape[1]} variables.</p></div>",
        _kpis(res),
        _tabs("main", [n for n, _ in pestanas]),
        "".join(_panel("main", i, n, c) for i, (n, c) in enumerate(pestanas)),
        "</div></body></html>",
    ])

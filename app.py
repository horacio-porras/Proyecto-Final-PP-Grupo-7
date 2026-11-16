"""Interfaz Streamlit de AutoEDA. Ejecutar: streamlit run app.py

Estilo de tablero (tipo Domo): lienzo gris claro, barra superior oscura, fila de cifras
resumen y una cuadrícula de tarjetas blancas, una por gráfico o tabla.
"""
import html
import itertools

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from autoeda import charts, insights, loader, pipeline, report

st.set_page_config(page_title="AutoEDA · Análisis exploratorio automático", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
:root {
  --canvas:#EDF0F4; --card:#FFFFFF; --line:#D9DEE5; --line-soft:#ECEFF3;
  --ink:#2F3A45; --muted:#6E7A87; --nav:#26323F; --blue:#4E8CBA; --blue-dark:#31689B;
}
html, body, .stApp, .stMarkdown, button, input, textarea, select { font-family:'Open Sans','Segoe UI',sans-serif; }
.stApp { background:var(--canvas); color:var(--ink); }
[data-testid="stHeader"] { background:transparent; }
.block-container { padding-top:1rem; max-width:1320px; }
#MainMenu, footer { visibility:hidden; }

/* Barra superior */
.topbar { background:var(--nav); color:#fff; border-radius:4px; padding:.85rem 1.3rem;
          display:flex; align-items:baseline; gap:1.1rem; flex-wrap:wrap; margin-bottom:1rem; }
.topbar .brand { font-size:1.25rem; font-weight:700; letter-spacing:-.2px; }
.topbar .crumb { color:#AEBBC8; font-size:.95rem; }
.topbar .crumb b { color:#fff; font-weight:600; }

/* Tarjetas: cada contenedor con key "card..." es una tarjeta blanca */
[class*="st-key-card"] { background:var(--card); border:1px solid var(--line) !important;
                         border-radius:4px !important; padding:.9rem 1rem .6rem !important; }
.ct { font-size:.95rem; font-weight:600; color:var(--ink); line-height:1.3; }
.cn { font-size:.8rem; color:var(--muted); margin-top:.15rem; }

/* Cifras resumen */
.kpi { background:var(--card); border:1px solid var(--line); border-radius:4px; padding:.8rem 1rem .9rem; min-height:118px; }
.kpi .l { font-size:.8rem; color:var(--muted); font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.kpi .v { font-size:1.9rem; font-weight:600; color:var(--ink); line-height:1.15; margin-top:.25rem;
          font-variant-numeric:tabular-nums; }
.kpi .s { font-size:.75rem; color:var(--muted); margin-top:.1rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* Hallazgos clave: cada fila con barra de prioridad */
.top-row { display:grid; grid-template-columns:1fr 150px; gap:1.2rem; align-items:center;
           padding:.65rem 0; border-top:1px solid var(--line-soft); }
.top-row:first-of-type { border-top:none; }
.top-row .txt { color:var(--ink); line-height:1.5; font-size:.92rem; }
.top-row .sec { display:block; font-size:.75rem; color:var(--muted); margin-top:.1rem; }
.bar { height:8px; background:var(--line-soft); border-radius:2px; overflow:hidden; }
.bar span { display:block; height:100%; background:var(--c); }
.bar-l { font-size:.72rem; color:var(--muted); margin-top:.2rem; text-align:right; font-variant-numeric:tabular-nums; }
@media (max-width:700px) { .top-row { grid-template-columns:1fr; gap:.4rem; } }

/* Listas de hallazgos por tema */
.sw { display:inline-block; width:10px; height:10px; border-radius:2px; background:var(--c); margin-right:.45rem; }
.cnt { float:right; font-size:.78rem; color:var(--muted); font-weight:400; }
ul.hl { list-style:none; padding:0 !important; margin:.45rem 0 .2rem !important; }
ul.hl li { margin:0 !important; padding:.45rem 0; border-top:1px solid var(--line-soft); color:#45515D; font-size:.88rem; line-height:1.5; }
ul.hl li:first-child { border-top:none; }

/* Grupos de segmentación (el color coincide con el gráfico PCA) */
.grupo { background:var(--card); border:1px solid var(--line); border-top:4px solid var(--c);
         border-radius:4px; padding:.8rem 1rem; margin-bottom:.5rem; }
.grupo .t { font-weight:600; color:var(--ink); }
.grupo .p { font-size:1.7rem; font-weight:600; color:var(--ink); font-variant-numeric:tabular-nums; }
.grupo .n { color:var(--muted); font-size:.8rem; }
.grupo ul { padding-left:1rem; margin:.5rem 0 0; font-size:.86rem; color:#45515D; }

/* Pasos iniciales */
.step { background:var(--card); border:1px solid var(--line); border-radius:4px; padding:1rem 1.2rem; height:100%; }
.step b { color:var(--blue-dark); font-size:.85rem; }
.step div { margin-top:.3rem; color:#45515D; }

/* Pestañas principales: franja blanca como navegación de páginas */
.stTabs [data-baseweb="tab-list"] { gap:4px; background:var(--card); border:1px solid var(--line);
                                    border-radius:4px; padding:0 .6rem; }
.stTabs [data-baseweb="tab"] { height:44px; padding:0 14px; font-weight:600; color:var(--muted); background:transparent; }
.stTabs [aria-selected="true"] { color:var(--blue-dark); }
.stTabs [data-baseweb="tab-highlight"] { background-color:var(--blue); height:3px; }
.stTabs [data-baseweb="tab-border"] { display:none; }
/* Sub-pestañas dentro de una pestaña: más discretas */
.stTabs .stTabs [data-baseweb="tab-list"] { background:transparent; border:none; border-bottom:1px solid var(--line);
                                            border-radius:0; padding:0; }
.stTabs .stTabs [data-baseweb="tab"] { height:38px; font-size:.88rem; }

/* Barra lateral */
section[data-testid="stSidebar"] { background:var(--card); border-right:1px solid var(--line); }
[data-testid="stFileUploaderDropzone"] { background:#F6F8FA !important; border:1.5px dashed #B9C3CE !important;
                                         border-radius:4px !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color:var(--blue) !important; }
[data-testid="stFileUploaderDropzone"] button { border:1px solid var(--blue) !important; color:var(--blue-dark) !important;
                                                background:#fff !important; border-radius:4px !important; }
[data-testid="stDownloadButton"] button { background:var(--blue) !important; color:#fff !important; border:none !important;
        border-radius:4px !important; font-weight:600 !important; width:100%; }
[data-testid="stDownloadButton"] button:hover { background:var(--blue-dark) !important; }
[data-testid="stDownloadButton"] button * { color:#fff !important; }
:focus-visible { outline:2px solid var(--blue) !important; outline-offset:2px; }

[data-testid="stExpander"] { background:var(--card); border:1px solid var(--line) !important; border-radius:4px; }
[data-testid="stAlert"] { border-radius:4px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

COLOR_SECCION = {"Resumen": "#6E7A87", "Calidad de datos": "#FBAD56", "Correlaciones": "#4E8CBA",
                 "Diferencias entre grupos": "#8E6BB0", "Dependencia entre categorías": "#FB8D34",
                 "Tendencias en el tiempo": "#80C25D", "Valores atípicos": "#E4584C", "Clustering": "#73B0D7"}

_tarjetas = itertools.count()
esc = html.escape


def tarjeta(titulo=None, nota=None):
    """Contenedor con estilo de tarjeta blanca y, opcionalmente, título y nota."""
    c = st.container(border=True, key=f"card{next(_tarjetas)}")
    if titulo:
        c.markdown(f"<div class='ct'>{esc(titulo)}</div>" + (f"<div class='cn'>{esc(nota)}</div>" if nota else ""),
                   unsafe_allow_html=True)
    return c


_graficos = itertools.count()


def mostrar(fig):
    # Clave única: un mismo gráfico puede aparecer en dos pestañas (p. ej. el PCA)
    key = f"fig{next(_graficos)}"
    try:
        st.plotly_chart(fig, width="stretch", theme=None, key=key)
    except TypeError:  # versiones antiguas de Streamlit
        st.plotly_chart(fig, use_container_width=True, theme=None, key=key)


def tabla(df, **kw):
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kw)
    except Exception:
        st.dataframe(df, use_container_width=True, **kw)


def kpi(col, valor, etiqueta, sub=""):
    col.markdown(f"<div class='kpi'><div class='l'>{etiqueta}</div><div class='v'>{valor}</div>"
                 f"<div class='s'>{sub or '&nbsp;'}</div></div>", unsafe_allow_html=True)


def grafico(fig):
    """Muestra un gráfico dentro de una tarjeta; el título del gráfico pasa a ser el de la tarjeta."""
    fig = go.Figure(fig)  # copia: el mismo gráfico puede mostrarse en otra pestaña con su título
    titulo = fig.layout.title.text
    fig.update_layout(title=None, margin=dict(t=36 if fig.layout.showlegend is not False else 10),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, title_text=""))
    with tarjeta(titulo):
        mostrar(fig)


def grid(figs, cols=2):
    for i in range(0, len(figs), cols):
        fila = st.columns(cols)
        for c, f in zip(fila, figs[i:i + cols]):
            with c:
                grafico(f)


def topbar(detalle):
    st.markdown(f"<div class='topbar'><div class='brand'>AutoEDA</div><div class='crumb'>{detalle}</div></div>",
                unsafe_allow_html=True)


# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("### Datos")
    archivos = st.file_uploader("Archivos CSV o Excel", type=["csv", "xlsx", "xls"], accept_multiple_files=True)
    st.caption("Puedes subir varios archivos y alternar entre ellos.")

if not archivos:
    topbar("Análisis exploratorio automático")
    c = st.columns(3)
    pasos = [("Paso 1", "Sube uno o varios archivos CSV o Excel desde la barra lateral."),
             ("Paso 2", "AutoEDA detecta tipos, limpia y ejecuta estadística, atípicos y clustering."),
             ("Paso 3", "Revisa los hallazgos, explora los gráficos y descarga el reporte HTML.")]
    for col, (t, d) in zip(c, pasos):
        col.markdown(f"<div class='step'><b>{t}</b><div>{d}</div></div>", unsafe_allow_html=True)
    st.stop()

datos, errores = loader.load_many(archivos)
for n, e in errores.items():
    st.error(f"{n}: {e}")
if not datos:
    st.stop()

with st.sidebar:
    nombre = st.selectbox("Dataset activo", list(datos)) if len(datos) > 1 else next(iter(datos))


@st.cache_data(show_spinner="Analizando datos...")
def analizar(n, df):
    return pipeline.run_analysis(df)


res = analizar(nombre, datos[nombre])
df, tipos = res["df"], res["tipos"]

with st.sidebar:
    st.download_button("Descargar reporte HTML", report.construir_html(nombre, res),
                       file_name=f"autoeda_{nombre}.html", mime="text/html")

topbar(f"<b>{esc(nombre)}</b>")

# ---------- Cifras resumen ----------
conteo = {t: sum(v == t for v in tipos.values()) for t in set(tipos.values())}
otras = df.shape[1] - conteo.get("numeric", 0)
otras = f"{otras} no numéricas" if otras else ""
m = res["outliers"]["isolation_forest"]
cl = res["clusters"]
k = st.columns(6)
kpi(k[0], f"{len(df):,}", "Filas")
kpi(k[1], df.shape[1], "Columnas", otras)
kpi(k[2], conteo.get("numeric", 0), "Numéricas")
kpi(k[3], f"{df.isna().mean().mean():.1%}", "Faltantes", "promedio")
kpi(k[4], m["n"], "Filas atípicas", f"{m['n'] / max(len(df), 1):.1%} del total")
kpi(k[5], cl["k"] if cl else "—", "Grupos", f"silhouette {cl['silhouette']:.2f}" if cl else "")
st.write("")

t1, t2, t3, t4, t5 = st.tabs(["Hallazgos", "Estadística", "Visualizaciones", "Valores atípicos", "Segmentación"])

# ---------- Hallazgos ----------
with t1:
    secciones = insights.por_seccion(res["insights"])
    resumen = secciones.pop("Resumen", [""])[0]
    top = insights.clave(res["insights"])
    if top:
        filas = "".join(
            f"<div class='top-row' style='--c:{COLOR_SECCION.get(sec, '#4E8CBA')}'>"
            f"<div class='txt'>{esc(f, quote=False)}<span class='sec'>{esc(sec)}</span></div>"
            f"<div><div class='bar'><span style='width:{p:.0f}%'></span></div>"
            f"<div class='bar-l'>prioridad {p:.0f}</div></div></div>"
            for sec, f, p in top)
        with tarjeta("Hallazgos clave", resumen):
            st.markdown(filas, unsafe_allow_html=True)
    st.write("")
    items = list(secciones.items())
    for i in range(0, len(items), 2):
        fila = st.columns(2)
        for col, (sec, frases) in zip(fila, items[i:i + 2]):
            lis = "".join(f"<li>{esc(f, quote=False)}</li>" for f in frases)
            with col, tarjeta():
                st.markdown(f"<div class='ct' style='--c:{COLOR_SECCION.get(sec, '#4E8CBA')}'>"
                            f"<span class='sw'></span>{esc(sec)}<span class='cnt'>{len(frases)}</span></div>"
                            f"<ul class='hl'>{lis}</ul>", unsafe_allow_html=True)

# ---------- Estadística ----------
with t2:
    d = res["stats"]["desc"]
    if not d.empty:
        with tarjeta("Estadística descriptiva", "Variables numéricas: conteo, media, desviación, cuartiles, asimetría y nulos"):
            st.dataframe(d.round(2), width="stretch")
    if res["stats"]["anova"]:
        a = pd.DataFrame(res["stats"]["anova"])
        a["eta2"] = (a["eta2"] * 100).round(1).astype(str) + " %"
        a["p"] = a["p"].map(lambda v: "<0.001" if v < 0.001 else f"{v:.3f}")
        a["F"] = a["F"].round(1)
        with tarjeta("Efecto de variables categóricas", "ANOVA de una vía; varianza explicada = eta²"):
            tabla(a.rename(columns={"categoria": "Categoría", "numerica": "Variable numérica",
                                    "eta2": "Varianza explicada"}))
    c1, c2 = st.columns(2)
    if res["stats"]["asociaciones"]:
        a = pd.DataFrame(res["stats"]["asociaciones"])
        a["p"] = a["p"].map(lambda v: "<0.001" if v < 0.001 else f"{v:.3f}")
        a[["chi2", "cramer_v"]] = a[["chi2", "cramer_v"]].round(2)
        with c1, tarjeta("Dependencia entre categóricas", "Chi-cuadrado y V de Cramér"):
            tabla(a.rename(columns={"a": "Variable A", "b": "Variable B", "chi2": "χ²", "cramer_v": "V de Cramér"}))
    if res["stats"]["tendencias"]:
        a = pd.DataFrame(res["stats"]["tendencias"]).drop(columns="serie")
        a["p"] = a["p"].map(lambda v: "<0.001" if v < 0.001 else f"{v:.3f}")
        a["rho"] = a["rho"].round(2)
        a["cambio"] = a["cambio"].map(lambda v: f"{v:+.0%}" if v == v else "—")
        with c2, tarjeta("Tendencias en el tiempo", "Spearman entre el orden del periodo y el promedio"):
            tabla(a.rename(columns={"fecha": "Fecha", "numerica": "Variable", "rho": "Spearman ρ",
                                    "periodos": "Periodos", "frecuencia": "Periodo", "cambio": "Cambio"}))
    with st.expander("Vista previa de los datos limpios"):
        st.dataframe(df.head(100))

# ---------- Visualizaciones ----------
with t3:
    figs = charts.todos(res)

    def de(*titulos):
        return [f for t, f in figs if t in titulos]

    s1, s2, s3, s4 = st.tabs(["Distribuciones", "Relaciones", "Segmentos", "Tiempo"])
    with s1:
        grid(de("Histogramas", "Boxplots", "Categóricas"), 3)
    with s2:
        for f in de("Correlación"):
            grafico(f)
        grid(de("Dispersión", "Por categoría", "Entre categorías"), 2)
        if not de("Correlación", "Dispersión", "Por categoría", "Entre categorías"):
            st.info("No se encontraron relaciones entre variables para graficar.")
    with s3:
        g = de("Clusters", "Silhouette")
        if g:
            grid(g, 2)
        else:
            st.info("Se necesitan al menos 2 variables numéricas y 20 filas.")
    with s4:
        g = de("Tendencias")
        if g:
            grid(g, 2)
        else:
            st.info("Se necesita una columna de fecha y al menos 4 periodos distintos.")

# ---------- Valores atípicos ----------
with t4:
    o = res["outliers"]
    filas = [{"Variable": c, "Atípicos (IQR)": d["iqr"], "% (IQR)": f"{d['pct_iqr']:.1%}",
              "Atípicos (Z-score)": d["zscore"],
              "Límite inferior": round(d["limites_iqr"][0], 2), "Límite superior": round(d["limites_iqr"][1], 2)}
             for c, d in o["por_columna"].items()]
    if filas:
        with tarjeta("Atípicos por variable", "IQR: fuera de 1.5 veces el rango intercuartílico. Z-score: |z| mayor que 3"):
            tabla(pd.DataFrame(filas))
    with tarjeta("Isolation Forest", f"{m['n']} filas atípicas ({m['n'] / max(o['total_filas'], 1):.1%}) "
                                     "al considerar todas las variables numéricas a la vez"):
        if m["indices"]:
            tabla(df.loc[m["indices"]].head(50), height=320)
        else:
            st.caption("No se marcaron filas.")

# ---------- Segmentación ----------
with t5:
    if not cl:
        st.info("Se necesitan al menos 2 variables numéricas y 20 filas.")
    else:
        db = cl["dbscan"]
        with tarjeta(f"K-means encontró {cl['k']} grupos",
                     f"Silhouette {cl['silhouette']:.2f}. DBSCAN: {db['clusters']} "
                     f"{'grupo denso' if db['clusters'] == 1 else 'grupos densos'} y {db['ruido']} puntos de ruido."):
            cols = st.columns(min(len(cl["perfil"]), 4))
            for i, g in enumerate(cl["perfil"]):
                color = charts.PALETA[g["cluster"] % len(charts.PALETA)]
                rasgos = "".join(
                    f"<li>{'Alto' if z > 0 else 'Bajo'} en <b>{esc(v)}</b> (media {mu:,.2f})</li>"
                    for v, z, mu in g["distintivas"])
                cols[i % len(cols)].markdown(
                    f"<div class='grupo' style='--c:{color}'><div class='t'>Grupo {g['cluster'] + 1}</div>"
                    f"<div class='p'>{g['porcentaje']:.0%}</div><div class='n'>{g['tamano']:,} registros</div>"
                    f"<ul>{rasgos}</ul></div>", unsafe_allow_html=True)
        st.write("")
        grid(de("Clusters", "Silhouette"), 2)

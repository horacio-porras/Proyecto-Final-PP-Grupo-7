"""Interfaz Streamlit de AutoEDA. Ejecutar: streamlit run app.py"""
import html

import pandas as pd
import streamlit as st

from autoeda import charts, loader, pipeline, report

st.set_page_config(page_title="AutoEDA · Análisis exploratorio automático", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root { --bg:#0B1220; --s1:#121A2B; --s2:#172238; --bd:#243049; --tx:#E6EDF7; --mu:#94A3B8; --ac:#2DD4BF; }
html, body, [class*="css"], .stMarkdown { font-family: 'Inter','Segoe UI',sans-serif; }
.stApp { background: var(--bg); color: var(--tx); }
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.2rem; max-width: 1250px; }
#MainMenu, footer { visibility: hidden; }

/* Encabezado */
.hero { background: linear-gradient(135deg,#0F2A4A 0%,#0F3D5E 55%,#0F766E 100%);
        border:1px solid #1F3B5C; padding: 2rem 2.3rem; border-radius: 16px; margin-bottom: 1.3rem; }
.hero h1 { color:#fff; margin:0; font-size:2.1rem; letter-spacing:-.5px; font-weight:700; }
.hero p { color:#B6C6DA; margin:.45rem 0 0; font-size:1.02rem; }

/* Tarjetas */
.kpi { background:var(--s1); border:1px solid var(--bd); border-radius:12px; padding:.95rem 1.2rem; }
.kpi .v { font-size:1.65rem; font-weight:700; color:#F1F5F9; line-height:1.2; }
.kpi .l { font-size:.72rem; text-transform:uppercase; letter-spacing:.09em; color:var(--mu); font-weight:600; }
.card { background:var(--s1); border:1px solid var(--bd); border-left:4px solid var(--c,#2DD4BF);
        border-radius:12px; padding:1rem 1.4rem .6rem; margin:.9rem 0; }
.card h4 { margin:.1rem 0 .6rem; color:#F1F5F9; font-size:1.02rem; font-weight:600; }
.card ul { padding-left:1.1rem; margin:0 0 .5rem; }
.card li { margin:.4rem 0; line-height:1.55; color:#CBD5E1; }
.grupo { background:var(--s1); border:1px solid var(--bd); border-top:4px solid var(--c);
         border-radius:12px; padding:1rem 1.2rem; height:100%; }
.grupo .t { font-weight:700; color:#F1F5F9; font-size:1.05rem; }
.grupo .p { font-size:1.6rem; font-weight:700; color:var(--c); }
.grupo ul { padding-left:1rem; margin:.4rem 0 0; font-size:.9rem; color:#CBD5E1; }
.step { background:var(--s1); border:1px solid var(--bd); border-radius:12px; padding:1.1rem 1.3rem; height:100%; }
.step b { color:var(--ac); font-size:.8rem; letter-spacing:.1em; }
.step div { margin-top:.3rem; color:#CBD5E1; }

/* Pestañas */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--bd); }
.stTabs [data-baseweb="tab"] { height: 44px; padding: 0 18px; font-weight: 600; color: var(--mu); background: transparent; }
.stTabs [aria-selected="true"] { color: var(--ac); }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--ac); }
.stTabs [data-baseweb="tab-border"] { background-color: var(--bd); }

/* Barra lateral */
section[data-testid="stSidebar"] { background:#0E1627; border-right:1px solid var(--bd); }
section[data-testid="stSidebar"] * { color: var(--tx); }
section[data-testid="stSidebar"] small, section[data-testid="stSidebar"] label p { color: var(--mu) !important; }

/* Cuadro de carga de archivos */
[data-testid="stFileUploaderDropzone"] { background: var(--s2) !important; border: 1.5px dashed #3B5078 !important;
        border-radius: 12px !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--ac) !important; }
[data-testid="stFileUploaderDropzone"] * { color: var(--tx) !important; }
[data-testid="stFileUploaderDropzone"] small { color: var(--mu) !important; }
[data-testid="stFileUploaderDropzone"] svg { fill: var(--ac) !important; color: var(--ac) !important; }
[data-testid="stFileUploaderDropzone"] button { background: transparent !important; border: 1px solid var(--ac) !important;
        color: var(--ac) !important; border-radius: 8px !important; }
[data-testid="stFileUploaderDropzone"] button:hover { background: rgba(45,212,191,.14) !important; }

/* Archivo ya cargado */
[data-testid="stFileUploaderFile"] { background: var(--s2) !important; border: 1px solid var(--bd) !important;
        border-radius: 10px !important; padding: .35rem .7rem !important; margin-top: .4rem; }
[data-testid="stFileUploaderFile"] * { color: var(--tx) !important; }
[data-testid="stFileUploaderFile"] small { color: var(--mu) !important; }
[data-testid="stFileUploaderDeleteBtn"] button { background: transparent !important; border: none !important; }

/* Botón de descarga y botones */
[data-testid="stDownloadButton"] button, .stButton button { background: linear-gradient(135deg,#0F766E,#14B8A6) !important;
        color: #fff !important; border: none !important; border-radius: 10px !important; font-weight: 600 !important;
        padding: .6rem 1rem !important; width: 100%; box-shadow: 0 2px 8px rgba(20,184,166,.25); }
[data-testid="stDownloadButton"] button:hover, .stButton button:hover { filter: brightness(1.12); }
[data-testid="stDownloadButton"] button *, .stButton button * { color: #fff !important; }

/* Selectores */
[data-baseweb="select"] > div { background: var(--s2) !important; border-color: var(--bd) !important; color: var(--tx) !important; }
[data-baseweb="select"] * { color: var(--tx) !important; }
[data-baseweb="popover"] [data-baseweb="menu"], [data-baseweb="popover"] ul { background: var(--s2) !important; }
[data-baseweb="popover"] li:hover { background: #1F2E4D !important; }

/* Expanders, tablas, alertas */
[data-testid="stExpander"] { background: var(--s1); border: 1px solid var(--bd) !important; border-radius: 12px; }
[data-testid="stExpander"] summary, [data-testid="stExpander"] summary * { color: var(--tx) !important; }
[data-testid="stDataFrame"] { border: 1px solid var(--bd); border-radius: 10px; overflow: hidden; }
[data-testid="stAlert"] { background: var(--s1) !important; border: 1px solid var(--bd); border-radius: 10px; }
[data-testid="stAlert"] * { color: var(--tx) !important; }
hr { border-color: var(--bd); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

COLOR_SECCION = {"Resumen": "#94A3B8", "Calidad de datos": "#FBBF24", "Correlaciones": "#60A5FA",
                 "Diferencias entre grupos": "#A78BFA", "Valores atípicos": "#F472B6", "Clustering": "#2DD4BF"}


def mostrar(fig):
    try:
        st.plotly_chart(fig, width="stretch", theme=None)
    except Exception:  # versiones antiguas de Streamlit
        st.plotly_chart(fig, use_container_width=True, theme=None)


def tabla(df):
    try:
        st.dataframe(df, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(df, use_container_width=True)


def kpi(col, valor, etiqueta):
    col.markdown(f"<div class='kpi'><div class='v'>{valor}</div><div class='l'>{etiqueta}</div></div>",
                 unsafe_allow_html=True)


def grid(figs, cols=2):
    for i in range(0, len(figs), cols):
        fila = st.columns(cols)
        for c, f in zip(fila, figs[i:i + cols]):
            with c:
                mostrar(f)


# ---------- Encabezado ----------
st.markdown("<div class='hero'><h1>AutoEDA</h1><p>Análisis exploratorio automatizado con hallazgos "
            "redactados en lenguaje natural. Sube tus datos y obtén resultados sin configurar nada.</p></div>",
            unsafe_allow_html=True)

# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("### Datos")
    archivos = st.file_uploader("Archivos CSV o Excel", type=["csv", "xlsx", "xls"], accept_multiple_files=True)
    st.caption("Puedes subir varios archivos y alternar entre ellos.")

if not archivos:
    c = st.columns(3)
    pasos = [("PASO 1", "Sube uno o varios archivos CSV o Excel desde la barra lateral."),
             ("PASO 2", "AutoEDA detecta tipos, limpia y ejecuta estadística, outliers y clustering."),
             ("PASO 3", "Revisa los hallazgos, explora los gráficos y descarga el reporte HTML.")]
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

# ---------- KPIs ----------
k = st.columns(5)
kpi(k[0], f"{len(df):,}", "Filas")
kpi(k[1], df.shape[1], "Columnas")
kpi(k[2], sum(t == "numeric" for t in tipos.values()), "Numéricas")
kpi(k[3], f"{df.isna().mean().mean():.1%}", "Valores faltantes")
kpi(k[4], res["clusters"]["k"] if res["clusters"] else "—", "Grupos detectados")
st.write("")

t1, t2, t3, t4, t5 = st.tabs(["Hallazgos", "Estadística", "Visualizaciones", "Valores atípicos", "Segmentación"])

# ---------- Hallazgos ----------
with t1:
    secciones = {}
    for sec, frase in res["insights"]:
        secciones.setdefault(sec, []).append(frase)
    for sec, frases in secciones.items():
        items = "".join(f"<li>{html.escape(f, quote=False)}</li>" for f in frases)
        st.markdown(f"<div class='card' style='--c:{COLOR_SECCION.get(sec, '#0F766E')}'>"
                    f"<h4>{html.escape(sec)}</h4><ul>{items}</ul></div>", unsafe_allow_html=True)

# ---------- Estadística ----------
with t2:
    st.markdown("#### Estadística descriptiva")
    d = res["stats"]["desc"]
    if not d.empty:
        st.dataframe(d.round(2))
    if res["stats"]["anova"]:
        st.markdown("#### Efecto de variables categóricas (ANOVA y eta²)")
        a = pd.DataFrame(res["stats"]["anova"])
        a["eta2"] = (a["eta2"] * 100).round(1).astype(str) + " %"
        a["p"] = a["p"].map(lambda v: "<0.001" if v < 0.001 else f"{v:.3f}")
        a["F"] = a["F"].round(1)
        tabla(a.rename(columns={"categoria": "Categoría", "numerica": "Variable numérica",
                                "eta2": "Varianza explicada"}))
    with st.expander("Vista previa de los datos limpios"):
        st.dataframe(df.head(100))

# ---------- Visualizaciones ----------
with t3:
    figs = charts.todos(res)

    def de(*titulos):
        return [(t, f) for t, f in figs if t in titulos]

    s1, s2, s3 = st.tabs(["Distribuciones", "Relaciones", "Segmentos"])
    with s1:
        for t in ("Histogramas", "Boxplots", "Categóricas"):
            g = [f for tt, f in figs if tt == t]
            if g:
                st.markdown(f"##### {t}")
                grid(g, 2)
    with s2:
        for t in ("Correlación", "Dispersión"):
            g = [f for tt, f in figs if tt == t]
            if g:
                st.markdown(f"##### {t}")
                grid(g, 1 if t == "Correlación" else 2)
        if not de("Correlación", "Dispersión"):
            st.info("Se necesitan al menos 2 variables numéricas.")
    with s3:
        g = [f for tt, f in figs if tt in ("Clusters", "Silhouette")]
        if g:
            grid(g, 2)
        else:
            st.info("Se necesitan al menos 2 variables numéricas y 20 filas.")

# ---------- Outliers ----------
with t4:
    o = res["outliers"]
    filas = [{"Variable": c, "Atípicos (IQR)": d["iqr"], "Atípicos (Z-score)": d["zscore"],
              "Límite inferior": round(d["limites_iqr"][0], 2), "Límite superior": round(d["limites_iqr"][1], 2)}
             for c, d in o["por_columna"].items()]
    if filas:
        tabla(pd.DataFrame(filas))
    m = o["isolation_forest"]
    st.markdown(f"**Isolation Forest (multivariado):** {m['n']} filas atípicas "
                f"({m['n'] / max(o['total_filas'], 1):.1%}).")
    if m["indices"]:
        with st.expander("Ver las filas marcadas"):
            st.dataframe(df.loc[m["indices"]].head(50))

# ---------- Segmentación ----------
with t5:
    cl = res["clusters"]
    if not cl:
        st.info("Se necesitan al menos 2 variables numéricas y 20 filas.")
    else:
        st.markdown(f"**K-means:** {cl['k']} grupos (silhouette {cl['silhouette']:.2f}). "
                    f"**DBSCAN:** {cl['dbscan']['clusters']} grupos densos y {cl['dbscan']['ruido']} puntos de ruido.")
        cols = st.columns(min(len(cl["perfil"]), 4))
        for i, g in enumerate(cl["perfil"]):
            color = charts.PALETA[i % len(charts.PALETA)]
            rasgos = "".join(
                f"<li>{'Alto' if z > 0 else 'Bajo'} en <b>{html.escape(v)}</b> (media {mu:,.2f})</li>"
                for v, z, mu in g["distintivas"])
            cols[i % len(cols)].markdown(
                f"<div class='grupo' style='--c:{color}'><div class='t'>Grupo {g['cluster'] + 1}</div>"
                f"<div class='p'>{g['porcentaje']:.0%}</div><div style='color:#94A3B8;font-size:.8rem'>"
                f"{g['tamano']} registros</div><ul>{rasgos}</ul></div>", unsafe_allow_html=True)

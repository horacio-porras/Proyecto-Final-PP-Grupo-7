"""Gráficos interactivos con Plotly (tema visual propio, sobrio)."""
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from .profiling import columnas

PALETA = ["#2DD4BF", "#60A5FA", "#FBBF24", "#F472B6", "#A78BFA", "#34D399", "#FB923C", "#94A3B8"]
_EJE = dict(gridcolor="#243049", zerolinecolor="#2F3E5C", linecolor="#3B5078", tickfont=dict(color="#B6C6DA"))

pio.templates["autoeda"] = go.layout.Template(layout=dict(
    colorway=PALETA,
    font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=13, color="#E6EDF7"),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    title=dict(font=dict(size=15, color="#F1F5F9"), x=0.02),
    xaxis=_EJE, yaxis=_EJE,
    margin=dict(l=45, r=20, t=55, b=45),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
))
pio.templates.default = "autoeda"
ESCALA_DIV = ["#F472B6", "#121A2B", "#2DD4BF"]


def histogramas(df, tipos, max_cols=8):
    figs = []
    for c in columnas(tipos, "numeric")[:max_cols]:
        f = px.histogram(df, x=c, nbins=30, title=f"Distribución de {c}")
        f.update_layout(bargap=0.05, yaxis_title="Frecuencia")
        figs.append(f)
    return figs


def boxplots(df, tipos, max_cols=8):
    return [px.box(df, y=c, points="outliers", title=f"Boxplot de {c}") for c in columnas(tipos, "numeric")[:max_cols]]


def categoricas(df, tipos, max_cols=4):
    figs = []
    for c in columnas(tipos, "categorical")[:max_cols]:
        s = df[c].value_counts().head(15)
        f = px.bar(x=s.index.astype(str), y=s.values, title=f"Frecuencia de {c}",
                   labels={"x": c, "y": "Conteo"})
        figs.append(f)
    return figs


def heatmap(res):
    m = res["stats"]["corr"]["pearson"]
    if m.empty:
        return None
    return px.imshow(m, text_auto=".2f", zmin=-1, zmax=1, color_continuous_scale=ESCALA_DIV,
                     title="Matriz de correlación (Pearson)", aspect="auto")


def dispersiones(res, max_n=4):
    df, cl = res["df"], res["clusters"]
    color = None
    if cl is not None and len(cl["etiquetas"]) == len(df):
        color = [f"Grupo {int(e) + 1}" for e in cl["etiquetas"]]
    figs = []
    for p in res["stats"]["corr"]["pares"][:max_n]:
        f = px.scatter(df, x=p["a"], y=p["b"], color=color, opacity=0.75,
                       title=f"{p['a']} vs {p['b']} (r={p['pearson']:.2f})",
                       labels={"color": "Grupo"})
        figs.append(f)
    return figs


def pca_clusters(res):
    cl = res["clusters"]
    if not cl:
        return None
    return px.scatter(x=cl["pca"][:, 0], y=cl["pca"][:, 1], opacity=0.8,
                      color=[f"Grupo {int(e) + 1}" for e in cl["etiquetas"]],
                      labels={"x": "Componente 1", "y": "Componente 2", "color": "Grupo"},
                      title="Segmentos de clientes (proyección PCA)")


def silhouette_k(res):
    cl = res["clusters"]
    if not cl:
        return None
    ks = list(cl["scores_k"])
    f = px.line(x=ks, y=[cl["scores_k"][k] for k in ks], markers=True,
                labels={"x": "Número de grupos (k)", "y": "Silhouette"},
                title="Selección de k por silhouette")
    f.add_vline(x=cl["k"], line_dash="dash", line_color="#FBBF24")
    return f


def todos(res):
    """Lista de (titulo, figura) para la app y el reporte."""
    df, tipos = res["df"], res["tipos"]
    figs = [("Histogramas", f) for f in histogramas(df, tipos)]
    figs += [("Boxplots", f) for f in boxplots(df, tipos)]
    figs += [("Categóricas", f) for f in categoricas(df, tipos)]
    for titulo, f in (("Correlación", heatmap(res)),):
        if f is not None:
            figs.append((titulo, f))
    figs += [("Dispersión", f) for f in dispersiones(res)]
    for titulo, f in (("Clusters", pca_clusters(res)), ("Silhouette", silhouette_k(res))):
        if f is not None:
            figs.append((titulo, f))
    return figs

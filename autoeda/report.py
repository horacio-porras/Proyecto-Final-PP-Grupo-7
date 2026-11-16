"""Exportación del análisis a un HTML autocontenido con estilo formal."""
import html
from . import charts, insights

CSS = """
body{font-family:Inter,'Segoe UI',Arial,sans-serif;background:#0B1220;color:#E6EDF7;margin:0}
.wrap{max-width:1000px;margin:0 auto;padding:0 1.2rem 3rem}
.hero{background:linear-gradient(135deg,#0F2A4A,#0F3D5E 55%,#0F766E);color:#fff;padding:2.2rem 0;margin-bottom:1.5rem}
.hero h1{margin:0;font-size:1.9rem}.hero p{margin:.4rem 0 0;color:#B6C6DA}
h2{color:#F1F5F9}
.kpis{display:flex;gap:.8rem;flex-wrap:wrap;margin-bottom:1.2rem}
.kpi{background:#121A2B;border:1px solid #243049;border-radius:12px;padding:.9rem 1.2rem;min-width:130px}
.kpi b{display:block;font-size:1.5rem;color:#F1F5F9}.kpi span{font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#94A3B8}
.card{background:#121A2B;border:1px solid #243049;border-left:4px solid #2DD4BF;border-radius:12px;padding:1rem 1.4rem;margin:1rem 0}
.card h2{margin:.2rem 0 .6rem;font-size:1.05rem;color:#F1F5F9}.card li{margin:.35rem 0;line-height:1.5;color:#CBD5E1}
.fig{background:#121A2B;border:1px solid #243049;border-radius:12px;padding:.5rem;margin:1rem 0}
"""


def kpis(res):
    df = res["df"]
    items = [("Filas", f"{len(df):,}"), ("Columnas", df.shape[1]),
             ("Numéricas", sum(t == "numeric" for t in res["tipos"].values())),
             ("Valores faltantes", f"{df.isna().mean().mean():.1%}")]
    if res["clusters"]:
        items.append(("Grupos detectados", res["clusters"]["k"]))
    return items


def construir_html(nombre, res):
    p = [f"<html><head><meta charset='utf-8'><title>AutoEDA - {html.escape(nombre)}</title>"
         f"<style>{CSS}</style></head><body>",
         f"<div class='hero'><div class='wrap'><h1>Reporte de análisis exploratorio</h1>"
         f"<p>{html.escape(nombre)} · generado con AutoEDA</p></div></div><div class='wrap'>",
         "<div class='kpis'>" + "".join(f"<div class='kpi'><b>{v}</b><span>{l}</span></div>" for l, v in kpis(res)) + "</div>"]
    secciones = insights.para_mostrar(res["insights"])
    for sec, frases in secciones.items():
        p.append(f"<div class='card'><h2>{html.escape(sec)}</h2><ul>"
                 + "".join(f"<li>{html.escape(f)}</li>" for f in frases) + "</ul></div>")
    p.append("<h2>Visualizaciones</h2>")
    primero = True
    for _, fig in charts.todos(res):
        p.append("<div class='fig'>" + fig.to_html(full_html=False, include_plotlyjs="cdn" if primero else False) + "</div>")
        primero = False
    p.append("</div></body></html>")
    return "\n".join(p)

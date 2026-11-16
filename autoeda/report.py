"""Exportación del análisis a un HTML autocontenido con estilo formal."""
import html
from . import charts, insights

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;600;700&display=swap');
body{font-family:'Open Sans','Segoe UI',Arial,sans-serif;background:#EDF0F4;color:#2F3A45;margin:0}
.wrap{max-width:1100px;margin:0 auto;padding:0 1.2rem 3rem}
.hero{background:#26323F;color:#fff;padding:1.1rem 0;margin-bottom:1.2rem}
.hero .wrap{padding-bottom:0}.hero h1{margin:0;font-size:1.35rem;font-weight:700}.hero p{margin:.25rem 0 0;color:#AEBBC8;font-size:.95rem}
h2{color:#2F3A45;font-size:1.05rem;margin:1.6rem 0 .6rem}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.7rem;margin-bottom:1rem}
.kpi{background:#fff;border:1px solid #D9DEE5;border-radius:4px;padding:.8rem 1rem}
.kpi span{display:block;font-size:.8rem;color:#6E7A87;font-weight:600}.kpi b{display:block;font-size:1.7rem;font-weight:600;margin-top:.2rem}
.card{background:#fff;border:1px solid #D9DEE5;border-radius:4px;padding:.9rem 1.2rem;margin:.8rem 0}
.card h2{margin:0 0 .4rem;font-size:.95rem}.card ul{list-style:none;padding:0;margin:0}
.card li{padding:.45rem 0;border-top:1px solid #ECEFF3;line-height:1.5;color:#45515D;font-size:.9rem}.card li:first-child{border-top:none}
.fig{background:#fff;border:1px solid #D9DEE5;border-radius:4px;padding:.5rem;margin:.8rem 0}
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
         f"<p>Generado con AutoEDA a partir de {html.escape(nombre)}</p></div></div><div class='wrap'>",
         "<div class='kpis'>" + "".join(f"<div class='kpi'><span>{l}</span><b>{v}</b></div>" for l, v in kpis(res)) + "</div>"]
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

# AutoEDA — Grupo 7

App web (Python + Streamlit) que recibe uno o varios CSV/Excel y genera un análisis exploratorio
automático con hallazgos en lenguaje natural.

## Instalación
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
## Estructura
Ver `autoeda/`: loader → profiling → (stats | outliers | clustering) → insights → app/report.
`pipeline.py` orquesta todo. `data/make_sample.py` genera un dataset de ejemplo.

# AutoEDA — Grupo 7

App web (Python + Streamlit) que recibe uno o varios CSV/Excel y genera un análisis exploratorio
automático con hallazgos en lenguaje natural.

## Qué analiza
- **Tipos de variable:** numérica, categórica, lógica (sí/no, verdadero/falso, 0/1), temporal, texto e ID.
- **Estadística:** descriptivas, correlaciones Pearson/Spearman, ANOVA/eta² (categórica → numérica),
  chi-cuadrado y V de Cramér (categórica ↔ categórica) y tendencias en el tiempo (Spearman por periodo).
- **IA:** atípicos con Z-score, IQR e Isolation Forest (umbral por IQR del puntaje, sin % fijo);
  clustering con K-means (k por silhouette) y DBSCAN, proyectado con PCA.
- **Hallazgos:** frases en español con una prioridad 0–100 según la fuerza del efecto;
  la app muestra primero los "Hallazgos clave".

## Instalación
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
## Estructura
Ver `autoeda/`: loader → profiling → (stats | outliers | clustering) → insights → app/report.
`pipeline.py` orquesta todo. `data/make_sample.py` genera un dataset de ejemplo.

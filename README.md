# AutoEDA — Análisis exploratorio automático con IA

Proyecto final de **Paradigmas de Programación** · Grupo 7

AutoEDA es una app web (Python + Streamlit) que recibe uno o varios archivos **CSV o Excel** y, sin
ningún paso manual, genera un análisis exploratorio completo: estadísticas, correlaciones, valores
atípicos, agrupamientos, gráficos interactivos y **hallazgos redactados en lenguaje natural**, como:

> *"'region' explica el 70% de la variación de 'costo_colones' (ANOVA F=461.2, p<0.001)."*
> *"Se detectaron 3 grupos con K-means (silhouette=0.65)."*

---

## Instalación y ejecución

Requisitos: **Python 3.10 o superior**. Los comandos se ejecutan desde la carpeta del proyecto. La primera vez se crea un entorno virtual (`.venv`) y se
instalan las dependencias; después solo hace falta activarlo y ejecutar la app.

<details>
<summary><b>macOS / Linux</b> (Terminal: bash o zsh)</summary>

**Primera vez:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Cada vez que quieras usar la app:**
```bash
source .venv/bin/activate
streamlit run app.py
```
</details>

<details>
<summary><b>Windows — PowerShell</b></summary>

**Primera vez:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Cada vez que quieras usar la app:**
```powershell
.venv\Scripts\Activate.ps1
streamlit run app.py
```

> Si aparece *"la ejecución de scripts está deshabilitada en este sistema"*, puedes saltarte la
> activación y usar directamente el Python del entorno:
> ```powershell
> .venv\Scripts\python -m streamlit run app.py
> ```
> O permitir scripts solo para tu usuario (una sola vez):
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`
</details>

<details>
<summary><b>Windows — Git Bash</b></summary>

**Primera vez:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

**Cada vez que quieras usar la app:**
```bash
source .venv/Scripts/activate
streamlit run app.py
```
</details>

<details>
<summary><b>Windows — Símbolo del sistema (CMD)</b></summary>

**Primera vez:**
```bat
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
```

**Cada vez que quieras usar la app:**
```bat
.venv\Scripts\activate.bat
streamlit run app.py
```
</details>

La app se abre sola en el navegador en **http://localhost:8501**. Para detenerla, presiona
`Ctrl + C` en la terminal.

<details>
<summary><b>Problemas comunes</b></summary>

| Problema | Solución |
|---|---|
| `python` no se reconoce (Windows) | Instala Python desde python.org y marca *"Add Python to PATH"*, o usa `py` en lugar de `python`. |
| `python3` no existe (macOS) | Instala Python con `brew install python` o desde python.org. |
| `streamlit` no se reconoce | El entorno virtual no está activado; actívalo o usa `python -m streamlit run app.py`. |
| *Port 8501 is already in use* | Ya hay otra instancia abierta. Ciérrala o usa `streamlit run app.py --server.port 8502`. |
</details>

---

## Cómo usar la app

1. En la **barra lateral**, sube uno o varios archivos CSV/Excel (puedes usar los de [`data/`](data/)).
2. El análisis corre solo. Si subiste varios archivos, elige cuál ver en **Dataset activo**.
3. Revisa los resultados en las pestañas y, si quieres, **descarga el reporte HTML**.

### Qué significa cada sección

#### Barra lateral
| Elemento | Para qué sirve |
|---|---|
| **Archivos CSV o Excel** | Carga uno o varios archivos (`.csv`, `.xlsx`, `.xls`, hasta 200 MB). El separador (`,` `;` tab) y la codificación se detectan solos. |
| **Dataset activo** | Aparece si subiste más de un archivo; cambia cuál se está analizando. |
| **Descargar reporte HTML** | Descarga un archivo con todos los hallazgos y gráficos interactivos. Se abre en cualquier navegador y se puede imprimir a PDF. |

#### Indicadores (tarjetas superiores)
**Filas** y **Columnas** después de la limpieza, cuántas variables son **Numéricas**, el porcentaje
promedio de **Valores faltantes** y cuántos **Grupos detectados** encontró K-means.

#### Pestañas
| Pestaña | Qué muestra | Cómo leerla |
|---|---|---|
| **Hallazgos** | El resumen en lenguaje natural. Arriba, los **Hallazgos clave**: los 5 resultados más importantes. Debajo, todo agrupado por tema. | Es lo primero que hay que leer. Cada hallazgo tiene una prioridad según qué tan fuerte es el efecto, así que lo más relevante aparece primero. |
| **Estadística** | Tabla de descriptivas (media, desviación, mínimo, cuartiles, máximo, asimetría, nulos), efecto de las categóricas (ANOVA), dependencia entre categóricas (chi-cuadrado) y tendencias en el tiempo. Al final, una vista previa de los datos limpios. | Para ver los números exactos que respaldan cada hallazgo. |
| **Visualizaciones** | Gráficos interactivos en 4 sub-pestañas (ver abajo). Se puede hacer zoom, pasar el mouse para ver valores y descargar cada gráfico como imagen. | Para explicar visualmente los hallazgos. |
| **Valores atípicos** | Por variable: cuántos valores son atípicos según IQR y Z-score, su porcentaje y los límites. Además, las filas que Isolation Forest marca como anómalas. | Valores atípicos pueden ser errores de captura o casos especiales que vale la pena revisar. |
| **Segmentación** | Los grupos encontrados por K-means, con su tamaño y las variables que más los distinguen (*"alto en ingreso, bajo en edad"*), más el resultado de DBSCAN. | Sirve para describir perfiles, por ejemplo tipos de clientes. |

**Sub-pestañas de Visualizaciones**
| Sub-pestaña | Gráficos |
|---|---|
| **Distribuciones** | Histogramas y boxplots de cada variable numérica; barras de frecuencia de las categóricas y lógicas. |
| **Relaciones** | Mapa de calor de correlaciones, diagramas de dispersión de los pares más relacionados (coloreados por grupo), boxplots de una numérica según una categórica, y tablas cruzadas entre categóricas. |
| **Segmentos** | Los grupos de K-means proyectados en 2D con PCA, y la curva de silhouette usada para elegir el número de grupos. |
| **Tiempo** | Promedio por mes (o por día) de cada variable numérica, cuando el archivo tiene una columna de fecha. |

### Glosario rápido
| Término | Significado en pocas palabras |
|---|---|
| **Correlación (Pearson r / Spearman ρ)** | Qué tanto suben o bajan juntas dos variables, de −1 a 1. Pearson mide relación lineal; Spearman, relación de orden (más robusta a atípicos). Correlación no implica causalidad. |
| **ANOVA y eta² (η²)** | Si una variable categórica (p. ej. región) marca diferencias en una numérica (p. ej. costo). η² es el **% de la variación explicada** por esa categoría. |
| **Chi-cuadrado y V de Cramér** | Si dos variables categóricas dependen una de la otra. V va de 0 (independientes) a 1 (una determina a la otra). |
| **p-valor** | Probabilidad de ver ese resultado por azar. Se reporta como significativo si p < 0.05. |
| **IQR** | Atípico si está muy por fuera del rango donde está el 50% central de los datos (1.5 × rango intercuartílico). |
| **Z-score** | Atípico si está a más de 3 desviaciones estándar del promedio. |
| **Isolation Forest** | Modelo de IA que detecta filas raras considerando todas las variables a la vez. |
| **K-means** | Algoritmo de IA que agrupa registros parecidos. El número de grupos (k) se elige solo. |
| **Silhouette** | Calidad de los grupos, de −1 a 1. Mayor a 0.5 indica grupos bien separados. |
| **DBSCAN** | Otro algoritmo de agrupamiento que busca zonas densas y marca como "ruido" los puntos aislados. |
| **PCA** | Resume muchas variables en 2 ejes para poder graficar los grupos. |

---

## Qué analiza (detalle técnico)
- **Tipos de variable:** numérica, categórica, lógica (sí/no, verdadero/falso, 0/1), temporal, texto e ID.
  Se convierten automáticamente textos con números o fechas.
- **Limpieza básica:** elimina filas/columnas vacías y duplicados, y reporta valores faltantes.
- **Estadística:** descriptivas, correlaciones Pearson/Spearman, ANOVA/eta² (categórica → numérica),
  chi-cuadrado y V de Cramér (categórica ↔ categórica) y tendencias en el tiempo (Spearman por periodo).
- **IA:** atípicos con Z-score, IQR e Isolation Forest (umbral por IQR del puntaje, sin % fijo);
  clustering con K-means (k por silhouette) y DBSCAN, proyectado con PCA.
- **Hallazgos:** frases en español con una prioridad 0–100 según la fuerza del efecto.

## Datasets de ejemplo
Están en [`data/`](data/) y se regeneran con `python data/make_sample.py`. Son sintéticos, con
patrones conocidos para comprobar que el sistema los encuentra.

| Archivo | Filas | Qué debería encontrar AutoEDA |
|---|---|---|
| `clientes_centro_comercial.csv` | 500 | 3 segmentos de clientes según edad, ingreso y gasto. |
| `ventas_tienda.csv` | 800 | La sucursal y la categoría explican las ventas; descuentos con faltantes. |
| `consumo_electrico.csv` | 400 | Más área y personas → más consumo → más costo; algunos hogares atípicos. |
| `envios_logistica.csv` | 600 | La región explica el costo, el costo sube mes a mes, el envío exprés llega más a tiempo. |

## Estructura del código

```
app.py                  Interfaz Streamlit
autoeda/
├── loader.py           Lee CSV/Excel (detecta separador y codificación)
├── profiling.py        Limpieza básica y detección de tipos
├── pipeline.py         Orquesta todo el análisis
├── stats.py            Descriptivas, correlaciones, ANOVA, chi-cuadrado, tendencias
├── charts.py           Gráficos Plotly
├── outliers.py         Z-score, IQR, Isolation Forest
├── clustering.py       K-means, DBSCAN, PCA
├── insights.py         Hallazgos en lenguaje natural y su prioridad
└── report.py           Reporte HTML
data/                   Datasets de ejemplo y su generador
```

Flujo: `loader → profiling → (stats | outliers | clustering) → insights → app / report`.

## Tecnologías
Python · Streamlit · Pandas · Scikit-learn · SciPy · Plotly · openpyxl

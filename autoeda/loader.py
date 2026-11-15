"""Carga de archivos CSV/Excel a DataFrames."""
from pathlib import Path
import pandas as pd

EXTENSIONES = (".csv", ".xlsx", ".xls")


def load_file(file, name=None) -> pd.DataFrame:
    """Lee un CSV o Excel (ruta o archivo subido en Streamlit)."""
    name = name or getattr(file, "name", str(file))
    ext = Path(name).suffix.lower()
    if ext == ".csv":
        ultimo_error = None
        for enc in ("utf-8", "latin-1"):
            try:
                if hasattr(file, "seek"):
                    file.seek(0)
                # sep=None: pandas detecta si el separador es coma, punto y coma o tab
                return pd.read_csv(file, sep=None, engine="python", encoding=enc)
            except UnicodeDecodeError as e:
                ultimo_error = e
        raise ValueError(f"No se pudo leer '{name}': {ultimo_error}")
    if ext in (".xlsx", ".xls"):
        if hasattr(file, "seek"):
            file.seek(0)
        return pd.read_excel(file)
    raise ValueError(f"Formato no soportado: '{ext}'. Use CSV o Excel.")


def load_many(files) -> dict:
    """Carga varios archivos. Devuelve {nombre: DataFrame}; los que fallan se reportan aparte."""
    datos, errores = {}, {}
    for f in files:
        nombre = getattr(f, "name", str(f))
        try:
            datos[nombre] = load_file(f, nombre)
        except Exception as e:  # noqa: BLE001
            errores[nombre] = str(e)
    return datos, errores

"""Detección de tipos de columna y limpieza básica."""
import warnings
import pandas as pd


def _intentar_numerico(s: pd.Series):
    conv = pd.to_numeric(s, errors="coerce")
    base = s.notna().sum()
    if base and conv.notna().sum() / base >= 0.9:
        return conv
    return None


def _intentar_fecha(s: pd.Series):
    muestra = s.dropna().astype(str)
    if muestra.empty or not muestra.str.contains(r"\d").all():
        return None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        try:
            conv = pd.to_datetime(s, errors="coerce", format="mixed")
        except (TypeError, ValueError):
            return None
    if conv.notna().sum() / max(s.notna().sum(), 1) >= 0.9:
        return conv
    return None


def profile(df: pd.DataFrame):
    """Limpia el DataFrame y clasifica columnas.

    Tipos: numeric, categorical, datetime, text, id.
    Devuelve (df_limpio, tipos, notas).
    """
    notas = []
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    antes = df.shape
    df = df.dropna(how="all").dropna(axis=1, how="all")
    dup = int(df.duplicated().sum())
    if dup:
        df = df.drop_duplicates()
        notas.append(f"Se eliminaron {dup} filas duplicadas.")
    if df.shape != antes and not dup:
        notas.append("Se eliminaron filas/columnas completamente vacías.")

    for c in df.columns:
        if df[c].dtype == object or str(df[c].dtype) in ("string", "str"):
            df[c] = df[c].astype("object").map(lambda v: v.strip() if isinstance(v, str) else v)
            df[c] = df[c].replace("", pd.NA)
            num = _intentar_numerico(df[c])
            if num is not None:
                df[c] = num
                notas.append(f"'{c}' se convirtió a numérica.")
                continue
            fecha = _intentar_fecha(df[c])
            if fecha is not None:
                df[c] = fecha
                notas.append(f"'{c}' se convirtió a fecha.")

    n = len(df)
    tipos = {}
    for c in df.columns:
        s = df[c]
        nun = s.nunique(dropna=True)
        if pd.api.types.is_datetime64_any_dtype(s):
            tipos[c] = "datetime"
        elif pd.api.types.is_bool_dtype(s):
            tipos[c] = "categorical"
        elif pd.api.types.is_numeric_dtype(s):
            es_entero = (s.dropna() % 1 == 0).all()
            if es_entero and nun == n and n > 20:
                tipos[c] = "id"
            elif nun <= 2:
                tipos[c] = "categorical"
            else:
                tipos[c] = "numeric"
        else:
            tipos[c] = "categorical" if nun <= max(20, 0.05 * n) else "text"

    nulos = df.isna().sum()
    for c, k in nulos[nulos > 0].items():
        notas.append(f"'{c}' tiene {k} valores faltantes ({k / max(n, 1):.1%}).")
    return df, tipos, notas


def columnas(tipos: dict, tipo: str):
    return [c for c, t in tipos.items() if t == tipo]

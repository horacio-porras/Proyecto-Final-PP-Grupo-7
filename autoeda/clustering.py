"""Clustering: K-means (k por silhouette) y DBSCAN, con proyección PCA."""
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from .profiling import columnas


def agrupar(df, tipos, k_max=8, seed=42):
    num = columnas(tipos, "numeric")
    if len(num) < 2 or len(df) < 20:
        return None
    X = df[num].apply(lambda s: s.fillna(s.median()))
    # Winsorizar (1%-99%) para que los outliers no formen clusters propios
    Xw = X.clip(X.quantile(0.01), X.quantile(0.99), axis=1)
    Xs = StandardScaler().fit_transform(Xw)
    n = len(Xs)
    rng = np.random.RandomState(seed)
    idx_s = rng.choice(n, size=min(n, 3000), replace=False)  # muestra para silhouette

    scores = {}
    for k in range(2, min(k_max, n - 1) + 1):
        lab = KMeans(n_clusters=k, n_init=10, random_state=seed).fit_predict(Xs)
        scores[k] = float(silhouette_score(Xs[idx_s], lab[idx_s]))
    k_best = max(scores, key=scores.get)
    km = KMeans(n_clusters=k_best, n_init=10, random_state=seed).fit(Xs)
    etiquetas = km.labels_

    # DBSCAN: eps tomado del percentil 90 de la distancia al vecino más cercano
    from sklearn.neighbors import NearestNeighbors
    minpts = max(5, 2 * len(num))
    d, _ = NearestNeighbors(n_neighbors=min(minpts, n - 1)).fit(Xs).kneighbors(Xs)
    eps = float(np.percentile(d[:, -1], 90))
    db = DBSCAN(eps=eps, min_samples=minpts).fit_predict(Xs)
    n_db = len(set(db)) - (1 if -1 in db else 0)

    coords = PCA(n_components=2, random_state=seed).fit_transform(Xs)

    perfil = []
    media, desv = X.mean(), X.std().replace(0, 1)
    for c in range(k_best):
        m = etiquetas == c
        z = ((X[m].mean() - media) / desv).sort_values(key=abs, ascending=False)
        perfil.append({
            "cluster": c, "tamano": int(m.sum()), "porcentaje": float(m.mean()),
            "distintivas": [(v, float(z[v]), float(X[m][v].mean())) for v in z.index[:4]],
        })
    return {
        "k": k_best, "silhouette": scores[k_best], "scores_k": scores,
        "etiquetas": etiquetas, "pca": coords, "perfil": perfil, "variables": num,
        "dbscan": {"clusters": n_db, "ruido": int((db == -1).sum()), "eps": eps, "etiquetas": db},
    }

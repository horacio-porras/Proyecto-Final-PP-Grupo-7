"""Genera 3 datasets sintéticos fáciles de interpretar. Ejecutar: python data/make_sample.py"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

# 1) Clientes de un centro comercial: 3 segmentos claros
n = 500
seg = rng.choice(3, n, p=[0.4, 0.35, 0.25])
edad = np.array([rng.normal(m, 4) for m in np.array([23, 38, 56])[seg]]).clip(18, 75).round()
ingreso = np.array([rng.normal(m, 250) for m in np.array([900, 2800, 1800])[seg]]).clip(400).round()
gasto = np.array([rng.normal(m, 8) for m in np.array([78, 55, 25])[seg]]).clip(1, 100).round()
visitas = np.array([rng.normal(m, 1.5) for m in np.array([9, 5, 2])[seg]]).clip(0).round()
pd.DataFrame({
    "id_cliente": range(1, n + 1),
    "genero": rng.choice(["Femenino", "Masculino"], n),
    "edad": edad, "ingreso_mensual_usd": ingreso,
    "puntaje_gasto": gasto, "visitas_al_mes": visitas,
}).to_csv("data/clientes_centro_comercial.csv", index=False)

# 2) Ventas de una cadena: la sucursal explica gran parte de las ventas
n = 800
suc = rng.choice(["San José", "Heredia", "Cartago", "Alajuela"], n)
base = {"San José": 1500, "Heredia": 900, "Cartago": 600, "Alajuela": 1000}
categoria = rng.choice(["Ropa", "Calzado", "Accesorios"], n)
unidades = rng.integers(1, 15, n)
precio = np.array([{"Ropa": 25, "Calzado": 55, "Accesorios": 12}[c] for c in categoria]) * rng.uniform(0.9, 1.1, n)
desc = rng.choice([0, 5, 10, 20], n)
factor = np.array([{'San José': 1.6, 'Heredia': 1.0, 'Cartago': 0.6, 'Alajuela': 1.1}[s] for s in suc])
ventas = unidades * precio * (1 - desc / 100) * factor
df = pd.DataFrame({
    "fecha": pd.date_range("2026-01-01", periods=n, freq="8h").strftime("%Y-%m-%d"),
    "sucursal": suc, "categoria": categoria, "unidades": unidades,
    "precio_unitario": precio.round(2), "descuento_pct": desc, "ventas_total": ventas.round(2),
})
df.loc[rng.choice(n, 15), "descuento_pct"] = np.nan  # faltantes
df.to_csv("data/ventas_tienda.csv", index=False)

# 3) Consumo eléctrico de hogares: más área y personas => más kWh => más costo
n = 400
area = rng.normal(110, 35, n).clip(40, 300).round()
personas = rng.integers(1, 7, n)
temp = rng.normal(24, 3, n).round(1)
kwh = (area * 1.6 + personas * 45 + (temp - 20) * 6 + rng.normal(0, 25, n)).clip(50).round()
costo = (kwh * 105 + rng.normal(0, 2500, n)).round()
df = pd.DataFrame({
    "tipo_vivienda": rng.choice(["Casa", "Apartamento"], n, p=[0.7, 0.3]),
    "area_m2": area, "personas": personas, "temperatura_prom_c": temp,
    "consumo_kwh": kwh, "costo_colones": costo,
})
df.loc[rng.choice(n, 5), "consumo_kwh"] *= 3  # unos pocos hogares atípicos
df.to_csv("data/consumo_electrico.csv", index=False)
print("Listo: 3 archivos en data/")

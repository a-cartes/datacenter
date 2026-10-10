"""Muestras analíticas unidad-año, emparejamiento y pesos (réplica adaptada, RM 2017-2025).

Reglas fijadas antes de estimar efectos (REGISTRO_DECISIONES.md, D-14 a D-19):
- Resultado: promedio anual de D = P - P_Quillota220 (USD/MWh) de las barras con cobertura
  >= 0,9 en los 9 años (panel de barras balanceado; evita cambios de composición), promedio
  simple entre barras de la unidad, como el promedio de nodos por sector del artículo.
  Variante 'no balanceada': todas las barras con cobertura >= 0,9 en el año.
- Tratamiento: G = año de la primera operación documentada en la unidad (G_doc); sensibilidad
  con G_min. Unidades 'previa' e 'incierta' se excluyen; controles = sin instalaciones.
- Emparejamiento: probit de tratamiento sobre covariables Censo 2017 (log población, log
  viviendas, proporción inmigrante, proporción pueblos originarios, proporción de viviendas con
  materialidad aceptable); 10 vecinos con reemplazo; tratados fuera del soporte común
  (puntaje > máximo de controles) se excluyen; cada copia de control pesa 1/m.
Salidas: datos/analitico/muestra_<alt>.csv (una fila por copia y año), con columnas de peso,
y resultados/emparejamiento_<alt>.json (balance antes y después).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datos" / "analitico"
COV = ["l_pob", "l_viv", "sh_inmigrantes", "sh_pueblos_originarios", "sh_viv_mat_aceptable"]
K = 10


def bars():
    D = pd.read_csv(ROOT / "datos" / "geo" / "barras_diccionario.csv")
    S = pd.read_csv(ROOT / "datos" / "geo" / "subestaciones_unidades.csv")
    D = D.merge(S[["id_subestacion", "comuna_ine", "distrito_ine", "distrito_nombre"]], on="id_subestacion", how="left")
    return D[D.comuna_ine.notna()]


def outcomes(map_bar_unit, balanced=True):
    A = pd.read_parquet(ROOT / "datos" / "panel" / "barra_anio.parquet")
    A = A[A.barra.isin(map_bar_unit) & (A.cobertura_D >= 0.9)]
    if balanced:
        n = A.groupby("barra").anio.nunique()
        A = A[A.barra.isin(n[n == 9].index)]
    A["unidad"] = A.barra.map(map_bar_unit)
    A.loc[A.horas_LC < 0.9 * A.horas_D, ["L", "C"]] = np.nan  # L y C solo con factores en >= 90% de las horas
    g = A.groupby(["unidad", "anio"]).agg(D=("D", "mean"), L=("L", "mean"), C=("C", "mean"), P=("P", "mean"),
                                          E=("E", "mean"), n_barras=("barra", "nunique"),
                                          n_barras_LC=("L", "count")).reset_index()
    g.loc[g.n_barras_LC < g.n_barras, ["L", "C"]] = np.nan
    return g


def covariates(level):
    if level == "comuna":
        c = pd.read_csv(ROOT / "datos" / "covariables" / "covariables_comuna.csv")
        c["unidad"] = c.NOM_COMUNA
    else:
        c = pd.read_csv(ROOT / "datos" / "covariables" / "covariables_distrito.csv")
        c["unidad"] = c.distrito_nombre
    c["l_pob"] = np.log(c.pob)
    c["l_viv"] = np.log(c.viv)
    return c


def smd(t, c, w=None):
    out = {}
    for v in COV:
        a, b = t[v], c[v]
        wb = np.ones(len(b)) if w is None else w
        mb = np.average(b, weights=wb)
        sd = np.sqrt((a.var() + b.var()) / 2)
        out[v] = {"tratados": float(a.mean()), "controles": float(mb), "dif_estandarizada": float((a.mean() - mb) / sd) if sd > 0 else None}
    return out


def match(U, alt):
    X = sm.add_constant(U[COV].astype(float))
    y = U.tratada.astype(int)
    info = {"n_tratadas": int(y.sum()), "n_controles": int((1 - y).sum())}
    try:
        m = sm.Probit(y, X).fit(disp=0, maxiter=200)
        U["ps"] = m.predict(X)
        info["probit"] = {"convergio": bool(m.mle_retvals.get("converged")), "coef": m.params.round(4).to_dict(),
                          "pseudo_r2": float(m.prsquared)}
        if (U.ps[y == 1] > 0.999).any() or not m.mle_retvals.get("converged"):
            raise RuntimeError("separación o no convergencia")
    except Exception as e:  # separación con muy pocos tratados: probit penalizado (la API discreta aplica L1)
        m = sm.Probit(y, X).fit_regularized(alpha=1.0, disp=0, maxiter=500)
        U["ps"] = m.predict(X)
        info["probit"] = {"nota": f"probit estándar falló ({e}); se usa probit con penalización L1 (alpha=1)",
                          "coef": pd.Series(m.params, index=X.columns).round(4).to_dict()}
    T, C = U[U.tratada], U[~U.tratada]
    sup = T.ps <= C.ps.max()
    info["tratadas_fuera_de_soporte"] = T.loc[~sup, "unidad"].tolist()
    T = T[sup]
    pairs = []
    info["desempate"] = "distancia absoluta en puntaje; distancia redondeada a 12 decimales, luego identificador alfanumérico ascendente"
    info["empates_en_corte"] = []
    for _, t in T.iterrows():
        # Los nodos de un mismo distrito pueden tener covariables y puntajes idénticos.
        # El quicksort por defecto no fija el orden de empates entre arquitecturas.
        # Redondear a 12 decimales neutraliza diferencias de precisión entre BLAS.
        # Desempate explícito por identificador alfanumérico, sin usar los precios.
        ranked = C.assign(_dist=(C.ps - t.ps).abs().round(12), _id=C.unidad.astype(str))
        ranked = ranked.sort_values(["_dist", "_id"], kind="stable")
        if len(ranked) > K and ranked.iloc[K-1]._dist == ranked.iloc[K]._dist:
            distance = ranked.iloc[K-1]._dist
            info["empates_en_corte"].append({"tratada": t.unidad, "distancia": float(distance),
                "candidatos": ranked.loc[ranked._dist == distance, "unidad"].tolist(),
                "elegidos": ranked.head(K).loc[lambda x: x._dist == distance, "unidad"].tolist()})
        for u in ranked.head(K).unidad:
            pairs.append({"tratada": t.unidad, "control": u})
    info["pares"] = pairs
    P = pd.DataFrame(pairs)
    m_ = P.control.value_counts()
    info["controles_unicos"] = int(len(m_))
    info["posiciones_de_control"] = int(len(P))
    info["balance_antes"] = smd(U[U.tratada], C)
    cw = C.set_index("unidad").loc[m_.index]
    info["balance_despues_pesos_frecuencia"] = smd(T, cw.reset_index(), w=m_.values)
    info["balance_despues_unicos"] = smd(T, cw.reset_index())
    return T, P, m_, info


def exposure_filters(B, map_bar_unit):
    """Controles expuestos: (a) alguna barra de la unidad a < 5 km de cualquier instalación
    (de cualquier año, incluidas unidades excluidas); (b) correlación >= 0,5 entre el D mensual
    2017-2018 de la unidad y el promedio de las unidades tratadas (regla del artículo, p. 18)."""
    I = pd.read_csv(ROOT / "datos" / "instalaciones" / "instalaciones_geo.csv").dropna(subset=["lat"])
    I = I[I.clase.isin(["campus_dedicado", "sala_urbana"])]
    lat0 = np.radians(-33.45)
    near = set()
    for _, b in B.dropna(subset=["lat"]).iterrows():
        d = np.sqrt(((I.lon - b.lon) * 111.32 * np.cos(lat0)) ** 2 + ((I.lat - b.lat) * 110.57) ** 2)
        if (d < 5).any():
            near.add(map_bar_unit.get(b.barra))
    Mm = pd.read_parquet(ROOT / "datos" / "panel" / "barra_mes.parquet")
    Mm = Mm[(Mm.mes < 201901) & Mm.barra.isin(map_bar_unit)]
    Mm["D"] = Mm.sum_D / Mm.horas_D.replace(0, np.nan)
    Mm["unidad"] = Mm.barra.map(map_bar_unit)
    S = Mm.groupby(["unidad", "mes"]).D.mean().unstack(0)
    return near, S


def build(alt, map_bar_unit, hist, cov_level, balanced=True, filtro=None, B=None):
    y = outcomes(map_bar_unit, balanced)
    cov = covariates(cov_level)
    H = hist.copy()
    if filtro:
        near, S = exposure_filters(B, map_bar_unit)
        tr = H.loc[H.estado == "tratada", "unidad"]
        if filtro == "lejos5km":
            drop = set(H.loc[(H.estado == "control") & H.unidad.isin(near), "unidad"])
        else:
            ref = S[[u for u in tr if u in S]].mean(axis=1)
            corr = S.corrwith(ref)
            drop = set(H.loc[(H.estado == "control") & H.unidad.map(corr).ge(0.5), "unidad"])
        H = H[~H.unidad.isin(drop)]
    H = H[H.unidad.isin(y.unidad.unique())]
    H = H[H.estado.isin(["tratada", "control"])]
    if "comuna_cov" in H:
        H = H.merge(cov[["unidad"] + COV].rename(columns={"unidad": "comuna_cov"}), on="comuna_cov", how="left")
    else:
        H = H.merge(cov[["unidad"] + COV], on="unidad", how="left")
    H["tratada"] = H.estado == "tratada"
    H = H.dropna(subset=COV)
    T, P, m_, info = match(H.copy(), alt)
    info["alternativa"] = alt
    info["panel_balanceado_de_barras"] = balanced
    # filas: tratadas (peso 1) y cada copia de control (peso 1/m)
    rows = [T[["unidad", "G_doc", "G_min"]].assign(copia="T", peso=1.0)]
    for i, (_, p) in enumerate(P.iterrows()):
        rows.append(pd.DataFrame({"unidad": [p.control], "G_doc": [np.nan], "G_min": [np.nan], "copia": [f"C{i}"],
                                  "peso": [1.0 / m_[p.control]]}))
    S = pd.concat(rows, ignore_index=True)
    M = S.merge(y, on="unidad")
    M["unidad_copia"] = M.unidad.astype(str) + "|" + M.copia
    # muestra completa sin emparejar (todas las tratadas y controles con precio) para comparación
    F = H[["unidad", "G_doc", "G_min", "tratada"]].merge(y, on="unidad")
    OUT.mkdir(parents=True, exist_ok=True)
    M.to_csv(OUT / f"muestra_{alt}.csv", index=False)
    F.to_csv(OUT / f"muestra_{alt}_sin_emparejar.csv", index=False)
    info["filas_muestra_emparejada"] = int(len(M))
    info["unidades_panel_sin_emparejar"] = int(F.unidad.nunique())
    info["anios"] = sorted(M.anio.unique().tolist())
    (ROOT / "resultados" / f"emparejamiento_{alt}.json").write_text(json.dumps(info, ensure_ascii=False, indent=1, default=str))
    print(alt, {k: info[k] for k in ["n_tratadas", "n_controles", "tratadas_fuera_de_soporte", "controles_unicos", "posiciones_de_control"]})
    return info


def main():
    B = bars()
    hd = pd.read_csv(ROOT / "datos" / "unidades" / "historia_distrito.csv")
    build("distrito", dict(zip(B.barra, B.distrito_nombre)), hd, "distrito")
    build("distrito_nobal", dict(zip(B.barra, B.distrito_nombre)), hd, "distrito", balanced=False)
    build("distrito_ctrl_lejos5km", dict(zip(B.barra, B.distrito_nombre)), hd, "distrito", filtro="lejos5km", B=B)
    build("distrito_ctrl_corr_menor05", dict(zip(B.barra, B.distrito_nombre)), hd, "distrito", filtro="corr", B=B)
    hc = pd.read_csv(ROOT / "datos" / "unidades" / "historia_comuna.csv")
    build("comuna", dict(zip(B.barra, B.comuna_ine)), hc, "comuna")
    dist_of_sub = B.groupby("id_subestacion").distrito_nombre.first()
    for r in [2, 3]:
        hn = pd.read_csv(ROOT / "datos" / "unidades" / f"historia_nodo_r{r}km.csv")
        hn["comuna_cov"] = hn.unidad.map(dist_of_sub)
        build(f"nodo_r{r}km", dict(zip(B.barra, B.id_subestacion)), hn, "distrito")


if __name__ == "__main__":
    main()

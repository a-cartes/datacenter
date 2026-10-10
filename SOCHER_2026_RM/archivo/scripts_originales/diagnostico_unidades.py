"""Historia de exposición y soporte empírico por unidad territorial candidata (RM, 2017-2025).

Alternativas: comuna (INE 2017), distrito censal (INE 2017) y entorno de nodo (subestación con
precio) con radio r km (2, 3 y 5). Para cada unidad se clasifica, con las instalaciones de
clase campus_dedicado o sala_urbana que operaban a 2025:
  previa    : alguna instalación con operación acreditada antes de 2019 (excluida, como las
              unidades con centros previos en el artículo);
  tratada   : primera operación documentada en 2019-2025 y ninguna previa; G = año;
  incierta  : instalación sin fecha que acote si operaba antes de 2019, o sin coordenadas
              en la unidad (solo afecta comuna/distrito por comuna declarada);
  control   : sin instalaciones conocidas ni proyectos operando a 2025.
G se calcula con dos reglas: G_doc (año de la primera operación documentada, op_max) y
G_min (año del límite inferior, op_min); difieren cuando la fecha es un intervalo.
Precios: barras RM con D anual y cobertura >= 0,9 en todos los años 2017-2025 (panel
balanceado) o en algún año (no balanceado). La pertenencia a una unidad usa la subestación.
Salidas: resultados/diagnostico_unidades.json y datos/unidades/historia_<alternativa>.csv
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUTU = ROOT / "datos" / "unidades"
Y0, Y1, ELIG = 2017, 2025, 2019


def year(s):
    return pd.to_datetime(s, errors="coerce").dt.year


def facilities():
    I = pd.read_csv(ROOT / "datos" / "instalaciones" / "instalaciones_geo.csv")
    I = I[I.clase.isin(["campus_dedicado", "sala_urbana"])].copy()
    I["y_min"] = year(I.op_min)
    I["y_doc"] = year(I.op_max)
    I["opera_2025"] = ~I.op_precision.isin(["no_opera_2025"]) & (I.y_doc.fillna(9999) <= Y1) | (
        I.op_precision.eq("cota_superior"))
    # proyectos sin fecha de operación (construcción/expansión) no generan exposición
    I.loc[I.op_max.isna() & ~I.op_precision.eq("cota_superior"), "opera_2025"] = False
    I["previa"] = I.y_doc < ELIG
    I["fecha_ambigua"] = I.op_precision.eq("cota_superior") & (I.y_doc >= ELIG)  # pudo existir antes de 2019
    return I


def classify(I, key):
    rows = []
    for u, g in I[I.opera_2025].groupby(key):
        if g.previa.any():
            st, G = "previa", None
        elif g.fecha_ambigua.any():
            st, G = "incierta", None
        else:
            st = "tratada"
        rec = {"unidad": u, "estado": st, "instalaciones": "; ".join(g.id),
               "G_doc": int(g.y_doc.min()) if st == "tratada" else None,
               "G_min": int(g.y_min.fillna(g.y_doc).min()) if st == "tratada" else None}
        rows.append(rec)
    return pd.DataFrame(rows)


def prices():
    A = pd.read_parquet(ROOT / "datos" / "panel" / "barra_anio.parquet")
    D = pd.read_csv(ROOT / "datos" / "geo" / "barras_diccionario.csv")
    S = pd.read_csv(ROOT / "datos" / "geo" / "subestaciones_unidades.csv")
    D = D.merge(S[["id_subestacion", "comuna_ine", "distrito_ine", "distrito_nombre"]], on="id_subestacion", how="left")
    rm = D[D.comuna_ine.notna()]
    A = A[A.barra.isin(rm.barra)]
    ok = A[(A.cobertura_D >= 0.9)].groupby("barra").anio.nunique()
    rm = rm.assign(anios_validos=rm.barra.map(ok).fillna(0).astype(int))
    rm["balanceada"] = rm.anios_validos == (Y1 - Y0 + 1)
    return rm


def summarize(H, units_with_price_bal, units_with_price_any, nombre):
    H = H.copy()
    t = H[H.estado == "tratada"]
    out = {"unidades_con_instalaciones": int(len(H)), "por_estado": H.estado.value_counts().to_dict(),
           "tratadas": t[["unidad", "G_doc", "G_min", "instalaciones"]].to_dict(orient="records"),
           "tratadas_con_precio_balanceado": int(t.unidad.isin(units_with_price_bal).sum()),
           "tratadas_con_precio_alguno": int(t.unidad.isin(units_with_price_any).sum()),
           "cohortes_G_doc_con_precio_bal": t[t.unidad.isin(units_with_price_bal)].G_doc.value_counts().sort_index().to_dict(),
           "G_doc_distinto_de_G_min": int((t.G_doc != t.G_min).sum())}
    return out


def main():
    OUTU.mkdir(parents=True, exist_ok=True)
    I = facilities()
    rm = prices()
    res = {"ventana": [Y0, Y1], "primer_G_elegible": ELIG, "instalaciones_consideradas": int(len(I)),
           "instalaciones_operando_2025": int(I.opera_2025.sum()),
           "barras_RM_localizadas": int(len(rm)), "barras_RM_balanceadas": int(rm.balanceada.sum()),
           "subestaciones_RM_con_barra_balanceada": int(rm[rm.balanceada].id_subestacion.nunique())}

    # A. comuna
    I["k_comuna"] = I.comuna_ine.fillna(I.comuna.str.upper().str.split(" \\(").str[0])
    H = classify(I, "k_comuna")
    allc = sorted(rm.comuna_ine.dropna().unique())
    full = pd.DataFrame({"unidad": sorted(set(allc) | set(H.unidad))}).merge(H, on="unidad", how="left")
    full["estado"] = full.estado.fillna("control")
    bal = set(rm[rm.balanceada].comuna_ine)
    anyp = set(rm[rm.anios_validos > 0].comuna_ine)
    full["con_precio_balanceado"] = full.unidad.isin(bal)
    full.to_csv(OUTU / "historia_comuna.csv", index=False)
    s = summarize(full[full.estado != "control"], bal, anyp, "comuna")
    s["controles_con_precio_balanceado"] = int(((full.estado == "control") & full.con_precio_balanceado).sum())
    s["unidades_RM"] = 52
    res["comuna"] = s

    # B. distrito (instalaciones sin coordenadas: su comuna completa queda incierta)
    I["k_dist"] = I.distrito_nombre
    H = classify(I[I.k_dist.notna()], "k_dist")
    sin = I[I.k_dist.isna() & I.opera_2025]
    dist_rm = rm.dropna(subset=["distrito_nombre"])
    full = pd.DataFrame({"unidad": sorted(set(dist_rm.distrito_nombre) | set(H.unidad))}).merge(H, on="unidad", how="left")
    full["comuna"] = full.unidad.str.rsplit("-", n=1).str[0]
    unc_c = set(sin.comuna.str.upper().str.split(" \\(").str[0])
    full.loc[full.estado.isna() & full.comuna.isin(unc_c), "estado"] = "incierta_por_instalacion_sin_coordenada"
    full["estado"] = full.estado.fillna("control")
    bal = set(rm[rm.balanceada].distrito_nombre)
    anyp = set(rm[rm.anios_validos > 0].distrito_nombre)
    full["con_precio_balanceado"] = full.unidad.isin(bal)
    full.to_csv(OUTU / "historia_distrito.csv", index=False)
    s = summarize(full[~full.estado.isin(["control", "incierta_por_instalacion_sin_coordenada"])], bal, anyp, "distrito")
    s["controles_con_precio_balanceado"] = int(((full.estado == "control") & full.con_precio_balanceado).sum())
    s["distritos_con_precio_balanceado"] = len(bal)
    s["distritos_RM"] = 451
    res["distrito"] = s

    # C. entorno de nodo
    S = rm.groupby("id_subestacion").agg(lat=("lat", "first"), lon=("lon", "first"), comuna=("comuna_ine", "first"),
                                          balanceada=("balanceada", "max"), subestacion=("subestacion", "first"),
                                          fecha_entrada=("fecha_entrada_dt", "first")).reset_index()
    loc = I[I.opera_2025 & I.lat.notna()]
    lat0 = np.radians(-33.45)
    for r in [2, 3, 5]:
        rows = []
        for _, n in S.iterrows():
            dx = (loc.lon - n.lon) * 111.32 * np.cos(lat0)
            dy = (loc.lat - n.lat) * 110.57
            dist = np.sqrt(dx ** 2 + dy ** 2)
            near = loc[dist <= r]
            unc = sin[sin.comuna.str.upper().str.split(" \\(").str[0] == str(n.comuna)]
            if len(near) == 0:
                st, G, Gm, ids = ("incierta_por_instalacion_sin_coordenada" if len(unc) else "control"), None, None, ""
            elif near.previa.any():
                st, G, Gm, ids = "previa", None, None, "; ".join(near.id)
            elif near.fecha_ambigua.any():
                st, G, Gm, ids = "incierta", None, None, "; ".join(near.id)
            else:
                st, ids = "tratada", "; ".join(near.id)
                G, Gm = int(near.y_doc.min()), int(near.y_min.fillna(near.y_doc).min())
            rows.append({"unidad": n.id_subestacion, "subestacion": n.subestacion, "comuna": n.comuna, "estado": st,
                         "G_doc": G, "G_min": Gm, "instalaciones": ids, "con_precio_balanceado": bool(n.balanceada),
                         "fecha_entrada_subestacion": n.fecha_entrada})
        full = pd.DataFrame(rows)
        full.to_csv(OUTU / f"historia_nodo_r{r}km.csv", index=False)
        t = full[full.estado == "tratada"]
        res[f"nodo_r{r}km"] = {"nodos": int(len(full)), "por_estado": full.estado.value_counts().to_dict(),
                              "tratados_con_precio_balanceado": int(t.con_precio_balanceado.sum()),
                              "tratados": t[["unidad", "subestacion", "comuna", "G_doc", "G_min", "instalaciones",
                                             "con_precio_balanceado"]].to_dict(orient="records"),
                              "controles_con_precio_balanceado": int(((full.estado == "control") & full.con_precio_balanceado).sum()),
                              "comunas_de_tratados": sorted(t.comuna.unique().tolist())}
    (ROOT / "resultados" / "diagnostico_unidades.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str)[:9000])


if __name__ == "__main__":
    main()

"""Covariables previas al tratamiento (Censo 2017, levantado el 19/04/2017) por distrito y comuna.

Fuentes: capas INE descargadas por descargar_censo2017_ine.py. Distrito: población y viviendas
(capa Distrito); composición agregada desde manzanas urbanas y entidades rurales (capas
Microdatos). Los valores no numéricos (p. ej., suprimidos por confidencialidad) quedan como
faltantes; se informa su número. No hay ingreso del hogar ni escolaridad en estas capas: el
análogo de ingreso mediano y educación del artículo no está disponible a esta escala.
Variables (definiciones propias, documentadas en REGISTRO_DECISIONES.md):
  pob, viv, densidad, sh_inmigrantes, sh_pueblos_originarios, sh_65mas, sh_viv_mat_aceptable,
  sh_urbana.
Salida: datos/covariables/covariables_distrito.csv, covariables_comuna.csv
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INE = ROOT / "fuentes" / "geo" / "ine_censo2017"
OUT = ROOT / "datos" / "covariables"
NUM = ["PERSONAS", "INMIGRANTES", "PUEBLOS_ORIGINARIOS", "DE_65_MAS_ANOS", "TOTAL_VIVIENDAS",
       "IND_MAT_ACEPTABLE", "IND_MAT_RECUPERABLE", "IND_MAT_IRRECUPERABLE"]


def props(name):
    return pd.DataFrame([f["properties"] for f in json.loads((INE / name).read_text())["features"]])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = props("Distrito_Densid_Superficie_0_RM.geojson")
    d["distrito_ine"] = d.CODIGO_C17.astype(str)
    d["distrito_nombre"] = d.NOM_COMUNA + "-" + d.COD_DISTRI.astype(str)
    m = props("Microdatos_Censo_1_RM.geojson")
    m["distrito_ine"] = (m.CUT.astype(int) * 100 + m.COD_DISTRITO.astype(int)).astype(str)
    e = props("Microdatos_Censo_0_RM.geojson")
    e["distrito_ine"] = (e.COD_COMUNA.astype(int) * 100 + e.DISTRITO.astype(int)).astype(str)
    x = pd.concat([m.assign(area="urbana"), e.assign(area="rural")], ignore_index=True)
    supr = {}
    for c in NUM:
        v = pd.to_numeric(x[c], errors="coerce")
        supr[c] = int(v.isna().sum() - x[c].isna().sum())
        x[c] = v
    g = x.groupby("distrito_ine")[NUM].sum(min_count=1)
    # denominadores solo con manzanas/entidades cuyo numerador es válido (supresión no es cero)
    for c in ["INMIGRANTES", "PUEBLOS_ORIGINARIOS", "DE_65_MAS_ANOS"]:
        g[f"PERS_{c}"] = x.PERSONAS.where(x[c].notna()).groupby(x.distrito_ine).sum(min_count=1)
    g["n_unidades"] = x.groupby("distrito_ine").size()
    D = d[["distrito_ine", "distrito_nombre", "COMUNA", "NOM_COMUNA", "TIPO_DISTR", "T_POB", "T_POB_U", "T_VIV",
           "SUPERFICIE__KM2_", "Densidad"]].merge(g, on="distrito_ine", how="left")
    D = D.rename(columns={"T_POB": "pob", "T_VIV": "viv", "SUPERFICIE__KM2_": "km2", "Densidad": "densidad"})
    D["sh_urbana"] = D.T_POB_U / D.pob
    D["sh_inmigrantes"] = D.INMIGRANTES / D.PERS_INMIGRANTES
    D["sh_pueblos_originarios"] = D.PUEBLOS_ORIGINARIOS / D.PERS_PUEBLOS_ORIGINARIOS
    D["sh_65mas"] = D.DE_65_MAS_ANOS / D.PERS_DE_65_MAS_ANOS
    tot = D[["IND_MAT_ACEPTABLE", "IND_MAT_RECUPERABLE", "IND_MAT_IRRECUPERABLE"]].sum(axis=1, min_count=1)
    D["sh_viv_mat_aceptable"] = D.IND_MAT_ACEPTABLE / tot
    D["cobertura_microdatos"] = D.PERSONAS / D.pob
    D.to_csv(OUT / "covariables_distrito.csv", index=False)
    c = D.groupby(["COMUNA", "NOM_COMUNA"]).agg(pob=("pob", "sum"), viv=("viv", "sum"), km2=("km2", "sum"),
                                                 PERSONAS=("PERSONAS", "sum"), INMIGRANTES=("INMIGRANTES", "sum"),
                                                 PUEBLOS_ORIGINARIOS=("PUEBLOS_ORIGINARIOS", "sum"),
                                                 DE_65_MAS_ANOS=("DE_65_MAS_ANOS", "sum"), T_POB_U=("T_POB_U", "sum"),
                                                 P_INM=("PERS_INMIGRANTES", "sum"), P_PO=("PERS_PUEBLOS_ORIGINARIOS", "sum"),
                                                 P_65=("PERS_DE_65_MAS_ANOS", "sum"),
                                                 IND_MAT_ACEPTABLE=("IND_MAT_ACEPTABLE", "sum"),
                                                 tot_mat=("IND_MAT_ACEPTABLE", lambda s: np.nan)).reset_index()
    tm = D.assign(t=tot).groupby("COMUNA").t.sum()
    c["densidad"] = c.pob / c.km2
    c["sh_urbana"] = c.T_POB_U / c.pob
    c["sh_inmigrantes"] = c.INMIGRANTES / c.P_INM
    c["sh_pueblos_originarios"] = c.PUEBLOS_ORIGINARIOS / c.P_PO
    c["sh_65mas"] = c.DE_65_MAS_ANOS / c.P_65
    c["sh_viv_mat_aceptable"] = c.IND_MAT_ACEPTABLE / c.COMUNA.map(tm)
    c.drop(columns=["tot_mat"]).to_csv(OUT / "covariables_comuna.csv", index=False)
    meta = {"valores_no_numericos_por_campo": supr, "distritos": int(len(D)), "comunas": int(len(c)),
            "cobertura_microdatos_mediana": float(D.cobertura_microdatos.median())}
    (OUT / "covariables_meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    print(meta)
    print(D[["pob", "viv", "densidad", "sh_inmigrantes", "sh_pueblos_originarios", "sh_65mas", "sh_viv_mat_aceptable", "sh_urbana"]].describe().T)


if __name__ == "__main__":
    main()

"""Diccionario de barras de precio: código de transferencia -> barra Infotécnica -> subestación.

Vínculos, en orden de prioridad (todos se registran; los conflictos quedan marcados):
  a) ID_INFO del TSV moderno (id de barra Infotécnica), por código y mes;
  b) nemotécnico de los archivos oficiales 'Homologación barras' (dic 2023 - jul 2024);
  c) ID_INFOTECNICA del archivo de factores reales del 15/07/2024.
Códigos históricos sin vínculo directo heredan el del mismo código moderno solo si este es
único; no se infiere por nombre parecido. La comuna y coordenadas son las de la subestación
en Infotécnica (consulta 2026-10-02), con su estado de certificación.
Salida: datos/geo/barras_diccionario.csv y datos/geo/barras_vigencia.csv (meses con precio).
"""
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd

from comun import canon_base, colapsar

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "datos" / "geo"


def main():
    # vigencia de códigos en precios
    vig = []
    for d, reg in [(ROOT / "datos" / "precios_hist", "historico"), (ROOT / "datos" / "precios_mod", "moderno")]:
        for f in sorted(d.glob("[0-9]*.parquet")):
            cols = ["barra", "P"] + (["id_info", "barra_info"] if reg == "moderno" else [])
            x = pd.read_parquet(f, columns=cols)
            g = x.groupby("barra").agg(n=("P", "size"), n_validos=("P", "count"),
                                       **({"id_info": ("id_info", "first"), "barra_info": ("barra_info", "first"),
                                           "n_id": ("id_info", "nunique")} if reg == "moderno" else {})).reset_index()
            g["mes"] = int(f.stem)
            g["regimen"] = reg
            vig.append(g)
    vig = pd.concat(vig)
    vig["barra_original"] = vig.barra
    vig["barra"] = vig.barra.map(canon_base)
    # alias por cambio de relleno con guiones bajos: mismo código colapsado, períodos sin superposición
    rng = vig.groupby("barra").mes.agg(["min", "max"]).reset_index()
    rng["clave"] = rng.barra.map(colapsar)
    alias = []
    for k, g in rng.groupby("clave"):
        if len(g) < 2:
            continue
        g = g.sort_values("min")
        if (g["min"].values[1:] > g["max"].values[:-1]).all():
            new = g.barra.iloc[-1]
            alias += [{"codigo_antiguo": b, "codigo_canonico": new, "hasta": mx, "desde_canonico": g["min"].iloc[-1]}
                      for b, mx in zip(g.barra.iloc[:-1], g["max"].iloc[:-1])]
        else:
            print("Códigos con misma clave y meses superpuestos (no se fusionan):", list(g.barra))
    pd.DataFrame(alias, columns=["codigo_antiguo", "codigo_canonico", "hasta", "desde_canonico"]).to_csv(GEO / "alias_codigos.csv", index=False)
    print("alias por guiones bajos:", len(alias))
    am = {a["codigo_antiguo"]: a["codigo_canonico"] for a in alias}
    vig["barra"] = vig.barra.map(lambda b: am.get(b, b))
    vig.to_csv(GEO / "barras_vigencia.csv", index=False)

    ib = pd.read_csv(GEO / "barras_infotecnica.csv")
    nemo = pd.DataFrame(__import__("json").load(open(ROOT / "fuentes" / "infotecnica" / "barras.json")))[["id", "nemotecnico"]]
    ib = ib.merge(nemo.rename(columns={"id": "id_barra_info"}), on="id_barra_info", how="left")
    se = pd.read_csv(GEO / "subestaciones_infotecnica.csv")

    links = []
    m = vig[vig.regimen == "moderno"].dropna(subset=["id_info"])
    m = m[m.id_info > 0]
    for (b, i), g in m.groupby(["barra", "id_info"]):
        links.append({"barra": b, "id_barra_info": int(i), "metodo": "a_id_info_tsv", "meses": len(g)})
    hom = []
    for f in sorted((ROOT / "fuentes" / "precios" / "originales" / "historico").rglob("Homolog*.xlsx")):
        h = pd.read_excel(f, sheet_name="HOMOLOGACIÓN").iloc[:, :3]
        h.columns = ["barra", "barra_aux", "nemotecnico"]
        h["barra"] = h.barra.astype(str).str.strip().map(canon_base).map(lambda b: am.get(b, b))
        h["nemotecnico"] = h.nemotecnico.astype(str).str.strip()
        h["archivo"] = f.parent.parent.name
        hom.append(h)
    hom = pd.concat(hom).dropna(subset=["nemotecnico"]).merge(ib[["id_barra_info", "nemotecnico"]], on="nemotecnico", how="left")
    for (b, i), g in hom.dropna(subset=["id_barra_info"]).groupby(["barra", "id_barra_info"]):
        links.append({"barra": b, "id_barra_info": int(i), "metodo": "b_homologacion", "meses": g.archivo.nunique()})
    z = ZipFile(ROOT / "fuentes" / "precios" / "Antecedentes_CMG_Real_def_240715.zip")
    fp = pd.read_excel(BytesIO(z.read("Fpen_Reales_240715.xlsx")))[["BARRA_TRANSF", "ID_INFOTECNICA"]].drop_duplicates()
    for _, r in fp[fp.ID_INFOTECNICA > 0].iterrows():
        links.append({"barra": am.get(canon_base(r.BARRA_TRANSF), canon_base(r.BARRA_TRANSF)), "id_barra_info": int(r.ID_INFOTECNICA), "metodo": "c_fpen_20240715", "meses": 1})
    # d) nombre exacto de barra Infotécnica informado en el TSV (sin etiquetas entre corchetes)
    nm = m.assign(nombre=m.barra_info.str.replace(r"\s*\[.*?\]", "", regex=True).str.strip())
    nm = nm.merge(ib[["id_barra_info", "barra_info_nombre"]], left_on="nombre", right_on="barra_info_nombre")
    for (b, i), g in nm.groupby(["barra", "id_barra_info_y" if "id_barra_info_y" in nm else "id_barra_info"]):
        links.append({"barra": b, "id_barra_info": int(i), "metodo": "d_nombre_barra_info", "meses": len(g)})
    L = pd.DataFrame(links)
    L["resuelve"] = L.id_barra_info.isin(ib.id_barra_info)
    L.to_csv(GEO / "barras_vinculos_todos.csv", index=False)
    L = L[L.resuelve]
    best = (L.sort_values(["barra", "metodo", "meses"], ascending=[True, True, False])
             .groupby("barra").agg(id_barra_info=("id_barra_info", "first"), metodo=("metodo", "first"),
                                   ids_distintos=("id_barra_info", "nunique"),
                                   todos=("id_barra_info", lambda s: ";".join(map(str, sorted(set(s)))))).reset_index())
    codes = vig.groupby("barra").agg(primer_mes=("mes", "min"), ultimo_mes=("mes", "max"), meses=("mes", "nunique"),
                                     codigos_originales=("barra_original", lambda s: ";".join(sorted(set(s)))),
                                     regimenes=("regimen", lambda s: ";".join(sorted(set(s))))).reset_index()
    D = codes.merge(best, on="barra", how="left").merge(ib, on="id_barra_info", how="left")
    # e) mismo prefijo exacto del código (misma subestación, otra tensión) con una única subestación vinculada;
    #    no se aplica a derivaciones (TAP*, T_*), que no son subestaciones.
    D["prefijo"] = D.barra.str[:14].str.rstrip("_")
    pref = D.dropna(subset=["id_subestacion"]).groupby("prefijo").id_subestacion.agg(["nunique", "first"])
    pref = pref[pref["nunique"] == 1]["first"]
    sin = D.id_subestacion.isna() & ~D.prefijo.str.match(r"^(TAP|T_|TOFF|EST)") & D.prefijo.isin(pref.index)
    D.loc[sin, "id_subestacion"] = D.loc[sin, "prefijo"].map(pref)
    D.loc[sin, "metodo"] = "e_prefijo_misma_subestacion"
    D = D.merge(se[["id_subestacion", "subestacion", "region", "provincia", "comuna", "comuna_estado", "lat", "lon",
                    "este_estado", "fecha_entrada_dt", "fecha_entrada_estado", "propietario_nombre"]].rename(
        columns={"propietario_nombre": "propietario_subestacion"}), on="id_subestacion", how="left", suffixes=("", "_se"))
    D["nivel_kv_codigo"] = D.barra.str[-3:]
    D["es_RM"] = D.region.fillna("").str.contains("Metropolitana")
    D.to_csv(GEO / "barras_diccionario.csv", index=False)
    print("códigos", len(D), "con subestación", D.id_subestacion.notna().sum(), "conflictos", (D.ids_distintos > 1).sum(),
          "RM", D.es_RM.sum())
    print(D.metodo.value_counts(dropna=False))
    print(D[D.id_subestacion.isna()].sort_values("meses", ascending=False)[["barra", "primer_mes", "ultimo_mes", "meses"]].head(30).to_string())


if __name__ == "__main__":
    main()

"""Panel barra-mes y barra-año de precios y del diferencial respecto de Quillota 220 kV.

Por hora h y barra i (código canónico):
  P_ih  : precio publicado (USD/MWh); E_h = P de QUILLOTA______220 en la misma hora y archivo.
  D_ih  = P_ih - E_h                       (resultado principal: componente espacial relativo)
  L_ih  = E_h (FP_ih - 1),  C_ih = P_ih - E_h FP_ih   (solo régimen histórico, FP por tramo)
Agregación: sumas y conteos por barra-mes; el promedio anual pondera por horas válidas.
Una hora entra en D si P_ih y E_h existen. No se rellenan faltantes; los ceros publicados
se conservan. Las horas del régimen moderno son promedios de cuartos (hora = HRA + 1).
Salidas: datos/panel/barra_mes.parquet, datos/panel/barra_anio.parquet, datos/panel/referencia_mes.csv
"""
from pathlib import Path

import numpy as np
import pandas as pd

from comun import canon

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "datos" / "panel"
REF = "QUILLOTA______220"


def month_frame(f, regimen):
    cols = ["mes", "dia", "hora", "barra", "P"] + (["fp"] if regimen == "historico" else ["n_cuartos"])
    x = pd.read_parquet(f, columns=cols)
    x["barra"] = x.barra.map(canon)
    if regimen == "moderno":
        x["fp"] = np.nan
    q = x[x.barra == REF][["dia", "hora", "P"]].rename(columns={"P": "E"})
    nq = q.groupby(["dia", "hora"]).size()
    q = q[q.set_index(["dia", "hora"]).index.map(nq).values == 1]  # referencia única por hora
    x = x.merge(q, on=["dia", "hora"], how="left")
    x["D"] = x.P - x.E
    x["L"] = x.E * (x.fp - 1)
    x["C"] = x.P - x.E * x.fp
    ok = x.P.notna() & x.E.notna()
    okf = ok & x.fp.notna()
    g = x.assign(okD=ok, okLC=okf,
                 Dv=x.D.where(ok), Pv=x.P.where(ok), Ev=x.E.where(ok),
                 Lv=x.L.where(okf), Cv=x.C.where(okf), Pall=x.P).groupby(["mes", "barra"])
    m = g.agg(horas_filas=("P", "size"), horas_P=("Pall", "count"), horas_D=("okD", "sum"), horas_LC=("okLC", "sum"),
              sum_P=("Pv", "sum"), sum_E=("Ev", "sum"), sum_D=("Dv", "sum"), sum_L=("Lv", "sum"), sum_C=("Cv", "sum"),
              sum_P_todas=("Pall", "sum"), ceros_P=("Pall", lambda s: int((s == 0).sum()))).reset_index()
    m["regimen"] = regimen
    ref = {"mes": int(x.mes.iloc[0]), "regimen": regimen, "horas_mes": int(x[["dia", "hora"]].drop_duplicates().shape[0]),
           "horas_con_referencia": int(len(q)), "E_media": float(q.E.mean()), "E_ceros": int((q.E == 0).sum())}
    return m, ref


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ms, refs = [], []
    for d, reg in [(ROOT / "datos" / "precios_hist", "historico"), (ROOT / "datos" / "precios_mod", "moderno")]:
        for f in sorted(d.glob("[0-9]*.parquet")):
            m, r = month_frame(f, reg)
            ms.append(m)
            refs.append(r)
            print(f.stem, reg, len(m), r["horas_con_referencia"], flush=True)
    M = pd.concat(ms, ignore_index=True)
    M["anio"] = M.mes // 100
    M.to_parquet(OUT / "barra_mes.parquet", index=False)
    pd.DataFrame(refs).to_csv(OUT / "referencia_mes.csv", index=False)
    sums = ["horas_filas", "horas_P", "horas_D", "horas_LC", "sum_P", "sum_E", "sum_D", "sum_L", "sum_C", "ceros_P"]
    A = M.groupby(["anio", "barra"])[sums].sum().reset_index()
    A["meses"] = M.groupby(["anio", "barra"]).mes.nunique().values
    R = pd.DataFrame(refs)
    R["anio"] = R.mes // 100
    hy = R.groupby("anio").horas_con_referencia.sum()
    A["horas_ref_anio"] = A.anio.map(hy)
    A["cobertura_D"] = A.horas_D / A.horas_ref_anio
    for v in ["P", "E", "D"]:
        A[v] = A[f"sum_{v}"] / A.horas_D.replace(0, np.nan)
    for v in ["L", "C"]:
        A[v] = A[f"sum_{v}"] / A.horas_LC.replace(0, np.nan)
    A.to_parquet(OUT / "barra_anio.parquet", index=False)
    print(A.groupby("anio").agg(barras=("barra", "nunique"), D=("D", "mean"), cobertura=("cobertura_D", "median")))


if __name__ == "__main__":
    main()

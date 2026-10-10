"""Diagnóstico de continuidad entre el régimen histórico (hasta 14/07/2024) y el nuevo (desde 15/07/2024).

Comprobaciones:
 1. Abril 2024: el precio horario del libro histórico es el promedio de los cuatro cuartos del
    CSV oficial de 15 minutos con la misma etiqueta de hora (define la convención horaria).
 2. 15/07/2024: el TSV mensual REAL-DEF reproduce el precio R de la muestra diaria oficial.
 3. Universo de barras a ambos lados del corte (julio 2024).
 4. Nivel de D en barras de la RM: diferencia entre 15-31 y 1-14 de julio, contrastada con la
    misma partición en 2023 y 2025 (placebos sin cambio de régimen).
Salida: resultados/continuidad_precios.json
"""
import json
from io import TextIOWrapper
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd

from comun import canon

ROOT = Path(__file__).resolve().parents[1]
REF = "QUILLOTA______220"


def hourly_rm():
    D = pd.read_csv(ROOT / "datos" / "geo" / "barras_diccionario.csv")
    return set(D.loc[D.es_RM, "barra"])


def load(mes):
    f = ROOT / "datos" / ("precios_mod" if mes >= 202407 and (ROOT / "datos" / "precios_mod" / f"{mes}.parquet").exists() else "precios_hist") / f"{mes}.parquet"
    return f


def daily_D(mes, rm):
    out = []
    for sub in ["precios_hist", "precios_mod"]:
        f = ROOT / "datos" / sub / f"{mes}.parquet"
        if not f.exists():
            continue
        x = pd.read_parquet(f, columns=["dia", "hora", "barra", "P"])
        x["barra"] = x.barra.map(canon)
        e = x[x.barra == REF][["dia", "hora", "P"]].rename(columns={"P": "E"})
        x = x[x.barra.isin(rm)].merge(e, on=["dia", "hora"])
        x["D"] = x.P - x.E
        g = x.groupby("dia").agg(D=("D", "mean"), E=("E", "mean"), barras=("barra", "nunique")).reset_index()
        g["fuente"] = sub
        out.append(g)
    return pd.concat(out)


def main():
    res = {}
    # 1
    c = pd.read_csv(ROOT / "fuentes/precios/originales/historico/202404/cmg2404_def/CMgBarras_15_min_Salida_2404.csv",
                    sep=";", usecols=[0, 1, 2, 3, 5])
    c.columns = ["fecha", "hora", "minuto", "barra", "P15"]
    c["dia"] = c.fecha % 100
    h = c.groupby(["barra", "dia", "hora"]).P15.agg(["mean", "size"]).reset_index()
    x = pd.read_parquet(ROOT / "datos/precios_hist/202404.parquet")
    m = x.merge(h, on=["barra", "dia", "hora"])
    e = (m.P - m["mean"]).abs()
    h2 = h.assign(hora=h.hora + 1)
    m2 = x.merge(h2, on=["barra", "dia", "hora"])
    res["1_abril2024_hora_vs_cuartos"] = {
        "pares": int(len(m)), "abs_dif_max": float(e.max()), "abs_dif_p99": float(e.quantile(.99)),
        "share_menor_0_01": float((e < 0.01).mean()),
        "share_menor_0_01_si_se_desplaza_una_hora": float(((m2.P - m2["mean"]).abs() < 0.01).mean()),
        "etiquetas_hora_csv": [int(c.hora.min()), int(c.hora.max())],
        "conclusion": "hora histórica h = promedio de cuartos HORA=h; HRA moderna = h-1"}
    # 2
    z = ZipFile(ROOT / "fuentes/precios/Antecedentes_CMG_Real_def_240715.zip")
    a = pd.read_csv(z.open("PromediosBarras20240715_20240715_R.csv"), sep=";").rename(columns={"CMg[mills/kWh]": "P_muestra"})
    t = pd.read_csv(ROOT / "fuentes/precios/originales/moderno/202407_REAL-DEF.tsv.gz", sep="\t")
    t = t[t.FECHA == "2024-07-15"]
    pc = [k for k in t.columns if "mills" in k or "USD" in k][0]
    t = t.rename(columns={pc: "P_tsv"})
    pc = "P_tsv"
    mm = a.merge(t, left_on=["BARRA", "HORA", "MINUTO"], right_on=["BARRA_TRANSF", "HRA", "MIN"], how="outer", indicator=True)
    dd = (mm["P_muestra"] - mm[pc]).abs()
    res["2_tsv_vs_muestra_diaria_20240715"] = {"union": mm._merge.value_counts().to_dict(),
                                               "abs_dif_max": float(dd.max()), "identicos": float((dd == 0).mean())}
    # 3
    hj = pd.read_parquet(ROOT / "datos/precios_hist/202407.parquet", columns=["barra"]).barra.map(canon).unique()
    mj = pd.read_parquet(ROOT / "datos/precios_mod/202407.parquet", columns=["barra"]).barra.map(canon).unique()
    res["3_universo_barras_julio2024"] = {"historico_1_14": int(len(hj)), "moderno_15_31": int(len(mj)),
                                         "solo_historico": sorted(set(hj) - set(mj)), "solo_moderno": sorted(set(mj) - set(hj))}
    # 4
    rm = hourly_rm()
    out = {}
    for y in [2023, 2024, 2025]:
        g = daily_D(int(f"{y}07"), rm)
        a1, a2 = g[g.dia <= 14], g[g.dia >= 15]
        diff = a2.D.mean() - a1.D.mean()
        se = np.sqrt(a1.D.var() / len(a1) + a2.D.var() / len(a2))
        out[str(y)] = {"D_1_14": float(a1.D.mean()), "D_15_31": float(a2.D.mean()), "diferencia": float(diff),
                       "ee_aprox_dias": float(se), "E_1_14": float(a1.E.mean()), "E_15_31": float(a2.E.mean()),
                       "barras_RM_dia": [int(g.barras.min()), int(g.barras.max())]}
    res["4_nivel_D_RM_particion_julio"] = out
    res["4_nota"] = ("Diferencias de nivel entre mitades de julio ocurren también sin cambio de régimen; "
                     "la comparación diaria no aísla un quiebre metodológico. Con efectos de año, un cambio "
                     "común a todas las barras se absorbe; uno que cambie diferencias entre barras no.")
    (ROOT / "resultados" / "continuidad_precios.json").write_text(json.dumps(res, ensure_ascii=False, indent=1))
    print(json.dumps(res, ensure_ascii=False, indent=1)[:4000])


if __name__ == "__main__":
    main()

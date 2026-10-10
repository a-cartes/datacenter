"""Piloto de conciliación de precios, factores de penalización y subsistemas.

Lee únicamente las dos muestras oficiales conservadas en fuentes/precios/:
  - cmg1712_def.zip (diciembre de 2017, régimen histórico horario)
  - Antecedentes_CMG_Real_def_240715.zip (15/07/2024, régimen nuevo de 15 minutos)

Contrasta la identidad P_it = lambda_{s(i),t} * FP_it dentro de cada subsistema,
verifica que Quillota 220 kV tenga FP = 1 y construye, como reconstrucción propia,
  E_t   = P_{Quillota220,t}
  L_it  = E_t * (FP_it - 1)                     (pérdidas marginales relativas a Quillota)
  C_it  = P_it - E_t * FP_it                    (separación de subsistemas / desacople)
  D_it  = P_it - E_t = L_it + C_it              (identidad contable exacta)
No ejecuta macros ni recalcula los libros. Escribe en datos/piloto/ y resultados/.

Uso: python scripts/piloto_conciliacion.py
"""
from io import BytesIO, TextIOWrapper
import csv
import json
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fuentes" / "precios"
OUT = ROOT / "datos" / "piloto"
RES = ROOT / "resultados"
REF = "QUILLOTA______220"
OUT.mkdir(parents=True, exist_ok=True)
RES.mkdir(parents=True, exist_ok=True)


def q(s, ps=(0.5, 0.9, 0.99, 1.0)):
    s = pd.Series(s).dropna()
    return {"n": int(s.size), **{f"p{int(p*100)}": float(s.quantile(p)) for p in ps}} if s.size else {"n": 0}


def sheet_rows(wb, name):
    ws = wb[name]
    ws.reset_dimensions()
    return list(ws.iter_rows(values_only=True))


# ----------------------------------------------------------------------------- 2024
def piloto_2024():
    z = ZipFile(SRC / "Antecedentes_CMG_Real_def_240715.zip")
    rd = lambda n: pd.read_csv(z.open(n), sep=";", encoding="utf-8-sig")
    pr = rd("PromediosBarras20240715_20240715_R.csv")
    co = rd("CmgBarrasComparativo_20240715_20240715_15.csv")
    fp = pd.read_excel(BytesIO(z.read("Fpen_Reales_240715.xlsx")))
    sb = pd.read_excel(BytesIO(z.read("Barras_Subsistemas_20240715.xlsx")), sheet_name=None)
    inner = ZipFile(BytesIO(z.read("CMgBarrasMinuto_20240715_20240715.zip")))
    mi = pd.read_csv(inner.open(inner.namelist()[0]), sep=";")
    out = {"archivo_minuto": inner.namelist()[0]}

    for df, h, m in [(pr, "HORA", "MINUTO"), (co, "HORA", "MINUTO"), (fp, "HORA", "MINUTO")]:
        df["t"] = df[h] * 60 + df[m]
    pr = pr.rename(columns={"CMg[mills/kWh]": "P", "CMg[$/KWh]": "P_clp"})

    # 1. Versiones: comparativo (E/P/R) frente al archivo de promedios R
    c = pr.merge(co, on=["BARRA", "t"], how="outer", indicator=True)
    out["comparativo_vs_promedios"] = {
        "union": c["_merge"].value_counts().to_dict(),
        "abs_R_menos_P_promedios": q((c["CMgR[mills/kWh]"] - c["P"]).abs()),
        "abs_preliminar_menos_real": q((c["CMgP[mills/kWh]"] - c["CMgR[mills/kWh]"]).abs()),
        "abs_enlinea_menos_real": q((c["CMgE[mills/kWh]"] - c["CMgR[mills/kWh]"]).abs()),
        "filas_MODIFICADO": c["MODIFICADO"].value_counts().to_dict(),
        "tipo_cambio_unico": sorted(c["USD"].dropna().unique().tolist()),
    }
    out["peso_por_kwh_vs_mills"] = q((pr.P_clp / pr.P).replace([np.inf, -np.inf], np.nan))

    # 2. Factores: universo y tipo
    d = pr.merge(fp[["BARRA_TRANSF", "t", "Fpen", "TIPO", "ID_INFOTECNICA"]],
                 left_on=["BARRA", "t"], right_on=["BARRA_TRANSF", "t"], how="left")
    out["factores"] = {
        "barras_con_factor": int(fp.BARRA_TRANSF.nunique()),
        "barras_precio_sin_factor": int(d.Fpen.isna().groupby(d.BARRA).all().sum()),
        "barras_factor_sin_precio": sorted(set(fp.BARRA_TRANSF) - set(pr.BARRA)),
        "tipo_filas": fp.TIPO.value_counts().to_dict(),
        "quillota220_fp": q(fp.loc[fp.BARRA_TRANSF == REF, "Fpen"], (0, 1.0)),
    }

    # 3. Estado de subsistema por minuto desde el archivo por minuto (función escalonada)
    mi["tm"] = mi.Hora * 60 + mi.Minuto
    mi = mi.sort_values(["Barra", "tm"])
    grid = pd.MultiIndex.from_product([mi.Barra.unique(), range(1440)], names=["Barra", "tm"])
    g = (mi.set_index(["Barra", "tm"])[["Subsistema Designado", "Configuracion", "CMg[mills/kWh]"]]
         .reindex(grid).groupby(level=0).ffill().reset_index())
    g.columns = ["Barra", "tm", "sd", "conf", "pmin"]
    g["t"] = g.tm // 15 * 15
    st = g.groupby(["Barra", "t"]).agg(sd=("sd", "first"), n_sd=("sd", "nunique"),
                                         n_conf=("conf", "nunique"), pmin=("pmin", "mean")).reset_index()
    d = d.merge(st, left_on=["BARRA", "t"], right_on=["Barra", "t"], how="left").drop(columns=["Barra", "BARRA_TRANSF"])
    out["archivo_minuto"] = {
        "nombre": out["archivo_minuto"], "barras": int(mi.Barra.nunique()), "eventos": int(len(mi)),
        "subsistemas_designados": mi["Subsistema Designado"].value_counts().to_dict(),
        "abs_promedio_minutos_menos_P15_todas": q((d.pmin - d.P).abs()),
        "abs_promedio_minutos_menos_P15_quillota220": q((d.pmin - d.P).abs()[d.BARRA == REF]),
        "nota": "Los precios por minuto usan factores distintos de los reales de 15 minutos; solo coinciden donde FP=1.",
    }

    # 4. Identidad P = lambda_s * FP dentro de subsistemas (intervalos sin cambio de subsistema)
    d["lam"] = d.P / d.Fpen
    ok = (d.n_sd == 1) & (d.P > 1)
    grp = d[ok].groupby(["t", "sd"]).lam
    rel = (d.lam - grp.transform("median").reindex(d.index)).abs() / d.lam
    out["identidad_lambda_fp"] = {
        "barra_intervalos_evaluados": int(ok.sum()),
        "desviacion_relativa_lambda": q(rel[ok]),
        "share_desv_menor_1e-4": float((rel[ok] < 1e-4).mean()),
        "por_tipo_factor": {k: q(v) for k, v in rel[ok].groupby(d.TIPO[ok])},
    }
    # Quillota en subsistema principal y lambda de su subsistema
    qq = d[d.BARRA == REF].set_index("t")
    out["quillota220_subsistema"] = qq.sd.value_counts().to_dict()

    # 5. Reconstrucción E, L, C, D
    d = d.merge(qq.P.rename("E"), left_on="t", right_index=True, how="left")
    d["L"] = d.E * (d.Fpen - 1)
    d["C"] = d.P - d.E * d.Fpen
    d["D"] = d.P - d.E
    out["identidad_D_igual_L_mas_C_max_abs"] = float((d.D - d.L - d.C).abs().max())
    inter = d.groupby("t").sd.nunique()
    out["intervalos"] = {"total": int(inter.size), "con_mas_de_un_subsistema": int((inter > 1).sum()),
                         "solo_un_subsistema": int((inter == 1).sum())}
    out["C_abs_por_estado"] = {
        "barras_en_subsistema_de_quillota": q(d.C.abs()[d.sd == d.t.map(qq.sd)]),
        "barras_en_otro_subsistema": q(d.C.abs()[(d.sd != d.t.map(qq.sd)) & d.sd.notna()]),
    }
    des = sb["Desacoples_Jerarquia"]
    out["desacoples_registrados"] = des.astype(str).to_dict(orient="records")
    sd4 = sorted(d.loc[d.sd == "SD4", "BARRA"].unique())
    out["barras_SD4"] = sd4
    rm = d[d.BARRA.isin(sd4)]
    out["SD4_resumen"] = {
        "intervalos_desacoplados": int(rm.loc[rm.sd == "SD4", "t"].nunique()),
        "C_medio_desacoplado": float(rm.loc[rm.sd == "SD4", "C"].mean()),
        "L_medio_desacoplado": float(rm.loc[rm.sd == "SD4", "L"].mean()),
        "D_medio_dia": float(rm.D.mean()), "C_medio_dia": float(rm.C.mean()), "L_medio_dia": float(rm.L.mean()),
    }
    cols = ["BARRA", "BARRA INFO ID", "BARRA INFO NOMBRE", "ID_INFOTECNICA", "HORA", "MINUTO", "t", "P", "P_clp",
            "Fpen", "TIPO", "sd", "n_sd", "n_conf", "lam", "E", "L", "C", "D"]
    d[cols].to_csv(OUT / "piloto_20240715_15min.csv.gz", index=False)
    return out


# ----------------------------------------------------------------------------- 2017
def piloto_2017():
    z = ZipFile(SRC / "cmg1712_def.zip")
    wb = openpyxl.load_workbook(BytesIO(z.read("cmg1712_def.xlsm")), read_only=True, data_only=True, keep_links=False)
    rows = sheet_rows(wb, "CMG Barras dolares")
    hdr = rows[8]
    bars = [b for b in hdr[3:] if b]
    data = [r[:3 + len(bars)] for r in rows[10:] if r and r[0] is not None and str(r[0]).startswith("2017")]
    P = pd.DataFrame(data, columns=["mes", "dia", "hora"] + bars).melt(["mes", "dia", "hora"], var_name="barra", value_name="P")
    P["P"] = pd.to_numeric(P.P, errors="coerce")
    P[["dia", "hora"]] = P[["dia", "hora"]].astype(int)

    fr = sheet_rows(wb, "Factores de Penalización")
    dates, blk = fr[8], fr[9]
    cur, dcol = None, {}
    for j in range(2, len(blk)):
        cur = dates[j] or cur
        dcol[j] = (cur, blk[j])
    F = [(r[0], pd.Timestamp(dcol[j][0]).day, int(dcol[j][1]), r[j])
         for r in fr[10:] if r and r[0] for j in range(2, len(r))
         if r[j] is not None and j in dcol and dcol[j][1] in (1, 2, 3)]
    F = pd.DataFrame(F, columns=["barra", "dia", "tramo", "fp"])
    F["fp"] = pd.to_numeric(F.fp, errors="coerce")

    cm = []
    for name in ["central marginal por barra (a)", "central marginal por barra (b)"]:
        rr = sheet_rows(wb, name)
        cm += [r[:7] for r in rr[1:] if r[0]]
    cm = pd.DataFrame(cm, columns=["barra", "dia", "sd", "hora", "orden", "central", "minutos"])
    cm[["dia", "hora"]] = cm[["dia", "hora"]].astype(int)
    sd = cm.groupby(["barra", "dia", "hora"]).agg(sd=("sd", "first"), n_sd=("sd", "nunique"),
                                                   n_central=("central", "nunique"), minutos=("minutos", "sum")).reset_index()
    wb.close()
    out = {"barras_precio": len(bars), "precios_vacios": int(P.P.isna().sum()),
           "barras_factor": int(F.barra.nunique()), "barras_central_marginal": int(sd.barra.nunique()),
           "minutos_por_barra_hora": q(sd.minutos, (0, 1.0)), "subsistemas_por_barra_hora_max": int(sd.n_sd.max())}

    d = P.merge(sd, on=["barra", "dia", "hora"], how="left")
    ev = d[(d.P > 5) & d.sd.notna()]
    # Búsqueda empírica de tramos: horas 1..a -> 1, a+1..b -> 2, resto -> 3
    best = []
    for a in range(1, 23):
        for b in range(a + 1, 24):
            x = ev.assign(tramo=np.where(ev.hora <= a, 1, np.where(ev.hora <= b, 2, 3)))
            x = x.merge(F, on=["barra", "dia", "tramo"], how="left")
            l = np.log(x.P / x.fp)
            dev = (l - l.groupby([x.dia, x.hora, x.sd]).transform("median")).abs()
            best.append({"a": a, "b": b, "media": float(dev.mean()), "share_menor_0_5pct": float((dev < 0.005).mean())})
    best = sorted(best, key=lambda r: r["media"])
    out["busqueda_tramos_top5"] = best[:5]
    a, b = best[0]["a"], best[0]["b"]
    out["tramos_elegidos"] = {"1": f"horas 1-{a}", "2": f"horas {a+1}-{b}", "3": f"horas {b+1}-24"}
    d["tramo"] = np.where(d.hora <= a, 1, np.where(d.hora <= b, 2, 3))
    d = d.merge(F, on=["barra", "dia", "tramo"], how="left")
    out["barra_horas_sin_factor"] = int(d.fp.isna().sum())
    out["quillota220_fp"] = q(d.loc[d.barra == REF, "fp"], (0, 1.0))
    d["lam"] = d.P / d.fp
    ok = (d.P > 5) & d.sd.notna() & d.fp.notna()
    rel = (np.log(d.lam) - np.log(d.lam).groupby([d.dia, d.hora, d.sd]).transform("median")).abs()
    out["identidad_lambda_fp"] = {"evaluadas": int(ok.sum()), "desv_log": q(rel[ok]),
                                  "share_menor_0_5pct": float((rel[ok] < 0.005).mean()),
                                  "nota": "Precios publicados con un decimal; error de redondeo esperado de hasta 0,05/P."}
    qq = d[d.barra == REF].set_index(["dia", "hora"])
    d = d.merge(qq.P.rename("E"), left_on=["dia", "hora"], right_index=True, how="left")
    d = d.merge(qq.sd.rename("sd_ref"), left_on=["dia", "hora"], right_index=True, how="left")
    d["L"] = d.E * (d.fp - 1)
    d["C"] = d.P - d.E * d.fp
    d["D"] = d.P - d.E
    out["quillota220_subsistema"] = qq.sd.value_counts().to_dict()
    nsub = d.groupby(["dia", "hora"]).sd.nunique()
    out["horas"] = {"total": int(nsub.size), "subsistemas_por_hora": nsub.value_counts().sort_index().to_dict()}
    out["C_abs"] = {"mismo_subsistema_que_quillota": q(d.C.abs()[d.sd == d.sd_ref]),
                    "otro_subsistema": q(d.C.abs()[(d.sd != d.sd_ref) & d.sd.notna()])}
    out["horas_precio_quillota_cero"] = int((qq.P == 0).sum())
    d.drop(columns=["mes"]).to_csv(OUT / "piloto_201712_hora.csv.gz", index=False)
    return out


if __name__ == "__main__":
    res = {"fecha_ejecucion": pd.Timestamp.now().isoformat(timespec="seconds"), "referencia": REF,
           "definiciones": {"E": "P de Quillota 220", "L": "E*(FP-1)", "C": "P-E*FP", "D": "P-E=L+C"},
           "2024-07-15": piloto_2024(), "2017-12": piloto_2017()}
    (RES / "piloto_conciliacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str))
    print(json.dumps(res, ensure_ascii=False, indent=1, default=str)[:6000])

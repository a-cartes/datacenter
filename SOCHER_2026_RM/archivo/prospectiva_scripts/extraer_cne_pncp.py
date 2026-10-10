"""Extrae a formatos tabulares el Informe Técnico Definitivo de Precio de Nudo de Corto Plazo (CNE, julio 2026).

Entradas (fuentes/originales/):
  CNE_02-Calcula_ITD_02-2026.xlsx : salidas del modelo OSE2000 de la CNE por barra, mes y bloque
  CNE_ITD-PNCP-Jul-2026.xlsx      : cuadros del informe (demanda, costos variables, combustibles, obras...)
Salidas (extraidos/cne_pncp_2026_2/):
  cmg_barra_mes_bloque.parquet     BarNom, anio, mes, bloque, cmg_usd_mwh   (esperado sobre hidrologías)
  energia_barra_mes_bloque.parquet BarNom, anio, mes, bloque, energia_gwh
  demanda_punta_barra.csv          volcado de la hoja 'Demanda Punta' (tabla dinámica filtrada a un año)
  barras_clasificacion.csv         BarNom, sistema (SIC/SING)
  bloques_horas.csv                correspondencia hora -> bloque por mes y tipo de día (Tabla 2 del informe)
  tablas_informe/<hoja>.csv        volcado literal de cada hoja de cuadros (sin reinterpretar unidades)

Los valores son BLOQUES REPRESENTATIVOS (24 por mes: 12 día hábil + 12 día inhábil, 2 horas cada uno),
no series horarias. Identificador de barra: nombre OSE2000 de la CNE ('BarNom'), distinto de los códigos
de barra del Coordinador usados en el panel histórico.
"""
import csv
import re
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fuentes" / "originales"
OUT = ROOT / "extraidos" / "cne_pncp_2026_2"


def volcar(ws, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            row = list(row)
            while row and row[-1] is None:
                row.pop()
            if row:
                w.writerow(["" if v is None else v for v in row])


def pivote(ws, valor):
    """Tabla dinámica con filas BarNom y columnas (AñoCld, MesCld, IBlo)."""
    rows = list(ws.iter_rows(values_only=True))
    r = next(i for i, row in enumerate(rows) if "BarNom" in row)
    c = rows[r].index("BarNom")
    anio, mes, blo = rows[r - 2], rows[r - 1], rows[r]
    cols = [(j, int(anio[j]), int(mes[j]), int(blo[j])) for j in range(c + 1, len(blo))
            if isinstance(blo[j], (int, float)) and isinstance(anio[j], (int, float)) and isinstance(mes[j], (int, float))]
    rec = []
    for row in rows[r + 1:]:
        nom = row[c]
        if not isinstance(nom, str) or nom.strip().lower().startswith("total"):
            continue
        for j, a, m, b in cols:
            v = row[j]
            if isinstance(v, (int, float)):
                rec.append((nom, a, m, b, float(v)))
    return pd.DataFrame(rec, columns=["BarNom", "anio", "mes", "bloque", valor])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(SRC / "CNE_02-Calcula_ITD_02-2026.xlsx", read_only=True, data_only=True)
    cmg = pivote(wb["CMg PNudo"], "cmg_usd_mwh")
    ene = pivote(wb["Energia PNudo"], "energia_gwh")
    cmg.to_parquet(OUT / "cmg_barra_mes_bloque.parquet", index=False)
    ene.to_parquet(OUT / "energia_barra_mes_bloque.parquet", index=False)
    volcar(wb["Demanda Punta"], OUT / "demanda_punta_barra.csv")
    volcar(wb["Bloques y Fijación"], OUT / "bloques_y_fijacion.csv")
    bc = [r for r in wb["Barras Clasificacion"].iter_rows(min_row=2, max_col=2, values_only=True) if r[0]]
    pd.DataFrame(bc, columns=["BarNom", "sistema"]).to_csv(OUT / "barras_clasificacion.csv", index=False)
    for d, n in ((cmg, "cmg"), (ene, "energia")):
        print(n, len(d), "filas;", d.BarNom.nunique(), "barras;", d.anio.min(), "-", d.anio.max(),
              "; bloques", sorted(d.bloque.unique())[:3], "...", d.bloque.max())
    wb2 = openpyxl.load_workbook(SRC / "CNE_ITD-PNCP-Jul-2026.xlsx", read_only=True, data_only=True)
    for ws in wb2.worksheets:
        volcar(ws, OUT / "tablas_informe" / (re.sub(r"[^\w\-]+", "_", ws.title) + ".csv"))
    print("hojas de cuadros:", len(wb2.worksheets))


if __name__ == "__main__":
    main()

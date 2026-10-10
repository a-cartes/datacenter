"""Extrae los anexos del Informe Definitivo de Previsión de Demanda Eléctrica 2025-2045 (CNE, febrero 2026).

Entrada: fuentes/originales/CNE_Anexos-Informe-Definitivo-de-Prevision-de-Demanda-Electrica-2025-2045.xlsx
Salidas (extraidos/cne_prevision_demanda_2025_2045/), todas en MWh mensuales (unidad declarada en la portada):
  clientes_libres_mensual.parquet     Anexo 2: cliente, rut, region, sector, punto_conexion, tension, anio, mes, mwh, mwh_ee
                                      (mwh_ee = hoja 'Anexo 2 EE', que incluye eficiencia energética)
  clientes_libres_anual.csv           suma anual por fila de cliente-punto de conexión
  regulados_se_primaria_mensual.parquet  Anexo 1: distribuidora, punto_conexion, tension, anio, mes, mwh
  regulados_ventas_mensual.parquet    Anexo 4 (ventas de clientes regulados)
Cada fila conserva 'fila_excel' para volver al original. No se corrigen nombres, RUT ni regiones.
"""
from pathlib import Path

import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fuentes" / "originales" / "CNE_Anexos-Informe-Definitivo-de-Prevision-de-Demanda-Electrica-2025-2045.xlsx"
OUT = ROOT / "extraidos" / "cne_prevision_demanda_2025_2045"
MES = {m: i + 1 for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                       "septiembre", "octubre", "noviembre", "diciembre"])}


def largo(ws, ids):
    rows = list(ws.iter_rows(values_only=True))
    h = next(i for i, r in enumerate(rows) if any(isinstance(v, str) and v.strip().lower().startswith("enero") for v in r))
    anio_row, mes_row = rows[h - 1], rows[h]
    c0 = next(j for j, v in enumerate(mes_row) if isinstance(v, str) and v.strip().lower().startswith("enero"))
    k0 = c0 - len(ids)
    cols, anio = [], None
    for j in range(c0, len(mes_row)):
        m = mes_row[j]
        if not isinstance(m, str) or m.strip().split()[0].lower() not in MES:
            continue
        a = anio_row[j] if j < len(anio_row) else None
        if isinstance(a, (int, float)):
            anio = int(a)
        elif len(m.split()) > 1 and m.split()[1].isdigit():
            anio = int(m.split()[1])
        cols.append((j, anio, MES[m.strip().split()[0].lower()]))
    rec = []
    for i, r in enumerate(rows[h + 1:], start=h + 2):
        if r[k0] is None or str(r[k0]).strip().lower().startswith("total"):
            continue
        base = [i] + [r[k0 + k] for k in range(len(ids))]
        for j, a, m in cols:
            v = r[j] if j < len(r) else None
            if isinstance(v, (int, float)):
                rec.append(base + [a, m, float(v)])
    return pd.DataFrame(rec, columns=["fila_excel"] + ids + ["anio", "mes", "mwh"])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.load_workbook(SRC, read_only=True, data_only=True)
    ids = ["cliente", "rut", "region", "sector", "punto_conexion", "tension"]
    a2 = largo(wb["Anexo 2"], ids)
    ee = largo(wb["Anexo 2 EE"], ids).rename(columns={"mwh": "mwh_ee"})
    lib = a2.merge(ee[["fila_excel", "anio", "mes", "mwh_ee"]], on=["fila_excel", "anio", "mes"], how="left")
    for c in ids:
        lib[c] = lib[c].astype(str)
    lib.to_parquet(OUT / "clientes_libres_mensual.parquet", index=False)
    (lib.groupby(["fila_excel"] + ids + ["anio"], as_index=False)[["mwh", "mwh_ee"]].sum()
        .to_csv(OUT / "clientes_libres_anual.csv", index=False))
    print("Anexo 2:", lib.fila_excel.nunique(), "filas cliente-punto;", lib.anio.min(), "-", lib.anio.max(),
          "; TWh 2030:", round(lib[lib.anio == 2030].mwh.sum() / 1e6, 2))
    for hoja, nom in (("Anexo 1", "regulados_se_primaria_mensual"), ("Anexo 4", "regulados_ventas_mensual")):
        d = largo(wb[hoja], ["distribuidora", "punto_conexion", "tension"])
        for c in ("distribuidora", "punto_conexion", "tension"):
            d[c] = d[c].astype(str)
        d.to_parquet(OUT / f"{nom}.parquet", index=False)
        print(hoja, d.fila_excel.nunique(), "filas;", d.anio.min(), "-", d.anio.max(),
              "; TWh 2030:", round(d[d.anio == 2030].mwh.sum() / 1e6, 2))


if __name__ == "__main__":
    main()

"""Extrae precios horarios por barra y factores de penalización por tramo de los libros
mensuales DEF del Coordinador (enero 2017 - 14 julio 2024), sin ejecutar macros.

Entrada: fuentes/precios/manifiesto_originales_historicos.csv y los originales enlazados.
Salida:  datos/precios_hist/AAAAMM.parquet  (una fila por barra x día x etiqueta de hora)
         datos/precios_hist/diagnostico_AAAAMM.json
Columnas: mes, dia, hora (etiqueta original 1-25), barra (nombre limpio), barra_original,
          P (mills/kWh = USD/MWh, valor publicado), fp (factor del tramo asignado),
          tramo, archivo, sha256.
No se rellenan faltantes: un precio vacío queda NaN; un cero publicado queda 0.

La asignación de horas a tramos de factores se elige en cada mes entre candidatos,
minimizando la dispersión de log(P/FP) entre barras de la misma hora (dentro de una
hora, las barras de un mismo subsistema comparten lambda). El ajuste queda registrado.

Uso: python scripts/extraer_precios_historicos.py [AAAAMM ...]   (por defecto, todos)
"""
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
import json
from pathlib import Path
import re
import sys
from zipfile import ZipFile

import numpy as np
import openpyxl
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MAN = ROOT / "fuentes" / "precios" / "manifiesto_originales_historicos.csv"
OUT = ROOT / "datos" / "precios_hist"
REF = "QUILLOTA______220"

# Elección de versión cuando hay más de un contenido en el mes (ver REGISTRO_DECISIONES.md)
ELECCION = {
    "201711": "cmg1711_def.zip",   # SEN definitivo; cmg1711.zip (SIC) se conserva para contraste
    "201810": "cmg1810_def.zip",   # DEF; el PRE se conserva y no se mezcla
    "202405": "cmg2405_def.zip",   # cmg2405_def-2.zip truncado; el de 1.489 bytes es HTML 416
}


def clean(b):
    return re.sub(r"\s+", "", str(b)) if b is not None else None


def open_book(path):
    """Devuelve (nombre, bytes) del libro cmgAAMM*.xlsm dentro de la ruta (zip, zip anidado o xlsm)."""
    p = ROOT / path
    if p.suffix.lower() == ".xlsm":
        return p.name, p.read_bytes()
    if p.suffix.lower() == ".rar":  # RAR v4: lectura con bsdtar (libarchive) a memoria; el original no se modifica
        import subprocess
        names = subprocess.run(["bsdtar", "-tf", str(p)], capture_output=True, text=True).stdout.split()
        n = next(x for x in names if re.match(r"cmg\d{4}.*\.xlsm$", Path(x).name, re.I))
        data = subprocess.run(["bsdtar", "-xOf", str(p), n], capture_output=True, check=True).stdout
        if not data:
            raise ValueError("extracción RAR vacía")
        return n, data
    z = ZipFile(p)
    for n in z.namelist():
        nm = Path(n).name
        if re.match(r"cmg\d{4}.*\.xlsm$", nm, re.I):
            return n, z.read(n)
    for n in z.namelist():
        if n.lower().endswith(".zip") and Path(n).name.lower().startswith("cmg"):
            z2 = ZipFile(BytesIO(z.read(n)))
            for n2 in z2.namelist():
                if re.match(r"cmg\d{4}.*\.xlsm$", Path(n2).name, re.I):
                    return n + ":" + n2, z2.read(n2)
    raise FileNotFoundError(path)


def rows(wb, name):
    ws = wb[name]
    ws.reset_dimensions()
    return ws.iter_rows(values_only=True)


def read_prices(wb):
    if "CMG Barras dolares" in wb.sheetnames:  # 2017: ancho, barras en columnas
        it = list(rows(wb, "CMG Barras dolares"))
        hdr = it[8]
        cols = [(j, hdr[j]) for j in range(3, len(hdr)) if hdr[j]]
        rec = []
        for r in it[10:]:
            if not r or r[0] is None or not re.match(r"^\d{6}$", str(r[0])):
                continue
            for j, b in cols:
                v = r[j] if j < len(r) else None
                rec.append((int(r[1]), int(r[2]), b, v))
        df = pd.DataFrame(rec, columns=["dia", "hora", "barra_original", "P"])
        unit = str(it[5][3]) if len(it[5]) > 3 else ""
    else:  # 2018+: largo, posiblemente en varios bloques de columnas lado a lado
        it = rows(wb, "CMG Barras")
        hdr = next(it)
        starts = [j for j, h in enumerate(hdr) if h == "Mes"]
        blocks = []
        for s in starts:
            ix = {}
            for j in range(s, min(s + 9, len(hdr))):
                if hdr[j] and hdr[j] not in ix:
                    ix[hdr[j]] = j
            pc = [h for h in ix if "mills" in str(h)][0]
            blocks.append((ix["Día"], ix["Hora"], ix["Barra"], ix[pc]))
        rec = [(r[a], r[b], r[c], r[d]) for r in it if r for a, b, c, d in blocks
               if c < len(r) and r[c] is not None and r[a] is not None]
        df = pd.DataFrame(rec, columns=["dia", "hora", "barra_original", "P"])
        unit = f"{pc}; bloques={len(blocks)}"
    df["P"] = pd.to_numeric(df.P, errors="coerce")
    df["dia"] = df.dia.astype(int)
    df["hora"] = df.hora.astype(int)
    df["barra"] = df.barra_original.map(clean)
    return df, unit


def read_fp(wb):
    it = list(rows(wb, "Factores de Penalización"))
    dates, lab = it[8], it[9]
    cur, dcol = None, {}
    for j in range(2, len(lab)):
        if j < len(dates) and dates[j] is not None:
            cur = pd.Timestamp(dates[j]).day
        if lab[j] is not None:
            dcol[j] = (cur, int(lab[j]))
    rec = []
    for r in it[10:]:
        if not r or r[0] is None:
            continue
        b = clean(r[0])
        for j in range(2, len(r)):
            if r[j] is not None and j in dcol:
                rec.append((b, dcol[j][0], dcol[j][1], r[j]))
    F = pd.DataFrame(rec, columns=["barra", "dia", "slot", "fp"])
    F["fp"] = pd.to_numeric(F.fp, errors="coerce")
    return F


def tramo_map(P, F):
    """Elige el mapeo hora->slot. Si solo hay 3 slots, busca cortes; si hay >=24, slot=hora."""
    nslot = F.groupby("dia").slot.nunique().max()
    ev = P[(P.P > 5) & P.P.notna()]
    if nslot >= 24:
        cands = {"hora": lambda h: h}
    else:
        cands = {f"1-{a}|{a+1}-{b}|{b+1}-": (lambda a, b: lambda h: np.where(h <= a, 1, np.where(h <= b, 2, 3)))(a, b)
                 for a in range(5, 12) for b in range(15, 22)}
    res = []
    for k, f in cands.items():
        x = ev.assign(slot=f(ev.hora.values)).merge(F, on=["barra", "dia", "slot"], how="inner")
        l = np.log(x.P / x.fp)
        # dispersión dentro de la hora alrededor de la moda aproximada (mediana): robusta a subsistemas
        dev = (l - l.groupby([x.dia, x.hora]).transform("median")).abs()
        res.append({"mapeo": k, "share_dev_menor_0_5pct": float((dev < 0.005).mean()),
                    "n": int(len(x))})
    res.sort(key=lambda r: -r["share_dev_menor_0_5pct"])
    return res[0]["mapeo"], cands[res[0]["mapeo"]], res[:3], int(nslot)


def process(row):
    try:
        return _process(row)
    except Exception as e:  # se registra y se continúa con los demás meses
        d = {"mes": row["mes"], "archivo": row["archivo_proyecto"], "error": repr(e)}
        OUT.mkdir(parents=True, exist_ok=True)
        (OUT / f"diagnostico_{row['mes']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
        return d


def _process(row):
    mes, path, h = row["mes"], row["archivo_proyecto"], row["sha256"]
    name, data = open_book(path)
    wb = openpyxl.load_workbook(BytesIO(data), read_only=True, data_only=True, keep_links=False)
    P, unit = read_prices(wb)
    F = read_fp(wb)
    wb.close()
    k, f, top, nslot = tramo_map(P, F)
    P["slot"] = f(P.hora.values)
    P = P.merge(F.rename(columns={"fp": "fp"}), on=["barra", "dia", "slot"], how="left")
    P.insert(0, "mes", int(mes))
    P["archivo"] = path + "::" + name
    P["sha256"] = h
    exact = P.duplicated(["barra", "dia", "hora", "P", "fp"])
    n_exact = int(exact.sum())
    P = P[~exact]
    dup = P.duplicated(["barra", "dia", "hora"]).sum()  # duplicados con valores distintos: se conservan y se informan
    q = P[P.barra == REF]
    diag = {
        "mes": mes, "archivo": path, "libro": name, "sha256": h, "unidad": unit,
        "filas": int(len(P)), "barras": int(P.barra.nunique()), "dias": int(P.dia.nunique()),
        "etiquetas_hora": sorted(P.hora.unique().tolist()), "dia_hora_unicos": int(P[["dia", "hora"]].drop_duplicates().shape[0]),
        "precios_vacios": int(P.P.isna().sum()), "precios_cero": int((P.P == 0).sum()),
        "precios_negativos": int((P.P < 0).sum()), "duplicados_identicos_eliminados": n_exact, "claves_duplicadas_valores_distintos": int(dup),
        "barras_con_salto_linea_en_nombre": int((P.barra_original.astype(str) != P.barra).groupby(P.barra).any().sum()),
        "slots_factor_por_dia": nslot, "mapeo_tramos": k, "ajuste_mapeos_top3": top,
        "barra_horas_sin_factor": int(P.fp.isna().sum()),
        "quillota220_horas": int(len(q)), "quillota220_fp_min_max": [float(q.fp.min()), float(q.fp.max())] if len(q) else None,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    P.drop(columns=["slot"]).to_parquet(OUT / f"{mes}.parquet", index=False)
    (OUT / f"diagnostico_{mes}.json").write_text(json.dumps(diag, ensure_ascii=False, indent=1, default=str))
    return diag


def selected():
    m = pd.read_csv(MAN, dtype=str)
    m = m[m.archivo_proyecto.str.contains(r"/cmg_?\d{4}[^/]*\.(?:zip|xlsm|rar)$", regex=True)]
    m = m[~m.archivo_proyecto.str.contains("Centrales|Registro", regex=True)]
    out = []
    for mes, g in m.groupby("mes"):
        if mes in ELECCION:
            g = g[g.archivo_proyecto.str.endswith("/" + ELECCION[mes])]
        g = g[~g.archivo_proyecto.str.contains("_pre", case=False)]
        if len(g) != 1:
            raise ValueError(f"{mes}: {len(g)} candidatos {g.archivo_proyecto.tolist()}")
        out.append(g.iloc[0].to_dict())
    return out


if __name__ == "__main__":
    todo = selected()
    if len(sys.argv) > 1:
        todo = [r for r in todo if r["mes"] in sys.argv[1:]]
    with ProcessPoolExecutor(max_workers=6) as ex:
        for d in ex.map(process, todo):
            if "error" in d:
                print(d["mes"], "ERROR", d["error"], flush=True)
                continue
            print(d["mes"], d["barras"], d["dias"], d["dia_hora_unicos"], "vacios", d["precios_vacios"],
                  "dupId", d["duplicados_identicos_eliminados"], "dupDist", d["claves_duplicadas_valores_distintos"], d["mapeo_tramos"], d["ajuste_mapeos_top3"][0]["share_dev_menor_0_5pct"],
                  "sinFP", d["barra_horas_sin_factor"], "Q", d["quillota220_horas"], flush=True)

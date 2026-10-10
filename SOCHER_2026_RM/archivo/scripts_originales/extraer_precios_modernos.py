"""Precios del régimen nuevo (desde 15/07/2024): TSV mensuales REAL-DEF de 15 minutos -> barra x hora.

Convención verificada (ver resultados/continuidad_precios.json): en el régimen histórico,
el precio horario publicado con etiqueta h es el promedio de los cuatro cuartos con HORA=h
del CSV oficial de 15 minutos; h=1 corresponde a 00:00-01:00. En el TSV nuevo HRA=0 es
00:00-01:00. Por eso: hora = HRA + 1. No se completan cuartos faltantes: P es la media de
los cuartos disponibles y n_cuartos queda registrado (precio horario completo si =4).
Salida: datos/precios_mod/AAAAMM.parquet con mes, dia, hora, barra, id_info, barra_info, P, n_cuartos.
"""
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import sys

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "fuentes" / "precios" / "originales" / "moderno"
OUT = ROOT / "datos" / "precios_mod"


def process(f):
    meta = json.loads(f.with_suffix("").with_suffix(".json").read_text())
    cols = None
    parts = []
    for ch in pd.read_csv(f, sep="\t", chunksize=2_000_000, dtype={"ID_INFO": "Int64"}):
        cols = list(ch.columns)
        pc = [c for c in ch.columns if "USD" in c or "mills" in c][0]
        ch = ch.rename(columns={pc: "P15", "BARRA_TRANSF": "barra", "ID_INFO": "id_info", "BARRA_INFO": "barra_info"})
        ch["P15"] = pd.to_numeric(ch.P15, errors="coerce")
        ch["fecha"] = pd.to_datetime(ch.FECHA)
        parts.append(ch[["barra", "id_info", "barra_info", "fecha", "HRA", "MIN", "P15", "VERSION"]])
    d = pd.concat(parts)
    dup = int(d.duplicated(["barra", "fecha", "HRA", "MIN"]).sum())
    g = d.groupby(["barra", "fecha", "HRA"], as_index=False).agg(
        P=("P15", "mean"), n_cuartos=("P15", "count"), id_info=("id_info", "first"), barra_info=("barra_info", "first"))
    g["hora"] = g.HRA + 1
    g["dia"] = g.fecha.dt.day
    mes = int(f.name[:6])
    g.insert(0, "mes", mes)
    g["archivo"] = str(f.relative_to(ROOT))
    g["sha256"] = meta.get("sha256_descomprimido")
    OUT.mkdir(parents=True, exist_ok=True)
    g.drop(columns=["HRA"]).to_parquet(OUT / f"{mes}.parquet", index=False)
    diag = {"mes": mes, "columnas": cols, "filas_15min": int(len(d)), "barras": int(d.barra.nunique()),
            "dias": sorted(d.fecha.dt.day.unique().tolist()), "HRA": sorted(d.HRA.unique().tolist()),
            "minutos": sorted(d.MIN.unique().tolist()), "versiones": d.VERSION.value_counts().to_dict(),
            "duplicados": dup, "precio_vacio": int(d.P15.isna().sum()),
            "horas_incompletas": int((g.n_cuartos < 4).sum()), "verificado_etag": meta.get("verificado_etag")}
    (OUT / f"diagnostico_{mes}.json").write_text(json.dumps(diag, ensure_ascii=False, indent=1, default=str))
    return diag


if __name__ == "__main__":
    files = sorted(SRC.glob("*_REAL-DEF.tsv.gz"))
    if len(sys.argv) > 1:
        files = [f for f in files if f.name[:6] in sys.argv[1:]]
    with ProcessPoolExecutor(3) as ex:
        for d in ex.map(process, files):
            print(d["mes"], d["barras"], len(d["dias"]), d["HRA"][:2], d["HRA"][-2:], "dup", d["duplicados"],
                  "vac", d["precio_vacio"], "inc", d["horas_incompletas"], d["versiones"], flush=True)

"""Agrega HT1+HT2 por etiquetas completas y compara el tramo 2024 ya auditado."""
from pathlib import Path
import hashlib
import json

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
SOCKETS = [f"LSCANTRS_110_HT{i}_EDG" for i in (1, 2, 3)]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    source = BASE / "tablas/mediciones_candidatos_15min.parquet"
    columns = ["IDSOCKET", "DATETIME", "UTCDATETIME", "etiqueta_utc", "fecha_local", "mes_local",
               "energia_D_kwh", "energia_R_kwh", "offset_local_min", "estado_polaridad"]
    d = pd.read_parquet(source, columns=columns, filters=[("IDSOCKET", "in", SOCKETS)])
    assert not d.duplicated(["IDSOCKET", "etiqueta_utc"]).any()
    previous = ROOT / "SOCHER_2026_v3/consumo/las_canteras_transformadores_15min_2024.csv.gz"
    old = pd.read_csv(previous, usecols=["IDSOCKET", "UTCDATETIME", "energia_D_kwh", "energia_R_kwh"])
    observed = d[d.mes_local.str.startswith("2024")].set_index(["IDSOCKET", "UTCDATETIME"]).sort_index()
    old = old.set_index(["IDSOCKET", "UTCDATETIME"]).sort_index()
    assert observed.index.equals(old.index) and len(old) == 67384
    errors = {}
    for c in ["energia_D_kwh", "energia_R_kwh"]:
        errors[c] = float(np.max(np.abs(observed[c] - old[c])))
        np.testing.assert_allclose(observed[c], old[c], rtol=1e-13, atol=1e-10)
    pair = d[d.IDSOCKET.isin(SOCKETS[:2])].copy()
    pair["pano"] = pair.IDSOCKET.str.extract(r"_(HT[12])_")[0]
    wide = pair.pivot(index="etiqueta_utc", columns="pano", values="energia_D_kwh")
    wide["D_HT1_HT2_kwh"] = wide[["HT1", "HT2"]].sum(axis=1, min_count=2)
    reverse = pair.pivot(index="etiqueta_utc", columns="pano", values="energia_R_kwh")
    wide["R_HT1_HT2_kwh"] = reverse[["HT1", "HT2"]].sum(axis=1, min_count=2)
    times = pair.drop_duplicates("etiqueta_utc").set_index("etiqueta_utc")[["DATETIME", "fecha_local", "offset_local_min"]]
    assert pair.groupby("etiqueta_utc").DATETIME.nunique().eq(1).all()
    wide = wide.join(times)
    wide["hora_utc_etiqueta"] = wide.index.floor("h")
    wide["minuto"] = wide.index.minute
    g = wide.groupby("hora_utc_etiqueta")
    hourly = g.agg(n_intervalos_pares_validos=("D_HT1_HT2_kwh", "count"),
                   energia_D_HT1_HT2_kwh=("D_HT1_HT2_kwh", lambda s: s.sum(min_count=4)),
                   energia_R_HT1_HT2_kwh=("R_HT1_HT2_kwh", lambda s: s.sum(min_count=4)),
                   primera_etiqueta_local=("DATETIME", "min"), ultima_etiqueta_local=("DATETIME", "max"),
                   fecha_local=("fecha_local", "first"), offset_local_min=("offset_local_min", "first"))
    hourly["cuatro_etiquetas_correctas"] = g.minuto.agg(lambda s: tuple(sorted(s)) == (0, 15, 30, 45))
    hourly["completo_por_etiquetas"] = hourly.n_intervalos_pares_validos.eq(4) & hourly.cuatro_etiquetas_correctas
    for col in ["energia_D_HT1_HT2_kwh", "energia_R_HT1_HT2_kwh"]:
        hourly[col] = hourly[col].where(hourly.completo_por_etiquetas)
    hourly["retiro_D_HT1_HT2_mw_por_etiquetas"] = hourly.energia_D_HT1_HT2_kwh / 1000
    hourly["canal_R_HT1_HT2_mw_por_etiquetas"] = hourly.energia_R_HT1_HT2_kwh / 1000
    hourly["centro_id_candidato"] = "EDGE_COLINA"
    hourly["HT3_incluido"] = False
    hourly["representa_consumo_total_campus"] = False
    hourly["enlace_precio_habilitado"] = False
    hourly["inicio_fin_fisico_acreditado"] = False
    hourly["vigencia_configuracion_2023_posterior_validada"] = False
    hourly = hourly.reset_index()
    hourly.to_parquet(BASE / "tablas/carga_HT1_HT2_hora_etiqueta.parquet", index=False, compression="zstd")
    hourly.to_csv(BASE / "tablas/carga_HT1_HT2_hora_etiqueta.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    yearly = d.copy()
    yearly["anio"] = yearly.fecha_local.str[:4]
    summary = yearly.groupby(["IDSOCKET", "anio"]).agg(registros=("etiqueta_utc", "size"),
        desde_local=("DATETIME", "min"), hasta_local=("DATETIME", "max"),
        D_kwh=("energia_D_kwh", "sum"), R_kwh=("energia_R_kwh", "sum"),
        intervalos_D_positivos=("energia_D_kwh", lambda x: x.gt(0).sum()),
        intervalos_R_positivos=("energia_R_kwh", lambda x: x.gt(0).sum())).reset_index()
    summary.to_csv(BASE / "tablas/resumen_transformadores_por_anio.csv", index=False)
    catalogue = []
    for p in sorted((BASE / "tablas").glob("*.parquet")):
        file = pq.ParquetFile(p)
        catalogue.append({"archivo": str(p.relative_to(BASE)), "filas": file.metadata.num_rows,
                          "columnas": len(file.schema_arrow.names), "bytes": p.stat().st_size, "sha256": sha(p)})
    report = {"fuente": str(source.relative_to(BASE)), "sha256_fuente": sha(source),
        "horas": len(hourly), "horas_incompletas": int((~hourly.completo_por_etiquetas).sum()),
        "dias_locales": hourly.fecha_local.nunique(), "desde_local": hourly.primera_etiqueta_local.min(),
        "hasta_local": hourly.ultima_etiqueta_local.max(), "mediciones_HT1_HT2_HT3": len(d),
        "comparacion_2024": {"filas": len(old), "errores_max_kwh": errors, "sha256_extracto_v3": sha(previous)},
        "HT2_R_positivo_intervalos": int(d.loc[d.IDSOCKET.eq(SOCKETS[1]), "energia_R_kwh"].gt(0).sum()),
        "energia_D_HT1_HT2_kwh": float(hourly.energia_D_HT1_HT2_kwh.sum()),
        "energia_R_HT1_HT2_kwh": float(hourly.energia_R_HT1_HT2_kwh.sum()),
        "no_incluye_HT3_ni_lineas": True, "no_convierte_fecha_presencia_en_tratamiento": True,
        "no_acredita_carga_total_campus": True, "catalogo_tablas": catalogue}
    if hourly.completo_por_etiquetas.all():
        np.testing.assert_allclose(hourly.energia_D_HT1_HT2_kwh.sum(), pair.energia_D_kwh.sum(), rtol=1e-12, atol=1e-7)
    (BASE / "verificacion_carga_horaria.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "catalogo_tablas"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

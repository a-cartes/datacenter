#!/usr/bin/env python3
"""Prueba controlada del verificador; usa dos filas sintéticas sólo temporales.

No altera los datos de investigación. Comprueba que cambios de precio, identidad
y nulidad se detecten aunque se actualicen los hashes de los CSV alterados.
"""
from __future__ import annotations

from contextlib import redirect_stdout
import gzip
import io
import json
from pathlib import Path
import tempfile

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

import construir_entrega as app


def create_fixture(out):
    rows = [{name: None for name, _, _ in app.FIELDS} for _ in range(2)]
    rows[0].update(fecha="2020-01-01", anio=2020, mes="2020-01", regimen_precio=app.HIST,
                   barra_cmg="PRUEBA_A", barra_cmg_original="PRUEBA_A", barra_mes_id="H|2020-01|PRUEBA_A",
                   hora_etiqueta_historica=1, precio_usd_mwh=0.0, version_fuente="DEF", fuente_id="sintetica_temporal")
    rows[1].update(fecha="2026-09-01", anio=2026, mes="2026-09", regimen_precio=app.MOD,
                   barra_cmg="PRUEBA_B", barra_cmg_original="PRUEBA_B", barra_mes_id="M|2026-09|1|PRUEBA_B",
                   id_info_fuente="1", hora_fuente_moderna=0, precio_usd_mwh=-12.3456789,
                   precio_usd_mwh_media_intervalos=-12.3456789, precio_clp_kwh=-10.3456789,
                   n_intervalos=4, minutos_observados="0,15,30,45", hora_completa_4_intervalos=True,
                   version_fuente="REAL-DEF", fuente_id="sintetica_temporal")
    table = pa.Table.from_pylist(rows, schema=app.SCHEMA)
    pq.write_table(table, out / (app.STEM + ".parquet"))
    return table.to_pandas(types_mapper=pd.ArrowDtype)


def write_csv_and_manifest(out, frame):
    frame.to_csv(out / (app.STEM + ".csv"), index=False, lineterminator="\n")
    (out / "por_anio").mkdir(exist_ok=True)
    for year, data in frame.groupby("anio"):
        data.to_csv(out / "por_anio" / f"Dataset_precios_barra_hora_{year}.csv", index=False, lineterminator="\n")
    with gzip.open(out / (app.STEM + ".csv.gz"), "wb") as f:
        f.write((out / (app.STEM + ".csv")).read_bytes())
    manifest = {"filas_precios_DEF": len(frame), "archivos": [
        dict(archivo=str(p.relative_to(out)), bytes=p.stat().st_size, sha256=app.sha(p))
        for p in sorted(out.rglob("*")) if p.is_file() and p.suffix in {".csv", ".gz", ".parquet"}]}
    (out / "Manifiesto_entrega.json").write_text(json.dumps(manifest))


def main():
    results = []
    tests = [("iguales_incluye_cero_negativo_y_nulos", None, None, 0, None),
             ("precio_alterado", "precio_usd_mwh", 0.01, 1, "Diferencia numérica"),
             ("identidad_alterada", "barra_cmg", "ALTERADO", 1, "Valores diferentes"),
             ("nulo_alterado", "id_info_fuente", "999", 1, "Máscara nula diferente")]
    with tempfile.TemporaryDirectory(prefix="socher_verificacion_") as temp:
        for name, field, value, expected, message in tests:
            out = Path(temp) / name; out.mkdir()
            frame = create_fixture(out)
            if field:
                frame.loc[0, field] = value
            write_csv_and_manifest(out, frame)
            with redirect_stdout(io.StringIO()):
                status = app.verify(out)
            report = json.loads((out / "Verificacion_entrega.json").read_text())
            assert status == expected, (name, report)
            if message:
                assert any(message in e for e in report["errores"]), (name, report)
            results.append(dict(prueba=name, resultado="OK", error_detectado=report["errores"]))
    print(json.dumps({"estado": "OK", "pruebas": results, "datos_de_investigacion_alterados": False}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

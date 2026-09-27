"""Read-only source reconstruction for the three exact ODATA ST01 sockets.

Run from any directory with the project .venv Python. Does not estimate prices,
date entry from readings, sum points, or infer historical polarity from a current
catalogue. DATETIME and UTCDATETIME are retained as printed labels.
"""
from pathlib import Path
import csv
import hashlib
import json
import pandas as pd
import openpyxl

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SOCKETS = ["LAMPA_220_JT5_ODT", "LAMPA_023_ET5_ODT", "NUELAMPA_220_J9_ODT"]
SOURCES = ROOT / "SOCHER_2026_v7_2020_2026/mediciones/extractos"
CATALOGUE = ROOT / "SOCHER_2026_v3/mapeo/CEN_SOCKET_HABILITADO_20260925.xlsx"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sources, monthly, daily = [], [], []
    for path in sorted(SOURCES.glob("medidores_candidatos_*.csv.gz")):
        manifest_path = path.with_name(path.name.replace(".csv.gz", "_manifest.json"))
        manifest = json.loads(manifest_path.read_text())
        digest = sha(path)
        assert digest == manifest["sha256_extracto"], path
        data = pd.read_csv(path, dtype=str, keep_default_na=False)
        month = f"{manifest['anio']:04d}-{manifest['mes']:02d}"
        sources.append({"file": str(path.relative_to(ROOT)), "sha256": digest,
                        "manifest_sha256": sha(manifest_path)})
        for socket in SOCKETS:
            d = data[data.IDSOCKET.eq(socket)].copy()
            assert socket in manifest["sockets_buscados"]
            assert len(d) == manifest["filas_por_socket"].get(socket, 0)
            m = {"mes_archivo": month, "IDSOCKET": socket, "registros": len(d),
                 "unidad_canales": "kWh según cabecera fuente",
                 "estado": "OBSERVADO" if len(d) else "SIN_REGISTRO_NO_EQUIVALE_A_CERO"}
            if len(d):
                for col in ["kWhD", "kWhR"]:
                    # The archived CSV uses comma decimals inside quoted fields.
                    # Do not silently coerce those valid energies to null.
                    raw = d[col].str.replace(",", ".", regex=False)
                    d[col] = pd.to_numeric(raw, errors="raise")
                    m[col + "_suma"] = d[col].sum(min_count=1)
                    m[col + "_nulos"] = int(d[col].isna().sum())
                    m[col + "_negativos"] = int(d[col].lt(0).sum())
                m.update({"fecha_primera_etiqueta": d.DATETIME.min(),
                          "fecha_ultima_etiqueta": d.DATETIME.max(),
                          "ID_SOC": ";".join(sorted(d.ID_SOC.unique())),
                          "FLUJO": ";".join(sorted(d.FLUJO.unique())),
                          "duplicados_socket_datetime_utc": int(d.duplicated(["IDSOCKET", "DATETIME", "UTCDATETIME"]).sum())})
                assert m["duplicados_socket_datetime_utc"] == 0
                d["fecha_civil_impresa"] = d.DATETIME.str[:10]
                for date, dd in d.groupby("fecha_civil_impresa", sort=True):
                    daily.append({"mes_archivo": month, "IDSOCKET": socket,
                                  "fecha_civil_impresa": date, "registros": len(dd),
                                  "n_etiquetas_locales": dd.DATETIME.nunique(),
                                  "kWhD_suma": dd.kWhD.sum(min_count=1),
                                  "kWhR_suma": dd.kWhR.sum(min_count=1),
                                  "nulos_D": int(dd.kWhD.isna().sum()),
                                  "nulos_R": int(dd.kWhR.isna().sum())})
            monthly.append(m)
    pd.DataFrame(monthly).to_csv(OUT / "cobertura_canales_odata_mensual.csv", index=False)
    pd.DataFrame(daily).to_csv(OUT / "canales_odata_diarios.csv", index=False)
    wb = openpyxl.load_workbook(CATALOGUE, read_only=True, data_only=True)
    rows = []
    for sheet in wb:
        it = sheet.iter_rows(values_only=True)
        columns = list(next(it))
        for row_number, row in enumerate(it, 2):
            record = dict(zip(columns, row))
            if any(any(term in str(v).upper() for term in ["LAMPA", "ODATA", "BATUCO"]) for v in row):
                record.update({"hoja_catalogo": sheet.title, "fila_excel": row_number,
                               "vigencia_historica_certificada": False})
                rows.append(record)
    wb.close()
    pd.DataFrame(rows).to_csv(OUT / "catalogo_sockets_lampa_odata.csv", index=False)
    # Independent, already-published v7 totals are a reconciliation, not inputs.
    previous = pd.read_csv(ROOT / "SOCHER_2026_v7_2020_2026/mediciones/tablas/cobertura_y_canales_por_mes.csv")
    previous["IDSOCKET"] = previous.IDSOCKET.str.strip()
    check = pd.DataFrame(monthly).merge(previous, left_on=["IDSOCKET", "mes_archivo"], right_on=["IDSOCKET", "mes_local"], validate="one_to_one")
    assert len(check) == len(monthly)
    max_d = float((check.kWhD_suma-check.energia_D_kwh).abs().max())
    max_r = float((check.kWhR_suma-check.energia_R_kwh).abs().max())
    assert max_d < 1e-6 and max_r < 1e-6
    report = {"script_sha256": sha(Path(__file__)), "catalogue_sha256": sha(CATALOGUE),
              "sources": sources, "months": len(sources), "socket_months": len(monthly),
              "rows_observed": sum(r["registros"] for r in monthly),
              "daily_rows": len(daily), "reconciliacion_v7_error_max_D_kWh": max_d,
              "reconciliacion_v7_error_max_R_kWh": max_r,
              "rule": "No sumar sockets ni interpretar primera observación como entrada",
              "outputs": {name: sha(OUT/name) for name in ["cobertura_canales_odata_mensual.csv", "canales_odata_diarios.csv", "catalogo_sockets_lampa_odata.csv"]}}
    (OUT / "verificacion_mediciones.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in {"sources", "outputs"}},ensure_ascii=False))

if __name__ == "__main__":
    main()

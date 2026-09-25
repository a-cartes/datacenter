"""Revisa los archivos exportados y una hora mediante suma decimal independiente."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json

import pandas as pd


BASE = Path(__file__).resolve().parents[1]
paths = [BASE / "tablas/carga_medidor_15min.parquet", BASE / "tablas/carga_campus_hora.parquet",
         BASE / "tablas/carga_medidor_15min.csv.gz", BASE / "controles/cobertura_mediciones_mensual.csv"]
d = pd.read_parquet(paths[0])
h = pd.read_parquet(paths[1])
c = pd.read_csv(paths[2], dtype=str, keep_default_na=False)
for col in ["kWhD", "kWhR", "IDSOCKET", "DATETIME", "UTCDATETIME"]:
    assert c[col].equals(d[col])
hour = h.loc[h.hora_utc_etiqueta.eq(pd.Timestamp("2024-06-25 04:00:00Z"))].iloc[0]
selected = d[d.etiqueta_utc.between(hour.hora_utc_etiqueta, hour.hora_utc_etiqueta + pd.Timedelta(minutes=45))
             & d.incluido_suma_HT1_HT2]
energy = sum(Decimal(x.replace(",", ".")) for x in selected.kWhD)
assert len(selected) == 8
assert abs(float(energy) - hour.energia_HT1_HT2_kwh) < 1e-10
coverage = pd.read_csv(paths[3])
assert coverage.loc[coverage.registros.eq(0), "energia_D_kwh"].isna().all()
assert h.loc[h.fecha_local.eq("2024-09-08")].shape[0] == 23
assert h.hora_utc_etiqueta.dt.tz is not None
assert d.loc[d.pano.eq("HT3"), "retiro_validado_kwh"].isna().all()
assert not d.enlace_precio_habilitado.any() and not h.enlace_precio_habilitado.any()
report = {
    "csv_conserva_campos_originales": True,
    "hora_comprobada": str(hour.hora_utc_etiqueta),
    "energia_8_filas_decimal_kwh": str(energy),
    "energia_horaria_kwh": float(hour.energia_HT1_HT2_kwh),
    "ausencias_no_son_ceros": True, "septiembre_8_23_horas": True,
    "HT3_retiro_nulo": True, "enlace_precio_deshabilitado": True,
    "campos_medidor": len(d.columns), "campos_hora": len(h.columns),
    "fuentes": [{"archivo": str(p.relative_to(BASE)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
}
(BASE / "controles/verificacion_mediciones_exportadas.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in report.items() if k != "fuentes"}, ensure_ascii=False, indent=2))

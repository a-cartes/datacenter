"""Verificación final de archivos exportados y descargas; no estima modelos."""
from pathlib import Path
from datetime import datetime, timezone
import ast
import hashlib
import json

import pandas as pd
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parents[1]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    expansion = json.loads((BASE / "verificacion_ampliacion.json").read_text())
    original_count = sum(json.loads(p.read_text())["filas_seleccionadas"] for p in (BASE / "extractos").glob("*_manifest.json"))
    main_table = pq.ParquetFile(BASE / "tablas/mediciones_candidatos_15min.parquet")
    assert main_table.metadata.num_rows == expansion["filas"] == original_count == 1862581
    assert len(expansion["meses_examinados"]) == 40
    assert expansion["desde_local"].startswith("2023-05-01")
    assert expansion["hasta_local"].startswith("2026-08-31")
    public = json.loads((BASE / "fuentes/consulta_publica_medidas_2026.json").read_text())
    assert len(public["descargas"]) == 2
    downloads = []
    for item in public["descargas"]:
        p = BASE / item["archivo"]
        assert p.stat().st_size == item["bytes"] and sha(p) == item["sha256"]
        downloads.append({k: item[k] for k in ["archivo", "bytes", "sha256", "anio", "mes"]})
    assert sum(d["bytes"] for d in downloads) == 530155551
    h = pd.read_parquet(BASE / "tablas/carga_HT1_HT2_hora_etiqueta.parquet")
    assert len(h) == 21912
    assert h.completo_por_etiquetas.all() and not h.HT3_incluido.any() and not h.enlace_precio_habilitado.any()
    assert not h.hora_utc_etiqueta.duplicated().any()
    assert abs(h.retiro_D_HT1_HT2_mw_por_etiquetas.sum() - h.energia_D_HT1_HT2_kwh.sum() / 1000) < 1e-8
    legacy = pd.read_parquet(BASE / "tablas/dataluna_horario_2020_2022_no_homologado.parquet")
    jan = pd.read_parquet(BASE / "tablas/dataluna_horario_2023_01_no_homologado.parquet")
    q1 = pd.read_parquet(BASE / "tablas/mediciones_canales_horarios_2023_01_04.parquet")
    assert len(legacy) == 20447 and not legacy.unidad_verificada.any()
    assert legacy.consumo_mw_homologado.isna().all()
    assert len(jan) == 744 and jan.unidad_rotulada.isna().all()
    assert len(q1) == 8548 and q1.unidad_rotulada.eq("kWh").all()
    assert q1.groupby(["archivo_original", "IDSOCKET", "fila_excel"]).size().eq(2).all()
    scripts = []
    for p in sorted((BASE / "scripts").glob("*.py")):
        ast.parse(p.read_text(), filename=str(p))
        scripts.append({"archivo": str(p.relative_to(BASE)), "sha256": sha(p)})
    report = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "estado": "OK",
        "filas_15min": original_count, "meses_csv": 40, "sockets": expansion["sockets_observados"],
        "horas_HT1_HT2": len(h), "horas_dataluna_2020_2022": len(legacy),
        "horas_dataluna_enero2023": len(jan), "valores_hora_canal_febrero_abril2023": len(q1),
        "descargas_verificadas": downloads, "scripts": scripts,
        "sin_unir_relojes_no_conciliados": True, "sin_imputar_tratamiento_o_consumo_faltante": True}
    (BASE / "verificacion_final_productos.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("descargas_verificadas", "scripts")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

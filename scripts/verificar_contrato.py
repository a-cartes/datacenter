"""Comprueba esquema, dimensiones, claves y ausencias causales de la versión base.

Lee tablas Parquet existentes y un contrato versionado. No reconstruye tablas,
no ajusta modelos y no convierte indicadores desconocidos en controles.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import os

import pandas as pd
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=os.getenv("SOCHER_OUTPUT_DIR", "artifacts"))
    args = parser.parse_args()
    out = Path(args.output_dir).expanduser()
    out = out.resolve() if out.is_absolute() else (ROOT / out).resolve()
    baseline_path = ROOT / "contracts/baseline_dataset.json"
    baseline = json.loads(baseline_path.read_text(encoding="utf-8"))
    errors, checked = [], []
    for table in baseline["tablas"]:
        path = ROOT / table["archivo"]
        check = {"tabla": table["tabla"], "archivo": table["archivo"]}
        try:
            meta = pq.ParquetFile(path)
            check.update(filas=meta.metadata.num_rows, columnas=len(meta.schema_arrow.names))
            if meta.metadata.num_rows != table["filas"]:
                errors.append(f"{table['tabla']}: filas {meta.metadata.num_rows}, esperadas {table['filas']}.")
            if meta.schema_arrow.names != table["columnas"]:
                errors.append(f"{table['tabla']}: nombres u orden de columnas diferentes del contrato.")
            selected = sorted(set(table["clave"] + table["columnas_totalmente_nulas"] + table["columnas_siempre_false"]))
            frame = pd.read_parquet(path, columns=selected)
            if frame[table["clave"]].isna().any().any() or frame.duplicated(table["clave"]).any():
                errors.append(f"{table['tabla']}: clave nula o duplicada {table['clave']}.")
            for col in table["columnas_totalmente_nulas"]:
                if not frame[col].isna().all():
                    errors.append(f"{table['tabla']}.{col}: la versión base requiere valores desconocidos nulos.")
            for col in table["columnas_siempre_false"]:
                if frame[col].isna().any() or not frame[col].eq(False).all():
                    errors.append(f"{table['tabla']}.{col}: habilitación inesperada en esta versión base.")
            check["columnas_leidas_para_claves_y_nulos"] = selected
        except (OSError, KeyError, ValueError) as exc:
            errors.append(f"{table['tabla']}: {type(exc).__name__}: {exc}")
        checked.append(check)
    result = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "estado": "OK" if not errors else "FALLO",
              "version_baseline": baseline["version"], "sha256_contrato": hashlib.sha256(baseline_path.read_bytes()).hexdigest(),
              "alcance": "Esquema y claves de la versión observada; ausencia de asignación causal. No es certificación de ATT/DiD.",
              "tablas": checked, "errores": errors}
    out.mkdir(parents=True, exist_ok=True)
    (out / "verificacion_contrato.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"estado": result["estado"], "tablas": len(checked), "errores": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Verifica tamaño y SHA-256 de insumos archivados sin reconstruir el dataset.

Sin argumentos, lee el inventario del repositorio y devuelve 0 si está íntegro.
Los originales declarados como no archivados son opcionales para esta capa;
se informa su exclusión sin descargar ni ejecutar análisis. No escribe archivos.
"""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "SOCHER_2026_dataset/documentacion/inventario_insumos_repositorio.json"


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventario", type=Path, default=DEFAULT)
    args = parser.parse_args()
    manifest = json.loads(args.inventario.read_text(encoding="utf-8"))
    errors, checked, optional, required = [], 0, 0, 0
    for entry in manifest["archivos"]:
        archived = entry.get("archivado", False)
        necessary = entry.get("requerido", False)
        if necessary:
            required += 1
        if not archived:
            optional += 1
            if necessary:
                errors.append({"ruta": entry.get("ruta"), "error": "requerido_no_archivado"})
            continue
        relative = entry.get("ruta")
        if not relative:
            errors.append({"ruta": relative, "error": "entrada_archivada_sin_ruta"})
            continue
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT) or Path(relative).is_absolute():
            errors.append({"ruta": relative, "error": "ruta_fuera_del_repositorio"})
            continue
        if not path.is_file():
            errors.append({"ruta": relative, "error": "archivo_archivado_ausente"})
            continue
        if path.stat().st_size != entry["bytes"]:
            errors.append({"ruta": relative, "error": "tamano_distinto"})
            continue
        if digest(path) != entry["sha256"]:
            errors.append({"ruta": relative, "error": "sha256_distinto"})
            continue
        checked += 1
    report = {"estado": "OK" if not errors else "FALLO", "archivos_verificados": checked,
              "requeridos_de_los_seis_pasos": required, "originales_opcionales_no_archivados": optional,
              "adquisicion_completa_incluida": False, "errores": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

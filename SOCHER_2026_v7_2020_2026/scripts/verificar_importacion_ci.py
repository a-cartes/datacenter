#!/usr/bin/env python3
"""Verifica artifacts de adquisición antes de incorporarlos al árbol moderno.

--integrar sólo se usa después de reservar el mes con el proceso local. Publica
los metadatos al final y nunca reemplaza archivos locales de contenido distinto.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parents[1]
MOD = BASE / "moderno"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(2**20), b""):
            h.update(chunk)
    return h.hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, required=True)
    parser.add_argument("--mes", required=True, choices=["2025-09", "2025-10", "2026-01", "2026-02"])
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--integrar", action="store_true")
    args = parser.parse_args()
    args.artifact = args.artifact.resolve()
    stem = args.mes.replace("-", "") + "_DEF"
    matches = list(args.artifact.rglob(stem + "_extraccion.json"))
    require(len(matches) == 1, "Debe existir un único manifiesto de extracción")
    tree = matches[0].parents[2]
    extraction = json.loads(matches[0].read_text())
    download_path = tree / "fuentes/metadatos" / (stem + ".json")
    download = json.loads(download_path.read_text())
    require(download["mes"] == extraction["mes"] == args.mes and extraction["version"] == "DEF", "Mes o versión distinta")
    require(extraction["seleccion_v6_sha256"] == sha(MOD / "config/seleccion_barras_v6.csv"), "Selección distinta")
    require(extraction["script_sha256"] == sha(MOD / "scripts/descargar_extraer_moderno.py"), "Parser local distinto; coordinar reextracción desde gzip antes de integrar")
    raw = tree / download["archivo"]
    require(raw.is_file() and sha(raw) == download["sha256_gzip_local"], "SHA gzip incorrecto")
    require(raw.stat().st_size == download["bytes_gzip_local"], "Tamaño gzip incorrecto")
    h, size = hashlib.sha256(), 0
    with gzip.open(raw, "rb") as f:
        for chunk in iter(lambda: f.read(2**20), b""):
            h.update(chunk); size += len(chunk)
    require(size == download["bytes_tsv_original"] and h.hexdigest() == download["sha256_tsv_descomprimido"], "TSV descomprimido distinto del manifiesto")
    files = [raw]
    for relative, expected in extraction["outputs"].items():
        path = (tree / relative).resolve()
        require(path.is_relative_to(tree.resolve()) and path.is_file() and sha(path) == expected, "Output distinto: " + relative)
        files.append(path)
    metadata = [download_path, matches[0]]
    for source in files + metadata:
        target = MOD / source.relative_to(tree)
        require(not target.exists() or sha(target) == sha(source), "Archivo local diferente, no sobrescribir: " + str(target.relative_to(MOD)))
    if args.integrar:
        # Metadatos finalizados son la señal para el finalizador local.
        for source in files + metadata:
            target = MOD / source.relative_to(tree)
            if target.exists():
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            temporary = target.with_name(target.name + ".from_ci.tmp")
            shutil.copyfile(source, temporary)
            require(sha(temporary) == sha(source), "Copia temporal distinta")
            require(not target.exists(), "Otro proceso produjo la fuente durante la copia")
            temporary.replace(target)
    report = {"estado": "OK", "mes": args.mes, "run_id": args.run_id,
              "integrado": args.integrar, "archivos_verificados": len(files) + len(metadata),
              "bytes_tsv_original": size, "sha256_tsv": h.hexdigest(),
              "filas_15min": extraction["filas_seleccionadas_15min"], "filas_horarias": extraction["filas_horarias"],
              "duplicados_clave": extraction["duplicados_clave"]}
    (args.artifact / "Verificacion_importacion_ci.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

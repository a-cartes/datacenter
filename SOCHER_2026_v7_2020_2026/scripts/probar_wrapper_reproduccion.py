#!/usr/bin/env python3
"""Prueba el lector de paquetes en repositorios temporales, sin subir datos.

El constructor mínimo de la prueba emite una sola fila ficticia temporal. Esta
prueba valida el contrato/extractor ZIP, no sustituye reconstruir el dataset real.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import warnings
import zipfile

BASE = Path(__file__).resolve().parents[1]
CONTENT = b"fecha,precio\n2000-01-01,0\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def exercise(wrapper, destination, scenario, optimized):
    destination.mkdir(parents=True)
    (destination / "scripts").mkdir()
    target_wrapper = destination / "scripts/reproducir_2020_2026.py"
    shutil.copyfile(wrapper, target_wrapper)
    base = destination / "SOCHER_2026_v7_2020_2026"
    (base / "scripts").mkdir(parents=True)
    builder = base / "scripts/construir_entrega.py"
    builder.write_text("from pathlib import Path\np=Path(__file__).resolve().parents[1]/'entrega'\np.mkdir(exist_ok=True)\n(p/'Dataset_precios_barra_hora_2020_2026.csv').write_bytes(" + repr(CONTENT) + ")\n")
    member = "../fuera_de_base.txt" if scenario == "traversal" else "datos/entrada.txt"
    payload = b"insumo de prueba temporal"
    record = dict(archivo=member, bytes=len(payload), sha256=digest(payload))
    if scenario == "hash_miembro":
        record["sha256"] = "0" * 64
    manifest = {"archivos": [record], "csv_principal_sha256": digest(CONTENT),
                "sha256_constructor": digest(builder.read_bytes())}
    if scenario == "constructor_distinto":
        manifest["sha256_constructor"] = "0" * 64
    package = destination / "paquete.zip"
    with zipfile.ZipFile(package, "w") as z:
        z.writestr(member, payload)
        if scenario == "duplicados_zip":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", UserWarning)
                z.writestr(member, payload)
        z.writestr("MANIFIESTO_INSUMOS.json", json.dumps(manifest))
    contract = {"sha256": digest(package.read_bytes()), "bytes": package.stat().st_size,
                "csv_principal_sha256": digest(CONTENT)}
    if scenario == "hash_paquete":
        contract["sha256"] = "0" * 64
    (destination / "contracts").mkdir()
    (destination / "contracts/insumos_2020_2026.json").write_text(json.dumps(contract))
    if scenario == "archivo_existente_distinto":
        (base / "datos").mkdir()
        (base / member).write_bytes(b"archivo previo que se debe conservar")
    command = [sys.executable] + (["-O"] if optimized else []) + [str(target_wrapper), "--insumos", str(package)]
    run = subprocess.run(command, cwd=destination, text=True, capture_output=True)
    expected = scenario == "valido"
    if (run.returncode == 0) != expected:
        raise RuntimeError(f"Caso {scenario}, -O={optimized}: salida inesperada {run.returncode}: {run.stderr}")
    if (destination / "fuera_de_base.txt").exists():
        raise RuntimeError("La prueba de ruta externa escribió fuera de la base")
    if scenario == "archivo_existente_distinto" and (base / member).read_bytes() != b"archivo previo que se debe conservar":
        raise RuntimeError("Se alteró el archivo previo")
    if expected and (base / "entrega/Dataset_precios_barra_hora_2020_2026.csv").read_bytes() != CONTENT:
        raise RuntimeError("El caso válido no reconstruyó los bytes esperados")
    return {"caso": scenario, "python_optimizado": optimized, "resultado": "OK",
            "comportamiento": "aceptado" if expected else "rechazado_antes_de_reconstruccion"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wrapper", type=Path, default=BASE.parent / "SOCHER_2026_repositorio/scripts/reproducir_2020_2026.py")
    parser.add_argument("--informe", type=Path, default=BASE / "documentacion/Prueba_wrapper_reproduccion.json")
    args = parser.parse_args()
    scenarios = ["valido", "hash_paquete", "hash_miembro", "traversal", "duplicados_zip", "archivo_existente_distinto", "constructor_distinto"]
    results = []
    with tempfile.TemporaryDirectory(prefix="socher_wrapper_") as temporary:
        for optimized in [False, True]:
            for scenario in scenarios:
                results.append(exercise(args.wrapper.resolve(), Path(temporary) / (scenario + str(optimized)), scenario, optimized))
    report = {"estado": "OK", "casos": len(results), "resultados": results,
              "sha256_wrapper": digest(args.wrapper.read_bytes()), "red_o_publicacion": False,
              "alcance": "Contrato ZIP y guardas en mini repositorios temporales; no es ejecución del dataset real ni de GitHub Actions."}
    args.informe.parent.mkdir(parents=True, exist_ok=True)
    args.informe.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

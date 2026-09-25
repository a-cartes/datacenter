"""Reconstruye el dataset desde extractos auditados incluidos en el repositorio.

No descarga datos, no reextrae los ZIP nacionales y no estima efectos causales.
La exportación Excel es opcional y utiliza escritura secuencial.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
from importlib import metadata
import json
import os
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "SOCHER_2026_dataset"
STEPS = ["construir_panel_precios.py", "construir_eventos_relaciones.py", "construir_mediciones.py",
         "verificar_mediciones.py", "verificar_y_catalogar.py", "documentar_panel.py"]
OBSERVED = {"pandas": "3.0.5", "numpy": "2.5.3", "pyarrow": "25.0.1", "openpyxl": "3.1.5"}


def output_path(value):
    path = Path(value).expanduser()
    return path.resolve() if path.is_absolute() else (ROOT / path).resolve()


def now():
    return datetime.now(timezone.utc).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--con-excel", action="store_true", help="Genera y verifica CSV y Excel completos en el directorio de artefactos.")
    parser.add_argument("--output-dir", default=os.getenv("SOCHER_OUTPUT_DIR", "artifacts"),
                        help="Artefactos y registros. Ruta relativa a la raíz del repositorio. También SOCHER_OUTPUT_DIR.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--comprobar-entradas", action="store_true", help="Comprueba entorno y huellas de insumos; no reconstruye tablas.")
    mode.add_argument("--solo-verificar", action="store_true", help="Comprueba insumos y contrato de tablas existentes; no las reconstruye.")
    args = parser.parse_args()
    if args.con_excel and (args.comprobar_entradas or args.solo_verificar):
        parser.error("--con-excel requiere reconstrucción; no combinar con modos de solo comprobación.")
    out = output_path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    log_path = out / "registro_reproduccion.json"
    log = {"inicio_utc": now(), "completado": False, "python_ejecutable": sys.executable,
           "python_version": platform.python_version(), "python_observado": "3.13.15",
           "sistema": platform.platform(), "instalacion_limpia_verificada": False,
           "alcance": "Reconstrucción desde extractos auditados incluidos; no adquisición original ni estimación causal.",
           "adquisicion_original_ejecutada": False, "estimacion_causal_ejecutada": False,
           "excel_solicitado": args.con_excel, "directorio_artefactos": str(out),
           "modo": "comprobar_entradas" if args.comprobar_entradas else "solo_verificar" if args.solo_verificar else "reconstruir",
           "dependencias": {}, "advertencias_entorno": [], "pasos": []}

    def save():
        log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")

    missing = []
    for name, expected in OBSERVED.items():
        try:
            actual = metadata.version(name)
        except metadata.PackageNotFoundError:
            actual = None
        log["dependencias"][name] = {"observada": actual, "referencia_local": expected}
        if actual is None and (name != "openpyxl" or args.con_excel):
            missing.append(name)
        elif actual is not None and actual != expected:
            log["advertencias_entorno"].append(f"{name}: se observó {actual}; referencia de reconstrucción {expected}.")
    if platform.python_version() != "3.13.15":
        log["advertencias_entorno"].append("Python difiere de 3.13.15; no se presupone compatibilidad por ese motivo.")
    if sys.flags.optimize:
        missing.append("ejecutar Python sin -O/-OO: las verificaciones de los constructores utilizan assert")
    if missing:
        log.update(error="Faltan requisitos de ejecución", faltantes=missing, fin_utc=now())
        save()
        print(log["error"] + ": " + ", ".join(missing), file=sys.stderr)
        return 2

    env = os.environ.copy()
    env["SOCHER_OUTPUT_DIR"] = str(out)
    # Evita heredar un modo que suprima las aserciones de los seis constructores.
    env.pop("PYTHONOPTIMIZE", None)
    for message in log["advertencias_entorno"]:
        print("Entorno: " + message, flush=True)

    def run(path, label, extra=()):
        if not path.is_file():
            raise FileNotFoundError(f"No existe el script requerido: {path.relative_to(ROOT)}")
        start = time.monotonic()
        command = [sys.executable, str(path), *extra]
        result = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        log["pasos"].append({"fase": label, "script": str(path.relative_to(ROOT)),
            "sha256_script": hashlib.sha256(path.read_bytes()).hexdigest(), "comando": command,
            "segundos": round(time.monotonic() - start, 3), "codigo_salida": result.returncode,
            "stdout": result.stdout, "stderr": result.stderr})
        save()
        if result.returncode:
            print(result.stderr or result.stdout, file=sys.stderr)
            raise RuntimeError(f"{path.name} terminó con código {result.returncode}.")
        print(f"{label}: {path.name} completado", flush=True)

    save()
    try:
        run(ROOT / "scripts/verificar_insumos.py", "Entradas")
        if not args.comprobar_entradas:
            if not args.solo_verificar:
                for step in STEPS:
                    run(DATASET / "scripts" / step, "Reconstrucción")
            run(ROOT / "scripts/verificar_contrato.py", "Contrato", ["--output-dir", str(out)])
            if args.con_excel:
                for step in ["preparar_exportacion_excel_csv.py", "exportar_excel_por_bloques.py", "verificar_exportacion_excel_csv.py"]:
                    run(DATASET / "scripts" / step, "Exportación", ["--output-dir", str(out)])
        log.update(completado=True, fin_utc=now())
    except (OSError, RuntimeError) as exc:
        log.update(error=str(exc), fin_utc=now())
        save()
        print(str(exc), file=sys.stderr)
        return 1
    save()
    print(f"Registro: {log_path}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

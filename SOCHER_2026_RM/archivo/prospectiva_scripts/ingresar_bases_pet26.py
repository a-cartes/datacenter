"""Registra e inventaría los ZIP del Anexo VII de la Propuesta Final PET 2026 una vez descargados con navegador.

www.coordinador.cl entrega estos .zip tras un desafío Cloudflare, por lo que no se descargan de forma
automática. Flujo:
  1. Descargar con el navegador (cualquier carpeta; por defecto se buscan en ~/Downloads y fuentes/originales):
       Anexo-VII-BD-PLP-PET26.zip        Anexo-VII-BD-PF-COORD-DPL.zip
  2. python scripts/ingresar_bases_pet26.py
El programa copia cada ZIP a fuentes/originales/, registra SHA-256 y tamaño en fuentes/registro_fuentes.csv,
lo descomprime en fuentes/originales/pet26/<id>/ (incluidos los ZIP anidados) y escribe
extraidos/pet26/inventario_<id>.csv con ruta, extensión, bytes y una clasificación tentativa por nombre.
La clasificación usa nombres habituales de archivos PLP y PowerFactory; es una ayuda para localizar insumos
y debe verificarse abriendo los archivos. No interpreta ni transforma datos.
"""
import csv
import re
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ORIG = ROOT / "fuentes" / "originales"
OUT = ROOT / "extraidos" / "pet26"
ZIPS = {"CEN_PET26_BD_PLP": "Anexo-VII-BD-PLP-PET26.zip", "CEN_PET26_BD_PF": "Anexo-VII-BD-PF-COORD-DPL.zip"}
PISTAS = [  # (patrón sobre el nombre en minúsculas, variable del modelo) -- tentativo
    (r"plpdem|demanda|dem_", "demanda por barra y etapa/bloque"),
    (r"plpbar\.dat|barras", "barras (identificadores)"),
    (r"plpcnfce|plpcen\.dat|centrales", "centrales: configuración y parámetros"),
    (r"plpcosce|cvar|costo", "costos variables de centrales"),
    (r"plpmance|mantcen|manten", "mantenimiento/disponibilidad de centrales"),
    (r"plpaflce|aflu|hidrolog|caudal", "afluentes e hidrologías"),
    (r"plpcnfem|plpemb|embalse|cota|plpfilemb|plpextrac|plplaja|plpmaule|plpralco|riego|convenio", "embalses, filtraciones y convenios de riego"),
    (r"plpcnfli|plplin\.dat|lineas", "líneas: topología, capacidad, reactancia"),
    (r"plpmanli|mantlin", "mantenimiento/entrada de líneas (obras futuras)"),
    (r"plpess|plpbat|bess|bater|almac", "almacenamiento"),
    (r"plpeta|plpblo|etapa|bloque|plpidsim", "etapas y bloques (resolución temporal)"),
    (r"plpbar\.csv|cmg|marginal", "resultados: costos marginales por barra"),
    (r"plpcen\.csv|generac", "resultados: generación y costos por central"),
    (r"plplin\.csv|flujo", "resultados: flujos por línea"),
    (r"plpemb\.csv|plpfal|falla", "resultados: embalses / energía no suministrada"),
    (r"\.pfd$|\.dz$", "PowerFactory: proyecto (requiere licencia DIgSILENT)"),
    (r"\.dgs$|\.dle$|\.raw$", "PowerFactory/PSS-E: intercambio de datos (legible sin licencia)"),
    (r"\.dpl$|dpl", "PowerFactory: script DPL"),
]


def localizar(nombre):
    for d in (ORIG, Path.home() / "Downloads", Path.home() / "Desktop"):
        for p in sorted(d.glob(nombre.replace(".zip", "*.zip"))):
            return p
    return None


def descomprimir(z, dest):
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(z) as f:
        f.extractall(dest)
    for sub in list(dest.rglob("*.zip")):
        d = sub.with_suffix("")
        if not d.exists():
            try:
                descomprimir(sub, d)
            except zipfile.BadZipFile:
                pass


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for id_, nombre in ZIPS.items():
        src = localizar(nombre)
        if not src:
            print(f"[falta] {nombre}: descárguelo con el navegador y vuelva a ejecutar")
            continue
        subprocess.run([sys.executable, str(ROOT / "scripts" / "descargar_fuentes.py"), "registrar", str(src), id_], check=True)
        dest = ORIG / "pet26" / id_
        descomprimir(ORIG / nombre, dest)
        with open(OUT / f"inventario_{id_}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ruta", "extension", "bytes", "posible_contenido"])
            n = 0
            for p in sorted(dest.rglob("*")):
                if p.is_file():
                    rel = str(p.relative_to(dest))
                    pista = "; ".join(v for pat, v in PISTAS if re.search(pat, rel.lower()))
                    w.writerow([rel, p.suffix.lower(), p.stat().st_size, pista])
                    n += 1
        print(f"[ok] {nombre}: {n} archivos -> extraidos/pet26/inventario_{id_}.csv")


if __name__ == "__main__":
    main()

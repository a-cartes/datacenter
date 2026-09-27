"""Extract and render the pages cited in the ODATA entry memorandum.

Run with the bundled Python runtime (pypdf), supplying --render to inspect PDFs.
No price outcomes are read and no event matrix or causal eligibility is modified.
"""
from pathlib import Path
from pypdf import PdfReader
import argparse
import hashlib
import json
import os
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent
SELECTED = {
    "SMA_carta_inicio_operacion_ODCH_ST01_061_2022_original.pdf": [1],
    "SMA_comprobante_inicio_operacion_20220818_original.pdf": [1],
    "SEA_DIA2020_Cap1.pdf": [10, 11, 31, 32, 61],
    "SEA_pertinencia20231026_CdP.pdf": [13, 23, 24],
    "CEN_IAC_carta20230703.pdf": [1, 4],
    "CEN_IAC_anexo20230703_0": [4],
    "CEN_EAF318_2025.pdf": [114],
    "RCA098_2021.pdf": [1],
    "SEA_Adenda20201001.pdf": [7],
    "OGP_cartera_abril2023.pdf": [47],
}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render", action="store_true")
    args = parser.parse_args()
    target = ROOT / "validacion"
    target.mkdir(exist_ok=True)
    evidence = []
    env = os.environ.copy()
    cache = Path(tempfile.gettempdir()) / "odata_fontconfig"
    cache.mkdir(exist_ok=True)
    config = cache / "fonts.conf"
    config.write_text(f'<?xml version="1.0"?><!DOCTYPE fontconfig SYSTEM "fonts.dtd"><fontconfig><dir>/System/Library/Fonts</dir><dir>/Library/Fonts</dir><cachedir>{cache}</cachedir></fontconfig>')
    env["FONTCONFIG_FILE"] = str(config)
    env["XDG_CACHE_HOME"] = str(cache)
    executable = "/Users/yo/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/pdftoppm"
    for name, pages in SELECTED.items():
        source = ROOT / "fuentes" / name
        assert source.read_bytes().startswith(b"%PDF"), name
        pdf = PdfReader(source)
        for page in pages:
            text = pdf.pages[page - 1].extract_text() or ""
            base = target / f"{name}_p{page}"
            Path(str(base) + ".txt").write_text(text)
            if args.render:
                with open(cache / "render.log", "ab") as log:
                    subprocess.run([executable, "-f", str(page), "-l", str(page), "-r", "110", "-png", "-singlefile", str(source), str(base)], check=True, stderr=log, env=env)
            evidence.append({"source": name, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(), "pdf_page_one_based": page, "text_sha256": hashlib.sha256(text.encode()).hexdigest(), "has_embedded_text": bool(text.strip())})
    (target / "paginas_citadas.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2))
    print(f"Selected {len(evidence)} pages from {len(SELECTED)} PDFs.")

if __name__ == "__main__":
    main()

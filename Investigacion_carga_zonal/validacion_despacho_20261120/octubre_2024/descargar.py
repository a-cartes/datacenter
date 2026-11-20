"""Descarga los ZIP definitivos enlazados por el Coordinador para octubre de 2024."""
import csv
import hashlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import urljoin
from zipfile import ZipFile

BASE = "https://www.coordinador.cl/mercados/documentos/costo-marginal-real/2024-costo-marginal-real-transferencias-economicas/octubre-2024-costo-marginal-real-transferencias-economicas/"
cache = Path(sys.argv[1])
cache.mkdir(parents=True, exist_ok=True)


def descargar(dia):
    pagina = BASE + f"{dia:02}-octubre-2024-costo-marginal-real-transferencias-economicas/"
    with urlopen(pagina, timeout=90) as respuesta:
        html = respuesta.read().decode("utf-8")
    enlaces = re.findall(r'href=["\x27]([^"\x27]+\.zip)["\x27]', html, flags=re.I)
    urls = list(dict.fromkeys(urljoin(pagina, u) for u in enlaces if "def" in u.lower() and f"2410{dia:02}" in u))
    if len(urls) != 1:
        raise ValueError((pagina, urls))
    destino = cache / f"{dia:02}.zip"
    if not destino.exists():
        with urlopen(urls[0], timeout=120) as r:
            contenido = r.read()
        temporal = destino.with_suffix(".part")
        temporal.write_bytes(contenido)
        with ZipFile(temporal) as z:
            assert z.testzip() is None
        temporal.replace(destino)
    return [dia, pagina, urls[0], hashlib.sha256(destino.read_bytes()).hexdigest()]


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as pool:
        filas = list(pool.map(descargar, range(1, 32)))
    with (cache / "fuentes.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["dia", "pagina", "zip", "sha256"])
        w.writerows(filas)

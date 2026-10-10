"""Costos marginales reales del régimen nuevo (desde el 15/07/2024): descarga propia y verificación.

Ruta pública usada por el botón de descarga de https://www.coordinador.cl/costos-marginales/
(patrón observado en el JavaScript público del sitio; no requiere credenciales):
  https://cen-datalake-public.s3.amazonaws.com/costos_marginales/CMG_REAL/{AAAA}/{M}/{AAAA}_{MM}_REAL-{VERSION}.tsv

El ETag de S3 de estos objetos es un MD5 multiparte ("<md5>-<n partes>"). Se reconstruye
localmente probando tamaños de parte habituales; si coincide, los bytes locales son
idénticos al objeto oficial vigente. Esto permite verificar copias descargadas antes
por el usuario sin volver a transferirlas (la red disponible rinde ~0,1-0,6 MB/s).

Modos:
  verificar <ruta.tsv.gz> AAAA-MM   : verifica una copia previa y la enlaza al proyecto
  descargar AAAA-MM [...]           : descarga con rangos paralelos y verifica
Salida: fuentes/precios/originales/moderno/AAAAMM_REAL-DEF.tsv.gz + .json
"""
from concurrent.futures import ThreadPoolExecutor
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys
import time

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "fuentes" / "precios" / "originales" / "moderno"
BASE = "https://cen-datalake-public.s3.amazonaws.com/costos_marginales/CMG_REAL/{y}/{m}/{y}_{mm:02d}_REAL-{v}.tsv"
MiB = 1 << 20


def url_for(ym, v="DEF"):
    y, m = map(int, ym.split("-"))
    return BASE.format(y=y, m=m, mm=m, v=v)


def head(url):
    h = requests.head(url, timeout=60)
    return {"status_head": h.status_code, "etag": (h.headers.get("ETag") or "").strip('"'),
            "last_modified": h.headers.get("Last-Modified"), "bytes_declarados": int(h.headers.get("Content-Length", 0) or 0)}


def part_sizes(url, n_parts):
    """Tamaño exacto de cada parte del objeto multiparte (HEAD ?partNumber=k)."""
    sizes = []
    for k in range(1, n_parts + 1):
        h = requests.head(f"{url}?partNumber={k}", timeout=60)
        sizes.append(int(h.headers["Content-Length"]))
    return sizes


def digests(stream_chunks, sizes):
    """SHA-256 del contenido y MD5 multiparte con los límites de parte oficiales, en una pasada."""
    sha, cur, parts, k, fill, n = hashlib.sha256(), hashlib.md5(), [], 0, 0, 0
    for chunk in stream_chunks:
        sha.update(chunk)
        n += len(chunk)
        view = memoryview(chunk)
        while len(view):
            size = sizes[k] if k < len(sizes) else float("inf")
            take = int(min(size - fill, len(view)))
            cur.update(view[:take])
            fill += take
            view = view[take:]
            if fill == size:
                parts.append(cur.digest())
                cur, fill, k = hashlib.md5(), 0, k + 1
    if fill:
        parts.append(cur.digest())
    return sha.hexdigest(), n, hashlib.md5(b"".join(parts)).hexdigest() + f"-{len(parts)}"


def gz_chunks(path, size=8 * MiB):
    with gzip.open(path, "rb") as g:
        while b := g.read(size):
            yield b


def record(ym, out, meta, origen):
    sizes = part_sizes(meta["url"], int(meta["etag"].split("-")[1])) if "-" in meta["etag"] else []
    sha, n, etag = digests(gz_chunks(out), sizes)
    meta.update({"mes": ym, "sha256_descomprimido": sha, "bytes_descomprimidos": n,
                 "etag_reconstruido": etag, "tamanos_partes": sizes,
                 "verificado_etag": etag == meta["etag"], "tamano_coincide": n == meta["bytes_declarados"],
                 "origen_bytes": origen, "fecha_registro_utc": pd.Timestamp.utcnow().isoformat(timespec="seconds")})
    out.with_suffix("").with_suffix(".json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    return meta


def verificar(src, ym):
    DEST.mkdir(parents=True, exist_ok=True)
    url = url_for(ym)
    meta = {"url": url, **head(url)}
    out = DEST / f"{ym.replace('-', '')}_REAL-DEF.tsv.gz"
    if not out.exists():
        os.link(src, out)
    return record(ym, out, meta, f"copia previa del usuario: {str(src).replace(str(Path.home()), '~')}")


def descargar(ym, threads=12, part=8 * MiB):
    DEST.mkdir(parents=True, exist_ok=True)
    url = url_for(ym)
    meta = {"url": url, **head(url)}
    out = DEST / f"{ym.replace('-', '')}_REAL-DEF.tsv.gz"
    if meta["status_head"] != 200:
        out.with_suffix("").with_suffix(".json").write_text(json.dumps(meta, indent=1))
        return meta
    raw = DEST / f".{ym}.tsv.part"
    total = meta["bytes_declarados"]
    with open(raw, "ab") as f:
        f.truncate(total)
    done_file = raw.with_suffix(".done")
    done = set(json.loads(done_file.read_text())) if done_file.exists() else set()
    ranges = [(s, min(s + part, total) - 1) for s in range(0, total, part) if s not in done]

    def get_range(r):
        s, e = r
        for k in range(8):
            try:
                resp = requests.get(url, headers={"Range": f"bytes={s}-{e}", "If-Match": f'"{meta["etag"]}"'}, timeout=300)
                if resp.status_code == 206 and len(resp.content) == e - s + 1:
                    with open(raw, "r+b") as f:
                        f.seek(s)
                        f.write(resp.content)
                    return s
            except requests.RequestException:
                pass
            time.sleep(3 * (k + 1))
        raise RuntimeError(f"rango {s}-{e} falló")

    with ThreadPoolExecutor(threads) as ex:
        for i, s in enumerate(ex.map(get_range, ranges)):
            done.add(s)
            if i % 10 == 0:
                done_file.write_text(json.dumps(sorted(done)))
    done_file.write_text(json.dumps(sorted(done)))
    with open(raw, "rb") as f, gzip.open(out.with_suffix(".gzpart"), "wb", compresslevel=6) as g:
        while b := f.read(8 * MiB):
            g.write(b)
    out.with_suffix(".gzpart").rename(out)
    meta = record(ym, out, meta, "descarga propia por rangos HTTP con If-Match al ETag")
    if meta["verificado_etag"]:
        raw.unlink()
        done_file.unlink()
    return meta


if __name__ == "__main__":
    if sys.argv[1] == "verificar":
        m = verificar(Path(sys.argv[2]), sys.argv[3])
    else:
        for ym in sys.argv[2:]:
            m = descargar(ym)
            print(ym, {k: m.get(k) for k in ["status_head", "bytes_declarados", "verificado_etag"]}, flush=True)
        sys.exit()
    print(sys.argv[3], {k: m.get(k) for k in ["etag", "etag_reconstruido", "verificado_etag", "tamano_coincide"]})

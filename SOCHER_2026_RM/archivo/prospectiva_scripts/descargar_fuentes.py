"""Descarga fuentes públicas de la prospectiva 2030 y mantiene el registro de procedencia.

Lee fuentes/lista_fuentes.csv (id, url, archivo, descripcion, version) y guarda cada archivo en
fuentes/originales/. Registra en fuentes/registro_fuentes.csv: URL, URL final, estado HTTP,
bytes, SHA-256, Last-Modified y ETag del servidor (indicadores de versión) y fecha de consulta.

No intenta superar el desafío Cloudflare de www.coordinador.cl (HTTP 403 con
'cf-mitigated: challenge', que hoy afecta a .zip y páginas HTML pero no a .pdf). Esos archivos
quedan con estado 'bloqueado_cloudflare' y deben descargarse con navegador; después se
registran con:  python scripts/descargar_fuentes.py registrar <ruta_local> <id>

Uso: python scripts/descargar_fuentes.py [id ...]      (sin argumentos: todos los pendientes)
"""
import csv
import hashlib
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LISTA = ROOT / "fuentes" / "lista_fuentes.csv"
REG = ROOT / "fuentes" / "registro_fuentes.csv"
DEST = ROOT / "fuentes" / "originales"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/129.0 Safari/537.36", "Accept-Language": "es-CL,es;q=0.9"}
CAMPOS = ["id", "archivo", "descripcion", "version", "url", "url_final", "estado", "http", "bytes", "sha256",
          "last_modified", "etag", "content_type", "fecha_consulta_utc", "origen_bytes"]


def sha(p, buf=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(buf):
            h.update(b)
    return h.hexdigest()


def leer(p):
    return list(csv.DictReader(open(p, encoding="utf-8"))) if p.exists() else []


def guardar(reg):
    with open(REG, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS)
        w.writeheader()
        w.writerows(sorted(reg.values(), key=lambda r: r["id"]))


def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def bajar(row):
    import requests

    out = DEST / row["archivo"]
    out.parent.mkdir(parents=True, exist_ok=True)
    rec = {**{k: "" for k in CAMPOS}, **{k: row.get(k, "") for k in ("id", "archivo", "descripcion", "version", "url")},
           "fecha_consulta_utc": ahora(), "origen_bytes": "descarga automática (requests)"}
    for k in range(3):
        try:
            with requests.get(row["url"], headers=UA, timeout=180, stream=True) as r:
                rec.update(http=r.status_code, url_final=r.url, content_type=r.headers.get("Content-Type", ""),
                           last_modified=r.headers.get("Last-Modified", ""), etag=r.headers.get("ETag", "").strip('"'))
                if r.status_code == 403 and r.headers.get("cf-mitigated") == "challenge":
                    rec["estado"] = "bloqueado_cloudflare"
                    return rec
                if r.status_code != 200:
                    rec["estado"] = f"error_http_{r.status_code}"
                    return rec
                tmp = out.with_name(out.name + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                tmp.replace(out)
            rec.update(estado="descargado", bytes=out.stat().st_size, sha256=sha(out))
            return rec
        except requests.RequestException as e:
            rec["estado"] = f"error_red: {type(e).__name__}"
            time.sleep(5 * (k + 1))
    return rec


def registrar(src, id_):
    lista = {r["id"]: r for r in leer(LISTA)}
    row = lista[id_]
    out = DEST / row["archivo"]
    out.parent.mkdir(parents=True, exist_ok=True)
    src = Path(src).expanduser()
    if src.resolve() != out.resolve():
        shutil.copy2(src, out)
    reg = {r["id"]: r for r in leer(REG)}
    reg[id_] = {**{k: "" for k in CAMPOS}, **{k: row.get(k, "") for k in ("id", "archivo", "descripcion", "version", "url")},
                "estado": "descarga_manual_navegador", "bytes": out.stat().st_size, "sha256": sha(out),
                "fecha_consulta_utc": ahora(),
                "last_modified": datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")
                + " (mtime local, no del servidor)",
                "origen_bytes": f"descarga manual del usuario: {str(src).replace(str(Path.home()), '~')}"}
    guardar(reg)
    print(reg[id_])


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "registrar":
        return registrar(sys.argv[2], sys.argv[3])
    ids = set(sys.argv[1:])
    reg = {r["id"]: r for r in leer(REG)}
    for row in leer(LISTA):
        if ids and row["id"] not in ids:
            continue
        prev = reg.get(row["id"])
        if not ids and prev and prev["estado"] in ("descargado", "descarga_manual_navegador") and (DEST / row["archivo"]).exists():
            continue
        rec = bajar(row)
        reg[row["id"]] = rec
        print(rec["id"], rec["estado"], rec["http"], rec["bytes"], flush=True)
        guardar(reg)
        time.sleep(1)


if __name__ == "__main__":
    main()

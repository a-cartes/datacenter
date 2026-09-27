"""Consulta el repositorio público enlazado por CEN y descarga meses faltantes.

No usa autenticación, cookies ni credenciales. Solo conserva metadatos públicos
seleccionados y huellas, nunca tokens efímeros del HTML de Box.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import subprocess
from urllib.parse import urlencode
import zipfile

BASE = Path(__file__).resolve().parents[1]
SHARE = "https://coordinador.app.box.com/v/transferenciaseconomicas"
SOURCE = "https://www.coordinador.cl/registro-y-reportes-prmte/"
KEEP = ["type", "id", "name", "itemSize", "filesCount", "parentFolderID", "date"]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def fetch(url):
    result = subprocess.run(["curl", "-L", "--fail", "--silent", "--show-error", "--max-time", "45", url],
                            capture_output=True, check=True)
    html = result.stdout.decode("utf-8")
    marker = "Box.postStreamData = "
    data, _ = json.JSONDecoder().raw_decode(html[html.index(marker) + len(marker):])
    return data, hashlib.sha256(result.stdout).hexdigest()


def folder(url, audit):
    data, digest = fetch(url)
    raw = data["/app-api/enduserapp/shared-folder"]
    clean = {"url": url, "sha256_respuesta_no_archivada": digest,
             "id": raw["currentFolderID"], "nombre": raw["currentFolderName"],
             "items": [{k: item.get(k) for k in KEEP} for item in raw["items"]]}
    audit.append(clean)
    return clean


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--meses", type=int, nargs="+", default=[7, 8])
    parser.add_argument("--descargar", action="store_true")
    args = parser.parse_args()
    out = BASE / "fuentes"
    out.mkdir(parents=True, exist_ok=True)
    dest_report = out / "consulta_publica_medidas_2026.json"
    previous = json.loads(dest_report.read_text()) if dest_report.exists() else {}
    prior_downloads = {x["archivo"]: x for x in previous.get("descargas", [])}
    audit, files = [], []
    top = folder(SHARE, audit)
    year = next(x for x in top["items"] if x["type"] == "folder" and x["name"] == "2026")
    yr = folder(f"{SHARE}/folder/{year['id']}", audit)
    for month in args.meses:
        mo = next(x for x in yr["items"] if x["name"].startswith(f"{month:02d}_"))
        content = folder(f"{SHARE}/folder/{mo['id']}", audit)
        for version in content["items"]:
            if version["type"] != "folder" or "definitiv" not in version["name"].lower():
                continue
            vf = folder(f"{SHARE}/folder/{version['id']}", audit)
            for item in vf["items"]:
                if item["type"] == "file" and "Puntos_de_Medida" in item["name"] and not item["name"].startswith("2_"):
                    files.append({**item, "anio": 2026, "mes": month, "mes_carpeta": mo["name"],
                                  "version": version["name"], "url_publica": f"{SHARE}/file/{item['id']}"})
    report = {"consulta_utc": datetime.now(timezone.utc).isoformat(), "portal_oficial": SOURCE,
              "repositorio_publico": SHARE, "carpetas": audit, "archivos_reales_definitivos_seleccionados": files,
              "bytes_declarados_seleccion": sum(x["itemSize"] for x in files), "descargas": list(prior_downloads.values())}
    dest_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"seleccion": files, "bytes": report["bytes_declarados_seleccion"]}, ensure_ascii=False, indent=2), flush=True)
    if not args.descargar:
        return
    assert report["bytes_declarados_seleccion"] <= 5_000_000_000, "Consultar autorización antes de descargar más de 5 GB"
    for item in files:
        dest = BASE / "originales_descargados" / "2026" / item["mes_carpeta"] / "Definitivo" / item["name"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists() and dest.stat().st_size == item["itemSize"] and zipfile.is_zipfile(dest):
            old = prior_downloads.get(str(dest.relative_to(BASE)))
            if old:
                assert sha(dest) == old["sha256"], "El ZIP local cambió desde la descarga documentada."
            print(f"Reutiliza archivo local 2026-{item['mes']:02d}", flush=True)
        else:
            data, _ = fetch(item["url_publica"])
            entry = data.get("/app-api/enduserapp/shared-file", {})
            url = entry.get("downloadURL") or entry.get("downloadUrl")
            if not url:
                # La vista de archivo usa el endpoint item/f_ID. Se exige que la
                # página pública autorice descarga antes de usar su enlace público.
                view = data.get(f"/app-api/enduserapp/item/f_{item['id']}", {})
                candidates = view.get("items", [])
                source_item = next((v for v in candidates if str(v.get("id")) == str(item["id"])), None)
                assert source_item and source_item.get("canDownload") is True
                assert not source_item.get("isDownloadBlockedByShieldAccessPolicy")
                shared_data, _ = fetch(SHARE)
                public_share = shared_data["/app-api/enduserapp/shared-item"]["sharedName"]
                url = "https://coordinador.app.box.com/index.php?" + urlencode({
                    "rm": "box_download_shared_file", "shared_name": public_share,
                    "file_id": f"f_{item['id']}"})
            part = dest.with_suffix(dest.suffix + ".part")
            subprocess.run(["curl", "-L", "--fail", "--silent", "--show-error", "--retry", "2", "--max-time", "600", "--output", str(part), url], check=True)
            assert part.stat().st_size == item["itemSize"], (part, part.stat().st_size, item["itemSize"])
            assert zipfile.is_zipfile(part), part
            part.replace(dest)
        info = {"url_publica": item["url_publica"], "archivo": str(dest.relative_to(BASE)),
                "bytes": dest.stat().st_size, "sha256": sha(dest), "box_file_id": item["id"],
                "anio": item["anio"], "mes": item["mes"], "version": item["version"]}
        prior_downloads[info["archivo"]] = info
        report["descargas"] = list(prior_downloads.values())
        dest_report.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Descarga verificada 2026-{item['mes']:02d}: {info['bytes']} bytes", flush=True)


if __name__ == "__main__":
    main()

"""Download only the public sources selected for the ODATA chronology audit."""
from pathlib import Path
from urllib.request import urlopen, Request
import datetime
import hashlib
import json

ROOT = Path(__file__).resolve().parent
DEST = ROOT / "fuentes"
manifest_path = DEST / "manifest_descarga.json"
old = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
manifest = {x["archivo"]: x for x in old}
for name, url in json.loads((ROOT / "fuentes_seleccionadas.json").read_text()).items():
    target = DEST / name
    if target.exists():
        assert hashlib.sha256(target.read_bytes()).hexdigest() == manifest[name]["sha256"]
        continue
    if name in manifest and "error" in manifest[name]:
        continue
    entry = {"archivo": name, "url": url, "consulta_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
        with urlopen(Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=45) as response:
            data = response.read()
            target.write_bytes(data)
            entry.update(status=response.status, mime=response.headers.get("Content-Type"), bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    except Exception as exc:
        entry["error"] = str(exc)
    manifest[name] = entry
    print(name, entry.get("status", entry.get("error")))
    manifest_path.write_text(json.dumps(list(manifest.values()), ensure_ascii=False, indent=2))

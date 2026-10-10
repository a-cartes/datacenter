"""Registra los libros mensuales originales del Coordinador (enero 2017 - julio 2024).

El portal del Coordinador responde 403 a descargas automatizadas (desafío Cloudflare,
verificado el 2026-10-02). Los libros fueron descargados manualmente por el usuario
mediante navegador y están en ~/Downloads y en carpetas de trabajos anteriores.
Este programa NO usa bases procesadas de esos trabajos: solo localiza archivos
originales, calcula SHA-256, compara duplicados y crea enlaces duros (sin copiar
bytes) en fuentes/precios/originales/historico/AAAAMM/. La URL y fecha de publicación
se toman de los registros de descarga previos y quedan marcadas como 'declaradas';
la integridad se verificó contra una descarga propia solo para diciembre de 2017.

Uso: python scripts/registrar_originales_historicos.py
"""
import csv
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "fuentes" / "precios" / "originales" / "historico"
HOME = Path.home()
DL = HOME / "Downloads"
V7 = DL / "Medidas Transferencias económicas-selected" / "SOCHER_2026_v7_2020_2026"
PREV = ROOT.parent / "Panel_datos" / "cmg_2017_2019" / "descargas"
OWN = ROOT / "fuentes" / "precios" / "cmg1712_def.zip"
PAT = re.compile(r"^cmg_?(\d{2})(\d{2})(_def|_pre)?")


def sha(p, buf=1 << 22):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        while b := f.read(buf):
            h.update(b)
    return h.hexdigest()


def candidates():
    for base in [DL, V7 / "historico" / "originales", V7 / "historico" / "originales" / "cuarentena"]:
        for p in sorted(base.iterdir()):
            m = PAT.match(p.name)
            if not m:
                continue
            if p.is_dir():
                for q in sorted(p.iterdir()):
                    if q.is_file():
                        yield m, q, p.name
            elif p.is_file():
                yield m, p, None


def declared():
    """Procedencia declarada en registros de descarga previos (URL, fecha de publicación)."""
    out = {}
    for j in PREV.rglob("*.fuente.json"):
        d = json.loads(j.read_text())
        out.setdefault(d.get("sha256"), d)
    fp = V7 / "entrega" / "Fuentes_precios.csv"
    if fp.exists():
        for r in csv.DictReader(open(fp)):
            if r["fuente_id"].startswith("historico_"):
                out.setdefault("mes:" + r["fuente_id"][10:16], {"url": r["url_original"],
                               "fecha_publicacion": r["fecha_publicacion_literal"],
                               "titulo": r["titulo_oficial"], "pagina_origen": r["url_indice"]})
    return out


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    dec = declared()
    own = sha(OWN)
    rows = []
    for m, p, carpeta in candidates():
        yymm = "20" + m.group(1) + m.group(2)
        version = (m.group(3) or "_sinsufijo")[1:].upper()
        rows.append({"mes": yymm, "version_nombre": version, "ruta": str(p), "carpeta_extraida": carpeta or "",
                     "archivo": p.name, "bytes": p.stat().st_size, "sha256": sha(p), "inode": p.stat().st_ino})
    # agrupar por mes y por contenido
    out, months = [], sorted({r["mes"] for r in rows})
    for mes in months:
        rs = [r for r in rows if r["mes"] == mes]
        by_hash = {}
        for r in rs:
            by_hash.setdefault(r["sha256"], []).append(r)
        for h, grp in by_hash.items():
            r0 = grp[0]
            sub = DEST / mes / (r0["carpeta_extraida"] or "")
            sub.mkdir(parents=True, exist_ok=True)
            clean = re.sub(r" \(\d\)", "", r0["archivo"])
            target = sub / clean
            if target.exists() and sha(target) != h:
                target = sub / (Path(clean).stem + "_" + h[:8] + Path(clean).suffix)
            if not target.exists():
                os.link(r0["ruta"], target)
            d = dec.get(h) or dec.get("mes:" + mes) or {}
            out.append({
                "mes": mes, "version_nombre": r0["version_nombre"], "archivo_proyecto": str(target.relative_to(ROOT)),
                "bytes": r0["bytes"], "sha256": h, "copias_identicas_encontradas": len(grp),
                "rutas_encontradas": " | ".join(x["ruta"].replace(str(HOME), "~") for x in grp),
                "contenidos_distintos_en_mes": len(by_hash),
                "url_declarada": d.get("url", ""), "fecha_publicacion_declarada": d.get("fecha_publicacion", ""),
                "pagina_origen_declarada": d.get("pagina_origen", ""),
                "procedencia_por_hash": "registro de descarga con mismo SHA-256" if h in dec else
                                        ("registro mensual previo (hash no comparado)" if d else "sin registro"),
                "verificado_contra_descarga_propia": "sí" if h == own else "no",
            })
    with open(ROOT / "fuentes" / "precios" / "manifiesto_originales_historicos.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)
    print(len(out), "archivos;", len(months), "meses")
    for r in out:
        if r["contenidos_distintos_en_mes"] > 1:
            print("VARIOS CONTENIDOS", r["mes"], r["archivo_proyecto"], r["bytes"])


if __name__ == "__main__":
    main()

"""Inventario y extracción literal de medidores candidatos desde originales locales.

Conserva D/R y etiquetas originales. No usa perfiles mensuales como serie horaria,
no infiere consumo por magnitud del canal y no estima fechas de tratamiento.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from datetime import datetime, timezone
import argparse
import csv
import gzip
import hashlib
import json
import shutil
import subprocess
import zipfile

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
CAT = ROOT / "SOCHER_2026_v6_multicentros/mapeo/socket_candidatos_extracto_20260924.csv"
RAW = ["ID_SOC", "IDSOCKET", "SUBESTACION", "TENSION", "YEARX", "MONX", "DAYX", "HOURX",
       "DATETIME", "UTCDATETIME", "kWhD", "kWhR", "FLUJO", "ULTIMA_LECTURA"]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def inventory():
    rows = []
    for year in range(2020, 2027):
        for p in sorted((ROOT / str(year)).glob("*/*/*")):
            if p.is_file() and p.suffix.lower() in (".zip", ".xlsx", ".xls"):
                rows.append({"anio_carpeta": year, "mes_carpeta": p.parent.parent.name,
                    "version_carpeta": p.parent.name, "archivo": str(p.relative_to(ROOT)),
                    "bytes": p.stat().st_size, "formato": p.suffix.lower(),
                    "definitivo": "definitiv" in p.parent.name.lower(),
                    "sha256": None, "estado_hash": "se_calcula_al_extraer_si_se_selecciona"})
    frame = pd.DataFrame(rows)
    frame.to_csv(BASE / "inventario_archivos_mediciones.csv", index=False)
    return frame


@contextmanager
def source_stream(path, z, member):
    if member.compress_type != 9:
        with z.open(member) as f:
            yield f
        return
    executable = shutil.which("7zz") or shutil.which("7z")
    if not executable:
        raise RuntimeError("El ZIP Deflate64 de diciembre 2023 requiere 7-Zip (7zz o 7z).")
    process = subprocess.Popen([executable, "x", "-so", "-bd", "-bsp0", str(path), member.filename],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        yield process.stdout
    finally:
        process.stdout.close()
        error = process.stderr.read().decode(errors="replace")
        code = process.wait()
        process.stderr.close()
        if code:
            raise RuntimeError(f"7-Zip no completó la lectura: {code}; {error[:500]}")


def extract(path, sockets):
    hierarchy = path.relative_to(BASE / "originales_descargados") if path.is_relative_to(BASE / "originales_descargados") else path.relative_to(ROOT)
    year = int(hierarchy.parts[0])
    month = int(hierarchy.parts[1][:2])
    out = BASE / "extractos" / f"medidores_candidatos_{year}_{month:02d}.csv.gz"
    manifest_path = out.with_name(out.name.replace(".csv.gz", "_manifest.json"))
    source_hash = sha(path)
    if out.exists() and manifest_path.exists():
        saved = json.loads(manifest_path.read_text())
        if saved["sha256_original"] == source_hash and saved["sha256_extracto"] == sha(out) and saved["sockets_buscados"] == sorted(sockets):
            print(f"{year}-{month:02d}: extracción verificada reutilizada", flush=True)
            return saved
    needle = [s.encode() for s in sorted({s.split("_")[0] for s in sockets})]
    dest = out.with_suffix(".gz.part")
    seen = {}
    record_count, lines_seen, total_bytes = 0, 1, 0
    with gzip.open(dest, "wt", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["archivo_original", "miembro_zip", "fila_csv_original"] + RAW)
        with zipfile.ZipFile(path) as z:
            members = [i for i in z.infolist() if i.filename.lower().endswith(".csv")]
            assert len(members) == 1, path
            member = members[0]
            with source_stream(path, z, member) as stream:
                header_bytes = stream.readline()
                header = next(csv.reader([header_bytes.decode("utf-8-sig").strip()], delimiter=";"))
                assert set(RAW[:-1]).issubset(header), (path, header)
                index = header.index("IDSOCKET")
                total_bytes += len(header_bytes)
                tail = b""
                while True:
                    chunk = stream.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    block = tail + chunk
                    stop = block.rfind(b"\n")
                    if stop < 0:
                        tail = block
                        continue
                    complete, tail = block[:stop], block[stop + 1:]
                    n_lines = complete.count(b"\n") + 1
                    if any(term in complete for term in needle):
                        for pos, line in enumerate(complete.split(b"\n"), 1):
                            if not any(term in line for term in needle):
                                continue
                            row = next(csv.reader([line.decode("utf-8-sig").rstrip("\r")], delimiter=";"))
                            assert len(row) == len(header), (path, lines_seen + pos)
                            if row[index] not in sockets:
                                continue
                            rec = dict(zip(header, row))
                            writer.writerow([str(path.relative_to(ROOT)), member.filename, lines_seen + pos] + [rec.get(c, "") for c in RAW])
                            record_count += 1
                            seen[row[index]] = seen.get(row[index], 0) + 1
                    lines_seen += n_lines
                if tail.strip():
                    lines_seen += 1
                    row = next(csv.reader([tail.decode("utf-8-sig").rstrip("\r")], delimiter=";"))
                    assert len(row) == len(header)
                    if row[index] in sockets:
                        rec = dict(zip(header, row))
                        writer.writerow([str(path.relative_to(ROOT)), member.filename, lines_seen] + [rec.get(c, "") for c in RAW])
                        record_count += 1
                        seen[row[index]] = seen.get(row[index], 0) + 1
    assert total_bytes == member.file_size
    dest.replace(out)
    manifest = {"fecha_utc": datetime.now(timezone.utc).isoformat(), "anio": year, "mes": month,
        "archivo_original": str(path.relative_to(ROOT)), "bytes_original": path.stat().st_size,
        "sha256_original": source_hash, "miembro_zip": member.filename,
        "bytes_csv_original": member.file_size, "bytes_csv_leidos": total_bytes,
        "lineas_csv_con_cabecera": lines_seen, "campos_originales": header,
        "compresion_zip": member.compress_type, "lector": "7-Zip en flujo para Deflate64" if member.compress_type == 9 else "zipfile estándar",
        "extracto": str(out.relative_to(BASE)), "sha256_extracto": sha(out),
        "filas_seleccionadas": record_count, "filas_por_socket": seen,
        "sockets_buscados": sorted(sockets), "tipo_fuente": "real_definitivo",
        "seleccion": "IDSOCKET exacto según catálogo candidato preservado, no vigencia histórica certificada"}
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{year}-{month:02d}: {record_count:,} registros, {len(seen)} sockets", flush=True)
    return manifest


def consolidate(sockets, catalog):
    parts, manifests = [], []
    for m in sorted((BASE / "extractos").glob("*_manifest.json")):
        meta = json.loads(m.read_text())
        p = BASE / meta["extracto"]
        assert sha(p) == meta["sha256_extracto"]
        d = pd.read_csv(p, dtype=str, keep_default_na=False)
        assert len(d) == meta["filas_seleccionadas"]
        d["sha256_original"] = meta["sha256_original"]
        d["archivo_extracto"] = str(p.relative_to(BASE))
        d["sha256_extracto"] = meta["sha256_extracto"]
        d["mes_archivo"] = f"{meta['anio']}-{meta['mes']:02d}"
        parts.append(d)
        manifests.append(meta)
    if not parts:
        return
    d = pd.concat(parts, ignore_index=True)
    d["etiqueta_utc"] = pd.to_datetime(d.UTCDATETIME, utc=True, errors="raise")
    local = pd.to_datetime(d.DATETIME, errors="raise")
    d["fecha_local"] = local.dt.strftime("%Y-%m-%d")
    d["mes_local"] = local.dt.strftime("%Y-%m")
    assert d.mes_local.eq(d.mes_archivo).all()
    assert not d.duplicated(["IDSOCKET", "etiqueta_utc"]).any()
    d["offset_local_min"] = ((local - d.etiqueta_utc.dt.tz_localize(None)).dt.total_seconds() / 60).astype("int64")
    d["zona_America_Santiago_coincide"] = local.eq(d.etiqueta_utc.dt.tz_convert("America/Santiago").dt.tz_localize(None))
    for c in ("D", "R"):
        d[f"energia_{c}_kwh"] = pd.to_numeric(d[f"kWh{c}"].str.replace(",", ".", regex=False), errors="coerce")
        invalid = d[f"kWh{c}"].ne("") & d[f"energia_{c}_kwh"].isna()
        assert not invalid.any(), d.loc[invalid, ["IDSOCKET", "DATETIME", f"kWh{c}"]].head()
        d[f"potencia_media_{c}_mw"] = d[f"energia_{c}_kwh"] / 250
    d["duracion_intervalo_minutos"] = 15
    d["inicio_fin_fisico_acreditado"] = False
    d["enlace_precio_habilitado"] = False
    d["fecha_tratamiento_validada"] = pd.NaT
    origin = catalog.set_index("punto_medida").origen_energia.to_dict()
    d["clasificacion_catalogo_20260924"] = d.IDSOCKET.map(origin)
    d["vigencia_historica_catalogo_validada"] = False
    ht12 = d.IDSOCKET.isin(["LSCANTRS_110_HT1_EDG", "LSCANTRS_110_HT2_EDG"])
    ht3 = d.IDSOCKET.eq("LSCANTRS_110_HT3_EDG")
    d["estado_polaridad"] = np.select([ht12, ht3],
        ["HT1_HT2_D_RETIRO_SEGUN_ACTAS_2023_CONTINUIDAD_A_REVISAR", "HT3_ORIENTACION_PENDIENTE"],
        default="CANALES_ORIGINALES_NO_ASIGNADOS_A_CONSUMO_CAMPUS")
    d = d.sort_values(["IDSOCKET", "etiqueta_utc"]).reset_index(drop=True)
    out = BASE / "tablas"
    d.to_parquet(out / "mediciones_candidatos_15min.parquet", index=False, compression="zstd")
    d.to_csv(out / "mediciones_candidatos_15min.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    quality = d.groupby(["IDSOCKET", "mes_local"]).agg(
        registros=("etiqueta_utc", "size"), fecha_local_desde=("DATETIME", "min"), fecha_local_hasta=("DATETIME", "max"),
        energia_D_kwh=("energia_D_kwh", lambda x: x.sum(min_count=1)), energia_R_kwh=("energia_R_kwh", lambda x: x.sum(min_count=1)),
        nulos_D=("energia_D_kwh", lambda x: x.isna().sum()), nulos_R=("energia_R_kwh", lambda x: x.isna().sum()),
        negativos_D=("energia_D_kwh", lambda x: x.lt(0).sum()), negativos_R=("energia_R_kwh", lambda x: x.lt(0).sum()),
        n_offsets=("offset_local_min", "nunique"), reloj_civil_coincide=("zona_America_Santiago_coincide", "all"))
    months = [f"{m['anio']}-{m['mes']:02d}" for m in manifests]
    quality = quality.reindex(pd.MultiIndex.from_product([sorted(sockets), sorted(months)], names=["IDSOCKET", "mes_local"]))
    quality["estado_presencia"] = np.where(quality.registros.notna(), "OBSERVADO", "SIN_REGISTRO_EN_ARCHIVO_EXAMINADO_NO_EQUIVALE_A_CERO")
    quality.registros = quality.registros.fillna(0).astype(int)
    quality.reset_index().to_csv(out / "cobertura_y_canales_por_mes.csv", index=False)
    report = {"filas": len(d), "sockets_observados": d.IDSOCKET.nunique(), "sockets_buscados": len(sockets),
        "archivos_originales_leidos": len(manifests), "desde_local": d.DATETIME.min(), "hasta_local": d.DATETIME.max(),
        "meses_examinados": sorted(months), "duplicados_socket_utc": 0,
        "reloj_civil_no_coincide": int((~d.zona_America_Santiago_coincide).sum()),
        "originales_bytes_suma": sum(m["bytes_original"] for m in manifests),
        "fuente_catalogo": str(CAT.relative_to(ROOT)), "sha256_catalogo": sha(CAT),
        "sin_estimacion_causal": True, "sin_imputacion_ausencias": True,
        "descargas_realizadas_por_este_script": 0, "manifiestos": [str(p.relative_to(BASE)) for p in sorted((BASE / "extractos").glob("*_manifest.json"))]}
    (BASE / "verificacion_ampliacion.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k not in ("manifiestos", "meses_examinados")}, ensure_ascii=False, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--anios", type=int, nargs="+", default=[2023, 2024, 2025, 2026])
    parser.add_argument("--solo-inventario", action="store_true")
    parser.add_argument("--consolidar", action="store_true", help="Solo consolida extractos existentes y verificados.")
    args = parser.parse_args()
    for path in [BASE, BASE / "extractos", BASE / "tablas", BASE / "fuentes"]:
        path.mkdir(parents=True, exist_ok=True)
    inv = inventory()
    if args.solo_inventario:
        print(inv.groupby(["anio_carpeta", "version_carpeta"]).agg(archivos=("archivo", "size"), bytes=("bytes", "sum")).to_string())
        return
    cat = pd.read_csv(CAT, keep_default_na=False)
    sockets = set(cat.punto_medida)
    assert len(sockets) == len(cat) == 30
    if not args.consolidar:
        paths = []
        for year in args.anios:
            paths.extend(p for p in (ROOT / str(year)).glob("*/Definitivo/*.zip")
                         if "Puntos_de_Medida" in p.name and not p.name.startswith("2_"))
            paths.extend(p for p in (BASE / "originales_descargados" / str(year)).glob("*/Definitivo/*.zip")
                         if "Puntos_de_Medida" in p.name and not p.name.startswith("2_"))
        paths = sorted(paths, key=str, reverse=True)
        assert paths
        with ThreadPoolExecutor(max_workers=2) as pool:
            work = [pool.submit(extract, p, sockets) for p in paths]
            for task in as_completed(work):
                task.result()
    consolidate(sockets, cat)


if __name__ == "__main__":
    main()

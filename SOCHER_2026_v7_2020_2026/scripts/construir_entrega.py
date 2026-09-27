#!/usr/bin/env python3
"""Entrega reproducible de precios DEF y capas de mediciones separadas.

Lee exclusivamente derivados locales: no descarga, no estima efectos, no imputa.
Las rutas se resuelven desde este archivo, no desde el directorio de ejecución.
"""
from __future__ import annotations

import argparse
import calendar
import csv
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
from datetime import date, datetime, timezone

import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / "entrega"
STEM = "Dataset_precios_barra_hora_2020_2026"
HIST = "historico_antes_20240715"
MOD = "CMg_Real_nuevo_desde_2024-07-15"
FIELDS = [
    ("fecha", "string", "Fecha civil rotulada en la fuente; no es fecha UTC."),
    ("anio", "int64", "Año de fecha."),
    ("mes", "string", "Mes civil YYYY-MM."),
    ("regimen_precio", "string", "Histórico hasta 14/07/2024 o nuevo CMg Real desde 15/07/2024."),
    ("barra_cmg", "string", "Etiqueta de barra seleccionada; no identifica necesariamente un activo estable entre meses."),
    ("barra_cmg_original", "string", "Etiqueta histórica original antes de normalización; moderna preservada literalmente."),
    ("codigo_fisico_mensual", "string", "Código de homologación mensual histórica exacta, si disponible; no se transporta entre meses."),
    ("nombre_fisico_mensual", "string", "Nombre de homologación histórica mensual, si disponible."),
    ("id_info_fuente", "string", "ID_INFO moderno original, puede estar vacío; no se imputa desde nombre."),
    ("barra_info_fuente", "string", "Nombre moderno original asociado a ID_INFO; texto original preservado."),
    ("familia_barra_historica", "string", "Familia usada por el filtro histórico; no es identidad física certificada."),
    ("estado_identidad", "string", "Estado de homologación/selección documentado por cada extractor."),
    ("barra_mes_id", "string", "Identificador de registro dentro de régimen y mes. No es identificador longitudinal."),
    ("hora_etiqueta_historica", "int64", "Etiqueta histórica 1–25. Vacía en régimen moderno. No convertir a UTC ni equiparar automáticamente con hora moderna."),
    ("hora_fuente_moderna", "int64", "HRA moderna 0–24 original. Vacía en histórico. Conserva la numeración fuente."),
    ("precio_usd_mwh", "float64", "Precio histórico publicado o media moderna sólo con cuatro intervalos 0,15,30,45. USD/MWh."),
    ("precio_usd_mwh_media_intervalos", "float64", "Media moderna de intervalos observados, incluso si hora incompleta; vacía en histórico. No sustituye automáticamente al precio horario válido."),
    ("precio_clp_kwh", "float64", "Precio moderno CLP/kWh sólo para horas completas; vacío en histórico."),
    ("n_intervalos", "int64", "Cantidad de intervalos modernos observados. Vacía en histórico (fuente ya horaria)."),
    ("minutos_observados", "string", "Minutos modernos observados, separados por coma; vacíos en histórico."),
    ("hora_completa_4_intervalos", "bool", "Validez de agregación moderna 15→60 minutos. Vacía en histórico, no falsa."),
    ("version_fuente", "string", "DEF histórico o REAL-DEF moderno. PRE se entrega en otro archivo."),
    ("fuente_id", "string", "Llave a Fuentes_precios.csv: archivos, SHA-256, unidades, reloj y método."),
    ("fila_fuente", "int64", "Fila del libro histórico. En moderno, trazabilidad al TSV y capa de intervalos mediante fuente_id."),
    ("columna_fuente", "int64", "Columna del libro histórico; vacía en moderno."),
    ("precio_ref_quillota_110_usd_mwh", "float64", "Precio de QUILLOTA______110 con coincidencia exacta única de fecha y hora dentro del mismo mes/régimen. Referencia descriptiva, no control causal."),
    ("diferencial_quillota_110_usd_mwh", "float64", "precio_usd_mwh menos precio_ref_quillota_110_usd_mwh. Vacío si falta cualquiera, referencia ambigua o hora incompleta."),
    ("id_ref_quillota_110", "string", "barra_mes_id de la observación única de referencia Quillota 110 con precio válido; no identidad longitudinal."),
    ("precio_ref_quillota_220_usd_mwh", "float64", "Precio de QUILLOTA______220 con coincidencia exacta única de fecha y hora dentro del mismo mes/régimen. Referencia descriptiva, no control causal."),
    ("diferencial_quillota_220_usd_mwh", "float64", "precio_usd_mwh menos precio_ref_quillota_220_usd_mwh. Vacío si falta cualquiera, referencia ambigua o hora incompleta."),
    ("id_ref_quillota_220", "string", "barra_mes_id de la observación única de referencia Quillota 220 con precio válido; no identidad longitudinal."),
]
TYPES = {"string": pa.string(), "int64": pa.int64(), "float64": pa.float64(), "bool": pa.bool_()}
SCHEMA = pa.schema([pa.field(n, TYPES[t]) for n, t, _ in FIELDS])


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def relative(path) -> str:
    p = Path(path)
    if not p.is_absolute():
        return str(p)
    # Manifiestos antiguos pueden conservar el directorio del equipo original.
    # Resolver por el ancla del proyecto permite relocalizar el paquete sin
    # publicar rutas personales ni reescribir manifiestos con sus hashes.
    marker = "/" + BASE.name + "/"
    if marker in str(p):
        return str(p).split(marker, 1)[1]
    for legacy in ["SOCHER_2026_v4", "SOCHER_2026_v3", "SOCHER_2026_v2", "SOCHER_2026_v6"]:
        marker = "/" + legacy + "/"
        if marker in str(p):
            return "../" + legacy + "/" + str(p).split(marker, 1)[1]
    return "origen_externo/" + p.name


def save_csv(rows, path, columns=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=columns).to_csv(path, index=False, encoding="utf-8", lineterminator="\n")


def month_range(start, end):
    return [p.strftime("%Y%m") for p in pd.period_range(start, end, freq="M")]


def expected_inputs():
    return [("historico", m, BASE / f"historico/derivados/precios_{m}.parquet")
            for m in month_range("2020-01", "2024-07")] + [
        ("moderno", m, BASE / f"moderno/datos/{m}_DEF_horario.parquet")
        for m in month_range("2024-07", "2026-09")]


def ready(kind, m, path):
    control = BASE / (f"historico/manifiestos/precios_{m}.json" if kind == "historico"
                      else f"moderno/fuentes/metadatos/{m}_DEF_extraccion.json")
    if not path.exists() or not control.exists():
        return False
    meta = json.loads(control.read_text())
    if kind == "moderno" and meta.get("schema_version") != "moderno_v7.1":
        return False
    key = relative(path) if kind == "historico" else str(path.relative_to(BASE / "moderno"))
    return meta.get("outputs", {}).get(key) == sha(path)


def normalize(path: Path, kind: str, m: str, version="DEF"):
    d = pd.read_parquet(path)
    assert not d.empty, f"Fuente vacía: {path}"
    d["fecha"] = d["fecha"].astype(str)
    assert d.fecha.str.startswith(f"{m[:4]}-{m[4:]}").all(), path
    n = pd.DataFrame(index=d.index, columns=[x[0] for x in FIELDS])
    n["fecha"] = d.fecha
    n["anio"] = d.fecha.str[:4].astype(int)
    n["mes"] = d.fecha.str[:7]
    n["barra_cmg"] = d.barra_cmg
    n["fuente_id"] = f"{kind}_{m}_{version}"
    source = {"fuente_id": f"{kind}_{m}_{version}", "archivo_derivado": relative(path),
              "sha256_derivado": sha(path), "filas": len(d), "version": version}
    if kind == "historico":
        assert d.version_fuente.eq("DEF").all() and d.fecha.lt("2024-07-15").all()
        assert d.hora_etiqueta.between(1, 25).all()
        assert not d.duplicated(["fecha", "hora_etiqueta", "barra_cmg"]).any()
        mapping = {"regimen_precio": "regimen_precio", "barra_cmg_original": "barra_cmg_original",
                   "codigo_fisico_mensual": "codigo_fisico", "nombre_fisico_mensual": "nombre_fisico",
                   "familia_barra_historica": "familia_barra", "estado_identidad": "estado_identidad",
                   "hora_etiqueta_historica": "hora_etiqueta", "precio_usd_mwh": "precio_usd_mwh",
                   "version_fuente": "version_fuente", "fila_fuente": "fila_fuente", "columna_fuente": "columna_fuente"}
        manifest = json.loads((BASE / f"historico/manifiestos/precios_{m}.json").read_text())
        source.update(archivo_original=relative(manifest["libro"]), sha256_original=manifest["libro_sha256"],
                      semantica_hora="etiqueta_fuente_1_25_sin_conversion_UTC",
                      unidad_precio_original="mills/kWh", factor_numerico_usd_mwh=1,
                      metodo_precio="valor_horario_publicado", archivo_control=f"historico/manifiestos/precios_{m}.json")
        catalog = BASE / "historico/catalogo/definitivos_cmg_2020_2024.csv"
        if catalog.exists():
            entries = pd.read_csv(catalog, dtype=str, keep_default_na=False)
            match = entries.loc[entries.mes.eq(m)]
            if len(match) == 1:
                e = match.iloc[0]
                source.update(url_original=e.url_archivo, url_indice=e.url_indice,
                              titulo_oficial=e.titulo_oficial, fecha_publicacion_literal=e.fecha_publicacion_literal)
        for a, b in mapping.items():
            n[a] = d[b]
        n["barra_mes_id"] = "H|" + n.mes + "|" + n.barra_cmg
    else:
        assert d.version.eq("REAL-" + version).all() and d.fecha.ge("2024-07-15").all()
        assert d.hora_fuente.between(0, 24).all()
        assert not d.duplicated(["id_info", "barra_cmg", "fecha", "hora_fuente", "version"]).any()
        assert d.loc[~d.hora_completa_4_intervalos, "precio_usd_mwh_horario"].isna().all()
        assert d.loc[d.hora_completa_4_intervalos, "n_intervalos"].eq(4).all()
        assert d.loc[d.hora_completa_4_intervalos, "minutos_observados"].eq("0,15,30,45").all()
        mapping = {"regimen_precio": "regimen", "id_info_fuente": "id_info", "barra_info_fuente": "barra_info",
                   "estado_identidad": "identidad", "hora_fuente_moderna": "hora_fuente",
                   "precio_usd_mwh": "precio_usd_mwh_horario", "precio_usd_mwh_media_intervalos": "precio_usd_mwh_media",
                   "precio_clp_kwh": "precio_clp_kwh_horario", "n_intervalos": "n_intervalos",
                   "minutos_observados": "minutos_observados", "hora_completa_4_intervalos": "hora_completa_4_intervalos",
                   "version_fuente": "version"}
        for a, b in mapping.items():
            n[a] = d[b]
        n["barra_cmg_original"] = d.barra_cmg
        n["barra_mes_id"] = "M|" + n.mes + "|" + d.id_info.fillna("").astype(str) + "|" + n.barra_cmg
        original_meta = json.loads((BASE / f"moderno/fuentes/metadatos/{m}_{version}.json").read_text())
        source.update(archivo_original="moderno/fuentes/tsv_originales/" + str(d.archivo_fuente.iloc[0]),
                      sha256_original=original_meta["sha256_gzip_local"],
                      sha256_contenido_tsv_descomprimido=d.sha256_tsv_fuente.iloc[0], url_original=original_meta["url"],
                      semantica_hora=d.unidad_temporal_fuente.iloc[0],
                      unidad_precio_original=d.unidad_precio_fuente.iloc[0], factor_numerico_usd_mwh=1,
                      metodo_precio="media_aritmetica_solo_4_intervalos_0_15_30_45",
                      archivo_control=f"moderno/fuentes/metadatos/{m}_{version}_extraccion.json")
    for name, typ, _ in FIELDS:
        if typ == "string":
            n[name] = n[name].astype("string").replace("", pd.NA)
        elif typ == "int64":
            n[name] = pd.to_numeric(n[name], errors="raise").astype("Int64")
        elif typ == "float64":
            n[name] = pd.to_numeric(n[name], errors="raise").astype("float64")
        else:
            n[name] = n[name].astype("boolean")
    h = "hora_etiqueta_historica" if kind == "historico" else "hora_fuente_moderna"
    n = n.sort_values(["fecha", h, "barra_mes_id"], kind="stable").reset_index(drop=True)
    assert not n.duplicated(["barra_mes_id", "fecha", h]).any()
    # Las referencias son contemporáneas dentro de esta partición. Dos
    # observaciones candidatas para una hora vuelven ambigua la referencia.
    keys = ["fecha", h]
    target = pd.MultiIndex.from_frame(n[keys])
    for voltage in [110, 220]:
        label = f"QUILLOTA______{voltage}"
        reference = n.loc[n.barra_cmg.eq(label)].copy()
        reference = reference.loc[~reference.duplicated(keys, keep=False) & reference.precio_usd_mwh.notna()]
        reference = reference.set_index(keys).reindex(target)
        pcol = f"precio_ref_quillota_{voltage}_usd_mwh"
        dcol = f"diferencial_quillota_{voltage}_usd_mwh"
        icol = f"id_ref_quillota_{voltage}"
        n[pcol] = reference.precio_usd_mwh.to_numpy(dtype=float)
        n[dcol] = n.precio_usd_mwh - n[pcol]
        n[icol] = pd.array(reference.barra_mes_id, dtype="string")
        assert n.loc[n.barra_cmg.eq(label) & n[pcol].notna(), dcol].eq(0).all()
    source.update(fecha_desde=n.fecha.min(), fecha_hasta=n.fecha.max(), regimen_precio=n.regimen_precio.iloc[0])
    return n, source


def inspect_coverage(n, kind, m, asof):
    h = "hora_etiqueta_historica" if kind == "historico" else "hora_fuente_moderna"
    grid = set(zip(n.fecha, n[h]))
    missing, bars = [], []
    for label, g in n.groupby("barra_cmg", sort=True):
        first = g.iloc[0]
        absent = sorted(grid - set(zip(g.fecha, g[h])))
        def values(column):
            return ";".join(sorted(g[column].dropna().astype(str).unique()))
        bars.append(dict(anio=int(m[:4]), mes=f"{m[:4]}-{m[4:]}", regimen_precio=first.regimen_precio,
                         barra_cmg=label, barra_mes_ids_observados=values("barra_mes_id"),
                         identificadores_mensuales=g.barra_mes_id.nunique(), codigo_fisico_mensual=values("codigo_fisico_mensual"),
                         id_info_fuente=values("id_info_fuente"), estado_identidad=values("estado_identidad"),
                         filas=len(g), precios_validos=int(g.precio_usd_mwh.notna().sum()), dias=g.fecha.nunique(),
                         fecha_desde=g.fecha.min(), fecha_hasta=g.fecha.max(),
                         etiquetas_union_del_mes=len(grid), ausencias_frente_union_del_mes=len(absent)))
        for dt, hr in absent:
            missing.append(dict(tipo="barra_ausente_en_etiqueta_observada_en_otras_barras", mes=f"{m[:4]}-{m[4:]}",
                                regimen_precio=first.regimen_precio, barra_mes_id="", barra_cmg=label,
                                fecha=dt, hora_fuente=int(hr), detalle="Comparación dentro del mismo régimen y mes; no demuestra vigencia faltante ni autoriza imputación."))
    for row in n.loc[n.precio_usd_mwh.isna()].itertuples(index=False):
        missing.append(dict(tipo="precio_horario_no_disponible_en_fila", mes=row.mes, regimen_precio=row.regimen_precio,
                            barra_mes_id=row.barra_mes_id, barra_cmg=row.barra_cmg, fecha=row.fecha,
                            hora_fuente=int(getattr(row, h)), detalle="Fila preservada; verificar intervalos y fuente."))
    start = date(int(m[:4]), int(m[4:]), 1)
    end = date(start.year, start.month, calendar.monthrange(start.year, start.month)[1])
    if kind == "historico":
        end = min(end, date(2024, 7, 14))
    else:
        start = max(start, date(2024, 7, 15))
    end = min(end, asof)
    dates = set(n.fecha)
    for day in pd.date_range(start, end):
        dt = day.strftime("%Y-%m-%d")
        if dt not in dates:
            missing.append(dict(tipo="dia_sin_DEF_en_seleccion_hasta_fecha_corte", mes=f"{m[:4]}-{m[4:]}",
                                regimen_precio=n.regimen_precio.iloc[0], barra_mes_id="", barra_cmg="", fecha=dt,
                                hora_fuente="", detalle="Ausencia de día en la fuente seleccionada; no se añaden 24 filas ni se presume horario DST."))
    if kind == "historico":
        manifest = json.loads((BASE / f"historico/manifiestos/precios_{m}.json").read_text())
        for entry in manifest.get("faltantes_explicitos", []):
            missing.append(dict(tipo="celda_historica_vacia_reportada_por_extractor", mes=f"{m[:4]}-{m[4:]}",
                                regimen_precio=HIST, barra_mes_id="", barra_cmg="", fecha="", hora_fuente="",
                                detalle=json.dumps(entry, ensure_ascii=False)))
    monthly = dict(anio=int(m[:4]), mes=f"{m[:4]}-{m[4:]}", regimen_precio=n.regimen_precio.iloc[0],
                   filas=len(n), barras_etiqueta=n.barra_cmg.nunique(), identidades_mensuales=n.barra_mes_id.nunique(),
                   dias=n.fecha.nunique(), fecha_desde=n.fecha.min(), fecha_hasta=n.fecha.max(),
                   precios_validos=int(n.precio_usd_mwh.notna().sum()), precios_nulos=int(n.precio_usd_mwh.isna().sum()),
                   etiquetas_union_del_mes=len(grid), archivo_fuente_id=n.fuente_id.iloc[0])
    for voltage in [110, 220]:
        monthly[f"filas_sin_referencia_quillota_{voltage}"] = int(n[f"precio_ref_quillota_{voltage}_usd_mwh"].isna().sum())
        monthly[f"diferenciales_validos_quillota_{voltage}"] = int(n[f"diferencial_quillota_{voltage}_usd_mwh"].notna().sum())
    return monthly, bars, missing


def export_measurements(out):
    dest = out / "mediciones_separadas"
    dest.mkdir(parents=True, exist_ok=True)
    result = []
    names = ["carga_HT1_HT2_hora_etiqueta", "dataluna_horario_2020_2022_no_homologado",
             "dataluna_horario_2023_01_no_homologado", "mediciones_canales_horarios_2023_01_04"]
    for name in names:
        p = BASE / "mediciones/tablas" / (name + ".parquet")
        d = pd.read_parquet(p)
        d["capa_fuente"] = relative(p)
        d["sha256_capa_fuente"] = sha(p)
        if name == "carga_HT1_HT2_hora_etiqueta":
            d["unidad_energia_D_R"] = "kWh"
            d["unidad_media_horaria_D_R"] = "MW"
            d["metodo_agregacion"] = "suma_HT1_HT2_con_4_pares_15min; kWh/1000_por_hora_de_etiquetas"
            d["capa_15min_trazable"] = "mediciones/tablas/mediciones_candidatos_15min.parquet"
        d.to_csv(dest / (name + ".csv"), index=False, encoding="utf-8", lineterminator="\n")
        result.append({"archivo": "mediciones_separadas/" + name + ".csv", "filas": len(d),
                       "columnas": len(d.columns), "fuente": relative(p), "sha256_fuente": sha(p)})
    shutil.copyfile(BASE / "mediciones/Cobertura_mediciones_2020_2026.md", dest / "Cobertura_mediciones_2020_2026.md")
    return result


def verify(out):
    manifest = json.loads((out / "Manifiesto_entrega.json").read_text())
    errors = []
    for entry in manifest["archivos"]:
        p = out / entry["archivo"]
        if not p.exists() or p.stat().st_size != entry["bytes"] or sha(p) != entry["sha256"]:
            errors.append("Archivo ausente o diferente: " + entry["archivo"])
    parquet_file = pq.ParquetFile(out / (STEM + ".parquet"))
    parquet_rows = parquet_file.metadata.num_rows
    csv_rows, by_year, null_prices = 0, {}, 0
    reader = pacsv.open_csv(out / (STEM + ".csv"), convert_options=pacsv.ConvertOptions(
        include_columns=["anio", "precio_usd_mwh"], column_types={"anio": pa.int64(), "precio_usd_mwh": pa.float64()}))
    for batch in reader:
        csv_rows += batch.num_rows
        null_prices += batch.column("precio_usd_mwh").null_count
        series = batch.column("anio").to_pandas().value_counts()
        for year, count in series.items():
            by_year[str(year)] = by_year.get(str(year), 0) + int(count)
    if not (csv_rows == parquet_rows == manifest["filas_precios_DEF"]):
        errors.append("Conteo CSV/Parquet/manifiesto no coincide")
    # Comparar todas las celdas de CSV/Parquet en bloques acotados. CSV y Parquet
    # usan la misma convención de nulos: campo vacío, nunca cero o texto 'nan'.
    full_csv_reader = pacsv.open_csv(out / (STEM + ".csv"), read_options=pacsv.ReadOptions(block_size=4 * 1024 * 1024),
        convert_options=pacsv.ConvertOptions(column_types=SCHEMA, null_values=[""], strings_can_be_null=True,
            true_values=["True", "true"], false_values=["False", "false"]))
    if not full_csv_reader.schema.equals(SCHEMA, check_metadata=False) or not parquet_file.schema_arrow.equals(SCHEMA, check_metadata=False):
        errors.append("Esquema CSV/Parquet no coincide con diccionario")
    p_iter = parquet_file.iter_batches(batch_size=65536)
    c_iter = iter(full_csv_reader)
    p_batch, c_batch = next(p_iter, None), next(c_iter, None)
    p_offset, c_offset, compared, maximum_error = 0, 0, 0, 0.0
    mismatches = []
    while p_batch is not None and c_batch is not None:
        size = min(p_batch.num_rows - p_offset, c_batch.num_rows - c_offset)
        for index, (name, typ, _) in enumerate(FIELDS):
            a = p_batch.column(index).slice(p_offset, size)
            b = c_batch.column(index).slice(c_offset, size)
            if not pc.is_null(a).equals(pc.is_null(b)):
                mismatches.append(f"Máscara nula diferente: {name}, desde fila {compared + 1}")
            elif typ == "float64":
                error = pc.max(pc.abs(pc.subtract(a, b))).as_py() or 0.0
                maximum_error = max(maximum_error, error)
                if error > 1e-10:
                    mismatches.append(f"Diferencia numérica {error}: {name}, desde fila {compared + 1}")
            elif not a.equals(b):
                mismatches.append(f"Valores diferentes: {name}, desde fila {compared + 1}")
        compared += size; p_offset += size; c_offset += size
        if len(mismatches) > 20:
            break
        if p_offset == p_batch.num_rows:
            p_batch, p_offset = next(p_iter, None), 0
        if c_offset == c_batch.num_rows:
            c_batch, c_offset = next(c_iter, None), 0
    if compared != csv_rows or p_batch is not None or c_batch is not None:
        mismatches.append("La comparación completa de filas CSV/Parquet no terminó simultáneamente")
    errors.extend(mismatches)
    # Concatenar en flujo todos los CSV anuales y un solo encabezado. Su hash
    # debe coincidir byte por byte con el principal, acreditando todos los campos.
    annual_hash, annual_header = hashlib.sha256(), None
    for year in sorted(by_year):
        with (out / "por_anio" / f"Dataset_precios_barra_hora_{year}.csv").open("rb") as f:
            header = f.readline()
            if annual_header is None:
                annual_header = header; annual_hash.update(header)
            elif header != annual_header:
                errors.append("Encabezado anual distinto: " + year)
            for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
                annual_hash.update(block)
    annual_exact = annual_hash.hexdigest() == sha(out / (STEM + ".csv"))
    if not annual_exact:
        errors.append("Concatenación anual no reproduce exactamente CSV principal")
    h = hashlib.sha256()
    with gzip.open(out / (STEM + ".csv.gz"), "rb") as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(block)
    if h.hexdigest() != sha(out / (STEM + ".csv")):
        errors.append("CSV gzip no reproduce exactamente CSV")
    for year, count in by_year.items():
        rows = sum(batch.num_rows for batch in pacsv.open_csv(out / "por_anio" / f"Dataset_precios_barra_hora_{year}.csv",
                   convert_options=pacsv.ConvertOptions(include_columns=["anio"], column_types={"anio": pa.int64()})))
        if rows != count:
            errors.append("Conteo anual incorrecto: " + year)
    result = dict(estado="OK" if not errors else "ERROR", errores=errors, filas_csv=csv_rows,
                  filas_parquet=parquet_rows, filas_por_anio=by_year, precios_nulos=null_prices,
                  filas_comparadas_todas_columnas=compared, columnas_comparadas=len(FIELDS),
                  tolerancia_absoluta_flotantes=1e-10, error_maximo_flotantes=maximum_error,
                  concatenacion_anual_identica_csv=annual_exact,
                  sha256_archivos_verificados=len(manifest["archivos"]), gzip_identico_csv=True if not errors else None,
                  utc=datetime.now(timezone.utc).isoformat())
    (out / "Verificacion_entrega.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, ensure_ascii=False), flush=True)
    return 0 if not errors else 1


def build(out, allow_partial, asof):
    inputs = expected_inputs()
    available = [x for x in inputs if ready(*x)]
    absent = [x for x in inputs if x not in available]
    if absent and not allow_partial:
        raise SystemExit(f"Faltan {len(absent)} de 82 archivos DEF. Espere la extracción o use --permitir-parcial --salida entrega_ensayo. " + ", ".join(f"{k}:{m}" for k, m, _ in absent))
    out.mkdir(parents=True, exist_ok=True)
    (out / "por_anio").mkdir(exist_ok=True)
    # Archivos producidos se reescriben; no se borran otros documentos de la carpeta.
    source_rows, coverage, bars, missing = [], [], [], []
    for kind, m, p in absent:
        missing.append(dict(tipo="archivo_mensual_DEF_no_disponible_localmente", mes=f"{m[:4]}-{m[4:]}",
                            regimen_precio=HIST if kind == "historico" else MOD, barra_mes_id="", barra_cmg="", fecha="", hora_fuente="", detalle=relative(p)))
    writer = pq.ParquetWriter(out / (STEM + ".parquet"), SCHEMA, compression="zstd")
    total, yearly_seen, labels_year = 0, set(), {}
    with (out / (STEM + ".csv")).open("w", encoding="utf-8", newline="") as full:
        try:
            for kind, m, p in sorted(available, key=lambda x: (x[1], x[0])):
                n, source = normalize(p, kind, m)
                assert n.fecha.le(asof.isoformat()).all(), "Hay fechas posteriores al corte solicitado"
                table = pa.Table.from_pandas(n, schema=SCHEMA, preserve_index=False)
                writer.write_table(table)
                n.to_csv(full, index=False, header=total == 0, lineterminator="\n")
                year = m[:4]
                n.to_csv(out / "por_anio" / f"Dataset_precios_barra_hora_{year}.csv", mode="a" if year in yearly_seen else "w",
                         index=False, header=year not in yearly_seen, encoding="utf-8", lineterminator="\n")
                yearly_seen.add(year)
                labels_year.setdefault(int(year), set()).update(n.barra_cmg.dropna().tolist())
                total += len(n)
                source_rows.append(source)
                month, month_bars, gaps = inspect_coverage(n, kind, m, asof)
                coverage.append(month); bars.extend(month_bars); missing.extend(gaps)
                print(f"{kind} {m}: {len(n):,} filas; acumuladas {total:,}", flush=True)
        finally:
            writer.close()
    if not total:
        raise SystemExit("No hay fuentes completas para producir la entrega")
    with (out / (STEM + ".csv")).open("rb") as src, gzip.GzipFile(filename=str(out / (STEM + ".csv.gz")), mode="wb", compresslevel=6, mtime=0) as dst:
        shutil.copyfileobj(src, dst, 4 * 1024 * 1024)
    save_csv(source_rows, out / "Fuentes_precios.csv")
    save_csv(coverage, out / "Cobertura_por_mes_regimen.csv")
    save_csv(bars, out / "Cobertura_por_mes_barra.csv")
    save_csv(missing, out / "Faltantes_precios_detalle.csv", ["tipo", "mes", "regimen_precio", "barra_mes_id", "barra_cmg", "fecha", "hora_fuente", "detalle"])
    annual = pd.DataFrame(coverage).groupby("anio", as_index=False).agg(filas=("filas", "sum"), precios_validos=("precios_validos", "sum"), precios_nulos=("precios_nulos", "sum"),
                    meses=("mes", "nunique"), fecha_desde=("fecha_desde", "min"), fecha_hasta=("fecha_hasta", "max"))
    annual["barras_etiquetas_distintas_no_identidades_estables"] = annual.anio.map(lambda y: len(labels_year[y]))
    annual.to_csv(out / "Cobertura_por_anio.csv", index=False, encoding="utf-8")
    save_csv([dict(variable=n, tipo=t, descripcion=desc) for n, t, desc in FIELDS], out / "Diccionario_precios.csv")
    measurements = export_measurements(out)
    pre = []
    for p in sorted((BASE / "moderno/datos").glob("*_PRE_horario.parquet")):
        n, source = normalize(p, "moderno", p.name[:6], version="PRE")
        assert n.fecha.le(asof.isoformat()).all(), "PRE contiene fechas posteriores al corte solicitado"
        dest = out / "preliminares_separados"; dest.mkdir(exist_ok=True)
        n.to_csv(dest / (p.stem + ".csv"), index=False, encoding="utf-8", lineterminator="\n")
        pre.append(source)
    if pre:
        save_csv(pre, out / "preliminares_separados/Fuentes_PRE.csv")
    manifest = dict(fecha_corte=asof.isoformat(), creado_utc=datetime.now(timezone.utc).isoformat(),
                    alcance="barras seleccionadas para el artículo; no universo nacional ni panel causal equilibrado",
                    estado="82_fuentes_DEF_integradas" if not absent else "PARCIAL_fuentes_pendientes",
                    fuentes_DEF_esperadas=82, fuentes_DEF_integradas=len(source_rows), fuentes_DEF_pendientes=len(absent),
                    filas_precios_DEF=total, fecha_desde=min(x["fecha_desde"] for x in coverage), fecha_hasta=max(x["fecha_hasta"] for x in coverage),
                    filas_faltantes_documentados=len(missing), fuentes_PRE_separadas=len(pre), mediciones=measurements,
                    estimaciones_causales=False, precios_unidos_a_consumo=False, UTC_precios_inferido=False,
                    script=relative(Path(__file__)), sha256_script=sha(Path(__file__)))
    guide(out, manifest, annual)
    manifest["archivos"] = [{"archivo": str(p.relative_to(out)), "bytes": p.stat().st_size, "sha256": sha(p)}
                            for p in sorted(out.rglob("*")) if p.is_file() and "ensayo" not in p.relative_to(out).parts
                            and p.name not in {"Manifiesto_entrega.json", "Verificacion_entrega.json"}]
    (out / "Manifiesto_entrega.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    return verify(out)


def guide(out, manifest, annual):
    text = f"""# Dataset de precios y mediciones para el artículo SOCHER

La entrega contiene **{manifest['filas_precios_DEF']:,} registros de precio de barras seleccionadas**, desde **{manifest['fecha_desde']} hasta {manifest['fecha_hasta']}**. Fecha de corte de la revisión: {manifest['fecha_corte']}. Se integraron {manifest['fuentes_DEF_integradas']} de 82 fuentes mensuales esperadas (55 históricas y 27 modernas). Estado: **{manifest['estado']}**. El nombre 2020–2026 describe el período de estudio, no significa que 2026 esté completo.

## Archivo que se debe abrir

- `{STEM}.csv` es la base principal: una fila por etiqueta de barra, fecha y hora de la fuente dentro del régimen. CSV UTF-8, separador coma, decimal punto, encabezado y campos vacíos para datos no disponibles. Conservar códigos como texto.
- `por_anio/` contiene la misma base dividida por año, sin duplicar observaciones dentro de cada archivo. La unión de esos archivos equivale al principal.
- `{STEM}.csv.gz` descomprime al mismo CSV. `{STEM}.parquet` conserva tipos y ocupa menos espacio.
- `Diccionario_precios.csv` explica todas las variables. `Fuentes_precios.csv` relaciona cada `fuente_id` con su archivo original, derivado, hash, unidades y método.
- `Cobertura_por_anio.csv`, `Cobertura_por_mes_regimen.csv` y `Cobertura_por_mes_barra.csv` muestran la cobertura real. `Faltantes_precios_detalle.csv` identifica archivos pendientes, días ausentes hasta la fecha de corte, precios horarios inválidos y huecos respecto de etiquetas observadas en otras barras del mismo mes.

## Cómo interpretar el tiempo, el precio y la barra

El histórico termina el 14 de julio de 2024 y conserva `hora_etiqueta_historica` (1–25). El régimen moderno comienza el 15 de julio y conserva `hora_fuente_moderna` (0–24). Ambas son etiquetas originales. No se deduce UTC, no se resta automáticamente una unidad ni se unen ambas horas a mediciones. No se completa una cuadrícula artificial de 24 horas por día: los cambios de hora requieren una concordancia documental específica.

El histórico conserva el valor horario publicado. En el moderno, `precio_usd_mwh` sólo se calcula si existen los cuatro minutos 0, 15, 30 y 45; `precio_usd_mwh_media_intervalos` preserva la media disponible para auditar las horas incompletas. Un mill/kWh equivale numéricamente a un USD/MWh. El precio local moderno se conserva aparte como CLP/kWh. No se hace conversión de moneda con un tipo de cambio inventado.

Las seis columnas de referencia añaden el precio de Quillota 110 y 220, el diferencial nodo menos referencia y el identificador mensual de cada referencia. Se exigen las etiquetas exactas `QUILLOTA______110` y `QUILLOTA______220`, una sola observación con esa fecha y hora en el mismo mes/régimen y un precio horario válido. Si falta o hay más de una candidata, las tres columnas de esa referencia quedan vacías. El precio original no se modifica. Estos diferenciales son descriptivos: Quillota puede recibir el mismo choque y no se presume un control causal no afectado.

`barra_mes_id` sirve como llave dentro de cada mes y régimen. No acredita una identidad longitudinal. Los códigos históricos provienen únicamente de homologaciones mensuales exactas; los ID_INFO modernos se conservan cuando la fuente los informa. No se rellena una identidad con meses vecinos ni se presume que dos nombres iguales representen un mismo activo en todo 2020–2026. La selección reúne barras relacionadas con el diseño del artículo y sus referencias, no todos los nodos del país.

La llave de fila es `barra_mes_id`, `fecha` y la columna de hora aplicable al régimen. `version_fuente` es DEF o REAL-DEF. Los archivos PRE, cuando existen, están en `preliminares_separados/` y no complementan ni reemplazan valores de la base definitiva.

Se utilizan los definitivos del índice histórico. Existen reliquidaciones posteriores, en particular para 2022, que se inventarían separadamente y no se mezclan aquí. DEF no significa que se haya seleccionado la revisión más reciente de cada fecha.

Una comparación con la exportación local anterior encontró diferencias en octubre de 2023 aun usando códigos físicos coincidentes. Se conserva el valor de estos libros DEF y su versión, sin llenar huecos con aquella exportación. El informe `../auditoria/Comparacion_DEF_con_exportacion_local.json` documenta esa discrepancia y evita confundir cambios de versión con errores de extracción o efectos económicos.

Los faltantes respecto de la unión de etiquetas del mes son un diagnóstico de desigualdad de cobertura: no prueban que una barra existiera antes de su primera observación o después de la última. Si todas las barras omiten simultáneamente una hora, esta comparación no puede detectarla. Los días enteros ausentes se enumeran por separado. Meses posteriores a septiembre de 2026 y fechas posteriores al corte no se crean como observaciones.

## Mediciones que se entregan separadamente

`mediciones_separadas/` contiene cuatro CSV horarios y su guía específica:

- HT1 + HT2: 21.912 horas completas de etiquetas, febrero de 2024–agosto de 2026; faltan enero y abril de 2024. D y R se mantienen separados, en kWh y media MW. Se exigen cuatro pares de intervalos. HT3 y líneas de tránsito se excluyen. No representa automáticamente consumo total del campus. El archivo conserva reloj explícito y las banderas de validación pendientes.
- DATALUNA 2020–2022: 20.447 horas observadas desde septiembre de 2020, con unidad y signo histórico todavía no homologados a consumo MW.
- DATALUNA enero de 2023: 744 valores horarios originales, también sin unidad homologada.
- Canales horarios de febrero–abril de 2023: 8.548 registros hora × canal de H1/H2 de TAP Libertadores; energía rotulada kWh y signo original conservado. Son canales de tránsito, no una medición independiente del consumo de un campus.

La capa completa de 1.862.581 observaciones de 15 minutos de 30 sockets está en `../mediciones/tablas/mediciones_candidatos_15min.parquet` y `.csv.gz` desde esta carpeta. No son 30 centros de datos. Las fuentes y unidades se conservan en cada capa; el reloj físico inicio/fin y la vigencia de algunas correspondencias siguen pendientes. Los CSV de mediciones no se han unido a precios y la aparición de un socket no se usa como inauguración.

## Uso en la investigación

Esta entrega permite describir y comparar cobertura y precios. ATT, DiD escalonado, estudio de eventos y spillovers necesitan todavía fechas de entrada acreditadas, correspondencia centro–nodo vigente, diseño de comparación y validación del reloj. El CSV no contiene tratamientos inferidos, efectos estimados ni resultados causales.

## Reproducción y control

Desde la raíz del proyecto, ejecutar `.venv/bin/python SOCHER_2026_v7_2020_2026/scripts/construir_entrega.py`. Las rutas dependen de la ubicación del script. Usa sólo derivados locales; descargar las fuentes originales corresponde a los extractores históricos, modernos y de mediciones. `--verificar` comprueba SHA-256 de todos los entregables, equivalencia byte a byte CSV/gzip y concatenación anual, y todas las celdas de CSV/Parquet en bloques de memoria. La igualdad de identificadores, enteros, booleanos y posiciones vacías es exacta. Para flotantes se permite sólo un error absoluto de serialización de hasta 1e-10, sin redondear los valores de salida. `--permitir-parcial --salida entrega_ensayo` permite una revisión durante las descargas sin confundirla con la entrega completa.

La reconstrucción de este CSV es completa desde las 82 particiones Parquet preservadas y sus metadatos. El paquete de insumos de la entrega permite repetir esa reconstrucción sin descargar archivos nacionales de varios gigabytes. La adquisición original es otra etapa: conserva scripts, manifiestos y URLs verificables, y algunos archivos del portal histórico pueden requerir descarga mediante la interfaz cuando el acceso HTTP directo responde 403. No se afirma reproducibilidad automática de esa adquisición bajo todas las condiciones de red. En la publicación del repositorio, el código y las guías se mantienen en Git y los datos se distribuyen como archivos de la versión.

Este CSV no es una conversión del Excel anterior: incorpora más años, fuentes, barras y observaciones. El peso en megabytes no mide la cantidad de información comparable porque CSV repite texto sin compresión, Excel almacena XML comprimido y Parquet comprime por columnas. Para comparar entregas deben usarse los conteos, períodos y variables documentados, no sólo el tamaño del archivo. El CSV completo puede exceder el límite de filas de una hoja de Excel; para trabajar con toda la base conviene R, Python, DuckDB o Parquet.

`Manifiesto_entrega.json` registra fuentes, cobertura, hashes y versión del constructor. `Verificacion_entrega.json` contiene el resultado de los controles. Se conserva el corte del 27/09/2026; para una actualización posterior deben ampliarse explícitamente las fuentes esperadas y revisarse los nuevos períodos.
"""
    (out / "LEEME_dataset.md").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--permitir-parcial", action="store_true", help="Permite fuentes mensuales aún pendientes y lo señala en guía/manifiesto")
    parser.add_argument("--salida", default="entrega", help="Carpeta de salida relativa a v7")
    parser.add_argument("--fecha-corte", default="2026-09-27", type=date.fromisoformat)
    parser.add_argument("--verificar", action="store_true", help="Verifica la entrega existente sin reconstruir")
    args = parser.parse_args()
    out = (BASE / args.salida).resolve()
    if out != BASE / "entrega" and not out.is_relative_to(BASE / "entrega"):
        # Permite ensayos dentro de entrega, nunca escrituras fuera del área asignada.
        if args.salida == "entrega_ensayo":
            out = BASE / "entrega/ensayo"
        else:
            parser.error("--salida debe estar dentro de entrega/ (o ser entrega_ensayo)")
    return verify(out) if args.verificar else build(out, args.permitir_parcial, args.fecha_corte)


if __name__ == "__main__":
    raise SystemExit(main())

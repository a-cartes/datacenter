#!/usr/bin/env python3
"""Derive auditable observational panels from immutable v0.2.0; no causal fit.

Run from any directory: python construir_panel.py --root /path/to/project
Only v8 outputs are written. No clock conversion, prices, or original metadata
are overwritten. --output-dir permits an independent reconstruction directory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import platform

import numpy as np
import pandas as pd
import pyarrow

EXPECTED_ROWS = 3_411_527
CSV_HASH = "19bc55d1a30cc59d63c2160a494ea39a42b625cdbb5f66761c360616e3f00d0b"
PARQUET_HASH = "84ca36dc328434dbeb9c0dda511b8eca1f4ee6caee48c29c0b642db7b7c93a00"
HOMOLOG_HASH = "435602c95a5e18e813f3f677d3140bd6298be046a5fd36c60459552be562f304"
V7 = Path("SOCHER_2026_v7_2020_2026")
HOMOLOG = V7 / "auditoria/control_descargas_20260927/miembros_nuevos/202308/Homologación barras cmg 2308.xlsx"
MONTH_KEY = ["mes", "familia_reloj", "barra_cmg"]
DAY_KEY = MONTH_KEY + ["fecha"]
OUTCOME_COLS = {
    "precio": "precio_usd_mwh",
    "dif_q110": "dif_q110",
    "dif_q220": "dif_q220",
}
DESCRIPTION = {
    "mes": "Mes YYYY-MM rotulado en la fuente; julio 2024 conserva dos familias de reloj.",
    "familia_reloj": "H: etiquetas históricas 1–25; M: HRA moderna 0–24. Sin conversión UTC ni unión entre familias.",
    "barra_cmg": "Etiqueta observacional de precio. No acredita por sí sola identidad física o relación con un campus.",
    "fecha": "Fecha rotulada de la fuente. No representa un instante UTC acreditado.",
    "serie_segmento_id": "Segmento observacional por etiqueta, reloj, código literal y meses contiguos. No certifica identidad física.",
    "id_documental_tipo": "nemotecnico_historico, ID_INFO_moderno, sin_identidad o ambiguo; se determina por mes sin transportar códigos.",
    "codigo_documentado": "Código histórico mensual exacto o ID_INFO moderno publicado y no marcador. No equivale a enlace físico longitudinal.",
    "identidad_longitudinal_certificada": "Siempre falso en este producto: requiere expediente de conexión y vigencia externo al panel de precios.",
    "regimen_precio": "Régimen original de publicación, sin mezcla de PRE.",
    "fuente_id": "Llave original a Fuentes_precios.csv congelado; la agregación no cambia la fuente.",
    "n_horas_observadas": "Número de etiquetas horarias con precio válido, distintas por fecha y reloj; no número de eventos independientes.",
    "n_etiquetas_union": "Número de etiquetas observadas en alguna barra del mismo día/reloj. No detecta omisiones simultáneas de todas las barras.",
    "n_horas_ausentes_frente_union": "Etiquetas de la unión diaria ausentes en esta barra; no imputadas.",
    "etiquetas_observadas": "Lista ordenada de etiquetas horarias fuente válidas, separadas por coma; vacía si falta todo el día.",
    "etiquetas_union": "Lista ordenada de etiquetas observadas en alguna barra ese día/reloj.",
    "firma_etiquetas": "SHA-256 de familia_reloj + | + lista de etiquetas; permite comprobar mismo soporte diario entre barras.",
    "soporte_24_etiquetas": "24 etiquetas únicas válidas y parejas completas en ambas referencias. Filtro técnico, nunca elegibilidad causal.",
    "cobertura_frente_union": "n_horas_observadas / n_etiquetas_union; no cobertura contra reloj físico independiente.",
    "n_pares_q110": "Número de diferencias con Quillota 110 emparejadas por fecha/reloj/etiqueta horaria.",
    "n_pares_q220": "Número de diferencias con Quillota 220 emparejadas por fecha/reloj/etiqueta horaria.",
    "n_dias_con_precio": "Días rotulados con al menos una etiqueta de precio en el mes y reloj.",
    "n_dias_calendario_regimen": "Días del calendario entre comienzo/fin del mes dentro del régimen y corte DEF global, incluso días sin precio de una barra.",
    "n_dias_sin_precio": "Días de ese calendario mensual sin precio observado; no son ceros.",
    "n_dias_24": "Días que satisfacen el filtro técnico soporte_24_etiquetas.",
    "n_horas_dias_24": "Etiquetas de los días que satisfacen soporte_24_etiquetas; 24 por día.",
    "fecha_desde_observada": "Primera fecha observada de la variante; no fecha de vigencia eléctrica.",
    "fecha_hasta_observada": "Última fecha observada de la variante; no fecha de vigencia eléctrica.",
    "estado_observacion": "completa_frente_union, parcial_frente_union o sin_observacion. No afirma integridad física del reloj.",
    "mes_civil_completo_en_regimen": "Todas las fechas civiles del mes dentro de este reloj y corte DEF; falso en julio 2024 y septiembre 2026.",
    "n_variantes_metadatos": "Variantes originales exactas dentro de etiqueta/mes/reloj; marcadores se conservan en mapeo_metadatos_observados.csv.",
    "overlay_agosto2023": "Indica código agregado por unión exacta al libro adicional de agosto de 2023, fuera de v0.2.0.",
    "nota_identidad": "Límite de interpretación del código documental del mes.",
    "nombre_documentado": "Nombre histórico o moderno documentado; múltiples variantes se conservan como JSON.",
    "barra_mes_id_originales_json": "Lista JSON de claves originales barra_mes_id; evita confundir marcadores modernos con nodos independientes.",
    "tiene_marcador_no_mostrar": "Alguna variante moderna incluye el texto [NO_MOSTRAR]; se conserva y no elimina precios.",
    "n_filas": "Número de observaciones horarias originales asociado a la fila de trazabilidad.",
    "codigo_fisico_mensual": "Código mensual original de v0.2.0; el overlay no lo sobrescribe.",
    "nombre_fisico_mensual": "Nombre mensual original de v0.2.0.",
    "id_info_fuente": "ID_INFO original moderno; incluye vacío o 0 donde publicado, sin imputación.",
    "barra_info_fuente": "Nombre original moderno, con marcadores literales conservados.",
    "estado_identidad": "Estado original v0.2.0 de homologación o ausencia documental.",
    "barra_mes_id": "Clave mensual original; no identidad longitudinal certificada.",
    "barra_cmg_original": "Etiqueta original antes de normalización histórica v0.2.0; conservada literalmente.",
    "familia_barra_historica": "Filtro histórico original; no entidad física certificada.",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def dump_json(path: Path, obj: object) -> None:
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def values_json(values: pd.Series) -> str:
    # Preserve literal 'nan' separately from genuinely absent values.
    items = {None if pd.isna(v) else str(v) for v in values}
    return json.dumps(sorted(items, key=lambda v: (v is not None, str(v))), ensure_ascii=False)


def valid_values(values: pd.Series) -> list[str]:
    return sorted({str(v) for v in values.dropna() if str(v).strip().lower() not in {"", "0", "-", "nan", "none"}})


def labels(values: pd.Series) -> str:
    return ",".join(map(str, sorted(set(map(int, values)))))


def summarize(frame: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    specs = {"n_horas_observadas": ("precio_usd_mwh", "count"),
             "n_pares_q110": ("dif_q110", "count"), "n_pares_q220": ("dif_q220", "count")}
    for prefix, col in OUTCOME_COLS.items():
        for statistic in ("mean", "std", "min", "max"):
            specs[f"{prefix}_{statistic}_usd_mwh"] = (col, statistic)
    return frame.groupby(keys, dropna=False, sort=True).agg(**specs).reset_index()


def column_description(col: str) -> str:
    if col in DESCRIPTION:
        return DESCRIPTION[col]
    if col.endswith("_dias_24"):
        return "Media mensual sobre horas de días con exactamente 24 etiquetas y parejas completas: " + column_description(col[:-8])
    for prefix, variable in (("precio", "precio original"), ("dif_q110", "diferencial horario emparejado barra menos Quillota 110"), ("dif_q220", "diferencial horario emparejado barra menos Quillota 220")):
        for stat, label in (("mean", "Media aritmética de horas observadas"), ("std", "Desviación estándar muestral de horas observadas"), ("min", "Mínimo horario observado"), ("max", "Máximo horario observado")):
            if col == f"{prefix}_{stat}_usd_mwh":
                return f"{label} del {variable}, USD/MWh. Mensual pondera horas; sin imputación ni inferencia causal."
    raise ValueError(f"Falta descripción para {col}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    out = (args.output_dir or root / "SOCHER_2026_v8_panel_causal").resolve()
    require(out != (root / V7).resolve() and (root / V7).resolve() not in out.parents, "Salida no puede modificar v7.")
    panel_dir, qa_dir = out / "panel", out / "validacion"
    panel_dir.mkdir(parents=True, exist_ok=True)
    qa_dir.mkdir(parents=True, exist_ok=True)
    source = root / V7 / "entrega"
    manifest = json.loads((source / "Manifiesto_entrega.json").read_text())
    source_paths = [source / "Dataset_precios_barra_hora_2020_2026.parquet", source / "Dataset_precios_barra_hora_2020_2026.csv", root / HOMOLOG, source / "Manifiesto_entrega.json", source / "Fuentes_precios.csv", source / "Faltantes_precios_detalle.csv"]
    sources = [{"archivo": str(p.relative_to(root)), "bytes": p.stat().st_size, "sha256": sha256(p)} for p in source_paths]
    require(sources[0]["sha256"] == PARQUET_HASH, "Parquet no corresponde a v0.2.0.")
    require(sources[1]["sha256"] == CSV_HASH, "CSV v0.2.0 cambió.")
    require(sources[2]["sha256"] == HOMOLOG_HASH, "Homologación agosto 2023 cambió.")
    declared = {r["archivo"]: r["sha256"] for r in manifest["archivos"]}
    require(declared[source_paths[0].name] == PARQUET_HASH and declared[source_paths[1].name] == CSV_HASH, "Manifiesto no concuerda con anclas congeladas.")
    df = pd.read_parquet(source_paths[0])
    require(df.shape == (EXPECTED_ROWS, 31), "Dimensiones congeladas inesperadas.")
    require(set(df.version_fuente.unique()) == {"DEF", "REAL-DEF"}, "PRE u otra versión en entrada.")
    require(df.fecha.min() == "2020-01-01" and df.fecha.max() == "2026-09-18", "Corte temporal inesperado.")
    require(df.precio_usd_mwh.notna().all(), "Precio original nulo.")
    df["familia_reloj"] = np.where(df.regimen_precio.eq("historico_antes_20240715"), "H", "M")
    df["hora_etiqueta"] = df.hora_etiqueta_historica.fillna(df.hora_fuente_moderna).astype(int)
    hour_key = ["familia_reloj", "fecha", "hora_etiqueta"]
    require(not df.duplicated(hour_key + ["barra_cmg"]).any(), "Precio duplicado por etiqueta/fecha/hora/régimen.")
    require(df.loc[df.familia_reloj.eq("M"), "hora_completa_4_intervalos"].eq(True).all(), "Agregado moderno incompleto.")
    errors = {}
    for kv in (110, 220):
        ref = df[df.barra_cmg.eq(f"QUILLOTA______{kv}")][hour_key + ["precio_usd_mwh"]].rename(columns={"precio_usd_mwh": f"ref_q{kv}"})
        require(not ref.duplicated(hour_key).any(), f"Referencia Quillota {kv} ambigua.")
        df = df.merge(ref, how="left", on=hour_key, validate="many_to_one", sort=False)
        df[f"dif_q{kv}"] = df.precio_usd_mwh - df[f"ref_q{kv}"]
        require(df[f"dif_q{kv}"].notna().all(), "Referencia faltante.")
        errors[str(kv)] = float((df[f"dif_q{kv}"] - df[f"diferencial_quillota_{kv}_usd_mwh"]).abs().max())
        require(errors[str(kv)] <= 1e-10, "Diferencial recomputado no concuerda.")

    meta_cols = ["barra_mes_id", "barra_cmg_original", "codigo_fisico_mensual", "nombre_fisico_mensual", "id_info_fuente", "barra_info_fuente", "familia_barra_historica", "estado_identidad", "regimen_precio", "fuente_id"]
    variants = df.groupby(MONTH_KEY + meta_cols, dropna=False, sort=True).agg(fecha_desde_observada=("fecha", "min"), fecha_hasta_observada=("fecha", "max"), n_filas=("fecha", "size")).reset_index()
    homolog = pd.read_excel(root / HOMOLOG, sheet_name="HOMOLOG", dtype=str)
    require(homolog.columns.tolist() == ["Barra CMG", "Nemotécnico", "Nombre Infotécnica"], "Columnas homologación inesperadas.")
    require(not homolog["Barra CMG"].duplicated().any(), "Etiqueta repetida en homologación.")
    # Matching is literal: no fuzzy matching, underscore editing, or propagation.
    hmap = homolog.set_index("Barra CMG")
    mapped = []
    for key, g in variants.groupby(MONTH_KEY, sort=True):
        mes, reloj, barra = key
        codes = valid_values(g.codigo_fisico_mensual if reloj == "H" else g.id_info_fuente)
        names = valid_values(g.nombre_fisico_mensual if reloj == "H" else g.barra_info_fuente)
        overlay = mes == "2023-08" and reloj == "H" and barra in hmap.index
        if overlay:
            require(not codes, "Overlay sobrescribiría código original.")
            codes = [hmap.loc[barra, "Nemotécnico"]]
            names = [hmap.loc[barra, "Nombre Infotécnica"]]
        typ = ("nemotecnico_historico" if reloj == "H" else "ID_INFO_moderno") if len(codes) == 1 else ("sin_identidad" if not codes else "ambiguo")
        row = dict(zip(MONTH_KEY, key))
        row.update(id_documental_tipo=typ, codigo_documentado=codes[0] if len(codes) == 1 else "", nombre_documentado=json.dumps(names, ensure_ascii=False), barra_mes_id_originales_json=values_json(g.barra_mes_id), n_variantes_metadatos=len(g), overlay_agosto2023=bool(overlay), tiene_marcador_no_mostrar=g.barra_info_fuente.fillna("").str.contains("NO_MOSTRAR", regex=False).any(), identidad_longitudinal_certificada=False, nota_identidad="Código mensual documentado; continuidad física no certificada" if len(codes) == 1 else "Sin código válido único; no elegible automáticamente", regimen_precio=g.regimen_precio.iloc[0], fuente_id=g.fuente_id.iloc[0], n_filas=int(g.n_filas.sum()))
        require(g.fuente_id.nunique() == 1 and g.regimen_precio.nunique() == 1, "Múltiples fuentes mensuales inesperadas.")
        mapped.append(row)
    mapping = pd.DataFrame(mapped)
    segments, transitions = [], []
    for (reloj, barra), g in mapping.groupby(["familia_reloj", "barra_cmg"], sort=True):
        previous, segment_no = None, 0
        for idx, row in g.sort_values("mes").iterrows():
            month_index = pd.Period(row.mes, "M").ordinal
            signature = (row.id_documental_tipo, row.codigo_documentado)
            change = previous is None or previous["signature"] != signature or month_index != previous["month_index"] + 1
            if change:
                segment_no += 1
                if previous is not None:
                    transitions.append({"familia_reloj": reloj, "barra_cmg": barra, "mes_anterior": previous["mes"], "mes_nuevo": row.mes, "codigo_anterior": previous["signature"][1], "codigo_nuevo": row.codigo_documentado, "motivo": "cambio_literal_codigo_o_disponibilidad" if previous["signature"] != signature else "mes_no_observado"})
            segment_id = f"{reloj}|{barra}|S{segment_no:02d}"
            segments.append((idx, segment_id))
            previous = dict(mes=row.mes, month_index=month_index, signature=signature)
    mapping["serie_segmento_id"] = pd.Series(dict(segments))

    daily = summarize(df, DAY_KEY)
    signatures = df.groupby(DAY_KEY, sort=True).hora_etiqueta.agg(labels).rename("etiquetas_observadas").reset_index()
    daily = daily.merge(signatures, on=DAY_KEY, validate="one_to_one")
    union = df.groupby(["mes", "familia_reloj", "fecha"], sort=True).hora_etiqueta.agg(labels).rename("etiquetas_union").reset_index()
    union["n_etiquetas_union"] = union.etiquetas_union.str.count(",") + 1
    # Calendar within each observed label-month and clock domain only. Labels
    # absent for whole months have unknown presence; they are not created.
    calendar_rows = []
    for (mes, reloj), g in mapping.groupby(["mes", "familia_reloj"], sort=True):
        month = pd.Period(mes, "M")
        lo = max(month.start_time, pd.Timestamp("2020-01-01" if reloj == "H" else "2024-07-15"))
        hi = min(month.end_time.normalize(), pd.Timestamp("2024-07-14" if reloj == "H" else "2026-09-18"))
        for barra in g.barra_cmg:
            calendar_rows.extend((mes, reloj, barra, day.strftime("%Y-%m-%d")) for day in pd.date_range(lo, hi, freq="D"))
    calendar = pd.DataFrame(calendar_rows, columns=DAY_KEY)
    daily = calendar.merge(daily, on=DAY_KEY, how="left", validate="one_to_one")
    daily = daily.merge(union, on=["mes", "familia_reloj", "fecha"], how="left", validate="many_to_one")
    for col in ("n_horas_observadas", "n_pares_q110", "n_pares_q220"):
        daily[col] = daily[col].fillna(0).astype(int)
    daily["etiquetas_observadas"] = daily.etiquetas_observadas.fillna("")
    daily["firma_etiquetas"] = (daily.familia_reloj + "|" + daily.etiquetas_observadas).map(lambda s: hashlib.sha256(s.encode()).hexdigest())
    daily["n_horas_ausentes_frente_union"] = daily.n_etiquetas_union - daily.n_horas_observadas
    daily["cobertura_frente_union"] = daily.n_horas_observadas / daily.n_etiquetas_union
    daily["soporte_24_etiquetas"] = daily.n_horas_observadas.eq(24) & daily.n_pares_q110.eq(24) & daily.n_pares_q220.eq(24)
    daily["estado_observacion"] = np.select([daily.n_horas_observadas.eq(0), daily.n_horas_ausentes_frente_union.eq(0)], ["sin_observacion", "completa_frente_union"], default="parcial_frente_union")
    # Small identity fields in panels; all originals and variants are sidecars.
    join_cols = MONTH_KEY + ["serie_segmento_id", "id_documental_tipo", "codigo_documentado", "identidad_longitudinal_certificada", "overlay_agosto2023", "tiene_marcador_no_mostrar", "regimen_precio", "fuente_id"]
    daily = daily.merge(mapping[join_cols], on=MONTH_KEY, validate="many_to_one")
    require(len(daily) == len(calendar), "Unión de metadatos duplicó días.")

    monthly = summarize(df, MONTH_KEY)
    cover = daily.groupby(MONTH_KEY, sort=True).agg(n_dias_calendario_regimen=("fecha", "size"), n_dias_con_precio=("n_horas_observadas", lambda v: int(v.gt(0).sum())), n_dias_24=("soporte_24_etiquetas", "sum"), n_horas_ausentes_frente_union=("n_horas_ausentes_frente_union", "sum"), n_etiquetas_union=("n_etiquetas_union", "sum")).reset_index()
    cover["n_dias_sin_precio"] = cover.n_dias_calendario_regimen - cover.n_dias_con_precio
    cover["mes_civil_completo_en_regimen"] = [n == pd.Period(m, "M").days_in_month for n, m in zip(cover.n_dias_calendario_regimen, cover.mes)]
    monthly = monthly.merge(cover, on=MONTH_KEY, validate="one_to_one")
    monthly["cobertura_frente_union"] = monthly.n_horas_observadas / monthly.n_etiquetas_union
    eligible_days = daily[daily.soporte_24_etiquetas][DAY_KEY]
    hours24 = df.merge(eligible_days, on=DAY_KEY, how="inner", validate="many_to_one")
    restricted = hours24.groupby(MONTH_KEY, sort=True).agg(n_horas_dias_24=("precio_usd_mwh", "size"), **{f"{prefix}_mean_usd_mwh_dias_24": (col, "mean") for prefix, col in OUTCOME_COLS.items()}).reset_index()
    monthly = monthly.merge(restricted, on=MONTH_KEY, how="left", validate="one_to_one").merge(mapping[join_cols], on=MONTH_KEY, validate="one_to_one")
    monthly["n_horas_dias_24"] = monthly.n_horas_dias_24.fillna(0).astype(int)

    require(int(daily.n_horas_observadas.sum()) == EXPECTED_ROWS, "Días no conservan conteo fuente.")
    require(int(monthly.n_horas_observadas.sum()) == EXPECTED_ROWS, "Meses no conservan conteo fuente.")
    require(not daily.duplicated(DAY_KEY).any() and not monthly.duplicated(MONTH_KEY).any(), "Clave final no única.")
    require(int(daily.n_horas_ausentes_frente_union.sum()) == 504, "No concuerda faltante observado v0.2.0.")
    require(daily.loc[daily.n_horas_observadas.eq(0), "precio_mean_usd_mwh"].isna().all(), "Día ausente rellenado.")
    weighted_errors = {}
    for prefix in OUTCOME_COLS:
        recomputed = daily.assign(weighted=daily[f"{prefix}_mean_usd_mwh"] * daily.n_horas_observadas).groupby(MONTH_KEY, sort=True).agg(total=("weighted", "sum"), n=("n_horas_observadas", "sum"))
        direct = monthly.set_index(MONTH_KEY)[f"{prefix}_mean_usd_mwh"]
        weighted_errors[prefix] = float((recomputed.total / recomputed.n - direct).abs().max())
        require(weighted_errors[prefix] < 1e-10, "Agregación diaria/mensual inconsistente.")

    outputs = []
    csv_checks = []
    def export(frame: pd.DataFrame, name: str, parquet: bool = False) -> None:
        path = panel_dir / f"{name}.csv"
        frame.to_csv(path, index=False, lineterminator="\n")
        # Read literal text to distinguish an empty field from source markers
        # such as the string 'nan'. Numeric serialization is checked separately.
        csv_read = pd.read_csv(path, dtype=str, keep_default_na=False)
        require(csv_read.shape == frame.shape and csv_read.columns.tolist() == frame.columns.tolist(), f"CSV alteró esquema: {name}")
        numeric_error = 0.0
        for col in frame:
            original = frame[col].reset_index(drop=True)
            actual_text = csv_read[col]
            if pd.api.types.is_numeric_dtype(original.dtype) and not pd.api.types.is_bool_dtype(original.dtype):
                actual = pd.to_numeric(actual_text.replace("", np.nan), errors="raise")
                require(actual.isna().tolist() == original.isna().tolist(), f"CSV alteró vacíos {name}.{col}")
                error = float((actual - original).abs().max()) if original.notna().any() else 0.0
                require(error <= 1e-10, f"CSV alteró valores {name}.{col}: {error}")
                numeric_error = max(numeric_error, error)
            else:
                expected_text = original.map(lambda v: "" if pd.isna(v) else str(v)).reset_index(drop=True)
                require(actual_text.tolist() == expected_text.tolist(), f"CSV alteró texto/marcadores {name}.{col}")
        csv_checks.append({"archivo": path.name, "filas": len(frame), "columnas": len(frame.columns), "error_maximo_numerico": numeric_error, "texto_y_vacios_exactos": True})
        outputs.append({"archivo": f"panel/{path.name}", "filas": len(frame), "columnas": len(frame.columns), "bytes": path.stat().st_size, "sha256": sha256(path)})
        if parquet:
            p = panel_dir / f"{name}.parquet"
            frame.to_parquet(p, index=False)
            reread = pd.read_parquet(p)
            pd.testing.assert_frame_equal(frame, reread)
            outputs.append({"archivo": f"panel/{p.name}", "filas": len(frame), "columnas": len(frame.columns), "bytes": p.stat().st_size, "sha256": sha256(p)})
    daily = daily.sort_values(["familia_reloj", "barra_cmg", "fecha"]).reset_index(drop=True)
    monthly = monthly.sort_values(["familia_reloj", "barra_cmg", "mes"]).reset_index(drop=True)
    export(daily, "panel_diario", True)
    export(monthly, "panel_mensual", True)
    export(mapping, "mapeo_mensual")
    export(variants, "mapeo_metadatos_observados")
    export(daily[daily.n_horas_ausentes_frente_union.gt(0)], "dias_con_ausencias")
    export(union, "calendario_etiquetas_observadas")
    transition_frame = pd.DataFrame(transitions, columns=["familia_reloj", "barra_cmg", "mes_anterior", "mes_nuevo", "codigo_anterior", "codigo_nuevo", "motivo"])
    export(transition_frame, "cambios_documentales_segmentos")
    overlay_frame = mapping[mapping.mes.eq("2023-08") & mapping.familia_reloj.eq("H")].copy()
    export(overlay_frame, "homologacion_agosto2023_validada")
    dictionary_rows = []
    for name, frame in (("panel_diario", daily), ("panel_mensual", monthly), ("mapeo_mensual", mapping), ("mapeo_metadatos_observados", variants)):
        for col in frame:
            dictionary_rows.append(dict(tabla=name, variable=col, tipo=str(frame[col].dtype), descripcion=column_description(col)))
    export(pd.DataFrame(dictionary_rows), "diccionario_panel")
    coverage = daily.groupby(["familia_reloj", "mes"], sort=True).agg(barras_etiqueta=("barra_cmg", "nunique"), filas_dia=("fecha", "size"), dias_distintos=("fecha", "nunique"), horas_precio=("n_horas_observadas", "sum"), dias_barra_24=("soporte_24_etiquetas", "sum"), dias_barra_sin_precio=("n_horas_observadas", lambda v: int(v.eq(0).sum())), horas_ausentes_union=("n_horas_ausentes_frente_union", "sum")).reset_index()
    export(coverage, "cobertura_mes_reloj")
    matched_overlay = overlay_frame[overlay_frame.overlay_agosto2023]
    report = {
        "estado": "OK", "creado_utc": datetime.now(timezone.utc).isoformat(),
        "version_base": "v0.2.0 inmutable", "script_sha256": sha256(Path(__file__)),
        "entorno": {"python": platform.python_version(), "pandas": pd.__version__, "numpy": np.__version__, "pyarrow": pyarrow.__version__},
        "entradas": sources, "filas_horarias_fuente": len(df), "columnas_fuente": 31,
        "fecha_desde": df.fecha.min(), "fecha_hasta": df.fecha.max(),
        "filas_diarias": len(daily), "filas_mensuales": len(monthly), "etiquetas_distintas": int(df.barra_cmg.nunique()),
        "segmentos_observacionales": int(mapping.serie_segmento_id.nunique()),
        "variantes_metadatos": len(variants), "barra_mes_id_distintos": int(df.barra_mes_id.nunique()),
        "distribucion_etiquetas_por_dia_barra": {str(k): int(v) for k, v in daily.n_horas_observadas.value_counts().sort_index().items()},
        "dias_barra_24_parejas_completas": int(daily.soporte_24_etiquetas.sum()),
        "ausencias_horarias_frente_union": int(daily.n_horas_ausentes_frente_union.sum()),
        "errores_maximos_diferencias_horarias_vs_v020": errors,
        "errores_maximos_agregacion_diaria_ponderada_vs_mensual": weighted_errors,
        "homologacion_agosto2023": {"filas_libro": len(homolog), "etiquetas_panel": len(overlay_frame), "enlaces_exactos": len(matched_overlay), "filas_precio_con_overlay": int(matched_overlay.n_filas.sum()), "no_enlazadas": overlay_frame.loc[~overlay_frame.overlay_agosto2023, "barra_cmg"].tolist(), "precio_modificado": False},
        "duplicados_precio_horario": 0, "duplicados_diarios": 0, "duplicados_mensuales": 0,
        "identidades_fisicas_longitudinales_certificadas": 0, "estimaciones_causales": False,
        "precios_unidos_a_carga": False, "UTC_inferido": False, "PRE_incorporado": False,
        "limitaciones": ["Calendario limitado a etiquetas observadas en el mes; ausencia de un mes completo no acredita retirada o inexistencia.", "Unión observada no detecta ausencia simultánea de todas las barras.", "24 etiquetas no certifican equivalencia con 24 horas físicas durante cambios de hora.", "Segmento documental no es campus ni unidad independiente ni homologación física certificada.", "Quillota es referencia descriptiva; no control causal validado.", "Nombres, marcadores y códigos originales quedan en tabla lateral; no se corrigen por similitud."],
        "archivos": outputs, "verificacion_csv_relectura": csv_checks,
    }
    dump_json(qa_dir / "validacion_panel.json", report)
    dump_json(qa_dir / "fuentes_hashes_panel.json", {"entradas": sources, "script_sha256": report["script_sha256"]})
    (panel_dir / "LEEME_panel.md").write_text(f"""# Panel observacional v8\n\nConstrucción desde **v0.2.0 congelado**: {len(df):,} precios DEF; {len(daily):,} filas barra–día de calendario y {len(monthly):,} filas barra–mes–reloj. Fechas: 2020-01-01 a 2026-09-18. Ningún precio se replica por centro de datos.\n\n## Reproducción\n\n`python SOCHER_2026_v8_panel_causal/scripts/construir_panel.py --root /ruta/al/proyecto`\n\nSe requieren pandas, numpy, pyarrow y openpyxl (entorno del proyecto). `--output-dir /ruta/alternativa` permite reconstruir en otra carpeta. El script verifica hashes de CSV y Parquet congelados, y del libro adicional de agosto 2023. No descarga ni modifica entregas anteriores.\n\n## Regla de agregación\n\nEl diario tiene clave `familia_reloj, barra_cmg, fecha`; el mensual añade `mes` y conserva separados los dos relojes de julio 2024. Cada diferencial se recomputa **antes** de agregar, mediante precio de barra menos referencia Quillota única, emparejada por fecha, familia de reloj y etiqueta horaria. El mensual promedia horas observadas, no medias diarias con igual peso. Se incluye una sensibilidad mensual sobre días de exactamente 24 etiquetas. El diario conserva listas y firmas de etiquetas para exigir soporte idéntico entre barras en cualquier comparación futura. Las medias, desviaciones, mínimos y máximos son descriptivos.\n\nHistórico: etiquetas 1–25; moderno: HRA 0–24, con cuatro intervalos válidos. No se resta una unidad, no se inventa UTC y no se une carga. La condición `soporte_24_etiquetas` es técnica; no habilita causalidad ni certifica duración física en días de cambio de hora.\n\nEl calendario amplía cada etiqueta/mes a todos los días dentro de su régimen y corte DEF. Hay {int(daily.n_horas_observadas.eq(0).sum())} filas de día sin precio y {int(daily.n_horas_ausentes_frente_union.sum())} etiquetas horarias ausentes frente a la unión. No se imputa. La ausencia de una etiqueta durante todo un mes permanece desconocida: no se crea un cero ni un estado de tratamiento. No hay PRE en el panel.\n\n## Identificadores y overlay\n\n`mapeo_mensual.csv` enlaza cada fila a sus identificadores originales. `mapeo_metadatos_observados.csv` preserva cada variante exacta, incluidos vacíos, 0, nombres y [NO_MOSTRAR], con fechas de **observación**, no vigencia eléctrica. Cambios de marcadores no crean nodos ni observaciones adicionales.\n\nLa homologación nueva de agosto de 2023 enlaza literalmente {len(matched_overlay)} de {len(overlay_frame)} etiquetas ({int(matched_overlay.n_filas.sum()):,} precios), sin alterar precios ni archivos v0.2.0. Los cinco enlaces no hallados permanecen vacíos. Los códigos no se transportan entre meses. Los {mapping.serie_segmento_id.nunique()} segmentos separan cambios literales, lagunas mensuales y familias de reloj; no son activos físicos certificados. En particular, los cambios septiembre–octubre de 2023 y julio de 2024 no se resuelven por semejanza.\n\n## Archivos y alcance\n\nCSV y Parquet diario/mensual contienen lo mismo. Las tablas de cobertura, diccionario, cambios documentales y homologación permiten revisar las uniones. `validacion/validacion_panel.json` registra conteos, errores numéricos, dependencias, hashes y límites. La base horaria íntegra permanece en v0.2.0; su clave de precio es única.\n\nNo hay tratamiento, exposición, controles certificados, ATT ni estimación de efectos en estos archivos. Las relaciones centro–evento–barra deben incorporarse desde expedientes externos con vigencia acreditada, sin multiplicar los precios por campus. Quillota 110/220 son referencias descriptivas.\n""", encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("estado", "filas_horarias_fuente", "filas_diarias", "filas_mensuales", "segmentos_observacionales", "distribucion_etiquetas_por_dia_barra", "homologacion_agosto2023")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

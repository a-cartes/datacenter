#!/usr/bin/env python3
"""Comprueba referencias exactas, ausentes, ambiguas e incompletas en temporales.

Parte de tres observaciones reales, las modifica únicamente como casos de prueba
y nunca escribe esos casos en la entrega ni altera el archivo fuente.
"""
import json
from pathlib import Path
import tempfile

import pandas as pd

import construir_entrega as app


def main():
    source = app.BASE / "moderno/datos/202609_DEF_horario.parquet"
    original_sha = app.sha(source)
    frame = pd.read_parquet(source)
    frame = frame.loc[frame.fecha.eq(frame.fecha.min()) & frame.hora_fuente.eq(0)]
    refs = ["QUILLOTA______110", "QUILLOTA______220"]
    node = frame.loc[~frame.barra_cmg.isin(refs)].iloc[0].barra_cmg
    base = frame.loc[frame.barra_cmg.isin(refs + [node])].copy()
    if len(base) != 3:
        raise RuntimeError("El caso requiere tres observaciones iniciales únicas")
    cases = {"exactas": base.copy(), "ausentes": base.loc[~base.barra_cmg.isin(refs)].copy()}
    duplicate = base.loc[base.barra_cmg.eq(refs[0])].copy()
    duplicate["id_info"] = "999999999"
    cases["ambigua_110"] = pd.concat([base, duplicate], ignore_index=True)
    incomplete = base.copy()
    mask = incomplete.barra_cmg.eq(refs[1])
    incomplete.loc[mask, "hora_completa_4_intervalos"] = False
    incomplete.loc[mask, "n_intervalos"] = 3
    incomplete.loc[mask, "minutos_observados"] = "0,15,30"
    incomplete.loc[mask, ["precio_usd_mwh_horario", "precio_clp_kwh_horario"]] = float("nan")
    cases["incompleta_220"] = incomplete
    results = []
    with tempfile.TemporaryDirectory(prefix="socher_referencias_") as temporary:
        for name, data in cases.items():
            path = Path(temporary) / (name + ".parquet")
            data.to_parquet(path, index=False)
            output, _ = app.normalize(path, "moderno", "202609")
            tested = output.loc[output.barra_cmg.eq(node)].iloc[0]
            for voltage in [110, 220]:
                prefix = f"quillota_{voltage}"
                fields = [f"precio_ref_{prefix}_usd_mwh", f"diferencial_{prefix}_usd_mwh", f"id_ref_{prefix}"]
                missing = name == "ausentes" or (name == "ambigua_110" and voltage == 110) or (name == "incompleta_220" and voltage == 220)
                if missing:
                    assert tested[fields].isna().all(), (name, voltage)
                else:
                    expected = float(base.loc[base.barra_cmg.eq(f"QUILLOTA______{voltage}"), "precio_usd_mwh_horario"].iloc[0])
                    assert tested[fields[0]] == expected
                    assert tested[fields[1]] == tested.precio_usd_mwh - expected
                    assert pd.notna(tested[fields[2]])
            assert tested.precio_usd_mwh == float(base.loc[base.barra_cmg.eq(node), "precio_usd_mwh_horario"].iloc[0])
            results.append({"caso": name, "resultado": "OK"})
    assert app.sha(source) == original_sha, "Se alteró la fuente"
    report = {"estado": "OK", "casos": results, "fuente_original_sin_modificaciones": True,
              "sha256_fuente": original_sha, "alcance": "Prueba de reglas de referencia, sin nuevas observaciones analíticas."}
    path = app.BASE / "documentacion/Prueba_referencias_descriptivas.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

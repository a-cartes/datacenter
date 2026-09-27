#!/usr/bin/env python3
"""Compara la expansión histórica con las observaciones de v6 compartidas.

No estima efectos ni altera datos: comprueba conservación de precios, claves y
homologaciones exactas en los cinco meses de la base ya verificada.
"""
from pathlib import Path
import json
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parent

def main():
    old = pd.read_parquet(ROOT/'SOCHER_2026_v6_multicentros/precios/CEN_panel_barra_hora_identificado_hasta_20240714.parquet')
    reports = []
    for month in ['202402', '202404', '202405', '202406', '202407']:
        new = pd.read_parquet(BASE/f'historico/derivados/precios_{month}.parquet')
        ref = old[old.mes_fuente == month]
        joined = ref.merge(new, on=['fecha', 'hora_etiqueta', 'barra_cmg'], how='outer',
            suffixes=('_v6', '_v7'), indicator=True, validate='one_to_one')
        both = joined[joined._merge == 'both']
        delta = (both.precio_usd_mwh_v6-both.precio_usd_mwh_v7).abs()
        identities = both[both.estado_identidad_v6 == 'homologacion_mensual_exacta']
        changed = identities[identities.nemotecnico.fillna('') != identities.codigo_fisico.fillna('')]
        reports.append({'mes':month,'filas_v6':len(ref),'filas_v7':len(new),
            'filas_comparadas':len(both),'solo_v6':int((joined._merge=='left_only').sum()),
            'solo_v7':int((joined._merge=='right_only').sum()),'max_diferencia_precio':float(delta.max()),
            'precios_diferentes_tol_1e_10':int((delta>1e-10).sum()),
            'codigos_exactos_comparados':len(identities),'codigos_exactos_diferentes':len(changed),
            'etiquetas_nuevas_v7':sorted(joined.loc[joined._merge=='right_only','barra_cmg'].unique().tolist())})
    out = BASE/'auditoria/Comparacion_precio_historico_v7_con_v6.json'
    out.write_text(json.dumps(reports, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    if any(r['solo_v6'] or r['precios_diferentes_tol_1e_10'] or r['codigos_exactos_diferentes'] for r in reports):
        raise SystemExit(1)

if __name__ == '__main__':
    main()

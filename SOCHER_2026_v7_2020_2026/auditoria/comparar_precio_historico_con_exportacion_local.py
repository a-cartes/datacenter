#!/usr/bin/env python3
"""Compara DEF mensual con exportación histórica previa, sin sustituir fuentes.

Une sólo por código exacto de barra, fecha y etiqueta de hora de ambos archivos.
Las divergencias se reportan: pueden deberse a versión, homologación o valores
fuente; no se corrigen por inferencia ni se convierten horas a UTC.
"""
from pathlib import Path
import json
import pandas as pd

BASE=Path(__file__).resolve().parent.parent
ROOT=BASE.parent

def main():
    source=ROOT/'SOCHER_2026_v3/precios/CEN_CMg_historicos_locales_2023_20240714_deduplicado.csv'
    old=pd.read_csv(source,sep=';',decimal=',',dtype={'barra_mnemotecnico':str})
    old=old.rename(columns={'barra_mnemotecnico':'codigo_fisico','hora':'hora_etiqueta'})
    reports=[]
    for p in sorted((BASE/'historico/derivados').glob('precios_*.parquet')):
        month=p.stem.split('_')[-1]
        if not '202301'<=month<='202407':continue
        prior=old[old.fecha.str.startswith(month[:4]+'-'+month[4:])]
        current=pd.read_parquet(p)
        current=current[current.codigo_fisico.notna() & current.codigo_fisico.ne('')]
        joined=prior.merge(current,on=['codigo_fisico','fecha','hora_etiqueta'],how='inner',validate='one_to_one')
        diff=(joined.costo_en_dolares-joined.precio_usd_mwh).abs()
        bad=joined[diff>1e-10]
        reports.append({'mes':month,'n_exportacion_local':len(prior),'n_comparadas_codigo_exacto':len(joined),
            'n_no_comparables':len(prior)-len(joined),'diferencias_mayores_1e_10':len(bad),
            'max_diferencia':float(diff.max()) if len(joined) else None,
            'ejemplos_diferentes':bad[['codigo_fisico','fecha','hora_etiqueta','costo_en_dolares','precio_usd_mwh']].head(10).to_dict('records')})
    out=BASE/'auditoria/Comparacion_DEF_con_exportacion_local.json'
    out.write_text(json.dumps({'fuente_previa':str(source.relative_to(ROOT)),
        'nota':'Comparación diagnóstica de códigos exactos. No permite igualar versiones o afirmar continuidad temporal.',
        'meses':reports},ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(reports,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()

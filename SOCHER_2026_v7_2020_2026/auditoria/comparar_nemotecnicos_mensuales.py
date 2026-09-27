#!/usr/bin/env python3
"""Documenta diferencias literales de códigos, sin resolver identidad por ceros."""
from pathlib import Path
from datetime import datetime, timezone
import json
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
HIST = BASE / 'historico'

def main():
    frames = []; sources = {}
    for month in ['202309', '202310']:
        frame = pd.read_parquet(HIST / f'derivados/precios_{month}.parquet',
            columns=['barra_cmg', 'codigo_fisico', 'nombre_fisico']).drop_duplicates()
        frames.append(frame.rename(columns={c:c+'_'+month for c in ['codigo_fisico','nombre_fisico']}))
        sources[month] = json.loads((HIST / f'manifiestos/precios_{month}.json').read_text())['homologacion']
    shared = frames[0].merge(frames[1],on='barra_cmg',how='inner',validate='one_to_one')
    changed = shared.loc[shared.codigo_fisico_202309.ne(shared.codigo_fisico_202310)]
    result = {'generado_utc':datetime.now(timezone.utc).isoformat(),
        'fuentes_homologacion':sources, 'barras_compartidas':len(shared),
        'nemotecnicos_literales_distintos':len(changed),
        'interpretacion':'Cambio literal observado en homologaciones mensuales; no se normalizan ceros ni se declara continuidad física por semejanza. Comparaciones por código exacto entre meses no son comparaciones completas de barras físicas.',
        'filas':changed.to_dict(orient='records')}
    (BASE / 'auditoria/Diferencias_nemotecnico_202309_202310.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['filas','fuentes_homologacion']},ensure_ascii=False))

if __name__ == '__main__': main()

#!/usr/bin/env python3
"""Resume cobertura declarada por los manifiestos, sin estimaciones ni imputación."""
from pathlib import Path
import csv, datetime as dt, json

HERE = Path(__file__).resolve().parent
HIST = HERE.parent

def main():
    catalog = json.loads((HERE/'catalogo_cmg_oficial_2020_2024.json').read_text())
    records = []
    for r in catalog['definitivos']:
        month = r['mes']; p = HIST/'manifiestos'/f'precios_{month}.json'
        report = json.loads(p.read_text()) if p.exists() else {}
        outputs_exist = all((HIST.parent/path).exists() for path in report.get('outputs', {})) if report else False
        records.append({'mes':month,'alcance':r['alcance'],'enlace_oficial_observado':bool(r['url_archivo']),
            'procesado_con_archivos':bool(report and outputs_exist),'filas':report.get('filas'),
            'etiquetas_barra':report.get('barras_etiqueta'),'desde':report.get('fecha_min'),
            'hasta':report.get('fecha_max'),'dias':report.get('dias'),
            'homologacion_mensual':bool(report.get('homologacion')) if report else None,
            'faltantes_explicitos':len(report.get('faltantes_explicitos',[])) if report else None,
            'duplicados':report.get('duplicados'),'libro_sha256':report.get('libro_sha256')})
    summary = {'generado_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'meses_objetivo_mas_puente':len(records),
        'meses_procesados':sum(r['procesado_con_archivos'] for r in records),
        'filas_procesadas':sum(r['filas'] or 0 for r in records if r['procesado_con_archivos']),
        'meses_pendientes':[r['mes'] for r in records if not r['procesado_con_archivos']],
        'nota':'Procesado describe extracción de precios; no demuestra continuidad física, UTC válido ni entrada de centros. No se infiere cobertura dentro del mes únicamente del número de días.',
        'meses':records}
    (HERE/'cobertura_historica_actual.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    with (HERE/'cobertura_historica_actual.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
    print(json.dumps({k:v for k,v in summary.items() if k!='meses'},ensure_ascii=False))

if __name__ == '__main__':
    main()

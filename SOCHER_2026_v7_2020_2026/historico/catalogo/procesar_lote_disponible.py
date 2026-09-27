#!/usr/bin/env python3
"""Registra nuevas descargas y procesa solamente los meses nuevos o pendientes.

No espera descargas ni accede a la red. Puede repetirse al terminar cada lote
del navegador. Conserva originales y errores; una descarga no es un resultado.
"""
from pathlib import Path
import argparse, json, subprocess, sys

HERE = Path(__file__).resolve().parent
HIST = HERE.parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workers',type=int,default=3)
    a=ap.parse_args()
    registered=subprocess.run([sys.executable,str(HERE/'registrar_descargas_historicas.py')],check=True,capture_output=True,text=True)
    status=json.loads(registered.stdout.strip().splitlines()[-1]);print(json.dumps(status,ensure_ascii=False),flush=True)
    records=json.loads((HERE/'descargas_historicas_registradas.json').read_text())['archivos']
    months=set(status['meses_nuevos'])
    for r in records:
        month=r['mes']; report=HIST/'manifiestos'/f'precios_{month}.json'
        extraction=HIST/'manifiestos'/f'extraccion_zip_{month}.json'
        previous=json.loads(extraction.read_text()) if extraction.exists() else {}
        if not report.exists() or previous.get('sha256_zip')!=r['sha256']:
            months.add(month)
    print(json.dumps({'meses_lote':sorted(months)},ensure_ascii=False),flush=True)
    returncode=0
    if months:
        proc=subprocess.run([sys.executable,str(HIST/'extraer_precios_historicos.py'),'--months',*sorted(months),'--workers',str(a.workers)])
        returncode=proc.returncode
    subprocess.run([sys.executable,str(HERE/'resumir_cobertura_historica.py')],check=True)
    raise SystemExit(returncode)

if __name__=='__main__':
    main()

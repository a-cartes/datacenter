"""Reproduce el cierre SOCHER en una carpeta separada y contrasta referencias congeladas."""
from pathlib import Path
import argparse, csv, hashlib, json, os, shutil, subprocess, sys, platform

ROOT = Path(__file__).resolve().parents[1]

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--salida', type=Path, default=ROOT/'salidas/reproduccion')
    ap.add_argument('--solo-integridad', action='store_true')
    args = ap.parse_args()
    manifest = json.loads((ROOT/'procedencia/manifest.json').read_text())
    for item in manifest['archivos']:
        p = ROOT/item['archivo']
        if not p.is_file() or sha(p) != item['sha256']:
            raise SystemExit('Integridad fallida: '+item['archivo'])
    print(f"Integridad OK: {len(manifest['archivos'])} archivos", flush=True)
    if args.solo_integridad:
        return
    out = args.salida.resolve()
    # No permitir sobreescribir el paquete, sus entradas ni una ejecución existente.
    if out == ROOT or ROOT.is_relative_to(out) or (out.is_relative_to(ROOT) and not out.is_relative_to(ROOT/'salidas')):
        raise SystemExit('La salida debe ser una carpeta nueva distinta del paquete.')
    if out.exists():
        raise SystemExit(f'La salida ya existe: {out}. Use otra carpeta para conservar la ejecución anterior.')
    out.mkdir(parents=True)
    work = out/'trabajo'; work.mkdir()
    for name in ['datos','scripts','procedencia','prospectiva_2030']:
        shutil.copytree(ROOT/name,work/name)
    (work/'resultados/cierre_socher_20261009').mkdir(parents=True)
    env = os.environ.copy(); env['MPLCONFIGDIR']=str(out/'cache_matplotlib');env['MPLBACKEND']='Agg'
    env['OMP_NUM_THREADS']='1'; env['OPENBLAS_NUM_THREADS']='1'
    tasks = [
        [sys.executable,'scripts/preparar_muestra.py'],
        [os.environ.get('RSCRIPT','Rscript'),'scripts/resultados_socher.R'],
        [os.environ.get('RSCRIPT','Rscript'),'scripts/contrastes_cierre_20261009.R'],
        [sys.executable,'scripts/diagnostico_cierre_20261009.py'],
        [sys.executable,'scripts/calculos_comparacion_2030.py'],
        [sys.executable,'scripts/verificar_cierre.py',str(ROOT),str(out)],
    ]
    executed=[]
    for i,cmd in enumerate(tasks,1):
        print(f'[{i}/{len(tasks)}] {Path(cmd[1]).name}',flush=True)
        log=out/f'{i:02d}_{Path(cmd[1]).stem}.log'
        with log.open('w') as stream:
            proc=subprocess.run(cmd,cwd=work,env=env,stdout=stream,stderr=subprocess.STDOUT)
        executed.append({'programa':cmd[1], 'codigo_salida':proc.returncode,'log':log.name})
        if proc.returncode:
            print(log.read_text()[-6000:])
            raise SystemExit(f'Falló {cmd[1]}; revisar {log}')
    report=json.loads((out/'verificacion.json').read_text())
    report['ejecucion']={'python':platform.python_version(),'sistema':platform.system(),'tareas':executed}
    (out/'verificacion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print('Reproducción verificada. Informe: '+str(out/'verificacion.json'))

if __name__=='__main__':
    main()

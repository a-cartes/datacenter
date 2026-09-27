#!/usr/bin/env python3
"""Finalizador local de esta ejecución: extrae fuentes completadas y verifica al concluir.

No agenda ejecuciones futuras ni modifica fuentes. Máximo 3 horas de espera por el lote activo.
"""
import datetime as dt, hashlib, json, subprocess, sys, time
from pathlib import Path
B=Path(__file__).resolve().parents[1];M=B/'fuentes/metadatos';SCRIPT=B/'scripts/descargar_extraer_moderno.py'
items=[(f'{y}-{m:02}','DEF') for y in [2024,2025,2026] for m in range(1,13) if (y,m)>=(2024,7) and (y,m)<=(2026,9)]+[('2026-09','PRE')]
start=time.monotonic()
while time.monotonic()-start<10800:
 done=0;digest=hashlib.sha256(SCRIPT.read_bytes()).hexdigest()
 old_sample_done=(M/'202609_PRE_extraccion.json').exists()
 for month,version in items:
  stem=month.replace('-','')+'_'+version;source=M/(stem+'.json');extraction=M/(stem+'_extraccion.json')
  if not source.exists():continue
  if (month,version) in [('2025-06','DEF'),('2026-09','DEF'),('2026-09','PRE')] and not old_sample_done:continue
  e=json.loads(extraction.read_text()) if extraction.exists() else {}
  if e.get('schema_version')=='moderno_v7.1' and e.get('script_sha256')==digest:
   done+=1;continue
  # Solo extrae: el código de red no se invoca y las fuentes están completas con manifiesto.
  cmd=[sys.executable,str(SCRIPT),'--months',month,'--phase','extract']
  if version=='PRE':
   # La CLI procesa también DEF de septiembre; sigue separado en archivos y versión.
   cmd+=['--include-pre-septiembre']
  subprocess.run(cmd,check=True);done+=1
 print(json.dumps({'fase':'estado_finalizador','completadas':done,'esperadas':len(items),'utc':dt.datetime.now(dt.timezone.utc).isoformat()}),flush=True)
 if done==len(items):
  subprocess.run([sys.executable,str(B/'scripts/verificar_lote_moderno.py')],check=True)
  print('LOTE_MODERNO_COMPLETO_Y_VERIFICADO',flush=True);break
 time.sleep(30)
else:raise TimeoutError('Faltan fuentes del lote activo; revisar logs, sin declarar completo')

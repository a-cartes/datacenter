"""Reproduce la base desde los extractos auditados existentes; no descarga ni estima efectos."""
from pathlib import Path
from datetime import datetime, timezone
import subprocess
import sys
import json
import hashlib
B=Path(__file__).resolve().parents[1]
steps=['construir_panel_precios.py','construir_eventos_relaciones.py','construir_mediciones.py',
       'verificar_mediciones.py','verificar_y_catalogar.py','documentar_panel.py']
log={'fecha_utc':datetime.now(timezone.utc).isoformat(),'python':sys.executable,
     'alcance':'Reproduce dataset desde extractos v3/v4/v6 preservados. No redescarga ni recompone toda la adquisición original.','pasos':[]}
for name in steps:
    path=B/'scripts'/name
    result=subprocess.run([sys.executable,str(path)],cwd=B.parent,text=True,capture_output=True)
    log['pasos'].append({'script':name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'exit_code':result.returncode,'stdout':result.stdout,'stderr':result.stderr})
    (B/'controles/registro_reproduccion.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))
    if result.returncode:
        print(result.stderr or result.stdout);raise SystemExit(result.returncode)
    print(name+': completado',flush=True)
log['completado']=True
(B/'controles/registro_reproduccion.json').write_text(json.dumps(log,ensure_ascii=False,indent=2))

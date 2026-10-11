"""Consulta acotada de BESS para identificar series separadas; sin exponer credenciales."""
from pathlib import Path
import requests,gzip,json,hashlib
from descargar_operacion_api import getkey
S=Path(__file__).resolve().parents[1];out=S/'fuentes_operacion/20261011_bess_catalogo';out.mkdir();key=getkey(Path.cwd())
try:
 r=requests.get('https://sipub.api.coordinador.cl/generacion-real/v3/findByDate',params=dict(startDate='2025-03-06',endDate='2025-03-06',tipoTecnologia='BESS',page=1,pageSize=10000,user_key=key),timeout=90)
 if r.status_code!=200:raise RuntimeError('HTTP '+str(r.status_code))
 o=r.json();raw=json.dumps(o,ensure_ascii=False,sort_keys=True).encode();assert key.encode() not in raw
 f=out/'bess_20250306.json.gz'
 with gzip.open(f,'wb') as z:z.write(raw)
 data=o.get('data',o.get('content',[]));print({k:v for k,v in o.items() if k not in ['data','content']})
 sel=[x for x in data if 'humberto' in str(x).lower()];print('Humberto',len(sel));print(sel[:3])
 (out/'manifiesto.json').write_text(json.dumps(dict(ruta='/generacion-real/v3/findByDate',filtro='tipoTecnologia=BESS;2025-03-06',archivo=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),filas=len(data)),indent=2))
except requests.RequestException as e:print(type(e).__name__)

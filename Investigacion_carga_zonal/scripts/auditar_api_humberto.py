from pathlib import Path
import requests,json,gzip,time,hashlib
from descargar_operacion_api import getkey
S=Path(__file__).resolve().parents[1];out=S/'fuentes_operacion/20261011_humberto_nocturno';out.mkdir();key=getkey(Path.cwd());manifest=[]
for label,extra in [('BESS',{'tipoTecnologia':'BESS'}),('PFV',{'idCentral':2209})]:
 params=dict(startDate='2026-01-10',endDate='2026-01-10',page=1,pageSize=10000,user_key=key,**extra)
 try:r=requests.get('https://sipub.api.coordinador.cl/generacion-real/v3/findByDate',params=params,timeout=90)
 except requests.RequestException as e:print(type(e).__name__);break
 if r.status_code!=200:print('HTTP',r.status_code);break
 o=r.json();raw=json.dumps(o,ensure_ascii=False,sort_keys=True).encode();assert key.encode() not in raw;f=out/(label+'.json.gz')
 with gzip.open(f,'wb') as z:z.write(raw)
 data=o.get('data',o.get('content',[]));print(label,{k:v for k,v in o.items() if k not in ['data','content']});print([x for x in data if 'humberto' in str(x).lower() and x['hora']==24]);manifest.append(dict(archivo=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),fecha='2026-01-10',filtro=extra,filas=len(data)));time.sleep(10)
(out/'manifiesto.json').write_text(json.dumps(manifest,indent=2))

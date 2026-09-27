from pathlib import Path
import hashlib,json,urllib.request
P=Path(__file__).resolve().parent
sources=[('AJ01','CEN_Solution2_IAC_20250704.pdf','https://cartas.coordinador.cl/download_anexos/68684eee3563571479b32843/0'),('AJ02','CEN_DE04070_20250704.pdf','https://cartas.coordinador.cl/download_saved_file/68684eee3563571479b32843')]
results=[]
(P/'fuentes').mkdir(parents=True,exist_ok=True)
for id,name,url in sources:
 p=P/'fuentes'/name;r={'id':id,'archivo':'fuentes/'+name,'url':url,'fecha_consulta':'2026-09-27'}
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as f:b=f.read()
   assert b.startswith(b'%PDF')
   p.write_bytes(b)
  b=p.read_bytes();r.update(estado='ARCHIVADO',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r.update(estado='NO_ARCHIVADO',error=str(e))
 results.append(r)
(P/'manifest_fuentes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(results,ensure_ascii=False,indent=2))

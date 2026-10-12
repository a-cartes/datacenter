from pathlib import Path
import requests,json,hashlib
from pypdf import PdfReader
out=Path(__file__).resolve().parents[1]/'fuentes_operacion/20261011_evento_20241203';out.mkdir();refs=[('EAF-563-2024.pdf','https://www.coordinador.cl/wp-content/uploads/2024/12/EAF-563-2024.pdf'),('Respuesta_EdgeConneX.pdf','https://cartas.coordinador.cl/download_saved_file/67b797ff356357171e3168f6'),('Anexo_respuesta_0','https://cartas.coordinador.cl/download_anexos/67b797ff356357171e3168f6/0')];m=[];text=[]
for name,url in refs:
 r=requests.get(url,timeout=50);record=dict(archivo=name,url=url,http=r.status_code)
 if r.status_code==200:
  p=out/name;p.write_bytes(r.content);record.update(sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content),tipo=r.headers.get('Content-Type'))
  if r.content.startswith(b'%PDF'):
   rr=PdfReader(p);record['paginas']=len(rr.pages)
   for i,page in enumerate(rr.pages):
    t=page.extract_text()
    if i<12 or ('canteras' in t.lower() and ('05:36' in t or '21:19' in t)):text.append(dict(archivo=name,pagina=i+1,texto=t))
 m.append(record);print({k:v for k,v in record.items() if k not in ['url','sha256']},flush=True)
(out/'manifiesto.json').write_text(json.dumps(m,indent=2));(out/'extractos.json').write_text(json.dumps(text,indent=2,ensure_ascii=False))

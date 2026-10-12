"""Fuentes primarias para candidatos elegidos por carga, sin seleccionar por precios."""
from pathlib import Path
import json,hashlib,time
import requests
from pypdf import PdfReader
S=Path(__file__).resolve().parents[1];out=S/'fuentes_operacion/20261011_variaciones_documentos';out.mkdir()
refs=[('EAF-584-2024.pdf','https://www.coordinador.cl/wp-content/uploads/2025/01/EAF-584-2024.pdf'),('Carta_DE_enero2025_Canteras.pdf','https://cartas.coordinador.cl/download_saved_file/678eb9623563570a1e506a79')]
for day in ['2024-08-08','2025-05-12','2025-05-14','2025-05-16','2025-12-19','2026-01-19','2026-05-13','2026-05-15']:
 y,m,d=day.split('-');name=f'Informe-Diario-{d}-{m}-{y}.pdf';refs.append((name,f'https://www.coordinador.cl/wp-content/uploads/{y}/{m}/{name}'))
manifest=[];extract=[]
for name,url in refs:
 try:
  r=requests.get(url,timeout=40);item=dict(archivo=name,url=url,http=r.status_code)
  if r.status_code==200 and r.content.startswith(b'%PDF'):
   p=out/name;p.write_bytes(r.content);item.update(sha256=hashlib.sha256(r.content).hexdigest(),bytes=len(r.content));pdf=PdfReader(p);item['paginas']=len(pdf.pages)
   for i,page in enumerate(pdf.pages):
    txt=page.extract_text();normalized=txt.lower()
    if any(s in normalized for s in ['canteras','edgeconnex']):extract.append(dict(archivo=name,pagina=i+1,texto=txt))
  else:item['estado']='no_recuperado'
 except Exception as e:item=dict(archivo=name,url=url,estado=type(e).__name__)
 manifest.append(item);(out/'manifiesto.json').write_text(json.dumps(manifest,indent=2));(out/'extractos_canteras.json').write_text(json.dumps(extract,indent=2,ensure_ascii=False));print(json.dumps({k:v for k,v in item.items() if k not in ['url','sha256']}),flush=True);time.sleep(2)

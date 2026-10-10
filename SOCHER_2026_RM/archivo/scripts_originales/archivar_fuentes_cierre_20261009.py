import urllib.request,hashlib,json
from pathlib import Path
from pypdf import PdfReader
p=Path(__file__).resolve().parents[1]/'resultados/cierre_socher_20261009/fuentes';p.mkdir(exist_ok=True);out=[]
urls=[('ODATA_ST01_DE02932_23','https://cartas.coordinador.cl/download_saved_file/64a328c53563574eab7a4eca'),('EDGE_DE03409_24','https://cartas.coordinador.cl/download_saved_file/6659e61a35635760544f0c17'),('ODATA_ST02_OP02215_26','https://cartas.coordinador.cl/download_saved_file/6abad5b73563570a7f1eb54a'),('EAF_312_2025','https://www.coordinador.cl/wp-content/uploads/2025/07/EAF-312-2025.pdf')]
for name,url in urls:
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'});data=urllib.request.urlopen(req,timeout=20).read();rec=dict(nombre=name,url=url)
  if data.startswith(b'%PDF'):
   f=p/(name+'.pdf');f.write_bytes(data);rec['sha256']=hashlib.sha256(data).hexdigest();t='\n'.join('PÁGINA '+str(i+1)+'\n'+x.extract_text() for i,x in enumerate(PdfReader(f).pages));(p/(name+'.txt')).write_text(t);print(name,len(data),flush=True)
  else:rec['error']='Respuesta no PDF';print(name,'not PDF',flush=True)
  out.append(rec)
 except Exception as e:out.append(dict(nombre=name,url=url,error=str(e)));print(name,e,flush=True)
(p/'registro.json').write_text(json.dumps(out,indent=2))

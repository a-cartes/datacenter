import urllib.request,json,hashlib,datetime,pathlib,concurrent.futures
OUT=pathlib.Path(__file__).parent/'fuentes'
SOURCES={
'CEN_EAF141_2026.pdf':'https://www.coordinador.cl/wp-content/uploads/2026/04/EAF-141-2026.pdf',
'ODATA_cronologia.html':'https://odatacolocation.com/es/sobre-nos-2/',
'CEN_ODATA_NuevaLampa_IAC202410.pdf':'https://cartas.coordinador.cl/download_anexos/6705c78535635702715c7943/0',
'CTNG_Memoria2019.pdf':'https://www.ctng.cl/wp-content/uploads/2020/04/Memoria-Corporativa-2019-CTNG.pdf',
'Infotecnica_Chacabuco_DUF_NUP5417.zip':'https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/470265/',
'Infotecnica_Chacabuco_AsBuilt20200703.zip':'https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/206388/',
'Infotecnica_Chacabuco_DUF20210121.zip':'https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/234695/',
'CEN_Informe_Diario_20240624.pdf':'https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-24-06-2024.pdf',
'CEN_Informe_Diario_20240625.pdf':'https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-25-06-2024.pdf',
'infotecnica_Chacabuco683_documentos.json':'https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/',
'infotecnica_Chacabuco_E53.json':'https://api-infotecnica.coordinador.cl/v1/panos/32081/',
'CEN_EAF289_2024.pdf':'https://www.coordinador.cl/wp-content/uploads/2024/07/EAF-289-2024.pdf',
'STM_Ascenty_E53_solicitud_20241213.pdf':'https://cartas.coordinador.cl/download_saved_file/676095103563570a6909d2f6',
'STM_Ascenty_E53_MNR_20250113.pdf':'https://cartas.coordinador.cl/download_saved_file/678a9ac43563572012d6e461',
'STM_Ascenty_E53_termino_20250604.pdf':'https://cartas.coordinador.cl/download_saved_file/684213aa3563577698e6da48',
'CEN_EAF575_2024.pdf':'https://www.coordinador.cl/wp-content/uploads/2025/01/EAF-575-2024.pdf',
'infotecnica_Chacabuco683_elementos.json':'https://api-infotecnica.coordinador.cl/v1/subestaciones/683/elementos/',
'CEN_Ascenty_Chile2_solicitud202411.pdf':'https://www.coordinador.cl/wp-content/uploads/2024/11/DE06670-24.pdf',
}
def get(pair):
 name,url=pair;p=OUT/name
 rec={'archivo':str(p),'url':url,'consulta':'2026-09-27'}
 try:
  if not p.exists():
   req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   with urllib.request.urlopen(req,timeout=50) as r: b=r.read()
   if name.endswith('.pdf') and not b.startswith(b'%PDF'):raise ValueError('No PDF')
   if name.endswith('.json'):json.loads(b)
   p.write_bytes(b)
  b=p.read_bytes();rec.update(bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),estado='descargado')
 except Exception as e:rec.update(estado='error',error=str(e))
 return rec
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: records=list(pool.map(get,SOURCES.items()))
 (OUT/'manifest_descargas.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 print(json.dumps(records,ensure_ascii=False,indent=2))

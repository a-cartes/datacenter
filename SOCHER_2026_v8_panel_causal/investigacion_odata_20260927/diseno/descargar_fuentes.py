from pathlib import Path
import urllib.request,hashlib,json,datetime
base=Path(__file__).resolve().parent
items=[
('ODD07','CEN EAF0132021 pruebas NuevaLampa enero2021','https://www.coordinador.cl/wp-content/uploads/2021/02/EAF-013-2021.pdf','CEN_EAF013_2021.pdf'),
('ODD08','CEN EAF0672021 fallaNuevaLampa marzo2021','https://www.coordinador.cl/wp-content/uploads/2021/03/EAF-067-2021.pdf','CEN_EAF067_2021.pdf'),
('ODD01','Enel transmisión Informe sostenibilidad 2021','https://www.enel.cl/content/dam/enel-cl/sostenibilidad/informes-de-sostenibilidad/enel-transmision/2021/IS-Enel-Tx-2021.pdf','enel_tx_sostenibilidad_2021.pdf'),
('ODD02','CEN Resumen solicitudes junio2020','https://www.coordinador.cl/wp-content/uploads/2020/07/Resumen-Solicitudes-Aprobaci%C3%B3n-de-Conexi%C3%B3n-de-Conexi%C3%B3n-Junio-2020.pdf','CEN_solicitudes_junio2020.pdf'),
('ODD03','CEN revision ingenieria conceptual S/E Lampa2025','https://cartas.coordinador.cl/download_anexos/68eeba133563576d444e32b4/0','CEN_revision_Lampa_2025.pdf'),
('ODD04','CNE Plan expansion transmision2022 preliminar marzo2023','https://www.cne.cl/wp-content/uploads/2023/03/ITP-Plan-de-Expansion-de-la-Transmision-2022.pdf','CNE_ITP_expansion2022.pdf'),
('ODD05','Ley Lobby obras ODATA2022-07-21','https://www.leylobby.gob.cl/instituciones/AM010/audiencias/2022/28236/630645','lobby_ODATA_obras_20220721.html'),
('ODD06','CEN CNE actualiza construccion mayo2025','https://cartas.coordinador.cl/download_saved_file/6818e0963563577bb5da060f','CNE_dc_mayo2025.pdf')]
manifest=[]
for fid,title,url,name in items:
 p=base/'fuentes'/name
 entry=dict(id=fid,title=title,url=url,retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),path=str(p.relative_to(base)))
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as r:
    p.write_bytes(r.read());entry['content_type']=r.headers.get('content-type')
  data=p.read_bytes();entry.update(bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),status='ARCHIVADO')
 except Exception as e: entry.update(status='NO_ARCHIVADO',error=str(e))
 manifest.append(entry)
 print(fid,entry['status'],entry.get('bytes'))
(base/'fuentes'/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')

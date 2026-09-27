"""Descarga fuentes públicas pertinentes, preservando bytes y SHA256; no credenciales."""
from pathlib import Path
import urllib.request, hashlib, json, concurrent.futures, datetime
OUT=Path(__file__).parent/'fuentes'
SOURCES={
 'CNE_Res190_20250417.pdf':'https://www.coordinador.cl/wp-content/uploads/2025/04/OP00973-25.pdf',
 'SEA_RCA486_20210705.pdf':'https://firma.sea.gob.cl/publicaciones/2b/80/2152538781',
 'MMA_Res122_RCA486_2021.pdf':'https://airerm.mma.gob.cl/wp-content/uploads/2022/05/2021_RES.EX_.122_RCA-486-2021.pdf',
 'SEA_ICE_Chile2_20210611.pdf':'https://firma.sea.gob.cl/publicaciones/45/39/2152199018',
 'SEA_Oficio_Camara_28716.pdf':'https://www.camara.cl/verDoc.aspx?prmID=28716&prmTipo=DOCUMENTORESPUESTAOFICIOCOMISION',
 'CEN_EAF456_2024.pdf':'https://www.coordinador.cl/wp-content/uploads/2024/09/EAF-456-2024.pdf',
 'CEN_EAF089_2025.pdf':'https://www.coordinador.cl/wp-content/uploads/2025/03/EAF-089-2025.pdf',
 'CEN_Minuta_Chile2_202501.pdf':'https://www.coordinador.cl/wp-content/uploads/2025/01/Minuta_Solicitud_Nuevo_Transformador_para_Data_Center_Chile.pdf',
 'Ascenty_SCL03_inauguracion.html':'https://ascenty.com/en/blog/news-ascenty-en/ascenty-inaugurates-its-third-data-center-in-chile-with-total-investments-exceeding-r-6-1-billion/',
 'TIA_SCL03_certificado_20250821.pdf':'https://tiaonline.org/wp-content/uploads/2025/08/Chile_Ascenty-DC-SCL03_DCCC-epi_TIA942CL250821001-Signed.pdf',
}
def fetch(pair):
 name,url=pair;p=OUT/name;r={'archivo':name,'url':url,'consulta_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 try:
  if not p.exists():
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=45) as response: b=response.read();r['url_final']=response.url
   if name.endswith('.pdf') and not b.startswith(b'%PDF'):raise ValueError('Respuesta no PDF: '+b[:80].decode(errors='replace'))
   p.write_bytes(b)
  b=p.read_bytes();r.update(estado='DESCARGADO',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
 except Exception as e:r.update(estado='ERROR',error=str(e))
 return r
if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor: rows=list(executor.map(fetch,SOURCES.items()))
 (OUT/'manifest.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 for row in rows: print(row['archivo'],row['estado'],row.get('bytes'),row.get('error',''))

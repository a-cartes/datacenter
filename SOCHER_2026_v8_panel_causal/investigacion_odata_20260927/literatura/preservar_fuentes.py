"""Preserva cuatro fuentes primarias de literatura; no calcula efectos chilenos."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib, json, urllib.request

OUT=Path(__file__).resolve().parent
SOURCES=[
 ('LIT01','MIT_CEEPR_WP2026_13.pdf','https://ceepr.mit.edu/wp-content/uploads/2026/06/MIT-CEEPR-WP-2026-13.pdf'),
 ('LIT02','Mamkhezri_2026_en_anexo_TURN04.pdf','https://docs.cpuc.ca.gov/PublishedDocs/SupDoc/A2411007/9108/604536651.pdf'),
 ('LIT03','Watten_Bistline_Blanford_2026v1.pdf','https://arxiv.org/pdf/2606.19777v1'),
 ('LIT04','DallasFed_WP2606.pdf','https://www.dallasfed.org/~/media/documents/research/papers/2026/wp2606.pdf'),
]

def acquire(spec):
    id,name,url=spec
    p=OUT/'fuentes'/name
    r={'id':id,'archivo':'fuentes/'+name,'url':url,'consulta':'2026-09-27'}
    try:
        if not p.exists():
            req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 academic research'})
            with urllib.request.urlopen(req,timeout=45) as resp:
                data=resp.read()
            assert data.startswith(b'%PDF'), 'Respuesta no PDF'
            p.write_bytes(data)
        b=p.read_bytes()
        assert b.startswith(b'%PDF')
        r.update(estado='ARCHIVADO',bytes=len(b),sha256=hashlib.sha256(b).hexdigest())
    except Exception as e:
        r.update(estado='NO_ARCHIVADO',error=str(e))
    return r

if __name__=='__main__':
    (OUT/'fuentes').mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=2) as pool: results=list(pool.map(acquire,SOURCES))
    (OUT/'manifest_fuentes.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(results,ensure_ascii=False,indent=2))

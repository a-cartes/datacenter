"""Documenta consultas públicas pequeñas y fuentes locales pertinentes, sin credenciales."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, urllib.request

OUT=Path(__file__).resolve().parents[1]
ROOT=OUT.parents[2]
sources=[
    ('CEN_SOCKET_HABILITADO','https://medidas.coordinador.cl/SOCKET/SOCKET_HABILITADO.xlsx',ROOT/'SOCHER_2026_v3/mapeo/CEN_SOCKET_HABILITADO_20260925.xlsx','Hoja 24092026, fila921; captura previa preservada'),
    ('CEN_DT_MEDIDAS_2021','https://medidas.coordinador.cl/public/DOCUMENTACION/NORMATIVA/Documento%20T%C3%A9cnico%20Sistema%20de%20Medidas%20de%20Energ%C3%ADa%202021.pdf',ROOT/'SOCHER_2026_v3/mapeo/CEN_Documento_Tecnico_Medidas_2021.pdf','Páginas8–9: unidad kWh e integración15min; no certifica etiqueta de CSV'),
    ('INFOTECNICA_ELEMENTOS_683','https://api-infotecnica.coordinador.cl/v1/subestaciones/683/elementos/',ROOT/'SOCHER_2026_v8_panel_causal/eventos/fuentes/infotecnica_Chacabuco683_elementos.json','Medidor6871 DT7 conexión16647; no medidor dedicado E53 identificado'),
    ('INFOTECNICA_MEDIDOR_6871','https://api-infotecnica.coordinador.cl/v1/medidores/6871/',OUT/'fuentes/infotecnica_medidor_6871.json','Consulta pública27sep2026; nombreDT7, sinserie en respuesta'),
    ('INFOTECNICA_DOCS_6871','https://api-infotecnica.coordinador.cl/v1/medidores/6871/documentos/',OUT/'fuentes/infotecnica_medidor_6871_documentos.json','Consulta pública27sep2026; respuesta[]')]
parser=argparse.ArgumentParser();parser.add_argument('--actualizar-api',action='store_true');args=parser.parse_args()
records=[]
for sid,url,path,use in sources:
    if args.actualizar_api and path.is_relative_to(OUT/'fuentes'):
        with urllib.request.urlopen(url,timeout=60) as r: content=r.read()
        json.loads(content);path.write_bytes(content)
    content=path.read_bytes()
    records.append({'fuente_id':sid,'url':url,'archivo':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'alcance':use})
(OUT/'fuentes/manifest_fuentes.json').write_text(json.dumps({'fecha_registro_utc':datetime.now(timezone.utc).isoformat(),'fuentes':records},ensure_ascii=False,indent=2))

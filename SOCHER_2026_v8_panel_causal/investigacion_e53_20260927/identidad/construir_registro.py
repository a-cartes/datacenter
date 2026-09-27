"""Reproduce el registro de hechos y extractos pertinentes sin acceso a red."""
from pathlib import Path
import csv, json, hashlib
from pypdf import PdfReader
BASE=Path(__file__).parent
def write(name, rows):
 with (BASE/name).open('w',newline='',encoding='utf-8-sig') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
sources=[
 ('E53I001','SEA_RCA486_20210705.pdf','SEA','p3 etapas; p4 dirección; p16 suministro'),
 ('E53I002','CNE_Res190_20250417.pdf','CNE','p2 considerandos2-3; p4 considerando12'),
 ('E53I003','CEN_EAF456_2024.pdf','CEN/Enel','p4 tabla consumos; p144 informe Enel sección6'),
 ('E53I004','CEN_EAF089_2025.pdf','CEN','p1 fecha; p64 tabla consumos'),
 ('E53I005','CEN_Minuta_Chile2_202501.pdf','CEN','p12 descripción y naturaleza; pp13-14 simulación'),
 ('E53I006','TIA_SCL03_certificado_20250821.pdf','EPI/TIA','p1 certificado instalación construida'),
 ('E53I007','SEA_ICE_Chile2_20210611.pdf','SEA','documento de respaldo; no añade prueba E53'),
 ('E53I008','MMA_Res122_RCA486_2021.pdf','MMA','p1 vistos; lectura web, original local no disponible'),
 ('E53I009','SEA_Oficio_Camara_28716.pdf','SEA/Cámara','p6; lectura web, original local no disponible'),
 ('E53I010','Ascenty_SCL03_inauguracion.html','Ascenty','anuncio corporativo; lectura web, original local no disponible'),
]
manifest={x['archivo']:x for x in json.loads((BASE/'fuentes/manifest.json').read_text())}
catalog=[]
for ident,filename,issuer,loc in sources:
 rec=manifest[filename];catalog.append(dict(fuente_id=ident,emisor=issuer,archivo='fuentes/'+filename if rec['estado']=='DESCARGADO' else '',url=rec['url'],localizador=loc,estado=rec['estado'],sha256=rec.get('sha256',''),bytes=rec.get('bytes',''),observacion=rec.get('error','')))
write('catalogo_fuentes_identidad.csv',catalog)
facts=[
 ('I01','Data Center Chile 2','Etapa3 ambiental','E53I001','p3','ACREDITADO','Etapa3 del proyecto Data Center Ascenty; etapa2 RCA113/2021 y etapa1 sin ingreso SEIA.','No equiparar numeración ambiental con numeración corporativa.',''),
 ('I02','Data Center Ascenty','Suministro previo campus','E53I001','p16 sección4.4.2 Energía','ACREDITADO','Enel construyó alimentador23kV desde Chacabuco a Guacolda2100 lotePC-9; sala ENEL Chile1 en Unidad2 Kúrcula.','No precisa paño/fecha PES ni consumo a mayo2025.',''),
 ('I03','Data Center Chile 2','Nuevo punto acometida previsto','E53I001','p16 sección4.4.2 Energía','PROYECTADO','Nueva sala ENEL Chile2 en Unidad3 Kúrcula; cada DC con sala propia.','No equivale a ejecución E53 ni vincula NUP5417.',''),
 ('I04','Data Center Chile 2','Proyecto de nuevo consumo T10','E53I002;E53I005','Res190 p2; Minuta p12','PROYECTADO','RCA486 respalda proyecto para nuevo transformador40MVA; proyección1.5MW2025 y20.4MW2031.','No homologar con8.37MW E53; no usar proyección como medición.',''),
 ('I05','Ascenty alimentador existente','Carga prefalla','E53I003','p144 sección6; p4 tabla','OBSERVADO_INFORME_FALLA','Carga desconectada3429kW;2clientes al29ago2024.','No curva horaria ni campus/fase exacto ni E53.','2024-08-29'),
 ('I06','Ascenty alimentador existente','Carga prefalla','E53I004','p64 tabla; fecha p1','OBSERVADO_INFORME_FALLA','Pérdida de consumo5.82MW;2clientes al25feb2025.','No restar a3429kW para inferir ampliación: fechas/horas/condiciones distintas.','2025-02-25'),
 ('I07','Ascenty E53','Energización','S003_v8','p1 carta04jun2025','ACREDITADO_REUTILIZADO','NUP5417 energizado y entregado a explotación05may2025.','La conexión realizada no certifica carga neta nueva.','2025-05-05'),
 ('I08','Ascenty E53','Nuevo proyecto según solicitud','S001_v8','p1 carta13dic2024','PROYECTADO_REUTILIZADO','Solicitud busca iniciar operación de proyecto y prevé8.37MW mayo2025.','No identifica Chile1/2/3, sala de entrega ni suministro sustituido.',''),
 ('I09','DC SCL03','Certificación instalación construida','E53I006','p1','ACREDITADO','DC SCL03 Ascenty Chile en Guacolda2100; certificación inicial21ago2025.','No prueba primera operación ni suministro E53 ni equivalencia RCA486.','2025-08-21'),
 ('I10','Data Center Chile 2','Mecanismo modelado','E53I005','pp13-14 tablas4-5/4-6','SIMULADO_EX_ANTE','Escenario2031 con20.4MW no detecta congestiones en líneas adyacentes.','No resultado causal/empírico2025; supuestos sobre Renca y red.',''),
 ('I11','E53 y Chile2/T10','Equivalencia','S001_v8;S002_v8;E53I001;E53I002','conjunto fuentes','NO_RESUELTO','Fuentes revisadas no establecen enlace nominal E53 a sala Chile2 ni Chile3.','Conservar como obras/hitos separados.',''),
 ('I12','E53','Carga nueva vs traslado','S001_v8;E53I001;E53I003;E53I004','conjunto fuentes','NO_RESUELTO','Existe demanda Ascenty previa y nuevo proyecto previsto; no balance de retiros antes/después E53.','No habilitar tratamiento primera entrada ni ATT de demanda neta.',''),
]
rows=[]
for i,project,subject,source,loc,status,fact,limit,date in facts:
 rows.append(dict(hecho_id=i,proyecto=project,tema=subject,fuente_id=source,localizador=loc,estado=status,hecho=fact,limite=limit,fecha_observada=date))
write('registro_hechos_identidad.csv',rows)
write('carga_preexistente_snapshot.csv',[
 dict(fecha='2024-08-29',hora_etiqueta='04:14',subestacion='Chacabuco',alimentador='Ascenty',carga_mw=3.429,clientes=2,tipo='carga_desconectada_informe_falla',fuente_id='E53I003',pagina_pdf=144,campus_fase='NO_IDENTIFICADO',asignable_E53='NO',utc='NO_INFERIDO'),
 dict(fecha='2025-02-25',hora_etiqueta='15:16',subestacion='Chacabuco',alimentador='Ascenty / NI',carga_mw=5.82,clientes=2,tipo='carga_desconectada_informe_falla',fuente_id='E53I004',pagina_pdf=64,campus_fase='NO_IDENTIFICADO',asignable_E53='NO',utc='NO_INFERIDO')])
spec={'SEA_RCA486_20210705.pdf':[1,3,4,16,31], 'CNE_Res190_20250417.pdf':[1,2,3,4,5], 'CEN_EAF456_2024.pdf':[1,4,144], 'CEN_EAF089_2025.pdf':[1,64], 'CEN_Minuta_Chile2_202501.pdf':[5,12,13,14], 'TIA_SCL03_certificado_20250821.pdf':[1]}
for name,pages in spec.items():
 r=PdfReader(BASE/'fuentes'/name)
 for pg in pages: (BASE/'validacion'/f'{Path(name).stem}_p{pg}.txt').write_text(r.pages[pg-1].extract_text())
print('Fuentes',len(catalog),'hechos',len(rows),'snapshots',2)

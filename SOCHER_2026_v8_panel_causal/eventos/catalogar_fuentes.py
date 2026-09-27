from pathlib import Path
import csv,hashlib,json
D=Path(__file__).resolve().parent; P=D.parent.parent
sources=[
('S001','STM solicitud conexión Ascenty E53 13dic2024','https://cartas.coordinador.cl/download_saved_file/676095103563570a6909d2f6','fuentes/STM_Ascenty_E53_solicitud_20241213.pdf','p1; finalidad iniciar proyecto;8.37MW previstos','Nueva; prevista no medida'),
('S002','STM MNR Ascenty E53 13ene2025','https://cartas.coordinador.cl/download_saved_file/678a9ac43563572012d6e461','fuentes/STM_Ascenty_E53_MNR_20250113.pdf','p1 párrafoE53/BP7','Nueva; conexión nominal'),
('S003','STM término NUP5417 04jun2025','https://cartas.coordinador.cl/download_saved_file/684213aa3563577698e6da48','fuentes/STM_Ascenty_E53_termino_20250604.pdf','p1 primer párrafo;05may2025','Nueva; realización'),
('S004','STM solicitud Chile2/DCGuacolda 15nov2024','https://www.coordinador.cl/wp-content/uploads/2024/11/DE06670-24.pdf','fuentes/CEN_Ascenty_Chile2_solicitud202411.pdf','pp1-2 T10/20.4MW/previsiónseptiembre2026','Nueva; proyecto distinto deE53'),
('S005','Infotécnica Chacabuco683 elementos','https://api-infotecnica.coordinador.cl/v1/subestaciones/683/elementos/','fuentes/infotecnica_Chacabuco683_elementos.json','Barras id703BP1;707BP2MT;1741BP7MT;1451BP8MT','Captura2026 no historial automático'),
('S006','CEN Informe diario24jun2024','https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-24-06-2024.pdf','fuentes/CEN_Informe_Diario_20240624.pdf','p24 sección7; última fila LasVegas52H4','Nueva; maniobra realizada según informe'),
('S007','CEN Informe diario25jun2024','https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-25-06-2024.pdf','fuentes/CEN_Informe_Diario_20240625.pdf','p24 sección7; p21 sección4.3','Nueva; reversión/reapertura y DonHumberto'),
('S008','CEN EAF575/2024','https://www.coordinador.cl/wp-content/uploads/2025/01/EAF-575-2024.pdf','fuentes/CEN_EAF575_2024.pdf','pp4,7,8; topologíaSonda/Ascenti','Nueva; fecha10dic2024, no extrapolar2020'),
('S009','Infotécnica DUF Chacabuco NUP5417','https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/470265/','fuentes/Infotecnica_Chacabuco_DUF_NUP5417.zip','lámina8(TR7) E53/BP7;lámina1(110kV) T7/BP1','Nueva; APIfecha08may2025; cartucho revisión18nov2024; plano nominal'),
('S010','Infotécnica listado documentos Chacabuco','https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/','fuentes/infotecnica_Chacabuco683_documentos.json','id470265 fecha_modificacion','Nueva; metadatos de vigencia documental'),
('S011','CEN EAF289/2024','https://www.coordinador.cl/wp-content/uploads/2024/07/EAF-289-2024.pdf','fuentes/CEN_EAF289_2024.pdf','registro2024061933 H2LasCanteras22jun','Consultaoperacional; no evidencia maniobra24jun'),
('S012','CEN EAF141/2026','https://www.coordinador.cl/wp-content/uploads/2026/04/EAF-141-2026.pdf','fuentes/CEN_EAF141_2026.pdf','p169 registroDI2026021293; inicio programado22mar2026','Nueva; estado ejecución exitosa/PES; fecha efectiva no visible; no EO'),
('S013','ODATA cronología corporativa','https://odatacolocation.com/es/sobre-nos-2/','','Encabezados2022 y2023; IniciooperacionesST01/ampliaciónfase2','Texto leído vía herramienta web; descarga directa404; no PDFarchivado'),
('S014','CEN IAC SolarMillán NuevaLampa octubre2024','https://cartas.coordinador.cl/download_anexos/6705c78535635702715c7943/0','fuentes/CEN_ODATA_NuevaLampa_IAC202410.pdf','p4 figura1 ODATAST01 NUP2129','Nueva; esquema incluye proyectos, no certifica ejecuciónODATA'),
('S015','Sonda presentación corporativa2021','https://www.sonda.com/docs/default-source/inversionistas-accion/informacion-financiera/presentaciones-corporativas/presentacion-corporativa-16th-larrainvial-andean-conference.pdf?sfvrsn=f6c0d94c_1','','p5 cronología inicioKudos2020','Fuenteprimaria leída web; año sin fecha eléctrica'),
('L002','Mapeo físico CMg y relaciónv6','','../../SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md','LasCanteras/Libertadores; v6relacion_centros_barras.csv filaChacabuco110','Antecedente local contrastado; homologaciónjul2024fila222'),
('L003','CEN informe Edgeconnex2021','https://www.coordinador.cl/wp-content/uploads/2021/07/InfDef_EdgeConneX_Sol._de_Ejecucion_de_Obra_Urgente_de_Transmision-2.pdf','../../SOCHER_2026_v3/eventos/CEN_Edgeconnex_Informe2021.pdf','pp1-2;5-6','Antecedentev3'),
('L004','CEN EAF143/2024','https://www.coordinador.cl/wp-content/uploads/2024/04/EAF-143-2024.pdf','../../SOCHER_2026_v3/mapeo/CEN_EAF143_2024.pdf','p105 reg2024032530/31','Antecedentev3'),
('L005','CEN reporte NI/MR septiembre2024','','../../SOCHER_2026_v2/fuentes_publicas/CEN_Reporte_NI_MR_Septiembre_2024.pdf','p7 NUP3016/3975','Antecedentev2; URL enmanifestv2'),
('L006','Diagnóstico carga junio y registrofechas','','../../SOCHER_2026_v4/eventos/Diagnostico_evento_carga.md','secSecuencia;registro_fechas_observadas_y_documentales.csv','Medicionesv4; no nueva fuenteindependiente'),
('L007','CEN EAF414/2024','https://www.coordinador.cl/wp-content/uploads/2024/08/EAF-414-2024.pdf','../../SOCHER_2026_v3/mapeo/CEN_EAF414_2024.pdf','p99 reg2024080203','Antecedentev3'),
('L008','CEN justificaciónEO NUP3349','','../../SOCHER_2026_v2/fuentes_publicas/CEN_NUP3349_Justificacion_EO_2024.pdf','p1','Antecedentev2; URL enmanifestv2'),
('L009','CTNG Memoria2019','https://www.ctng.cl/wp-content/uploads/2020/04/Memoria-Corporativa-2019-CTNG.pdf','','p5','Reintento descarga2026; previa lecturav3'),
('L010','CNE717/2019','https://www.cne.cl/wp-content/uploads/2019/11/Res.-Ext.-N%C2%B0-717.pdf','../../SOCHER_2026_v3/eventos/CNE_Resolucion717_2019.pdf','EntradaLibertadores ampliación','Antecedentev3'),
('L011','CEN ECS2021','https://www.coordinador.cl/wp-content/uploads/2021/11/ECS2021_Preliminar.pdf','../../SOCHER_2026_v3/eventos/CEN_ECS2021_Preliminar.pdf','p108 tabla5-33','Antecedentev3'),
('L012','Enel Memoria2020','https://www.enel.cl/content/dam/enel-cl/inversionistas/enel-distribucion-chile/reportes/memorias/2020/Memoria-Enel-Dx-2020.pdf','','pp107-108','Leídav3/v8web; descarga previa403'),
('L013','Ascenty inauguraciónChile1','https://ascenty.com/blog/news-ascenty/ascenty-inaugura-seu-primeiro-data-center-no-chile-e-comeca-a-construcao-de-sua-segunda-unidade-no-pais/','','Comunicado17nov2020','Antecedentev3'),
('L014','CEN minuta nuevo transformadorChile2','https://www.coordinador.cl/wp-content/uploads/2025/01/Minuta_Solicitud_Nuevo_Transformador_para_Data_Center_Chile.pdf','','minuta2025','Antecedentev6; previstaagosto2026'),
('L015','Registrov6 candidatos/sockets ODATA','https://medidas.coordinador.cl/SOCKET/SOCKET_HABILITADO.xlsx','../../SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv','ODATA_LAMPA','Antecedentev6'),
('L016','ODATA carta24nov2025','https://cartas.coordinador.cl/download_saved_file/6925c4f93563570b31306392','','p1','Contrastadaweb2026; EOestimada noviembre2025'),
('L017','SantaTeresa proyectoampliación','https://cartas.coordinador.cl/show/68a378dd3563570a01a644dd','../../SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv','SANTA_TERESA_LAMPA','Antecedentev6'),
('L018','CirionDIA2023/SAN2','https://infofirma.sea.gob.cl/DocumentosSEA/MostrarDocumento?docId=2023%2F05%2F24%2Fcecb-c2f6-40e9-a2fd-cb30bcdbafb1','../../SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv','CIRION_QUILICURA','Antecedentev6'),
('L019','Quilicura sinDC adjudicado','','../../SOCHER_2026_v6_multicentros/mapeo/registro_centros_candidatos.csv','QUILICURA_SIN_DC_ADJUDICADO','Antecedentev6')]
cols=['fuente_id','titulo','url','ruta_local_relativa_a_eventos','localizador','nota','sha256_local','estado_archivo','fecha_consulta']
records=[]
for sid,title,url,path,loc,note in sources:
 f=(D/path) if path else None
 exists=bool(f and f.exists()); h=hashlib.sha256(f.read_bytes()).hexdigest() if exists else ''
 records.append(dict(zip(cols,[sid,title,url,path,loc,note,h,'DISPONIBLE' if exists else 'NO_ARCHIVADO','2026-09-27'])))
with (D/'catalogo_fuentes.csv').open('w',encoding='utf-8-sig',newline='') as f:
 w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows(records)
seen={x['fuente_id'] for x in records}
with (D/'matriz_eventos_elegibilidad.csv').open(encoding='utf-8-sig') as f:
 for r in csv.DictReader(f): assert set(r['fuente_ids'].split(';'))<=seen, r
print('Fuentes',len(records),'vinculos de matriz resueltos')

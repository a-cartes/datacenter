from pathlib import Path
import json,csv,hashlib
R=Path(__file__).resolve().parents[1];O=R/'resultados/cierre_socher_20261009'
d=json.loads((O/'diagnostico.json').read_text());e=json.loads((O/'contrastes_estadisticos.json').read_text());v=json.loads((O/'verificacion_agosto_2021.json').read_text())
# Curated evidence table; dates describe distinct events and are never conflated.
rows=[
['ODATA ST01','2022 inauguración','ODATA CHILE SPA — Batuco 023 en previsión CNE','2025, fila 3066: verificar fila en archivo extraído','Nueva Lampa 220 kV paño J9','30','MW del proyecto SAC','03-07-2023 autorización; trabajos programados 30-06-2025','DE02932-23 pp.1 y 4; EAF312/2025 DI2025070947; CNE Anexo2','No reconstruye carga 2022-2025 ni transición entre conexiones'],
['EdgeConneX SCL01','2021 anuncio de disponibilidad; intervalo 2020-2021','EDGECONNEX CHILE SPA — Batuco 023 en previsión CNE','2025','Batuco; 23 kV no coincide exactamente con barras históricas 13/110 kV','7','MW de capacidad anunciada','19-01-2021 comunicado','Inventario EDGECONNEX_2021; CNE Anexo2','Capacidad ofrecida no es retiro horario ni prueba histórica de punto de conexión'],
['EdgeConneX expansión NUP3975','No es primera entrada','Edgeconnex Chile II SpA — Las Canteras 110 en previsión CNE','2025','Las Canteras; no asignar automáticamente II y V a una etapa','40','MW en cuerpo; MVA en encabezado de la misma carta','29-05-2024 energización de paños','DE03409-24 p.1','Inconsistencia de unidad impide dosis sin aclaración; nodo de precios desde abril2024, sin pre propio'],
['ODATA ST02 NUP3129','2023 apertura anunciada','LO ESPEJO DATA CENTER SPA — Panamericana 012 en previsión CNE','2025','Panamericana, vínculo de titular reforzado por carta ST02','40.6','MW TI máximos anunciados','08-09-2026 fin de puesta en servicio de instalaciones, carta25-09-2026 ingresada28-09','OP02215-26; ALIGNED_2023; CNE Anexo2','No cambiar apertura2023 por EO2026; separar edificio, etapas e instalaciones eléctricas. Corregir atribución previa GTD'],
['Ascenty operador','Varias etapas 2020-2025','ASCENTY CHILE SPA — Chacabuco 012 y 023','2025','Chacabuco','','Sin MW operativos anuales por edificio','','CNE Anexo2','Dos puntos no equivalen a dos edificios; no desagregar SCL1/2/3 sin fuente'],
['Google Dataluna operador','Presencia previa','DATALUNA — Los Libertadores 110 y Chacabuco 023','2025','Dos puntos en previsión','','Previsión, no retiro histórico','','CNE Anexo2','No construir fecha o dosis histórica desde esta fotografía'],
['Microsoft operador','Región inaugurada2025','MICROSOFT DATACENTER CHILE LIMITADA — Chacabuco 012 y Chicureo 023','2025','Dos puntos en previsión','0','MWh previstos 2025 en esas filas','','CNE Anexo2','Cero en proyección no demuestra ausencia de consumo; no asignar las tres zonas físicas'],
['Scala operador','Operación por etapas no cerrada','SCALA CHILE DATA CENTERS SPA — Placilla CHQ 012','2025','Placilla CHQ','','Previsión sin correspondencia edificio','','CNE Anexo2','No confundir con nueva conexión Huechuraba80MW2030'],
['Ascenty SCL4','Proyecto futuro','No aplica período histórico','2027-2028 propuestos','Punta Verde110 kV','50;150','MW eléctricos acumulados previstos','Fines2027; fines2028 en DE04560-25; SAC posterior cambia calendario','DE04560-25; OP02142-25','Escenario, no tratamiento2017-2025; 150 total, no200'],
]
# Resolve actual Excel row from existing CNE extract.
with (R/'prospectiva_2030/extraidos/demanda_digital/clientes_digitales_cne_anual.csv').open() as f:
 c=list(csv.DictReader(f))
for z in c:
 if z['anio']=='2025' and z['cliente']=='ODATA CHILE SPA':rows[0][3]='2025, fila Excel '+z['fila_excel']
with (O/'matriz_conexiones_potencias.csv').open('w') as f:
 w=csv.writer(f);w.writerow(['caso','hito_edificio','registro_cliente_conexion','fecha_registro','conexion_documentada','magnitud','tipo_magnitud','hito_electrico','fuente','decision']);w.writerows(rows)
# Preserve original misattribution, correct only audited supplemental copy.
p=O/'conexiones_operadores_CNE_2025.csv'
with p.open() as f:rd=csv.DictReader(f);fields=rd.fieldnames;cc=list(rd)
for z in cc:
 if z['cliente']=='LO ESPEJO DATA CENTER SPA':z['operador']='ODATA ST02 según OP02215-26; atribución previa GTD no respaldada'
with p.open('w') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(cc)
compar=[
['Versión','PDF marzo2026,57p,SSRN5736562','Aplicación chilena2017-2025','SHA256 '+d['sha256_articulo']],
['Resultado','Congestión+pérdidas PJM','D=Pbarra−PQuillota220','D no es componente PJM observado ni todo efecto sistémico'],
['Unidad','Census tract-año','Distrito censal2017-año','Agregación geográfica; no implica conexión'],
['Ventana','2015-2024; entradas2017+','2017-2025; entradas2019+','Al menos2 años pre; ventanas diferentes'],
['Entrada','Primera operación; fechas completadas con anuncios','Colina2021,Lampa2022,SanBernardo2023','Fechas de apertura; etapas de conexión posteriores se registran aparte'],
['Barras','Incluye nuevos nodos','Incluye barras con cobertura anual>=90%','Canteras2024 excluida por75%; entra2025; NuevaLampa220soloSep2025 no alcanza90%'],
['Matching','Probit10NN reemplazo,ACS ingreso educación etc.','Probit10NN reemplazo,Censo población viviendas demografía materialidad','Sustituciones de covariables; no réplica exacta'],
['Pesos','1/m por copia','1/m por copia','Cada control único peso total1'],
['Estimación','Sun-Abraham,FEterritorio/año,referencia−1','Mismo esquema,3tratados18controles','Virginia19tratados115controles'],
['Inferencia','Agrupación por census tract','Agrupación por distrito; intervalos t convencionales','Tres tratados y pretrayectorias impiden afirmación causal firme'],
['Resultado','2.4914 USD/MWh,SE1.2460 publicado','1.052630869 USD/MWh; ICt[0.484444,1.620818]','No prueba igualdad ni diferencia entre países'],
['Alcance','Análisis causal reportado por autores','Réplica adaptada y diagnóstico de identificación','No reestimamos microdatos/código de Virginia'],
]
with (O/'correspondencia_virginia.csv').open('w') as f:w=csv.writer(f);w.writerow(['dimension','Virginia','Santiago','alcance']);w.writerows(compar)
text=f'''CIERRE ANALÍTICO SOCHER — 9 OCTUBRE 2026

Conclusión
Se mantiene la réplica adaptada como referencia, sin afirmar efecto causal. Se explica la caída previa relativa de Lampa mediante el crecimiento mayor del diferencial de los controles en2021. Las conexiones mejoran el diagnóstico de exposición, pero las fuentes disponibles no permiten aún construir una dosis histórica homogénea por instalación. Esto cierra los resultados preliminares del resumen, no un efecto causal definitivo ni un contrafactual2030.

1. Correspondencia con Virginia
Ejemplar57p marzo2026 del usuario, hash {d['sha256_articulo']}. Leídas pp.7-14 y ficha existente con tablas pp.33-34. La matriz correspondencia_virginia.csv separa reproducción de método de adaptaciones. La incorporación de nodos tiene umbral local90%: Canteras existe desde2024, pero solo entra al promedio2025. No reestimación de Virginia ni nuevo acceso a sus microdatos. Los2.49 publicados y1.05 chilenos no estiman idéntica variable física ni demuestran diferencia entre mercados.

2. Qué pasó en Lampa y controles
2020→2021: D de Lampa pasa de0.666456 a1.519782; controles de1.795171 a6.805787 (consultar series exactas). Cambio Lampa {d['cambio_Lampa_2020_2021']['D']:.9f}; cambio controles {d['cambio_controles_2020_2021']['D']:.9f}. La brecha Lampa−controles cae4.157290USD/MWh. El precio total local de Lampa sube39.647842USD/MWh y Quillota38.794516. No fue una caída absoluta del precio de Lampa ni una demostración de selección por holgura.
17/18 controles aumentanD. No es un único control atípico. Mismas52 barras de control en2020 y2021 y mismas2 de Lampa; las2 de Lampa presentan precios prácticamente idénticos, cobertura100%. No explica el salto una incorporación de barras en esos años.
Descomposición del cambio de controles: L+2.030730; C+2.979886USD/MWh. Lampa: L+0.854288; C−0.000962. C es residual por separación de subsistemas con factores por tramos; no toda congestión física. La asimetría es compatible con distinta exposición a restricciones, no identifica por sí sola la línea o falla causante.
Julio2021: D controles14.7600 yLampa2.7899; agosto21.1215 y2.3632. En agosto el componente C medio de controles es15.0857 y supera1USD/MWh en155/744 horas. Se revisaron {v['celdas']} celdas del13/08/2021, barrasLampa220,Quillota220,Andes13/110; error frente al libro original {v['error_maximo']}. No se reextrajeron todos los años ni se atribuye el episodio a una contingencia específica sin bitácora operacional.

3. Contrastes y fechas
ATT referencia−1={d['ATT']:.9f}; contraste descriptivo post menos promedio del pre propio por cohorte={d['contraste_pre_completo']:.9f}. Se usan los mismos18controles y se ponderan cohortes por5,4,3períodos post. No usar el promedio bruto de coeficientes previos de distinta composición. Tabla contrastes_cohortes.csv.
Lampa: ATT3.092433; contraste todo su pre−0.124556. Colina−0.225772 y−0.116572; SanBernardo0.463567 y0.013848. Sin Lampa ATT0.032730aprox (valor exacto en resultados05/10).
Lampa2023 con misma muestra05/10: ATT{e['fecha_original_misma_muestra']['ATT']:.9f}; intervalo{e['fecha_original_misma_muestra']['IC95']}. La fecha anterior cambia poco el punto y mucho su error; no conservar solo especificación favorable. El1.32 original combina otra fecha, otro universo de barras y otro matching.
Test conjunto completo de12 coeficientes previos cohorte-horizonte: covarianza agrupada rango5, Wald no calculable. No reportar un p inventado ni usar pseudoinversa como arreglo. Test exploratorio de3promedios en ventana común−4,−3,−2: F(3,20)={e['test_previo_ventana_comun']['F']:.6f}, pconvencional={e['test_previo_ventana_comun']['p_convencional']:.9g}. No valida inferencia con3tratados. Refuerza junto al diagnóstico descriptivo que no puede defenderse paralelismo. No elegir nueva muestra para pasar el test.

4. Conexiones y potencia
ST01: cartaDE02932-23 autoriza30MW hacia NuevaLampa220,pañoJ9,en2023. No certifica retiro30MW desde2022. Anexo deEAF312/2025 contiene trabajos programados DI2025070947 para30/06/2025; no equivale a certificado de término efectivo. Base deprevisión CNE2025registraODATA/Batuco023. Diferentes hitos y puntos no deben mezclarse. En precios hayBatuco013/110,no023; no se fuerza alias entre tensiones. NuevaLampa220apareceSep2025,sin pretratamiento local.
EdgeConneX comparte denominaciónBatuco023 en otra fila; LasCanteras110aparece paraChileII. La carta deChileV tercera etapa mezcla40MVA en encabezado y40MW en cuerpo; confirma energización de paños29/05/2024 pero no retiro40MW. Faltan correspondencias por sociedad/etapa y carga efectiva.
ST02: cartaOP02215-26,firmada25/09/2026,solicitaEO y da fin de puesta enservicio08/09/2026. La firma esLoEspejoDataCenterSpA,que permite corregir la atribución previaGTD de la filaCNEPanamericana012. No cambia por sí sola la apertura del edificio2023. No tratar40.6MW TI de diseño como potencia eléctrica retirada.
Ascenty,Google,Microsoft yScala tienen registros por cliente/punto en previsión2025-2045, no serie histórica por edificio2017-2025. Los ceros proyectados Microsoft no prueban consumo cero. Se preserva base original y se corrige solo copia auditada.
Decisión: no estimar una dosis causal ni reasignar retrospectivamente tratamientos. Una comparación por conexiones requerirá fechas de vigencia de cada suministro y retiro por etapa. La documentación ya permite señalar que independencia geográfica no implica eléctrica y que una conexión futura no prueba exposición histórica.

5. Alcance SOCHER
Word actualizado con título económico, introducción concentrada, resultado principal calificado, fila fecha original misma muestra, diagnóstico gráficoLampa, ventana previa y mecanismo de conexión. Conserva prospectiva2030 como sensibilidad explícita, no efecto de precios. Los25/13controles comunales yATT1.65 son una escala alternativa, no sustituyen el resultado distrital ni reparan el problema. Extensión máxima4p no verificada en convocatoria;4p es presupuesto editorial de trabajo.

Reproducción desde directorio del artículo
.venv/bin/python Replica_RM_desde_cero/scripts/diagnostico_cierre_20261009.py
.venv/bin/python Replica_RM_desde_cero/scripts/verificar_agosto_2021.py
/usr/local/bin/Rscript Replica_RM_desde_cero/scripts/contrastes_cierre_20261009.R
Python con pypdf: scripts/archivar_fuentes_cierre_20261009.py (solo fuentes públicas, requiere red)
Python: scripts/documentar_cierre_20261009.py
Python con python-docx: scripts/crear_resumen_socher_cierre_20261009.py
Los tres scripts de análisis no modifican las bases originales.
'''
# Take exact annual levels from saved table, avoid transcription ambiguity.
with (O/'series_grupos_anuales.csv').open() as f:aa=list(csv.DictReader(f))
vals={(r['grupo'],r['anio']):r['D'] for r in aa}
text=text.replace('controles de1.795171 a6.805787 (consultar series exactas)',f"controles de{float(vals['Controles','2020']):.6f} a{float(vals['Controles','2021']):.6f}")
(O/'INFORME_CIERRE.txt').write_text(text)
# Input/output hash manifest for standalone audit.
files=[R/'datos/panel/barra_anio.parquet',R/'datos/panel/barra_mes.parquet',R/'resultados/socher_20261005/muestra_principal.csv']
(O/'integridad_insumos.json').write_text(json.dumps({str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in files},indent=2))
print(O/'INFORME_CIERRE.txt')

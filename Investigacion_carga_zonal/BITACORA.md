# Bitácora — nueva estrategia de carga zonal

## 2026-10-11 · Apertura y línea de base

Solicitud: revisar consumos efectivos y conexiones, identificar faltantes y plantear estimación zonal, preservando las bases anteriores y registrando cambios.

Se abrió la rama `codex/carga-zonal-20261011` desde `cb61a5b87af5c5037890a71defe6f5af8c3b2cff` (v0.3.0). El repositorio de publicación estaba limpio. El proyecto contenedor tenía cambios previos, registrados en `estado_inicial.json`; no se incluyeron en esta etapa. Commit del contenedor: `b58d8a94eb49f580792cbd73d45561f84d2c7547`.

Se conservó la tabla histórica de efectos como parte de la instantánea. No se cambiaron cohortes, controles, fechas, resultados o texto SOCHER.

## Ejecución 1 · Inventario local

Se leyeron catálogos, panel comercial, pilotos, documentación, inventario de instalaciones y topología. Resultado: `resultados/20261011_inventario/`, 265 insumos con SHA-256 idéntico antes/después; 653 originales con existencia/tamaño comprobados. Se reprodujo el agregado de Panamericana.

La tabla inicial de cifras históricas se serializó con `NaN` para algunas celdas vacías. Esa primera salida se conserva intacta como registro: `NaN` no representa un resultado nuevo ni cero. Se corrigió el serializador de la ejecución siguiente para generar JSON estándar con `null`. El script inicial se conserva en `historial/auditar_disponibilidad_v1.py`.

## Ejecución 2 · Tablas físicas recuperadas y conciliadas

Los informes v7 documentaban mediciones no presentes como tablas en el checkout público. La búsqueda local las encontró en Descargas, carpeta `Medidas Transferencias económicas-selected/SOCHER_2026_v7_2020_2026/mediciones` (el nombre físico usa acento Unicode descompuesto). No se trasladaron ni modificaron.

Se verificaron las cinco tablas Parquet contra las huellas y tamaños del informe v7. Se amplió la auditoría a 271 insumos y se conservaron todos sin cambio. Se recalculó HT1+HT2 desde los registros de 15 minutos, coincidiendo con 21.912 horas del agregado archivado; se generó cobertura por socket/mes y la trayectoria mensual.

Resultado vigente: `resultados/20261011_inventario_v2/`. Se distinguen datos físicos, retiros comerciales muestreados, capacidades y previsiones. La revisión de los 63 registros es una matriz de disponibilidad: las pistas por operador quedan marcadas como candidatas, no como enlace certificado por edificio.

## Cierre de esta revisión

Se entregan informe, propuesta de diseño, tabla de cambios y mecanismo de verificación de preservación. No se descargaron nuevas bases, no se contactó a nadie y no se estimó un nuevo coeficiente de precios. El crecimiento observado de carga en equipos seleccionados se informa como dato para la siguiente etapa.

La prioridad pasa a la conciliación de conexiones/etapas y fronteras, empezando por Las Canteras y ODATA. Se mantiene abierto el análisis causal, con reglas que permitan distinguir crecimiento neto, transferencia de suministro y exposición compartida.

## Regla para próximas entradas

Cada entrada indicará fecha, pregunta, insumos con hash, transformación, carpeta de salida nueva, comprobaciones, hallazgo y cambio respecto de la decisión anterior. Los intentos fallidos se conservan o documentan; nunca se presenta una ejecución revisada como si fuera la original.


## 2026-10-11 · Conciliación Las Canteras y ODATA

Nueva solicitud del usuario: conciliar consumo físico y comercial, revisar conexiones y preparar la estimación zonal buscando indicios, sin modificar bases. Punto de partida: commit `f1e99a4`.

Antes de los nuevos coeficientes se guardó `PROTOCOLO_CONCILIACION_20261011.md`: fronteras, canales, pares comerciales, reglas de completitud, hipótesis horarias, nodos del corredor y cuatro diagnósticos carga/precio. Ejecución inicial: `20261011_conciliacion_v1`.

Resultados: 60 días comparables Canteras–SIP, error absoluto diario 0,44%; 18 días ST01–Lampa, 1,21%; un día ST02–Lo Espejo, 0,34%. Los casos Batuco/J9 y Panamericana012/CT no representan el mismo consumo en su ventana solapada. Se conservan todos los días, incluidos los discrepantes de junio de ST01.

La asociación Canteras carga–D fue positiva en los cuatro diagnósticos, sobre 25 meses en niveles. Se registró después `ADENDA_DIAGNOSTICOS_20261011.md` para examinar señal común del corredor, exclusión de meses y claves comerciales ST02. Esas pruebas son posteriores/exploratorias. Resultado: asociación casi igual en el corredor y una hipótesis de dos componentes comerciales que concuerda con CT1/CT2 los días 15/25 de julio. La alternativa no reemplaza los valores ambiguos originales.

Se revisó el plano J9–JT5 y la documentación de conexión/puesta en servicio. Se separó el hito de JT4 Lampa de la identificación pendiente del T5 ODATA. Se guardaron tabla de conexiones, fuentes y hashes. La figura descriptiva se inspeccionó visualmente; no presenta un efecto causal.

### Corrección interna de presentación de la tabla diaria

Pandas conservaba categorías de barras no seleccionadas al agrupar precios y generó filas vacías con cero observaciones. Todas estaban excluidas por la regla de elegibilidad; ninguna entró al panel mensual o regresiones. Se archivó el script v1 en `historial/conciliar_canteras_odata_v1.py` y se explicitó `observed=True` y una comprobación de barras permitidas. Nueva ejecución: **20261011_conciliacion_v2**, vigente.

Se preserva v1 completa. V2 reduce la tabla diaria de 1.199.095 a 10.271 filas observadas. Ocho tablas científicas son idénticas byte por byte, incluidos coeficientes, conciliación y panel; los precios diarios elegibles también son idénticos. Evidencia: `resultados/comparacion_conciliacion_v1_v2.json`. No cambió una base original ni una conclusión.

La ejecución principal verificó 33 insumos antes/después; el diagnóstico adicional, 11. La verificación previa de 271 insumos volvió a pasar. Se conservan la réplica, la versión v0.3.0 y las auditorías previas. No hubo descargas ni contactos externos.

## 2026-10-11 · Publicación de disponibilidad (CZ-012)

A petición explícita del usuario se incorpora la tabla íntegra de nueve recursos al README de GitHub, con fuentes y alcance local. Se publica el avance hasta a5275d5, sin reemplazar el cierre v0.3.0. La comprobación de preservación permite ahora únicamente README.md como excepción editorial fuera de la etapa; los archivos científicos siguen protegidos. Se archiva el comprobador anterior. No se modifican datos para esta publicación.

## 2026-10-11 · Controles externos y obras concurrentes (CZ-013 a CZ-016)

La tabla se publicó efectivamente en main, commit779b97c, sin modificar el tagv0.3.0. Antes de calcular nuevas pendientes se guardó PROTOCOLO_CONTROLES_EXTERNOS_20261011.md. Se conocían los resultados de la conciliación y se leyó el antecedente nacional EDGE2024, dominado por Punta Peuco023; no se presenta esta etapa como confirmación independiente.

Ejecución20261011_controles_externos_v1:84 candidatos, ranking solo con12 meses previos y validación en los12 siguientes; K5/K10, zona fija de tres barras. La comparación cercana dio pendiente zonal−0,0087 en nivelesK5. La revisión de las rutas encontró abastecimiento común por Cerro Navia y una obra posterior en Punta Peuco industrial. Se conservan selección y resultados completos.

Después se registró ADENDA_CONTROLES_DISTANTES_20261011.md. Se añadió exclusión de RM y del componente110kV del catálogo, completando tensión ausente solo desde nombres explícitos. Ejecución20261011_controles_distantes_v1: siete candidatos, K5/K7, pendientes+0,0830/+0,1031. Validación previa muestra separación+2,081/+3,132USD/MWh. La restricción se añadió después de ver la primera selección; no se oculta su condición exploratoria.

Se incorporaron tres retiros comerciales concurrentes en61 días comunes, sin imputar faltantes ni sumar claves ambiguas. Se revisaron obras de la zona y de los comparadores: ECS2025, fichas y aristas. Los indicadores de obras son sensibilidad; algunas pueden ser mediadores de demanda. Se conservaron ajustes inestables, incluido el aumento de coeficiente al excluir meses de entrada. No se declara ninguna especificación causal.

La verificación posterior añadió exclusión individual de controles como diagnóstico de influencia, calculó pendientes por fórmula independiente y comprobó D=P−Q y soporte:12 comprobaciones,46 insumos preservados. Los dos análisis principales verificaron38/39 insumos. La figura se inspeccionó visualmente. No se escribieron bases anteriores ni se cambió el manuscrito.

Reproducción pública final:80 regresiones, coeficientes y errores HAC recalculados con NumPy mediante fórmula independiente de statsmodels. Error máximo de beta9,99e−15; de error estándar5,93e−13. No requiere originales ni descarga de26GB. Se añade entorno mínimo versionado.

## 2026-10-11 · Prioridad Energy Economics y heterogeneidad horaria

El usuario establece Energy Economics como objetivo principal y SOCHER como avance separado. Solicita comprobar si mayor carga o congestión ocultan un efecto al agregar mensualmente. Se conserva el cierre anterior y se registra PROTOCOLO_HORARIO_20261011.md antes de ajustar nuevas regresiones. Punto de partida0f9168d.

Ejecución20261011_horas_v1:18.168 horas de757 días,25 meses; cargaHT1+HT2 y comparadores fijos de la etapa anterior. Se separan bloques de reloj, spline sobrep75mensual y estado Quillota≥100, este último sin interpretarlo como congestión exógena. ModelosA mes/hora-semana yB día/mes×hora/hora-semana; covarianza por scores semanales HAC4 y alternativa mensual; Holm de diferencias por familia. Hay40 regresiones principales y120 contrastes; se conservan señales negativas y positivas.

La asociación distante intradiaria solar es+0,5912, con intervalo[−0,2558;1,4382]; la de tarde-noche−0,0609. La pendiente por encima del umbral de carga es mayor, pero su diferencia no queda precisada. Una interacción negativa con precio sistémico alto frente a cercanos supera Holm: se informa sin convertirla en efecto causal. Dos subperíodos y ambos desfases horarios se calcularon según protocolo.

Ejecución20261011_episodios_horarios_v1: revisión de129 páginas de registros operativos de tres EAF,3 días. Se clasifican19 horas completas con restricción específica,46 sin ese control y7 desconocidas/transición. El estado no se extiende al resto de fechas. Para06-11-2024 el comienzo observado es prorrata01:34; no se infiere medianoche. El texto original y los documentos no se modifican.

La descomposición de pendiente mensual usa siempre la carga media mensual total: contribuciones+0,071708(solar),−0,002219(tarde),+0,013537(resto), suma+0,083026. Se distingue de las pendientes por bloque con su propia carga. El cálculo de agregación aclara el protocolo sin redefinir bloques ni escoger especificaciones posteriores.

Verificaciones:31 y6 insumos preservados; comprobación general de271 tambiénOK. Panel mensual reconstruido hasta3,6e−15; estimaciónB contrastada mediante dummies dispersas y LSQR independiente, error1,2e−11. Figura inspeccionada. Los demás cambios son nuevos informes, código, derivados y enlaces; no se toca el manuscrito ni bases originales.

Cierre de reproducción pública: las 40 regresiones y los 120 contrastes principales se reprodujeron desde el panel publicado, incluidos errores estándar semanales y mensuales; diferencia máxima menor a 9e−16. La comprobación final de los 271 insumos y del cierre histórico volvió a pasar sin diferencias.

## 11 de octubre: calendario operativo, flujos y cargas concurrentes

Solicitud: avanzar hacia la identificación del mecanismo diurno, priorizando Energy Economics. Inicio en 690987f. Se registra PROTOCOLO_OPERACION_20261011 antes de nuevas estimaciones y se preservan todos los insumos previos. El entorno científico existente se reutiliza: el runtime documental no incluye SciPy. No se instalan paquetes ni se modifican bases.

Se reextraen doce canales físicos con sus dos direcciones y se construye un calendario UTC de 18.264 horas, enlazado con las 18.168 horas del panel elegible. La frontera HT1+HT2 se reproduce con error máximo 2,7e−15. Google comercial concilia con TAP H1+H2 R en 1.528 horas de 64 fechas (WAPE 0,868%). Los canales LBR permanecen separados y no se asignan a Google por inferencia. Se ejecutan siete especificaciones en muestras comparables; los 61 días comerciales no se extrapolan a meses completos.

La descarga RIO por web no termina; la conexión API existente sí permite recuperar datos. No se registra ni publica la credencial. Piloto: página0 y1 idénticas, descarga desde1 y comprobación de página extra. Un primer lote recibe HTTP429: se detiene y se reanuda en carpetas nuevas con pausas de10s y dos trabajadores. Prueba de100.000 filas recibe504; se mantiene10.000. Las ejecuciones interrumpidas se retienen con estado incompleto, nunca como ausencia de restricciones. El piloto de limitaciones responde502, no se interpreta como base vacía.

Se descarga por el visor oficial Qlik la línea929 Lo Aguirre–Alto Jahuel C1, ambos extremos y años2024–2026. Se conserva el CSV exacto. Antes de2026 presenta ceros casi universales y magnitudes anómalas; ese tramo se excluye de la sensibilidad, sin reescalarlo ni corregir sus originales. La sensibilidad2026 compara modelos sobre las mismas5.692 horas; la señal diurna ya es próxima a cero antes de introducir el flujo500kV. No se atribuye ese cambio respecto al panel completo al control de flujos.

ADENDA_OPERACION_20261011 documenta estas decisiones y la clasificación separada de Ctx y prorrata. El calendario piloto audita siete meses y concuerda con las15 horas Ctx y46 sin ese control de los casos EAF; cuatro horas de prorrata quedan separadas. El primer ensayo de regresión RIO calculó salidas pero falló al registrar una ruta relativa; se conserva como ejecución no cerrada. Se corrige únicamente la resolución absoluta del argumento para la ejecución definitiva.

La revisión de RIO detecta el 22-01-2025 una restricción local Las Canteras–Santiago Solar (12:54–17:52), además del control sistémico AJ–LA. Se busca corroboración primaria en EAF039/2025. El episodio se examina después de conocer el patrón horario; no se elimina del panel ni se presenta como experimento exógeno. Se preservan los canales H1–H4: H2 registra cero entre10 y16 y H1 concentra tránsito. La causa de la maniobra requiere la solicitud SD2025004130.

EAF039/2025 descargado y archivado con hash. Se corroboran las instrucciones en pp.58/65 y se obtiene SD2025004130 en p.136: mantenimiento programado de Las Canteras–Las Vegas, secciones5186/5187 vinculadas a H2. La intervención asociada SI2025005181 (p.101) especifica cambios de protecciones/alimentación y menciona Don Humberto. La imagen de p.136 y la figura nueva se revisan visualmente. Este hallazgo resuelve la búsqueda documental del episodio; no se atribuye al mantenimiento la totalidad de la señal diurna.

Finaliza la adquisición RIO:25 meses completos (agosto2024–agosto2026),263 páginas archivadas incluyendo25 páginas adicionales vacías y2.251.700 registros antes de deduplicación. Todos los manifiestos mensuales terminan en descarga completa pendiente de validación. El parser definitivo valida paginación, hashes, fechas, duplicados e instrucciones; los estados desconocidos se conservan.

Cierre del calendario definitivo:747 fechas presentes de761 solicitadas (14 ausentes),15.201 duplicados exactos y40 registros discordantes; estos últimos no afectan instrucciones AJLA. En el panel,744 de757 días tienen RIO;198 horas Ctx,812 posteriores a final documentado y17.158 desconocidas/transición. Solo18 horas solares restringidas, en tres fechas de2025. No hay menciones AJLA500 en2026; no se interpreta como ausencia de congestión.

La estimación RIO v1 completó las tablas pero falló al serializar un entero NumPy. V2 corrigió la rama estimable; persistió el entero en la rama no estimable. Se archivan ambas versiones de código y ejecuciones sin cierre. V3 convierte los metadatos a tipos nativos y termina correctamente. Estimaciones, parámetros y soporte son idénticos byte por byte en v1/v2/v3. Se conserva el diagnóstico de rango9/10 del modelo por bloque, sin eliminar términos. Los dos modelos restringidos usan1.010 horas; Holm mínimo0,084.

Se entrega calendario integrado horario y resumen diario, además de menciones locales pendientes de duración (06-03-2025 y11-02-2026). Se preservan los doce canales y las señales de cero sin declararlas desconexiones. La reproducción pública verifica340 contrastes (175 cargas/flujos,75 flujo500 y90 RIO), dos sistemas LSQR independientes y duraciones del calendario. Informe y figura separan asociación, soporte y evidencia operativa; no se cambia SOCHER.


## 11 de octubre: generación vecina y maniobras (CZ-028 a CZ-031)

Inicio9fdf14e. Se registra PROTOCOLO_GENERACION_20261011 antes de descargar las series y estimar. Se mantiene prioridad Energy Economics, frontera HT1+HT2, comparadores y FE. La revisión documental añade BESS separado y fallas26-02-2025 antes de ver los coeficientes. No se modifica SOCHER.

El primer piloto sin red termina ConnectionError; el piloto con página0 responde502. Se conserva código y manifiestos. El piloto páginas1/2 verifica resultados distintos y nombres/IDs364 y2209. Consulta completa:36.530 registros de dos centrales, seis páginas incluidas dos extras vacías. Se usa la credencial local solo para la API oficial, sin registrarla. Consulta separada BESS06-03-2025: central nula,48 registros Don Humberto separados en inyección/retiro; no se presenta como historia completa ni se mezcla con PV.

Procesamiento v1 se detiene antes de regresiones por hora25 fechada06-04-2025 00:00 junto a hora1. Se conserva en auditoría, se excluye únicamente la fila especial del enlace y se mantiene la hora regular. V2 se detiene por colisión de columna auxiliar en el segundo enlace de desfase; v3 usa clave UTC explícita y valida unicidad. Se archivan los códigos anteriores y sus salidas parciales. Los46 duplicados exactos se separan solo en derivados. El último día de consulta trae medianoche únicamente: se mantienen756 días completos comunes, sin imputar23 horas faltantes.

V3 estima15 modelos y375 contrastes. Sobre18.144 horas, solar distante0,539365 baseGoogle;0,551079 conambasPV;0,549616 concuadrados. Sin cuatrofechas0,535678. Todos los intervalos solares incluyen0; menorHolm de diferencias principales0,484. Los subperíodos y desfases se conservan completos. Validación con48 valores delEAF039 da discrepancia máxima0,04MW compatible con redondeo.

Se archivanEAF092/093/108 yIRF2026001051 conhashes. EAF108 tiene otra falla como tema principal; solo su anexo nacionalCDC acredita solicitud14:12, estadoHR18:36 y cierre23:50 del06-03-2025. No se confunde solicitud con apertura efectiva. Se detecta discrepancia entreEAF092(consumo previo0MW enCanteras) ymedidoresHT1+HT2 positivos. Los tránsitosH3/H4 caen a0 en26feb, peroH4 no cae a0 el06mar durante la ventana de solicitud; se deja pendiente certificación de frontera/estado/calidad.

Reproducción pública375 contrastes, error máximo4,5e-13, dos verificacionesLSQR independientes menores5e-11;13 insumos de la estimación sin cambios. Comprobación general271 insumos ytag históricoOK. Las nuevas tablas, calendario documental, informe y figura quedan separados de originales. El ajuste solar no elimina la señal diurna; todavía faltan BESS completo, estados efectivos y una fuente defendible de variación exógena de carga.


Auditoría final posterior: la figura muestra generación nocturna en la serie etiquetada PFV Don Humberto. Se detiene el cierre editorial y se conserva borrador pre-QA. Son112 horas sobre0,1MW en98 días; umbral1MW marca93 horas en85 días. SantiagoSolar no tiene ese problema en los horarios evaluados. Consulta diaria10-01-2026 confirma44,2MW PFV y44,85MW BESS a23:00 en la propia API. No se restan ni corrigen datos. ADENDA_CALIDAD_GENERACION se registra antes de nuevas sensibilidades. Nueve modelos adicionales225 contrastes:soloSantiago enmuestra completa0,551033;sin98días base0,183773 ysoloSantiago0,204167. La reducción entre muestras no se atribuye al controlsolar. Informe y figura auditados reemplazan la lectura del borrador; el rótulo API no certifica fronteraPV. Se preservan todas las versiones.

## 11 de octubre: batería Don Humberto y estados efectivos (CZ-033 a CZ-037)

Inicio f757d7c. Protocolo antes de nuevas descargas y estimaciones. Enero se amplía por calendario a diciembre y febrero antes de observar pendientes. API180.274 registros de todas las BESS,23páginas; tres ventanas completas,70duplicados exactos DonHumberto y tres valores ausentes. La v1 de conciliación se detiene por exigir todas las horas completas: se conserva. V2 audita las ausencias; no imputa y selecciona87días para modelos API.

Se reextraen cinco canales DonHumberto de tres ZIP definitivos existentes. Lectura inicial de enero omitió separador decimal y concatenó texto en el resumen por canal. Se detecta antes de cualquier regresión física; se conserva código y resumen inválido comprimido en historial/20261011_bess_decimal. Se corrige decimal=',' y se reconstruye solo ese derivado; los bytes seleccionados y el ZIP son idénticos. Se verifican43.200 registros, UTC/local, cuatro intervalos por hora y2160horas completas. D yR no se suman entre versiones de archivos.

Enero: inyecciónAPI frente a FB1+FB2+FB3 WAPE0,0479%; retiros sumados WAPE13,5328% con denominador físico (12,4849% con denominador API en diagnóstico inicial). En los tres meses205horas muestran solapamiento de retirocentral con retirototal físico y retirosistema positivo. No se corrige la API. Diecisiete horas nocturnas de enero presentan PFVpositivo; el10ene23:00 PFV44,20, BESSfísico44,851 yH1neto44,144. EAF008 pp52/58/64 corrobora96 valoresAPI dentro de0,05MW; esto corrobora publicaciones, no demuestra una segunda medición independiente. Se preserva la incertidumbre de fronteraPV.

Se localiza SD2025023534 enEAF108p114 con fechas efectivas14:17–23:50, distintas de solicitud y término programado. Durante ocho horas completas H4 yTapLibertadoresH1 coinciden con WAPE0,0247%: la apertura de extremo remoto no elimina suministro de una derivación intermedia. Se corrige la interpretación provisional de la aparente discrepanciaH4. Informe diario11febp19 da cierre de línea13:55 yretorno de central14:45 tras salida12:15. Se codifican573,100 y150min; fuera de episodios no se presupone topología normal. SD2025004130 continúa sin intervalo efectivo completo certificado.

ComparaciónAPI87días:200contrastes. Adenda física registrada al detectar solapamiento de retiros, antes de extraer diciembre/febrero y de estimar nuevos modelos. Comparación física90días, común87 ysin11feb89:300contrastes. Diurna90días base2,832528;Santiago2,762213;BESSfísico2,760125;fronteraH1 2,774132. Intervalos aproximados de muestra corta, no conclusión causal. Controles simultáneos potencialmente endógenos. VariaciónMWparcial0,145; diferencia solar–resto0,890 con intervalo que incluye0.

Sensibilidad de influencia mensual añadida después de conocer2,774, con adenda separada para conservar intactos los hashes del protocolo anterior. Se publican150contrastes ylos tres modelos ajustados:2,699 sin diciembre;2,789 sin enero;3,035 sin febrero. No se elige una omisión preferida. Los650contrastes se reproducen; cuatro sistemas LSQR concuerdan a menos de3,3e−10. Verificación de271insumos protegidos ytagSOCHEROK. TresZIP conservan los hashes inventariados. Informe, figura y scripts nuevos, resultados anteriores intactos.

## 11 de octubre: extensión larga y variaciones de carga (CZ-038 a CZ-043)

Inicio465c236, limpio y publicado. Se registra protocolo antes de nuevas extracciones y resultados. Extracción de23ZIP definitivos existentes, reutilizando tres selecciones conciliadas. Se localizan adicionalmente julio/agosto2026 en originales_descargados de v7; hashes contra sus manifiestos anteriores. Adenda de fuentes antes de estimar. No se mezclan los libros horarios de otra familia ni preliminares. Total25meses,359.428 filas de15min;18.264horas físicas. FB1 no aparece en agosto/septiembre2024, queda ausente. No hay discordanciasUTC/local; se mantienen DST. Panel conH1 18.144h yconBESS16.704h;90días reproducidos a7,1e−15MW.

El detector lee soloHT1/HT2/HT3 y no precios: tres escalones de medianas7días (08ago2024,19dic2025,15may2026); regla baja conserva3, alta2. Once comienzos de caídas; nueve recuperan90% de referencia dentro24h. Dos comienzos tras niveles altos tienen recuperación muy tardía: no se interpretan como apagones prolongados. Se preservan candidatos completos, reglas, valores y soporte. Se reproducen con medianas/agrupación independientes desde carga pública.

Modelos:19especificaciones,475contrastes. LargoBESS696días:0,567 base y0,575 ajustado, intervalo[-0,332;1,482]. Antesdic0,441;90días2,774;desdemar−0,264. Los efectos fijos de día absorben niveles diarios, por lo que este ajuste no estima directamente el efecto de escalones permanentes. Dos contrastesLSQR concuerdan a menos8,1e−11. No se selecciona la ventana90días como resultado general.

La búsqueda documental inicial recuperaEAF584, que no se utiliza para atribuir la falla; luego se identificaEAF563 correcto. CartaDE00344-25 yrespuesta18feb2025 conanexo incorporado enp2. Solicitud adicional /download_anexos/0 devuelve500, no significa falta de respuesta. Informes diarios12/14/16may2025 devuelven404; otros seis informes se recuperan. La ausencia de menciones en informes diarios/RIO no se interpreta como red normal. Se conserva trazabilidad de intentos yfuentes.

EAF563pp1–7 atribuye accidente local03dic2024 aanimal, barra23kV1 fuera05:36–21:19 y1,12MW afectados. Respuestaoperadorp2: cuatro alimentadores deun clienteEdgeConneXII enColina, no cuatrocentros. Medición:2,080MW antes;0,907en6–15h;1,937en17–20h por incrementoHT2. El diagramaEAFp6 se inspecciona visualmente: ramas de transformadores ylíneas110kV; no acredita por sísolo el estado posterior de toda la red. La transferencia interna continúa como hipótesis por documentar.

Adenda diagnóstica posterior a inspección explicita que se conocían precios0 en8–18h. Se conservan los ceros y se comparan martes±7/14días sin presentar inferencia causal ni cocienteIV. Carga relativa−1,232/−1,223MW ybrecha−0,721/−0,892USD/MWh; conexiónHumberto ySantiagoSolar también cambian. Episodio se prioriza como dossiercandidato, pendiente contrafactual, red efectiva ymaniobraHT2. Se descarta apagón25feb como shock propio delcentro por fuente oficialCEN, sin eliminarlo de las series históricas.

Verificación42hashes de insumos nuevos,271históricos y25ZIP originales. Figuras científicas revisadas visualmente; se corrige únicamente posición de leyenda que tapaba una fecha. Resultados anteriores ySOCHER intactos. Se publican informe, fuentes, selección física, paneles, todoslos candidatos yreproducción.

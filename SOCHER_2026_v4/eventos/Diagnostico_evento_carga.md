# Diagnóstico del evento de carga de Las Canteras, 24–25 de junio de 2024

Auditoría realizada el 25 de septiembre de 2026. Se examinaron únicamente mediciones y documentación ya guardadas; no se usaron precios para localizar fechas ni se estimaron efectos causales. Los números provienen de canales originales kWhD/kWhR con su identificación y tiempo conservados.

## Dictamen

**Existe un aumento sustancial y sostenido del retiro registrado en HT1 y HT2, iniciado por etapas en la noche local del 24 de junio. El mecanismo físico que lo originó no está resuelto.** No se explica por agregar días incompletos, rellenar faltantes, confundir kWh con kW, intercambiar D/R en esos dos transformadores o cambiar de versión preliminar a definitiva. La secuencia tampoco es un salto simultáneo con un único factor común para ambos medidores. Estas verificaciones reducen esas explicaciones concretas; no prueban por sí solas que toda la variación represente carga informática nueva ni descartan cambios particulares de configuración, escala, frontera de medición, transferencia de carga o respaldo.

El 25 de junio es el primer **día local completo posterior a la transición observada**. El 24 contiene parte del aumento y debe identificarse como transición, incluyendo una sensibilidad que lo excluya de la comparación diaria. Esta fecha surge de la inspección de carga; no constituye un evento exógeno establecido antes de observar los datos. Las fechas administrativas de mayo y las maniobras documentadas de abril permanecen separadas.

## Secuencia horaria y persistencia

Las cifras son MW medios del intervalo, calculados como kWh/250. Se preserva la etiqueta UTC del original y su etiqueta local. No se acreditó si la etiqueta corresponde físicamente al inicio o al fin del intervalo; por eso no se atribuye precisión instantánea adicional.

| Etiqueta UTC | Etiqueta local (UTC−4) | HT1 D, MW | HT2 D, MW | HT1 + HT2, MW |
|---|---|---:|---:|---:|
| 25/06 01:15 | 24/06 21:15 | 0.041398 | 0.027149 | 0.068547 |
| 25/06 01:30 | 24/06 21:30 | 0.041124 | 0.091576 | 0.132700 |
| 25/06 01:45 | 24/06 21:45 | 0.040931 | 0.803257 | 0.844187 |
| 25/06 02:00 | 24/06 22:00 | 0.041033 | 0.883317 | 0.924349 |
| 25/06 02:15 | 24/06 22:15 | 0.041023 | 0.869421 | 0.910444 |
| 25/06 02:30 | 24/06 22:30 | 0.041174 | 0.870338 | 0.911512 |
| 25/06 02:45 | 24/06 22:45 | 0.045781 | 0.866729 | 0.912510 |
| 25/06 03:00 | 24/06 23:00 | 0.122446 | 0.865139 | 0.987585 |
| 25/06 03:15 | 24/06 23:15 | 0.139763 | 0.872299 | 1.012061 |

La variación principal de HT2 aparece en la etiqueta local 21:45, tras un primer aumento a las 21:30; HT1 sube principalmente a las 23:00. Sus aumentos medios entre bloques de siete días son distintos: multiplicadores descriptivos 3.970 y 36.410, respectivamente. **No son factores instrumentales** y no se aplican para corregir datos.

Se comparan bloques completos de igual longitud: 17–23 de junio y 25 de junio–1 de julio, con 672 intervalos por transformador en cada bloque. No se optimizaron estas ventanas buscando un resultado de precios.

| Serie | Media 17–23 jun, MW | Media 25 jun–1 jul, MW | Diferencia, MW |
|---|---:|---:|---:|
| HT1 | 0.037422 | 0.148562 | 0.111140 |
| HT2 | 0.025078 | 0.913091 | 0.888013 |
| HT1 + HT2 | 0.062500 | 1.061654 | 0.999153 |
| Balance auxiliar H1–H4 | 0.068976 | 1.059077 | 0.990102 |

El total diario es 0.145616 MW el 24 y 1.048994 MW el 25. La media mensual conjunta continúa elevada en julio (1.087619 MW), agosto (1.891333) y diciembre (2.157770). La asignación entre HT1 y HT2 cambia durante el año. Esto no debe modelarse como una participación fija de cada transformador.

“Sostenido” no significa sin interrupciones: el 8 de julio hay 47 etiquetas consecutivas entre 09:00 y 20:30 locales con retiro conjunto inferior a 0,1 MW. El mínimo mensual conjunto es 0.056407 MW; se conserva este episodio en `julio_retiro_inferior_01MW.csv`, sin eliminarlo ni seleccionar otra fecha de tratamiento. No se asigna una causa a ese retorno temporal.

## Calidad, versiones y configuración

- Junio tiene 2.880 intervalos por socket en cada uno de los seis sockets auditados, sin duplicación socket–UTC, sin faltantes numéricos y con separación temporal de 15 min. HT1/HT2 tienen R igual a cero durante todos sus intervalos observados de 2024. Los meses sin HT1/HT2 en los originales (enero y abril) siguen ausentes; febrero y marzo contienen ceros observados. La comparación de junio no depende de esas ausencias.
- ID_SOC, subestación, tensión y FLUJO permanecen constantes dentro de junio. HT1 es 12656 y HT2 es 12657; ambos FLUJO 1, LAS CANTERAS, 110 kV. Son etiquetas estables, no registros históricos de calibración.
- Se reextrajeron íntegramente los ZIP originales de junio preliminar y definitivo: 17,280 registros comunes (seis sockets), sin altas/bajas de claves y **cero diferencias textuales en D/R**. Solo cambia ULTIMA_LECTURA: 2 de julio en preliminar frente a 5 de julio en definitivo. Tampoco hay coincidencias de estos sockets en incompletas preliminares ni estimadas definitivas. El definitivo reextraído coincide exactamente, campo por campo, con el extracto v3. Todo ello es comparación de versiones del mismo sistema.
- El catálogo oficial guardado identifica HT1/HT2 como retiro D e inyección R, con medidores distintos (ION9000, seriales MZ-2208A690-01 y MZ-2206A994-01). Infotécnica los enlaza a transformadores 3593/3594 de Las Canteras. **El catálogo es una captura de 2026 y no certifica configuración invariable en 2024.** No se dispone en estos archivos de un historial de multiplicadores/TC/TP/calibraciones de HT1/HT2 que cierre esa alternativa. No se aplica ningún multiplicador inferido de ratios de carga.
- HT3 queda fuera: solo aparece de octubre a diciembre en los originales, D cero/R positivo y clasificación actual G_C distinta de HT1/HT2. Su configuración guardada no prueba orientación física de TC. Esta anomalía no se resuelve invirtiendo su signo.

## Flujos auxiliares: reversión frecuente, balance aproximado

H1–H4 se catalogan como tránsito; jamás se suman como demanda del centro. Se usa, solo como comprobación auxiliar, la suma algebraica de sus canales R−D. El residuo entre esa suma y el retiro HT1+HT2 promedia 0.006475 MW antes y -0.002576 MW después. La concordancia de niveles apoya consistencia interna. El residuo puede ser negativo y mostrar transitorios grandes; **no se interpreta como pérdida física identificada**, ni se certifica una frontera cerrada o sincronización perfecta.

En la etiqueta local 21:30 del 24 de junio, H2 y H3 registran energía positiva en ambos canales; en 21:45 su neto R−D ya ha invertido el signo. H1/H4 conservan su sentido en esa secuencia. Pero la inversión **no es excepcional**: H2/H3 presentan 80 inversiones cada uno en mayo y 90 cada uno en junio; 76 ocurren antes del 24 de junio y 13 desde el 25 de junio hasta fin de junio. Incluso exigiendo que ambos netos adyacentes superen 1 MW en valor absoluto, hay 34 inversiones H2 y 33 H3 en junio. Al día siguiente del salto vuelven a cambiar varias veces.

Estos conteos usan observaciones no nulas separadas exactamente 15 min; se guardan los intervalos y denominadores elegibles. Los cambios de signo son compatibles con variación habitual de flujos. Sin un registro operacional no permiten distinguir despacho, maniobra o reconfiguración, ni atribuir causalidad entre reversión y aumento de retiro. La lectura correcta es **cambio de retiro y flujo concurrentes, mecanismo no resuelto**, sin elevar una reversión frecuente a prueba de una obra nueva.

## Qué puede sostener el artículo

Se puede presentar el 25 de junio como ancla de una exposición observada al aumento del retiro registrado, explicar la transición parcial del 24, mostrar resultados por transformador y documentar una consistencia interna entre canales. No puede llamarse inauguración del centro, primera carga informática, demanda de IA, shock exógeno, nueva capacidad medida o validación física independiente. La evidencia de medición apoya investigar un cambio de demanda, pero no sustituye la identificación causal ni excluye desplazamiento de carga entre fronteras eléctricas.

Para cerrar el mecanismo se requiere una fuente independiente de las mismas lecturas: bitácora CDC/NeoMante con ejecución real, órdenes de maniobra de HT/ET1–2/alimentadores 23 kV, o registro del operador sobre toma/transferencia de carga y modificaciones de medición. La ausencia de una carta hallada en la búsqueda acotada v3 no prueba ausencia de maniobra. Los documentos y fechas observadas se distinguen en `registro_fechas_observadas_y_documentales.csv`.

## Trazabilidad y reproducción

El script `../scripts/auditar_evento_carga_junio.py` reconstruye tablas, dictamen y registro, verifica los hashes de extractos v3 y reextrae los originales junio en flujo (sin materializar CSV nacionales). Reutiliza extracciones v4 solo si sus hashes y los del ZIP coinciden. `--figures` agrega dos figuras científicas PNG/SVG. El análisis usa pandas/numpy; matplotlib solo para figuras. No se modifica v3 ni los originales.

Fuentes conceptuales ya guardadas: `SOCHER_2026_v3/mapeo/Memo_mapeo_electrico_y_unidades.md`, catálogo `socket_seleccion_identidad_y_polaridad_20260924.csv`, Infotécnica medidores 5085/5084 y subestación 2433; Documento Técnico CEN 2021 pp. 8–9 (kWh/canales/15 min), EAF143/2024 p. 105 y EAF414/2024 p. 99. El inventario y hashes quedan en `metadatos_auditoria.json` y manifiestos de extracción. `intervalos_evento_15min.csv` mantiene D/R separados, UTC/local y balance auxiliar. `resumen_ventanas_y_persistencia.csv` contiene las cifras sin redondear.

Diccionario: `HT*_D_mw` es kWhD/250, `HT*_R_mw` es kWhR/250, `retiro_HT1_HT2_mw` exige ambos registros válidos; `H*_neto_R_menos_D_mw` conserva signo instrumental; `balance_lineas_R_menos_D_mw` exige cuatro líneas válidas; `residuo_lineas_menos_HT_mw` es diferencia contable auxiliar. En las tablas diarias se promedian intervalos observados, con conteos explícitos y sin imputar ausencias. Septiembre tiene 2.876 intervalos por HT por el cambio de hora; no se fabrican los cuatro faltantes locales.

## Apéndice: documentación histórica de configuración HT1/HT2

Consulta acotada del 25 de septiembre de 2026. Se revisaron únicamente los dos listados públicos de Infotécnica para medidores 5085 (HT1) y 5084 (HT2), y los dos anexos EME que esos listados contienen. No se consultaron servicios privados ni se amplió la búsqueda a otros equipos.

**El antecedente histórico refuerza la identidad de los medidores, la dirección de los canales y la integración de 15 minutos. No documenta el mecanismo del salto de junio de 2024 ni acredita que la configuración se mantuviera constante hasta entonces.** Cada listado contiene un único archivo 7z, modificado en la API el 18 de abril de 2024. Los reportes de configuración y actas de auditoría pertinentes dentro de ambos paquetes están fechados el 27 de septiembre de 2023. No se encontró en estos dos listados un documento modificado alrededor del 24 de junio de 2024, ni en los componentes pertinentes un historial de cambios de esa fecha. Esto describe el alcance de la consulta; no demuestra que no existan otros registros operacionales.

| Medidor y enlace público | Documento interno y página | Evidencia verificada |
|---|---|---|
| [5085, anexo HT1](https://api-infotecnica.coordinador.cl/v1/medidores/5085/documentos/421551/) | `HT1/2.d/2d.- Rep. Conf. Med MZ-2208A690-01.pdf`, p. 1 | Configuración creada el 27-09-2023; serie MZ-2208A690-01; PT primario/secundario 115000/115; CT 200/1; polaridades de fase Normal. |
| [5084, anexo HT2](https://api-infotecnica.coordinador.cl/v1/medidores/5084/documentos/421552/) | `HT2/2.d/2d.- Rep. Conf. Med MZ-2206A994-01.pdf`, p. 1 | Configuración creada el 27-09-2023; serie MZ-2206A994-01; las mismas relaciones PT y CT y polaridades Normal. |
| Ambos anexos | `2.d`, pp. 11–12 | Perfil Revenue con energía por intervalo en canales delivered/received; duración de 15 minutos. |
| HT1 y HT2 | `2.j/2j. Actas de auditoría al esquema de medida de energía [serie].pdf`, p. 3 | Actas TCR-23-674 y TCR-23-675, respectivamente, de 27-09-2023. Vinculan serie, paño y S/E Las Canteras; validan delivered como retiro y received como inyección; intervalo 15 minutos. |
| HT1 y HT2 | `2.b/2b.- Cert. OLCA. Med [serie].pdf`, p. 1 | Certificados de calibración de 13-09-2022, anteriores al evento y sin seguimiento de junio de 2024. |

Las relaciones PT y CT de los reportes son antecedentes de parametrización de los equipos. No constituyen un nuevo factor que deba multiplicarse por los kWh ya publicados en los CSV del CEN. La auditoría conserva la conversión de energía de intervalo a potencia media, kWh/250, y no introduce correcciones metrológicas inferidas de la magnitud del salto. Documentar una configuración en 2023 no permite afirmar que permaneció invariable en 2024; tampoco las polaridades digitales marcadas Normal certifican por sí solas todos los aspectos de instalación física posteriores.

La página 3 de ambas actas marca como conforme que el primer período diario se registra a las 00:15. Los CSV publicados, en cambio, contienen etiquetas desde las 00:00. Este contraste hace necesario un diccionario de publicación que relacione perfil del medidor y etiqueta del archivo. **No se aplica desplazamiento automático de 15 minutos.** Las tablas y figuras mantienen las etiquetas UTC y locales originales, y el texto describe el aumento durante la noche del 24. La conclusión de que el 25 es el primer día local completo posterior es robusta a esa ambigüedad de 15 minutos, porque la última etapa principal observada queda antes de medianoche.

Como dato territorial auxiliar, las actas p. 3 sitúan los dos medidores en comuna Colina y consignan coordenadas norte 6312586,677 / este 341043,584, zona 19H. La ficha EME guardada, hoja `Ficha`, filas 5–6, presenta las mismas coordenadas bajo encabezados UTM–Datum WGS84 y relaciona ambos equipos con NUP3975. Esto aporta una localización declarada específica del equipo, pero no reemplaza la validación cartográfica de límites ni resuelve automáticamente la discrepancia con documentos posteriores que consignan Tiltil para la subestación. La ficha histórica clasifica origen de energía como T, mientras el catálogo 2026 clasifica HT1/HT2 como R: se conserva esa diferencia documental sin inferir de ella un cambio físico en junio. Los canales delivered/retiro y received/inyección sí están explícitamente validados en las actas históricas.

La consulta no aporta una bitácora de toma de carga, un cambio de multiplicadores fechado en junio o medición independiente del episodio de 2024. Por tanto, se mantiene el dictamen principal: **aumento persistente del retiro registrado, con consistencia interna y mecanismo físico/metrológico aún no completamente resuelto**. El tratamiento no se convierte por estos anexos en un shock exógeno ni en una inauguración acreditada.

Los originales y manifiestos quedan en `fuentes_medidores/`. `manifest_listados.json` guarda las dos consultas y hashes; `manifest_anexos.json`, los dos paquetes originales y sus hashes; `manifest_componentes_pertinentes.json`, los componentes examinados. `extractos_pertinentes_configuracion.json` conserva únicamente campos útiles para este diagnóstico, sin replicar parámetros de acceso o comunicaciones ajenos al análisis. Las páginas 1 de configuración y 3 de auditoría de cada medidor se renderizaron y verificaron visualmente. No se modifica la documentación v3.


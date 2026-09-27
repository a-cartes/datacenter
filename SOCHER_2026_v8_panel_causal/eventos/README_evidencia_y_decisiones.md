# Matriz de eventos y nueva evidencia documental

Revisión: 27 de septiembre de 2026. La matriz contiene **24 hitos documentales y observados**, agrupados en 9 claves de campus/grupo (una es `NO_ES_CAMPUS`). No son 24 intervenciones independientes. **Ningún hito queda habilitado todavía para ATT.** Esto no significa que no existan fechas realizadas: varias están acreditadas, pero el tratamiento económico, su historia, la ruta de precio o los comparadores siguen incompletos. Las fuentes nuevas cierran brechas concretas, sin modificar la entrega v0.2.0.

## Cierre más avanzado: Ascenty, alimentador E53, 5 de mayo de 2025

Las tres cartas de STM permiten separar propósito, conexión y ejecución:

- [Solicitud de 13 de diciembre de 2024, p. 1](https://cartas.coordinador.cl/download_saved_file/676095103563570a6909d2f6), S001: alimentador para iniciar un proyecto datacenter en las cercanías de Chacabuco, con servicio previsto en mayo de 2025. Los 8,37 MW son una previsión, no una lectura de demanda.
- [Solicitud MNR de 13 de enero de 2025, p. 1](https://cartas.coordinador.cl/download_saved_file/678a9ac43563572012d6e461), S002: E53 en barra principal N°7 de 23 kV; posición equipada, con tendido subterráneo hasta el equipo de maniobra.
- [Carta de término de 4 de junio de 2025, p. 1](https://cartas.coordinador.cl/download_saved_file/684213aa3563577698e6da48), S003: NUP 5417 energizado y entregado a explotación el **5 de mayo de 2025**. La página fue renderizada y revisada visualmente.

El [unifilar NUP 5417 de Infotécnica](https://api-infotecnica.coordinador.cl/v1/subestaciones/683/documentos/470265/), S009, confirma la cadena nominal: **E53 → BP7 23 kV → transformador 7 → BP1 110 kV**, en láminas 8 y 1, respectivamente. El archivo se incorporó al listado público el 8 de mayo de 2025; el cartucho de revisión del plano refiere la conexión E53 en noviembre de 2024. La combinación de plano nominal y carta de ejecución acredita una ruta construida, pero no un historial continuo del estado de interruptores.

La [API de elementos de Chacabuco](https://api-infotecnica.coordinador.cl/v1/subestaciones/683/elementos/), S005, identifica BP7 como barra 1741, `BA14T0835SE009T0835`; BP1 de 110 kV es barra 703, `BA01T0835SE009T0835`. La relación v6 y la homologación de julio de 2024 enlazan esta última con `CHACABUCO_____110`. Se registra **enlace nominal aguas arriba**, no precio en el empalme. `CHACABUCO_____023` corresponde a BP2 (`BA05...`), no a BP7: no se sustituye una por otra por compartir tensión.

**Brecha que permanece:** las cartas no identifican Chile1/Chile2/Chile3 ni el punto de retiro previo. No prueban si E53 incorporó demanda neta, sustituyó otra alimentación o atendió fases en crecimiento. Tampoco demuestran carga real en la fecha de energización. Por tanto, el evento es un candidato documentado para estudiar una conexión, pero no se convierte en primera entrada de un campus o en un shock de demanda exógeno.

La solicitud separada Chile2/DC Guacolda identifica un transformador N°10 y demanda final proyectada de 20,4 MW (S004). La previsión de septiembre de 2026 de esa carta y la de agosto de 2026 de la minuta previa se conservan como previsiones; no se adjudica NUP 5417 a ese transformador sin una fuente que establezca la equivalencia.

## Las Canteras: maniobra operacional contemporánea a la noche del cambio de retiro

El [Informe Diario del CEN de 24 de junio de 2024, p. 24, sección 7](https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-24-06-2024.pdf), S006, informa apertura de Las Vegas 52H4 con etiqueta **24/06/2024 21:40**, por control de transferencia de Quillota–San Pedro. También informa Santiago Solar 52H2 abierto desde el 22 de junio a las 20:48. Son fuentes operacionales independientes de las lecturas HT1/HT2 que se usaron para detectar el cambio.

El [Informe del día 25, p. 24](https://www.coordinador.cl/wp-content/uploads/2024/06/Informe-Diario-25-06-2024.pdf), S007, registra fin de la primera apertura de Las Vegas a las 12:09 y una nueva apertura a las 16:09. Santiago Solar cambia de H2 abierto a H2 cerrado/H1 abierto a las 16:05, por control de transferencia de ATR2+ATR3 de Cerro Navia. Su p. 21 registra además primera energización de la línea Don Humberto–Punta Peuco el día 25. Estas configuraciones se conservan aparte en `configuraciones_operacionales_nuevas.csv`.

La proximidad de **etiquetas nocturnas** a la subida de HT2 del diagnóstico v4 es relevante. No se ha conciliado el reloj del informe con el perfil del medidor ni con CMg; no se afirma simultaneidad física exacta entre 21:40 y 21:45. Tampoco se demuestra que la maniobra causó el aumento persistente de retiro o que se transfirió carga del campus. La nueva evidencia impide tratar el entorno de red como invariable en la ventana y ofrece una hipótesis operacional verificable, sin sustituir la brecha de carga neta nueva por otra afirmación no comprobada.

El EAF289/2024 (S011) aporta una intervención de ajustes de protección H2 el 22 de junio; no se adjudica a la noche del 24. La búsqueda no encontró una orden de toma/traslado de carga específica de HT1/HT2 ni cambio de medición en esa noche. Los diarios no son un censo de todas las maniobras: ausencia de mención no prueba ausencia de operación.

## Sonda y Ascenty anteriores: topología posterior, sin retroactividad

El [EAF575/2024](https://www.coordinador.cl/wp-content/uploads/2025/01/EAF-575-2024.pdf), S008, p. 7, presenta el diagrama previo a la falla del 10 de diciembre: Sonda en BP8 de 23 kV, servida por T8 desde BP2 de 110 kV; el alimentador rotulado “Ascenti” aparece en BP3 de 23 kV. Pp. 4 y 8 documentan recuperación mediante acople temporal BP3–BP8 y retorno a la topología previa. La página del esquema fue revisada visualmente.

Esto **no homologa retrospectivamente** el alimentador Ascenty de 12 kV cuya PES Enel fecha el 20 de junio de 2020, ni cierra la identidad del campus Sonda. La diferencia de tensión/ruta puede reflejar cambios posteriores o diferencias de nomenclatura: se registra, sin resolver por parecido de nombre. La PES Sonda de 9 de septiembre de 2020 y el año corporativo de operación Kudos 2020 son hitos distintos. BP8 no es BP2 de 23 kV, y BP2 de 110 kV no se iguala a BP1 del precio sin evidencia de acople.

Se recuperaron los paquetes públicos AsBuilt julio de 2020 y DUF enero de 2021. El primero contiene archivos CAD y el segundo cuatro láminas PDF sin texto extraíble. No se completó su reconstrucción histórica en este paquete; no se usan para certificar vigencia 2020. La brecha concreta es identificar paño y alimentación del campus en la PES y los cambios posteriores.

## ODATA: campus operativo y obra eléctrica no son el mismo evento

La [cronología del operador](https://odatacolocation.com/es/sobre-nos-2/), S013, sitúa inicio de operaciones ST01 en **2022** y ampliación de fase 2 en **2023**. Se mantienen intervalos anuales, sin crear días ficticios. La lectura fue accesible vía búsqueda web; la descarga directa devolvió 404, de modo que no se reporta un original local disponible.

El [IAC Solar Millán de octubre de 2024, p. 4](https://cartas.coordinador.cl/download_anexos/6705c78535635702715c7943/0), S014, representa la conexión NUP2129 ODATA ST01 en Nueva Lampa. El esquema de proyectos no fecha su ejecución ni acredita que esa misma ruta abastecía ST01 desde 2022. La búsqueda también recuperó metadatos de prórrogas de garantía NUP2129 en noviembre de 2025 y febrero de 2026; no se descargaron documentos confidenciales y no se interpreta una garantía como ausencia de operación del campus.

Para San Bernardo, [EAF141/2026, p. 169, registro DI2026021293](https://www.coordinador.cl/wp-content/uploads/2026/04/EAF-141-2026.pdf), S012, registra estado de ejecución exitosa de pruebas con inicio programado el 22 de marzo y describe instalaciones ODATA aún en puesta en servicio. Incluye condiciones para H1/H4 y las barras de Panamericana. Esto añade evidencia de ejecución y estado de pruebas; no acredita entrada comercial definitiva ni precisión horaria de realización porque esa tabla no presenta aquí columnas efectivas completas. La previsión EO noviembre de 2025 de la carta anterior sigue sin poder adoptarse como fecha realizada.

## Cómo integrar los archivos

`matriz_eventos_elegibilidad.csv` tiene una fila por hito/enlace y conserva incertidumbre de fechas y vigencias. Las fechas mínimas/máximas son intervalos documentales, no cohortes automáticas. `catalogo_fuentes.csv` resuelve todos los identificadores y contiene URL, archivo, localizador, huella y estado de archivo. `fuentes/manifest_descargas.json` y `manifest_miembros.json` conservan originales y miembros con huellas. `validacion/` contiene comprobaciones puntuales. Los scripts `construir_matriz_eventos.py` y `catalogar_fuentes.py` reproducen los CSV sin acceso a red; `descargar_fuentes.py` recupera solo las fuentes nuevas pertinentes.

No se une esta matriz directamente uno-a-muchos a precios: una barra–período permanece una observación aunque varios centros o hitos estén relacionados. Ninguna fila certifica comparadores como no tratados ni exposición cero. Fuera de las conexiones documentadas, la exposición sigue desconocida.

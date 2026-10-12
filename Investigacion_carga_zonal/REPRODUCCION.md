# Reproducción y control de cambios

## Dependencias y alcance

La auditoría se ejecutó con Python 3.13.9, pandas 2.3.3 y pyarrow 21.0.0, usando el entorno ya disponible en `Replica_RM_desde_cero/.venv`. No instala paquetes ni necesita red. Requiere el proyecto local completo y la carpeta de mediciones v7; los resúmenes versionados no reemplazan esos insumos.

Desde la raíz del proyecto contenedor:

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/auditar_disponibilidad.py   --proyecto .   --mediciones-legacy '/ruta/a/SOCHER_2026_v7_2020_2026/mediciones'   --ejecucion nombre_nuevo
```

La ruta de mediciones contiene `tablas/`. Usar un nombre nuevo para cada ejecución: el programa rechaza directorios existentes y rutas que salgan de `resultados/`. No ejecutar el script histórico v1: se conserva para documentar la primera auditoría.

La auditoría registra las referencias de insumos mediante tres prefijos (`proyecto:`, `repositorio:`, `mediciones_legacy:`), bytes y SHA-256. Comprueba fuentes antes/después y guarda resultados separados. Los 653 originales voluminosos se verifican por existencia/tamaño; sus hashes anteriores se conservan sin afirmar una nueva lectura completa.

Para comprobar nuevamente la preservación sin regenerar resultados:

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/verificar_preservacion.py   --proyecto .   --mediciones-legacy '/ruta/a/SOCHER_2026_v7_2020_2026/mediciones'
```

## Qué se conserva

- Versión científica anterior: tag v0.3.0, commit `cb61a5b87af5c5037890a71defe6f5af8c3b2cff`.
- Árbol Git anterior y estado del proyecto: dentro de cada ejecución.
- Primera auditoría y script v1: conservados, incluso su particularidad de serialización JSON documentada.
- Ejecución vigente: `20261011_inventario_v2`.
- Bases originales: solo lectura; no se imputaron ceros, cambiaron signos ni reemplazaron fechas en ellas.

## Si una base necesita una corrección

1. Registrar el problema y la evidencia; identificar archivo y filas/columnas afectadas.
2. Conservar original y SHA-256; crear una **versión derivada nueva** en esta etapa con referencia al original, sin sobrescribirlo.
3. Registrar en `CONTROL_CAMBIOS.csv`: identificador, fecha, antes, después, motivo, insumos, salidas y estado. Un cambio de hipótesis o criterio también se registra.
4. Recalcular únicamente productos dependientes en otra carpeta de ejecución y comparar cobertura, magnitudes y estimaciones afectadas con la versión anterior.
5. Versionar código, decisión y evidencia mediante un commit; conservar las versiones descartadas con su explicación.

Git conserva código e informes; los hashes verifican identidad de insumos externos. Ninguno sustituye una copia de respaldo de archivos grandes. Esta etapa no crea una copia adicional de los 26,54 GB.

## Límites del control

La comprobación SHA-256 cubre los 271 insumos seleccionados, no todos los archivos de todo el disco. La identidad de tablas v7 acredita que se leyeron las mismas tablas archivadas; no convierte automáticamente sus fronteras en consumo exclusivo de un centro. La comprobación del tag permite constatar que el cierre publicado anterior sigue identificado por el mismo commit.


## Conciliación y diagnósticos del 11 de octubre

Resultados principales vigentes: `resultados/20261011_conciliacion_v2/`. La v1 se conserva junto con su código archivado; la corrección posterior solo eliminó filas vacías no elegibles de la tabla diaria. Los diagnósticos adicionales y la figura se calcularon sobre v1; las observaciones utilizadas y tablas científicas son idénticas a v2, como documenta `comparacion_conciliacion_v1_v2.json`.

Reproducir la conciliación en una carpeta nueva:

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/conciliar_canteras_odata.py --proyecto . --mediciones-legacy '/ruta/a/SOCHER_2026_v7_2020_2026/mediciones' --ejecucion conciliacion_nueva
```

Reproducir la adenda (lee los resultados archivados v1 y tres originales SIP del worktree previo, solo en lectura):

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/diagnosticos_adicionales.py --proyecto . --mediciones-legacy '/ruta/a/SOCHER_2026_v7_2020_2026/mediciones' --ejecucion diagnostico_nuevo
```

Los originales SIP se esperan en `.claude/worktrees/sip-api/Panel_datos/sip_api/barrido_v2/`; no se importa el código de ese proyecto ni se modifica ese worktree. La identidad de cada archivo está en el manifiesto de la ejecución. La alternativa ST02 sigue siendo condicional.

La figura usa `matplotlib`, además de las dependencias anteriores. `scripts/figura_conciliacion.py` reconstruye la figura desde las tablas archivadas y rechaza sobrescribir su carpeta de salida. Para una variante, crear otra versión del script o cambiar expresamente la carpeta de salida, registrando ese cambio.

## Estimación zonal con comparadores externos

El entorno de investigación usa además `statsmodels` para OLS y covarianza HAC. Desde el proyecto contenedor, con los insumos locales anteriores:

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/estimar_controles_externos.py --proyecto . --ejecucion controles_externos_nueva
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/estimar_controles_distantes.py --proyecto . --ejecucion controles_distantes_nueva
```

Las carpetas de ejecución archivadas del11de octubre conservan los paneles mensuales y diarios usados. Para repetir únicamente las regresiones no es necesario descargar los originales voluminosos: los derivados publicados contienen los regresores y resultados de cada muestra. La selección completa necesita el panel nacional y mapas locales listados en los manifiestos.

`scripts/auditar_resultados_zonales.py` comprueba las ejecuciones archivadas y extrae antecedentes de fuentes locales. `scripts/figura_controles_zonales.py` usa exclusivamente resultados publicados. Ambos rechazan sobrescribir su carpeta; para una nueva auditoría o figura cambiar únicamente la carpeta de salida en una copia versionada. El protocolo y la adenda se conservan íntegros; no se modifican retrospectivamente.

### Verificación pública sin originales locales

Desde la raíz del repositorio, en un entorno Python3.13 con las dos dependencias de `Investigacion_carga_zonal/requirements-reproduccion-publica.txt`:

```bash
python -m pip install -r Investigacion_carga_zonal/requirements-reproduccion-publica.txt
python Investigacion_carga_zonal/scripts/reproducir_estimaciones_publicadas.py
```

No escribe archivos por defecto ni necesita red después de instalar dependencias. Reproduce80 coeficientes y errores HAC mediante OLS NumPy y una fórmula independiente de covarianza Bartlett; contrasta las cifras archivadas. [Resultado ejecutado](resultados/20261011_verificacion_zonal_v1/reproduccion_publica.json). Esto verifica la aritmética desde derivados públicos; la reextracción y validación de fronteras requieren los originales identificados en cada manifiesto. Las dependencias del análisis completo están en `requirements-analisis-local.txt`.

## Análisis horario y episodios operativos

Resultados principales: `resultados/20261011_horas_v1/`. Desde el proyecto contenedor:

```bash
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/estimar_heterogeneidad_horaria.py --proyecto . --ejecucion horas_nueva
Replica_RM_desde_cero/.venv/bin/python -B Publicacion_GitHub_datacenter/Investigacion_carga_zonal/scripts/episodios_y_agregacion_horaria.py --proyecto . --ejecucion episodios_nueva
```

El segundo comando lee el panel horario archivado v1 y tres PDF originales locales; requiere `pypdf==6.19.0`. No descarga fuentes ni reemplaza resultados. Los estados se limitan a tres días; las horas restantes no se imputan sin restricción. Los manifiestos fijan todos los insumos.

Desde la raíz de una copia pública de GitHub, con las dependencias de `requirements-analisis-local.txt` instaladas, sin acceso a originales:

```bash
python Investigacion_carga_zonal/scripts/reproducir_horario_publico.py
python Investigacion_carga_zonal/scripts/verificar_horario_publico.py
```

El primer comando repite40 regresiones principales y contrasta120 pendientes/diferencias y sus errores estándar. El segundo reconstruye las medias mensuales anteriores y contrasta el sistema intradiario mediante dummies explícitas y LSQR, una ruta numérica independiente. No escriben archivos por defecto. La figura se reconstruye con `scripts/figura_heterogeneidad_horaria.py`; conserva la carpeta existente y requiere cambiar la salida en una copia versionada para generar otra.

## Calendario, flujos y cargas concurrentes

Las reglas están en `PROTOCOLO_OPERACION_20261011.md` y `ADENDA_OPERACION_20261011.md`. Los insumos API comprimidos y su paginación se conservan en `fuentes_operacion/`; también el CSV Qlik original y el EAF039/2025. Las descargas interrumpidas quedan separadas y no acreditan ausencia de instrucciones.

Para comprobar las nuevas regresiones **desde la copia pública**, con las mismas dependencias científicas ya indicadas:

```bash
python Investigacion_carga_zonal/scripts/verificar_operacion_publica.py --incluir-rio --salida /tmp/verificacion_operacion_nueva.json
```

La ruta de salida debe ser nueva. El programa reproduce pendientes e intervalos de las comparaciones físicas, comerciales, del flujo de500kV y de estados RIO; verifica además duraciones del calendario. Dos sistemas de coeficientes se contrastan con dummies explícitas y LSQR independiente. No descarga datos ni modifica entradas.

Para reconstruir el calendario a partir de los JSON ya publicados y estimar en nuevas carpetas:

```bash
python Investigacion_carga_zonal/scripts/construir_calendario_rio.py --ejecucion calendario_rio_nuevo
python Investigacion_carga_zonal/scripts/estimar_estados_rio.py --panel Investigacion_carga_zonal/resultados/calendario_rio_nuevo/panel_con_RIO.csv.gz --ejecucion estimacion_rio_nueva
python Investigacion_carga_zonal/scripts/estimar_operacion_canteras.py --ejecucion estimacion_operacion_nueva
```

El calendario solo considera carpetas mensuales `_completo` cuyo manifiesto acredita descarga paginada terminada; comprueba cada hash y una página extra vacía. El estado desconocido se conserva. El contraste con EAF anteriores distingue Ctx y prorrata.

La reextracción de los doce canales usa `calendario_operativo_canteras.py`, con los insumos locales descritos en su manifiesto. `documentar_topologia_canteras.py` extrae cuatro tramos y ocho secciones del catálogo local. `auditar_flujo500_canteras.py`, `resumir_calendario_local.py` y `figura_operacion_canteras.py` conservan rutas de salida fijas y rechazan sobrescritura: para otra ejecución, cambiar únicamente el destino en una copia versionada. Los verificadores públicos no requieren esa reextracción.

`descargar_operacion_api.py` y `lote_rio_202408_202608.py` documentan la adquisición, pero no son necesarios para reproducir resultados publicados. Requieren acceso autorizado a la API del Coordinador. La credencial se lee localmente y nunca se incluye en manifiestos o URLs publicadas. El lote usa dos trabajadores, pausas y páginas de10.000 registros; los intentos fallidos de mayor tamaño y el ensayo RIO incompleto se conservan identificados. La ejecución piloto de regresión interrumpida no es un resultado vigente.


## Generación solar y maniobras

Resultado vigente: `resultados/20261011_generacion_v3/`. V1 se detuvo al detectar hora25 mal alineada; v2 por columna auxiliar duplicada en el enlace de desfases. Ambas se conservan como ejecuciones incompletas, junto con su código en `historial/`. V3 usa clave UTC explícita, excluye solo la fila especial y mantiene fechas completas comunes. No se modifica ningún original.

Desde una copia pública, con las dependencias de análisis local instaladas:

```bash
python Investigacion_carga_zonal/scripts/verificar_generacion_publica.py --salida /tmp/verificacion_generacion_nueva.json
python Investigacion_carga_zonal/scripts/estimar_generacion_canteras.py --ejecucion generacion_nueva
```

El primero reproduce375 contrastes y sus intervalos, comprueba13 hashes y contrasta dos modelos con LSQR independiente. El segundo reconstruye panel y estimaciones desde las respuestas API archivadas y EAF039, sin necesidad de descargar nuevamente ni disponer de credenciales. Ambos rechazan sobrescribir salidas. El parser verifica las centrales por ID/nombre y tecnología, elimina duplicados exactos solo en derivados y conserva auditoría de fechas especiales y faltantes.

`documentar_maniobras_generacion.py` y `figura_generacion_canteras.py` reconstruyen el calendario documental y figura, respectivamente; sus destinos fijos rechazan sobrescritura. Para una nueva ejecución, cambiar solamente el destino en una copia versionada. El calendario marca intervalos parciales y no convierte ausencia de documentación en red sin restricciones.

`descargar_generacion_selectiva.py` registra la adquisición selectiva por central y paginación desde1, con diez segundos entre solicitudes. `consultar_bess_humberto.py` documenta la consulta diaria que identifica la batería separada, con idCentral nulo. Los scripts de descarga requieren acceso a la API del CEN; nunca se registra la clave. Las consultas API fallidas se conservan, sin interpretarlas como ausencia de generación.


### Auditoría posterior de generación nocturna

La figura final es `figuras/20261011_generacion_auditada/`; la anterior conserva la interpretación provisional del rótulo API. `ADENDA_CALIDAD_GENERACION_20261011.md` documenta la detección posterior y criterios de las nuevas sensibilidades. No se modifica el panel v3.

```bash
python Investigacion_carga_zonal/scripts/sensibilidad_calidad_generacion.py --ejecucion calidad_generacion_nueva
```

`verificar_calidad_generacion.py` reproduce225 contrastes adicionales, verifica nombres y tipos de las respuestas API, y contrasta el ajuste soloSantiago con LSQR. Su salida fija rechaza sobrescritura: cambiar únicamente destino en copia versionada para repetir. La verificación archivada es `resultados/verificacion_calidad_generacion_20261011.json`. El rótulo Solar se verifica como campo de fuente, no como garantía de frontera física. La consulta diariaPFV/BESS de10-01-2026 se conserva en `fuentes_operacion/20261011_humberto_nocturno/`.

## Batería Don Humberto y estados efectivos

Informe vigente: `INFORME_BESS_Y_ESTADOS_20261011.md`. Todas las selecciones físicas y respuestas API necesarias se incluyen; no hacen falta los ZIP de varios GB ni credenciales para reproducir el análisis publicado.

Desde la raíz del repositorio, con `requirements-analisis-local.txt`:

```bash
python Investigacion_carga_zonal/scripts/conciliar_bess_y_estados.py --ejecucion bess_conciliacion_nueva
python Investigacion_carga_zonal/scripts/estimar_bess_canteras.py --conciliacion bess_conciliacion_nueva --ejecucion bess_API_nueva
python Investigacion_carga_zonal/scripts/estimar_bess_fisico.py --ejecucion bess_fisico_nuevo
python Investigacion_carga_zonal/scripts/sensibilidad_bess_meses.py --ejecucion bess_influencia_nueva
```

Las salidas deben ser nuevas. El tercer y cuarto comando toman las selecciones/paneles publicados como insumos fijos. Las estimaciones incluyen repetición íntegra de coeficientes e intervalos; los modelosAPI y físicos incluyen cuatro verificaciones con dummies explícitas y LSQR. Las verificaciones archivadas suman650contrastes. El modelo físico conserva90días; el API excluye tres días por un componente ausente; la muestra común permite separar cambios de covariables de cambios de soporte.

`extraer_medidores_humberto_ampliacion.py --zip RUTA_ZIP --ejecucion NOMBRE_NUEVO` permite reextraer también enero: valida el SHA contra el inventario, filtra por etiqueta original, conserva todos los campos y comprueba que el ZIP no cambió. Requiere los originales locales, no incluidos por su tamaño. Los tres manifiestos de selección registran ubicación relativa y hash. La lectura utiliza punto y coma y coma decimal; el primer resumen defectuoso y el script anterior se conservan claramente identificados en el historial, sin uso analítico.

`descargar_bess_ventanas.py` documenta consultas, paginación, reintentos y página adicional vacía. Requiere la credencial local existente para la API oficial; no la publica. `figura_bess_estados.py` reproduce la figura a partir de conciliaciones publicadas; reemplaza exclusivamente sus dos archivos gráficos derivados. El calendario de estados guarda fuentes, páginas, inicios y fines efectivos, y fracciones horarias. Las96 cifras impresas deEAF008 se cotejan conAPI tolerando el redondeo a0,1; los extractos literales permiten revisar la transcripción.

## Extensión larga y variaciones de carga

Informe: `INFORME_EXTENSION_LARGA_20261011.md`. Las selecciones físicas de los25meses están publicadas, incluyendo referencias yhashes de losZIP originales. Los tres meses anteriormente conciliados se reutilizan por ruta yhash. FB1 deagosto/septiembre2024 permanece ausente.

```bash
python Investigacion_carga_zonal/scripts/verificar_extension_larga.py --salida /tmp/verificacion_extension_nueva.json
python Investigacion_carga_zonal/scripts/conciliar_humberto_largo.py --ejecucion panel_largo_nuevo
python Investigacion_carga_zonal/scripts/estimar_humberto_largo.py --ejecucion estimacion_larga_nueva
python Investigacion_carga_zonal/scripts/diagnosticar_variaciones_carga.py --ejecucion diagnostico_variaciones_nuevo
```

El verificador comprueba hashes, vuelve a detectar escalones desde carga pública usando otra implementación y valida duraciones. Lee el comprobante de reproducción de las regresiones; para volver a estimar475contrastes, usar el tercer comando, que además repite los ajustes ycontrasta dos modelos conLSQR. Los comandos de estimación/diagnóstico toman elpanel publicado como entrada fija; la segunda línea permite comprobar separadamente su reconstrucción. Salidas nuevas obligatorias.

`detectar_variaciones_carga.py --mediciones RUTA_PARQUET_V7` reproduce la extracción desde el insumo local verificado; su salida fija no debe sobrescribirse. La verificación pública utiliza `carga_fisica_horaria.csv.gz` para comprobar la misma detección sin necesitar eseparquet. El detector solo lee consumo, no precios. Los contrastes posteriores del episodio son descriptivos; su adenda declara la inspección previa de precios yrecuperación.

`extraer_humberto_largo.py --originales RAIZ_DESCARGAS` y`extraer_humberto_final_2026.py --legacy CARPETA_MEDICIONES_V7` documentan la reextracción de originales. Requieren archivos masivos locales, no necesarios para la reproducción pública. VerificanSHA antes/después. Sus destinos fijos rechazan sobrescritura; para repetir desdeZIP, cambiar únicamente salida enuna copia versionada. `documentar_variaciones_carga.py` y`descargar_evento_20241203.py` registran adquisición documental; no se ejecutan para reproducir tablas yconservan intentos404/500 como fallas de adquisición. La respuesta deloperador contiene suanexo enpágina2.

`figura_extension_larga.py` reproduce las dosfiguras PNG/PDF a partir detablas publicadas ysolo sustituye sus derivados gráficos. LosEAF se conservan íntegros; eldiagrama deEAF563p6 se revisó visualmente ylos extractos localizan páginas relevantes. Elestado previo dibujado no certifica por sísolo elestado durante toda lafalla.

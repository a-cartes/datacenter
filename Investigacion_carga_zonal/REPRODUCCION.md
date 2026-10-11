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

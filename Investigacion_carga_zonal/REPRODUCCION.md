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

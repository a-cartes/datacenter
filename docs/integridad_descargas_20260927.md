# Control de descargas e integridad de las fuentes

**Revisión del 27 de septiembre de 2026, posterior a v0.2.0.** No se detectó truncación en los archivos de precios efectivamente utilizados. Este resultado se refiere a la integridad de los archivos; no declara terminado el dataset causal.

La revisión responde a la presencia de archivos `Unconfirmed … .crdownload` en Descargas. Su existencia acredita intentos incompletos, pero no permite deducir por sí sola qué archivos alimentaron el CSV. Se siguió la cadena de fuentes de cada partición, se leyeron los archivos hasta el final y se contrastaron tamaños, CRC y huellas SHA-256.

## Resultado de los controles

| Componente | Alcance comprobado | Resultado |
|---|---|---|
| Histórico | 55 libros de precios y 11 tablas de homologación usadas; 3.916 miembros internos de Excel | Sin errores de integridad; hashes y conteos coinciden con los registros de extracción |
| Formato moderno | 28 originales: 27 DEF y 1 PRE separado; 10.809.879.936 bytes TSV descomprimidos | Lectura íntegra, CRC, tamaños y SHA-256 correctos; tamaño igual al `Content-Length` registrado |
| Procedencia moderna | 56 particiones de 15 minutos y horarias | Referencian los originales comprobados; los tres parciales archivados están excluidos |
| Nuevas descargas completas | Julio y agosto de 2023; febrero de 2024 | Los tres libros de precios son idénticos a los utilizados; los 12 miembros exteriores de los ZIP pasan CRC |
| CSV publicado | 3.411.527 filas y 31 columnas | Conserva exactamente su huella publicada; no fue sustituido |

## Qué ocurrió con los archivos incompletos

`Unconfirmed 151935.crdownload`, seleccionado en la captura, contiene un auxiliar `FPen_2303_def.zip` cortado. No es el libro de precios empleado para marzo de 2023: ese libro procede de otro ZIP completo y verificado.

La procedencia original de los 55 meses históricos se divide en 49 ZIP con directorio central y miembros utilizados reverificados, dos recuperaciones de libros completos en v7, una recuperación heredada de v4 y tres carpetas descomprimidas por Safari. **No todos los archivos parciales fueron simplemente descartados:** algunos contenían, antes del punto de interrupción, un libro de precios completo. Su recuperación exigió longitud exacta, fin correcto de descompresión, CRC y estructura interna de Excel. No se completaron bytes faltantes ni se convirtió un archivo parcial en ZIP cambiando su extensión.

Para reforzar la evidencia, se descargaron completos los ZIP de **julio/agosto de 2023 y febrero de 2024**. La igualdad SHA-256 confirma que los libros recuperados tienen exactamente los mismos bytes que los contenidos en esas nuevas descargas oficiales. Febrero incluye también una homologación idéntica. Los archivos de contraste se preservaron localmente; sus huellas, URLs y resultados están documentados en el [detalle de los tres contrastes](../SOCHER_2026_v7_2020_2026/auditoria/control_descargas_20260927/Resumen_contrastes_completos_20260927.md).

## Hallazgo adicional: homologación de agosto de 2023

El ZIP completo de agosto contiene una tabla de equivalencias que no se había obtenido en la recuperación anterior. Tiene 59.318 bytes y SHA-256 `435602c95a5e18e813f3f677d3140bd6298be046a5fd36c60459552be562f304`. Sus diez miembros internos de Excel pasan CRC.

Se conserva como evidencia separada en `miembros_nuevos/202308/`. **Todavía no forma parte de v0.2.0.** No modifica los precios, pero permite revisar y completar identificadores en una próxima versión. Deben verificarse su correspondencia mensual y las uniones antes de incorporarla; la equivalencia de un código tampoco acredita por sí sola una conexión física centro–barra.

## Alcance y límites

- Esta auditoría comprueba bytes, estructura y procedencia. No repite una comparación independiente de todas las celdas de los libros nacionales con todas las filas extraídas. La comparación previa CSV–Parquet y la reproducción del paquete son controles diferentes.
- Se verificaron los miembros históricos utilizados. No se repitió el CRC de todos los auxiliares de los otros 49 ZIP nacionales; sí se comprobó todo el contenedor exterior de las tres descargas nuevas.
- Un archivo íntegro puede contener vacíos o errores del proveedor. La cobertura sigue siendo desigual entre barras y fechas. DEF llega al 18 de septiembre de 2026; PRE permanece separado.
- Las fechas de entrada, las conexiones centro–barra, los relojes y la selección de controles siguen pendientes de validación científica.

## Evidencia y repetición del control

Los informes y scripts están en [la carpeta de auditoría](https://github.com/a-cartes/datacenter/tree/main/SOCHER_2026_v7_2020_2026/auditoria/control_descargas_20260927), junto con un inventario de huellas. Las ejecuciones iniciales se conservan; las revalidaciones posteriores tienen su propio informe. La copia exacta del programa moderno original respalda la huella registrada en `moderno.json`; su variante parametrizada permite repetir el control en otra ubicación.

La repetición requiere los originales nacionales y antecedentes de procedencia locales: el paquete `Insumos_reproduccion_2020_2026.zip` distribuye particiones y metadatos, **no todos esos originales**. El script `auditar_moderno.py` recibe `--moderno-dir` y `--output`; el histórico utiliza la estructura de carpetas v7 y los antecedentes v4 registrados. Todos escriben informes nuevos; no alteran precios ni manifiestos congelados. Las pruebas de truncamiento y modificación de bytes se realizan en memoria.

El [control del CSV al cierre](../SOCHER_2026_v7_2020_2026/auditoria/control_descargas_20260927/csv_al_cierre_sin_cambios.json) conserva su SHA-256: `19bc55d1a30cc59d63c2160a494ea39a42b625cdbb5f66761c360616e3f00d0b`. Se añade evidencia a la versión existente, sin reemplazar el tag, los archivos publicados ni los datos anteriores.

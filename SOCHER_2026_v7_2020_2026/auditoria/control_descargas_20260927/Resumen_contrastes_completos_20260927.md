# Contraste con nuevas descargas completas

Los tres libros de precios procedentes de recuperaciones de miembros completos se contrastaron con nuevas descargas oficiales completas. Los SHA-256 coinciden exactamente con los utilizados en la entrega. Se comprobaron todos los CRC del contenedor exterior en las tres descargas.

| Mes | Precio frente a entrega | Homologación | Informe |
|---|---|---|---|
| 202307 | SHA-256 idéntico | Sin miembro de homologación CMg en el índice exterior | [contraste_zip_completo_202307_20260927T053008Z.json](contraste_zip_completo_202307_20260927T053008Z.json) |
| 202308 | SHA-256 idéntico | Adicional; guardada sólo en auditoría, pendiente de futura versión | [contraste_zip_completo_202308_20260927T053213Z.json](contraste_zip_completo_202308_20260927T053213Z.json) |
| 202402 | SHA-256 idéntico | Idéntica a la utilizada | [contraste_zip_completo_202402_20260927T052841Z.json](contraste_zip_completo_202402_20260927T052841Z.json) |

La homologación adicional de agosto de 2023 se conserva en `miembros_nuevos/202308/Homologación barras cmg 2308.xlsx`, con SHA-256 `435602c95a5e18e813f3f677d3140bd6298be046a5fd36c60459552be562f304`. Sus CRC internos OOXML también resultaron correctos. No se incorporó a los datos, manifiestos, paquete de insumos ni versión v0.2.0 congelados.

Las copias de los ZIP se conservan en `originales_contraste/`. La concordancia demuestra igualdad de los archivos y detecta truncamiento o corrupción de bytes; no certifica las fechas de entrada de centros, los vínculos eléctricos o la identificación causal.

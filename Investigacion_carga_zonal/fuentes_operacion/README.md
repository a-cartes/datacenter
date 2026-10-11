# Fuentes operativas preservadas

Descargas del Coordinador Eléctrico Nacional realizadas para el calendario de Las Canteras. Las fuentes originales no se corrigen; los estados de calidad y los derivados están en `../resultados/`.

- `20261011_rio_YYYYMM_completo/`: respuesta API de instrucciones operacionales CMg, comprimida por página. El manifiesto registra ruta pública, fechas solicitadas, número de página, filas, tamaño y SHA-256. Una página adicional vacía comprueba el final de la paginación. La validación posterior está en `../resultados/20261011_calendario_rio_v1/`.
- Otras carpetas RIO: pilotos, intentos interrumpidos y prueba de100.000 filas. Se preservan para trazabilidad; no se mezclan automáticamente con meses completos. Algunas páginas0/1 del piloto son idénticas; la descarga mensual usa páginas desde1.
- `20261011_limitaciones_piloto/`: intento que recibió errorHTTP502; no acredita ausencia de limitaciones.
- `20261011_qlik_AJLA/`: CSV exacto de la exportación Qlik, línea929 Lo Aguirre–Alto Jahuel C1, ambos extremos. El tramo anterior a2026 presenta anomalías y no se usa en la sensibilidad de precios.
- `20261011_EAF0392025/`: PDF oficial íntegro, manifiesto y extracción de las páginas relevantes. Documenta el registro operativo del22-01-2025 y las solicitudes SD2025004130/SI2025005181. La falla que da título al EAF no se usa para atribuir causalmente esos otros eventos.

El archivo API conserva el nombre de campo original `zona_desaclope`. Las etiquetas, despachos e instrucciones no son medidas de energía generada. La ausencia de una anotación no se convierte en ausencia de congestión.

Las credenciales de consulta no forman parte del repositorio. Los scripts de descarga requieren acceso autorizado local; la reproducción de los resultados publicados usa los archivos ya archivados.

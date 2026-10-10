# Registro de cambios

## 0.3.0 — Cierre SOCHER RM

- Nueva entrada principal 2017–2025 y manuscrito aportado por los autores.
- Reconstrucción de muestras y emparejamiento, estimación Sun–Abraham, sensibilidad de Lampa, tendencias previas, Figura 1 y cuenta condicional 2030.
- Paneles, inventario, fuentes, decisiones y referencias con SHA-256; 35 controles científicos de consistencia en la ejecución local.
- Separación explícita entre reproducción desde derivados y adquisición de originales.
- Versiones previas conservadas; no se presenta inferencia causal robusta ni simulación PET26 ejecutada.
- Documentación de acceso público y citación actualizadas.
- Desempate explícito entre nodos con covariables idénticas para asegurar portabilidad Mac/Linux; referencias históricas conservadas. No cambia la muestra ni las estimaciones distritales del resumen.

# Historial de versiones

## Auditoría posterior a v0.2.0 — 27 de septiembre de 2026

- Recomprueba integridad de 55 libros históricos, 11 homologaciones usadas y 28 originales modernos (27 DEF y 1 PRE separado).
- Contrasta julio/agosto de 2023 y febrero de 2024 con nuevas descargas oficiales completas: libros de precios idénticos a los usados.
- Preserva una homologación adicional de agosto de 2023 como evidencia, pendiente de una nueva versión; no modifica códigos ni precios publicados.
- Añade informes, programas y límites del [control de descargas](docs/integridad_descargas_20260927.md). La integridad de archivos no equivale a una nueva validación celda por celda ni causal.
- Mantiene sin cambios el CSV, los archivos de la versión, el paquete de insumos y el tag v0.2.0.

## v0.2.0 — 27 de septiembre de 2026

- Amplía precios a 3.411.527 registros de barra y hora publicada, entre 01/01/2020 y 18/09/2026, en 31 variables.
- Integra 55 particiones históricas y 27 modernas DEF; mantiene septiembre PRE separado.
- Añade CSV completo, siete CSV anuales, Parquet, diccionario, cobertura y reporte de faltantes.
- Conserva los relojes originales y códigos mensuales, sin inferir UTC ni tratamientos.
- Incorpora 1.862.581 mediciones de 15 minutos en una capa separada, con antecedentes horarios y agregado HT1 + HT2 sujeto a validación eléctrica.
- Valida las 31 columnas entre CSV y Parquet, la concatenación anual y el archivo comprimido. Recontrasta los 178.016 precios anteriores sin diferencias.
- Preserva fuentes, huellas, extracción desde ZIP/OOXML/TSV y cuatro adquisiciones verificadas en GitHub Actions.
- Distribuye un paquete de insumos para reconstrucción exacta de los CSV; los originales nacionales permanecen como etapa de adquisición separada.
- Reconstruye el mismo CSV en el entorno local y en Linux, desde el paquete publicado, y conserva los informes de ambas ejecuciones.
- La verificación computacional no resuelve fechas de tratamiento, continuidad física ni validez causal.

## 0.1.0 — Base observada, paquete de trabajo

Preparación local: 25 de septiembre de 2026. [Primera versión del repositorio privado](https://github.com/a-cartes/datacenter/releases/tag/v0.1.0): 26 de septiembre UTC, todavía 25 de septiembre en Chile.

- Panel de 178.016 observaciones de barra y hora, con 66 variables.
- Diferenciales descriptivos respecto de Quillota 110 y 220 kV.
- Registro separado de candidatos, eventos, conexiones y mediciones.
- Exportaciones originales de Excel y CSV verificadas íntegramente.
- Documentación del proceso, controles e identificación explícita de vacíos.
- Estructura independiente para reproducción desde los extractos conservados.
- Proceso sistematizado mediante una adaptación documental de W3C PROV-DM, ocho etapas y diez decisiones auditables.
- Modelo formal de medición, enlace eléctrico con vigencia y diseño causal propuesto, con bibliografía primaria.
- Instalación en un entorno virtual nuevo y reconstrucción completa de CSV y Excel verificadas en macOS ARM64; registros conservados.
- Versiones transitivas fijadas y flujo manual de GitHub Actions preparado para reconstrucción completa.
- Reconstrucción completa en Linux verificada en [GitHub Actions](https://github.com/a-cartes/datacenter/actions/runs/36204205401), con evidencia conservada y CSV idéntico al original.

El paquete no adjudica tratamientos ni presenta estimaciones causales. La adquisición completa desde todos los archivos originales y la réplica por otro investigador siguen pendientes de demostración.

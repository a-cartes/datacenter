# Prueba de reproducción en un entorno nuevo

[Inicio](../README.md) · [Instrucciones](reproducir.md) · [Proceso](proceso.md)

**Resultado: satisfactorio.** El 25 de septiembre de 2026, hora de Chile, se instaló un entorno virtual nuevo y se reconstruyó el paquete en una carpeta temporal independiente. La prueba se realizó en el mismo equipo del trabajo original, con Python 3.13.15 sobre macOS ARM64. No es una réplica realizada por otro investigador ni una prueba en Linux o Windows.

## Qué se comprobó

| Comprobación | Resultado |
|---|---|
| Aislamiento de paquetes | `include-system-site-packages = false` |
| Instalación desde requisitos declarados | Siete paquetes instalados, incluidas dependencias transitivas |
| Insumos archivados | 90 archivos verificados por tamaño y SHA-256 |
| Secuencia ejecutada | 11 pasos con salida cero: entradas, seis constructores/controles, contrato y tres pasos de exportación |
| Contrato de salida | Doce tablas verificadas |
| CSV y Excel | 178.016 filas, 66 variables, claves únicas, vacíos y diccionario verificados |
| CSV reconstruido frente a entrega original | SHA-256 idéntico: equivalencia exacta de bytes |
| Excel frente a su fuente | Error numérico máximo 5,6843 × 10⁻¹⁴; tolerancia absoluta 10⁻¹⁰ |
| Duración registrada de reconstrucción y exportación | 219,53 segundos, sin incluir instalación ni trabajo humano previo |

El Excel regenerado tiene otra huella de archivo. Las huellas identifican contenedores exactos; el control compara el contenido científico y la estructura del libro. Un hash distinto del Excel no demuestra pérdida de datos.

## Evidencia conservada

- [Manifiesto y huellas de los registros](evidencia/2026-09-25/manifiesto.json).
- [Registro de los once pasos y sus programas](evidencia/2026-09-25/registro_reproduccion.json).
- [Verificación integral de las exportaciones](evidencia/2026-09-25/verificacion_exportacion_excel_csv.json).
- [Contrato de las doce tablas](evidencia/2026-09-25/verificacion_contrato.json).
- [Configuración del entorno](evidencia/2026-09-25/pyvenv.cfg), [dependencias instaladas](evidencia/2026-09-25/dependencias_instaladas.txt), [registro de instalación](evidencia/2026-09-25/instalacion.log) y [salida de ejecución](evidencia/2026-09-25/ejecucion.log).

Los registros se conservan con sus rutas temporales originales. Son evidencia histórica de esta ejecución; no deben copiarse como rutas de configuración en otro equipo. El campo `instalacion_limpia_verificada` del ejecutor permanece en `false` porque ese programa no crea ni evalúa entornos. La evidencia de instalación nueva está separada en la configuración y el registro de instalación de esta auditoría.

Los códigos de construcción comprobados corresponden al paquete local de base; cada paso conserva la huella del programa. La documentación metodológica añadida después no modifica esos programas. El [programa de archivado](../scripts/archivar_prueba.py) comprueba los informes, las huellas de los programas ejecutados y los archivos exportados antes de conservar la evidencia.

## Cómo se hizo

1. Copiar los archivos del paquete a una carpeta independiente, excluyendo tablas regeneradas, artefactos, entornos y Git.
2. Crear un entorno nuevo con Python 3.13.15, sin paquetes del sistema.
3. Instalar `requirements.txt`, guardar el registro de instalación y las versiones instaladas.
4. Ejecutar `python scripts/reproducir.py --con-excel` desde la copia independiente.
5. Comprobar el resultado, conservar los registros y contrastar la huella del CSV con la entrega original.

El archivo [requirements-lock.txt](../requirements-lock.txt) fija las siete versiones que resultaron de esa instalación. Conserva versiones transitivas; no es un bloqueo con hashes de ruedas para todas las plataformas.

## Límite de la prueba

Se reconstruye desde extractos archivados. La nueva adquisición y extracción de todos los originales nacionales, la validación de fechas y vínculos eléctricos y la estimación causal no fueron ejecutadas. Las comprobaciones locales tampoco prueban que GitHub Actions haya corrido: sus resultados se acreditan por separado cuando exista una ejecución remota.

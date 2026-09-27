# Prueba de reproducción en un entorno nuevo

> Esta página conserva la documentación de **v0.1.0**, con cobertura parcial de 2024. Para el dataset ampliado y su verificación consulte la [guía 2020–2026](ampliacion_2020_2026.md).

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

Se reconstruye desde extractos archivados. La nueva adquisición y extracción de todos los originales nacionales, la validación de fechas y vínculos eléctricos y la estimación causal no fueron ejecutadas. La prueba local y la prueba remota siguiente conservan evidencias separadas.

## Reproducción remota en GitHub Actions

La [ejecución 36204205401](https://github.com/a-cartes/datacenter/actions/runs/36204205401) terminó con resultado **success** el 26 de septiembre de 2026 UTC, todavía 25 de septiembre en Chile. Utilizó el código `f4081cda5efd142358674e9c5524156ac985e9d3`, un equipo Linux x86_64 de GitHub y Python 3.13.15. Instaló `requirements-lock.txt` y ejecutó `scripts/reproducir.py --con-excel`.

Los once pasos terminaron satisfactoriamente. El contrato de doce tablas y la comparación de las 178.016 filas de cada exportación resultaron **OK**. La huella del CSV coincide con la entrega local: `1464b1e03084046250b80a854c99c6f45a2508b0d972f5222ed348e8c4070a47`. El máximo error numérico del Excel fue 5,6843 × 10⁻¹⁴, dentro de la tolerancia de 10⁻¹⁰.

Se conservan [metadatos de GitHub](evidencia/github-36204205401/ejecucion_github.json), [registro de pasos](evidencia/github-36204205401/registro_reproduccion.json), [contrato](evidencia/github-36204205401/verificacion_contrato.json), [verificación de exportaciones](evidencia/github-36204205401/verificacion_exportacion_excel_csv.json) y [manifiesto de integridad](evidencia/github-36204205401/manifiesto.json). Estas copias permanecen en Git aunque caduque el artefacto temporal de Actions.

Esta prueba acredita ejecución en otra plataforma y equipo. No representa revisión por un investigador independiente, verificación de todos los originales nacionales ni identificación causal. Los cambios posteriores de documentación de la versión v0.1.0 no alteran los programas, insumos ni requisitos que fueron comprobados en esa ejecución. Los archivos descargables de la versión corresponden a la auditoría local, con sus propias huellas e informe; no se intercambian con el contenedor Excel generado en Linux.

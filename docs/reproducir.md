# Reproducir esta versión

[Inicio](../README.md) · [Datos](datos.md) · [Método](metodologia.md)

## Alcance comprobado

La reconstrucción se ejecutó satisfactoriamente en una carpeta independiente del proyecto original, usando el entorno Python local existente. Incluyó los seis pasos de construcción y comprobación, más la revisión de entradas y el contrato de doce tablas. El panel resultante conserva 178.016 filas y 66 variables.

Esta prueba demuestra la reconstrucción desde los extractos incluidos en el paquete. No demuestra una instalación limpia de dependencias ni una nueva descarga y extracción de todos los originales nacionales.

## Preparar el entorno

Se observaron Python 3.13.15, pandas 3.0.5, numpy 2.5.3, pyarrow 25.0.1 y openpyxl 3.1.5. Están registrados en `requirements.txt`, `.python-version` y `environment.json`. La siguiente instalación debe verificarse en el equipo donde vaya a utilizarse:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Los comandos siguientes asumen que estás en la raíz del repositorio. En Windows, utiliza el ejecutable del entorno correspondiente. No ejecutes Python con `-O` ni `-OO`: los constructores usan aserciones para verificar los datos.

## Comprobar los insumos

Sin instalar bibliotecas de análisis, puedes comprobar las huellas y tamaños de los archivos incluidos:

```bash
python scripts/verificar_insumos.py
```

El [inventario de entradas](../SOCHER_2026_dataset/documentacion/inventario_insumos_repositorio.json) registra 90 archivos archivados, 41 requeridos para los seis pasos y 20 originales opcionales no incluidos. Los archivos de soporte complementan la revisión documental; los originales no archivados no se presentan como descargados ni como entradas verificadas.

## Reconstruir el panel

```bash
.venv/bin/python scripts/reproducir.py
```

La secuencia verifica las entradas, reconstruye precios, relaciones y mediciones, ejecuta controles y comprueba el contrato de tablas. Los resultados tabulares quedan en `SOCHER_2026_dataset/tablas/` y el registro general en `artifacts/registro_reproduccion.json`.

Para comprobar una base ya construida:

```bash
.venv/bin/python scripts/reproducir.py --solo-verificar
```

## Generar CSV y Excel

```bash
.venv/bin/python scripts/reproducir.py --con-excel
```

La opción incorpora la exportación completa y su verificación. Genera `Dataset_articulo.csv` y `Dataset_articulo.xlsx` en `artifacts/`. Se puede cambiar esa carpeta mediante `--output-dir` o la variable `SOCHER_OUTPUT_DIR`.

La entrega original se generó y verificó con Python 3.12.14. El comando portable de exportación está preparado, pero no se ha repetido la exportación completa bajo el entorno Python 3.13 de esta prueba. Los archivos originales se conservan fuera del repositorio como entregas de referencia.

## Criterios de éxito

- Cada paso termina con código cero y el registro indica `completado: true`.
- El contrato verifica doce tablas, claves y dimensiones esperadas.
- El panel horario mantiene 178.016 identificadores únicos y 66 columnas.
- Los campos causales pendientes siguen vacíos y ninguna fila queda declarada elegible.
- La exportación, cuando se solicita, conserva valores, tipos, vacíos y diccionario frente a su fuente.

Las huellas identifican archivos exactos. Los tiempos de ejecución, rutas del nuevo equipo y metadatos de archivos regenerados pueden cambiar. Para evaluar equivalencia científica se utilizan también los controles de contenido y tolerancias documentadas.

## Qué se conserva y qué se regenera

El historial del repositorio incluye código, documentación, contratos, insumos compactos necesarios y controles de referencia. `artifacts/`, entornos y tablas regeneradas están excluidos del historial. La lectura de los controles de una entrega anterior debe distinguirse de una ejecución nueva: la evidencia de la ejecución actual está en su propio registro.

Las comprobaciones de GitHub Actions verifican la integridad de las entradas y la sintaxis del código. Su resultado no sustituye la reproducción completa ni acredita identificación causal.

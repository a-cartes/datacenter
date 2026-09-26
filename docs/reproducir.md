# Reproducir esta versión

[Inicio](../README.md) · [Datos](datos.md) · [Método](metodologia.md)

## Alcance comprobado

La reconstrucción y la exportación completa se ejecutaron satisfactoriamente en una carpeta independiente, con dependencias instaladas en un entorno virtual nuevo. Incluyó once pasos: entradas, seis pasos de construcción y comprobación, contrato de doce tablas y tres pasos de exportación. El panel resultante conserva 178.016 filas y 66 variables. La [auditoría del 25 de septiembre](auditoria.md) conserva los registros.

La prueba se realizó en el mismo equipo del trabajo original, sobre macOS ARM64. Demuestra instalación en un entorno virtual nuevo y reconstrucción desde los extractos incluidos. No equivale a una réplica independiente en otro equipo ni a una nueva descarga y extracción de todos los originales nacionales.

## Preparar el entorno

Se comprobaron Python 3.13.15, pandas 3.0.5, numpy 2.5.3, pyarrow 25.0.1 y openpyxl 3.1.5. `requirements.txt` declara las bibliotecas principales; `requirements-lock.txt` incluye las versiones transitivas observadas en la instalación nueva. Utiliza Python 3.13.15 para repetir ese entorno:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
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

La entrega original se generó con Python 3.12.14. La exportación portable se repitió y verificó con Python 3.13.15 en el entorno nuevo: el CSV conserva exactamente la huella original y el Excel mantiene valores, vacíos y estructura dentro de la tolerancia declarada. Los archivos grandes se conservan fuera del historial de código como entregas de referencia.

## Criterios de éxito

- Cada paso termina con código cero y el registro indica `completado: true`.
- El contrato verifica doce tablas, claves y dimensiones esperadas.
- El panel horario mantiene 178.016 identificadores únicos y 66 columnas.
- Los campos causales pendientes siguen vacíos y ninguna fila queda declarada elegible.
- La exportación, cuando se solicita, conserva valores, tipos, vacíos y diccionario frente a su fuente.

Las huellas identifican archivos exactos. Los tiempos de ejecución, rutas del nuevo equipo y metadatos de archivos regenerados pueden cambiar. Para evaluar equivalencia científica se utilizan también los controles de contenido y tolerancias documentadas.

## Qué se conserva y qué se regenera

El historial del repositorio incluye código, documentación, contratos, insumos compactos necesarios y controles de referencia. `artifacts/`, entornos y tablas regeneradas están excluidos del historial. La lectura de los controles de una entrega anterior debe distinguirse de una ejecución nueva: la evidencia de la ejecución actual está en su propio registro.

El flujo automático de GitHub Actions comprueba entradas, enlaces de documentación y sintaxis. El flujo manual **Reconstrucción completa** instala las versiones declaradas, reconstruye el paquete con Excel y conserva los informes durante 14 días. Está preparado para ejecutarse desde la pestaña Actions; esta preparación no acredita una ejecución remota. Ninguno de los dos flujos prueba identificación causal.

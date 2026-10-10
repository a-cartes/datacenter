# Fuentes y reconstrucción desde originales

## Dos alcances distintos

El comando público regenera la muestra, el emparejamiento y los resultados desde paneles derivados y metadatos congelados. No necesita los aproximadamente 18 GB de originales de precios ni las bases PET26. Esta es la reproducción ejecutable comprobada de la entrega.

La reconstrucción desde fuentes primarias es un alcance adicional. Se conservan los programas de adquisición y extracción en `archivo/scripts_originales/`, los documentos de validación y los manifiestos con URL, versión y huella. Algunas descargas del Coordinador requieren intervención manual, y los programas históricos contienen convenciones de directorios del trabajo original. No se afirma que una nueva descarga vaya a entregar exactamente la misma versión del proveedor.

## Orden del procesamiento completo

1. Obtener los originales mensuales seleccionados de `procedencia/manifiesto_originales_historicos.csv`; comprobar tamaño y SHA-256 y colocarlos en la estructura `fuentes/precios/originales/historico/` que indica el manifiesto.
2. Recuperar los TSV modernos con `descargar_cmg_moderno.py`, conservando versión y ETag; revisar su continuidad con los libros históricos.
3. Ejecutar extracción histórica y moderna, diccionario de barras, geografía e inventario. Las fuentes Infotécnica, INE, SEA y cartas se identifican en la documentación archivada y el catálogo de instalaciones.
4. Construir paneles barra-mes y barra-año y covariables. Comprobar coberturas y alias antes de compararlos con los archivos publicados.
5. Ejecutar el procedimiento actual de muestras y estimación. El antiguo `ejecutar_todo.sh` describe el flujo inicial; **no sustituye** el cierre SOCHER actual.

No se redistribuyen automáticamente PDFs, páginas web o modelos de terceros en este paquete nuevo. Las fuentes institucionales conservan sus derechos y condiciones de uso; las URLs y huellas permiten identificar la evidencia. `procedencia/registro_fuentes.csv` registra la adquisición prospectiva; `datos/instalaciones/fuentes_instalaciones.csv` registra el inventario. Algunos enlaces individuales pueden cambiar o requerir navegador.

## Archivos incluidos

| Carpeta | Contenido y función |
|---|---|
| `datos/panel/` | Panel barra-año, barra-mes y referencia mensual; insumos numéricos derivados |
| `datos/geo/` | Diccionarios, vigencia, alias y correspondencia espacial |
| `datos/covariables/` | Agregados censales y metadatos; no microdatos personales |
| `datos/unidades/` | Historia de exposición por distrito, comuna y radios |
| `datos/instalaciones/` | Inventario, hitos, coordenadas de instalaciones y catálogo documental |
| `datos/analitico/` | Muestras congeladas para comprobar la reconstrucción |
| `datos/precios_hist/202108.parquet` | Extracto horario de agosto 2021 para contrastar la auditoría de 96 precios |
| `prospectiva_2030/extraidos/demanda_digital/` | Previsión por clientes clasificados y proyectos; no retiros observados |
| `procedencia/manifest.json` | Tamaños y SHA-256 de los insumos y referencias incluidos |

El artículo original de Virginia se identifica por DOI, versión y hash en `procedencia/articulo_virginia.json`; su PDF no se incluye. La reproducción chilena no depende de que ese PDF esté en el escritorio del investigador.

## Revisión del paquete antes de publicar

Se incorporan carpetas seleccionadas, sin entornos locales, credenciales, archivos `.env`, cachés ni descargas masivas. Las rutas personales de los archivos históricos se sustituyen por marcadores, por lo que sus hashes públicos pueden diferir de las copias locales. Los valores numéricos de las entradas analíticas se contrastan con los archivos de origen.

No se eliminó ni reescribió el historial anterior del repositorio. El carácter público no concede por sí solo una licencia nueva sobre fuentes de terceros; véase `REUSE.md` en la raíz.

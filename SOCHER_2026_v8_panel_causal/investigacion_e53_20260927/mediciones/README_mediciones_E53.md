# Medición disponible para investigar E53: ET7 de Chacabuco

27 de septiembre de 2026. **Se recuperaron 90.532 registros de 15 minutos del socket `CHCABUCO_023_ET7_CHL`, desde enero de 2024 hasta agosto de 2026. La serie pertenece al punto ET7 compartido y no mide aisladamente a Ascenty.** No se estima causalidad con estos datos, ni se añade UTC a los precios.

## Identidad y alcance

El [catálogo público de sockets](https://medidas.coordinador.cl/SOCKET/SOCKET_HABILITADO.xlsx) preservado en v3 contiene 6.446 filas, hoja `24092026`. La fila Excel 921 identifica `CHCABUCO_023_ET7_CHL`, STM II, 23 kV, medidor `MW1509A74602_0100`, serie `MW-1509A746-02`. Sus columnas asignan **inyección activa a kWhD y retiro activo a kWhR**. Se conservan ambos canales literalmente; no se convierte el canal mayor en consumo del cliente. La captura de septiembre de 2026 no acredita vigencia histórica continua de esa configuración.

La búsqueda completa no halló Ascenty en ningún campo ni E53 entre los 18 sockets de la subestación Chacabuco. El recorrido de los 32 ZIP definitivos locales observó 19 nombres históricos de Chacabuco —incluido el cambio nominal CT4_CHL/CT4_ENT— y ninguno rotulado Ascenty o E53. Esto describe el ámbito examinado; no prueba que no exista un medidor bajo otra denominación.

La [API de elementos de Chacabuco](https://api-infotecnica.coordinador.cl/v1/subestaciones/683/elementos/) identifica el medidor 6871 como `DT7`, nodo conexión 16647. La [ficha del medidor](https://api-infotecnica.coordinador.cl/v1/medidores/6871/) no informa serie, y el [listado de documentos](https://api-infotecnica.coordinador.cl/v1/medidores/6871/documentos/) devuelve una lista vacía. La correspondencia exacta por serie entre DT7 de Infotécnica y ET7 del catálogo queda pendiente; se informa como candidato de medición de T7, sin omitir esa diferencia nominal. La ruta nominal E53→BP7→T7 acreditada en el expediente de eventos no vuelve exclusivo el total del transformador.

## Unidad, etiquetas y cobertura

Las cabeceras originales son `kWhD` y `kWhR`, dentro del CSV publicado como `Puntos_de_Medida_15MIN_CSV`. El [Documento Técnico de Medidas del CEN 2021](https://medidas.coordinador.cl/public/DOCUMENTACION/NORMATIVA/Documento%20T%C3%A9cnico%20Sistema%20de%20Medidas%20de%20Energ%C3%ADa%202021.pdf), páginas 8–9, especifica kWh para energía activa e integración de 15 min. La potencia equivalente media por intervalo se obtiene como **kWh/(0,25 h×1.000)=kWh/250 MW**. No son valores kW publicados y no se aplica otro factor PT/CT.

Hay 31 meses completos en etiquetas civiles; marzo de 2025 está totalmente ausente del original examinado. Energías y medias de ese mes permanecen nulas. Los cambios horarios generan meses con intervalos adicionales o faltantes según la zona civil, no errores ni imputaciones. Las 90.532 parejas `DATETIME`/`UTCDATETIME` coinciden con America/Santiago, con offsets −180/−240 min; no hay claves socket×UTC duplicadas. Esta comprobación no acredita si el CSV etiqueta el comienzo o el final físico del intervalo. Por eso se describe fecha de **etiqueta**, no se desplazan 15 min y la unión con precios sigue deshabilitada.

`et7_cobertura_diaria.csv` enumera todos los días del ámbito, cantidad esperada según reloj civil, registros observados, completitud y ausencia. Todos los días observados están completos. La ausencia de marzo no se interpreta como desconexión ni entrada del centro.

## Resúmenes descriptivos con ventanas de protocolo

Se usa g = 6 de mayo de 2025, excluyendo del contraste g−7 a g−1 (29 de abril–5 de mayo). Estas fechas se toman del protocolo de investigación; las medias de canales no constituyen un ATT ni una prueba del mecanismo.

| Ventana | Fechas de etiqueta | Días completos/esperados | Intervalos/esperados | Canal D medio (MW) |
|---|---|---:|---:|---:|
| Pre [−112,−8] |14 enero–28 abril 2025|74/105|7.108/10.084|16,9994|
| Post [0,89] |6 mayo–3 agosto 2025|90/90|8.640/8.640|19,4026|
| Subventana post [0,27] |6 mayo–2 junio 2025|28/28|2.688/2.688|17,1908|

El pre no tiene soporte completo por marzo. La diferencia entre medias usa períodos con composición estacional distinta y no separa los alimentadores de T7, cambios de suministro ni otras cargas. No se atribuye a Ascenty ni se presenta con significación estadística. El canal R suma 0 kWh en el pre y 0,0065248 kWh en el post de 90 días; se mantiene, sin redondearlo a inexistencia.

El resumen exploratorio de 30 fechas anterior/posterior al 5 de mayo, ya inspeccionado, se conserva y se rotula `exploratorio_posterior_a_inspeccion`: D = 16,1724 → 17,4098 MW. **No se presenta como ventana prerregistrada.** La tabla completa también muestra que mayo de 2024 tenía 18,8906 MW y mayo de 2025 16,8838 MW en canal D. Esto impide leer el aumento breve como demostración suficiente de entrada de demanda nueva.

## Reproducción y archivos

`scripts/extraer_et7.py` lee los 32 originales nacionales ya auditados y extrae únicamente ET7 con archivo, miembro ZIP y fila CSV exacta. Los manifiestos reutilizan explícitamente los hashes de originales de v7, cotejan tamaño, bytes y filas recorridas, validan CRC al leer y calculan hashes nuevos para extractos. No se repite la adquisición, no se modifican originales y no se descargan datos nacionales. Dos consultas pequeñas adicionales a Infotécnica están preservadas y documentadas en `fuentes/manifest_fuentes.json`.

- `et7_15min.csv.gz`: campos originales y conversiones separados, 90.532 filas.
- `et7_cobertura_mensual.csv`, `et7_cobertura_diaria.csv`, `et7_descriptivo_diario.csv` y `et7_ventanas_descriptivas.csv`: soporte y descriptivos.
- `catalogo_chacabuco.csv`, `control_catalogo.json` y `sockets_chacabuco_observados_por_mes.csv`: búsqueda reproducible de identidad.
- `diccionario_et7.csv`, `verificacion_et7.json`, `extractos/*_manifest.json`: procedencia, controles y límites.
- `et7_diario.png` y `et7_diario.svg`: canal D diario, con marzo de 2025 sin interpolar y fecha de energización señalada.

Desde la raíz del proyecto: `.venv/bin/python SOCHER_2026_v8_panel_causal/investigacion_e53_20260927/mediciones/scripts/extraer_et7.py`, seguido de `scripts/documentar_fuentes.py` en la misma carpeta. El segundo script documenta fuentes preservadas y solo vuelve a consultar los dos endpoints si se agrega `--actualizar-api`. Dependencias: pandas, openpyxl, matplotlib; bibliotecas estándar para ZIP, CSV y HTTP. El primer procesamiento usó el Python incluido de Codex para la extracción; la figura usa el entorno existente del proyecto porque matplotlib no estaba en el entorno incluido.

La copia del repositorio no contiene los ZIP nacionales voluminosos. Con `--solo-consolidar` se reconstruyen las tablas y figura desde los 32 extractos comprimidos y manifiestos incluidos, sin originales ni red. Para volver a extraer, `--datos-raiz /ruta/al/proyecto-original` indica la raíz externa que conserva los ZIP y v3/v7. Las rutas de salida se resuelven desde el archivo del script y funcionan al copiar la carpeta bajo el repositorio.

La reproducción desde extractos conservó exactamente el SHA-256 del CSV principal de la primera ejecución. `scripts/verificar_productos.py` coteja por separado los campos literales de los 32 extractos con el CSV final, concilia agregados diarios y mensuales y comprueba que los 31 días de ausencia mantienen energía y media nulas. El resultado ejecutado está en `verificacion_tabular.json`: 90.532 filas, 943 días completos y 31 días ausentes, sin discrepancias de campos ni totales dentro de la tolerancia de 0,0001 kWh.

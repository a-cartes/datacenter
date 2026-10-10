#!/bin/zsh
# Flujo reproducible de la réplica (desde la carpeta Replica_RM_desde_cero).
# Etapa A (adquisición; requiere red, no se repite por defecto):
#   python scripts/registrar_originales_historicos.py      # enlaza y verifica libros 2017-2024
#   python scripts/descargar_cmg_moderno.py verificar|descargar ...  # TSV desde 15/07/2024
#   python scripts/descargar_infotecnica.py ; python scripts/consultar_sea.py ; python scripts/fichas_sea.py
#   python scripts/consultar_cartas_coordinador.py ; python scripts/descargar_censo2017_ine.py
#   python scripts/candidatos_directorios.py ; python scripts/archivar_web.py URL ...
# Etapa B (procesamiento y estimación, sin red salvo caché de geocodificación):
set -e
PY=.venv/bin/python
$PY scripts/inspeccionar_muestras.py
$PY -W ignore scripts/piloto_conciliacion.py > logs/piloto.log
$PY -W ignore scripts/extraer_precios_historicos.py > logs/extraer_precios_historicos_final.log
$PY scripts/extraer_precios_modernos.py > logs/extraer_precios_modernos.log
$PY -W ignore scripts/diccionario_barras.py > logs/diccionario.log
$PY scripts/geolocalizar.py > logs/geolocalizar.log
$PY scripts/hitos_instalaciones.py
$PY scripts/registro_fuentes_instalaciones.py > logs/fuentes.log
(cd scripts && ../$PY construir_panel_barras.py > ../logs/panel.log)
(cd scripts && ../$PY continuidad_precios.py > ../logs/continuidad.log)
(cd scripts && ../$PY diagnostico_unidades.py > ../logs/diagnostico.log)
$PY scripts/covariables_censo.py > logs/covariables.log
$PY -W ignore scripts/preparar_muestra.py > logs/muestras.log
for a in "distrito G_doc" "distrito G_min" "distrito_nobal G_doc" "distrito_ctrl_lejos5km G_doc" \
         "distrito_ctrl_corr_menor05 G_doc" "comuna G_doc" "comuna G_min" "nodo_r2km G_doc" "nodo_r3km G_doc"; do
  Rscript scripts/estimar.R ${=a} > "logs/estimar_${a// /_}.log" 2>&1
done
$PY scripts/resumir_estimaciones.py

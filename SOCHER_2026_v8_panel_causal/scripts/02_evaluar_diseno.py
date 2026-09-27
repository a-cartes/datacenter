#!/usr/bin/env python3
"""Matriz de comparadores y puerta documental. No infiere no tratamiento por ausencia.

No calcula ATT cuando faltan tratamientos/comparadores. No es un estimador:
deja un diagnóstico reproducible de por qué la especificación aún no se ejecuta.
"""
from pathlib import Path
import argparse
import hashlib
import json
import pandas as pd


def sha(path):
    return hashlib.file_digest(path.open('rb'), 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    root = args.root.resolve()
    stage = root / 'SOCHER_2026_v8_panel_causal'
    out = stage / 'resultados'
    out.mkdir(parents=True, exist_ok=True)
    evpath = stage / 'eventos/matriz_eventos_elegibilidad.csv'
    relpath = root / 'SOCHER_2026_v6_multicentros/mapeo/relacion_centros_barras.csv'
    covpath = root / 'SOCHER_2026_v7_2020_2026/entrega/Cobertura_por_mes_barra.csv'
    configpath = stage / 'documentos/protocolo_config.json'
    events = pd.read_csv(evpath, dtype=str).fillna('')
    relations = pd.read_csv(relpath, dtype=str).fillna('')
    coverage = pd.read_csv(covpath)
    rows = []
    for bar, data in coverage.groupby('barra_cmg', sort=True):
        links = relations.loc[relations.barra_cmg.eq(bar)]
        current = events.loc[events.barra_cmg.eq(bar)]
        linked = sorted(set(links.centro_id) | set(current.centro_id))
        isref = bar in ['QUILLOTA______110', 'QUILLOTA______220']
        reason = ('Referencia descriptiva: exposición y ausencia de tratamiento sin certificar'
                  if isref else 'Vínculo candidato con centro: historia y exposición sin cerrar'
                  if linked else 'Sin vínculo en el registro consultado: ausencia de tratamiento y exposición desconocidas')
        rows.append({
            'barra_cmg': bar,
            'fecha_precio_desde': str(data.fecha_desde.min()),
            'fecha_precio_hasta': str(data.fecha_hasta.max()),
            'n_meses_observados': int(data.mes.nunique()),
            'n_filas_horarias': int(data.filas.sum()),
            'centros_candidatos': ';'.join(linked),
            'referencia_descriptiva': 'SI' if isref else 'NO',
            'historia_no_tratamiento_verificada': 'DESCONOCIDA',
            'exposicion_electrica': 'DESCONOCIDA',
            'elegible_control_causal': 'NO',
            'motivo': reason,
            'fuente_historia': 'relacion_centros_barras_v6;matriz_eventos_v8',
            'fuente_cobertura': 'v0.2.0/Cobertura_por_mes_barra.csv',
        })
    controls = pd.DataFrame(rows)
    assert controls.barra_cmg.is_unique
    assert controls.n_filas_horarias.sum() == 3411527
    controls.to_csv(out / 'matriz_controles_revision.csv', index=False)
    closed = events.elegible_evento_causal.eq('SI')
    n_controls = int(controls.elegible_control_causal.eq('SI').sum())
    status = {
        'estado': 'NO_ESTIMABLE_CON_EXPEDIENTES_ACTUALES',
        'eventos_en_registro': len(events),
        'eventos_habilitados': int(closed.sum()),
        'campus_habilitados': int(events.loc[closed, 'campus_grupo_id'].nunique()),
        'barras_tratadas_habilitadas': int(events.loc[closed & events.barra_cmg.ne(''), 'barra_cmg'].nunique()),
        'comparadores_habilitados': n_controls,
        'att': None,
        'error_estandar': None,
        'event_study_causal': None,
        'spillovers_causales': None,
        'motivos': [],
        'protocolo_sha256': sha(configpath),
        'entradas': {str(p.relative_to(root)): sha(p) for p in [evpath, relpath, covpath]},
        'nota': 'No disponible no es cero. Los conteos son de expedientes, no pruebas de identificación.'
    }
    if not closed.any():
        status['motivos'].append('Ningún evento tiene cerrada su elegibilidad documental y causal.')
    if n_controls == 0:
        status['motivos'].append('No hay comparadores con historia de tratamiento y exposición eléctrica verificadas.')
    if closed.any() or n_controls:
        # La habilitación posterior exige revisar el diseño completo, no activar silenciosamente un modelo.
        status['motivos'].append('Hay nuevas habilitaciones: revisar soporte, vigencia, reloj e inferencia antes de implementar la estimación registrada.')
    (out / 'estado_estimacion.json').write_text(json.dumps(status, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in status.items() if k not in ['entradas', 'protocolo_sha256']}, ensure_ascii=False))


if __name__ == '__main__':
    main()

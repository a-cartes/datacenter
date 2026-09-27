#!/usr/bin/env python3
"""Descripción E53 según adenda guardada antes del cálculo; no estima causalidad."""
from pathlib import Path
import argparse
import hashlib
import json
import os
os.environ.setdefault('MPLCONFIGDIR', '/private/tmp/socher_e53_mpl')
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def sha(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--stage', type=Path, default=Path(__file__).resolve().parents[2])
    p.add_argument('--output', type=Path)
    a = p.parse_args()
    stage = a.stage.resolve()
    here = Path(__file__).resolve().parent
    out = a.output or here / 'resultados'
    out.mkdir(parents=True, exist_ok=True)
    cfgpath = here / 'adenda_01.json'
    cfg = json.loads(cfgpath.read_text())
    panel = stage / 'panel/panel_diario.csv'
    if not panel.exists():
        panel = panel.with_suffix('.csv.gz')
    # The hash checks the uncompressed frozen daily table, including in repository copies.
    import gzip
    with (gzip.open(panel, 'rb') if panel.suffix == '.gz' else panel.open('rb')) as f:
        panel_hash = hashlib.file_digest(f, 'sha256').hexdigest()
    assert panel_hash == cfg['panel_sha256']
    d = pd.read_csv(panel, parse_dates=['fecha'], dtype={'codigo_documentado': str}, low_memory=False)
    g = pd.Timestamp(cfg['g'])
    dates = pd.date_range(g + pd.Timedelta(days=-112), g + pd.Timedelta(days=89))
    q = d.loc[d.familia_reloj.eq('M') & d.fecha.isin(dates)]
    assert not q.duplicated(['barra_cmg', 'fecha']).any()
    c = q.loc[q.barra_cmg.eq(cfg['barra'])].set_index('fecha').reindex(dates)
    assert c.codigo_documentado.eq(cfg['id_info']).all()
    c.index.name = 'fecha'
    c['t'] = (c.index - g).days
    c['valido_24_comun'] = c.n_horas_observadas.eq(24) & c.n_pares_q110.eq(24) & c.n_pares_q220.eq(24)
    for ref, name in [('QUILLOTA______110', 'q110'), ('QUILLOTA______220', 'q220')]:
        r = q.loc[q.barra_cmg.eq(ref)].set_index('fecha').reindex(dates)
        c['precio_' + name] = r.precio_mean_usd_mwh
        c['firma_' + name] = r.firma_etiquetas
        c['valido_24_comun'] &= r.n_horas_observadas.eq(24) & c.firma_etiquetas.eq(r.firma_etiquetas)
        valid = c.valido_24_comun
        np.testing.assert_allclose(c.loc[valid, 'precio_mean_usd_mwh'] - c.loc[valid, 'precio_' + name], c.loc[valid, 'dif_' + name + '_mean_usd_mwh'], atol=1e-10, rtol=0)
    c['periodo_principal'] = np.select([c.t.between(-112, -8), c.t.between(0, 89)], ['pre', 'post'], default='anticipacion')
    c['motivo_fuera_principal'] = np.select([~c.valido_24_comun, c.periodo_principal.eq('anticipacion')], ['no_24_etiquetas_comunes', 'anticipacion_registrada'], default='')
    c['apagón_25_26feb'] = c.index.isin(pd.to_datetime(['2025-02-25', '2025-02-26']))
    c.to_csv(out / 'episodio_diario_completo.csv', float_format='%.12g')
    scenarios = [{'id': 'principal', 'pre': cfg['pre'], 'post': cfg['post'], 'excluir_fechas': []}] + cfg['sensibilidades']
    rows, contrasts = [], []
    for scenario in scenarios:
        good = c.valido_24_comun & ~c.index.isin(pd.to_datetime(scenario['excluir_fechas']))
        for variable in cfg['series']:
            values = {}
            for period in ['pre', 'post']:
                lo, hi = scenario[period]
                v = c.loc[good & c.t.between(lo, hi), variable]
                assert v.notna().all()
                values[period] = v
                rows.append({'escenario': scenario['id'], 'serie': variable, 'periodo': period,
                             'desde': (g + pd.Timedelta(days=lo)).date().isoformat(), 'hasta': (g + pd.Timedelta(days=hi)).date().isoformat(),
                             'n_dias': len(v), 'media_usd_mwh': v.mean(), 'mediana_usd_mwh': v.median(),
                             'p10_usd_mwh': v.quantile(.1), 'p90_usd_mwh': v.quantile(.9), 'std_usd_mwh': v.std()})
            contrasts.append({'escenario': scenario['id'], 'serie': variable,
                              'n_pre': len(values['pre']), 'n_post': len(values['post']),
                              'media_pre_usd_mwh': values['pre'].mean(), 'media_post_usd_mwh': values['post'].mean(),
                              'cambio_descriptivo_usd_mwh': values['post'].mean() - values['pre'].mean(),
                              'es_estimacion_causal': False})
    pd.DataFrame(rows).to_csv(out / 'resumen_periodos.csv', index=False, float_format='%.12g')
    contrast = pd.DataFrame(contrasts)
    contrast.to_csv(out / 'contrastes_descriptivos.csv', index=False, float_format='%.12g')
    # Each weekly block is fixed to the documentary date, never selected from prices.
    v = c.loc[c.valido_24_comun & c.periodo_principal.ne('anticipacion')].copy()
    v['semana_relativa'] = v.t // 7
    weekly = v.groupby('semana_relativa').agg(n_dias=('t', 'size'), t_min=('t', 'min'), t_max=('t', 'max'), **{s: (s, 'mean') for s in cfg['series']}).reset_index()
    weekly['fecha_centro'] = g + pd.to_timedelta(weekly.semana_relativa * 7 + 3, unit='D')
    weekly.to_csv(out / 'trayectoria_semanal.csv', index=False, float_format='%.12g')
    c.loc[c.t.eq(-8), cfg['series'] + ['valido_24_comun']].to_csv(out / 'valor_dia_base.csv', float_format='%.12g')
    excluded = c.loc[~c.valido_24_comun, ['t', 'n_horas_observadas', 'n_pares_q110', 'n_pares_q220', 'etiquetas_observadas', 'motivo_fuera_principal']]
    excluded.to_csv(out / 'dias_sin_soporte24.csv')
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False})
    fig, axes = plt.subplots(2, 1, figsize=(11.5, 8), sharex=True)
    series = [[('precio_mean_usd_mwh', 'Chacabuco 110', '#174A6E'), ('precio_q110', 'Quillota 110', '#D0893E')],
              [('dif_q110_mean_usd_mwh', 'Respecto de Quillota 110', '#174A6E'), ('dif_q220_mean_usd_mwh', 'Respecto de Quillota 220', '#AD594D')]]
    for ax, lines in zip(axes, series):
        for variable, label, color in lines:
            display = c[variable].where(c.valido_24_comun & c.periodo_principal.ne('anticipacion'))
            ax.plot(c.index, display, lw=.6, alpha=.26, color=color)
            for mask in [weekly.semana_relativa.lt(-1), weekly.semana_relativa.ge(0)]:
                w = weekly.loc[mask]
                ax.plot(w.fecha_centro, w[variable], lw=2, color=color, label=label if mask is not None and w.semana_relativa.min() < 0 else None)
        ax.axvspan(g - pd.Timedelta(days=7), g - pd.Timedelta(hours=12), color='#CCCCCC', alpha=.2)
        ax.axvline(g, color='#555555', ls='--', lw=1)
        ax.axhline(0, color='#555555', lw=.7)
        ax.set_ylabel('USD/MWh')
        ax.grid(axis='y', alpha=.15)
        ax.legend(frameon=False, loc='upper left')
    axes[0].set_title('Conexión E53: precios antes y después de mayo de 2025', loc='left', fontweight='bold', fontsize=14)
    axes[1].set_title('Diferenciales diarios y medias por semana', loc='left', fontsize=11)
    axes[0].annotate('6 de mayo\nPrimer día completo siguiente', xy=(g, .98), xycoords=('data', 'axes fraction'), xytext=(8, -5), textcoords='offset points', va='top', fontsize=9)
    axes[1].xaxis.set_major_locator(mdates.MonthLocator())
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
    fig.text(.09, .025, 'Líneas finas: días con 24 etiquetas comunes; gruesas: medias por bloques fijos de siete días.\nFranja gris: anticipación excluida. El último bloque contiene seis días. Comparación descriptiva, sin atribución causal.', fontsize=9, color='#444444')
    fig.tight_layout(rect=[0, .085, 1, 1])
    fig.savefig(out / 'episodio_e53_precios.png', dpi=180)
    fig.savefig(out / 'episodio_e53_precios.pdf')
    plt.close(fig)
    main = contrast.loc[contrast.escenario.eq('principal')]
    assert main.n_pre.eq(104).all() and main.n_post.eq(90).all()
    # Internal arithmetic decomposition is necessary: Δspread = Δnode − Δreference.
    changes = main.set_index('serie').cambio_descriptivo_usd_mwh
    for ref in ['q110', 'q220']:
        assert abs(changes['dif_' + ref + '_mean_usd_mwh'] - (changes.precio_mean_usd_mwh - changes['precio_' + ref])) < 1e-10
    meta = {'estado': 'OK', 'adenda_sha256': sha(cfgpath), 'panel_diario_sha256': panel_hash,
            'script_sha256': sha(Path(__file__)), 'dias_calendario': len(c), 'dias_pre24': 104, 'dias_post24': 90,
            'dias_no24': [d.date().isoformat() for d in excluded.index],
            'codigo_documentado_unico': sorted(c.codigo_documentado.unique().tolist()),
            'duplicados_fecha': int(c.index.duplicated().sum()), 'escenarios_reportados': len(scenarios), 'contrastes_reportados': len(contrast),
            'estimaciones_causales': 0, 'p_valores': 0, 'muestra_identica_entre_series': True,
            'salidas_tabulares_sha256': {f.name: sha(f) for f in sorted(out.glob('*.csv'))}}
    (out / 'validacion.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n')
    print(main.to_string(index=False))
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

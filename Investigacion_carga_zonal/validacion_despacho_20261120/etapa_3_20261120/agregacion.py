"""Pérdida de precisión al valorar dos barras distintas con una sola serie de precios."""
import argparse
import pandas as pd

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mensual')
    p.add_argument('salida')
    args=p.parse_args()
    m=pd.read_csv(args.mensual)
    cols=['horas_fisicas','compras_50MW_BP1_USD','compras_50MW_BP2_USD']
    a=m.groupby(m.mes//100)[cols].sum()
    a.index.name='anio'
    d1=a.compras_50MW_BP1_USD
    d2=a.compras_50MW_BP2_USD
    a['error_minimax_50MW_USD']=(d1-d2).abs()/2
    a['peso_BP1_indiferencia']=-d2/(d1-d2)
    assert ((d1*d2)<0).all() and a.peso_BP1_indiferencia.between(0,1).all()
    a.to_csv(args.salida,float_format='%.8f')

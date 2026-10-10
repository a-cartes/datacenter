"""Funciones compartidas de identificación de barras."""
from functools import lru_cache
from pathlib import Path
import re

import pandas as pd

ALIAS = Path(__file__).resolve().parents[1] / "datos" / "geo" / "alias_codigos.csv"


def canon_base(code):
    """Unifica la variante 'Ñ'->'N' (desde junio de 2023 el Coordinador publica con 'N' los
    20 códigos que antes llevaban 'Ñ'; p. ej. PIÑATAS_______066 hasta 2023-05)."""
    return code.replace("Ñ", "N") if isinstance(code, str) else code


@lru_cache(maxsize=1)
def _alias():
    if ALIAS.exists():
        a = pd.read_csv(ALIAS)
        return dict(zip(a.codigo_antiguo, a.codigo_canonico))
    return {}


def canon(code):
    """Código canónico: variante Ñ/N y alias por cambio de relleno con guiones bajos
    (mismo texto y tensión, sin meses superpuestos; ver diccionario_barras.py)."""
    c = canon_base(code)
    return _alias().get(c, c)


def colapsar(code):
    return re.sub(r"_+", "_", code) if isinstance(code, str) else code

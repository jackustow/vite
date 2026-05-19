"""Inferencia del TPDOC según longitud del NMDOC."""


def inferir_tpdoc(nmdoc: str | None) -> str | None:
    """
    Infiere el tipo de documento según longitud numérica del NMDOC.

    - len < 9 dígitos → TPDOC = '13' (persona natural / cédula)
    - len = 9 dígitos → TPDOC = '31' (persona jurídica / NIT)
    - len > 9 dígitos → TPDOC = '13'

    Args:
        nmdoc: número de identificación (puede ser str o None)
    Returns:
        str '13' o '31', o None si nmdoc está vacío
    """
    if not nmdoc:
        return None
    solo_digitos = "".join(c for c in str(nmdoc) if c.isdigit())
    longitud = len(solo_digitos)
    if longitud == 0:
        return None
    return '31' if longitud == 9 else '13'


def aplicar_tpdoc(tercero: dict) -> dict | None:
    """
    Calcula el TPDOC correcto y retorna el cambio si difiere del actual.

    Args:
        tercero: dict con claves 'tpdoc', 'nmdoc'
    Returns:
        dict {'tpdoc': nuevo_valor} si cambió, None si no hubo cambio
    """
    nuevo = inferir_tpdoc(tercero.get('nmdoc'))
    if nuevo is None:
        return None
    actual = str(tercero.get('tpdoc')) if tercero.get('tpdoc') is not None else None
    if actual == nuevo:
        return None
    return {'tpdoc': nuevo}

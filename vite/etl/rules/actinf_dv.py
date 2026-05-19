"""Cálculo del Dígito de Verificación (DV) para NITs colombianos — algoritmo DIAN."""


def calcular_dv_colombia(nit) -> int:
    """
    Calcula el dígito de verificación para un NIT colombiano.
    Algoritmo oficial DIAN (Módulo 11).

    Args:
        nit: int o str con el número de identificación
    Returns:
        int con el dígito de verificación (0-9)
    Raises:
        ValueError: si nit no contiene números válidos
    """
    nit_limpio = "".join(c for c in str(nit) if c.isdigit())
    if not nit_limpio:
        raise ValueError(f"El NIT '{nit}' no contiene números válidos.")

    coeficientes = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    sumatoria = 0
    for i, digito in enumerate(reversed(nit_limpio)):
        if i >= len(coeficientes):
            break
        sumatoria += int(digito) * coeficientes[i]

    residuo = sumatoria % 11
    return 11 - residuo if residuo > 1 else residuo


def aplicar_dv(tercero: dict) -> dict | None:
    """
    Calcula y actualiza el DV si TPDOC=31 y el valor calculado difiere del actual.

    Args:
        tercero: dict con claves 'tpdoc', 'nmdoc', 'dv' (todas en minúscula)
    Returns:
        dict {'dv': nuevo_valor} si cambió, None si no hubo cambio
    """
    if tercero.get('tpdoc') != '31':
        return None
    nmdoc = tercero.get('nmdoc')
    if not nmdoc:
        return None
    try:
        dv_calculado = str(calcular_dv_colombia(nmdoc))
    except ValueError:
        return None
    dv_actual = tercero.get('dv')
    if dv_actual is not None and str(dv_actual) == dv_calculado:
        return None
    return {'dv': dv_calculado}

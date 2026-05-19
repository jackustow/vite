"""Redistribución de campos de nombres, apellidos y razón social según TPDOC."""


def redistribuir_nombres(tercero: dict) -> dict:
    """
    Corrige la distribución de nombres/apellidos/razón social según tipo de documento.

    Reglas:
    - TPDOC=13 (persona natural): AP1 y NM1 son obligatorios, RZ debe ser None.
      Si RZ tiene valor: dividir por espacios y distribuir:
        word[0]→ap1, word[1]→nm1, word[2]→ap2, word[3+]→nm2, RZ=None.
    - TPDOC=31 (persona jurídica): RZ es obligatorio, AP1/AP2/NM1/NM2 deben ser None.
      Si AP1/AP2/NM1/NM2 tienen algún valor: concatenar (no nulos) en RZ,
      luego AP1=AP2=NM1=NM2=None.

    Args:
        tercero: dict con claves tpdoc, ap1, ap2, nm1, nm2, rz (minúscula)
    Returns:
        dict con los campos que cambiaron (vacío si no hubo cambios)
    """
    cambios: dict = {}
    tpdoc = str(tercero.get('tpdoc') or '').strip()

    if tpdoc == '13':
        rz = tercero.get('rz')
        if rz and str(rz).strip():
            palabras = str(rz).split()
            if palabras:
                cambios['ap1'] = palabras[0] if len(palabras) >= 1 else None
                cambios['nm1'] = palabras[1] if len(palabras) >= 2 else None
                cambios['ap2'] = palabras[2] if len(palabras) >= 3 else None
                if len(palabras) >= 4:
                    cambios['nm2'] = " ".join(palabras[3:])
                else:
                    cambios['nm2'] = None
                cambios['rz'] = None

    elif tpdoc == '31':
        partes = [
            str(tercero[f]).strip()
            for f in ('ap1', 'ap2', 'nm1', 'nm2')
            if tercero.get(f) and str(tercero[f]).strip()
        ]
        if partes:
            cambios['rz'] = " ".join(partes)
            cambios['ap1'] = None
            cambios['ap2'] = None
            cambios['nm1'] = None
            cambios['nm2'] = None

    return cambios

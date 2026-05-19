"""Inferencia del TPDOC según reglas de negocio y NMDOC."""


def inferir_tpdoc(
    nmdoc: str | None,
    pais: str | None = None,
    rz: str | None = None,
) -> str | None:
    """
    Infiere el tipo de documento según reglas de negocio.

    Orden de aplicación:
    1) Si NMDOC tiene más de 8 dígitos y está compuesto solo por '2' → '43'
    2) Si NMDOC tiene 9 dígitos e inicia por '444' → '43'
    3) Si PAIS está informado y es distinto de '169', y RZ está informado → '42'
    4) Regla base por longitud:
       - len = 9 dígitos → '31'
       - cualquier otra longitud numérica válida → '13'

    Args:
        nmdoc: número de identificación (puede ser str o None)
        pais: código de país (puede ser str o None)
        rz: razón social (puede ser str o None)
    Returns:
        str con TPDOC inferido, o None si nmdoc no tiene dígitos
    """
    if not nmdoc:
        return None
    solo_digitos = "".join(c for c in str(nmdoc) if c.isdigit())
    longitud = len(solo_digitos)
    if longitud == 0:
        return None

    # Regla 1
    if longitud > 8 and set(solo_digitos) == {"2"}:
        return "43"

    # Regla 2
    if longitud == 9 and solo_digitos.startswith("444"):
        return "43"

    # Regla 3
    pais_limpio = str(pais).strip() if pais is not None else ""
    rz_limpio = str(rz).strip() if rz is not None else ""
    if pais_limpio and pais_limpio != "169" and rz_limpio:
        return "42"

    # Regla base
    return "31" if longitud == 9 else "13"


def aplicar_tpdoc(tercero: dict) -> dict | None:
    """
    Calcula el TPDOC correcto y retorna el cambio si difiere del actual.

    Args:
        tercero: dict con claves 'tpdoc', 'nmdoc'
    Returns:
        dict {'tpdoc': nuevo_valor} si cambió, None si no hubo cambio
    """
    nuevo = inferir_tpdoc(
        nmdoc=tercero.get("nmdoc"),
        pais=tercero.get("pais"),
        rz=tercero.get("rz"),
    )
    if nuevo is None:
        return None
    actual = str(tercero.get('tpdoc')) if tercero.get('tpdoc') is not None else None
    if actual == nuevo:
        return None
    return {'tpdoc': nuevo}

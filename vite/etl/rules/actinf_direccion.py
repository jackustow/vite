"""Normalización de direcciones según nomenclaturas colombianas DIAN."""

import re


def _construir_patron(nomenclaturas: dict) -> list[tuple[str, str]]:
    """
    Expande el dict de nomenclaturas en pares (palabra_clave, codigo).
    Ordenados de más largo a más corto para evitar coincidencias parciales.

    Args:
        nomenclaturas: dict {nomenclatura_id: [palabras_clave]}
    Returns:
        lista de tuplas (palabra_clave_uppercase, codigo) ordenada desc por longitud
    """
    pares: list[tuple[str, str]] = []
    for codigo, palabras_clave in nomenclaturas.items():
        for palabra in palabras_clave:
            palabra = palabra.strip()
            if palabra:
                pares.append((palabra, codigo))
    # Ordenar de más larga a más corta para que "Avenida Calle" se reemplace antes que "Avenida"
    pares.sort(key=lambda x: len(x[0]), reverse=True)
    return pares


def normalizar_direccion(
    direccion: str | None,
    nomenclaturas: dict,
) -> tuple[str | None, bool]:
    """
    Normaliza una dirección colombiana según nomenclaturas DIAN.

    Pasos:
    1. Uppercase
    2. Reemplazar palabras completas que coincidan con palabras clave de nomenclaturas
    3. Eliminar caracteres especiales (solo letras, dígitos y espacios)
    4. Colapsar espacios y strip
    5. Verificar longitud mínima de 8 caracteres

    Args:
        direccion: dirección original
        nomenclaturas: dict {nomenclatura_id: [palabras_clave]}
    Returns:
        tuple (direccion_procesada, fue_normalizada_completamente)
        - Si len >= 8: retorna (dirección normalizada, True)
        - Si len < 8 tras normalización: retorna (direccion uppercase sin normalizar, False)
        - Si dirección es None/vacía: retorna (None, False)
    """
    if not direccion or not str(direccion).strip():
        return None, False

    texto = str(direccion).strip().upper()

    # Reemplazar palabras completas según nomenclaturas
    pares = _construir_patron(nomenclaturas)
    for palabra, codigo in pares:
        # Límite de palabra: no precedido ni seguido por letra, dígito o Ñ/acento
        patron = r'(?<![A-ZÁÉÍÓÚÑ0-9])' + re.escape(palabra.upper()) + r'(?![A-ZÁÉÍÓÚÑ0-9])'
        texto = re.sub(patron, codigo, texto, flags=re.IGNORECASE)

    # Eliminar caracteres que no sean letras (incluyendo acentuadas/Ñ), dígitos o espacios
    texto = re.sub(r'[^A-ZÁÉÍÓÚÑ0-9 ]', ' ', texto)

    # Colapsar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto).strip()

    if len(texto) < 8:
        # No se puede normalizar correctamente — retornar solo uppercase original limpio
        texto_fallback = re.sub(r'[^A-ZÁÉÍÓÚÑ0-9 ]', ' ', str(direccion).upper())
        texto_fallback = re.sub(r'\s+', ' ', texto_fallback).strip()
        return texto_fallback, False

    return texto, True

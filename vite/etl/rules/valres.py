"""Validaciones restrictivas para terceros en medios magnéticos DIAN Colombia."""

from dataclasses import dataclass

# Constantes del dominio
TPDOC_NATURAL = '13'
TPDOC_JURIDICA = '31'
PAIS_COLOMBIA = '169'


@dataclass
class ValidationError:
    codigo: str
    descripcion: str


def _vacio(valor) -> bool:
    """Retorna True si el valor es None o una cadena en blanco."""
    return valor is None or str(valor).strip() == ''


# ---------------------------------------------------------------------------
# Validaciones individuales
# ---------------------------------------------------------------------------

def validar_globales(tercero: dict) -> list[ValidationError]:
    """
    Validaciones globales que aplican a todos los terceros:
    - TPDOC y NMDOC no pueden ser None/vacíos.
    - Si TPDOC='13': AP1 y NM1 son obligatorios, RZ debe ser None.
    - Si TPDOC='31': RZ es obligatorio, AP1/AP2/NM1/NM2 deben ser None.

    Args:
        tercero: dict con campos del tercero en minúscula
    Returns:
        lista de ValidationError (vacía si no hay errores)
    """
    errores: list[ValidationError] = []

    tpdoc = tercero.get('tpdoc')
    nmdoc = tercero.get('nmdoc')

    if _vacio(tpdoc):
        errores.append(ValidationError(
            codigo='VAL_GLOBAL_01',
            descripcion='El campo TPDOC es obligatorio y no puede estar vacío.',
        ))
    if _vacio(nmdoc):
        errores.append(ValidationError(
            codigo='VAL_GLOBAL_02',
            descripcion='El campo NMDOC es obligatorio y no puede estar vacío.',
        ))

    tpdoc_str = str(tpdoc).strip() if not _vacio(tpdoc) else ''

    if tpdoc_str == TPDOC_NATURAL:
        if _vacio(tercero.get('ap1')):
            errores.append(ValidationError(
                codigo='VAL_GLOBAL_03',
                descripcion='Para persona natural (TPDOC=13) el campo AP1 es obligatorio.',
            ))
        if _vacio(tercero.get('nm1')):
            errores.append(ValidationError(
                codigo='VAL_GLOBAL_04',
                descripcion='Para persona natural (TPDOC=13) el campo NM1 es obligatorio.',
            ))
        if not _vacio(tercero.get('rz')):
            errores.append(ValidationError(
                codigo='VAL_GLOBAL_05',
                descripcion='Para persona natural (TPDOC=13) el campo RZ debe estar vacío.',
            ))

    elif tpdoc_str == TPDOC_JURIDICA:
        if _vacio(tercero.get('rz')):
            errores.append(ValidationError(
                codigo='VAL_GLOBAL_06',
                descripcion='Para persona jurídica (TPDOC=31) el campo RZ es obligatorio.',
            ))
        for campo in ('ap1', 'ap2', 'nm1', 'nm2'):
            if not _vacio(tercero.get(campo)):
                errores.append(ValidationError(
                    codigo='VAL_GLOBAL_07',
                    descripcion=(
                        f'Para persona jurídica (TPDOC=31) el campo '
                        f'{campo.upper()} debe estar vacío.'
                    ),
                ))

    return errores


def validar_tpdoc_01(tercero: dict) -> list[ValidationError]:
    """
    TPDOC debe ser '13' o '31'.

    Args:
        tercero: dict con campo 'tpdoc'
    Returns:
        lista de ValidationError
    """
    tpdoc = tercero.get('tpdoc')
    if str(tpdoc).strip() not in (TPDOC_NATURAL, TPDOC_JURIDICA):
        return [ValidationError(
            codigo='VAL_TPDOC_01',
            descripcion=(
                f"El TPDOC '{tpdoc}' no es válido. "
                f"Valores permitidos: '{TPDOC_NATURAL}' (natural) o '{TPDOC_JURIDICA}' (jurídica)."
            ),
        )]
    return []


def validar_tpdoc_02(tercero: dict) -> list[ValidationError]:
    """
    Si TPDOC='13': AP1 y NM1 son obligatorios, RZ debe ser None/vacío.

    Args:
        tercero: dict con campos tpdoc, ap1, nm1, rz
    Returns:
        lista de ValidationError
    """
    errores: list[ValidationError] = []
    if str(tercero.get('tpdoc')).strip() != TPDOC_NATURAL:
        return errores
    if _vacio(tercero.get('ap1')):
        errores.append(ValidationError(
            codigo='VAL_TPDOC_02',
            descripcion='TPDOC=13: el campo AP1 (primer apellido) es obligatorio.',
        ))
    if _vacio(tercero.get('nm1')):
        errores.append(ValidationError(
            codigo='VAL_TPDOC_02',
            descripcion='TPDOC=13: el campo NM1 (primer nombre) es obligatorio.',
        ))
    if not _vacio(tercero.get('rz')):
        errores.append(ValidationError(
            codigo='VAL_TPDOC_02',
            descripcion='TPDOC=13: el campo RZ (razón social) debe estar vacío para personas naturales.',
        ))
    return errores


def validar_tpdoc_03(tercero: dict) -> list[ValidationError]:
    """
    Si TPDOC='31': RZ es obligatorio, AP1/AP2/NM1/NM2 deben ser None/vacíos.

    Args:
        tercero: dict con campos tpdoc, rz, ap1, ap2, nm1, nm2
    Returns:
        lista de ValidationError
    """
    errores: list[ValidationError] = []
    if str(tercero.get('tpdoc')).strip() != TPDOC_JURIDICA:
        return errores
    if _vacio(tercero.get('rz')):
        errores.append(ValidationError(
            codigo='VAL_TPDOC_03',
            descripcion='TPDOC=31: el campo RZ (razón social) es obligatorio para personas jurídicas.',
        ))
    for campo in ('ap1', 'ap2', 'nm1', 'nm2'):
        if not _vacio(tercero.get(campo)):
            errores.append(ValidationError(
                codigo='VAL_TPDOC_03',
                descripcion=(
                    f'TPDOC=31: el campo {campo.upper()} debe estar vacío para personas jurídicas.'
                ),
            ))
    return errores


def validar_dv_01(tercero: dict) -> list[ValidationError]:
    """
    Si TPDOC='31': DV no puede ser None ni vacío.

    Args:
        tercero: dict con campos tpdoc, dv
    Returns:
        lista de ValidationError
    """
    if str(tercero.get('tpdoc')).strip() != TPDOC_JURIDICA:
        return []
    if _vacio(tercero.get('dv')):
        return [ValidationError(
            codigo='VAL_DV_01',
            descripcion='TPDOC=31: el Dígito de Verificación (DV) es obligatorio.',
        )]
    return []


def validar_dir_01(tercero: dict) -> list[ValidationError]:
    """
    DIR debe tener más de 8 caracteres (no None, len > 8).

    Args:
        tercero: dict con campo 'dir'
    Returns:
        lista de ValidationError
    """
    dir_valor = tercero.get('dir')
    if _vacio(dir_valor) or len(str(dir_valor).strip()) <= 8:
        return [ValidationError(
            codigo='VAL_DIR_01',
            descripcion=(
                'La dirección debe tener más de 8 caracteres. '
                f"Valor actual: '{dir_valor}'."
            ),
        )]
    return []


def validar_pais_01(tercero: dict, paises_validos: set[str]) -> list[ValidationError]:
    """
    PAIS debe ser un valor presente en paises_validos.

    Args:
        tercero: dict con campo 'pais'
        paises_validos: conjunto de códigos de países válidos
    Returns:
        lista de ValidationError
    """
    pais = tercero.get('pais')
    if _vacio(pais) or str(pais).strip() not in paises_validos:
        return [ValidationError(
            codigo='VAL_PAIS_01',
            descripcion=f"El código de país '{pais}' no es válido o no está en la lista de países permitidos.",
        )]
    return []


def validar_dpto_01(
    tercero: dict,
    pais_dpto_set: set[tuple],
    aplica_pais: bool,
) -> list[ValidationError]:
    """
    Verifica que el departamento exista en la combinación (pais, dpto).

    - Si aplica_pais=True: verifica (pais, dpto) en pais_dpto_set
    - Si aplica_pais=False: verifica ('169', dpto) en pais_dpto_set

    Args:
        tercero: dict con campos 'pais', 'dpto'
        pais_dpto_set: conjunto de tuplas (pais, dpto) válidas
        aplica_pais: indica si el formato requiere el campo PAIS
    Returns:
        lista de ValidationError
    """
    dpto = tercero.get('dpto')
    if _vacio(dpto):
        return [ValidationError(
            codigo='VAL_DPTO_01',
            descripcion='El campo DPTO (departamento) es obligatorio.',
        )]

    pais = str(tercero.get('pais')).strip() if aplica_pais and not _vacio(tercero.get('pais')) else PAIS_COLOMBIA
    dpto_str = str(dpto).strip()

    if (pais, dpto_str) not in pais_dpto_set:
        return [ValidationError(
            codigo='VAL_DPTO_01',
            descripcion=(
                f"La combinación PAIS='{pais}', DPTO='{dpto_str}' "
                f"no existe en la tabla de departamentos."
            ),
        )]
    return []


def validar_mpio_01(
    tercero: dict,
    pais_dpto_mpio_set: set[tuple],
    aplica_pais: bool,
    aplica_dpto: bool,
) -> list[ValidationError]:
    """
    Verifica que el municipio exista en la combinación (pais, dpto, mpio).

    - aplica_pais=False → usa PAIS_COLOMBIA como pais
    - aplica_dpto=False → usa el dpto del tercero de todas formas

    Args:
        tercero: dict con campos 'pais', 'dpto', 'mpio'
        pais_dpto_mpio_set: conjunto de tuplas (pais, dpto, mpio) válidas
        aplica_pais: indica si el formato requiere el campo PAIS
        aplica_dpto: indica si el formato requiere el campo DPTO
    Returns:
        lista de ValidationError
    """
    mpio = tercero.get('mpio')
    if _vacio(mpio):
        return [ValidationError(
            codigo='VAL_MPIO_01',
            descripcion='El campo MPIO (municipio) es obligatorio.',
        )]

    pais = str(tercero.get('pais')).strip() if aplica_pais and not _vacio(tercero.get('pais')) else PAIS_COLOMBIA
    dpto = str(tercero.get('dpto')).strip() if not _vacio(tercero.get('dpto')) else ''
    mpio_str = str(mpio).strip()

    if (pais, dpto, mpio_str) not in pais_dpto_mpio_set:
        return [ValidationError(
            codigo='VAL_MPIO_01',
            descripcion=(
                f"La combinación PAIS='{pais}', DPTO='{dpto}', MPIO='{mpio_str}' "
                f"no existe en la tabla de municipios."
            ),
        )]
    return []


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def ejecutar_validaciones(
    tercero: dict,
    formato_id: str,
    validaciones_formato: list[str],
    campos_requeridos: dict[str, bool],
    paises_validos: set[str],
    pais_dpto_set: set[tuple],
    pais_dpto_mpio_set: set[tuple],
) -> list[ValidationError]:
    """
    Ejecuta primero validaciones globales y luego las validaciones específicas del formato.

    Args:
        tercero: dict con los campos del tercero en minúscula
        formato_id: identificador del formato DIAN (para logging futuro)
        validaciones_formato: lista de códigos de validación a ejecutar
          (ej. ['VAL_TPDOC_01', 'VAL_DV_01', 'VAL_DIR_01', 'VAL_PAIS_01', 'VAL_DPTO_01', 'VAL_MPIO_01'])
        campos_requeridos: dict {nombre_campo: bool} indicando si el campo aplica en el formato
        paises_validos: conjunto de códigos de países válidos
        pais_dpto_set: conjunto de tuplas (pais, dpto) válidas
        pais_dpto_mpio_set: conjunto de tuplas (pais, dpto, mpio) válidas
    Returns:
        lista acumulada de ValidationError
    """
    errores: list[ValidationError] = []

    # Siempre ejecutar validaciones globales
    errores.extend(validar_globales(tercero))

    # Mapa de validaciones disponibles
    aplica_pais = campos_requeridos.get('PAIS', False)
    aplica_dpto = campos_requeridos.get('DPTO', False)

    mapa_validaciones: dict[str, callable] = {
        'VAL_TPDOC_01': lambda: validar_tpdoc_01(tercero),
        'VAL_TPDOC_02': lambda: validar_tpdoc_02(tercero),
        'VAL_TPDOC_03': lambda: validar_tpdoc_03(tercero),
        'VAL_DV_01': lambda: validar_dv_01(tercero),
        'VAL_DIR_01': lambda: validar_dir_01(tercero),
        'VAL_PAIS_01': lambda: validar_pais_01(tercero, paises_validos),
        'VAL_DPTO_01': lambda: validar_dpto_01(tercero, pais_dpto_set, aplica_pais),
        'VAL_MPIO_01': lambda: validar_mpio_01(tercero, pais_dpto_mpio_set, aplica_pais, aplica_dpto),
    }

    for codigo in validaciones_formato:
        funcion = mapa_validaciones.get(codigo)
        if funcion is not None:
            errores.extend(funcion())

    return errores

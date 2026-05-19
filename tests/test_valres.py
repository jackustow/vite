"""Tests unitarios para vite.etl.rules.valres."""

import pytest
from vite.etl.rules.valres import (
    ValidationError,
    _vacio,
    validar_globales,
    validar_tpdoc_01,
    validar_tpdoc_02,
    validar_tpdoc_03,
    validar_dv_01,
    validar_dir_01,
    validar_pais_01,
    validar_dpto_01,
    validar_mpio_01,
    ejecutar_validaciones,
)


# ---------------------------------------------------------------------------
# Fixtures / constantes de apoyo
# ---------------------------------------------------------------------------

PAISES_VALIDOS = {'169', '170', '840'}
PAIS_DPTO_SET = {('169', '05'), ('169', '11'), ('169', '76'), ('170', '01')}
PAIS_DPTO_MPIO_SET = {
    ('169', '05', '001'),
    ('169', '11', '001'),
    ('169', '76', '001'),
}

def tercero_natural_valido() -> dict:
    return {
        'tpdoc': '13', 'nmdoc': '12345678',
        'ap1': 'GARCIA', 'ap2': None, 'nm1': 'PEDRO', 'nm2': None, 'rz': None,
        'dv': None, 'dir': 'CALLE 23 A 15 30 PISO 2',
        'pais': '169', 'dpto': '05', 'mpio': '001',
    }

def tercero_juridico_valido() -> dict:
    return {
        'tpdoc': '31', 'nmdoc': '123456789',
        'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        'rz': 'EMPRESA SA', 'dv': '7',
        'dir': 'CARRERA 10 23 45 PISO 3',
        'pais': '169', 'dpto': '05', 'mpio': '001',
    }


# ---------------------------------------------------------------------------
# _vacio
# ---------------------------------------------------------------------------

class TestVacio:
    def test_none_es_vacio(self):
        assert _vacio(None) is True

    def test_string_vacio_es_vacio(self):
        assert _vacio('') is True

    def test_espacios_es_vacio(self):
        assert _vacio('   ') is True

    def test_cero_no_es_vacio(self):
        assert _vacio(0) is False

    def test_cero_string_no_es_vacio(self):
        assert _vacio('0') is False

    def test_valor_normal_no_es_vacio(self):
        assert _vacio('hola') is False


# ---------------------------------------------------------------------------
# validar_tpdoc_01
# ---------------------------------------------------------------------------

class TestValidarTpdoc01:
    """TPDOC debe ser '13' o '31'."""

    def test_tpdoc_99_genera_error(self):
        tercero = {'tpdoc': '99'}
        errores = validar_tpdoc_01(tercero)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_TPDOC_01'

    def test_tpdoc_13_sin_error(self):
        tercero = {'tpdoc': '13'}
        assert validar_tpdoc_01(tercero) == []

    def test_tpdoc_31_sin_error(self):
        tercero = {'tpdoc': '31'}
        assert validar_tpdoc_01(tercero) == []

    def test_tpdoc_none_genera_error(self):
        tercero = {'tpdoc': None}
        errores = validar_tpdoc_01(tercero)
        assert len(errores) == 1

    def test_tpdoc_vacio_genera_error(self):
        tercero = {'tpdoc': ''}
        errores = validar_tpdoc_01(tercero)
        assert len(errores) == 1

    def test_retorna_lista_de_validation_error(self):
        errores = validar_tpdoc_01({'tpdoc': '99'})
        assert all(isinstance(e, ValidationError) for e in errores)


# ---------------------------------------------------------------------------
# validar_tpdoc_02
# ---------------------------------------------------------------------------

class TestValidarTpdoc02:
    def test_natural_sin_ap1_genera_error(self):
        tercero = {'tpdoc': '13', 'ap1': None, 'nm1': 'PEDRO', 'rz': None}
        errores = validar_tpdoc_02(tercero)
        assert any(e.codigo == 'VAL_TPDOC_02' for e in errores)

    def test_natural_sin_nm1_genera_error(self):
        tercero = {'tpdoc': '13', 'ap1': 'GARCIA', 'nm1': None, 'rz': None}
        errores = validar_tpdoc_02(tercero)
        assert any(e.codigo == 'VAL_TPDOC_02' for e in errores)

    def test_natural_con_rz_genera_error(self):
        tercero = {'tpdoc': '13', 'ap1': 'GARCIA', 'nm1': 'PEDRO', 'rz': 'NO DEBERIA'}
        errores = validar_tpdoc_02(tercero)
        assert any(e.codigo == 'VAL_TPDOC_02' for e in errores)

    def test_natural_valido_sin_error(self):
        tercero = {'tpdoc': '13', 'ap1': 'GARCIA', 'nm1': 'PEDRO', 'rz': None}
        assert validar_tpdoc_02(tercero) == []

    def test_juridica_ignorada(self):
        tercero = {'tpdoc': '31', 'ap1': None, 'nm1': None, 'rz': None}
        assert validar_tpdoc_02(tercero) == []


# ---------------------------------------------------------------------------
# validar_tpdoc_03
# ---------------------------------------------------------------------------

class TestValidarTpdoc03:
    def test_juridica_sin_rz_genera_error(self):
        tercero = {'tpdoc': '31', 'rz': None, 'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None}
        errores = validar_tpdoc_03(tercero)
        assert any(e.codigo == 'VAL_TPDOC_03' for e in errores)

    def test_juridica_con_ap1_genera_error(self):
        tercero = {'tpdoc': '31', 'rz': 'EMPRESA SA', 'ap1': 'GARCIA', 'ap2': None, 'nm1': None, 'nm2': None}
        errores = validar_tpdoc_03(tercero)
        assert any(e.codigo == 'VAL_TPDOC_03' for e in errores)

    def test_juridica_valida_sin_error(self):
        tercero = {'tpdoc': '31', 'rz': 'EMPRESA SA', 'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None}
        assert validar_tpdoc_03(tercero) == []

    def test_natural_ignorada(self):
        tercero = {'tpdoc': '13', 'rz': None, 'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None}
        assert validar_tpdoc_03(tercero) == []


# ---------------------------------------------------------------------------
# validar_dv_01
# ---------------------------------------------------------------------------

class TestValidarDv01:
    """Si TPDOC='31': DV no puede ser None ni vacío."""

    def test_juridica_dv_none_genera_error(self):
        tercero = {'tpdoc': '31', 'dv': None}
        errores = validar_dv_01(tercero)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_DV_01'

    def test_juridica_dv_vacio_genera_error(self):
        tercero = {'tpdoc': '31', 'dv': ''}
        errores = validar_dv_01(tercero)
        assert len(errores) == 1

    def test_juridica_dv_presente_sin_error(self):
        tercero = {'tpdoc': '31', 'dv': '7'}
        assert validar_dv_01(tercero) == []

    def test_natural_dv_none_sin_error(self):
        """Para persona natural el DV no aplica → sin error."""
        tercero = {'tpdoc': '13', 'dv': None}
        assert validar_dv_01(tercero) == []

    def test_natural_dv_presente_sin_error(self):
        tercero = {'tpdoc': '13', 'dv': '3'}
        assert validar_dv_01(tercero) == []


# ---------------------------------------------------------------------------
# validar_dir_01
# ---------------------------------------------------------------------------

class TestValidarDir01:
    """DIR debe tener más de 8 caracteres."""

    def test_dir_corta_genera_error(self):
        """'CORTO' tiene 5 chars → error."""
        tercero = {'dir': 'CORTO'}
        errores = validar_dir_01(tercero)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_DIR_01'

    def test_dir_exactamente_8_genera_error(self):
        """Exactamente 8 chars → error (debe ser MAYOR que 8)."""
        tercero = {'dir': '12345678'}
        errores = validar_dir_01(tercero)
        assert len(errores) == 1

    def test_dir_9_chars_sin_error(self):
        """9 chars → sin error."""
        tercero = {'dir': '123456789'}
        assert validar_dir_01(tercero) == []

    def test_dir_larga_sin_error(self):
        tercero = {'dir': 'CALLE 23 A 15 30'}
        assert validar_dir_01(tercero) == []

    def test_dir_none_genera_error(self):
        tercero = {'dir': None}
        errores = validar_dir_01(tercero)
        assert len(errores) == 1

    def test_dir_vacia_genera_error(self):
        tercero = {'dir': ''}
        errores = validar_dir_01(tercero)
        assert len(errores) == 1


# ---------------------------------------------------------------------------
# validar_pais_01
# ---------------------------------------------------------------------------

class TestValidarPais01:
    """PAIS debe estar en paises_validos."""

    def test_pais_invalido_genera_error(self):
        tercero = {'pais': '999'}
        errores = validar_pais_01(tercero, PAISES_VALIDOS)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_PAIS_01'

    def test_pais_valido_sin_error(self):
        tercero = {'pais': '169'}
        assert validar_pais_01(tercero, PAISES_VALIDOS) == []

    def test_pais_none_genera_error(self):
        tercero = {'pais': None}
        errores = validar_pais_01(tercero, PAISES_VALIDOS)
        assert len(errores) == 1

    def test_pais_vacio_genera_error(self):
        tercero = {'pais': ''}
        errores = validar_pais_01(tercero, PAISES_VALIDOS)
        assert len(errores) == 1

    def test_todos_los_paises_validos_pasan(self):
        for pais in PAISES_VALIDOS:
            tercero = {'pais': pais}
            assert validar_pais_01(tercero, PAISES_VALIDOS) == []


# ---------------------------------------------------------------------------
# validar_dpto_01
# ---------------------------------------------------------------------------

class TestValidarDpto01:
    def test_dpto_valido_con_pais_sin_error(self):
        tercero = {'pais': '169', 'dpto': '05'}
        assert validar_dpto_01(tercero, PAIS_DPTO_SET, aplica_pais=True) == []

    def test_dpto_invalido_con_pais_genera_error(self):
        tercero = {'pais': '169', 'dpto': '99'}
        errores = validar_dpto_01(tercero, PAIS_DPTO_SET, aplica_pais=True)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_DPTO_01'

    def test_dpto_valido_sin_pais_aplica_colombia(self):
        """aplica_pais=False → usa '169' por defecto."""
        tercero = {'pais': None, 'dpto': '05'}
        assert validar_dpto_01(tercero, PAIS_DPTO_SET, aplica_pais=False) == []

    def test_dpto_none_genera_error(self):
        tercero = {'pais': '169', 'dpto': None}
        errores = validar_dpto_01(tercero, PAIS_DPTO_SET, aplica_pais=True)
        assert len(errores) == 1

    def test_pais_extranjero_valido_en_set(self):
        tercero = {'pais': '170', 'dpto': '01'}
        assert validar_dpto_01(tercero, PAIS_DPTO_SET, aplica_pais=True) == []


# ---------------------------------------------------------------------------
# validar_mpio_01
# ---------------------------------------------------------------------------

class TestValidarMpio01:
    def test_mpio_valido_sin_error(self):
        tercero = {'pais': '169', 'dpto': '05', 'mpio': '001'}
        assert validar_mpio_01(tercero, PAIS_DPTO_MPIO_SET, aplica_pais=True, aplica_dpto=True) == []

    def test_mpio_invalido_genera_error(self):
        tercero = {'pais': '169', 'dpto': '05', 'mpio': '999'}
        errores = validar_mpio_01(tercero, PAIS_DPTO_MPIO_SET, aplica_pais=True, aplica_dpto=True)
        assert len(errores) == 1
        assert errores[0].codigo == 'VAL_MPIO_01'

    def test_mpio_none_genera_error(self):
        tercero = {'pais': '169', 'dpto': '05', 'mpio': None}
        errores = validar_mpio_01(tercero, PAIS_DPTO_MPIO_SET, aplica_pais=True, aplica_dpto=True)
        assert len(errores) == 1

    def test_mpio_sin_pais_usa_colombia(self):
        """aplica_pais=False → usa '169'."""
        tercero = {'pais': None, 'dpto': '11', 'mpio': '001'}
        assert validar_mpio_01(tercero, PAIS_DPTO_MPIO_SET, aplica_pais=False, aplica_dpto=True) == []


# ---------------------------------------------------------------------------
# validar_globales
# ---------------------------------------------------------------------------

class TestValidarGlobales:
    def test_tpdoc_none_genera_error(self):
        tercero = {**tercero_natural_valido(), 'tpdoc': None}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_01' for e in errores)

    def test_nmdoc_none_genera_error(self):
        tercero = {**tercero_natural_valido(), 'nmdoc': None}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_02' for e in errores)

    def test_natural_valido_sin_errores_globales(self):
        assert validar_globales(tercero_natural_valido()) == []

    def test_juridica_valida_sin_errores_globales(self):
        assert validar_globales(tercero_juridico_valido()) == []

    def test_natural_sin_ap1_genera_global_03(self):
        tercero = {**tercero_natural_valido(), 'ap1': None}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_03' for e in errores)

    def test_natural_con_rz_genera_global_05(self):
        tercero = {**tercero_natural_valido(), 'rz': 'NO DEBERIA'}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_05' for e in errores)

    def test_juridica_sin_rz_genera_global_06(self):
        tercero = {**tercero_juridico_valido(), 'rz': None}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_06' for e in errores)

    def test_juridica_con_ap1_genera_global_07(self):
        tercero = {**tercero_juridico_valido(), 'ap1': 'GARCIA'}
        errores = validar_globales(tercero)
        assert any(e.codigo == 'VAL_GLOBAL_07' for e in errores)


# ---------------------------------------------------------------------------
# ejecutar_validaciones — dispatcher
# ---------------------------------------------------------------------------

class TestEjecutarValidaciones:
    """Verifica el dispatcher de validaciones."""

    def test_formato_solo_tpdoc_01_con_tpdoc_99(self):
        """Formato con solo VAL_TPDOC_01 y TPDOC='99' → retorna error VAL_TPDOC_01."""
        tercero = {
            'tpdoc': '99', 'nmdoc': '12345678',
            'ap1': 'A', 'nm1': 'B', 'ap2': None, 'nm2': None, 'rz': None,
            'dv': None, 'dir': 'CALLE 10 20 30', 'pais': '169', 'dpto': '05', 'mpio': '001',
        }
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_TPDOC_01'],
            campos_requeridos={},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        codigos = [e.codigo for e in errores]
        assert 'VAL_TPDOC_01' in codigos

    def test_validaciones_vacias_solo_ejecuta_globales(self):
        """Sin validaciones específicas → solo ejecuta globales."""
        tercero = tercero_natural_valido()
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=[],
            campos_requeridos={},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        assert errores == []

    def test_codigo_desconocido_ignorado(self):
        """Código de validación no registrado → se ignora sin error."""
        tercero = tercero_natural_valido()
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_INEXISTENTE_99'],
            campos_requeridos={},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        assert errores == []

    def test_multiples_validaciones_acumulan_errores(self):
        """Múltiples validaciones fallando → todos los errores se acumulan."""
        tercero = {
            'tpdoc': '99', 'nmdoc': '12345678',
            'ap1': None, 'nm1': None, 'ap2': None, 'nm2': None, 'rz': None,
            'dv': None, 'dir': 'CORTO', 'pais': '999', 'dpto': '99', 'mpio': '999',
        }
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_TPDOC_01', 'VAL_DIR_01', 'VAL_PAIS_01'],
            campos_requeridos={},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        codigos = [e.codigo for e in errores]
        assert 'VAL_TPDOC_01' in codigos
        assert 'VAL_DIR_01' in codigos
        assert 'VAL_PAIS_01' in codigos

    def test_dpto_con_aplica_pais_true(self):
        """VAL_DPTO_01 con aplica_pais derivado de campos_requeridos."""
        tercero = {**tercero_natural_valido(), 'dpto': '99'}
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_DPTO_01'],
            campos_requeridos={'PAIS': True},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        assert any(e.codigo == 'VAL_DPTO_01' for e in errores)

    def test_mpio_con_aplica_pais_y_dpto(self):
        """VAL_MPIO_01 con aplica_pais y aplica_dpto derivados de campos_requeridos."""
        tercero = {**tercero_natural_valido(), 'mpio': '999'}
        errores = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_MPIO_01'],
            campos_requeridos={'PAIS': True, 'DPTO': True},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        assert any(e.codigo == 'VAL_MPIO_01' for e in errores)

    def test_retorna_lista_de_validation_error(self):
        """El resultado es siempre una lista de ValidationError."""
        tercero = tercero_natural_valido()
        resultado = ejecutar_validaciones(
            tercero=tercero,
            formato_id='1001',
            validaciones_formato=['VAL_TPDOC_01'],
            campos_requeridos={},
            paises_validos=PAISES_VALIDOS,
            pais_dpto_set=PAIS_DPTO_SET,
            pais_dpto_mpio_set=PAIS_DPTO_MPIO_SET,
        )
        assert isinstance(resultado, list)

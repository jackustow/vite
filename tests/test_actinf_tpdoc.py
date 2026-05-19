"""Tests unitarios para vite.etl.rules.actinf_tpdoc."""

import pytest
from vite.etl.rules.actinf_tpdoc import inferir_tpdoc, aplicar_tpdoc


# ---------------------------------------------------------------------------
# inferir_tpdoc — longitud del NMDOC
# ---------------------------------------------------------------------------

class TestInferirTpdoc:
    """Verifica la inferencia del tipo de documento según longitud."""

    def test_8_digitos_es_natural(self):
        """NMDOC con 8 dígitos → TPDOC='13' (persona natural)."""
        assert inferir_tpdoc('12345678') == '13'

    def test_9_digitos_es_juridica(self):
        """NMDOC con exactamente 9 dígitos → TPDOC='31' (persona jurídica)."""
        assert inferir_tpdoc('123456789') == '31'

    def test_10_digitos_es_natural(self):
        """NMDOC con 10 dígitos → TPDOC='13'."""
        assert inferir_tpdoc('1234567890') == '13'

    def test_11_digitos_es_natural(self):
        """NMDOC con 11+ dígitos → TPDOC='13'."""
        assert inferir_tpdoc('12345678901') == '13'

    def test_1_digito_es_natural(self):
        """NMDOC con muy pocos dígitos → TPDOC='13'."""
        assert inferir_tpdoc('1') == '13'

    def test_nmdoc_none_retorna_none(self):
        """None → retorna None."""
        assert inferir_tpdoc(None) is None

    def test_nmdoc_vacio_retorna_none(self):
        """String vacío → retorna None."""
        assert inferir_tpdoc('') is None

    def test_nmdoc_solo_letras_retorna_none(self):
        """String sin dígitos → retorna None."""
        assert inferir_tpdoc('abcdef') is None

    def test_nmdoc_con_guiones_cuenta_solo_digitos(self):
        """Guiones son ignorados; se cuentan solo los dígitos."""
        # '12-3456789' tiene 9 dígitos → '31'
        assert inferir_tpdoc('12-3456789') == '31'

    def test_nmdoc_con_espacios_cuenta_solo_digitos(self):
        """Espacios son ignorados."""
        # '1234 56789' tiene 9 dígitos → '31'
        assert inferir_tpdoc('1234 56789') == '31'

    def test_nmdoc_8_digitos_con_letras_mixtas(self):
        """Solo se cuentan los dígitos aunque haya letras."""
        # 'A1234567B' tiene 7 dígitos → '13'
        assert inferir_tpdoc('A1234567B') == '13'

    def test_retorna_string(self):
        """El resultado es siempre un string (no int)."""
        resultado = inferir_tpdoc('123456789')
        assert isinstance(resultado, str)


# ---------------------------------------------------------------------------
# aplicar_tpdoc — lógica de actualización
# ---------------------------------------------------------------------------

class TestAplicarTpdoc:
    """Verifica que aplicar_tpdoc retorne el cambio correcto o None."""

    def test_tpdoc_cambia_retorna_dict(self):
        """Cuando el TPDOC calculado difiere del actual → retorna dict con nuevo valor."""
        tercero = {'tpdoc': '13', 'nmdoc': '123456789'}  # 9 dígitos → debería ser '31'
        resultado = aplicar_tpdoc(tercero)
        assert resultado == {'tpdoc': '31'}

    def test_tpdoc_igual_retorna_none(self):
        """Cuando el TPDOC calculado es igual al actual → retorna None."""
        tercero = {'tpdoc': '31', 'nmdoc': '123456789'}  # ya es '31' → sin cambio
        assert aplicar_tpdoc(tercero) is None

    def test_tpdoc_natural_sin_cambio(self):
        """TPDOC='13' con NMDOC de 8 dígitos → sin cambio."""
        tercero = {'tpdoc': '13', 'nmdoc': '12345678'}
        assert aplicar_tpdoc(tercero) is None

    def test_tpdoc_natural_cambia_de_31_a_13(self):
        """TPDOC='31' incorrecto con NMDOC de 8 dígitos → cambia a '13'."""
        tercero = {'tpdoc': '31', 'nmdoc': '12345678'}
        resultado = aplicar_tpdoc(tercero)
        assert resultado == {'tpdoc': '13'}

    def test_nmdoc_none_retorna_none(self):
        """NMDOC=None → no se puede inferir, retorna None."""
        tercero = {'tpdoc': '13', 'nmdoc': None}
        assert aplicar_tpdoc(tercero) is None

    def test_nmdoc_vacio_retorna_none(self):
        """NMDOC vacío → no se puede inferir, retorna None."""
        tercero = {'tpdoc': '13', 'nmdoc': ''}
        assert aplicar_tpdoc(tercero) is None

    def test_tpdoc_none_con_nmdoc_9_digitos(self):
        """TPDOC=None con NMDOC de 9 dígitos → retorna {'tpdoc': '31'}."""
        tercero = {'tpdoc': None, 'nmdoc': '123456789'}
        resultado = aplicar_tpdoc(tercero)
        assert resultado == {'tpdoc': '31'}

    def test_tpdoc_como_entero_se_compara_correctamente(self):
        """TPDOC almacenado como int se convierte a string para comparar."""
        tercero = {'tpdoc': 31, 'nmdoc': '123456789'}
        # int 31 → str '31' → igual al calculado '31' → sin cambio
        assert aplicar_tpdoc(tercero) is None

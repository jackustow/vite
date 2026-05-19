"""Tests unitarios para vite.etl.rules.actinf_dv."""

import pytest
from vite.etl.rules.actinf_dv import calcular_dv_colombia, aplicar_dv


# ---------------------------------------------------------------------------
# calcular_dv_colombia — NITs conocidos
# ---------------------------------------------------------------------------

class TestCalcularDvColombia:
    """Verifica el algoritmo DIAN con valores conocidos."""

    def test_nit_80100491_dv_3(self):
        """NIT 80100491 debe tener DV=3."""
        assert calcular_dv_colombia(80100491) == 3

    def test_nit_811022981_dv_7(self):
        """NIT 811022981 debe tener DV=7."""
        assert calcular_dv_colombia(811022981) == 7

    def test_nit_como_string(self):
        """El NIT puede pasarse como string y produce el mismo resultado."""
        assert calcular_dv_colombia("80100491") == 3

    def test_nit_con_ceros_a_la_izquierda(self):
        """Ceros a la izquierda en el string no alteran el resultado."""
        # "080100491" tiene los mismos dígitos significativos que "80100491"
        assert calcular_dv_colombia("080100491") == calcular_dv_colombia("80100491")

    def test_nit_con_formato_con_guiones(self):
        """El NIT puede venir con guiones y los ignora correctamente."""
        assert calcular_dv_colombia("80100491-3") == 3

    def test_nit_con_espacios(self):
        """Espacios en el NIT son ignorados."""
        assert calcular_dv_colombia("80 100 491") == 3

    def test_nit_vacio_lanza_value_error(self):
        """Un string sin dígitos lanza ValueError."""
        with pytest.raises(ValueError, match="no contiene números válidos"):
            calcular_dv_colombia("")

    def test_nit_none_lanza_value_error(self):
        """None como argumento lanza ValueError."""
        with pytest.raises(ValueError, match="no contiene números válidos"):
            calcular_dv_colombia(None)

    def test_nit_solo_letras_lanza_value_error(self):
        """Un string con solo letras lanza ValueError."""
        with pytest.raises(ValueError, match="no contiene números válidos"):
            calcular_dv_colombia("abcdef")

    def test_retorna_entero(self):
        """El valor retornado es un int."""
        resultado = calcular_dv_colombia(80100491)
        assert isinstance(resultado, int)

    def test_dv_en_rango_0_a_9(self):
        """El DV siempre está entre 0 y 9 (no puede ser 10)."""
        # El algoritmo produce 11-residuo o residuo; 11-1=10 nunca ocurre porque
        # residuo==1 → return 1, y residuo==0 → return 0
        resultado = calcular_dv_colombia(80100491)
        assert 0 <= resultado <= 9


# ---------------------------------------------------------------------------
# aplicar_dv — lógica de actualización
# ---------------------------------------------------------------------------

class TestAplicarDv:
    """Verifica que aplicar_dv retorne el cambio correcto o None."""

    def test_tpdoc_31_dv_incorrecto_retorna_cambio(self):
        """TPDOC=31 con DV incorrecto → retorna dict con el DV correcto."""
        tercero = {'tpdoc': '31', 'nmdoc': '80100491', 'dv': '9'}
        resultado = aplicar_dv(tercero)
        assert resultado is not None
        assert resultado == {'dv': '3'}

    def test_tpdoc_31_dv_correcto_retorna_none(self):
        """TPDOC=31 con DV ya correcto → retorna None (sin cambio)."""
        tercero = {'tpdoc': '31', 'nmdoc': '80100491', 'dv': '3'}
        assert aplicar_dv(tercero) is None

    def test_tpdoc_31_dv_none_retorna_cambio(self):
        """TPDOC=31 con DV=None → retorna dict con el DV calculado."""
        tercero = {'tpdoc': '31', 'nmdoc': '80100491', 'dv': None}
        resultado = aplicar_dv(tercero)
        assert resultado == {'dv': '3'}

    def test_tpdoc_13_retorna_none(self):
        """TPDOC=13 (persona natural) → no aplica DV, retorna None."""
        tercero = {'tpdoc': '13', 'nmdoc': '12345678', 'dv': None}
        assert aplicar_dv(tercero) is None

    def test_tpdoc_diferente_retorna_none(self):
        """Cualquier TPDOC diferente de '31' → retorna None."""
        tercero = {'tpdoc': '22', 'nmdoc': '123456789', 'dv': None}
        assert aplicar_dv(tercero) is None

    def test_nmdoc_none_retorna_none(self):
        """TPDOC=31 pero NMDOC=None → no puede calcular DV, retorna None."""
        tercero = {'tpdoc': '31', 'nmdoc': None, 'dv': None}
        assert aplicar_dv(tercero) is None

    def test_nmdoc_vacio_retorna_none(self):
        """TPDOC=31 pero NMDOC vacío → retorna None."""
        tercero = {'tpdoc': '31', 'nmdoc': '', 'dv': None}
        assert aplicar_dv(tercero) is None

    def test_nit_811022981_dv_7(self):
        """Verifica segundo NIT conocido (811022981 → DV=7)."""
        tercero = {'tpdoc': '31', 'nmdoc': '811022981', 'dv': None}
        resultado = aplicar_dv(tercero)
        assert resultado == {'dv': '7'}

    def test_dv_como_entero_se_convierte_correctamente(self):
        """DV almacenado como int se compara correctamente con el calculado."""
        # dv=3 como int debe considerarse igual a '3' calculado
        tercero = {'tpdoc': '31', 'nmdoc': '80100491', 'dv': 3}
        assert aplicar_dv(tercero) is None

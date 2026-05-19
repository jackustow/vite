"""Tests unitarios para vite.etl.rules.actinf_nombres."""

import pytest
from vite.etl.rules.actinf_nombres import redistribuir_nombres


# ---------------------------------------------------------------------------
# TPDOC=31 — persona jurídica: campos de nombres → razón social
# ---------------------------------------------------------------------------

class TestRedistribuirNombresJuridica:
    """TPDOC=31: AP1/AP2/NM1/NM2 deben moverse a RZ."""

    def test_cuatro_campos_a_razon_social(self):
        """AP1, AP2, NM1, NM2 se concatenan en RZ y quedan en None."""
        tercero = {
            'tpdoc': '31',
            'ap1': 'MARTINEZ', 'ap2': 'LOPEZ',
            'nm1': 'JUAN', 'nm2': 'CARLOS',
            'rz': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['rz'] == 'MARTINEZ LOPEZ JUAN CARLOS'
        assert cambios['ap1'] is None
        assert cambios['ap2'] is None
        assert cambios['nm1'] is None
        assert cambios['nm2'] is None

    def test_solo_ap1_y_nm1(self):
        """Solo AP1 y NM1 presentes → se concatenan en RZ."""
        tercero = {
            'tpdoc': '31',
            'ap1': 'INDUSTRIAS', 'ap2': None,
            'nm1': 'ANDINA', 'nm2': None,
            'rz': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['rz'] == 'INDUSTRIAS ANDINA'
        assert cambios['ap1'] is None
        assert cambios['nm1'] is None

    def test_solo_ap1(self):
        """Solo AP1 presente → se mueve a RZ."""
        tercero = {
            'tpdoc': '31',
            'ap1': 'ACME', 'ap2': None,
            'nm1': None, 'nm2': None,
            'rz': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['rz'] == 'ACME'
        assert cambios['ap1'] is None

    def test_ninguno_de_los_campos_tiene_valor(self):
        """Si AP1/AP2/NM1/NM2 son None → no hay cambios (ya está bien o aún falta RZ)."""
        tercero = {
            'tpdoc': '31',
            'ap1': None, 'ap2': None,
            'nm1': None, 'nm2': None,
            'rz': 'EMPRESA YA TIENE RZ',
        }
        cambios = redistribuir_nombres(tercero)
        # No hay nombres que mover → no hay cambios desde esta función
        assert cambios == {}

    def test_campos_con_espacios_en_blanco_ignorados(self):
        """Campos con solo espacios no se incluyen en la concatenación."""
        tercero = {
            'tpdoc': '31',
            'ap1': 'ACME', 'ap2': '   ',
            'nm1': 'SA', 'nm2': None,
            'rz': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['rz'] == 'ACME SA'


# ---------------------------------------------------------------------------
# TPDOC=13 — persona natural: razón social → campos de nombres
# ---------------------------------------------------------------------------

class TestRedistribuirNombresNatural:
    """TPDOC=13: RZ debe distribuirse en AP1/NM1/AP2/NM2."""

    def test_cuatro_palabras(self):
        """RZ con 4 palabras: word[0]→ap1, word[1]→nm1, word[2]→ap2, word[3]→nm2."""
        tercero = {
            'tpdoc': '13',
            'rz': 'CRUZ ROMERO JAIME ANDRES',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['ap1'] == 'CRUZ'
        assert cambios['nm1'] == 'ROMERO'
        assert cambios['ap2'] == 'JAIME'
        assert cambios['nm2'] == 'ANDRES'
        assert cambios['rz'] is None

    def test_tres_palabras(self):
        """RZ con 3 palabras: ap1, nm1, ap2 poblados; nm2=None."""
        tercero = {
            'tpdoc': '13',
            'rz': 'HERNANDEZ NIETO PEDRO',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['ap1'] == 'HERNANDEZ'
        assert cambios['nm1'] == 'NIETO'
        assert cambios['ap2'] == 'PEDRO'
        assert cambios['nm2'] is None
        assert cambios['rz'] is None

    def test_dos_palabras(self):
        """RZ con 2 palabras: ap1 y nm1 poblados; ap2=None, nm2=None."""
        tercero = {
            'tpdoc': '13',
            'rz': 'GOMEZ RIVERA',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['ap1'] == 'GOMEZ'
        assert cambios['nm1'] == 'RIVERA'
        assert cambios['ap2'] is None
        assert cambios['nm2'] is None
        assert cambios['rz'] is None

    def test_mas_de_cuatro_palabras_concatena_en_nm2(self):
        """Palabras en posición 4+ se concatenan en NM2."""
        tercero = {
            'tpdoc': '13',
            'rz': 'GARCIA TORRES LUIS MIGUEL ANTONIO',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['ap1'] == 'GARCIA'
        assert cambios['nm1'] == 'TORRES'
        assert cambios['ap2'] == 'LUIS'
        assert cambios['nm2'] == 'MIGUEL ANTONIO'
        assert cambios['rz'] is None

    def test_cinco_palabras_nm2_contiene_resto(self):
        """5 palabras: las últimas dos se unen en NM2."""
        tercero = {
            'tpdoc': '13',
            'rz': 'APELLIDO1 NOMBRE1 APELLIDO2 NOMBRE2 EXTRA',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios['nm2'] == 'NOMBRE2 EXTRA'

    def test_rz_none_sin_cambios(self):
        """RZ=None para persona natural → sin cambios."""
        tercero = {
            'tpdoc': '13',
            'rz': None,
            'ap1': 'GARCIA', 'ap2': None, 'nm1': 'PEDRO', 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios == {}

    def test_rz_vacio_sin_cambios(self):
        """RZ con solo espacios para persona natural → sin cambios."""
        tercero = {
            'tpdoc': '13',
            'rz': '   ',
            'ap1': 'GARCIA', 'ap2': None, 'nm1': 'PEDRO', 'nm2': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios == {}


# ---------------------------------------------------------------------------
# Sin cambios necesarios
# ---------------------------------------------------------------------------

class TestSinCambios:
    """Casos donde no debe haber cambios."""

    def test_tpdoc_desconocido_no_modifica(self):
        """TPDOC distinto de '13' y '31' → no hay cambios."""
        tercero = {
            'tpdoc': '22',
            'ap1': 'GARCIA', 'ap2': None, 'nm1': 'PEDRO', 'nm2': None,
            'rz': None,
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios == {}

    def test_juridica_con_rz_ya_completo_sin_nombres(self):
        """TPDOC=31 con RZ ya poblado y nombres vacíos → sin cambios."""
        tercero = {
            'tpdoc': '31',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
            'rz': 'EMPRESA SA',
        }
        cambios = redistribuir_nombres(tercero)
        assert cambios == {}

    def test_retorna_dict_vacio_no_none(self):
        """La función retorna un dict vacío (no None) cuando no hay cambios."""
        tercero = {
            'tpdoc': '31',
            'ap1': None, 'ap2': None, 'nm1': None, 'nm2': None,
            'rz': 'EMPRESA SA',
        }
        resultado = redistribuir_nombres(tercero)
        assert isinstance(resultado, dict)
        assert len(resultado) == 0

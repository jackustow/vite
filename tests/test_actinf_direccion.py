"""Tests unitarios para vite.etl.rules.actinf_direccion."""

import pytest
from vite.etl.rules.actinf_direccion import normalizar_direccion, _construir_patron


# Nomenclaturas mínimas usadas en los tests
NOMENCLATURAS = {
    'CR': ['Carrera', 'Crr'],
    'AP': ['Apartamento', 'Aparta'],
    'ED': ['Edificio'],
    'SUR': ['Sur'],
}


# ---------------------------------------------------------------------------
# normalizar_direccion — casos principales
# ---------------------------------------------------------------------------

class TestNormalizarDireccion:
    """Verifica la normalización completa de direcciones colombianas."""

    def test_direccion_completa_normalizada(self):
        """
        Dirección del spec:
        'Carrera 25 A # 38D sur - 111, Apartamento 1513, Edificio Castello'
        Debe quedar en uppercase, con nomenclaturas reemplazadas y sin especiales.
        """
        direccion = "Carrera 25 A # 38D sur - 111, Apartamento 1513, Edificio Castello"
        resultado, normalizado = normalizar_direccion(direccion, NOMENCLATURAS)

        assert normalizado is True
        assert resultado is not None
        # Letras de nomenclaturas reemplazadas
        assert 'CR' in resultado          # 'Carrera' → 'CR'
        assert 'AP' in resultado          # 'Apartamento' → 'AP'
        assert 'ED' in resultado          # 'Edificio' → 'ED'
        assert 'SUR' in resultado         # 'sur' → 'SUR'
        # No debe contener caracteres especiales como '#', '-', ','
        assert '#' not in resultado
        assert '-' not in resultado
        assert ',' not in resultado
        # Resultado en mayúsculas
        assert resultado == resultado.upper()

    def test_uppercase(self):
        """El resultado siempre está en mayúsculas."""
        direccion = "calle 10 sur"
        resultado, _ = normalizar_direccion(direccion, {})
        assert resultado == resultado.upper()

    def test_sin_especiales(self):
        """Los caracteres especiales se eliminan."""
        direccion = "CLL 10 # 20-30 (piso 2)"
        resultado, normalizado = normalizar_direccion(direccion, {})
        assert '(' not in (resultado or '')
        assert ')' not in (resultado or '')

    def test_espacios_multiples_colapsados(self):
        """Espacios múltiples se reducen a uno."""
        direccion = "CALLE   10   A   20   30"
        resultado, _ = normalizar_direccion(direccion, {})
        assert '  ' not in (resultado or '')

    def test_direccion_none_retorna_none_false(self):
        """None → retorna (None, False)."""
        resultado, normalizado = normalizar_direccion(None, NOMENCLATURAS)
        assert resultado is None
        assert normalizado is False

    def test_direccion_vacia_retorna_none_false(self):
        """String vacío → retorna (None, False)."""
        resultado, normalizado = normalizar_direccion('', NOMENCLATURAS)
        assert resultado is None
        assert normalizado is False

    def test_direccion_solo_espacios_retorna_none_false(self):
        """String con solo espacios → retorna (None, False)."""
        resultado, normalizado = normalizar_direccion('   ', NOMENCLATURAS)
        assert resultado is None
        assert normalizado is False

    def test_direccion_corta_retorna_fallback_false(self):
        """Dirección que tras normalizar tiene < 8 chars → retorna (fallback, False)."""
        # "AB 1" → 4 caracteres tras normalizar
        direccion = "AB 1"
        resultado, normalizado = normalizar_direccion(direccion, NOMENCLATURAS)
        assert normalizado is False
        assert resultado is not None
        # El fallback debe ser la versión uppercase/limpia original (no la normalizada)
        assert len(resultado) > 0

    def test_nomenclaturas_vacias_solo_limpia(self):
        """Sin nomenclaturas → sigue eliminando especiales y poniendo uppercase."""
        direccion = "Calle 10 # 20-30"
        resultado, normalizado = normalizar_direccion(direccion, {})
        # No se reemplazan nomenclaturas pero se limpian especiales
        assert resultado is not None
        assert '#' not in resultado
        assert '-' not in resultado
        assert resultado == resultado.upper()

    def test_nomenclatura_no_reemplaza_subcadena(self):
        """'Sur' no debe reemplazar dentro de 'Surtidora' (límite de palabra)."""
        direccion = "SURTIDORA CALLE 10 123456789"
        resultado, _ = normalizar_direccion(direccion, NOMENCLATURAS)
        # 'SURTIDORA' no debe quedar como 'SURTIDORAA' ni 'SURRTIDORA'
        assert 'SURTIDORA' in resultado

    def test_retorna_tupla(self):
        """La función siempre retorna una tupla de 2 elementos."""
        resultado = normalizar_direccion("CALLE 10 23 45 678", NOMENCLATURAS)
        assert isinstance(resultado, tuple)
        assert len(resultado) == 2

    def test_bool_normalizado_es_true_cuando_longitud_suficiente(self):
        """Una dirección con >= 8 chars tras normalización retorna True en el segundo elemento."""
        direccion = "CALLE 10 23 45"  # > 8 chars
        _, normalizado = normalizar_direccion(direccion, {})
        assert normalizado is True

    def test_reemplazo_case_insensitive(self):
        """El reemplazo de nomenclaturas es insensible a mayúsculas."""
        for variante in ('carrera', 'Carrera', 'CARRERA', 'CarRera'):
            resultado, _ = normalizar_direccion(f"{variante} 10 20 30 40", NOMENCLATURAS)
            assert resultado is not None
            assert 'CR' in resultado


# ---------------------------------------------------------------------------
# _construir_patron — helper interno
# ---------------------------------------------------------------------------

class TestConstruirPatron:
    """Verifica que el helper ordene correctamente los patrones."""

    def test_ordenado_de_mas_largo_a_mas_corto(self):
        """Los patrones más largos deben aparecer primero."""
        nomenclaturas = {
            'AV': ['Avenida'],
            'AVC': ['Avenida Calle'],
        }
        pares = _construir_patron(nomenclaturas)
        longitudes = [len(p[0]) for p in pares]
        assert longitudes == sorted(longitudes, reverse=True)

    def test_palabras_vacias_ignoradas(self):
        """Palabras clave vacías o solo espacios no se incluyen."""
        nomenclaturas = {'CR': ['Carrera', '', '  ']}
        pares = _construir_patron(nomenclaturas)
        codigos_palabras = [p[0] for p in pares]
        assert '' not in codigos_palabras
        assert '  ' not in codigos_palabras

    def test_dict_vacio_retorna_lista_vacia(self):
        """Sin nomenclaturas → lista vacía."""
        assert _construir_patron({}) == []

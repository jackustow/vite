"""Consulta del servicio MUISCA de la DIAN mediante Playwright (sync API).

Este módulo está diseñado para ejecutarse dentro de un worker thread; por eso
utiliza la API síncrona de Playwright en lugar de la asíncrona.
"""

import logging

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

from vite.config.settings import DIAN_URL, TPDOC_NATURAL, TPDOC_JURIDICA
from vite.etl.rules.actinf_dv import calcular_dv_colombia

logger = logging.getLogger(__name__)

# Cache en memoria para evitar consultas duplicadas durante la sesión
_cache: dict[str, dict | None] = {}


def consultar_tercero(nmdoc: str, tpdoc: str) -> dict | None:
    """
    Consulta información del tercero en MUISCA DIAN.

    El resultado se guarda en caché para evitar consultas repetidas al mismo
    NMDOC durante la misma sesión ETL.

    Args:
        nmdoc: número de identificación (sin DV).
        tpdoc: tipo de documento ('13' → persona natural, '31' → persona jurídica).
    Returns:
        dict con los campos actualizados desde DIAN (ap1, ap2, nm1, nm2 o rz),
        o None si el tercero no fue encontrado o ocurrió un error.
    """
    if nmdoc in _cache:
        return _cache[nmdoc]

    resultado = None
    try:
        resultado = _consultar_dian(nmdoc, tpdoc)
    except Exception as e:
        logger.warning("Error consultando DIAN para NMDOC=%s: %s", nmdoc, e)

    _cache[nmdoc] = resultado
    return resultado


def _consultar_dian(nmdoc: str, tpdoc: str) -> dict | None:
    """Implementación interna de la consulta Playwright contra MUISCA DIAN.

    Args:
        nmdoc: número de identificación.
        tpdoc: tipo de documento.
    Returns:
        dict con los campos encontrados, o None si no hay datos.
    """
    try:
        dv = str(calcular_dv_colombia(nmdoc))
    except ValueError:
        logger.warning("NMDOC=%s no tiene un NIT válido para calcular DV.", nmdoc)
        return None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # ---------------------------------------------------------- #
            # Navegación inicial
            # ---------------------------------------------------------- #
            page.goto(DIAN_URL, timeout=20000)
            page.wait_for_load_state("networkidle", timeout=15000)

            # ---------------------------------------------------------- #
            # Cerrar modal "AYUDA" si aparece
            # ---------------------------------------------------------- #
            try:
                page.wait_for_selector("text=AYUDA", timeout=3000)
                close_btn = page.locator(
                    "input[value='Cerrar'], button:has-text('Cerrar'), a:has-text('Cerrar')"
                ).first
                if close_btn.is_visible():
                    close_btn.click()
                    page.wait_for_timeout(500)
            except PlaywrightTimeoutError:
                pass  # El modal no apareció; continuar normalmente

            # ---------------------------------------------------------- #
            # Rellenar NIT
            # ---------------------------------------------------------- #
            nit_input = page.locator(
                "input[id$='nit'], input[name*='nit'], input[id*='nit']"
            ).first
            nit_input.wait_for(state="visible", timeout=10000)
            nit_input.fill(nmdoc)

            # ---------------------------------------------------------- #
            # Rellenar Dígito de Verificación
            # ---------------------------------------------------------- #
            dv_input = page.locator(
                "input[id$='dv'], input[name*='dv'], input[id*='dv']"
            ).first
            dv_input.wait_for(state="visible", timeout=5000)
            dv_input.fill(dv)

            # ---------------------------------------------------------- #
            # Hacer clic en Buscar
            # ---------------------------------------------------------- #
            buscar_btn = page.locator(
                "input[value='Buscar'], button:has-text('Buscar')"
            ).first
            buscar_btn.wait_for(state="visible", timeout=5000)
            buscar_btn.click()

            # Esperar a que la respuesta se renderice en la página
            page.wait_for_load_state("networkidle", timeout=15000)
            page.wait_for_timeout(1000)

            # ---------------------------------------------------------- #
            # Verificar modal de ERROR
            # ---------------------------------------------------------- #
            page_text = page.inner_text("body").lower()
            if "no corresponde" in page_text or "no es válido" in page_text:
                logger.debug("DIAN reportó NIT no válido para NMDOC=%s.", nmdoc)
                return None

            # ---------------------------------------------------------- #
            # Extraer campos según tipo de documento
            # ---------------------------------------------------------- #
            resultado: dict = {}

            if tpdoc == TPDOC_NATURAL:
                # Persona natural: AP1, AP2, NM1, NM2
                resultado.update(
                    _extraer_campo(page, "Primer Apellido", "ap1")
                )
                resultado.update(
                    _extraer_campo(page, "Segundo Apellido", "ap2")
                )
                resultado.update(
                    _extraer_campo(page, "Primer Nombre", "nm1")
                )
                resultado.update(
                    _extraer_campo(page, "Segundo Nombre", "nm2")
                )
            elif tpdoc == TPDOC_JURIDICA:
                # Persona jurídica: Razón Social
                resultado.update(
                    _extraer_campo(page, "Razón Social", "rz")
                )
            else:
                # Tipo desconocido: intentar ambos bloques de campos
                resultado.update(_extraer_campo(page, "Primer Apellido", "ap1"))
                resultado.update(_extraer_campo(page, "Segundo Apellido", "ap2"))
                resultado.update(_extraer_campo(page, "Primer Nombre", "nm1"))
                resultado.update(_extraer_campo(page, "Segundo Nombre", "nm2"))
                resultado.update(_extraer_campo(page, "Razón Social", "rz"))

            return resultado if resultado else None

        except PlaywrightTimeoutError:
            logger.warning("Timeout consultando DIAN para NMDOC=%s.", nmdoc)
            return None
        except Exception as e:
            logger.warning(
                "Error inesperado consultando DIAN para NMDOC=%s: %s", nmdoc, e
            )
            return None
        finally:
            browser.close()


def _extraer_campo(page, label_text: str, clave: str) -> dict:
    """
    Extrae el valor del campo del formulario de respuesta DIAN cuyo label
    contiene label_text.

    El formulario de respuesta de MUISCA usa tablas HTML donde cada fila
    tiene una celda de etiqueta y una celda de valor adyacente.  Se prueban
    varias estrategias de localización para cubrir variaciones del markup.

    Args:
        page: objeto Page de Playwright.
        label_text: texto visible del label en la tabla (p.ej. "Primer Apellido").
        clave: clave del dict de resultado (p.ej. "ap1").
    Returns:
        dict con {clave: valor} si se encontró un valor no vacío, {} en caso
        contrario.
    """
    valor = None

    # Estrategia 1: celda <td> o <th> con el texto del label seguida de
    # la celda hermana inmediata (selector CSS ~ td o + td)
    estrategias = [
        # La celda de valor está en el mismo <tr>, como hermana del <td> del label
        f"tr:has(td:text-is('{label_text}')) td:last-child",
        f"tr:has(th:text-is('{label_text}')) td:last-child",
        # Selector de hermano adyacente directo
        f"td:text-is('{label_text}') + td",
        f"th:text-is('{label_text}') + td",
        # Coincidencia parcial de texto (por si el label tiene espacios extra)
        f"tr:has-text('{label_text}') td:last-child",
    ]

    for selector in estrategias:
        try:
            locator = page.locator(selector).first
            if locator.count() == 0:
                continue
            # Intentar leer como input primero, luego como celda de texto
            tag = locator.evaluate("el => el.tagName.toLowerCase()")
            if tag == "input":
                raw = locator.input_value()
            else:
                raw = locator.inner_text()
            raw = raw.strip() if raw else ""
            if raw:
                valor = raw
                break
        except Exception:
            continue

    if valor:
        return {clave: valor}
    return {}


def limpiar_cache() -> None:
    """Limpia el caché de sesión.

    Debe llamarse al inicio de cada proceso ETL para garantizar que no se
    reutilicen resultados de ejecuciones anteriores.
    """
    _cache.clear()

"""Fase 2 ETL: Transformación y validación de terceros."""
import logging
from vite.config.settings import TIPO_ACTINF, TIPO_VALRES, TIPO_INFOOK, TPDOC_NATURAL, TPDOC_JURIDICA
from vite.db.repositories import config_repo, terceros_repo, log_repo
from vite.etl.rules import actinf_dv, actinf_tpdoc, actinf_nombres, actinf_direccion, valres
from vite.services.dian_scraper import consultar_tercero, limpiar_cache

logger = logging.getLogger(__name__)


def ejecutar(empresa_id: int, periodo_id: int, callback: callable = None) -> None:
    """Transforma y valida todos los terceros. Orden: ACTINF → VALRES → INFOOK."""

    # ------------------------------------------------------------------
    # Pre-carga en memoria (una sola consulta de cada recurso compartido)
    # ------------------------------------------------------------------
    nomenclaturas = config_repo.get_nomenclaturas()
    paises_validos = config_repo.get_paises_ids()
    pais_dpto_set = config_repo.get_pais_dpto_set()
    pais_dpto_mpio_set = config_repo.get_pais_dpto_mpio_set()
    limpiar_cache()

    terceros = terceros_repo.get_all_terceros(empresa_id, periodo_id)
    total = len(terceros)
    logger.info("Iniciando transformación: %d terceros.", total)

    # Precargar mapa de formatos por tercero: {nmdoc: [formato_id, ...]}
    formatos_map: dict[str, list[int]] = {}
    for t in terceros:
        nmdoc = t["nmdoc"]
        formatos_map[nmdoc] = terceros_repo.get_formatos_tercero(
            empresa_id, periodo_id, nmdoc
        )

    # Precargar cache de validaciones y campos_requeridos por formato_id
    # para evitar queries repetidas dentro del loop de terceros.
    formatos_distintos: set[int] = set()
    for formatos in formatos_map.values():
        formatos_distintos.update(formatos)

    _cache_formato: dict[int, tuple[list[str], dict[str, bool]]] = {}
    for fmt_id in formatos_distintos:
        validaciones_fmt = config_repo.get_validaciones_formato(fmt_id)
        campos_req = config_repo.get_campos_requeridos(fmt_id)
        _cache_formato[fmt_id] = (validaciones_fmt, campos_req)

    # ------------------------------------------------------------------
    # Loop principal
    # ------------------------------------------------------------------
    for idx, tercero in enumerate(terceros):
        nmdoc = tercero["nmdoc"]

        if callback:
            callback(f"Transformando {idx + 1}/{total}: NMDOC={nmdoc}")

        hubo_actinf = False
        hubo_valres = False

        # --- ACTINF 1: TPDOC ---
        cambio = actinf_tpdoc.aplicar_tpdoc(tercero)
        if cambio:
            terceros_repo.update_campos(empresa_id, periodo_id, nmdoc, cambio)
            log_repo.insert_log(
                empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                descripcion=(
                    f"TPDOC actualizado de '{tercero.get('tpdoc')}' "
                    f"a '{cambio['tpdoc']}'"
                ),
            )
            tercero.update(cambio)
            hubo_actinf = True

        # --- ACTINF 2: DV ---
        cambio = actinf_dv.aplicar_dv(tercero)
        if cambio:
            terceros_repo.update_campos(empresa_id, periodo_id, nmdoc, cambio)
            log_repo.insert_log(
                empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                descripcion=f"DV calculado automáticamente: {cambio['dv']}",
            )
            tercero.update(cambio)
            hubo_actinf = True

        # --- ACTINF 3: Dirección ---
        dir_original = tercero.get("dir")
        if dir_original:
            dir_nueva, normalizada = actinf_direccion.normalizar_direccion(
                dir_original, nomenclaturas
            )
            if normalizada and dir_nueva != dir_original:
                terceros_repo.update_campos(
                    empresa_id, periodo_id, nmdoc, {"dir": dir_nueva}
                )
                log_repo.insert_log(
                    empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                    descripcion="Dirección normalizada según nomenclaturas DIAN",
                )
                tercero["dir"] = dir_nueva
                hubo_actinf = True
            elif not normalizada and dir_original:
                log_repo.insert_log(
                    empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                    descripcion=(
                        "Alerta: dirección demasiado corta tras normalización (< 8 chars)"
                    ),
                )
                hubo_actinf = True

        # --- ACTINF 4: Nombres / Razón social ---
        cambio = actinf_nombres.redistribuir_nombres(tercero)
        if cambio:
            terceros_repo.update_campos(empresa_id, periodo_id, nmdoc, cambio)
            log_repo.insert_log(
                empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                descripcion=(
                    f"Campos de identificación redistribuidos según "
                    f"TPDOC={tercero.get('tpdoc')}"
                ),
            )
            tercero.update(cambio)
            hubo_actinf = True

        # --- ACTINF 5: Consulta DIAN ---
        if _necesita_consulta_dian(tercero):
            if callback:
                callback(f"Consultando DIAN para NMDOC={nmdoc}...")
            resultado = consultar_tercero(nmdoc, tercero.get("tpdoc", ""))
            if resultado:
                actualizaciones = {
                    k: v for k, v in resultado.items()
                    if v and not tercero.get(k)
                }
                if actualizaciones:
                    terceros_repo.update_campos(
                        empresa_id, periodo_id, nmdoc, actualizaciones
                    )
                    log_repo.insert_log(
                        empresa_id, periodo_id, nmdoc, TIPO_ACTINF,
                        descripcion=(
                            f"Datos completados desde DIAN: "
                            f"{list(actualizaciones.keys())}"
                        ),
                    )
                    tercero.update(actualizaciones)
                    hubo_actinf = True

        # --- VALRES ---
        for formato_id in formatos_map.get(nmdoc, []):
            validaciones_fmt, campos_req = _cache_formato.get(
                formato_id, ([], {})
            )

            errores = valres.ejecutar_validaciones(
                tercero=tercero,
                formato_id=formato_id,
                validaciones_formato=validaciones_fmt,
                campos_requeridos=campos_req,
                paises_validos=paises_validos,
                pais_dpto_set=pais_dpto_set,
                pais_dpto_mpio_set=pais_dpto_mpio_set,
            )
            for error in errores:
                log_repo.insert_log(
                    empresa_id, periodo_id, nmdoc, TIPO_VALRES,
                    codigo_validacion=error.codigo,
                    descripcion=f"[Formato {formato_id}] {error.descripcion}",
                )
                hubo_valres = True

        # --- INFOOK ---
        if not hubo_actinf and not hubo_valres:
            log_repo.insert_log(
                empresa_id, periodo_id, nmdoc, TIPO_INFOOK,
                descripcion=(
                    "Registro correcto: superó todas las validaciones sin intervención"
                ),
            )

    logger.info("Transformación finalizada: %d terceros procesados.", total)


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _necesita_consulta_dian(tercero: dict) -> bool:
    """
    Retorna True si el tercero requiere consulta a la DIAN para completar
    sus datos de identificación.

    - Persona natural (TPDOC_NATURAL): consulta si faltan primer apellido o
      primer nombre.
    - Persona jurídica (TPDOC_JURIDICA): consulta si falta la razón social.
    - Cualquier otro TPDOC: no consulta.
    """
    tpdoc = tercero.get("tpdoc")
    if tpdoc == TPDOC_NATURAL:
        return not (tercero.get("ap1") and tercero.get("nm1"))
    if tpdoc == TPDOC_JURIDICA:
        return not tercero.get("rz")
    return False

"""Fase 3 ETL: Generación del informe Excel de validaciones."""
from pathlib import Path
from datetime import datetime
from loguru import logger
from vite.etl import LoadError
from vite.db.repositories import log_repo, terceros_repo
from vite.services.excel_parser import write_report


def ejecutar(
    empresa_id: int,
    periodo_id: int,
    carpeta_salida: Path,
    callback: callable = None,
) -> Path:
    """
    Genera el informe Excel de validaciones ETL.

    Hoja 1 (siempre): log completo de acciones (ACTINF, VALRES, INFOOK).
    Hoja 2 (solo si no hay errores VALRES): datos validados de todos los
    terceros del período.

    Returns:
        Path del archivo generado.

    Raises:
        LoadError: si la escritura del archivo Excel falla.
    """
    logger.info(
        "FASE 3 — Generación de informe: empresa={}, periodo={}",
        empresa_id, periodo_id,
    )

    if callback:
        callback("Preparando datos del informe...")

    log_entries = log_repo.get_log_entries(empresa_id, periodo_id)
    terceros = terceros_repo.get_all_terceros(empresa_id, periodo_id)

    # Mapa rápido nmdoc → tpdoc para enriquecer el log
    tpdoc_map: dict[str, str | None] = {
        t["nmdoc"]: t.get("tpdoc") for t in terceros
    }

    # Hoja 1: una fila por entrada de log
    hoja1_data = [
        {
            "nmdoc": e["nmdoc"],
            "tpdoc": tpdoc_map.get(e["nmdoc"]),
            "tipo_accion": e["tipo_accion"],
            "codigo_validacion": e.get("codigo_validacion"),
            "descripcion": e.get("descripcion"),
        }
        for e in log_entries
    ]

    # Hoja 2: sólo si no existen errores VALRES
    tiene_errores = terceros_repo.has_valres_errors(empresa_id, periodo_id)
    hoja2_data = None if tiene_errores else terceros

    if callback:
        callback("Generando hoja 1: Informe de validaciones...")
        if not tiene_errores:
            callback("Sin errores VALRES — generando hoja 2: Datos validados...")
        else:
            callback("Hay errores VALRES — hoja 2 no se generará.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = carpeta_salida / f"Informe_validacion_terceros_{timestamp}.xlsx"

    try:
        write_report(output_path, hoja1_data, hoja2_data)
    except Exception as e:
        logger.error("Error escribiendo informe Excel: {}", e)
        raise LoadError(f"Error generando el informe Excel: {e}") from e

    logger.info("FASE 3 — Informe generado: {}", output_path)
    if callback:
        callback(f"Informe generado: {output_path.name}")

    return output_path

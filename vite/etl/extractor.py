"""Fase 1 ETL: Extracción de datos desde archivos Excel hacia PostgreSQL."""
from pathlib import Path
from loguru import logger
from vite.etl import ExtractionError
from vite.db.repositories import config_repo, terceros_repo
from vite.services.excel_parser import read_excel, extract_formato_from_filename


def ejecutar(
    empresa_id: int,
    periodo_id: int,
    archivos: list[Path],
    callback: callable = None,
) -> list[tuple[Path, int]]:
    """
    Extrae datos de archivos Excel y los carga en PostgreSQL.

    Raises ExtractionError si algún archivo no contiene un número de formato
    válido en su nombre, o si falta una columna requerida según la configuración
    de la empresa.

    Proceso en dos fases:
      FASE A — Valida estructura de TODOS los archivos antes de importar.
      FASE B — Importa sólo si la fase A no arrojó errores, ordenando por
                prioridad de formato.
    """
    # ------------------------------------------------------------------
    # FASE A: Validar estructura de todos los archivos
    # ------------------------------------------------------------------
    archivos_validados: list[tuple[Path, int, object]] = []

    logger.info(
        "FASE 1 — Extracción iniciada: empresa={}, periodo={}, archivos={}",
        empresa_id, periodo_id, [a.name for a in archivos],
    )

    for archivo in archivos:
        formato_id = extract_formato_from_filename(archivo.name)
        if formato_id is None:
            logger.error("Archivo sin formato válido en el nombre: {}", archivo.name)
            raise ExtractionError(
                f"'{archivo.name}' no contiene número de formato válido"
            )

        logger.debug("Leyendo archivo: {} (formato {})", archivo.name, formato_id)
        df = read_excel(archivo)

        campos_empresa = config_repo.get_campos_empresa(empresa_id)
        campos_req = config_repo.get_campos_requeridos(formato_id)

        for campo_id, aplica in campos_req.items():
            if aplica and campos_empresa.get(campo_id) not in df.columns:
                logger.error(
                    "Campo requerido '{}' no encontrado en {} (formato {})",
                    campos_empresa.get(campo_id), archivo.name, formato_id,
                )
                raise ExtractionError(
                    f"Campo '{campos_empresa.get(campo_id)}' no encontrado en "
                    f"Formato {formato_id}. Verifique la configuración de "
                    f"columnas para la empresa."
                )

        archivos_validados.append((archivo, formato_id, df))
        logger.debug("Estructura válida: {} (formato {})", archivo.name, formato_id)

    # ------------------------------------------------------------------
    # FASE B: Importar en orden de prioridad
    # ------------------------------------------------------------------
    prioridades = config_repo.get_prioridades()   # {formato_id: prioridad}
    archivos_validados.sort(key=lambda t: prioridades.get(t[1], 99))

    # Conjunto de campo_id en minúscula para filtrar columnas renombradas
    campos_empresa_global = config_repo.get_campos_empresa(empresa_id)
    campos_validos = {campo_id.lower() for campo_id in campos_empresa_global}

    resultado: list[tuple[Path, int]] = []

    for archivo, formato_id, df in archivos_validados:
        if callback:
            callback(f"Importando formato {formato_id}: {archivo.name}")

        # Construir mapa de renombrado: columna_empresa → campo_id_lower
        campos_empresa = config_repo.get_campos_empresa(empresa_id)
        renombrar_mapa = {
            empresa_campo: campo_id.lower()
            for campo_id, empresa_campo in campos_empresa.items()
        }

        # Renombrar sólo las columnas presentes en el mapa
        columnas_a_renombrar = {
            col: renombrar_mapa[col]
            for col in df.columns
            if col in renombrar_mapa
        }
        df = df.rename(columns=columnas_a_renombrar)

        registros_procesados = 0
        for _, fila in df.iterrows():
            # Conservar sólo campos canónicos (minúscula)
            fila_dict = {
                col: valor
                for col, valor in fila.items()
                if col in campos_validos
            }

            # Saltar filas sin NMDOC
            nmdoc = fila_dict.get("nmdoc")
            if not nmdoc:
                continue

            terceros_repo.upsert_tercero(empresa_id, periodo_id, fila_dict)
            terceros_repo.upsert_formato(empresa_id, periodo_id, fila_dict["nmdoc"], formato_id)
            registros_procesados += 1

        if callback:
            callback(f"Formato {formato_id}: {registros_procesados} registros procesados")

        logger.info(
            "Formato {} ({}): {} registros importados.",
            formato_id,
            archivo.name,
            registros_procesados,
        )
        resultado.append((archivo, formato_id))

    logger.info(
        "FASE 1 — Extracción completada: {} archivo(s) procesado(s).",
        len(resultado),
    )
    return resultado

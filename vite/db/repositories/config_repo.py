from vite.db.connection import get_connection, get_dict_cursor


def get_campos_empresa(empresa_id: int) -> dict[str, str]:
    """
    Retorna mapeo {campo_id: empresa_campo} para una empresa.
    Ej: {'TPDOC': 'Tipo de documento', 'NMDOC': 'Número de identificación', ...}
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT campo_id, empresa_campo"
            " FROM cfg_campos_terceros_empresas"
            " WHERE empresa_id = %s",
            (empresa_id,),
        )
        result = cur.fetchall()
        cur.close()
    return {row["campo_id"]: row["empresa_campo"] for row in result}


def get_campos_requeridos(formato_id: int) -> dict[str, bool]:
    """
    Retorna {campo_id: aplica(bool)} para un formato específico.
    Ej: {'TPDOC': True, 'NMDOC': True, 'DV': False, ...}
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT campo_id, aplica"
            " FROM cfg_campos_requeridos"
            " WHERE formato_id = %s",
            (formato_id,),
        )
        result = cur.fetchall()
        cur.close()
    return {row["campo_id"]: bool(row["aplica"]) for row in result}


def get_prioridades() -> dict[int, int]:
    """
    Retorna {formato_id: prioridad} para ordenar importación.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT formato_id, prioridad"
            " FROM cfg_prioridad_importacion"
            " ORDER BY prioridad"
        )
        result = cur.fetchall()
        cur.close()
    return {row["formato_id"]: row["prioridad"] for row in result}


def get_nomenclaturas() -> dict[str, list[str]]:
    """
    Retorna {nomenclatura_id: [palabras_clave]} — split por ',' del campo nomenclatura_palabras_clave.
    Ej: {'CR': ['Carrera', 'Crr', 'Carr'], 'AP': ['Apartamento', 'Aparta']}
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT nomenclatura_id, nomenclatura_palabras_clave FROM cfg_nomenclatura"
        )
        result = cur.fetchall()
        cur.close()
    return {
        row["nomenclatura_id"]: [
            w.strip() for w in row["nomenclatura_palabras_clave"].split(",")
        ]
        for row in result
        if row["nomenclatura_palabras_clave"]
    }


def get_validaciones_formato(formato_id: int) -> list[str]:
    """
    Retorna lista de códigos de validación para un formato.
    Ej: ['VAL_TPDOC_01', 'VAL_TPDOC_02', 'VAL_DIR_01']
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT codigo FROM cfg_validaciones_formatos WHERE formato_id = %s",
            (formato_id,),
        )
        result = cur.fetchall()
        cur.close()
    return [row["codigo"] for row in result]


def get_paises_ids() -> set[str]:
    """
    Retorna set de pais_id válidos.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute("SELECT pais_id FROM cfg_paises")
        result = cur.fetchall()
        cur.close()
    return {row["pais_id"] for row in result}


def get_pais_dpto_set() -> set[tuple[str, str]]:
    """
    Retorna set de tuplas (pais_id, dpto_id) válidas.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute("SELECT DISTINCT pais_id, dpto_id FROM cfg_geografia")
        result = cur.fetchall()
        cur.close()
    return {(row["pais_id"], row["dpto_id"]) for row in result}


def get_pais_dpto_mpio_set() -> set[tuple[str, str, str]]:
    """
    Retorna set de tuplas (pais_id, dpto_id, mpio_id) válidas.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute("SELECT pais_id, dpto_id, mpio_id FROM cfg_geografia")
        result = cur.fetchall()
        cur.close()
    return {(row["pais_id"], row["dpto_id"], row["mpio_id"]) for row in result}

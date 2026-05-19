from vite.db.connection import get_connection, get_dict_cursor


def insert_log(
    empresa_id: int,
    periodo_id: int,
    nmdoc: str,
    tipo_accion: str,
    codigo_validacion: str | None = None,
    descripcion: str | None = None,
) -> None:
    """
    Inserta un registro de log ETL.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            """
            INSERT INTO mov_terceros_log
                (empresa_id, periodo_id, nmdoc, tipo_accion, codigo_validacion, descripcion)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (empresa_id, periodo_id, nmdoc, tipo_accion, codigo_validacion, descripcion),
        )
        cur.close()


def get_log_entries(empresa_id: int, periodo_id: int) -> list[dict]:
    """
    Retorna todos los logs para empresa+periodo, ordenados por ts ASC.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT * FROM mov_terceros_log"
            " WHERE empresa_id = %s AND periodo_id = %s"
            " ORDER BY ts",
            (empresa_id, periodo_id),
        )
        result = cur.fetchall()
        cur.close()
    return [dict(row) for row in result]


def get_log_by_tipo(empresa_id: int, periodo_id: int, tipo_accion: str) -> list[dict]:
    """
    Filtra logs por tipo_accion.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT * FROM mov_terceros_log"
            " WHERE empresa_id = %s AND periodo_id = %s AND tipo_accion = %s"
            " ORDER BY ts",
            (empresa_id, periodo_id, tipo_accion),
        )
        result = cur.fetchall()
        cur.close()
    return [dict(row) for row in result]


def delete_log_by_empresa_periodo(empresa_id: int, periodo_id: int) -> None:
    """
    Elimina todos los logs de un proceso (para re-ejecución limpia).
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "DELETE FROM mov_terceros_log WHERE empresa_id = %s AND periodo_id = %s",
            (empresa_id, periodo_id),
        )
        cur.close()

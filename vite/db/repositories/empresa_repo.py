from vite.db.connection import get_connection, get_dict_cursor


def get_all() -> list[dict]:
    """Retorna todas las empresas [{empresa_id, empresa_desc}]"""
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT empresa_id, empresa_desc FROM cfg_empresa ORDER BY empresa_id"
        )
        result = cur.fetchall()
        cur.close()
    return [dict(row) for row in result]


def get_by_id(empresa_id: int) -> dict | None:
    """Retorna empresa por ID o None"""
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT empresa_id, empresa_desc FROM cfg_empresa WHERE empresa_id = %s",
            (empresa_id,),
        )
        row = cur.fetchone()
        cur.close()
    return dict(row) if row is not None else None

from vite.db.connection import get_connection, get_dict_cursor

# Campos válidos para UPDATE dinámico (nmdoc es la PK, no se actualiza)
_CAMPOS_VALIDOS = frozenset(
    {"tpdoc", "dv", "ap1", "ap2", "nm1", "nm2", "rz", "dir", "dpto", "mpio", "pais"}
)


def upsert_tercero(empresa_id: int, periodo_id: int, campos: dict) -> None:
    """
    Inserta un tercero. Si ya existe (mismo empresa_id+periodo_id+nmdoc), no hace nada.
    campos: dict con claves en minúscula {tpdoc, nmdoc, dv, ap1, ap2, nm1, nm2, rz, dir, dpto, mpio, pais}
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            """
            INSERT INTO mov_terceros_importados
                (empresa_id, periodo_id, tpdoc, nmdoc, dv, ap1, ap2, nm1, nm2, rz, dir, dpto, mpio, pais)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (
                empresa_id,
                periodo_id,
                campos.get("tpdoc"),
                campos.get("nmdoc"),
                campos.get("dv"),
                campos.get("ap1"),
                campos.get("ap2"),
                campos.get("nm1"),
                campos.get("nm2"),
                campos.get("rz"),
                campos.get("dir"),
                campos.get("dpto"),
                campos.get("mpio"),
                campos.get("pais"),
            ),
        )
        cur.close()


def upsert_formato(empresa_id: int, periodo_id: int, nmdoc: str, formato: int) -> None:
    """
    Inserta asociación tercero-formato. Ignora si ya existe.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            """
            INSERT INTO mov_terceros_importados_formato
                (empresa_id, periodo_id, nmdoc, formato)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (empresa_id, periodo_id, nmdoc, formato),
        )
        cur.close()


def get_all_terceros(empresa_id: int, periodo_id: int) -> list[dict]:
    """
    Retorna todos los terceros de empresa+periodo.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT * FROM mov_terceros_importados"
            " WHERE empresa_id = %s AND periodo_id = %s",
            (empresa_id, periodo_id),
        )
        result = cur.fetchall()
        cur.close()
    return [dict(row) for row in result]


def get_formatos_tercero(empresa_id: int, periodo_id: int, nmdoc: str) -> list[int]:
    """
    Retorna los formatos asociados a un tercero específico.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT formato FROM mov_terceros_importados_formato"
            " WHERE empresa_id = %s AND periodo_id = %s AND nmdoc = %s",
            (empresa_id, periodo_id, nmdoc),
        )
        result = cur.fetchall()
        cur.close()
    return [row["formato"] for row in result]


def update_campos(empresa_id: int, periodo_id: int, nmdoc: str, cambios: dict) -> None:
    """
    Actualiza campos específicos de un tercero.

    cambios: dict con claves en minúscula. Solo actualiza campos en _CAMPOS_VALIDOS.
    Construye el SET clause dinámicamente.
    Si cambios está vacío (o ningún campo es válido) → return sin hacer nada.
    """
    campos_filtrados = {k: v for k, v in cambios.items() if k in _CAMPOS_VALIDOS}
    if not campos_filtrados:
        return

    set_clause = ", ".join(f"{campo} = %s" for campo in campos_filtrados)
    valores = list(campos_filtrados.values())
    valores.extend([empresa_id, periodo_id, nmdoc])

    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            f"UPDATE mov_terceros_importados"
            f" SET {set_clause}"
            f" WHERE empresa_id = %s AND periodo_id = %s AND nmdoc = %s",
            valores,
        )
        cur.close()


def has_valres_errors(empresa_id: int, periodo_id: int) -> bool:
    """
    True si existe al menos un log con tipo_accion='VALRES' para empresa+periodo.
    """
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "SELECT EXISTS("
            "  SELECT 1 FROM mov_terceros_log"
            "  WHERE empresa_id = %s AND periodo_id = %s AND tipo_accion = 'VALRES'"
            ")",
            (empresa_id, periodo_id),
        )
        row = cur.fetchone()
        cur.close()
    return bool(row["exists"])

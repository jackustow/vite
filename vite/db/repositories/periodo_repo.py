from vite.db.connection import get_connection, get_dict_cursor


def get_all() -> list[int]:
    """Retorna todos los períodos ordenados descendentemente (ej: [2026, 2025, 2024])"""
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute("SELECT periodo_id FROM cfg_periodo ORDER BY periodo_id DESC")
        result = cur.fetchall()
        cur.close()
    return [row["periodo_id"] for row in result]


def create(year: int) -> None:
    """Crea un nuevo período si no existe"""
    with get_connection() as conn:
        cur = get_dict_cursor(conn)
        cur.execute(
            "INSERT INTO cfg_periodo (periodo_id) VALUES (%s) ON CONFLICT DO NOTHING",
            (year,),
        )
        cur.close()

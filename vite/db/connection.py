import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from vite.config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, DB_MIN_CONN, DB_MAX_CONN

_pool: pool.ThreadedConnectionPool | None = None


def _get_pool() -> pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        _pool = pool.ThreadedConnectionPool(
            DB_MIN_CONN, DB_MAX_CONN,
            host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
            user=DB_USER, password=DB_PASSWORD
        )
    return _pool


@contextmanager
def get_connection():
    conn = _get_pool().getconn()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        _get_pool().putconn(conn)


def get_dict_cursor(conn):
    return conn.cursor(cursor_factory=RealDictCursor)

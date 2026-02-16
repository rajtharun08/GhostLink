import sqlite3
from contextlib import contextmanager

DB_FILE = "ghostlink.db"

@contextmanager
def get_db():
    """Provides a temporary sqlite3 connection and closes it automatically."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()
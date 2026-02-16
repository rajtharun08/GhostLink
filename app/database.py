import sqlite3
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()
DB_FILE = os.getenv("DATABASE_URL", "ghostlink.db")

@contextmanager
def get_db():
    """Provides a temporary sqlite3 connection and closes it automatically."""
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Manually creates the tables using the schema.sql file."""
    with get_db() as conn:
        with open("app/schema.sql", "r") as f:
            conn.executescript(f.read())
        conn.commit()
    print("GhostLink database ({DB_FILE}) is ready.")
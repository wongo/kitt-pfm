"""SQLite database connection and initialization."""
import aiosqlite
import sqlite3
from pathlib import Path
from .schema import SCHEMA

DB_PATH: Path = None

async def init_db(db_path: Path):
    """Create tables if they don't exist."""
    global DB_PATH
    DB_PATH = db_path
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA)
        await db.commit()

def get_db_path() -> Path:
    return DB_PATH

def init_db_sync(db_path: Path):
    """Synchronous DB init for first-run."""
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()

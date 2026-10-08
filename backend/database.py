import os
import sqlite3
from pathlib import Path

DATABASE_URL = os.environ.get("DATABASE_URL")

# Si DATABASE_URL usa postgres:// (formato heredado de Render), cambiar a postgresql://
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

DB_FILE = Path(__file__).resolve().parent / "inventario.db"

class DatabaseAdapter:
    def __init__(self):
        self.is_postgres = bool(DATABASE_URL)
        
    def get_connection(self):
        if self.is_postgres:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        else:
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            return conn

    def placeholder(self):
        return "%s" if self.is_postgres else "?"

db_adapter = DatabaseAdapter()

def get_db_connection():
    return db_adapter.get_connection()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if db_adapter.is_postgres:
        # PostgreSQL syntax
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            quantity DOUBLE PRECISION NOT NULL DEFAULT 0,
            unit VARCHAR(50) NOT NULL,
            min_stock DOUBLE PRECISION DEFAULT 2,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
    else:
        # SQLite syntax
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT NOT NULL,
            min_stock REAL DEFAULT 2,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)

    # NO sembramos ningún producto por defecto. El inventario solo contendrá lo que tú agregues.
    conn.commit()
    conn.close()

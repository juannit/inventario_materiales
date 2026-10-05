import sqlite3
from pathlib import Path

DB_FILE = Path(__file__).parent / "inventario.db"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de materiales
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

    # Tabla de historial de movimientos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id INTEGER,
        change_amount REAL NOT NULL,
        previous_quantity REAL NOT NULL,
        new_quantity REAL NOT NULL,
        reason TEXT DEFAULT 'Ajuste rápido',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (material_id) REFERENCES materials (id) ON DELETE CASCADE
    );
    """)
    
    # Sembrar datos de ejemplo basados en el diseño del usuario si la tabla está vacía
    cursor.execute("SELECT COUNT(*) as count FROM materials")
    if cursor.fetchone()["count"] == 0:
        initial_items = [
            ("Cartulina", "Papelería", 15.0, "unidades", 5.0, "Cartulinas de colores variados"),
            ("Pinceles", "Pintura", 12.0, "unidades", 3.0, "Pinceles planos y redondos surtidos"),
            ("Cinta decorativa", "Manualidades", 8.0, "metros", 2.0, "Cinta washi tape dorada"),
            ("MDF", "Materiales", 3.0, "láminas", 1.0, "Planchas de MDF 3mm 60x40cm"),
            ("Papel Kraft", "Papelería", 25.0, "pliegos", 5.0, "Pliegos Kraft 80gr"),
            ("Alambre de cobre", "Manualidades", 150.0, "centímetros", 30.0, "Grosor 1mm para modelado"),
            ("Pintura Acrílica", "Pintura", 6.0, "botes", 2.0, "Colores primarios 250ml")
        ]
        cursor.executemany("""
            INSERT INTO materials (name, category, quantity, unit, min_stock, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, initial_items)
        conn.commit()
        
    conn.commit()
    conn.close()

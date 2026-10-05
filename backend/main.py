import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import get_db_connection, init_db

app = FastAPI(title="Sistema de Inventario para Diseño y Papelería")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar DB al cargar el módulo
init_db()

@app.on_event("startup")
def on_startup():
    init_db()

# Esquemas Pydantic
class MaterialBase(BaseModel):
    name: str = Field(..., min_length=1, description="Nombre del material")
    category: str = Field(..., min_length=1, description="Categoría")
    quantity: float = Field(ge=0, description="Cantidad disponible")
    unit: str = Field(..., min_length=1, description="Unidad de medida (láminas, metros, unidades, etc.)")
    min_stock: Optional[float] = Field(default=2.0, ge=0, description="Stock mínimo de alerta")
    notes: Optional[str] = Field(default="", description="Notas o especificaciones")

class MaterialCreate(MaterialBase):
    pass

class MaterialUpdate(MaterialBase):
    pass

class StockAdjust(BaseModel):
    delta: float = Field(..., description="Cantidad a sumar o restar (positivo o negativo)")
    reason: Optional[str] = Field(default="Ajuste manual", description="Motivo del ajuste")

# Rutas API
@app.get("/api/materials")
def list_materials(search: Optional[str] = None, category: Optional[str] = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM materials WHERE 1=1"
    params = []
    
    if search:
        query += " AND (name LIKE ? OR notes LIKE ? OR category LIKE ?)"
        term = f"%{search}%"
        params.extend([term, term, term])
        
    if category and category.lower() != "todas":
        query += " AND category = ?"
        params.append(category)
        
    query += " ORDER BY category ASC, name ASC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]

@app.get("/api/materials/{material_id}")
def get_material(material_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return dict(row)

@app.post("/api/materials", status_code=201)
def create_material(material: MaterialCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO materials (name, category, quantity, unit, min_stock, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (material.name.strip(), material.category.strip(), material.quantity, material.unit.strip(), material.min_stock, material.notes.strip()))
    new_id = cursor.lastrowid
    
    # Registrar log inicial
    cursor.execute("""
        INSERT INTO inventory_logs (material_id, change_amount, previous_quantity, new_quantity, reason)
        VALUES (?, ?, 0, ?, 'Creación de material')
    """, (new_id, material.quantity, material.quantity))
    
    conn.commit()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (new_id,))
    new_material = dict(cursor.fetchone())
    conn.close()
    return new_material

@app.put("/api/materials/{material_id}")
def update_material(material_id: int, material: MaterialUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantity FROM materials WHERE id = ?", (material_id,))
    prev = cursor.fetchone()
    if not prev:
        conn.close()
        raise HTTPException(status_code=404, detail="Material no encontrado")
    
    prev_qty = prev["quantity"]
    
    cursor.execute("""
        UPDATE materials 
        SET name = ?, category = ?, quantity = ?, unit = ?, min_stock = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (material.name.strip(), material.category.strip(), material.quantity, material.unit.strip(), material.min_stock, material.notes.strip(), material_id))
    
    if prev_qty != material.quantity:
        cursor.execute("""
            INSERT INTO inventory_logs (material_id, change_amount, previous_quantity, new_quantity, reason)
            VALUES (?, ?, ?, ?, 'Edición de información')
        """, (material_id, material.quantity - prev_qty, prev_qty, material.quantity))
        
    conn.commit()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    return updated

@app.patch("/api/materials/{material_id}/adjust")
def adjust_stock(material_id: int, adjust: StockAdjust):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT quantity FROM materials WHERE id = ?", (material_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Material no encontrado")
        
    current_qty = row["quantity"]
    new_qty = max(0.0, round(current_qty + adjust.delta, 2))
    
    cursor.execute("""
        UPDATE materials SET quantity = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?
    """, (new_qty, material_id))
    
    cursor.execute("""
        INSERT INTO inventory_logs (material_id, change_amount, previous_quantity, new_quantity, reason)
        VALUES (?, ?, ?, ?, ?)
    """, (material_id, round(new_qty - current_qty, 2), current_qty, new_qty, adjust.reason))
    
    conn.commit()
    cursor.execute("SELECT * FROM materials WHERE id = ?", (material_id,))
    updated = dict(cursor.fetchone())
    conn.close()
    return updated

@app.delete("/api/materials/{material_id}")
def delete_material(material_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Material no encontrado")
    return {"message": "Material eliminado con éxito"}

@app.get("/api/categories")
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM materials ORDER BY category ASC")
    rows = cursor.fetchall()
    conn.close()
    base_cats = ["Papelería", "Pintura", "Manualidades", "Materiales", "Herramientas", "Textil", "Otros"]
    existing_cats = [r["category"] for r in rows if r["category"]]
    # Unir manteniendo orden
    all_cats = list(dict.fromkeys(base_cats + existing_cats))
    return all_cats

@app.get("/api/units")
def get_units():
    return [
        {"id": "unidades", "label": "Unidades / Piezas", "step": 1, "is_decimal": False},
        {"id": "láminas", "label": "Láminas / Placas", "step": 1, "is_decimal": False},
        {"id": "pliegos", "label": "Pliegos", "step": 1, "is_decimal": False},
        {"id": "metros", "label": "Metros (m)", "step": 0.5, "is_decimal": True},
        {"id": "centímetros", "label": "Centímetros (cm)", "step": 10, "is_decimal": False},
        {"id": "rollos", "label": "Rollos", "step": 1, "is_decimal": False},
        {"id": "cajas", "label": "Cajas / Paquetes", "step": 1, "is_decimal": False},
        {"id": "botes", "label": "Botes / Frascos", "step": 1, "is_decimal": False},
        {"id": "gramos", "label": "Gramos (g)", "step": 50, "is_decimal": False},
        {"id": "kilos", "label": "Kilogramos (kg)", "step": 0.5, "is_decimal": True},
        {"id": "litros", "label": "Litros (L)", "step": 0.5, "is_decimal": True}
    ]

@app.get("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total_items, SUM(quantity) as total_units FROM materials")
    total_row = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(*) as low_stock FROM materials WHERE quantity <= min_stock")
    low_row = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(DISTINCT category) as total_categories FROM materials")
    cat_row = cursor.fetchone()
    
    conn.close()
    return {
        "total_materials": total_row["total_items"] or 0,
        "low_stock_count": low_row["low_stock"] or 0,
        "total_categories": cat_row["total_categories"] or 0
    }

# Servir archivos estáticos del frontend
frontend_dir = Path(__file__).parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

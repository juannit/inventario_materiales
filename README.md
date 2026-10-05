# 🎨 Sistema de Inventario para Materiales y Objetos de Diseño

Sistema de inventario digital diseñado específicamente para talleres de diseño, papelerías y artesanos, con soporte para múltiples tipos de unidades de medida (láminas, metros, centímetros, unidades, pliegos, etc.).

## 🚀 Cómo Ejecutar el Proyecto

Desde una terminal en esta carpeta:

```bash
python run.py
```

Esto iniciará el servidor backend y abrirá automáticamente la aplicación en tu navegador web en:
👉 `http://localhost:8000`

---

## 🛠️ Estructura del Proyecto

```
inventario_papeleria/
├── backend/
│   ├── main.py          # API REST con FastAPI (CRUD, ajustes rápidos, filtros)
│   ├── database.py      # Base de datos SQLite y semillas iniciales
│   └── inventario.db    # Base de datos SQLite persistente
├── frontend/
│   └── index.html       # Interfaz visual interactiva (Tailwind CSS + Alpine.js + Lucide)
├── run.py               # Script de inicio rápido
└── README.md
```

---

## ✨ Características Implementadas

1. **Selector de Unidades de Medida**:
   - Conteo: *Unidades, Láminas, Pliegos, Rollos, Cajas, Botes*.
   - Longitud continua: *Metros (m), Centímetros (cm)*.
   - Peso y Volumen: *Gramos (g), Kilogramos (kg), Litros (L)*.
2. **Ajuste Rápido de Stock**:
   - Botones `+` y `-` adaptados a la unidad de medida.
3. **Buscador y Filtros en Tiempo Real**:
   - Búsqueda por texto libre y chips de categorías (*Papelería*, *Pintura*, *Manualidades*, *Materiales*, etc.).
4. **Alertas de Stock Bajo**:
   - Indicadores visuales cuando la cantidad actual es menor o igual al umbral mínimo.
5. **Historial de Movimientos**:
   - Registro automático de cada cambio en la base de datos SQLite.

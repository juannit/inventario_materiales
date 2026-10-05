import uvicorn
import webbrowser
import threading
import time
import sys
import os
import socket
from pathlib import Path

# Añadir backend al path
backend_dir = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_dir))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://localhost:8000")

if __name__ == "__main__":
    local_ip = get_local_ip()
    port = int(os.environ.get("PORT", 8000))

    print("=================================================================")
    print("  ATELIER HADA - SISTEMA DE INVENTARIO DISPONIBLE")
    print(f"  En tu computadora:       http://localhost:{port}")
    print(f"  Desde otros celulares/PC: http://{local_ip}:{port}")
    print("=================================================================")
    
    # Iniciar navegador en segundo plano solo en entorno local
    if "PORT" not in os.environ:
        threading.Thread(target=open_browser, daemon=True).start()
    
    # Iniciar FastAPI con Uvicorn escuchando en toda la red (0.0.0.0)
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False, app_dir=str(backend_dir))

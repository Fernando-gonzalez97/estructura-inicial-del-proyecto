"""
Utilidades para manejo de archivos
"""
import json
import os
from datetime import datetime
from config import HEARTBEAT_FILE, LOG_FILE

def guardar_heartbeat(datos):
    """Guardar heartbeat en archivo"""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            json.dump(datos, f, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando heartbeat: {e}")
        return False

def cargar_heartbeat():
    """Cargar último heartbeat"""
    try:
        if os.path.exists(HEARTBEAT_FILE):
            with open(HEARTBEAT_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error cargando heartbeat: {e}")
    return None

def log_evento(mensaje):
    """Registrar evento en log"""
    from datetime import timezone, timedelta
    argentina_tz = timezone(timedelta(hours=-3))
    timestamp = datetime.now(argentina_tz).strftime("%Y-%m-%d %H:%M:%S")
    
    log_msg = f"[{timestamp}] {mensaje}\n"
    
    try:
        os.makedirs("../logs", exist_ok=True)
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg)
    except Exception as e:
        print(f"Error escribiendo log: {e}")
    
    print(log_msg.strip())
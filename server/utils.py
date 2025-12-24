 """Guardar heartbeat en archivo"""
    try:
        with open(HEARTBEAT_FILE, 'w') as f:
            json.dump(datos, f, indent=2)
        return True
    except Exception as e:
        print(f"Error guardando heartbeat: {e}")
        return False

def log_evento(mensaje):
    """Registrar evento en log"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {mensaje}\n"
    
    try:
        # Crear carpeta logs si no existe
        os.makedirs("../logs", exist_ok=True)
        
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(log_msg)
    except Exception as e:
        print(f"Error escribiendo log: {e}")
    
    # También imprimir en consola
    print(log_msg.strip())
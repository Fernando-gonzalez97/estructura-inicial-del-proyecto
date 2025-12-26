"""
Monitor de conexión del servidor
Detecta desconexiones y envía alertas
"""

import time
from datetime import datetime
from config import MAX_HEARTBEAT_TIMEOUT
from utils import cargar_heartbeat, log_evento
from telegram_bot import enviar_alerta

# Variable global para rastrear alertas
alerta_desconexion_enviada = False

def monitor_conexion():
    """
    Monitorear conexión y enviar alertas si se desconecta
    Esta función corre en un hilo separado
    """
    global alerta_desconexion_enviada
    
    while True:
        time.sleep(60)  # Chequear cada 60 segundos
        
        ultimo = cargar_heartbeat()
        
        if ultimo:
            hace = int((datetime.now().timestamp() - ultimo['timestamp']))
            
            # Si pasaron más de MAX_HEARTBEAT_TIMEOUT sin señal
            if hace > MAX_HEARTBEAT_TIMEOUT:
                if not alerta_desconexion_enviada:
                    # Enviar alerta de desconexión
                    timestamp_ultimo = datetime.fromtimestamp(ultimo['timestamp'])
                    tiempo_str = timestamp_ultimo.strftime("%Y-%m-%d %H:%M:%S")
                    minutos = hace // 60
                    
                    mensaje = (
                        f"🔌 ALERTA: PC DESCONECTADA\n\n"
                        f"Monitor Radio 97.7 no responde\n"
                        f"Última señal: {tiempo_str}\n"
                        f"Hace: {minutos} minuto(s)"
                    )
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 Alerta de desconexión enviada a Telegram")
                    
                    alerta_desconexion_enviada = True
            else:
                # Si volvió la conexión, resetear flag
                if alerta_desconexion_enviada:
                    mensaje = (
                        f"✅ RECONEXIÓN EXITOSA\n\n"
                        f"Monitor Radio 97.7 volvió a responder"
                    )
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 Alerta de reconexión enviada a Telegram")
                    
                    alerta_desconexion_enviada = False

def resetear_alerta():
    """Resetear flag de alerta cuando llega un heartbeat"""
    global alerta_desconexion_enviada
    
    # Si estaba desconectado, enviar mensaje de reconexión
    if alerta_desconexion_enviada:
        mensaje = (
            f"✅ RECONEXIÓN EXITOSA\n\n"
            f"Monitor Radio 97.7 volvió a responder"
        )
        
        if enviar_alerta(mensaje):
            log_evento("📤 Alerta de reconexión enviada a Telegram")
        
        alerta_desconexion_enviada = False
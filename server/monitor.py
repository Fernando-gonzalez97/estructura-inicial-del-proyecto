"""
Monitor de conexión del servidor
Detecta desconexiones y silencios, envía alertas
"""

import time
from datetime import datetime, timezone, timedelta
from config import MAX_HEARTBEAT_TIMEOUT, MONITOR_CHECK_INTERVAL, MIN_SILENCE_DURATION
from utils import cargar_heartbeat, log_evento
from telegram_bot import enviar_alerta

# Variables globales para rastrear alertas
alerta_desconexion_enviada = False
alerta_silencio_enviada = False
tiempo_inicio_silencio = None
contador_chequeos = 0

# Zona horaria Argentina
ARGENTINA_TZ = timezone(timedelta(hours=-3))

def formatear_fecha_argentina(timestamp):
    """Convertir timestamp a formato Argentina"""
    dt = datetime.fromtimestamp(timestamp, tz=ARGENTINA_TZ)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def monitor_conexion():
    """
    Monitorear conexión y silencio, enviar alertas
    Esta función corre en un hilo separado
    """
    global alerta_desconexion_enviada, alerta_silencio_enviada
    global tiempo_inicio_silencio, contador_chequeos
    
    log_evento("🔍 Monitor de conexión INICIADO")
    log_evento(f"⏱️ Timeout desconexión: {MAX_HEARTBEAT_TIMEOUT}s")
    log_evento(f"🔇 Timeout silencio: {MIN_SILENCE_DURATION}s")
    log_evento(f"🔄 Intervalo de chequeo: {MONITOR_CHECK_INTERVAL}s")
    
    while True:
        time.sleep(MONITOR_CHECK_INTERVAL)
        
        contador_chequeos += 1
        
        ultimo = cargar_heartbeat()
        
        if ultimo:
            ahora = datetime.now(timezone.utc).timestamp()
            hace = int(ahora - ultimo['timestamp'])
            
            # Log cada 10 chequeos (cada 5 minutos aprox)
            if contador_chequeos % 10 == 0:
                log_evento(f"💓 Monitor activo - Último heartbeat hace {hace}s")
            
            # ==========================================
            # CHEQUEO 1: DESCONEXIÓN (PC apagada)
            # ==========================================
            if hace > MAX_HEARTBEAT_TIMEOUT:
                if not alerta_desconexion_enviada:
                    minutos = hace // 60
                    fecha_ultima = formatear_fecha_argentina(ultimo['timestamp'])
                    
                    mensaje = (
                        f"🔴 ALERTA: PC DESCONECTADA\n\n"
                        f"📻 Monitor Radio 97.7 no responde\n"
                        f"🕐 Última señal: {fecha_ultima}\n"
                        f"⏱️ Hace: {minutos} minuto(s)"
                    )
                    
                    log_evento(f"🚨 PC DESCONECTADA - Sin señal hace {minutos} min")
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 ✅ Alerta de DESCONEXIÓN enviada")
                        alerta_desconexion_enviada = True
                    else:
                        log_evento("📤 ❌ ERROR: No se pudo enviar alerta")
                    
                    # Resetear silencio ya que no hay conexión
                    alerta_silencio_enviada = False
                    tiempo_inicio_silencio = None
            
            # ==========================================
            # CHEQUEO 2: PC CONECTADA
            # ==========================================
            else:
                # Si estaba desconectada y volvió
                if alerta_desconexion_enviada:
                    mensaje = (
                        f"✅ PC RESTAURADA EN LÍNEA NUEVAMENTE\n\n"
                        f"📻 Monitor Radio 97.7 FM\n"
                        f"🟢 Conexión restablecida"
                    )
                    
                    log_evento("🎉 PC RECONECTADA")
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 ✅ Alerta de RECONEXIÓN enviada")
                    
                    alerta_desconexion_enviada = False
                
                # ==========================================
                # CHEQUEO 3: SILENCIO (PC conectada pero sin audio)
                # ==========================================
                is_silent = ultimo.get('is_silent', False)
                
                if is_silent:
                    # Marcar inicio de silencio si es la primera vez
                    if tiempo_inicio_silencio is None:
                        tiempo_inicio_silencio = ultimo['timestamp']
                        log_evento("🔇 Silencio detectado, iniciando conteo...")
                    
                    # Calcular duración del silencio
                    duracion_silencio = int(ahora - tiempo_inicio_silencio)
                    
                    # Si supera el tiempo mínimo y no se envió alerta
                    if duracion_silencio >= MIN_SILENCE_DURATION and not alerta_silencio_enviada:
                        fecha_inicio = formatear_fecha_argentina(tiempo_inicio_silencio)
                        
                        mensaje = (
                            f"🔇 ALERTA: Silencio detectado\n\n"
                            f"📻 Monitor Radio 97.7 FM\n"
                            f"🕐 Inicio: {fecha_inicio}\n"
                            f"⏱️ Duración: {duracion_silencio}s"
                        )
                        
                        log_evento(f"🔇 SILENCIO PROLONGADO - Duración: {duracion_silencio}s")
                        
                        if enviar_alerta(mensaje):
                            log_evento("📤 ✅ Alerta de SILENCIO enviada")
                            alerta_silencio_enviada = True
                        else:
                            log_evento("📤 ❌ ERROR: No se pudo enviar alerta de silencio")
                
                else:
                    # Si había silencio y ahora volvió el audio
                    if alerta_silencio_enviada:
                        fecha_restauracion = formatear_fecha_argentina(ultimo['timestamp'])
                        
                        mensaje = (
                            f"🔊 Audio restaurado\n\n"
                            f"📻 Monitor Radio 97.7 FM\n"
                            f"🕐 Restaurado: {fecha_restauracion}\n"
                            f"✅ Audio transmitiendo normalmente"
                        )
                        
                        log_evento("🔊 AUDIO RESTAURADO")
                        
                        if enviar_alerta(mensaje):
                            log_evento("📤 ✅ Alerta de audio restaurado enviada")
                        
                        alerta_silencio_enviada = False
                    
                    # Resetear contador de silencio
                    tiempo_inicio_silencio = None
        
        else:
            # No hay ningún heartbeat guardado
            if contador_chequeos % 5 == 0:
                log_evento("⚠️ Sin datos de heartbeat - Esperando primera señal...")

def resetear_alerta():
    """Resetear flag de alerta cuando llega un heartbeat"""
    global alerta_desconexion_enviada
    
    # Si estaba desconectado, enviar mensaje de reconexión
    if alerta_desconexion_enviada:
        mensaje = (
            f"✅ PC RESTAURADA EN LÍNEA NUEVAMENTE\n\n"
            f"📻 Monitor Radio 97.7 FM\n"
            f"🟢 Conexión restablecida"
        )
        
        log_evento("🎉 PC RECONECTADA por heartbeat")
        
        if enviar_alerta(mensaje):
            log_evento("📤 ✅ Alerta de RECONEXIÓN enviada")
        
        alerta_desconexion_enviada = False
"""
Monitor de conexión del servidor
Detecta desconexiones y silencios, envía alertas
"""

import time
from datetime import datetime, timezone, timedelta
from config import MAX_HEARTBEAT_TIMEOUT, MONITOR_CHECK_INTERVAL, MIN_SILENCE_DURATION
from utils import cargar_heartbeat, log_evento
from telegram_bot import enviar_alerta

# Variables globales para rastrear alertas
alerta_desconexion_enviada = False
alerta_silencio_enviada = False
tiempo_inicio_silencio = None
contador_chequeos = 0

# Zona horaria Argentina
ARGENTINA_TZ = timezone(timedelta(hours=-3))

def formatear_fecha_argentina(timestamp):
    """Convertir timestamp a formato Argentina"""
    dt = datetime.fromtimestamp(timestamp, tz=ARGENTINA_TZ)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def monitor_conexion():
    """
    Monitorear conexión y silencio, enviar alertas
    Esta función corre en un hilo separado
    """
    global alerta_desconexion_enviada, alerta_silencio_enviada
    global tiempo_inicio_silencio, contador_chequeos
    
    log_evento("🔍 Monitor de conexión INICIADO")
    log_evento(f"⏱️ Timeout desconexión: {MAX_HEARTBEAT_TIMEOUT}s")
    log_evento(f"🔇 Timeout silencio: {MIN_SILENCE_DURATION}s")
    log_evento(f"🔄 Intervalo de chequeo: {MONITOR_CHECK_INTERVAL}s")
    
    while True:
        time.sleep(MONITOR_CHECK_INTERVAL)
        
        contador_chequeos += 1
        
        ultimo = cargar_heartbeat()
        
        if ultimo:
            ahora = datetime.now(timezone.utc).timestamp()
            hace = int(ahora - ultimo['timestamp'])
            
            # Log cada 10 chequeos (cada 5 minutos aprox)
            if contador_chequeos % 10 == 0:
                log_evento(f"💓 Monitor activo - Último heartbeat hace {hace}s")
            
            # ==========================================
            # CHEQUEO 1: DESCONEXIÓN (PC apagada)
            # ==========================================
            if hace > MAX_HEARTBEAT_TIMEOUT:
                if not alerta_desconexion_enviada:
                    minutos = hace // 60
                    fecha_ultima = formatear_fecha_argentina(ultimo['timestamp'])
                    
                    mensaje = (
                        f"🔴 ALERTA: PC DESCONECTADA\n\n"
                        f"📻 Monitor Radio 97.7 no responde\n"
                        f"🕐 Última señal: {fecha_ultima}\n"
                        f"⏱️ Hace: {minutos} minuto(s)"
                    )
                    
                    log_evento(f"🚨 PC DESCONECTADA - Sin señal hace {minutos} min")
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 ✅ Alerta de DESCONEXIÓN enviada")
                        alerta_desconexion_enviada = True
                    else:
                        log_evento("📤 ❌ ERROR: No se pudo enviar alerta")
                    
                    # Resetear silencio ya que no hay conexión
                    alerta_silencio_enviada = False
                    tiempo_inicio_silencio = None
            
            # ==========================================
            # CHEQUEO 2: PC CONECTADA
            # ==========================================
            else:
                # Si estaba desconectada y volvió
                if alerta_desconexion_enviada:
                    mensaje = (
                        f"✅ PC RESTAURADA EN LÍNEA NUEVAMENTE\n\n"
                        f"📻 Monitor Radio 97.7 FM\n"
                        f"🟢 Conexión restablecida"
                    )
                    
                    log_evento("🎉 PC RECONECTADA")
                    
                    if enviar_alerta(mensaje):
                        log_evento("📤 ✅ Alerta de RECONEXIÓN enviada")
                    
                    alerta_desconexion_enviada = False
                
                # ==========================================
                # CHEQUEO 3: SILENCIO (PC conectada pero sin audio)
                # ==========================================
                is_silent = ultimo.get('is_silent', False)
                
                if is_silent:
                    # Marcar inicio de silencio si es la primera vez
                    if tiempo_inicio_silencio is None:
                        tiempo_inicio_silencio = ultimo['timestamp']
                        log_evento("🔇 Silencio detectado, iniciando conteo...")
                    
                    # Calcular duración del silencio
                    duracion_silencio = int(ahora - tiempo_inicio_silencio)
                    
                    # Si supera el tiempo mínimo y no se envió alerta
                    if duracion_silencio >= MIN_SILENCE_DURATION and not alerta_silencio_enviada:
                        fecha_inicio = formatear_fecha_argentina(tiempo_inicio_silencio)
                        
                        mensaje = (
                            f"🔇 ALERTA: Silencio detectado\n\n"
                            f"📻 Monitor Radio 97.7 FM\n"
                            f"🕐 Inicio: {fecha_inicio}\n"
                            f"⏱️ Duración: {duracion_silencio}s"
                        )
                        
                        log_evento(f"🔇 SILENCIO PROLONGADO - Duración: {duracion_silencio}s")
                        
                        if enviar_alerta(mensaje):
                            log_evento("📤 ✅ Alerta de SILENCIO enviada")
                            alerta_silencio_enviada = True
                        else:
                            log_evento("📤 ❌ ERROR: No se pudo enviar alerta de silencio")
                
                else:
                    # Si había silencio y ahora volvió el audio
                    if alerta_silencio_enviada:
                        fecha_restauracion = formatear_fecha_argentina(ultimo['timestamp'])
                        
                        mensaje = (
                            f"🔊 Audio restaurado\n\n"
                            f"📻 Monitor Radio 97.7 FM\n"
                            f"🕐 Restaurado: {fecha_restauracion}\n"
                            f"✅ Audio transmitiendo normalmente"
                        )
                        
                        log_evento("🔊 AUDIO RESTAURADO")
                        
                        if enviar_alerta(mensaje):
                            log_evento("📤 ✅ Alerta de audio restaurado enviada")
                        
                        alerta_silencio_enviada = False
                    
                    # Resetear contador de silencio
                    tiempo_inicio_silencio = None
        
        else:
            # No hay ningún heartbeat guardado
            if contador_chequeos % 5 == 0:
                log_evento("⚠️ Sin datos de heartbeat - Esperando primera señal...")

def resetear_alerta():
    """Resetear flag de alerta cuando llega un heartbeat"""
    global alerta_desconexion_enviada
    
    # Si estaba desconectado, enviar mensaje de reconexión
    if alerta_desconexion_enviada:
        mensaje = (
            f"✅ PC RESTAURADA EN LÍNEA NUEVAMENTE\n\n"
            f"📻 Monitor Radio 97.7 FM\n"
            f"🟢 Conexión restablecida"
        )
        
        log_evento("🎉 PC RECONECTADA por heartbeat")
        
        if enviar_alerta(mensaje):
            log_evento("📤 ✅ Alerta de RECONEXIÓN enviada")
        
        alerta_desconexion_enviada = False

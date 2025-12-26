🔍 Cómo Funciona el Sistema
Explicación técnica del funcionamiento del monitor de radio.
🎯 Objetivo
Detectar automáticamente cuando la radio tiene problemas y alertar inmediatamente, incluso si:

Hay silencio en el stream
La PC de la radio se cuelga
Hay corte de luz
Hay problemas de red

🏗️ Arquitectura del Sistema
┌─────────────────────┐
│   PC DE LA RADIO    │
│  (Windows + Python) │
│                     │
│  ┌───────────────┐  │
│  │  monitor.py   │  │ ← Interfaz gráfica
│  │               │  │
│  │ • Lee stream  │  │
│  │ • Analiza dB  │  │
│  │ • Detecta     │  │
│  │   silencio    │  │
│  └───────┬───────┘  │
│          │          │
│          ↓          │
│    Heartbeat        │
│    cada 30s         │
└──────────┼──────────┘
           │
           │ HTTP POST
           │
           ↓
┌──────────────────────┐
│  SERVIDOR EXTERNO    │
│  (PythonAnywhere)    │
│                      │
│  ┌────────────────┐  │
│  │    app.py      │  │ ← API Flask
│  │  (recibe POST) │  │
│  └────────┬───────┘  │
│           │          │
│           ↓          │
│  ┌────────────────┐  │
│  │ last_heartbeat │  │ ← Archivo JSON
│  │     .json      │  │
│  └────────┬───────┘  │
│           │          │
│           ↓          │
│  ┌────────────────┐  │
│  │  monitor.py    │  │ ← Vigilante
│  │  (chequea      │  │
│  │   timeouts)    │  │
│  └────────┬───────┘  │
└───────────┼──────────┘
            │
            ↓
       ¿Timeout?
            │
     ┌──────┴──────┐
     │             │
    SÍ            NO
     │             │
     ↓             ↓
  🚨 ALERTA    ✅ OK
     │
     ↓
┌─────────────┐
│  TELEGRAM   │
│   📱 Bot    │
└─────────────┘
🔄 Flujo de Datos
1️⃣ Detección de Audio (PC Radio)
python# 1. Conecta al stream
stream = requests.get("http://radio.com/stream")

# 2. Lee audio (5 segundos)
audio_data = stream.read(5_segundos)

# 3. Analiza nivel de decibelios
audio = AudioSegment.from_file(audio_data)
db_level = audio.dBFS  # ej: -45.2 dBFS

# 4. Compara con umbral
if db_level < SILENCE_THRESH:  # ej: -60 dBFS
    es_silencio = True
2️⃣ Envío de Heartbeat
Cada 30 segundos (configurable):
pythondatos = {
    "radio_id": "lg_fm_radio",
    "timestamp": 1703188923,      # Unix timestamp
    "audio_level": -45.2,          # dBFS actual
    "is_silent": False,            # ¿Hay silencio?
    "status": "ok"
}

# Envía al servidor
requests.post(
    "https://fernandogonzalezz97.pythonanywhere.com/",
    json=datos
)
3️⃣ Recepción en Servidor
python# app.py recibe el POST
@app.route('/heartbeat', methods=['POST'])
def recibir_heartbeat():
    datos = request.get_json()
    
    # Guarda en archivo JSON
    with open('last_heartbeat.json', 'w') as f:
        json.dump(datos, f)
    
    return {"status": "ok"}
4️⃣ Vigilancia de Timeouts
El vigilante (monitor.py) corre en loop infinito:
pythonwhile True:
    # Lee último heartbeat
    ultimo = cargar_heartbeat()
    
    # Calcula tiempo transcurrido
    hace_segundos = time.now() - ultimo['timestamp']
    
    # ¿Pasó el timeout?
    if hace_segundos > 120:  # 2 minutos
        # ¡RADIO CAÍDA!
        enviar_alerta_telegram("🚨 Radio caída")
    
    time.sleep(30)  # Chequear cada 30s
📊 Estados del Sistema
🟢 Estado Normal

Audio: > -60 dBFS
Heartbeat: cada 30s
Servidor: recibe señales
Telegram: sin alertas

🟡 Silencio Detectado

Audio cae bajo -60 dBFS
Se mantiene > 10 segundos
Alerta local desde PC radio
Heartbeat continúa (con flag is_silent: true)

🔴 Radio Caída

PC radio deja de enviar heartbeats
Servidor no recibe señal por > 2 minutos
Alerta desde servidor
Puede ser por:

Cuelgue de PC
Corte de luz
Problema de red
Monitor cerrado



🟢 Restauración

Heartbeats vuelven a llegar
Servidor detecta recuperación
Alerta de restauración

🔔 Tipos de Alertas
Alerta de Silencio (desde PC)
⚠️ ALERTA: Silencio detectado
2024-12-21 14:30:45
Duración: 15s
Causa: Audio bajo umbral
Alerta de Caída (desde Servidor)
🚨 ALERTA: Radio caída

Última señal: hace 180s
Nivel audio: -45.2 dBFS
Hora: 
Causa: Sin heartbeats
Alerta de Restauración
✅ Radio restaurada

Señal recibida correctamente
⏱️ Tiempos Configurables
ParámetroValorDescripciónCHECK_INTERVAL2sFrecuencia de análisis de audioHEARTBEAT_INTERVAL30sEnvío de señales al servidorMIN_SILENCE_DURATION10sSilencio mínimo para alertarMAX_HEARTBEAT_TIMEOUT120sTimeout para detectar caídaMONITOR_CHECK_INTERVAL30sFrecuencia del vigilante
🎚️ Umbrales de Audio
dBFS (Decibels relative to Full Scale)
   0 dBFS ────────── Máximo (distorsión)
 -10 dBFS ────────── Muy alto
 -20 dBFS ────────── Alto
 -30 dBFS ────────── Medio-alto
 -40 dBFS ────────── Medio
 -50 dBFS ────────── Bajo
 -60 dBFS ────────── Muy bajo ← UMBRAL DEFAULT
 -70 dBFS ────────── Casi silencio
-inf dBFS ────────── Silencio absoluto
Ajustar según tu stream:

Stream ruidoso: -50 dBFS
Stream normal: -60 dBFS
Stream limpio: -70 dBFS

🔐 Seguridad de Datos
Almacenamiento Local (PC Radio)

Logs: logs/radio.log
Sin datos sensibles

Almacenamiento Servidor

Heartbeats: last_heartbeat.json (solo último)
Logs: logs/servidor.log
No guarda historial completo

Comunicación

HTTP(S) entre PC y servidor
API de Telegram (HTTPS)
Sin autenticación (agregar JWT en v2)

🚀 Optimizaciones Futuras
v1.1 (Planeado)

 Base de datos para historial
 Dashboard web con gráficos
 Múltiples radios simultáneas
 Autenticación API

v1.2 (Futuro)

🐛 Depuración
Logs a revisar
PC Radio:
bashlogs/radio.log
Servidor:
bashlogs/servidor.log
Endpoints de debug
bash# ¿Servidor vivo?
url https://estructura-inicial-del-proyecto.onrender.com/

# Estado actual
url https://estructura-inicial-del-proyecto.onrender.com/


# Dashboard visual
https://estructura-inicial-del-proyecto.onrender.com/
📚 Recursos Técnicos

Flask Documentation
CustomTkinter Docs
Pydub Documentation
Telegram Bot API
FFmpeg Wiki

🤝 Contribuir
Para mejorar el sistema:

Fork del repositorio
Crear branch (feature/mejora)
Commit cambios
Pull request

📞 Soporte
Para problemas técnicos, revisá:

Esta documentación
Los logs del sistema
Issues en GitHub (si aplicable)
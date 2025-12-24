# ===================================
# Configuración - Monitor Radio 
# PC de la Radio 
# ===================================

# ========================
# STREAM DE AUDIO
# ========================
STREAM_URL = "http://stream.lgcomunicaciones.com:8045/;stream/1"

# ========================
# SERVIDOR EXTERNO
# ========================
# URL del servidor donde enviar heartbeats
# URL del servidro
SERVER_URL = "https://fernandogonzalezz97.pythonanywhere.com/"

# ========================
# TELEGRAM (Alertas locales)
# ========================
TELEGRAM_BOT_TOKEN = "7661456231:AAEJ5E169mxgVWGJhTilblt6rj20cy_sztc"
TELEGRAM_CHAT_ID = "7298850248"

# ========================
# DETECCIÓN DE SILENCIO
# ========================
# Umbral de silencio en dBFS (decibelios)
# -60 = muy sensible | -40 = menos sensible
SILENCE_THRESH = -60

# Duración mínima de silencio antes de alertar (segundos)
MIN_SILENCE_DURATION = 10

# ========================
# HEARTBEAT
# ========================
# Cada cuántos segundos enviar señal al servidor
HEARTBEAT_INTERVAL = 30

# ========================
# MONITOREO
# ========================
# Intervalo entre chequeos de audio (segundos)
CHECK_INTERVAL = 2

# Timeout para conexiones HTTP (segundos)
TIMEOUT = 10

# ========================
# INTERFAZ GRÁFICA
# ========================
# Título de la ventana
WINDOW_TITLE = "Monitor Radio "

# Tamaño de ventana (ancho x alto)
WINDOW_SIZE = "700x500"

# Tema: "dark" o "light"
THEME = "dark"


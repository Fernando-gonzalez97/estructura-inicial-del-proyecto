📻 Instalación en PC de la Radio
Guía paso a paso para instalar el monitor en la computadora de la radio.
📋 Requisitos Previos

Windows 7 o superior
Python 3.8 o superior
FFmpeg instalado
Conexión a Internet
Bot de Telegram configurado

🔧 Instalación de Python

Descargá Python desde python.org
IMPORTANTE: Durante la instalación, marcá "Add Python to PATH"
Verificá la instalación abriendo CMD y ejecutando:

cmd   python --version
🎵 Instalación de FFmpeg

Descargá FFmpeg desde ffmpeg.org
Extraé el archivo ZIP
Agregá FFmpeg al PATH del sistema:

Buscá "Variables de entorno" en Windows
Editá "Path" en Variables del sistema
Agregá la ruta de la carpeta bin de FFmpeg



📦 Instalación del Monitor
Opción 1: Instalación Automática (Recomendada)

Copiá la carpeta radio/ a tu PC
Abrí la carpeta y ejecutá instalar.bat
Esperá a que termine la instalación
¡Listo! ✅

Opción 2: Instalación Manual
cmd# Crear entorno virtual
python -m venv venv

# Activar entorno
venv\Scripts\activate

# Instalar dependencias
pip install customtkinter
pip install requests
pip install pydub
⚙️ Configuración
Editá el archivo config.py:
python# URL del stream de tu radio
STREAM_URL = "http://tu-radio.com:8000/stream"

# URL del servidor externo (cuando lo tengas)
SERVER_URL = https://estructura-inicial-del-proyecto.onrender.com/

# Credenciales de Telegram
TELEGRAM_BOT_TOKEN = "tu_token_aqui"
TELEGRAM_CHAT_ID = "tu_chat_id_aqui"

# Ajustes de detección
SILENCE_THRESH = -60  # Más negativo = más sensible
MIN_SILENCE_DURATION = 10  # Segundos de silencio antes de alertar
🚀 Ejecutar el Monitor
Primera vez:
cmdinstalar.bat
Uso diario:
cmdiniciar.bat
O desde CMD:
cmdvenv\Scripts\activate
python monitor.py
🎛️ Uso de la Interfaz

Estado: Muestra si el monitor está activo
Nivel de Audio: dBFS actual del stream
Estado Stream: Conexión con el servidor de audio
Heartbeat: Última vez que envió señal al servidor
Log: Historial de eventos

Botones:

▶ Iniciar Monitoreo: Comienza el monitoreo automático
⏸ Detener Monitoreo: Pausa el monitoreo
📱 Test Telegram: Prueba el envío de alertas

🔍 Solución de Problemas
Error: "Python no encontrado"

Instalá Python y asegurate de marcarlo en PATH

Error: "FFmpeg no encontrado"

Instalá FFmpeg y agregalo al PATH

Error: "Timeout conectando"

Verificá la URL del stream
Comprobá tu conexión a Internet

Error: "Error Telegram"

Verificá el token del bot
Verificá el chat ID
Probá el bot manualmente en Telegram

El monitor no detecta silencios

Ajustá SILENCE_THRESH (más negativo = más sensible)
Verificá que el stream esté funcionando

📝 Notas

El monitor debe quedar corriendo 24/7
Se recomienda configurarlo para iniciar automáticamente con Windows
Los logs se guardan en ../logs/radio.log

🆘 Soporte
Si tenés problemas, revisá:

Los logs en la interfaz
El archivo logs/radio.log
La configuración en config.py
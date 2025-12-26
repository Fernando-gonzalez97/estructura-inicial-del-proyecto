🌐 Instalación en Servidor Externo
Guía para deployar el servidor de monitoreo en PythonAnywhere (u otro servicio).
🎯 ¿Por qué un servidor externo?
El servidor externo actúa como vigilante independiente:

Si la PC de la radio se cuelga → el servidor lo detecta
Si hay corte de luz → el servidor alerta
Monitoreo 24/7 sin depender de la PC local

📋 Opción 1: PythonAnywhere (Recomendado)
Paso 1: Crear cuenta

Visitá pythonanywhere.com
Creá una cuenta gratuita
Elegí un nombre de usuario (será tu URL: tuusuario.pythonanywhere.com)

Paso 2: Subir archivos
Opción A: Desde Git
bash# En la consola Bash de PythonAnywhere
cd ~
git clone https://github.com/Fernando-gonzalez97/estructura-inicial-del-proyecto
cd radio-monitor/server
Opción B: Upload manual

Andá a "Files"
Creá carpeta radio-monitor/server
Subí todos los archivos de server/

Paso 3: Crear entorno virtual
bashcd ~/radio-monitor/server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Paso 4: Configurar Web App

Andá a "Web" en el dashboard
Click "Add a new web app"
Elegí "Manual configuration" → Python 3.10
Configurá:

WSGI file:
pythonimport sys
path = '/home/TUUSUARIO/radio-monitor/server'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
Virtualenv:
/home/TUUSUARIO/radio-monitor/server/venv

Click "Reload" en la web app

Paso 5: Iniciar el Monitor
Abrí 2 consolas Bash:
Console 1 - API Flask:
bashcd ~/radio-monitor/server
source venv/bin/activate
python app.py
Console 2 - Vigilante:
bashcd ~/radio-monitor/server
source venv/bin/activate
python monitor.py
Paso 6: Verificar
Visitá: https://fernandogonzalezz97.pythonanywhere.com/
Deberías ver el dashboard del monitor.
📋 Opción 2: VPS (DigitalOcean, AWS, etc.)
Requisitos

Ubuntu 20.04 o superior
Python 3.8+
nginx (opcional)
systemd (para auto-inicio)

Instalación
bash# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y dependencias
sudo apt install python3 python3-pip python3-venv -y

# Clonar repositorio
git clone https://github.com/Fernando-gonzalez97/estructura-inicial-del-proyecto
cd radio-monitor/server

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Crear servicios systemd
/etc/systemd/system/radio-api.service:
ini[Unit]
Description=Radio Monitor API
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/home/tu-usuario/radio-monitor/server
Environment="PATH=/home/tu-usuario/radio-monitor/server/venv/bin"
ExecStart=/home/tu-usuario/radio-monitor/server/venv/bin/python app.py

[Install]
WantedBy=multi-user.target
/etc/systemd/system/radio-monitor.service:
ini[Unit]
Description=Radio Monitor Vigilante
After=network.target

[Service]
User=tu-usuario
WorkingDirectory=/home/tu-usuario/radio-monitor/server
Environment="PATH=/home/tu-usuario/radio-monitor/server/venv/bin"
ExecStart=/home/tu-usuario/radio-monitor/server/venv/bin/python monitor.py

[Install]
WantedBy=multi-user.target
Habilitar servicios
bashsudo systemctl daemon-reload
sudo systemctl enable radio-api
sudo systemctl enable radio-monitor
sudo systemctl start radio-api
sudo systemctl start radio-monitor

# Verificar estado
sudo systemctl status radio-api
sudo systemctl status radio-monitor
⚙️ Configuración
Editá server/config.py:
python# Telegram
TELEGRAM_BOT_TOKEN = "tu_token_aqui"
TELEGRAM_CHAT_ID = "tu_chat_id_aqui"

# Timeouts
MAX_HEARTBEAT_TIMEOUT = 120  # 2 minutos sin señal = alerta
MONITOR_CHECK_INTERVAL = 30  # Chequear cada 30 segundos

# Flask
FLASK_PORT = 5000
FLASK_DEBUG = False  # SIEMPRE False en producción
🧪 Pruebas
Test 1: API funcionando
bashcurl https://fernandogonzalezz97.pythonanywhere.com/ping
# Respuesta esperada: "{"mensaje":"Servidor activo","status":"ok","timestamp":"2025-12-23T00:49:47.759269"}
Test 2: Enviar heartbeat manual
bashcurl -X POST https://tuusuario.pythonanywhere.com/heartbeat \ 
https://fernandogonzalezz97.pythonanywhere.com/ (interfaz web)

  -H "Content-Type: application/json" \
  -d '{
    "radio_id": "test",
    "timestamp": 1234567890,
    "audio_level": -30,
    "is_silent": false
  }'
Test 3: Ver estado
bashcurl https://fernandogonzalezz97.pythonanywhere.com/status (API JSON)
📊 Monitoreo del Servidor
Ver logs
bash# En PythonAnywhere
cd ~/radio-monitor/logs
tail -f servidor.log

# En VPS
journalctl -u radio-api -f
journalctl -u radio-monitor -f
Reiniciar servicios
bash# PythonAnywhere: desde el dashboard Web → Reload

# VPS:
sudo systemctl restart radio-api
sudo systemctl restart radio-monitor
🔒 Seguridad

No expongas tokens: Usá variables de entorno
HTTPS: PythonAnywhere lo da gratis, en VPS usá Let's Encrypt
Firewall: Solo abrí puertos necesarios
Actualizaciones: Mantené el sistema actualizado

🆘 Solución de Problemas
Error 502 Bad Gateway

Verificá que app.py esté corriendo
Revisá logs de errores

Monitor no detecta caídas

Verificá que monitor.py esté corriendo
Revisá MAX_HEARTBEAT_TIMEOUT en config

Sin alertas en Telegram

Verificá tokens
Probá telegram_bot.py manualmente

📝 Mantenimiento

Revisá logs semanalmente
Actualizá dependencias mensualmente
Hacé backups de configuración

🔗 URLs útiles

Dashboard: https://estructura-inicial-del-proyecto.onrender.com//

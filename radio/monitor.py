"""
Monitor de Radio 
Detecta silencio + Envía heartbeat al servidor
Interfaz moderna con CustomTkinter
"""

import customtkinter as ctk
import threading
import requests
import time
import os
import shutil
from datetime import datetime
from pydub import AudioSegment
import io

# Importar configuración
from config import *

# ========================
# Configurar FFmpeg
# ========================
def find_ffmpeg():
    """Encuentra FFmpeg en el sistema"""
    try:
        import subprocess
        result = subprocess.run(['where', 'ffmpeg'], 
                              capture_output=True, 
                              text=True, 
                              shell=True,
                              timeout=3)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().split('\n')[0].strip()
    except:
        pass
    
    ffmpeg_path = shutil.which('ffmpeg')
    if ffmpeg_path:
        return ffmpeg_path
    
    return 'ffmpeg'

os.environ["PYDUB_CONVERT_MODE"] = "ffmpeg"
AudioSegment.converter = find_ffmpeg()
AudioSegment.ffprobe = find_ffmpeg().replace('ffmpeg', 'ffprobe')

# ========================
# Clase Principal
# ========================
class MonitorRadio(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configurar ventana
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        
        # Configurar tema
        ctk.set_appearance_mode(THEME)
        ctk.set_default_color_theme("blue")
        
        # Variables de estado
        self.monitoring = False
        self.monitor_thread = None
        self.last_status = False
        self.silence_start_time = None
        self.last_heartbeat = time.time()
        self.consecutive_errors = 0
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Iniciar monitoreo automático
        self.after(500, self.iniciar_monitoreo)
        
    def crear_interfaz(self):
        """Crear interfaz gráfica moderna"""
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # ==================
        # Título
        # ==================
        titulo = ctk.CTkLabel(
            self.main_frame,
            text="🎙️ Monitor Radio ",
            font=("Arial", 24, "bold")
        )
        titulo.pack(pady=(0, 20))
        
        # ==================
        # Estado
        # ==================
        estado_frame = ctk.CTkFrame(self.main_frame)
        estado_frame.pack(fill="x", padx=10, pady=10)
        
        self.estado_label = ctk.CTkLabel(
            estado_frame,
            text="🔴 Detenido",
            font=("Arial", 18, "bold"),
            text_color="red"
        )
        self.estado_label.pack(pady=10)
        
        # ==================
        # Métricas
        # ==================
        metricas_frame = ctk.CTkFrame(self.main_frame)
        metricas_frame.pack(fill="x", padx=10, pady=10)
        
        # Audio Level
        ctk.CTkLabel(metricas_frame, text="🔊 Nivel de Audio:", 
                    font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10, pady=5)
        self.audio_label = ctk.CTkLabel(metricas_frame, text="-- dBFS", 
                                       font=("Arial", 14, "bold"))
        self.audio_label.grid(row=0, column=1, sticky="w", padx=10, pady=5)
        
        # Stream Status
        ctk.CTkLabel(metricas_frame, text="🌐 Estado Stream:", 
                    font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10, pady=5)
        self.stream_label = ctk.CTkLabel(metricas_frame, text="Desconocido", 
                                        font=("Arial", 12))
        self.stream_label.grid(row=1, column=1, sticky="w", padx=10, pady=5)
        
        # Heartbeat
        ctk.CTkLabel(metricas_frame, text="💓 Último Heartbeat:", 
                    font=("Arial", 12)).grid(row=2, column=0, sticky="w", padx=10, pady=5)
        self.heartbeat_label = ctk.CTkLabel(metricas_frame, text="Nunca", 
                                           font=("Arial", 12))
        self.heartbeat_label.grid(row=2, column=1, sticky="w", padx=10, pady=5)
        
        # ==================
        # Botón Control
        # ==================
        self.toggle_btn = ctk.CTkButton(
            self.main_frame,
            text="▶ Iniciar Monitoreo",
            command=self.toggle_monitoreo,
            font=("Arial", 14, "bold"),
            height=40
        )
        self.toggle_btn.pack(pady=20)
        
        # ==================
        # Log de eventos
        # ==================
        log_label = ctk.CTkLabel(self.main_frame, text="📋 Registro de Eventos", 
                                font=("Arial", 14, "bold"))
        log_label.pack(pady=(10, 5))
        
        self.log_text = ctk.CTkTextbox(self.main_frame, height=150, width=600)
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
    def log(self, mensaje, importante=False):
        """Agregar mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        linea = f"[{timestamp}] {mensaje}\n"
        
        self.log_text.insert("end", linea)
        self.log_text.see("end")
        
    def toggle_monitoreo(self):
        """Iniciar/detener monitoreo"""
        if not self.monitoring:
            self.iniciar_monitoreo()
        else:
            self.detener_monitoreo()
            
    def iniciar_monitoreo(self):
        """Iniciar monitoreo"""
        self.monitoring = True
        self.estado_label.configure(text="🟢 Activo", text_color="green")
        self.toggle_btn.configure(text="⏸ Detener Monitoreo")
        
        self.log("✅ Monitoreo iniciado", importante=True)
        self.log(f"Umbral: {SILENCE_THRESH} dBFS | Heartbeat: cada {HEARTBEAT_INTERVAL}s")
        
        # Iniciar thread de monitoreo
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        
    def detener_monitoreo(self):
        """Detener monitoreo"""
        self.monitoring = False
        self.estado_label.configure(text="🔴 Detenido", text_color="red")
        self.toggle_btn.configure(text="▶ Iniciar Monitoreo")
        
        self.log("⛔ Monitoreo detenido", importante=True)
        
    def enviar_telegram(self, texto):
    """Enviar mensaje a Telegram usando el módulo"""
    from telegram import enviar_alerta
    if enviar_alerta(texto):
        self.log("📤 Alerta enviada a Telegram")
        return True
    else:
        self.log("⚠️ Error enviando alerta")
        return False
            
    def enviar_heartbeat(self, audio_level, es_silencio):
        """Enviar heartbeat al servidor"""
        try:
            datos = {
                "radio_id": "radio_fm_97.7",
                "timestamp": time.time(),
                "audio_level": audio_level,
                "is_silent": es_silencio,
                "status": "ok"
            }
            
            response = requests.post(SERVER_URL, json=datos, timeout=5)
            
            if response.status_code == 200:
                self.last_heartbeat = time.time()
                self.after(0, lambda: self.heartbeat_label.configure(
                    text=datetime.now().strftime("%H:%M:%S")))
                return True
            return False
            
        except Exception as e:
            if self.consecutive_errors == 0:
                self.log(f"⚠️ Error heartbeat: {str(e)[:40]}")
            return False
            
    def analizar_audio(self):
        """Analizar audio del stream"""
        try:
            r = requests.get(STREAM_URL, stream=True, timeout=TIMEOUT)
            
            if r.status_code != 200:
                self.after(0, lambda: self.stream_label.configure(
                    text=f"HTTP {r.status_code}"))
                return None
            
            # Leer datos
            raw_data = r.raw.read(44100 * 2 * 2 * 5)
            
            if len(raw_data) < 1000:
                return None
            
            # Procesar audio
            try:
                audio = AudioSegment.from_file(io.BytesIO(raw_data), format="mp3")
                db_level = audio.dBFS
            except:
                if self.consecutive_errors == 0:
                    self.log("⚠️ Error procesando audio")
                self.consecutive_errors += 1
                return None
            
            # Actualizar UI
            self.after(0, lambda d=db_level: self.audio_label.configure(
                text=f"{d:.1f} dBFS"))
            self.after(0, lambda: self.stream_label.configure(text="Conectado ✓"))
            
            self.consecutive_errors = 0
            
            return db_level < SILENCE_THRESH
            
        except requests.exceptions.Timeout:
            if self.consecutive_errors <= 1:
                self.log("⏱️ Timeout conectando")
            self.consecutive_errors += 1
            return None
        except Exception as e:
            if self.consecutive_errors <= 1:
                self.log(f"❌ Error: {str(e)[:50]}")
            self.consecutive_errors += 1
            return None
            
    def monitor_loop(self):
        """Loop principal de monitoreo"""
        ultimo_heartbeat = time.time()
        
        while self.monitoring:
            es_silencio = self.analizar_audio()
            
            if es_silencio is None:
                time.sleep(CHECK_INTERVAL)
                continue
            
            now = time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Detectar silencio
            if es_silencio:
                if self.silence_start_time is None:
                    self.silence_start_time = time.time()
                
                duracion = time.time() - self.silence_start_time
                
                if duracion >= MIN_SILENCE_DURATION and not self.last_status:
                    msg = f"⚠️ ALERTA: Silencio detectado\n{now}\nDuración: {duracion:.0f}s"
                    self.enviar_telegram(msg)
                    self.log(f"🔴 SILENCIO DETECTADO ({duracion:.0f}s)", importante=True)
                    self.last_status = True
            
            # Detectar audio restaurado
            else:
                if self.silence_start_time is not None:
                    self.silence_start_time = None
                
                if self.last_status:
                    msg = f"✅ Audio restaurado\n{now}"
                    self.enviar_telegram(msg)
                    self.log("🟢 AUDIO RESTAURADO", importante=True)
                    self.last_status = False
            
            # Enviar heartbeat cada X segundos
            if time.time() - ultimo_heartbeat >= HEARTBEAT_INTERVAL:
                audio_level = -999 if es_silencio is None else (
                    SILENCE_THRESH - 10 if es_silencio else SILENCE_THRESH + 10)
                self.enviar_heartbeat(audio_level, es_silencio)
                ultimo_heartbeat = time.time()
            
            time.sleep(CHECK_INTERVAL)

# ========================
# Ejecutar aplicación
# ========================
if __name__ == "__main__":
    app = MonitorRadio()
    app.mainloop()
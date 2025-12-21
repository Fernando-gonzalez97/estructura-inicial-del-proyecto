"""
Bot de Telegram - Envío de Alertas
"""

import requests
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

def enviar_alerta(mensaje):
    """
    Enviar mensaje de alerta a Telegram
    
    Args:
        mensaje (str): Texto del mensaje
        
    Returns:
        bool: True si se envió correctamente
    """
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        
        datos = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML"
        }
        
        response = requests.post(url, data=datos, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Alerta enviada a Telegram")
            return True
        else:
            print(f"⚠️ Error Telegram: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando a Telegram: {str(e)}")
        return False
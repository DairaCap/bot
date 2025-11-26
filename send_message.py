import requests

# ================================
# CONFIGURACIÓN
# ================================

# Pega aquí tu token de BotFather
BOT_TOKEN = "8332297959:AAHz8-lTxWgTVAWhTySmYtyfVbJyxxFJjCU"

# Tu Telegram User ID (ya lo sacamos de getUpdates)
CHAT_ID = 130531908

# Mensaje que quieres enviar
TEXT = "¡Hola Daira! 🚀 Tu bot ya está enviando mensajes."


# ================================
# FUNCIÓN QUE ENVÍA EL MENSAJE
# ================================

def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": chat_id,
        "text": text
    }

    r = requests.post(url, json=payload)

    # Ver salida limpia
    print("Status:", r.status_code)
    print("Response:", r.json())


# ================================
# EJECUCIÓN
# ================================

if _name_ == "_main_":
    send_message(CHAT_ID, TEXT)
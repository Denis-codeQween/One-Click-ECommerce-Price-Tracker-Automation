import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """
    Sends a text message to a Telegram chat.
    Splits long messages into chunks and sends without parse_mode
    to prevent markup errors caused by product title characters.
    """
    if not TOKEN or not CHAT_ID:
        print("[ERROR] Telegram token or chat ID is missing in .env file.")
        return False

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    max_length = 4000
    
    if len(message) <= max_length:
        messages = [message]
    else:
        messages = [message[i:i+max_length] for i in range(0, len(message), max_length)]
        
    success = True
    for chunk in messages:
        payload = {
            "chat_id": CHAT_ID,
            "text": chunk
            # Without parse_mode to prevent characters like *, _, [ ] from breaking the delivery
        }
        try:
            response = requests.post(url, json=payload)
            res_data = response.json()
            if not res_data.get("ok"):
                print(f"[ERROR] Failed to send Telegram alert part: {response.text}")
                success = False
        except Exception as e:
            print(f"[ERROR] Telegram connection error: {e}")
            success = False
            
    return success

if __name__ == "__main__":
    test_msg = "Telegram bot is successfully connected to Price Tracker!"
    print("Sending test message...")
    send_telegram_alert(test_msg)
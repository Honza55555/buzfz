import os
from flask import Flask, request
import requests

app = Flask(__name__)

# Získej token bota z prostředí
BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

@app.route("/", methods=["POST"])
def webhook():
    # Zpracuj příchozí update
    update = request.get_json()
    if not update:
        return "OK"
    # Pokud update obsahuje message
    if "message" in update:
        message = update["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")
        # Pokud uživatel zadá /start, odpověz "ahoj"
        if text == "/start":
            send_message(chat_id, "ahoj")
    return "OK"

def send_message(chat_id, text):
    url = f"{API_URL}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)

if __name__ == "__main__":
    # Render očekává PORT jako proměnnou prostředí
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


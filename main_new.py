from flask import Flask, request
import requests
import json
import os
from datetime import date, timedelta
import random
import datetime

print("=== НОВИЙ MAIN.PY ЗАВАНТАЖУЄТЬСЯ ===")

TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

@app.route("/test", methods=["GET"])
def test():
    print("=== ТЕСТОВИЙ ENDPOINT ВИКЛИКАНО ===")
    return "Test endpoint works!"

@app.route("/hello", methods=["GET"])
def hello():
    return "Hello endpoint!"

@app.route("/webhook_info", methods=["GET"])
def webhook_info():
    return f"""
    <h1>Telegram Bot Webhook Info</h1>
    <p>Bot Token: {TOKEN[:20]}...</p>
    <p>Webhook URL: https://your-domain.com/{TOKEN}</p>
    <p>Status: Ready to receive updates</p>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True) 
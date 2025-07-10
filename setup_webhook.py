#!/usr/bin/env python3
"""
Простий скрипт для налаштування webhook Telegram бота
"""

import requests
import json

def setup_webhook():
    """Налаштовує webhook для Telegram бота"""
    
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    
    print("🤖 Налаштування Telegram Bot Webhook")
    print("=" * 50)
    
    # Перевіряємо поточний стан webhook
    print("📊 Перевірка поточного webhook...")
    check_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(check_url)
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                current_url = webhook_info.get("url", "")
                print(f"   Поточний URL: {current_url if current_url else 'Не налаштовано'}")
            else:
                print(f"   Помилка: {result.get('description', 'Unknown')}")
    except Exception as e:
        print(f"   Помилка перевірки: {e}")
    
    print(f"\n📋 Інструкції для налаштування webhook:")
    print(f"1. Запустіть ваш бот: $env:PORT=10005; python run.py")
    print(f"2. Встановіть ngrok: ngrok http 10005")
    print(f"3. Скопіюйте публічний URL з ngrok (наприклад: https://abc123.ngrok.io)")
    print(f"4. Виконайте наступну команду:")
    print(f"   curl -X POST https://api.telegram.org/bot{TOKEN}/setWebhook")
    print(f"   -H 'Content-Type: application/json'")
    print(f"   -d '{{\"url\": \"https://abc123.ngrok.io/{TOKEN}\"}}'")
    
    print(f"\n🔗 Або відкрийте в браузері:")
    print(f"   https://api.telegram.org/bot{TOKEN}/setWebhook?url=https://abc123.ngrok.io/{TOKEN}")
    
    print(f"\n📱 Після налаштування webhook:")
    print(f"   - Надішліть /start боту в Telegram")
    print(f"   - Перевірте логи у консолі бота")
    
    return TOKEN

def test_bot():
    """Тестує бота через API"""
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    
    print(f"\n🧪 Тестування бота...")
    
    # Отримуємо інформацію про бота
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                print(f"✅ Бот активний:")
                print(f"   Ім'я: {bot_info.get('first_name', 'Unknown')}")
                print(f"   Username: @{bot_info.get('username', 'Unknown')}")
                print(f"   ID: {bot_info.get('id', 'Unknown')}")
            else:
                print(f"❌ Помилка: {result.get('description', 'Unknown')}")
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")

if __name__ == "__main__":
    TOKEN = setup_webhook()
    test_bot()
    
    print(f"\n🎯 Готово! Тепер налаштуйте webhook та запустіть бота.") 
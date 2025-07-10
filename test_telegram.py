#!/usr/bin/env python3
"""
Тестування Telegram бота через API
"""

import requests
import json

def test_bot_api():
    """Тестує бота через Telegram API"""
    
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    
    print("🧪 Тестування Telegram бота")
    print("=" * 40)
    
    # Тестуємо отримання інформації про бота
    print("1. Перевірка інформації про бота...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe")
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                bot_info = result.get("result", {})
                print(f"✅ Бот активний:")
                print(f"   Ім'я: {bot_info.get('first_name')}")
                print(f"   Username: @{bot_info.get('username')}")
                print(f"   ID: {bot_info.get('id')}")
            else:
                print(f"❌ Помилка: {result.get('description')}")
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
    
    # Перевіряємо webhook
    print(f"\n2. Перевірка webhook...")
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                url = webhook_info.get("url", "")
                if url:
                    print(f"✅ Webhook активний: {url}")
                    
                    # Тестуємо webhook
                    print(f"\n3. Тестування webhook...")
                    test_data = {
                        "update_id": 123456789,
                        "message": {
                            "message_id": 1,
                            "from": {
                                "id": 123456789,
                                "first_name": "Test",
                                "username": "testuser"
                            },
                            "chat": {
                                "id": 123456789,
                                "type": "private"
                            },
                            "date": 1234567890,
                            "text": "/start"
                        }
                    }
                    
                    try:
                        webhook_response = requests.post(url, json=test_data, timeout=10)
                        print(f"✅ Webhook відповідь: {webhook_response.status_code}")
                        if webhook_response.status_code == 200:
                            print(f"   Відповідь: {webhook_response.text}")
                    except Exception as e:
                        print(f"❌ Помилка webhook: {e}")
                else:
                    print(f"❌ Webhook не налаштований")
            else:
                print(f"❌ Помилка: {result.get('description')}")
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
    except Exception as e:
        print(f"❌ Помилка перевірки webhook: {e}")
    
    print(f"\n📋 Інструкції:")
    print(f"1. Відкрийте Telegram")
    print(f"2. Знайдіть: @{bot_info.get('username') if 'bot_info' in locals() else 'Valou5578bot'}")
    print(f"3. Надішліть: /start")
    print(f"4. Якщо не працює - перевірте логи на Render")

def send_test_message():
    """Надсилає тестове повідомлення (потрібен chat_id)"""
    
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    
    print(f"\n📤 Для надсилання тестового повідомлення:")
    print(f"1. Надішліть /start боту в Telegram")
    print(f"2. Скопіюйте ваш chat_id з логів")
    print(f"3. Використайте команду:")
    print(f"   curl -X POST https://api.telegram.org/bot{TOKEN}/sendMessage")
    print(f"   -H 'Content-Type: application/json'")
    print(f"   -d '{{\"chat_id\": \"ВАШ_CHAT_ID\", \"text\": \"Тест\"}}'")

if __name__ == "__main__":
    test_bot_api()
    send_test_message() 
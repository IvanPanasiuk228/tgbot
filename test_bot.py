#!/usr/bin/env python3
"""
Тестування Telegram бота локально
"""

import requests
import json

def test_bot_locally():
    """Тестує бота локально"""
    
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    local_url = "http://localhost:10005"
    
    print("🧪 Тестування бота локально")
    print("=" * 40)
    
    # Тестуємо основні endpoints
    endpoints = [
        ("/", "Головна сторінка"),
        ("/hello", "Тестовий endpoint"),
        ("/test", "Тестовий endpoint"),
        ("/webhook_info", "Інформація про webhook")
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{local_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: {response.text[:50]}...")
            else:
                print(f"❌ {description}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: Помилка підключення - {e}")
    
    print(f"\n📱 Для тестування з Telegram:")
    print(f"1. Запустіть бота: $env:PORT=10005; python run.py")
    print(f"2. Встановіть ngrok вручну:")
    print(f"   - Завантажте з https://ngrok.com/")
    print(f"   - Розархівуйте в папку")
    print(f"   - Запустіть: ./ngrok http 10005")
    print(f"3. Скопіюйте URL та оновіть webhook")
    
    print(f"\n🌐 Або використовуйте поточний хостинг:")
    print(f"   Ваш бот вже працює на Render!")
    print(f"   Знайдіть @Valou5578bot в Telegram")

def check_webhook_status():
    """Перевіряє статус webhook"""
    
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    
    print(f"\n📊 Статус webhook:")
    try:
        response = requests.get(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                url = webhook_info.get("url", "")
                if url:
                    print(f"✅ Webhook активний: {url}")
                else:
                    print(f"❌ Webhook не налаштований")
            else:
                print(f"❌ Помилка: {result.get('description')}")
    except Exception as e:
        print(f"❌ Помилка перевірки: {e}")

if __name__ == "__main__":
    test_bot_locally()
    check_webhook_status()
    
    print(f"\n🎯 Рекомендації:")
    print(f"1. Спробуйте написати боту @Valou5578bot в Telegram")
    print(f"2. Якщо не працює - запустіть локальний сервер")
    print(f"3. Для ngrok - завантажте вручну з офіційного сайту") 
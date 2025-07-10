#!/usr/bin/env python3
"""
Скрипт для налаштування ngrok туннелю для Telegram бота
"""

import os
import time
import requests
from pyngrok import ngrok

def setup_ngrok():
    """Налаштовує ngrok туннель для Telegram бота"""
    
    print("🚀 Налаштування ngrok туннелю...")
    
    # Закриваємо всі попередні туннелі
    ngrok.kill()
    
    # Відкриваємо туннель на порту 10005
    port = 10005
    public_url = ngrok.connect(port)
    
    print(f"✅ Туннель відкрито!")
    print(f"🌐 Публічний URL: {public_url}")
    print(f"🔗 Локальний порт: {port}")
    
    # Формуємо webhook URL
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    webhook_url = f"{public_url}/{TOKEN}"
    
    print(f"\n📱 Webhook URL для Telegram:")
    print(f"   {webhook_url}")
    
    # Налаштовуємо webhook автоматично
    print(f"\n🔧 Налаштування webhook...")
    telegram_api_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"
    
    try:
        response = requests.post(telegram_api_url, json={
            "url": webhook_url,
            "allowed_updates": ["message", "callback_query"]
        })
        
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                print("✅ Webhook успішно налаштовано!")
                print(f"📊 Статус: {result.get('description', 'OK')}")
            else:
                print(f"❌ Помилка налаштування: {result.get('description', 'Unknown error')}")
        else:
            print(f"❌ HTTP помилка: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Помилка підключення: {e}")
    
    print(f"\n📋 Інструкції:")
    print(f"1. Запустіть ваш бот: python run.py (на порту 10005)")
    print(f"2. Перевірте webhook: {telegram_api_url.replace('/setWebhook', '/getWebhookInfo')}")
    print(f"3. Надішліть повідомлення боту в Telegram")
    print(f"4. Для зупинки натисніть Ctrl+C")
    
    return public_url, webhook_url

def check_webhook():
    """Перевіряє поточний стан webhook"""
    TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
    url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            if result.get("ok"):
                webhook_info = result.get("result", {})
                print(f"\n📊 Поточний стан webhook:")
                print(f"   URL: {webhook_info.get('url', 'Не налаштовано')}")
                print(f"   Статус: {'Активний' if webhook_info.get('url') else 'Неактивний'}")
                return webhook_info
    except Exception as e:
        print(f"❌ Помилка перевірки: {e}")
    
    return None

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Telegram Bot Webhook Setup")
    print("=" * 50)
    
    # Перевіряємо поточний стан
    check_webhook()
    
    # Налаштовуємо новий туннель
    public_url, webhook_url = setup_ngrok()
    
    print(f"\n⏳ Туннель активний. Натисніть Ctrl+C для зупинки...")
    
    try:
        # Тримаємо туннель відкритим
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n🛑 Зупинка туннелю...")
        ngrok.kill()
        print(f"✅ Туннель закрито") 
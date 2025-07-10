#!/usr/bin/env python3
"""
Скрипт для запуску Telegram бота
"""

import os
import sys
from main import app

def main():
    """Головна функція для запуску бота"""
    print("🚀 Запуск Telegram бота...")
    print("📱 Бот буде доступний на порту 10000")
    print("🌐 Локальний URL: http://localhost:10000")
    print("📋 Для зупинки натисніть Ctrl+C")
    print("-" * 50)
    
    try:
        # Запускаємо Flask додаток
        port = int(os.environ.get("PORT", 10000))
        app.run(
            host="0.0.0.0", 
            port=port, 
            debug=True,
            use_reloader=False  # Вимикаємо reloader для уникнення подвійного запуску
        )
    except KeyboardInterrupt:
        print("\n🛑 Бот зупинено користувачем")
    except Exception as e:
        print(f"❌ Помилка запуску: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
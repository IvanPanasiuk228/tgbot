from flask import Flask, request
import requests
import json
import os
from datetime import date, timedelta
import random
import datetime

TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# === Всі ваші структури і функції для роботи з файлами ===
# Завантаження звичайних завдань
if os.path.exists("tasks.json"):
    with open("tasks.json", encoding="utf-8") as f:
        user_tasks = json.load(f)
else:
    user_tasks = {}

def save_tasks():
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(user_tasks, f, ensure_ascii=False)

# Завантаження балансу
if os.path.exists("scores.json"):
    with open("scores.json", encoding="utf-8") as f:
        user_scores = json.load(f)
else:
    user_scores = {}

def save_scores():
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(user_scores, f, ensure_ascii=False)

# Завантаження товарів
if os.path.exists("products.json"):
    with open("products.json", encoding="utf-8") as f:
        products = json.load(f)
else:
    products = [
        {"name": "Книга", "price": 10},
        {"name": "Кава", "price": 5},
        {"name": "Квиток у кіно", "price": 20}
    ]
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False)

def save_products():
    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False)

# Завантаження постійних завдань
if os.path.exists("permatasks.json"):
    with open("permatasks.json", encoding="utf-8") as f:
        permatasks = json.load(f)
else:
    permatasks = [
        {"name": "Зробити зарядку", "score": 2},
        {"name": "Почитати книгу", "score": 3},
        {"name": "Медитація", "score": 1.5}
    ]
    with open("permatasks.json", "w", encoding="utf-8") as f:
        json.dump(permatasks, f, ensure_ascii=False)

def save_permatasks():
    with open("permatasks.json", "w", encoding="utf-8") as f:
        json.dump(permatasks, f, ensure_ascii=False)

# Завантаження цілей
if os.path.exists("goals.json"):
    with open("goals.json", encoding="utf-8") as f:
        goals = json.load(f)
else:
    goals = []
    with open("goals.json", "w", encoding="utf-8") as f:
        json.dump(goals, f, ensure_ascii=False)

def save_goals():
    with open("goals.json", "w", encoding="utf-8") as f:
        json.dump(goals, f, ensure_ascii=False)

# Завантаження статистики користувача
if os.path.exists("user_stats.json"):
    with open("user_stats.json", encoding="utf-8") as f:
        user_stats = json.load(f)
else:
    user_stats = {}

def save_user_stats():
    with open("user_stats.json", "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False)

# Завантаження показаних фото для користувачів
if os.path.exists("user_shown_photos.json"):
    with open("user_shown_photos.json", encoding="utf-8") as f:
        user_shown_photos = json.load(f)
else:
    user_shown_photos = {}

def save_user_shown_photos():
    with open("user_shown_photos.json", "w", encoding="utf-8") as f:
        json.dump(user_shown_photos, f, ensure_ascii=False)

# === Всі ваші функції для розрахунків, бонусів, статистики ===
def calculate_score(time, difficulty, nb, mental, time_weight, difficulty_weight, nb_weight, mental_weight, task_priority):
    sum_weights = time_weight + difficulty_weight + nb_weight + mental_weight
    weighted_average = (
        time_weight * time +
        difficulty_weight * difficulty +
        nb_weight * nb +
        mental_weight * mental
    ) / sum_weights
    score = weighted_average * task_priority
    return score

def get_today_combo(user_id):
    today = str(date.today())
    stats_today = user_stats.setdefault(user_id, {}).setdefault(today, {})
    if "combo" in stats_today:
        return stats_today["combo"]
    # Якщо combo ще не встановлено для сьогодні, переносимо з учора
    yesterday = str(date.today() - timedelta(days=1))
    stats_yesterday = user_stats.get(user_id, {}).get(yesterday, {})
    prev_combo = stats_yesterday.get("combo", 1)
    done_yesterday = stats_yesterday.get("done", [])
    if len(done_yesterday) >= 5:
        new_combo = min(prev_combo + 0.25, 15)
    else:
        new_combo = 1
    stats_today["combo"] = new_combo
    save_user_stats()
    return new_combo

def update_user_stats_on_done(user_id, task_name, score):
    today = str(date.today())
    stats = user_stats.setdefault(user_id, {}).setdefault(today, {})
    stats.setdefault("done", []).append({"name": task_name, "score": score})
    # Оновлюємо combo через get_today_combo
    stats["combo"] = get_today_combo(user_id)
    stats["bonus"] = stats.get("bonus", 0)
    save_user_stats()
    if len(stats["done"]) == 3 and stats["bonus"] == 0:
        user_scores[user_id] = user_scores.get(user_id, 0) + 10
        stats["bonus"] = 10
        save_scores()

def get_daily_report(user_id):
    today = str(date.today())
    stats = user_stats.get(user_id, {}).get(today, {})
    done = stats.get("done", [])
    combo = get_today_combo(user_id)
    bonus = stats.get("bonus", 0)

    report = f"📅 {today}:\n"
    report += f"✅ Завдань виконано: {len(done)}\n"
    report += f"🔥 Combo: x{combo:.2f}\n"
    if bonus:
        report += f"🎯 Bonus: +{bonus:.2f}\n"
    report += "\n📊 Бали за день:\n"
    for item in done:
        report += f"- {item['name']}: {item['score']:.2f}\n"
    total = sum(item['score'] for item in done)
    multiplier = combo
    scores_str = ' + '.join([f"{item['score']:.2f}" for item in done])
    report += f"\n🎯 Сума: ({scores_str}) × {multiplier:.2f} = {total * multiplier:.2f}\n"
    if bonus:
        report += f"+ 🎯 Daily Quest: +{bonus:.2f}\n"
    final = total * multiplier + bonus
    report += f"\n✅ Фінал: {final:.2f} балів"
    
    # Додаємо порівняння з середніми показниками чоловіків
    if final > 0:
        report += f"\n\n💪 Зробив більше ніж 99% чоловіків за день!"
    
    return report

# === Функція для надсилання повідомлення ===
def send_message(chat_id, text, reply_markup=None, parse_mode=None):
    url = f"{TELEGRAM_API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
    requests.post(url, json=payload)

def send_main_menu(chat_id):
    keyboard = [
        [{"text": "Додати завдання", "callback_data": "add_task"}],
        [{"text": "Мої завдання", "callback_data": "my_tasks"}],
        [{"text": "Постійні завдання", "callback_data": "permatasks"}],
        [{"text": "Баланс", "callback_data": "my_score"}],
        [{"text": "Купити", "callback_data": "buy"}],
        [{"text": "Цілі", "callback_data": "goals"}],
        [{"text": "Статистика", "callback_data": "my_stats"}]
    ]
    reply_markup = json.dumps({"inline_keyboard": keyboard})
    send_message(chat_id, "Вітаю! Обери дію:", reply_markup=reply_markup)

# === Webhook endpoint ===
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        user_id = str(chat_id)
        # Тут розгалуження по командах і тексту
        if text == "/start":
            send_main_menu(chat_id)
        elif text == "/my_score":
            score = user_scores.get(user_id, 0)
            send_message(chat_id, f"Баланс: {score:.2f}⭐️")
        # ... (далі переносите всю логіку з handle_message, button_handler, тощо)
        else:
            send_message(chat_id, "Я отримав твоє повідомлення!")
    elif "callback_query" in data:
        # Тут логіка для inline-кнопок (callback_query)
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        user_id = str(chat_id)
        data_value = query["data"]
        # Далі розгалуження по data_value, наприклад:
        if data_value == "add_task":
            send_message(chat_id, "Введи текст завдання:")
        elif data_value == "my_score":
            score = user_scores.get(user_id, 0)
            send_message(chat_id, f"Баланс: {score:.2f}⭐️")
        # ... і так далі для інших кнопок
        send_message(chat_id, f"Оброблено callback: {data_value}")
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

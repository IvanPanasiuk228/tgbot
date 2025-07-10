from flask import Flask, request
import requests
import json
import os
from datetime import date, timedelta
import random
import datetime

print("=== РОБОЧИЙ MAIN.PY ЗАВАНТАЖУЄТЬСЯ ===")

TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

# === Всі ваші структури і функції для роботи з файлами ===
if os.path.exists("tasks.json"):
    with open("tasks.json", encoding="utf-8") as f:
        user_tasks = json.load(f)
else:
    user_tasks = {}

def save_tasks():
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(user_tasks, f, ensure_ascii=False)

if os.path.exists("scores.json"):
    with open("scores.json", encoding="utf-8") as f:
        user_scores = json.load(f)
else:
    user_scores = {}

def save_scores():
    with open("scores.json", "w", encoding="utf-8") as f:
        json.dump(user_scores, f, ensure_ascii=False)

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

if os.path.exists("user_stats.json"):
    with open("user_stats.json", encoding="utf-8") as f:
        user_stats = json.load(f)
else:
    user_stats = {}

def save_user_stats():
    with open("user_stats.json", "w", encoding="utf-8") as f:
        json.dump(user_stats, f, ensure_ascii=False)

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
    # Якщо комбо вже є для сьогодні - повертаємо його
    if "combo" in stats_today:
        return stats_today["combo"]
    
    # Інакше розраховуємо нове комбо
    yesterday = str(date.today() - timedelta(days=1))
    stats_yesterday = user_stats.get(user_id, {}).get(yesterday, {})
    prev_combo = stats_yesterday.get("combo", 1)
    done_yesterday = stats_yesterday.get("done", [])
    # Перевіряємо, чи вчора було виконано 5+ завдань
    if len(done_yesterday) >= 5:
        new_combo = min(prev_combo + 0.25, 15)  # +0.25 до комбо
    else:
        new_combo = 1  # Скидаємо до 1
    stats_today["combo"] = new_combo
    save_user_stats()
    return new_combo

def update_user_stats_on_done(user_id, task_name, score):
    today = str(date.today())
    stats = user_stats.setdefault(user_id, {}).setdefault(today, {})
    stats.setdefault("done", []).append({"name": task_name, "score": score})
    stats["combo"] = get_today_combo(user_id)
    stats["bonus"] = stats.get("bonus", 0)
    
    # Нараховуємо бали до балансу користувача
    combo = stats["combo"]
    earned_score = score * combo
    user_scores[user_id] = user_scores.get(user_id, 0) + earned_score
    
    # Зберігаємо зміни
    save_user_stats()
    save_scores()
    
    # Бонус за 3 завдання
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
    if final > 0:
        report += f"\n\n💪 Зробив більше ніж 99% чоловіків за день!"
    return report

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
    response = requests.post(url, json=payload)
    return response.json()

def edit_message(chat_id, message_id, text, reply_markup=None, parse_mode=None):
    """Редагує існуюче повідомлення"""
    url = f"{TELEGRAM_API_URL}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    if parse_mode:
        payload["parse_mode"] = parse_mode
    response = requests.post(url, json=payload)
    return response.json()

def send_main_menu(chat_id):
    keyboard = [
        [{"text": "Додати завдання", "callback_data": "add_task"}],
        [{"text": "Мої завдання", "callback_data": "my_tasks"}],
        [{"text": "Постійні завдання", "callback_data": "permatasks"}],
        [{"text": "Баланс", "callback_data": "my_score"}],
        [{"text": "Купити", "callback_data": "buy"}],
        [{"text": "Цілі", "callback_data": "goals"}],
        [{"text": "Статистика", "callback_data": "my_stats"}],
        [{"text": "Екстра бали", "callback_data": "extra_score"}]
    ]
    reply_markup = json.dumps({"inline_keyboard": keyboard})
    send_message(chat_id, "Вітаю! Обери дію:", reply_markup=reply_markup)

def send_back_button(chat_id, text):
    """Відправляє повідомлення з кнопкою 'Назад'"""
    keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
    reply_markup = json.dumps({"inline_keyboard": keyboard})
    send_message(chat_id, text, reply_markup=reply_markup)

pending_extra_score = {}

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    print(f"📨 Отримано webhook запит від Telegram")
    data = request.get_json()
    print(f"📋 Дані: {data}")
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        user_id = str(chat_id)
        if user_id in pending_extra_score and pending_extra_score[user_id]:
            try:
                extra = float(text)
                user_scores[user_id] = user_scores.get(user_id, 0) + extra
                save_scores()
                send_message(chat_id, f"Вам нараховано {extra}⭐️ екстра балів! Ваш новий баланс: {user_scores[user_id]:.2f}⭐️")
                pending_extra_score[user_id] = False
            except ValueError:
                send_message(chat_id, "Будь ласка, введіть число.")
        elif text == "/start":
            send_main_menu(chat_id)
        elif text == "/my_score":
            score = user_scores.get(user_id, 0)
            send_message(chat_id, f"Баланс: {score:.2f}⭐️")
            send_main_menu(chat_id)
        elif text.startswith("/add_task "):
            # Додавання завдання через команду
            task_text = text[10:]  # Видаляємо "/add_task "
            if task_text.strip():
                # Додаємо завдання до списку користувача
                if user_id not in user_tasks:
                    user_tasks[user_id] = []
                user_tasks[user_id].append(task_text)
                save_tasks()
                send_message(chat_id, f"Завдання '{task_text}' додано!")
            else:
                send_message(chat_id, "Будь ласка, вкажіть текст завдання після /add_task")
        elif text.startswith("/done "):
            # Позначення завдання як виконаного
            task_text = text[6:]  # Видаляємо "/done "
            if task_text.strip():
                # Розраховуємо бали (базова оцінка 5 балів)
                base_score = 5.0
                update_user_stats_on_done(user_id, task_text, base_score)
                send_message(chat_id, f"✅ Завдання '{task_text}' виконано! +{base_score:.2f}⭐️")
            else:
                send_message(chat_id, "Будь ласка, вкажіть текст завдання після /done")
        else:
            send_main_menu(chat_id)
    elif "callback_query" in data:
        query = data["callback_query"]
        chat_id = query["message"]["chat"]["id"]
        message_id = query["message"]["message_id"]
        user_id = str(chat_id)
        data_value = query["data"]
        
        if data_value == "back_to_menu":
            keyboard = [
                [{"text": "Додати завдання", "callback_data": "add_task"}],
                [{"text": "Мої завдання", "callback_data": "my_tasks"}],
                [{"text": "Постійні завдання", "callback_data": "permatasks"}],
                [{"text": "Баланс", "callback_data": "my_score"}],
                [{"text": "Купити", "callback_data": "buy"}],
                [{"text": "Цілі", "callback_data": "goals"}],
                [{"text": "Статистика", "callback_data": "my_stats"}],
                [{"text": "Екстра бали", "callback_data": "extra_score"}]
            ]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, "Вітаю! Обери дію:", reply_markup=reply_markup)
        elif data_value == "add_task":
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, "Введи текст завдання або використай команду /add_task [текст]", reply_markup=reply_markup)
        elif data_value == "my_score":
            score = user_scores.get(user_id, 0)
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, f"Баланс: {score:.2f}⭐️", reply_markup=reply_markup)
        elif data_value == "permatasks":
            keyboard = []
            for idx, t in enumerate(permatasks):
                keyboard.append([{
                    "text": f"{t['name']} ({t['score']}⭐️)",
                    "callback_data": f"do_permatask_{idx}"
                }])
            keyboard.append([{"text": "⬅️ Назад", "callback_data": "back_to_menu"}])
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, "Оберіть завдання для виконання:", reply_markup=reply_markup)
        elif data_value == "my_tasks":
            tasks = user_tasks.get(user_id, [])
            if tasks:
                text = "Ваші завдання:\n"
                for t in tasks:
                    text += f"- {t}\n"
            else:
                text = "У вас немає завдань."
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, text, reply_markup=reply_markup)
        elif data_value == "buy":
            text = "Магазин:\n"
            for p in products:
                text += f"- {p['name']} ({p['price']}⭐️)\n"
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, text, reply_markup=reply_markup)
        elif data_value == "goals":
            if goals:
                text = "Ваші цілі:\n"
                for g in goals:
                    text += f"- {g}\n"
            else:
                text = "У вас немає цілей."
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, text, reply_markup=reply_markup)
        elif data_value == "my_stats":
            report = get_daily_report(user_id)
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, report, reply_markup=reply_markup)
        elif data_value == "extra_score":
            pending_extra_score[user_id] = True
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, "Введіть кількість екстра балів, яку хочете нарахувати:", reply_markup=reply_markup)
        elif data_value.startswith("do_permatask_"):
            idx = int(data_value.split("_")[-1])
            task = permatasks[idx]
            reward = task["score"]
            user_scores[user_id] = user_scores.get(user_id, 0) + reward
            save_scores()
            update_user_stats_on_done(user_id, task["name"], reward)
            keyboard = [[{"text": "⬅️ Назад", "callback_data": "back_to_menu"}]]
            reply_markup = json.dumps({"inline_keyboard": keyboard})
            edit_message(chat_id, message_id, f"Ви виконали: {task['name']}! +{reward}⭐️ до балансу.", reply_markup=reply_markup)
    return "ok"

@app.route("/", methods=["GET"])
def index():
    return "Bot is running!"

@app.route("/test", methods=["GET"])
def test():
    print("=== ЦЕ ТОЧНО ТОЙ main.py ===")
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

@app.route("/reset_balance/<user_id>", methods=["GET"])
def reset_balance(user_id):
    """Скидає баланс користувача до 0"""
    if user_id in user_scores:
        user_scores[user_id] = 0
        save_scores()
        return f"Баланс користувача {user_id} скинуто до 0"
    return f"Користувача {user_id} не знайдено"

@app.route("/set_balance/<user_id>/<float:amount>", methods=["GET"])
def set_balance(user_id, amount):
    """Встановлює баланс користувача"""
    user_scores[user_id] = amount
    save_scores()
    return f"Баланс користувача {user_id} встановлено на {amount}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

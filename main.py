from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import json
import os
from datetime import date, timedelta
import random
import datetime
import threading
from telegram.error import TelegramError
import threading

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

# Формула підрахунку балів
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

# /start команда
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Start handler called!")
    try:
        await update.message.reply_text("Вітаю! Обери дію:")
    except Exception as e:
        print(f"Error in start handler: {e}")

# Підменю для завдань
async def tasks_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Додати завдання", callback_data="add_task")],
        [InlineKeyboardButton("Мої завдання", callback_data="my_tasks")],
        [InlineKeyboardButton("Постійні завдання", callback_data="permatasks")],
        [InlineKeyboardButton("← Назад", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.edit_message_text("Меню завдань:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Меню завдань:", reply_markup=reply_markup)

# Команда для отримання chat_id
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Ваш user_id: {user_id}\nВаш chat_id: {chat_id}")

# Обробка кнопок меню
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = str(query.from_user.id)
    if query.data == "add_task":
        context.user_data["adding_task"] = True
        context.user_data["task_stage"] = "text"
        await query.edit_message_text("Введи текст завдання:")
    elif query.data == "my_tasks":
        tasks = user_tasks.get(user_id, [])
        if tasks:
            keyboard = []
            for idx, task in enumerate(tasks):
                keyboard.append([InlineKeyboardButton(f"Виконано {idx+1}", callback_data=f"done_{idx}")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Твої завдання:\n" + "\n".join(f"{i+1}. {t}" for i, t in enumerate(tasks)),
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("У тебе ще немає завдань.")
    elif query.data == "permatasks":
        keyboard = []
        for idx, task in enumerate(permatasks):
            keyboard.append([InlineKeyboardButton(f"Виконано '{task['name']}'", callback_data=f"permadone_{idx}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        task_list = "\n".join([f"{i+1}. {t['name']} — {t['score']:.2f}⭐️" for i, t in enumerate(permatasks)])
        await query.edit_message_text(f"Постійні завдання:\n{task_list}", reply_markup=reply_markup)
    elif query.data == "my_score":
        score = user_scores.get(user_id, 0)
        await query.edit_message_text(f"Баланс: {score:.2f}⭐️")
    elif query.data == "buy":
        keyboard = []
        for idx, product in enumerate(products):
            keyboard.append([InlineKeyboardButton(f"Купити '{product['name']}' за {product['price']:.2f}⭐️", callback_data=f"buy_{idx}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        product_list = "\n".join([f"{i+1}. {p['name']} — {p['price']:.2f}⭐️" for i, p in enumerate(products)])
        await query.edit_message_text(f"Доступні товари:\n{product_list}", reply_markup=reply_markup)
    elif query.data == "goals":
        keyboard = []
        for idx, goal in enumerate(goals):
            keyboard.append([InlineKeyboardButton(f"Виконано '{goal['name']}'", callback_data=f"goal_done_{idx}")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        goal_list = "\n".join([f"{i+1}. {g['name']} — {g['score']:.2f}⭐️" for i, g in enumerate(goals)])
        await query.edit_message_text(f"Твої цілі:\n{goal_list}", reply_markup=reply_markup)
    elif query.data.startswith("done_"):
        idx = int(query.data.split("_")[1])
        tasks = user_tasks.get(user_id, [])
        if 0 <= idx < len(tasks):
            task = tasks.pop(idx)
            import re
            match = re.search(r"Бали: ([0-9.]+)", task)
            score = float(match.group(1)) if match else 0
            user_scores[user_id] = user_scores.get(user_id, 0) + score
            save_tasks()
            save_scores()
            update_user_stats_on_done(user_id, task, score)
            await query.edit_message_text(f"Завдання виконано! +{score:.2f}⭐️\nТвій новий баланс: {user_scores[user_id]:.2f}")
        else:
            await query.edit_message_text("Завдання не знайдено.")
    elif query.data.startswith("permadone_"):
        idx = int(query.data.split("_")[1])
        if 0 <= idx < len(permatasks):
            task = permatasks[idx]
            user_scores[user_id] = user_scores.get(user_id, 0) + task["score"]
            save_scores()
            update_user_stats_on_done(user_id, task["name"], task["score"])
            await query.edit_message_text(
                f"Завдання '{task['name']}' виконано! +{task['score']:.2f}⭐️\nТвій новий баланс: {user_scores[user_id]:.2f}"
            )
        else:
            await query.edit_message_text("Завдання не знайдено.")
    elif query.data.startswith("buy_"):
        idx = int(query.data.split("_")[1])
        if 0 <= idx < len(products):
            product = products[idx]
            price = product["price"]
            score = user_scores.get(user_id, 0)
            if score >= price:
                user_scores[user_id] = score - price
                save_scores()
                await query.edit_message_text(f"Ти купив(ла) '{product['name']}' за {price:.2f}⭐️!\nТвій новий баланс: {user_scores[user_id]:.2f}")
                # Якщо у товару є url, надсилаємо його
                if "url" in product:
                    await context.bot.send_message(chat_id=query.message.chat_id, text=f"Посилання на товар: {product['url']}")
                # Якщо у товару є file_ids (масив фото)
                if "file_ids" in product:
                    shown = user_shown_photos.get(user_id, [])
                    available = [fid for fid in product["file_ids"] if fid not in shown]
                    if available:
                        chosen = random.choice(available)
                        await context.bot.send_photo(chat_id=query.message.chat_id, photo=chosen)
                        shown.append(chosen)
                        user_shown_photos[user_id] = shown
                        save_user_shown_photos()
                # Якщо є photo_url, надсилаємо фото
                if "photo_url" in product:
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=product["photo_url"])
                # Якщо є video_url, надсилаємо відео
                if "video_url" in product:
                    await context.bot.send_video(chat_id=query.message.chat_id, video=product["video_url"])
            else:
                await query.edit_message_text(f"Недостатньо балів для покупки '{product['name']}'. Твій баланс: {score:.2f}")
        else:
            await query.edit_message_text("Товар не знайдено.")
    elif query.data.startswith("goal_done_"):
        idx = int(query.data.split("_")[2])
        if 0 <= idx < len(goals):
            goal = goals.pop(idx)
            user_scores[user_id] = user_scores.get(user_id, 0) + goal["score"]
            save_goals()
            save_scores()
            update_user_stats_on_done(user_id, goal["name"], goal["score"])
            await query.edit_message_text(
                f"Ціль '{goal['name']}' виконано! +{goal['score']:.2f}⭐️\nТвій новий баланс: {user_scores[user_id]:.2f}"
            )
        else:
            await query.edit_message_text("Ціль не знайдено.")
    elif query.data == "extra":
        context.user_data["adding_extra"] = True
        await query.edit_message_text("Введи кількість екстра балів, які хочеш додати:")
    elif query.data == "my_stats":
        report = get_daily_report(user_id)
        await query.edit_message_text(report)
    elif query.data == "top_1_percent":
        top_1_percent_text = """💪 **ПЛАН ДНЯ: СИЛЬНЕ НІЖ 99% ЧОЛОВІКІВ**

👨‍💻 **Програмування** — 6–8 год
🗣 **Мови** — 3–4 год (говоріння, граматика, аудіо)
🏋️‍♂️ **Зал** — 1 год 
❄️ **Холодний душ** 2 рази
🧘‍♂️ **Медитація** — 30 хв
⚔️ **Виклик**
🎧 **Аудіо-лекції** — 1–2 год (під час їжі / прогулянки / сауни)
🔥 **Сауна** — 15–30 хв

**🎯 ЦЕ ТВОЙ ШАНС СТАТИ ЛЕГЕНДОЮ**

Кожен день, коли ти виконуєш цей план, ти стаєш сильнішим ніж 99% чоловіків на планеті.

**🪓 STAY HARD.**"""
        
        keyboard = [
            [InlineKeyboardButton("✅ Виконано", callback_data="top_1_percent_done")],
            [InlineKeyboardButton("← Назад до меню", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(top_1_percent_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif query.data == "top_1_percent_done":
        # Збільшуємо комбо на 0.25
        today = str(date.today())
        stats = user_stats.setdefault(user_id, {}).setdefault(today, {})
        current_combo = stats.get("combo", 1)
        new_combo = current_combo + 0.25
        stats["combo"] = new_combo
        save_user_stats()
        
        await query.edit_message_text(
            f"💪 **ПЛАН ВИКОНАНО!**\n\n"
            f"🔥 Твій комбо збільшено: {current_combo:.2f} → {new_combo:.2f}\n\n"
            f"**Ти дійсно сильніший ніж 99% чоловіків!**\n\n"
            f"🪓 Stay hard.",
            parse_mode='Markdown'
        )
    elif query.data == "back_to_menu":
        await start(update, context)

# Покрокове додавання завдання
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("handle_message called!")
    user_id = str(update.effective_user.id)
    text = update.message.text.lower().strip()
    # Ключові слова для запуску меню
    if text in ["меню", "старт", "start", "почати"]:
        await start(update, context)
        return
    if context.user_data.get("adding_extra"):
        try:
            extra = float(update.message.text)
            user_scores[user_id] = user_scores.get(user_id, 0) + extra
            save_scores()
            context.user_data["adding_extra"] = False
            await update.message.reply_text(f"Додано {extra:.2f}⭐️ до твого балансу!\nТепер твій баланс: {user_scores[user_id]:.2f}⭐️")
        except Exception:
            await update.message.reply_text("Введи число для екстра балів!")
        return
    if context.user_data.get("adding_task"):
        stage = context.user_data.get("task_stage")
        if stage == "text":
            context.user_data["new_task_text"] = update.message.text
            context.user_data["task_stage"] = "time"
            await update.message.reply_text("Введи час виконання (наприклад, 2):")
        elif stage == "time":
            try:
                context.user_data["new_task_time"] = float(update.message.text)
                context.user_data["task_stage"] = "difficulty"
                await update.message.reply_text("Введи складність (1-10):")
            except ValueError:
                await update.message.reply_text("Введи число для часу виконання!")
        elif stage == "difficulty":
            try:
                context.user_data["new_task_difficulty"] = float(update.message.text)
                context.user_data["task_stage"] = "nb"
                await update.message.reply_text("Введи НБ (1-10):")
            except ValueError:
                await update.message.reply_text("Введи число для складності!")
        elif stage == "nb":
            try:
                context.user_data["new_task_nb"] = float(update.message.text)
                context.user_data["task_stage"] = "mental"
                await update.message.reply_text("Введи ментальну силу (1-10):")
            except ValueError:
                await update.message.reply_text("Введи число для НБ!")
        elif stage == "mental":
            try:
                context.user_data["new_task_mental"] = float(update.message.text)
                context.user_data["task_stage"] = "priority"
                await update.message.reply_text("Введи пріоритет (наприклад, 1.5):")
            except ValueError:
                await update.message.reply_text("Введи число для ментальної сили!")
        elif stage == "priority":
            try:
                context.user_data["new_task_priority"] = float(update.message.text)
                time = context.user_data["new_task_time"]
                difficulty = context.user_data["new_task_difficulty"]
                nb = context.user_data["new_task_nb"]
                mental = context.user_data["new_task_mental"]
                task_priority = context.user_data["new_task_priority"]
                time_weight = 1
                difficulty_weight = 2
                nb_weight = 3
                mental_weight = 1
                score = calculate_score(time, difficulty, nb, mental, time_weight, difficulty_weight, nb_weight, mental_weight, task_priority)
                task_text = context.user_data.get("new_task_text", "(без назви)")
                task_full = f"{task_text} (Бали: {score:.2f}⭐️)"
                user_tasks.setdefault(user_id, []).append(task_full)
                save_tasks()
                context.user_data.clear()
                await update.message.reply_text(
                    f"Завдання додано!\n\n"
                    f"Текст: {task_text}\n"
                    f"Час: {time}\n"
                    f"Складність: {difficulty}\n"
                    f"НБ: {nb}\n"
                    f"Ментальна сила: {mental}\n"
                    f"Пріоритет: {task_priority}\n"
                    f"Бали: {score:.2f}⭐️"
                )
            except ValueError:
                await update.message.reply_text("Введи число для пріоритету!")
    else:
        pass

# Функція для автоматичного повідомлення про зал
async def send_gym_reminder(context: ContextTypes.DEFAULT_TYPE):
    # Ваш chat_id
    YOUR_CHAT_ID = 5575102874
    try:
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID, 
            text="🏋️ Ти сьогодні вже був у залі?"
        )
    except Exception as e:
        print(f"Помилка надсилання повідомлення: {e}")

# Функція для щоденного звіту
async def send_daily_report(context: ContextTypes.DEFAULT_TYPE):
    # Ваш chat_id
    YOUR_CHAT_ID = 5575102874
    
    # Дата початку (завтрашня дата)
    start_date = date.today() + timedelta(days=1)  # Завтра
    today = date.today()
    
    # Підрахунок днів
    days_passed = (today - start_date).days + 1
    total_days = 365
    progress_percent = (days_passed / total_days) * 100
    
    # Масив цитат для мотивації
    quotes = [
        "Ніхто не прийде тебе рятувати. Ніхто не змусить тебе вставати рано. Ніхто не прокладе шлях. Це твій хрест і твій шанс.\nТи або ростеш, або здаєшся. Середини немає.",
        "Ти не можеш контролювати результат, але можеш контролювати зусилля.",
        "Кожен день - це нова можливість стати кращою версією себе.",
        "Сила не в тому, скільки ти можеш підняти, а в тому, скільки разів ти можеш піднятися після падіння.",
        "Твоє тіло може майже все. Твоя голова - це те, що тебе обмежує.",
        "Сьогодні я зроблю те, що інші не хочуть, щоб завтра я мав те, що інші не можуть.",
        "Ти не програєш, поки не здаєшся.",
        "Кожен крок вперед - це перемога над вчорашнім собою.",
        "Ти сильніший, ніж думаєш, і зможеш більше, ніж уявляєш.",
        "Сьогоднішні жертви - це завтрашні перемоги."
    ]
    
    # Вибираємо цитату на основі дня (щоб вона змінювалася)
    quote_index = days_passed % len(quotes)
    daily_quote = quotes[quote_index]
    
    report_text = f"""📅 День {days_passed}/365
📈 Прогрес: {progress_percent:.1f}%

"{daily_quote}"

🪓 Stay hard."""
    
    try:
        await context.bot.send_message(
            chat_id=YOUR_CHAT_ID,
            text=report_text
        )
    except Exception as e:
        print(f"Помилка надсилання щоденного звіту: {e}")

# === Flask app for webhook ===
TOKEN = "8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE"
WEBHOOK_PATH = f"/{TOKEN}"
# Змініть на свою адресу Render нижче!
WEBHOOK_URL = f"https://tgbot-kqfh.onrender.com/{TOKEN}"

# === PTB Application ===
telegram_app = ApplicationBuilder().token(TOKEN).build()

async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        await update.message.reply_text(f"Photo file_id: {file_id}")
    elif update.message.video:
        file_id = update.message.video.file_id
        await update.message.reply_text(f"Video file_id: {file_id}")
    else:
        await update.message.reply_text("Надішліть фото або відео у відповідь на цю команду.")

# Додаємо всі handler-и
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("get_id", get_id))
telegram_app.add_handler(CallbackQueryHandler(button_handler))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
telegram_app.add_handler(MessageHandler((filters.PHOTO | filters.VIDEO) & ~filters.COMMAND, get_file_id))

# Job Queue (нагадування)
def setup_jobs():
    telegram_app.job_queue.run_daily(
        send_gym_reminder,
        time=datetime.time(hour=6, minute=0),
    )
    telegram_app.job_queue.run_daily(
        send_daily_report,
        time=datetime.time(hour=9, minute=0),
    )
    print("Бот запущено!")
    print("Автоматичні повідомлення про зал налаштовано на 6:00 щодня")
    print("Автоматичні щоденні звіти налаштовано на 9:00 щодня")

# === Flask endpoint для Telegram webhook ===
if __name__ == "__main__":
    setup_jobs()
    port = int(os.environ.get("PORT", 10000))
    telegram_app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=WEBHOOK_URL,
        drop_pending_updates=True
    )

# === Інструкція ===
# Після деплою на Render, зареєструйте webhook для вашого бота:
# curl -F "url=https://ВАШ-РЕНДЕР-АДРЕСА.onrender.com/8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE" https://api.telegram.org/bot8076795269:AAG0z1_n31zSeLxk_z-PKJZLv_rv3JR5XHE/setWebhook
# Замість ВАШ-РЕНДЕР-АДРЕСА.onrender.com підставте свою адресу Render Web Service.

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

async def error_handler(update, context):
    print("Exception while handling an update!")
    print(f"Update: {update}")
    print(f"Context error: {context.error}")

telegram_app.add_error_handler(error_handler)

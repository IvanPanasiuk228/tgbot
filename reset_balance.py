import json
import os

def reset_user_balance(user_id):
    """Скидає баланс користувача до 0"""
    if os.path.exists("scores.json"):
        with open("scores.json", "r", encoding="utf-8") as f:
            user_scores = json.load(f)
    else:
        user_scores = {}
    
    user_id_str = str(user_id)
    if user_id_str in user_scores:
        old_balance = user_scores[user_id_str]
        user_scores[user_id_str] = 0
        with open("scores.json", "w", encoding="utf-8") as f:
            json.dump(user_scores, f, ensure_ascii=False)
        print(f"✅ Баланс користувача {user_id_str} скинуто з {old_balance} до 0")
    else:
        print(f"❌ Користувача {user_id_str} не знайдено")

if __name__ == "__main__":
    # Скидаємо баланс для вашого ID
    reset_user_balance("5575102874") 
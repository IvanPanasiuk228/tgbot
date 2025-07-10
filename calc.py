from score_utils import calculate_score

def main():
    print("Підрахунок балів для постійного завдання")
    try:
        time = float(input("Введи час виконання: "))
        difficulty = float(input("Введи складність (1-10): "))
        nb = float(input("Введи НБ (1-10): "))
        mental = float(input("Введи ментальну силу (1-10): "))
        task_priority = float(input("Введи пріоритет (наприклад, 1.5): "))

        # Можеш змінити ваги тут
        time_weight = 1
        difficulty_weight = 2
        nb_weight = 3
        mental_weight = 1

        score = calculate_score(time, difficulty, nb, mental, time_weight, difficulty_weight, nb_weight, mental_weight, task_priority)
        print(f"Бали за завдання: {score:.2f}⭐️")
    except Exception as e:
        print("Помилка! Введи всі значення правильно.")

if __name__ == "__main__":
    main()
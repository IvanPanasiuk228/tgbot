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

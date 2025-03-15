def calculate_bmi_adjusted_goals(bmi, base_goals):
    adjusted_goals = base_goals.copy()
    if bmi < 18.5:  # Underweight
        adjusted_goals["calories"] *= 1.15
        adjusted_goals["protein"] *= 1.2
        adjusted_goals["carbs"] *= 1.1
    elif 25 <= bmi < 30:  # Overweight
        adjusted_goals["calories"] *= 0.9
        adjusted_goals["carbs"] *= 0.85
        adjusted_goals["fat"] *= 0.9
    elif bmi >= 30:  # Obese
        adjusted_goals["calories"] *= 0.8
        adjusted_goals["carbs"] *= 0.7
        adjusted_goals["fat"] *= 0.8
    for key in adjusted_goals:
        adjusted_goals[key] = round(adjusted_goals[key])
    return adjusted_goals

# Diet Type Configurations
DIET_GOALS = {
    "Standard": {"calories": 2000, "protein": 50, "carbs": 250, "fat": 70},
    "Keto": {"calories": 1800, "protein": 90, "carbs": 50, "fat": 155},
    "Vegan": {"calories": 2200, "protein": 60, "carbs": 300, "fat": 65}
}
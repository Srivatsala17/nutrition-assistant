from langchain_core.tools import tool

from core.vector_store import search_foods
from db import crud


def make_tools(user_id: int):
    """Build tools tied to one user, so the LLM never has to pass a user id."""
    user = crud.get_user(user_id)
    allergy_words = [a.strip().lower() for a in user["allergies"].split(",") if a.strip()]

    def is_safe(food):
        name = food["name"].lower()
        return not any(a in name for a in allergy_words)

    @tool
    def search_food_database(query: str, min_protein: float = 0,
                             max_calories: float = 0, k: int = 5) -> str:
        """Search the food database for foods matching a description.
        Use for meal ideas and nutrition facts.
        min_protein: only foods with at least this many grams of protein (0 = no limit).
        max_calories: only foods with at most this many kcal (0 = no limit).
        Returns numbered foods with their source for citation."""
        diet = "veg" if user["diet"] == "veg" else None
        foods = search_foods(query, k=40, diet=diet)
        foods = [f for f in foods if is_safe(f)]
        if min_protein:
            foods = [f for f in foods if f["protein"] >= min_protein]
            foods.sort(key=lambda f: f["protein"], reverse=True)
        if max_calories:
            foods = [f for f in foods if f["calories"] <= max_calories]
        foods = foods[:k]
        if not foods:
            return "No matching foods found."
        return "\n".join(
            f"[{i}] {f['name']}: {f['calories']} kcal, {f['protein']}g protein, "
            f"{f['carbs']}g carbs, {f['fat']}g fat (source: {f['source']})"
            for i, f in enumerate(foods, start=1)
        )

    @tool
    def log_meal(food_name: str, servings: float = 1,
                 meal_type: str = "snack") -> str:
        """Log food the user ate. Looks up nutrition automatically.
        servings: number of servings (e.g. 2 for '2 rotis').
        meal_type: breakfast, lunch, dinner or snack."""
        matches = [f for f in search_foods(food_name, k=5) if is_safe(f)]
        if not matches:
            return f"Could not find '{food_name}' in the database."
        f = matches[0]
        crud.log_meal(user_id, f["name"], f["calories"] * servings,
                      f["protein"] * servings, f["carbs"] * servings,
                      f["fat"] * servings, meal_type)
        return (f"Logged {servings} x {f['name']} "
                f"({round(f['calories'] * servings)} kcal) "
                f"(source: {f['source']})")

    @tool
    def log_weight(weight_kg: float) -> str:
        """Record the user's current body weight in kg."""
        crud.log_weight(user_id, weight_kg)
        return f"Logged weight: {weight_kg} kg"

    @tool
    def get_remaining_calories() -> str:
        """Get today's calorie target, calories eaten, and calories remaining."""
        return str(crud.get_remaining_calories(user_id))

    @tool
    def get_weekly_summary() -> str:
        """Get the last 7 days of calories and weight, for progress questions."""
        return str(crud.get_weekly_summary(user_id))

    return [search_food_database, log_meal, log_weight,
            get_remaining_calories, get_weekly_summary]
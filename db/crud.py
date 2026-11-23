from datetime import datetime, timedelta, date

from sqlalchemy import func

from db.database import SessionLocal
from db.models import User, Meal, WeightLog

ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
}


def calculate_calorie_target(age, gender, height_cm, weight_kg, activity_level, goal):
    """Mifflin-St Jeor formula, then adjust for the goal."""
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age
    bmr += 5 if gender.lower() == "male" else -161
    tdee = bmr * ACTIVITY_FACTORS.get(activity_level, 1.55)
    if goal == "lose":
        tdee -= 500
    elif goal == "gain":
        tdee += 300
    return int(max(tdee, 1200))  # never go below 1200 kcal


def create_user(name, age, gender, height_cm, weight_kg, goal, diet,
                allergies="", activity_level="moderate"):
    target = calculate_calorie_target(age, gender, height_cm, weight_kg,
                                      activity_level, goal)
    with SessionLocal() as db:
        user = User(name=name, age=age, gender=gender, height_cm=height_cm,
                    weight_kg=weight_kg, goal=goal, diet=diet,
                    allergies=allergies, activity_level=activity_level,
                    calorie_target=target)
        db.add(user)
        db.flush()  # get the new id
        db.add(WeightLog(user_id=user.id, weight_kg=weight_kg))
        db.commit()
        return user.id


def get_user(user_id):
    with SessionLocal() as db:
        u = db.get(User, user_id)
        if not u:
            return None
        return {
            "id": u.id, "name": u.name, "age": u.age, "gender": u.gender,
            "height_cm": u.height_cm, "weight_kg": u.weight_kg, "goal": u.goal,
            "diet": u.diet, "allergies": u.allergies,
            "activity_level": u.activity_level, "calorie_target": u.calorie_target,
        }


def log_meal(user_id, food_name, calories, protein=0, carbs=0, fat=0,
             meal_type="snack"):
    with SessionLocal() as db:
        db.add(Meal(user_id=user_id, food_name=food_name, meal_type=meal_type,
                    calories=calories, protein=protein, carbs=carbs, fat=fat))
        db.commit()


def log_weight(user_id, weight_kg):
    with SessionLocal() as db:
        db.add(WeightLog(user_id=user_id, weight_kg=weight_kg))
        user = db.get(User, user_id)
        user.weight_kg = weight_kg
        db.commit()


def get_today_meals(user_id):
    start = datetime.combine(date.today(), datetime.min.time())
    with SessionLocal() as db:
        rows = (db.query(Meal)
                  .filter(Meal.user_id == user_id, Meal.logged_at >= start)
                  .order_by(Meal.logged_at).all())
        return [{"food": m.food_name, "meal_type": m.meal_type,
                 "calories": m.calories, "protein": m.protein,
                 "carbs": m.carbs, "fat": m.fat} for m in rows]


def get_remaining_calories(user_id):
    user = get_user(user_id)
    meals = get_today_meals(user_id)
    eaten = sum(m["calories"] for m in meals)
    return {
        "target": user["calorie_target"],
        "eaten": round(eaten),
        "remaining": round(user["calorie_target"] - eaten),
        "protein_eaten": round(sum(m["protein"] for m in meals)),
    }


def get_weight_history(user_id, days=60):
    since = datetime.now() - timedelta(days=days)
    with SessionLocal() as db:
        rows = (db.query(WeightLog)
                  .filter(WeightLog.user_id == user_id, WeightLog.logged_at >= since)
                  .order_by(WeightLog.logged_at).all())
        return [{"date": w.logged_at.strftime("%Y-%m-%d"), "weight_kg": w.weight_kg}
                for w in rows]


def get_weekly_summary(user_id):
    since = datetime.now() - timedelta(days=7)
    with SessionLocal() as db:
        rows = (db.query(func.date(Meal.logged_at), func.sum(Meal.calories))
                  .filter(Meal.user_id == user_id, Meal.logged_at >= since)
                  .group_by(func.date(Meal.logged_at)).all())
    daily = {str(d): round(float(c)) for d, c in rows}
    avg = round(sum(daily.values()) / len(daily)) if daily else 0
    return {
        "daily_calories": daily,
        "average_calories": avg,
        "target": get_user(user_id)["calorie_target"],
        "weight_history": get_weight_history(user_id, days=7),
    }
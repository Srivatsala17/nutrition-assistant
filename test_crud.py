from db import crud

uid = crud.create_user(
    name="Test User", age=25, gender="female", height_cm=160, weight_kg=60,
    goal="lose", diet="veg", allergies="peanuts", activity_level="light",
)
print("User id:", uid)
print("Profile:", crud.get_user(uid))

crud.log_meal(uid, "Roti", 120, 3, 20, 3, "lunch")
crud.log_meal(uid, "Dal tadka", 150, 9, 20, 4, "lunch")
crud.log_weight(uid, 59.5)

print("Remaining:", crud.get_remaining_calories(uid))
print("Today:", crud.get_today_meals(uid))
print("Weekly:", crud.get_weekly_summary(uid))
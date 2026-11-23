from core.tools import make_tools

USER_ID = 1  # change to your id

tools = {t.name: t for t in make_tools(USER_ID)}

print(tools["search_food_database"].invoke(
    {"query": "high protein snack", "min_protein": 10}))
print()
print(tools["log_meal"].invoke({"food_name": "roti", "servings": 2, "meal_type": "dinner"}))
print(tools["get_remaining_calories"].invoke({}))
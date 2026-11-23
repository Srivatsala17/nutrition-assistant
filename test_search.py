from core.vector_store import search_foods

for q, diet in [("high protein vegetarian", "veg"), ("low calorie snack", None)]:
    print("\nQuery:", q)
    for r in search_foods(q, k=5, diet=diet):
        print(f"- {r['name']} | {r['calories']} kcal | {r['protein']}g protein | "
              f"{r['diet']} | score {r['score']} | source: {r['source']}")
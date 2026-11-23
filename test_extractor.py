from core.food_extractor import extract_foods

for s in ["i had 2 rotis and dal tadka for lunch",
          "ate a banana and 3 idli this morning",
          "how many calories are left today"]:
    print(s, "->", extract_foods(s))
import re
import pandas as pd
import config

RAW_CSV = "data/raw_foods.csv"
SOURCE = "Kaggle: Indian Food Nutrition Dataset"

NON_VEG_WORDS = [
    "chicken", "mutton", "fish", "egg", "eggs", "prawn", "prawns", "shrimp",
    "lamb", "beef", "pork", "keema", "crab", "meat", "tuna", "salmon",
    "bacon", "ham", "sausage", "anda", "gosht", "murgh", "machhli",
]
NON_VEG_PATTERN = re.compile(r"\b(" + "|".join(NON_VEG_WORDS) + r")\b", re.IGNORECASE)


def guess_diet(name: str) -> str:
    return "non-veg" if NON_VEG_PATTERN.search(name) else "veg"


def main():
    df = pd.read_csv(RAW_CSV)

    df = df.rename(columns={
        "Dish Name": "name",
        "Calories (kcal)": "calories",
        "Carbohydrates (g)": "carbs",
        "Protein (g)": "protein",
        "Fats (g)": "fat",
        "Fibre (g)": "fibre",
        "Free Sugar (g)": "sugar",
        "Sodium (mg)": "sodium",
        "Calcium (mg)": "calcium",
        "Iron (mg)": "iron",
    })

    keep = ["name", "calories", "protein", "carbs", "fat",
            "fibre", "sugar", "sodium", "calcium", "iron"]
    df = df[keep]

    df["name"] = df["name"].astype(str).str.strip()
    for col in keep[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["name", "calories", "protein", "carbs", "fat"])
    df = df[df["calories"] > 0]
    df = df.drop_duplicates(subset="name").reset_index(drop=True)

    df["diet"] = df["name"].apply(guess_diet)
    df["source"] = SOURCE

    df.to_csv(config.FOODS_CSV, index=False)
    print("Saved", len(df), "foods to", config.FOODS_CSV)
    print(df["diet"].value_counts())
    print(df.head())


if __name__ == "__main__":
    main()
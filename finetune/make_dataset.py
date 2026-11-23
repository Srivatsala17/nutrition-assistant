import json
import random
import re
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import pandas as pd
import config

random.seed(42)

df = pd.read_csv(config.FOODS_CSV)
names = [n.lower().strip() for n in df["name"]]
names = [n for n in names if re.fullmatch(r"[a-z' ]+", n)
         and 1 <= len(n.split()) <= 4 and " and " not in n]

QTY = ["1", "2", "3", "4", "one", "two", "three", "a", "an", "half", "2.5", "1.5"]
STARTS = ["i had", "i ate", "i just ate", "for lunch i had", "for dinner i ate",
          "had", "ate", "just finished", "my breakfast was", "i consumed", "i have eaten"]
ENDS = ["", "", "for lunch", "for dinner", "for breakfast", "as a snack",
        "today", "this morning", "last night"]
CONNECTORS = ["and", "and", "with", "plus", ","]
NEGATIVES = ["how many calories are left today", "what should i eat tonight",
             "show my weekly summary", "i weigh 62 kg now", "suggest a high protein dinner",
             "how was my week", "what is my calorie target"]


def make_sample():
    if random.random() < 0.05:
        tokens = random.choice(NEGATIVES).split()
        return {"tokens": tokens, "labels": ["O"] * len(tokens)}

    tokens, labels = [], []
    for w in random.choice(STARTS).split():
        tokens.append(w); labels.append("O")

    for i in range(random.choice([1, 1, 2, 2, 3])):
        if i > 0:
            tokens.append(random.choice(CONNECTORS)); labels.append("O")
        if random.random() < 0.8:
            tokens.append(random.choice(QTY)); labels.append("QTY")
        for j, w in enumerate(random.choice(names).split()):
            tokens.append(w)
            labels.append("B-FOOD" if j == 0 else "I-FOOD")

    for w in random.choice(ENDS).split():
        tokens.append(w); labels.append("O")
    return {"tokens": tokens, "labels": labels}


data = [make_sample() for _ in range(3000)]
out = Path(__file__).parent / "ner_data.json"
out.write_text(json.dumps(data))
print("Saved", len(data), "samples to", out)
for s in data[:3]:
    print(list(zip(s["tokens"], s["labels"])))
from functools import lru_cache
from pathlib import Path

import config

MODEL_DIR = Path(config.BASE_DIR) / "finetune" / "food_ner_model"

QTY_WORDS = {
    "a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "half": 0.5,
}


@lru_cache(maxsize=1)
def _get_pipeline():
    if not MODEL_DIR.exists():
        return None
    from transformers import pipeline
    return pipeline(
        "token-classification",
        model=str(MODEL_DIR),
        tokenizer=str(MODEL_DIR),
        aggregation_strategy="simple",
        device=-1,  # CPU is fine for short sentences
    )


def _parse_qty(word):
    word = word.lower().strip()
    if word in QTY_WORDS:
        return QTY_WORDS[word]
    try:
        return float(word)
    except ValueError:
        return 1


def extract_foods(text):
    """Return a list of (servings, food_name). Empty list if the model is missing."""
    ner = _get_pipeline()
    if ner is None:
        return []
    items, pending_qty = [], None
    for ent in sorted(ner(text), key=lambda e: e["start"]):
        if ent["entity_group"] == "QTY":
            pending_qty = _parse_qty(ent["word"])
        elif ent["entity_group"] == "FOOD":
            items.append((pending_qty or 1, ent["word"].strip()))
            pending_qty = None
    return items
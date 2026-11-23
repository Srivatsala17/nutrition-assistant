import chromadb
import pandas as pd

import config
from core.embeddings import embed_texts

COLLECTION_NAME = "foods"


def _get_client():
    return chromadb.PersistentClient(path=config.CHROMA_PATH)


def build_food_text(row):
    """The sentence that gets embedded for each food."""
    return (
        f"{row['name']}: {row['calories']} kcal, {row['protein']}g protein, "
        f"{row['carbs']}g carbs, {row['fat']}g fat, {row['diet']}"
    )


def ingest_foods():
    """Read foods.csv, embed every food, store in Chroma."""
    df = pd.read_csv(config.FOODS_CSV).fillna(0)
    client = _get_client()

    # delete the old collection so you can safely re-run
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    col = client.create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})

    docs = [build_food_text(r) for _, r in df.iterrows()]
    col.add(
        ids=[str(i) for i in range(len(df))],
        documents=docs,
        embeddings=embed_texts(docs),
        metadatas=df.to_dict("records"),  # includes the 'source' column for citations
    )
    print("Stored", len(df), "foods in", config.CHROMA_PATH)


def search_foods(query, k=5, diet=None):
    """Return the top k foods as dicts (with source for citations)."""
    col = _get_client().get_collection(COLLECTION_NAME)
    res = col.query(
        query_embeddings=embed_texts([query]),
        n_results=k,
        where={"diet": diet} if diet else None,
    )
    results = []
    for meta, dist in zip(res["metadatas"][0], res["distances"][0]):
        meta["score"] = round(1 - dist, 3)  # higher = more similar
        results.append(meta)
    return results
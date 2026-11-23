from sentence_transformers import SentenceTransformer
import config

_model = None


def get_model():
    """Load the encoder once and reuse it."""
    global _model
    if _model is None:
        _model = SentenceTransformer(config.EMBEDDING_MODEL)
    return _model


def embed_texts(texts):
    """Turn a list of texts into vectors."""
    return get_model().encode(texts, show_progress_bar=False).tolist()
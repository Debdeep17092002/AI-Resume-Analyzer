from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_WORDS = 150  # the model reads ~256 tokens at most, so we split long text


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(MODEL_NAME)


def _chunks(text: str, size: int = CHUNK_WORDS) -> list[str]:
    words = (text or "").split()
    if not words:
        return [""]
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)]


def get_embedding(text: str) -> np.ndarray:
    """Embed long text by encoding chunks and averaging the vectors."""
    vectors = get_model().encode(_chunks(text), normalize_embeddings=True)
    mean = vectors.mean(axis=0)
    norm = np.linalg.norm(mean)
    return mean / norm if norm else mean


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0
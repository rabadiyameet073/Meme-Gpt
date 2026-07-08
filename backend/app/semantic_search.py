import json
import math
import re
from pathlib import Path

from app.config import DATA_DIR

DIM = 384
_embeddings: dict[str, list[float]] | None = None


def _load_embeddings() -> dict[str, list[float]]:
    global _embeddings
    if _embeddings is not None:
        return _embeddings

    path = DATA_DIR / "embeddings.json"
    _embeddings = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data:
            _embeddings[item["id"]] = item["vector"]
    return _embeddings


def tokenize(text: str) -> list[str]:
    return [t for t in re.sub(r"[^\w\s%]", " ", text.lower()).split() if len(t) > 1]


def _hash_term(term: str) -> int:
    h = 0
    for ch in term:
        h = (h * 31 + ord(ch)) & 0xFFFFFFFF
    return h % DIM


def _build_idf(corpus: list[list[str]]) -> dict[str, float]:
    df: dict[str, int] = {}
    n = len(corpus)
    for doc in corpus:
        for term in set(doc):
            df[term] = df.get(term, 0) + 1
    return {term: math.log((n + 1) / (count + 1)) + 1 for term, count in df.items()}


def _normalize(vec: list[float]) -> list[float]:
    mag = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / mag for v in vec]


def _build_vector(tokens: list[str], idf: dict[str, float]) -> list[float]:
    tf: dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    vec = [0.0] * DIM
    for term, count in tf.items():
        vec[_hash_term(term)] += (count / len(tokens)) * idf.get(term, 0)
    return _normalize(vec)


def _cosine(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    return sum(a[i] * b[i] for i in range(n))


def semantic_scores(query: str, memes: list[dict]) -> dict[str, float]:
    query_tokens = tokenize(query)
    corpus = [
        tokenize(f"{m['name']} {m['dialogue']} {m['explanation']} {' '.join(m['keywords'])}")
        for m in memes
    ]
    idf = _build_idf(corpus)
    query_vec = _build_vector(query_tokens, idf)
    stored = _load_embeddings()
    scores: dict[str, float] = {}

    for i, meme in enumerate(memes):
        score = 0.0
        meme_vec = _build_vector(corpus[i], idf)
        score += _cosine(query_vec, meme_vec) * 0.4

        meme_terms = set(corpus[i])
        overlap = sum(1 for qt in query_tokens if qt in meme_terms)
        for kw in meme["keywords"]:
            kl = kw.lower()
            for qt in query_tokens:
                if qt in kl or kl in qt:
                    overlap += 0.5
        score += (overlap / max(len(query_tokens), 1)) * 0.35

        if meme["id"] in stored:
            score += _cosine(query_vec[: len(stored[meme["id"]])], stored[meme["id"]]) * 0.25

        scores[meme["id"]] = min(score, 1.0)

    return scores

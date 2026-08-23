import json
import logging
import math
import re
from pathlib import Path

from app.config import DATA_DIR, USE_TRANSFORMER_MODEL

logger = logging.getLogger("memegpt.semantic_search")

DIM = 384
_embeddings_cache: dict[str, list[float]] | None = None
_st_model = None
_model_attempted = False


def _get_transformer_model():
    global _st_model, _model_attempted
    if not USE_TRANSFORMER_MODEL or _model_attempted:
        return _st_model

    _model_attempted = True
    try:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformers model (all-MiniLM-L6-v2)...")
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
        logger.info("SentenceTransformer model loaded successfully.")
    except Exception as e:
        logger.warning(f"Could not load SentenceTransformer ({e}). Falling back to TF-IDF semantic search.")
        _st_model = None
    return _st_model


def _load_embeddings() -> dict[str, list[float]]:
    global _embeddings_cache
    if _embeddings_cache is not None:
        return _embeddings_cache

    path = DATA_DIR / "embeddings.json"
    _embeddings_cache = {}
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for item in data:
                _embeddings_cache[item["id"]] = item["vector"]
            logger.info(f"Loaded {len(_embeddings_cache)} pre-computed embeddings from {path.name}")
        except Exception as e:
            logger.error(f"Error loading embeddings file: {e}")
    return _embeddings_cache


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
    if not tokens:
        return [0.0] * DIM
    tf: dict[str, int] = {}
    for t in tokens:
        tf[t] = tf.get(t, 0) + 1
    vec = [0.0] * DIM
    for term, count in tf.items():
        vec[_hash_term(term)] += (count / len(tokens)) * idf.get(term, 0)
    return _normalize(vec)


def _cosine(a: list[float], b: list[float]) -> float:
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(a[i] * b[i] for i in range(n))


def embed_text(text: str) -> list[float]:
    """Generate 384-dimensional L2-normalized vector for given text."""
    model = _get_transformer_model()
    if model is not None:
        try:
            vec = model.encode(text, convert_to_numpy=True).tolist()
            return _normalize(vec)
        except Exception:
            pass
    tokens = tokenize(text)
    idf = {t: 1.0 for t in tokens}
    return _build_vector(tokens, idf)



def semantic_scores(query: str, memes: list[dict]) -> dict[str, float]:
    query_tokens = tokenize(query)
    corpus = [
        tokenize(f"{m['name']} {m['dialogue']} {m['explanation']} {' '.join(m.get('keywords', []))}")
        for m in memes
    ]
    idf = _build_idf(corpus)
    query_vec = _build_vector(query_tokens, idf)
    stored = _load_embeddings()

    # Check if sentence-transformers model is available for live query embedding
    model = _get_transformer_model()
    st_query_vec = None
    if model is not None:
        try:
            st_query_vec = model.encode(query, convert_to_numpy=True).tolist()
        except Exception as e:
            logger.warning(f"Failed to encode query with model: {e}")

    scores: dict[str, float] = {}

    for i, meme in enumerate(memes):
        score = 0.0
        meme_vec = _build_vector(corpus[i], idf)
        
        # Base TF-IDF Cosine
        score += _cosine(query_vec, meme_vec) * 0.4

        # Keyword and term overlap bonus
        meme_terms = set(corpus[i])
        overlap = sum(1 for qt in query_tokens if qt in meme_terms)
        for kw in meme.get("keywords", []):
            kl = kw.lower()
            for qt in query_tokens:
                if qt in kl or kl in qt:
                    overlap += 0.5
        score += (overlap / max(len(query_tokens), 1)) * 0.35

        # Vector comparison (using stored embeddings or transformer model)
        meme_id = meme["id"]
        if meme_id in stored:
            target_vec = stored[meme_id]
            if st_query_vec is not None:
                score += _cosine(st_query_vec, target_vec) * 0.25
            else:
                score += _cosine(query_vec[: len(target_vec)], target_vec) * 0.25

        scores[meme_id] = min(score, 1.0)

    return scores


async def async_semantic_scores(query: str, memes: list[dict]) -> dict[str, float]:
    """Non-blocking async wrapper that runs CPU-heavy model inference in a threadpool."""
    from starlette.concurrency import run_in_threadpool
    return await run_in_threadpool(semantic_scores, query, memes)

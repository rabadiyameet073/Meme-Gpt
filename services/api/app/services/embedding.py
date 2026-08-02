class EmbeddingService:
    def __init__(self):
        self.model_name = "all-MiniLM-L6-v2"

    def embed_text(self, text: str) -> list[float]:
        # Return mock 384-dimensional vector stub
        return [0.01] * 384

embedding_service = EmbeddingService()

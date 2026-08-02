class QdrantSearchService:
    def __init__(self):
        self.collection_name = "memes"

    async def search_vector(self, vector: list[float], limit: int = 12):
        return []

search_service = QdrantSearchService()

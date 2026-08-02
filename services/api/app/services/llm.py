class LLMService:
    def __init__(self):
        self.provider = "Groq"

    async def parse_intent(self, query: str) -> dict:
        return {
            "query": query,
            "detected_emotion": "humor",
            "search_keywords": query.split()
        }

llm_service = LLMService()

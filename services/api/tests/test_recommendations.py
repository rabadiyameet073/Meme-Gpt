import pytest
from app.services.recommendation import recommendation_service
from app.models.search import SearchRequest

@pytest.mark.asyncio
async def test_recommendation_pipeline():
    req = SearchRequest(query="debugging code")
    res = await recommendation_service.search(req)
    assert res.total_found > 0

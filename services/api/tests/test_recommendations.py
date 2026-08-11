import pytest
from app.services.recommendation import recommendation_service
from app.models.search import SearchRequest

@pytest.mark.asyncio
async def test_recommendation_pipeline():
    res = await recommendation_service.recommend(user_text="debugging code")
    assert res.success is True
    assert isinstance(res.results, list)

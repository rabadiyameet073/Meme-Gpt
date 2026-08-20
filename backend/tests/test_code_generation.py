"""Tests for internal AI code & content generation from 05_AI_System/Code_Generation.md."""

from app.services.llm_service import (
    generate_meme_tags,
    generate_weekly_blog_post,
    generate_test_dataset,
)


def test_generate_meme_tags_schema():
    tags = generate_meme_tags("This Is Fine", "THIS IS FINE", "Dog in burning room")
    assert isinstance(tags, dict)
    assert "emotions" in tags
    assert isinstance(tags["emotions"], list)
    assert len(tags["emotions"]) >= 1

    assert "situations" in tags
    assert isinstance(tags["situations"], list)
    assert len(tags["situations"]) >= 1

    assert "keywords" in tags
    assert isinstance(tags["keywords"], list)

    assert "tone" in tags
    assert "meme_type" in tags
    assert "alt_text" in tags


def test_generate_weekly_blog_post_markdown():
    memes = [
        {"name": "This Is Fine", "caption": "Dog drinking coffee in a fire"},
        {"name": "Distracted Boyfriend", "caption": "Man looking back at another girl"},
    ]
    post = generate_weekly_blog_post("Developer", memes)
    assert isinstance(post, str)
    assert "# Top 20 Developer Memes of This Week" in post
    assert "developer memes" in post.lower()
    assert "MemeGPT" in post


def test_generate_test_dataset():
    dataset = generate_test_dataset(3)
    assert isinstance(dataset, list)
    assert len(dataset) == 3
    for item in dataset:
        assert "id" in item
        assert "name" in item
        assert "caption" in item
        assert "emotions" in item
        assert "tags" in item

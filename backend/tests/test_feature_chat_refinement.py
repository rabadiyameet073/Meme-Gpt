"""Tests for Chat Refinement feature from 08_Features/Chat_Refinement.md."""

import uuid
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, init_db, Meme
from app.services.chat_refinement_service import (
    parse_refinement_command,
    parse_intent_with_context,
    clear_session_history,
)

client = TestClient(app)
init_db()


def test_command_parser_rules():
    # 1. Reset
    cmd_reset = parse_refinement_command("try something different")
    assert cmd_reset["is_reset"] is True

    # 2. Tone
    cmd_tone = parse_refinement_command("something more sarcastic please")
    assert cmd_tone["tone_shift"] == "sarcastic"

    # 3. Emotion
    cmd_emotion = parse_refinement_command("give me something sadder")
    assert cmd_emotion["emotion_shift"] == "sadness"

    # 4. Format
    cmd_fmt = parse_refinement_command("show me GIFs instead")
    assert cmd_fmt["format_preference"] == "gif"

    # 5. Reference index
    cmd_ref = parse_refinement_command("the second one but as a GIF")
    assert cmd_ref["reference_index"] == 2
    assert cmd_ref["format_preference"] == "gif"

    # 6. Similarity
    cmd_sim = parse_refinement_command("more like the first one")
    assert cmd_sim["is_similar_search"] is True
    assert cmd_sim["reference_index"] == 1


def test_multi_turn_flow_end_to_end():
    session_id = f"sess_{uuid.uuid4().hex[:8]}"

    # Populate DB with sample test memes
    with next(get_db()) as db:
        test_ids = [f"turn_meme_{i}_{uuid.uuid4().hex[:4]}" for i in range(3)]
        db.add(Meme(
            id=test_ids[0],
            name="Monday Sarcasm Meme",
            slug=f"monday-sarcasm-{test_ids[0]}",
            category="work",
            dialogue="Oh look, Monday again.",
            explanation="Sarcastic monday",
            keywords='["monday", "sarcastic", "work"]',
            gif_ref="https://cdn.memegpt.com/gifs/monday.gif",
            image_ref="https://cdn.memegpt.com/images/monday.png",
        ))
        db.add(Meme(
            id=test_ids[1],
            name="Exhausted Coffee Meme",
            slug=f"exhausted-coffee-{test_ids[1]}",
            category="work",
            dialogue="Need coffee now.",
            explanation="Tired feeling",
            keywords='["exhausted", "tired", "coffee"]',
            gif_ref="https://cdn.memegpt.com/gifs/coffee.gif",
            image_ref="https://cdn.memegpt.com/images/coffee.png",
        ))
        db.commit()

    # Turn 1: Initial query
    turn1_res = client.post("/api/v1/chat/refine", json={
        "query": "Monday morning feeling",
        "session_id": session_id,
        "limit": 5,
    })
    assert turn1_res.status_code == 200
    t1 = turn1_res.json()
    assert t1["success"] is True
    assert t1["turn"] == 1
    assert len(t1["results"]) >= 1

    # Turn 2: Tone refinement
    turn2_res = client.post("/api/v1/chat/refine", json={
        "query": "Something more sarcastic",
        "session_id": session_id,
        "limit": 5,
    })
    assert turn2_res.status_code == 200
    t2 = turn2_res.json()
    assert t2["success"] is True
    assert t2["turn"] == 2
    assert t2["intent_parsed"]["tone"] == "sarcastic"
    assert "Monday morning feeling" in t2["enriched_query"]

    # Turn 3: Positional reference + format switch
    turn3_res = client.post("/api/v1/chat/refine", json={
        "query": "The first one but as a GIF",
        "session_id": session_id,
        "limit": 5,
    })
    assert turn3_res.status_code == 200
    t3 = turn3_res.json()
    assert t3["success"] is True
    assert t3["is_reference_selection"] is True
    assert len(t3["results"]) == 1
    assert t3["results"][0]["id"] == t2["results"][0]["id"]
    assert "gif" in t3["results"][0]["preview_url"]

    # Turn 4: Reset
    turn4_res = client.post("/api/v1/chat/refine", json={
        "query": "Try something different",
        "session_id": session_id,
    })
    assert turn4_res.status_code == 200
    t4 = turn4_res.json()
    assert t4["turn"] == 1  # Reset back to turn 1


def test_session_history_endpoints():
    session_id = f"sess_hist_{uuid.uuid4().hex[:8]}"

    # Send a query
    client.post("/api/v1/chat/search", json={
        "query": "Gaming meme",
        "session_id": session_id,
    })

    # Inspect history
    get_res = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["turns_count"] == 1

    # Delete session
    del_res = client.delete(f"/api/v1/chat/sessions/{session_id}")
    assert del_res.status_code == 200
    assert del_res.json()["cleared"] is True

    # Inspect history again (should be 0)
    get_res_empty = client.get(f"/api/v1/chat/sessions/{session_id}")
    assert get_res_empty.json()["turns_count"] == 0

"""Tests for Database Relationships, Foreign Keys, and Cascade Behaviors from 06_Database/Relationships.md."""

import uuid
from app.database import get_db, init_db, Meme, MemeVote, MemeUsage, Feedback, SavedMeme, User
from app.services.database_service import (
    get_relationship_catalog,
    get_cascade_behavior_rules,
    get_cardinality_matrix,
    verify_referential_integrity,
    simulate_cascade_delete,
)

# Ensure tables exist
init_db()


def test_get_relationship_catalog():
    catalog = get_relationship_catalog()
    assert "foreign_keys" in catalog
    fks = {fk["relationship"]: fk for fk in catalog["foreign_keys"]}

    assert "MemeVote → Meme" in fks
    assert fks["MemeVote → Meme"]["on_delete"] == "CASCADE"

    assert "MemeUsage → Meme" in fks
    assert fks["MemeUsage → Meme"]["on_delete"] == "CASCADE"

    assert "SavedMeme → User" in fks
    assert fks["SavedMeme → User"]["on_delete"] == "CASCADE"

    assert "Feedback → User" in fks
    assert fks["Feedback → User"]["on_delete"] == "SET NULL"

    assert "Feedback → Meme" in fks
    assert fks["Feedback → Meme"]["on_delete"] == "CASCADE"


def test_get_cascade_behavior_rules_and_cardinality():
    rules = get_cascade_behavior_rules()
    assert len(rules) == 3
    reasons = [r["reason"] for r in rules]
    assert any("GDPR" in r for r in reasons)
    assert any("analytics value" in r for r in reasons)

    cardinality = get_cardinality_matrix()
    assert len(cardinality) == 5
    card_map = {c["entity_a"] + "->" + c["entity_b"]: c for c in cardinality}
    assert "Meme->MemeVotes" in card_map
    assert "1:N" in card_map["Meme->MemeVotes"]["cardinality"]
    assert "User->Memes" in card_map
    assert "M:N" in card_map["User->Memes"]["cardinality"]


def test_verify_referential_integrity():
    with next(get_db()) as db:
        integrity = verify_referential_integrity(db)
        assert integrity["status"] == "healthy"
        assert integrity["referential_integrity_intact"] is True


def test_simulate_cascade_delete():
    with next(get_db()) as db:
        # Create a test meme with vote, usage, and feedback
        test_id = str(uuid.uuid4())
        test_meme = Meme(
            id=test_id,
            name="Test Cascade Meme",
            slug=f"test-cascade-{test_id[:8]}",
            category="test",
            dialogue="dialogue",
            explanation="explanation",
            keywords="[]",
        )
        db.add(test_meme)
        db.flush()

        # Add child records
        db.add(MemeVote(meme_id=test_id, session_id="test_sess", vote=1))
        db.add(MemeUsage(meme_id=test_id, query="test query", confidence=0.9, session_id="test_sess"))
        db.add(Feedback(meme_id=test_id, action="thumbs_up", session_id="test_sess"))
        db.commit()

        # Execute cascade delete simulation
        res = simulate_cascade_delete(db, test_id)
        db.commit()

        assert res["status"] == "cascaded_successfully"
        assert res["all_children_cleaned"] is True
        assert res["deleted_children"]["votes"] >= 1
        assert res["deleted_children"]["usage_logs"] >= 1
        assert res["deleted_children"]["feedback"] >= 1

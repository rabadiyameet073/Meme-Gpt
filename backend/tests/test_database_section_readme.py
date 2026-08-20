"""Tests for Section 06 — Database README from 06_Database/README.md."""

from app.services.database_service import get_database_section_catalog


def test_get_database_section_catalog():
    catalog = get_database_section_catalog()
    assert catalog["section"] == "06 — Database"
    assert catalog["previous_section"] == "05_AI_System"
    assert catalog["next_section"] == "07_APIs"
    assert len(catalog["documents"]) == 8

    doc_names = [d["document"] for d in catalog["documents"]]
    assert "Database_Overview.md" in doc_names
    assert "Schema.md" in doc_names
    assert "Tables.md" in doc_names
    assert "Relationships.md" in doc_names
    assert "Indexing.md" in doc_names
    assert "Performance.md" in doc_names
    assert "Migrations.md" in doc_names
    assert "Backup_Recovery.md" in doc_names

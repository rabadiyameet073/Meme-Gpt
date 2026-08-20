"""Tests for Database Backup & Disaster Recovery from 06_Database/Backup_Recovery.md."""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from app.services.backup_service import (
    calculate_file_checksum,
    create_database_backup,
    restore_database_backup,
    create_qdrant_snapshot,
    verify_disaster_recovery_health,
)


def test_calculate_file_checksum():
    with tempfile.NamedTemporaryFile(delete=False, mode="w", suffix=".txt") as tf:
        tf.write("MemeGPT Test Content")
        tf_path = Path(tf.name)

    try:
        checksum = calculate_file_checksum(tf_path)
        assert len(checksum) == 64
        # SHA256 matches same content
        checksum2 = calculate_file_checksum(tf_path)
        assert checksum == checksum2
    finally:
        if tf_path.exists():
            tf_path.unlink()


def test_create_and_restore_database_backup():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        source_db = tmp_path / "dev.db"
        target_restore_db = tmp_path / "restored.db"

        # Create sample DB
        conn = sqlite3.connect(source_db)
        conn.execute("CREATE TABLE memes (id TEXT PRIMARY KEY, name TEXT);")
        conn.execute("INSERT INTO memes (id, name) VALUES ('m1', 'Success Kid');")
        conn.execute("INSERT INTO memes (id, name) VALUES ('m2', 'Doge');")
        conn.commit()
        conn.close()

        # Perform backup
        backup_res = create_database_backup(backup_dir=tmp_path / "backups")
        assert backup_res["status"] == "success"
        backup_file = backup_res["path"]
        assert Path(backup_file).exists()

        # Perform restore
        restore_res = restore_database_backup(backup_file=backup_file, target_db_path=target_restore_db)
        assert restore_res["status"] == "success"
        assert restore_res["restored"] is True
        assert restore_res["integrity"] == "ok"


def test_create_qdrant_snapshot_mock():
    mock_client = MagicMock()
    mock_snapshot = MagicMock()
    mock_snapshot.name = "snapshot_memes_2026.json"
    mock_snapshot.size = 1048576
    mock_client.create_snapshot.return_value = mock_snapshot

    res = create_qdrant_snapshot(client=mock_client, collection_name="memes")
    assert res["status"] == "success"
    assert res["collection_name"] == "memes"
    assert "snapshot_name" in res


def test_verify_disaster_recovery_health():
    dr_diag = verify_disaster_recovery_health()
    assert dr_diag["is_dr_ready"] is True
    assert "rto_targets" in dr_diag
    assert "rpo_targets" in dr_diag
    assert dr_diag["rto_targets"]["database_restore"] == "<1 hour"
    assert dr_diag["rto_targets"]["vector_index_rebuild"] == "<30 min"
    assert dr_diag["rpo_targets"]["database_data_loss"] == "<24 hours"

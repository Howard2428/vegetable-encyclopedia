"""
Shared fixtures for the vegetable-encyclopedia test suite.
Sets up an in-memory SQLite database so every test session starts clean.
"""

import sys
import os
import pytest

# Ensure the project root is on sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from utils.db_manager import DBManager


@pytest.fixture(autouse=True)
def _reset_db(tmp_path):
    """Create a fresh in-memory SQLite DB for every test, then tear it down."""
    # Reset singleton state
    DBManager._instance = None
    DBManager._connection = None

    db_path = str(tmp_path / "test.db")
    DBManager.initialize(db_type="sqlite", db_path=db_path)

    # Run the init script to create tables
    init_sql = os.path.join(PROJECT_ROOT, "data", "init_db.sql")
    DBManager.init_db(init_sql)

    yield

    DBManager.close()

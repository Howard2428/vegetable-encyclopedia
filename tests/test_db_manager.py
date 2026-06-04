"""Unit tests for utils/db_manager.py."""

import pytest
from utils.db_manager import DBManager


class TestDBManager:

    def test_singleton(self):
        a = DBManager()
        b = DBManager()
        assert a is b

    def test_get_connection(self):
        conn = DBManager.get_connection()
        assert conn is not None

    def test_get_db_type(self):
        assert DBManager.get_db_type() == 'sqlite'

    def test_close_and_reopen(self, tmp_path):
        DBManager.close()
        with pytest.raises(RuntimeError):
            DBManager.get_connection()
        # Re-init for following tests (autouse fixture will reset anyway)
        DBManager.initialize(db_type='sqlite',
                             db_path=str(tmp_path / "test2.db"))

    def test_invalid_db_type(self):
        DBManager.close()
        with pytest.raises(ValueError, match="不支持的数据库类型"):
            DBManager.initialize(db_type='postgres')

    def test_mysql_without_config(self):
        DBManager.close()
        with pytest.raises(ValueError, match="MySQL配置不能为空"):
            DBManager.initialize(db_type='mysql', db_config=None)

    def test_init_db_creates_tables(self):
        conn = DBManager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name='veg_vegetable'"
        )
        assert cursor.fetchone() is not None

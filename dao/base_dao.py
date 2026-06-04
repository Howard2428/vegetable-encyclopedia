"""
基础数据访问对象
提供所有DAO类共用的数据库操作方法。
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Any
from utils.db_manager import DBManager

logger = logging.getLogger(__name__)


class BaseDAO:
    """基础DAO类，封装通用的数据库操作"""

    def __init__(self):
        self.db = DBManager()

    def get_connection(self):
        """获取数据库连接"""
        return self.db.get_connection()

    def execute_update(self, sql: str, params: tuple = ()) -> int:
        """
        执行INSERT/UPDATE/DELETE语句

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            受影响的行数或最后插入的ID

        Raises:
            RuntimeError: 当数据库操作失败时
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error("数据库写操作失败 [SQL: %s]: %s", sql.strip()[:80], e)
            raise RuntimeError(f"数据库写操作失败: {e}") from e
        # 如果是INSERT语句，返回最后插入的ID
        if sql.strip().upper().startswith('INSERT'):
            return cursor.lastrowid
        return cursor.rowcount

    def execute_query(self, sql: str, params: tuple = ()) -> list:
        """
        执行SELECT查询

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            查询结果列表

        Raises:
            RuntimeError: 当查询失败时
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as e:
            logger.error("数据库查询失败 [SQL: %s]: %s", sql.strip()[:80], e)
            raise RuntimeError(f"数据库查询失败: {e}") from e

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Any]:
        """
        查询单条记录

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            单条记录或None

        Raises:
            RuntimeError: 当查询失败时
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchone()
        except Exception as e:
            logger.error("数据库查询失败 [SQL: %s]: %s", sql.strip()[:80], e)
            raise RuntimeError(f"数据库查询失败: {e}") from e

    def fetch_all(self, sql: str, params: tuple = ()) -> list:
        """
        查询所有匹配记录

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            所有匹配记录列表
        """
        return self.execute_query(sql, params)

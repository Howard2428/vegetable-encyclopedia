"""
基础数据访问对象
提供所有DAO类共用的数据库操作方法。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Optional, Any
from utils.db_manager import DBManager


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
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
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
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchall()

    def fetch_one(self, sql: str, params: tuple = ()) -> Optional[Any]:
        """
        查询单条记录

        Args:
            sql: SQL语句
            params: 参数元组

        Returns:
            单条记录或None
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        return cursor.fetchone()

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

    def count(self, table: str, where: str = '', params: tuple = ()) -> int:
        """
        统计记录数

        Args:
            table: 表名
            where: 可选的WHERE子句（不含WHERE关键字）
            params: WHERE子句的参数

        Returns:
            记录数
        """
        sql = f"SELECT COUNT(*) as cnt FROM {table}"
        if where:
            sql += f" WHERE {where}"
        row = self.fetch_one(sql, params)
        return row['cnt'] if row else 0

"""
数据库连接管理模块
提供SQLite（优先）和MySQL两种数据库连接支持。
采用单例模式，确保全局只有一个数据库连接实例。
"""

import sqlite3
import os
from typing import Optional


class DBManager:
    """数据库连接管理器（单例模式）"""

    _instance: Optional['DBManager'] = None
    _connection: Optional[sqlite3.Connection] = None
    _db_type: str = 'sqlite'
    _db_path: str = ''

    def __new__(cls, *args, **kwargs):
        """单例模式：确保全局只有一个实例"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def initialize(cls, db_type: str = 'sqlite', db_path: str = '',
                   db_config: Optional[dict] = None) -> None:
        """
        初始化数据库连接

        Args:
            db_type: 数据库类型，'sqlite' 或 'mysql'
            db_path: SQLite数据库文件路径（与db_config二选一）
            db_config: MySQL连接配置字典，包含host, port, user, password, database
        """
        cls._db_type = db_type

        if db_type == 'sqlite':
            cls._db_path = db_path or os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'data', 'vegetable_db.db'
            )
            cls._connection = sqlite3.connect(cls._db_path)
            cls._connection.row_factory = sqlite3.Row
            # 启用外键约束
            cls._connection.execute("PRAGMA foreign_keys = ON")
        elif db_type == 'mysql':
            if db_config is None:
                raise ValueError("MySQL配置不能为空")
            import pymysql
            cls._connection = pymysql.connect(
                host=db_config.get('host', 'localhost'),
                port=db_config.get('port', 3306),
                user=db_config.get('user', 'root'),
                password=db_config.get('password', ''),
                database=db_config.get('database', 'vegetable_db'),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
            )
        else:
            raise ValueError(f"不支持的数据库类型: {db_type}")

    @classmethod
    def get_connection(cls):
        """获取数据库连接"""
        if cls._connection is None:
            raise RuntimeError("数据库未初始化，请先调用 DBManager.initialize()")
        return cls._connection

    @classmethod
    def init_db(cls, sql_file_path: Optional[str] = None) -> None:
        """
        执行建表脚本初始化数据库

        Args:
            sql_file_path: SQL建表脚本文件路径，默认使用data/init_db.sql
        """
        if sql_file_path is None:
            sql_file_path = os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                '..', 'data', 'init_db.sql'
            )

        conn = cls.get_connection()
        cursor = conn.cursor()

        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # 按分号分割执行每条SQL语句
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for statement in statements:
            try:
                if cls._db_type == 'sqlite':
                    cursor.execute(statement)
                else:
                    cursor.execute(statement)
            except Exception as e:
                # 表已存在则跳过
                if 'already exists' in str(e).lower() or \
                   'duplicate' in str(e).lower():
                    continue
                raise

        conn.commit()

    @classmethod
    def close(cls) -> None:
        """关闭数据库连接"""
        if cls._connection is not None:
            cls._connection.close()
            cls._connection = None
            cls._instance = None

    @classmethod
    def get_db_type(cls) -> str:
        """获取当前数据库类型"""
        return cls._db_type

"""
用户数据访问对象
负责sys_user表的所有数据库操作。
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Optional
from dao.base_dao import BaseDAO
from entity.user import User


class UserDAO(BaseDAO):
    """用户表数据访问对象"""

    def create_user(self, username: str, password_hash: str,
                    email: str = '', role: str = 'user') -> int:
        """
        创建新用户

        Args:
            username: 用户名
            password_hash: 加密后的密码哈希
            email: 邮箱
            role: 角色 ('user' 或 'admin')

        Returns:
            新用户的user_id
        """
        sql = """
            INSERT INTO sys_user (username, password_hash, email, role, register_time)
            VALUES (?, ?, ?, ?, datetime('now', 'localtime'))
        """
        return self.execute_update(sql, (
            username, password_hash,
            email if email else None,  # 空邮箱存NULL，避免UNIQUE冲突
            role
        ))

    def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名查询用户"""
        sql = "SELECT * FROM sys_user WHERE username = ?"
        row = self.fetch_one(sql, (username,))
        return User.from_row(row) if row else None

    def get_by_id(self, user_id: int) -> Optional[User]:
        """根据ID查询用户"""
        sql = "SELECT * FROM sys_user WHERE user_id = ?"
        row = self.fetch_one(sql, (user_id,))
        return User.from_row(row) if row else None

    def update_last_login(self, user_id: int) -> None:
        """更新最后登录时间"""
        sql = """
            UPDATE sys_user
            SET last_login_time = datetime('now', 'localtime')
            WHERE user_id = ?
        """
        self.execute_update(sql, (user_id,))

    def check_username_exists(self, username: str) -> bool:
        """检查用户名是否存在"""
        return self.count('sys_user', 'username = ?', (username,)) > 0

    def update_password(self, user_id: int, new_password_hash: str) -> None:
        """更新用户密码"""
        sql = """
            UPDATE sys_user
            SET password_hash = ?
            WHERE user_id = ?
        """
        self.execute_update(sql, (new_password_hash, user_id))

    def get_all_users(self) -> list:
        """获取所有用户列表（不含密码哈希）"""
        sql = """
            SELECT user_id, username, email, role, register_time, last_login_time
            FROM sys_user ORDER BY user_id
        """
        return self.fetch_all(sql)

    def get_user_count(self) -> int:
        """统计用户总数"""
        return self.count('sys_user')

    def delete_all_users(self) -> int:
        """删除所有用户及关联数据（收藏夹、清单、浏览历史），返回删除用户数"""
        user_count = self.count('sys_user')

        # 按外键依赖顺序删除
        self.execute_update("DELETE FROM veg_browse_history")
        self.execute_update("DELETE FROM veg_list_item")
        self.execute_update("DELETE FROM veg_custom_list")
        self.execute_update("DELETE FROM veg_favorite_item")
        self.execute_update("DELETE FROM veg_favorites_list")
        self.execute_update("DELETE FROM sys_user")

        return user_count

    def check_email_exists(self, email: str) -> bool:
        """检查邮箱是否已被使用"""
        if not email:
            return False
        return self.count('sys_user', 'email = ?', (email,)) > 0

"""
用户实体类
管理系统用户的基础身份信息。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户实体"""

    user_id: Optional[int] = None
    username: str = ''
    password_hash: str = ''
    email: str = ''
    role: str = 'user'      # 'user' 或 'admin'
    register_time: Optional[datetime] = None
    last_login_time: Optional[datetime] = None

    @property
    def is_admin(self) -> bool:
        """检查是否为管理员"""
        return self.role == 'admin'

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'password_hash': self.password_hash,
            'email': self.email,
            'role': self.role,
            'register_time': self.register_time,
            'last_login_time': self.last_login_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建实体"""
        return cls(
            user_id=data.get('user_id'),
            username=data.get('username', ''),
            password_hash=data.get('password_hash', ''),
            email=data.get('email', ''),
            role=data.get('role', 'user'),
            register_time=data.get('register_time'),
            last_login_time=data.get('last_login_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'User':
        """从数据库行对象创建实体（兼容有无role列的情况）"""
        if row is None:
            return None
        return cls(
            user_id=row['user_id'],
            username=row['username'],
            password_hash=row['password_hash'],
            email=row['email'] or '',
            role=row['role'] if 'role' in row.keys() else 'user',
            register_time=row['register_time'],
            last_login_time=row['last_login_time'],
        )

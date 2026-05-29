"""
自定义清单实体类
存储用户创建的自定义蔬菜清单。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CustomList:
    """自定义清单实体"""

    list_id: Optional[int] = None
    user_id: int = 0
    list_name: str = ''
    description: str = ''
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'list_id': self.list_id,
            'user_id': self.user_id,
            'list_name': self.list_name,
            'description': self.description,
            'create_time': self.create_time,
            'update_time': self.update_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CustomList':
        """从字典创建实体"""
        return cls(
            list_id=data.get('list_id'),
            user_id=data.get('user_id', 0),
            list_name=data.get('list_name', ''),
            description=data.get('description', ''),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'CustomList':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        return cls(
            list_id=row['list_id'],
            user_id=row['user_id'],
            list_name=row['list_name'],
            description=row['description'] or '',
            create_time=row['create_time'],
            update_time=row['update_time'],
        )

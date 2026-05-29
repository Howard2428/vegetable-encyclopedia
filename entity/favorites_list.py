"""
收藏夹实体类
存储用户创建的收藏夹，支持多个收藏夹分类管理。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FavoritesList:
    """收藏夹实体"""

    fav_list_id: Optional[int] = None
    user_id: int = 0
    list_name: str = ''
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        """将实体转换为字典"""
        return {
            'fav_list_id': self.fav_list_id,
            'user_id': self.user_id,
            'list_name': self.list_name,
            'create_time': self.create_time,
            'update_time': self.update_time,
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'FavoritesList':
        """从字典创建实体"""
        return cls(
            fav_list_id=data.get('fav_list_id'),
            user_id=data.get('user_id', 0),
            list_name=data.get('list_name', ''),
            create_time=data.get('create_time'),
            update_time=data.get('update_time'),
        )

    @classmethod
    def from_row(cls, row) -> 'FavoritesList':
        """从数据库行对象创建实体"""
        if row is None:
            return None
        return cls(
            fav_list_id=row['fav_list_id'],
            user_id=row['user_id'],
            list_name=row['list_name'],
            create_time=row['create_time'],
            update_time=row['update_time'],
        )
